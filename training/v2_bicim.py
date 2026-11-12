"""Megazeka-Sayı v2 · C kaynağı: yeni girdi biçimleri.

Dört kategori (docs/SPEC-v2.md §C):
  yari       (C1) yarı normalleşmiş girdi: sayının bir kısmı rakam, büyüklük/birim/para sözcükleri yazıyla
  bitisik    (C2) bitişik yazılmış sayı sözcükleri (onbeş, ikiyüz elli, binyediyüz ...)
  saat_deyis (C3) günlük saat deyişleri (beşe on kala, dördü yirmi geçe ...)
  tarih      (C4) ayın günü (ayın on beşinde, mayısın on dokuzunda ...)

Kullanım:
  python training/v2_bicim.py --out data/v2 --seed 2203 --train 14000 --validation 400 --test 500

Akış ters yöndedir: hedef (yazılı biçim) mevcut `kur_*` kurucularıyla kurulur; girdi ondan deterministik türetilir.
Etiketler elle yazılmaz. Test bölümü, train/validation'da hiç kullanılmayan taşıyıcı şablonlarla üretilir.
"""
from __future__ import annotations

import argparse
import calendar
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))

from megazeka_sayi import sablonlar as B  # noqa: E402
from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.turkce import (  # noqa: E402
    EKLER, UNLULER, ae, ek_uret, iiuu, ilk_harfi_buyut, inflect, lower_tr,
)

BAYT_SINIRI = 180
KATEGORILER = ("yari", "bitisik", "saat_deyis", "tarih")
KAT_AGIRLIK = {"yari": 6500, "bitisik": 3000, "saat_deyis": 2500, "tarih": 2000}
SARMALA_ORANI = 0.22
P_EK = 0.27  # C1'de ekli satır olasılığı (sayi_ek sınıfı hep ekli)

SLOT = B.SLOT

DOLGU = dict(B.FILLERS)
DOLGU.update({
    "kalabalik": ["kişi", "öğrenci", "seyirci", "yolcu", "ziyaretçi", "izleyici", "abone", "hasta", "işçi", "turist",
                  "üye", "katılımcı", "aday", "müşteri"],
    "adet": ["koli", "paket", "kitap", "bilet", "araç", "ürün", "sipariş", "mesaj", "fotoğraf", "dosya", "adet"],
    "vakit": ["sabah", "öğlen", "öğleden sonra", "akşam", "gece"],
})


# ======================================================================================
# Genel yardımcılar
# ======================================================================================

def _secim(rng, ciftler):
    return rng.choices([d for d, _ in ciftler], [w for _, w in ciftler])[0]


def kota(toplam: int, agirlik: dict) -> dict:
    """En büyük kalan yöntemiyle paylaştırma."""
    t = sum(agirlik.values())
    ham = {k: toplam * w / t for k, w in agirlik.items()}
    sayi = {k: int(v) for k, v in ham.items()}
    kalan = toplam - sum(sayi.values())
    for k in sorted(ham, key=lambda k: (-(ham[k] - sayi[k]), k))[:kalan]:
        sayi[k] += 1
    return sayi


def ek_parca(yazili: str) -> str:
    """Kesme işaretinden sonraki yazılı ek ("5'e" -> "e")."""
    return yazili.partition("'")[2]


def girdi_gruplu(n: int) -> list[str]:
    """12500 -> ['12 bin', '500']; 3200000 -> ['3 milyon', '200 bin']; 1500 -> ['bin', '500']."""
    toks = []
    for deger, ad in S.BASAMAKLAR:
        g, n = divmod(n, deger)
        if g:
            toks.append("bin" if (ad == "bin" and g == 1) else f"{g} {ad}")
    if n:
        toks.append(str(n))
    return toks


def iyelik_durum(kok: str, tur: str) -> tuple[str, str]:
    """Sayı sözcüğüne 3. tekil iyelik + durum eki. (sözlü sözcük, kesmeden sonraki yazılı ek).

    tur: iyelik3 -(s)I · bulunma -(s)InDA · ayrilma -(s)InDAn · yonelme -(s)InA · belirtme -(s)InI.
    Sözlü biçimde `dört` -> `dörd` yumuşar; yazılı ek kanonik sözcüğe göredir (4'ünde).
    """
    k = lower_tr(kok)
    p = ek_uret(k, "iyelik3")
    v = p[-1]
    if tur == "iyelik3":
        ek = p
    elif tur == "bulunma":
        ek = p + "nd" + ae(v)
    elif tur == "ayrilma":
        ek = p + "nd" + ae(v) + "n"
    elif tur == "yonelme":
        ek = p + "n" + ae(v)
    elif tur == "belirtme":
        ek = p + "n" + iiuu(v)
    else:
        raise KeyError(tur)
    govde = "dörd" if k == "dört" else k
    return govde + ek, ek


class Durum:
    """Bölüm başına dengeleme sayaçları (en az kullanılanı seç)."""

    def __init__(self):
        self.sayac: Counter = Counter()

    def dengeli(self, rng, ad, adaylar):
        w = min(adaylar, key=lambda a: (self.sayac[(ad, a)], rng.random()))
        self.sayac[(ad, w)] += 1
        return w


# ======================================================================================
# Şablonlar (metinler dosyanın sonunda)
# ======================================================================================

@dataclass(frozen=True)
class Sablon:
    id: str
    kat: str
    sinif: str
    metin: str
    ek: str | None      # ilk varlık yuvasının eki
    alt: str | None     # ilk varlık yuvasının alt türü


SABLONLAR: dict[tuple[str, str], list[Sablon]] = {}
TEST_IDLERI: set[str] = set()
HEPSI: list[Sablon] = []


def _sablonlari_kur(taslak: dict) -> None:
    gorulen = set()
    for (kat, sinif), blok in taslak.items():
        satirlar = [s.strip() for s in blok.strip().splitlines() if s.strip()]
        liste = []
        for i, metin in enumerate(satirlar):
            assert metin not in gorulen, ("yinelenen şablon metni", metin)
            gorulen.add(metin)
            yuvalar = [m for m in SLOT.finditer(metin) if m.group(1) in ("E", "e", "s")]
            assert yuvalar, ("varlık yuvası yok", metin)
            for m in SLOT.finditer(metin):
                ad, alt, ek = m.group(1), m.group(2), m.group(3)
                assert ad in ("E", "e", "s") or ad in DOLGU, ("bilinmeyen yuva", metin, ad)
                assert not ek or ek in EKLER, ("bilinmeyen ek", metin, ek)
            ilk = yuvalar[0]
            sb = Sablon(f"v2c-{kat}-{sinif}-{i:03d}", kat, sinif, metin, ilk.group(3), ilk.group(2))
            liste.append(sb)
            HEPSI.append(sb)
        SABLONLAR[(kat, sinif)] = liste
    # test bölünmesi: grup (kategori, sınıf, ekli mi) başına ~%18, sabit tohum
    rng = random.Random("megazeka-v2c-sablon-bolunmesi")
    gruplar = defaultdict(list)
    for sb in HEPSI:
        gruplar[(sb.kat, sb.sinif, sb.ek is not None)].append(sb.id)
    for k in sorted(gruplar):
        idler = sorted(gruplar[k])
        n = len(idler)
        m = max(1, math.ceil(0.18 * n)) if n >= 3 else (1 if n == 2 else 0)
        TEST_IDLERI.update(rng.sample(idler, m))
    for (kat, sinif), liste in SABLONLAR.items():
        assert any(sb.id in TEST_IDLERI for sb in liste), ("sınıfın test şablonu yok", kat, sinif)
        assert any(sb.id not in TEST_IDLERI for sb in liste), ("sınıfın train şablonu yok", kat, sinif)


def sablon_havuzu(kat, sinif, test):
    return [sb for sb in SABLONLAR[(kat, sinif)] if (sb.id in TEST_IDLERI) == test]


def sablon_sec(rng, kat, sinif, test, ekli=None, uygun=None):
    havuz = sablon_havuzu(kat, sinif, test)
    if uygun:
        havuz = [sb for sb in havuz if uygun(sb)] or havuz
    if ekli is not None:
        alt = [sb for sb in havuz if (sb.ek is not None) == ekli]
        havuz = alt or havuz
    return rng.choice(havuz)


def varlik_yuvalari(sb: Sablon):
    return [(m.group(1), m.group(2), m.group(3)) for m in SLOT.finditer(sb.metin) if m.group(1) in ("E", "e", "s")]


def kur_cumle(rng, sb, buyuk, varliklar, sabit=None):
    """Şablonu doldurur. varliklar: yuva sırasıyla (girdi, hedef) çiftleri. Büyük harf kipi: ilk harf büyük + sonda nokta;
    küçük harf kipi: şablon metni küçültülür ve noktalaması atılır (varlık metinleri olduğu gibi kalır)."""
    metin = sb.metin
    if rng.random() < SARMALA_ORANI:
        metin = B.sarmala(metin, rng)
    parcalar = []
    son = 0
    vi = 0
    kullanilan: dict[str, set] = {}
    for m in SLOT.finditer(metin):
        if m.start() > son:
            lit = metin[son:m.start()]
            parcalar.append(("m", lit, lit))
        ad = m.group(1)
        if ad in ("E", "e", "s"):
            g, h = varliklar[vi]
            vi += 1
            parcalar.append(("v", g, h))
        else:
            if sabit and ad in sabit:
                s = sabit[ad]
            else:
                havuz = [x for x in DOLGU[ad] if x not in kullanilan.setdefault(ad, set())]
                s = rng.choice(havuz)
                kullanilan[ad].add(s)
            parcalar.append(("m", s, s))
        son = m.end()
    if son < len(metin):
        lit = metin[son:]
        parcalar.append(("m", lit, lit))
    assert vi == len(varliklar), (sb.id, vi, len(varliklar))
    gl, hl = [], []
    for tur, a, b in parcalar:
        if tur == "m" and not buyuk:
            a = lower_tr(a).translate(B._NOKTALAMA)
            b = a
        gl.append(a)
        hl.append(b)
    g, h = "".join(gl), "".join(hl)
    if buyuk:
        if g[-1] not in ".?!":
            g += "."
            h += "."
        g, h = ilk_harfi_buyut(g), ilk_harfi_buyut(h)
    g = re.sub(r" {2,}", " ", g).strip()
    h = re.sub(r" {2,}", " ", h).strip()
    return g, h


# ======================================================================================
# C1 · yarı normalleşmiş girdi — deterministik kurucular
# ======================================================================================
# Sayı belirtimi (spec):
#   ("int", n[, kurus])                       tam sayı
#   ("dec", tam, kesir, bucuk)                ondalık / buçuklu
#   ("buyuk", tam, kesir, buyukluk, bucuk)    yuvarlak büyük sayı (milyon, milyar)
# mod: "grup" -> 12 bin 500 · "duz" -> 12500

def yari_girdi(spec, v, ek, mod):
    """Hedef varlıktan (v) yarı normalleşmiş girdi: sayı kısmı rakam, geri kalan sözlü sözcükler korunur."""
    toks = v.sozlu.split()
    tur = spec[0]
    if tur == "int":
        n = spec[1]
        nk = S.sayi_kelimeleri(n)
        assert toks[:len(nk)] == nk or ek, (toks, nk)
        tail = toks[len(nk):]
        if tail or not ek:
            sayi = [str(n)] if mod == "duz" else girdi_gruplu(n)
            return " ".join(sayi + tail)
        suf = ek_parca(v.yazili)
        if mod == "duz":
            return f"{n}'{suf}"
        g = girdi_gruplu(n)
        if n % 1000:
            g[-1] += "'" + suf
        else:
            on, _, ad = g[-1].rpartition(" ")
            g[-1] = (on + " " if on else "") + inflect(ad, ek)[0]
        return " ".join(g)
    if tur == "dec":
        _, tam, kesir, bucuk = spec
        nk = (S.sayi_kelimeleri(tam) + ["buçuk"]) if bucuk else S.ondalik_kelimeleri(tam, kesir)
        tail = toks[len(nk):]
        sayi = f"{tam} buçuk" if bucuk else f"{tam},{kesir}"
        return " ".join([sayi] + tail)
    if tur == "buyuk":
        _, tam, kesir, buyukluk, bucuk = spec
        i = next(j for j, t in enumerate(toks) if t.startswith(buyukluk))
        sayi = f"{tam} buçuk" if bucuk else (f"{tam},{kesir}" if kesir else str(tam))
        return " ".join([sayi] + toks[i:])
    raise KeyError(tur)


def yari_para(spec, ek=None, birim="TL", ad="lira", mod="grup", virgul=False):
    if spec[0] == "buyuk":
        _, tam, kesir, buyukluk, bucuk = spec
        v = V.kur_buyuk_yuvarlak(tam, kesir, buyukluk, bucuk, False, "TL" if birim == "TL" else "dolar", ek)
        return yari_girdi(spec, v, ek, mod), v.yazili
    n = spec[1]
    kurus = spec[2] if len(spec) > 2 else None
    if birim == "TL":
        v = V.kur_para(lira=n, kurus=kurus, ek=ek, ad=ad)
    else:
        kurus = None
        v = V.kur_para(lira=n, birim=birim, ek=ek)
    if kurus is None:
        return yari_girdi(("int", n), v, ek, mod), v.yazili
    toks = v.sozlu.split()
    nk = S.sayi_kelimeleri(n)
    nk2 = S.sayi_kelimeleri(kurus)
    rest = toks[len(nk):]
    mid = rest[:len(rest) - len(nk2) - 1]
    son = rest[-1]
    if virgul:
        if ek and ad == "lira":
            mid = mid[:-1] + [inflect(mid[-1], ek)[0]]
        return f"{n},{kurus:02d} " + " ".join(mid), v.yazili
    sayi = [str(n)] if mod == "duz" else girdi_gruplu(n)
    return " ".join(sayi + mid + [str(kurus), son]), v.yazili


def yari_olcu(spec, birim, ek=None, soz_idx=0, mod="duz"):
    if spec[0] == "int":
        v = V.kur_olcu(spec[1], "", birim, soz_idx, False, False, ek)
    else:
        _, tam, kesir, bucuk = spec
        v = V.kur_olcu(tam, kesir, birim, soz_idx, bucuk, False, ek)
    return yari_girdi(spec, v, ek, mod), v.yazili


def yari_sayi(spec, ek=None, mod="grup"):
    """Çıplak sayı (ardından ad şablonda gelir ya da ek sayıya bağlanır)."""
    if spec[0] == "int":
        v = V.kur_kardinal(spec[1], "rakamla", ek)
    else:
        _, tam, kesir, buyukluk, bucuk = spec
        v = V.kur_buyuk_yuvarlak(tam, kesir, buyukluk, bucuk, False, None, ek)
    return yari_girdi(spec, v, ek, mod), v.yazili


def yari_yuzde(tam, kesir="", bucuk=False, ek=None):
    v = V.kur_yuzde(tam, kesir, bucuk, False, ek)
    if bucuk:
        toks = v.sozlu.split()
        tail = toks[1 + len(S.sayi_kelimeleri(tam)):]
        return f"yüzde {tam} " + " ".join(tail), v.yazili
    return "yüzde " + v.yazili[1:], v.yazili


def yari_saat(h, m=30, bicim="iki_nokta", ek=None, sifirli=False):
    """bicim: iki_nokta (14:30'da) · bucuk (3 buçukta) · tam (saat 5'te: girdi = hedef). 'saat' sözcüğü şablondadır."""
    if bicim == "bucuk":
        v = V.kur_saat(h, 30, True, "dk", ek)
        return f"{h} {v.sozlu.split()[-1]}", v.yazili
    if bicim == "tam":
        v = V.kur_saat(h, bicim="tam", ek=ek)
        return v.yazili, v.yazili
    v = V.kur_saat(h, m, False, "dk", ek)
    suf = ek_parca(v.yazili)
    hh = f"{h:02d}" if sifirli else str(h)
    return f"{hh}:{m:02d}" + ("'" + suf if suf else ""), v.yazili


def ay_duzelt(v, ay, ek):
    """V.kur_tarih, ocak/aralık + ünlüyle başlayan ekte sözlü yumuşamayı (ocağa, aralığı) uygulamaz; düzeltir."""
    ay_k = lower_tr(V.AYLAR[ay - 1])
    toks = v.sozlu.split()
    son = toks[-1]
    if ek and ay_k.endswith("k") and son.startswith(ay_k) and len(son) > len(ay_k) and son[len(ay_k)] in UNLULER:
        toks[-1] = ay_k[:-1] + "ğ" + son[len(ay_k):]
        return V.Varlik(v.yazili, " ".join(toks), v.kategori)
    return v


def yari_tarih(gun, ay, yil=None, ek=None):
    v = V.kur_tarih(gun, ay, yil, ek, False)
    AY = V.AYLAR[ay - 1]
    if yil is None:
        v = ay_duzelt(v, ay, ek)
        return f"{gun} " + v.sozlu.split()[-1], v.yazili
    return v.yazili.replace(AY, lower_tr(AY), 1), v.yazili


def yari_eksi(tam, kesir="", birim="derece", bucuk=False, ek=None, mod="duz"):
    if birim == "TL":
        v = V.kur_eksi(tam, "", "TL", False, ek)
        kesir, bucuk = "", False
    else:
        v = V.kur_eksi(tam, kesir, birim, bucuk, ek)
    toks = v.sozlu.split()
    assert toks[0] == "eksi"
    if bucuk:
        nk = S.sayi_kelimeleri(tam) + ["buçuk"]
        sayi = [f"{tam} buçuk"]
    elif kesir:
        nk = S.ondalik_kelimeleri(tam, kesir)
        sayi = [f"{tam},{kesir}"]
    else:
        nk = S.sayi_kelimeleri(tam)
        sayi = [str(tam)] if mod == "duz" else girdi_gruplu(tam)
    tail = toks[1 + len(nk):]
    return "eksi " + " ".join(sayi + tail), v.yazili


def yari_telefon(r, bicim="bitisik", arti90=False, ek=None):
    v = V.kur_telefon(r, ("sayi",) * 4, arti90, ek)
    suf = ek_parca(v.yazili)
    if arti90:
        g = {"bitisik": "+90" + r[1:], "yarim": f"+90 {r[1:4]} {r[4:]}"}[bicim]
    else:
        g = {"bitisik": r, "sifir_ayri": f"{r[0]} {r[1:4]} {r[4:7]} {r[7:9]} {r[9:]}",
             "dort_yedi": f"{r[:4]} {r[4:]}", "dort_uc_dort": f"{r[:4]} {r[4:7]} {r[7:]}"}[bicim]
    return g + ("'" + suf if suf else ""), v.yazili


# ======================================================================================
# C1 · örnekleyiciler
# ======================================================================================

_MANTIS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 500]
_KURUS = [50, 90, 99, 75, 25, 95, 5, 10, 45, 80, 60, 20, 40]
_KURUS_W = [20, 12, 12, 8, 7, 6, 6, 5, 4, 4, 3, 3, 2]


def _bin_katsayi(rng):
    r = rng.random()
    if r < 0.40:
        return rng.randint(2, 9)
    if r < 0.82:
        return rng.choice([10, 12, 15, 20, 25, 30, 40, 50, 60, 75, 80]) if rng.random() < 0.5 else rng.randint(10, 99)
    return rng.choice([100, 120, 150, 200, 250, 300, 500, 750]) if rng.random() < 0.5 else rng.randint(100, 999)


def _bin_cift(rng):
    a = _secim(rng, [(1, 14), (rng.randint(2, 9), 34), (rng.randint(10, 99), 40), (rng.randint(100, 999), 12)])
    r = rng.random()
    if r < 0.50:
        b = rng.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 750, 800, 900])
    elif r < 0.78:
        b = rng.randint(100, 999)
    else:
        b = rng.randint(1, 99)  # iç sıfır: 5 bin 25 -> 5.025
    return a * 1000 + b


def _duz(rng):
    r = rng.random()
    if r < 0.45:
        return rng.choice([1250, 1500, 1750, 2500, 3500, 4500, 7500]) if rng.random() < 0.4 else rng.randint(1000, 9999)
    if r < 0.80:
        return rng.randint(10, 99) * 1000 + rng.choice([0, 0, 250, 500, 750, rng.randint(1, 999)])
    return rng.randint(100, 999) * 1000 + rng.choice([0, 0, 500, rng.randint(1, 999)])


def _milyon_a(rng):
    m = _secim(rng, [(rng.randint(1, 9), 55), (rng.randint(10, 99), 35), (rng.randint(100, 999), 10)])
    r = rng.random()
    if r < 0.55:
        a, b = rng.choice([100, 200, 250, 300, 500, 750]) if rng.random() < 0.6 else rng.randint(1, 999), 0
    elif r < 0.85:
        a, b = rng.randint(1, 999), rng.randint(1, 999)
    else:
        a, b = 0, rng.randint(1, 999)
    return m * 10**6 + a * 1000 + b


def _buyuk_spec(rng, form):
    """B: 2 buçuk milyon · C: 2,5 milyon · D: 15 milyon."""
    buyukluk = "milyar" if rng.random() < 0.15 else "milyon"
    tam = rng.choice(_MANTIS) if buyukluk == "milyon" else rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50])
    if form in ("B", "C") and tam > 100:
        tam = rng.choice([x for x in _MANTIS if x <= 100])
    if form == "B":
        return ("buyuk", tam, "5", buyukluk, True)
    if form == "C":
        kesir = _secim(rng, [("5", 60), ("25", 10), ("75", 10), ("2", 7), ("3", 7), ("8", 6)])
        return ("buyuk", tam, kesir, buyukluk, False)
    return ("buyuk", tam, "", buyukluk, False)


def _milyon_spec(rng, ekli_bare=False):
    form = _secim(rng, [("A", 40), ("B", 22), ("C", 13), ("D", 25)])
    if form == "A":
        return ("int", _milyon_a(rng)), "grup"
    return _buyuk_spec(rng, form), "grup"


def c1_para(rng, alt, ek):
    dogru = alt == "dogru"
    if dogru:
        alt = _secim(rng, [("birim", 30), ("bin_tek", 18), ("bin_cift", 18), ("duz", 20), ("milyon", 14)])
    doviz = rng.random() < 0.13
    birim = _secim(rng, [("dolar", 45), ("avro", 30), ("euro", 10), ("sterlin", 15)]) if doviz else "TL"
    ad = "Türk lirası" if (birim == "TL" and ek is None and alt != "milyon" and rng.random() < 0.12) else "lira"
    kurus = None
    mod = "grup"
    if alt == "milyon":
        spec, mod = _milyon_spec(rng)
    else:
        if alt == "bin_tek":
            n = _bin_katsayi(rng) * 1000
        elif alt == "bin_cift":
            n = _bin_cift(rng)
        elif alt == "duz":
            n = _duz(rng)
        elif alt == "birim":
            n = rng.choice([5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 250, 500]) if rng.random() < 0.6 else rng.randint(2, 999)
        else:
            return None
        if birim == "TL" and rng.random() < (0.22 if alt in ("duz", "birim", "bin_cift") else 0.05):
            kurus = rng.choices(_KURUS, _KURUS_W)[0]
        spec = ("int", n, kurus) if kurus else ("int", n)
        mod = "duz" if alt in ("duz", "birim") else "grup"
    virgul = alt == "duz" and kurus is not None and rng.random() < 0.6
    g, h = yari_para(spec, ek, birim, ad, mod, virgul)
    return (h, h) if dogru else (g, h)


_GRUP = {
    "agirlik": (["kg", "g"], [70, 30]),
    "uzunluk": (["km", "m", "cm", "mm"], [20, 30, 40, 10]),
    "mesafe": (["km", "m"], [70, 30]),
    "boy": (["cm"], [1]),
    "hacim": (["L", "mL"], [70, 30]),
    "alan": (["m2"], [1]),
    "veri": (["GB", "MB", "TB"], [45, 40, 15]),
    "guc": (["kW", "W", "V"], [30, 40, 30]),
    "sicaklik": (["C"], [1]),
}
_BUYUK_OLCU = {"km", "m", "kg", "g", "L", "mL", "MB", "GB", "W", "kW", "m2"}
_OLCU_TAVAN = {"km": 20000, "m": 9999, "kg": 9999, "g": 9999, "L": 9999, "mL": 9999, "MB": 99999, "GB": 9999,
               "W": 9999, "kW": 9999, "m2": 9999}
_BUCUK_OLCU = {"kg", "km", "m", "cm", "L", "GB", "TB", "C", "m2", "V", "kW"}


def _olcu_kucuk(rng, b):
    def ond(lo, hi, p):
        tam = rng.randint(lo, hi)
        kesir = _secim(rng, [("5", 40), ("25", 8), ("75", 8), ("2", 6), ("3", 6), ("4", 4), ("6", 4), ("8", 4)]) \
            if rng.random() < p else ""
        return tam, kesir

    if b == "kg":
        return ond(1, 80, 0.25)
    if b == "g":
        return rng.randrange(50, 1000, 25), ""
    if b == "km":
        return ond(1, 800, 0.15)
    if b == "m":
        return ond(1, 500, 0.12)
    if b == "cm":
        return ond(5, 210, 0.08)
    if b == "mm":
        return ond(1, 100, 0.12)
    if b == "L":
        return ond(1, 60, 0.25)
    if b == "mL":
        return rng.randrange(50, 1000, 25), ""
    if b == "m2":
        return ond(20, 500, 0.06)
    if b == "GB":
        return (rng.choice([1, 2, 4, 8, 16, 32, 64, 128, 256, 512]), "") if rng.random() < 0.75 else ond(1, 100, 0.2)
    if b == "MB":
        return ond(5, 999, 0.1)
    if b == "TB":
        return ond(1, 8, 0.25)
    if b == "kW":
        return ond(1, 300, 0.1)
    if b == "W":
        return rng.randrange(5, 1000, 5), ""
    if b == "V":
        return (rng.choice([3, 5, 9, 12, 24, 110, 220, 230, 380]), "") if rng.random() < 0.7 else ond(1, 40, 0.3)
    if b == "C":
        return ond(1, 45, 0.12)
    raise KeyError(b)


def c1_olcu(rng, alt, ek, grup):
    dogru = alt == "dogru"
    if dogru:
        alt = _secim(rng, [("birim", 50), ("bucuk", 14), ("duz", 12), ("bin_tek", 12), ("bin_cift", 12)])
    birimler, w = _GRUP[grup or rng.choice(sorted(_GRUP))]
    if alt in ("bin_tek", "bin_cift", "duz"):
        cand = [b for b in birimler if b in _BUYUK_OLCU]
        if not cand:
            return None
        b = rng.choice(cand)
    else:
        b = rng.choices(birimler, w)[0]
    idx = rng.randrange(2)
    if alt == "bucuk":
        if b not in _BUCUK_OLCU:
            return None
        tam, _ = _olcu_kucuk(rng, b)
        spec, mod = ("dec", tam, "5", True), "duz"
    elif alt == "birim":
        tam, kesir = _olcu_kucuk(rng, b)
        spec, mod = (("dec", tam, kesir, False) if kesir else ("int", tam)), "duz"
    elif alt in ("bin_tek", "bin_cift", "duz"):
        uret = {"bin_tek": lambda: _bin_katsayi(rng) * 1000, "bin_cift": lambda: _bin_cift(rng), "duz": lambda: _duz(rng)}[alt]
        n = uret()
        for _ in range(60):
            if n <= _OLCU_TAVAN[b]:
                break
            n = uret()
        else:
            return None
        spec, mod = ("int", n), ("duz" if alt == "duz" else "grup")
    else:
        return None
    g, h = yari_olcu(spec, b, ek, idx, mod)
    return (h, h) if dogru else (g, h)


def c1_sayi(rng, alt, ek, sinif):
    dogru = alt == "dogru"
    if dogru:
        alt = _secim(rng, [("kucuk", 26), ("orta", 14), ("bin_tek", 12), ("bin_cift", 14), ("duz", 22), ("milyon", 12)])
    mod = "grup"
    if alt == "kucuk":
        if not dogru:
            return None
        spec = ("int", rng.randint(1, 9))
    elif alt == "orta":
        if not dogru:
            return None
        spec = ("int", rng.randint(10, 999))
    elif alt == "bin_tek":
        spec = ("int", _bin_katsayi(rng) * 1000)
    elif alt == "bin_cift":
        spec = ("int", _bin_cift(rng))
    elif alt == "duz":
        n = _duz(rng)
        while ek and 1000 <= n <= 2100:  # bağlamsız yalın yıl benzeri sayı üretme
            n = _duz(rng)
        spec, mod = ("int", n), "duz"
    elif alt == "milyon":
        spec, mod = _milyon_spec(rng)
    else:
        return None
    g, h = yari_sayi(spec, ek, mod)
    return (h, h) if dogru else (g, h)


def c1_yuzde(rng, alt, ek):
    dogru = alt == "dogru"
    tur = _secim(rng, [("int", 40), ("dec", 28), ("bucuk", 32)])
    if tur == "int":
        tam = rng.choice(V._YUZDE_INT) if rng.random() < 0.75 else rng.randint(1, 100)
        g, h = yari_yuzde(tam, ek=ek)
    elif tur == "dec":
        tam = rng.randint(0, 40) if rng.random() < 0.85 else rng.randint(41, 150)
        kesir = _secim(rng, [("5", 40), ("25", 10), ("75", 8), ("2", 8), ("3", 8), ("1", 6), ("8", 6), ("05", 7), ("15", 7)])
        g, h = yari_yuzde(tam, kesir, False, ek)
    else:
        g, h = yari_yuzde(rng.randint(1, 45), "5", True, ek)
    return (h, h) if dogru else (g, h)


def c1_saat(rng, alt, ek, sinif):
    dogru = alt == "dogru"
    if dogru:
        alt = "saat" if sinif == "saat_ns" else _secim(rng, [("saat", 70), ("tam", 30)])
    if alt == "bucuk":
        if sinif != "saat":
            return None
        g, h = yari_saat(rng.randint(1, 12), 30, "bucuk", ek)
    elif alt == "tam":
        g, h = yari_saat(rng.randint(1, 12), 0, "tam", ek)
    else:
        hh = rng.choices(range(1, 24), [1, 1, 1, 2, 3, 4, 6, 8, 9, 9, 8, 8, 9, 9, 9, 8, 8, 9, 8, 6, 4, 2, 1])[0]
        m = rng.choices([30, 15, 45, 0, 5, 10, 20, 40, 50, 55, 25, 35, rng.randint(1, 59)],
                        [24, 12, 12, 7, 5, 6, 6, 4, 4, 3, 3, 3, 8])[0]
        g, h = yari_saat(hh, m, "iki_nokta", ek, sifirli=(hh < 10 and rng.random() < 0.25))
    return (h, h) if dogru else (g, h)


def _tarih_degeri(rng, gunay=False):
    yil = rng.randint(1970, 2030) if rng.random() < 0.7 else rng.randint(1900, 2035)
    ay = rng.randint(1, 12)
    gun = rng.randint(1, calendar.monthrange(yil, ay)[1])
    if gunay and gun == 1:
        gun = rng.randint(2, 28)
    return gun, ay, yil


def c1_tarih(rng, alt, ek, sb_alt):
    dogru = alt == "dogru"
    if sb_alt == "yil":
        if not dogru:
            return None
        yil = rng.randint(1950, 2035)
        h = V.kur_yil(yil, None).yazili
        return h, h
    tur = _secim(rng, [("tam", 55), ("gunay", 45)])
    gun, ay, yil = _tarih_degeri(rng, gunay=(tur == "gunay"))
    g, h = yari_tarih(gun, ay, yil if tur == "tam" else None, ek)
    return (h, h) if dogru else (g, h)


def c1_derece(rng, alt, ek, sinif):
    dogru = alt == "dogru"
    if sinif == "bakiye":
        n = rng.choice([50, 100, 250, 500, 1250, 2000, 4000]) if rng.random() < 0.7 else rng.randint(10, 9999)
        mod = "grup" if (n >= 1000 and n % 1000 == 0 and rng.random() < 0.5) else "duz"
        g, h = yari_eksi(n, "", "TL", False, ek, mod)
        return (h, h) if dogru else (g, h)
    birim = "C" if rng.random() < 0.3 else "derece"
    r = rng.random()
    if r < 0.6:
        g, h = yari_eksi(rng.randint(1, 35), "", birim, False, ek)
    elif r < 0.8:
        g, h = yari_eksi(rng.randint(1, 30), _secim(rng, [("5", 50), ("2", 15), ("3", 15), ("8", 10), ("25", 10)]),
                         birim, False, ek)
    else:
        g, h = yari_eksi(rng.randint(1, 30), "5", birim, True, ek)
    return (h, h) if dogru else (g, h)


def _tel_rakam(rng):
    if rng.random() < 0.75:
        alan = "05" + rng.choice("345") + rng.choice("0123456789")
    else:
        alan = "0" + rng.choice(["212", "216", "312", "232", "224", "242", "322", "352"])
    return alan + "".join(rng.choice("0123456789") for _ in range(7))


def c1_tel(rng, alt, ek):
    dogru = alt == "dogru"
    r = _tel_rakam(rng)
    arti90 = rng.random() < 0.10
    bicim = rng.choice(["bitisik", "yarim"]) if arti90 else rng.choice(["bitisik", "sifir_ayri", "dort_yedi", "dort_uc_dort"])
    g, h = yari_telefon(r, bicim, arti90, ek)
    return (h, h) if dogru else (g, h)


def c1_kod(rng, alt, ek, sb_alt=None):
    """Kod / PIN / posta kodu / numara: rakam rakam, noktasız; yalnız zaten doğru biçim (girdi = hedef)."""
    if alt != "dogru" or ek:
        return None
    n = 5 if sb_alt == "posta" else _secim(rng, [(3, 8), (4, 35), (5, 15), (6, 20), (8, 8), (9, 5), (10, 4), (11, 5)])
    while True:
        r = "".join(rng.choice("0123456789") for _ in range(n))
        if rng.random() < 0.2:
            r = r[0] + r[0] + r[2:]
        if n == 4 and 1000 <= int(r) <= 2100:
            continue
        break
    h = V.kur_kod(r).yazili
    return h, h


C1_ALT_SINIF = {
    "bin_tek": [("para", .40), ("olcu", .12), ("sayi", .30), ("sayi_ek", .18)],
    "bin_cift": [("para", .40), ("olcu", .10), ("sayi", .30), ("sayi_ek", .20)],
    "milyon": [("para", .38), ("sayi", .40), ("sayi_ek", .22)],
    "duz": [("para", .38), ("olcu", .14), ("sayi", .32), ("sayi_ek", .16)],
    "birim": [("para", .25), ("olcu", .75)],
    "yuzde": [("yuzde", 1.0)],
    "bucuk": [("olcu", .55), ("saat", .45)],
    "saat": [("saat", .60), ("saat_ns", .40)],
    "tarih": [("tarih", 1.0)],
    "eksi": [("derece", .72), ("bakiye", .28)],
    "telefon": [("tel", 1.0)],
    "dogru": [("para", .17), ("olcu", .12), ("yuzde", .12), ("sayi", .17), ("sayi_ek", .05), ("saat", .08),
              ("saat_ns", .05), ("tarih", .12), ("derece", .04), ("tel", .04), ("bakiye", .04), ("kod", .05)],
}
C1_ALT_AGIRLIK = {
    "bin_tek": 480, "bin_cift": 440, "milyon": 440, "duz": 480, "birim": 700, "yuzde": 520, "bucuk": 420,
    "saat": 560, "tarih": 480, "eksi": 330, "telefon": 330, "dogru": 700, "karisik": 620,
}


def c1_varlik(rng, alt, sinif, ek, sb_alt):
    if sinif in ("sayi", "sayi_ek"):
        return c1_sayi(rng, alt, ek, sinif)
    if sinif == "para":
        return c1_para(rng, alt, ek)
    if sinif == "olcu":
        return c1_olcu(rng, alt, ek, sb_alt)
    if sinif == "yuzde":
        return c1_yuzde(rng, alt, ek)
    if sinif in ("saat", "saat_ns"):
        return c1_saat(rng, alt, ek, sinif)
    if sinif == "tarih":
        return c1_tarih(rng, alt, ek, sb_alt)
    if sinif in ("derece", "bakiye"):
        return c1_derece(rng, alt, ek, sinif)
    if sinif == "tel":
        return c1_tel(rng, alt, ek)
    if sinif == "kod":
        return c1_kod(rng, alt, ek, sb_alt)
    raise KeyError(sinif)


# karışık cümlelerde birinci (rakamlı) varlığın alt biçimleri
_KARISIK_E = {
    "sayi": [("bin_tek", 3), ("duz", 3), ("dogru", 4), ("milyon", 1), ("bin_cift", 2)],
    "para": [("bin_tek", 3), ("duz", 3), ("birim", 3), ("dogru", 3), ("bin_cift", 2)],
    "olcu": [("birim", 6), ("bucuk", 2), ("dogru", 3), ("duz", 1)],
    "yuzde": [("yuzde", 6), ("dogru", 3)],
    "saat": [("saat", 6), ("dogru", 3)],
    "tarih": [("tarih", 6), ("dogru", 3)],
    "derece": [("eksi", 6), ("dogru", 3)],
    "tel": [("telefon", 6), ("dogru", 3)],
}


def c1_karisik(rng, test, durum):
    sb = sablon_sec(rng, "yari", "karisik", test)
    varliklar = []
    kalir_hepsi = True
    for ad, alt, ek in varlik_yuvalari(sb):
        kat, _, sub = (alt or "").partition("_")
        if ad == "e":
            sinif = "saat_ns" if kat == "saat" else kat
            ealt = _secim(rng, _KARISIK_E[kat])
            ent = c1_varlik(rng, ealt, sinif, ek, sub or None)
            if ent is None:
                return None
        else:
            v = V.ORNEKLEYICILER[kat](rng, sub or None, None, "yaziyla", False)
            ent = (v.sozlu, v.yazili)
        varliklar.append(ent)
        if ent[0] != ent[1]:
            kalir_hepsi = False
    if kalir_hepsi:
        return None
    buyuk = rng.random() < 0.4
    g, h = kur_cumle(rng, sb, buyuk, varliklar)
    return g, h, sb, {"alt": "karisik", "ekli": sb.ek is not None, "ozdes": False}


def c1_tek(rng, alt, test, durum):
    if alt == "karisik":
        return c1_karisik(rng, test, durum)
    sinif = _secim(rng, C1_ALT_SINIF[alt])
    ekli = True if sinif == "sayi_ek" else rng.random() < P_EK

    def uygun(sb):
        # yıl şablonları (2026 yılında) yalnız zaten doğru biçim satırlarında kullanılır
        return not (sb.sinif == "tarih" and sb.alt == "yil" and alt != "dogru")

    sb = sablon_sec(rng, "yari", sinif, test, ekli, uygun)
    ent = c1_varlik(rng, alt, sinif, sb.ek, sb.alt)
    if ent is None:
        return None
    ozdes = ent[0] == ent[1]
    if ozdes and alt not in ("dogru", "milyon"):
        return None
    buyuk = rng.random() < 0.4
    g, h = kur_cumle(rng, sb, buyuk, [ent])
    return g, h, sb, {"alt": alt, "ekli": sb.ek is not None, "ozdes": ozdes}


# ======================================================================================
# C2 · bitişik yazılmış sayılar
# ======================================================================================
# Bir varlık için (Varlik, spans) kurulur; spans: sözlü sözcük dizisinde art arda gelen sayı sözcüklerinin (başlangıç, uzunluk)
# aralıkları. Birleştirme yalnız bu aralıkların içinde yapılır; birim/para/ay sözcükleri ayrı kalır.

def bitistir(toks, spans, sec):
    """sec: 'tam' (aralık içindeki bütün sınırlar) ya da birleşecek sınırların kümesi (i: toks[i] ile toks[i+1])."""
    adaylar = []
    for a, n in spans:
        for i in range(a, a + n - 1):
            if toks[i] == "bin" and toks[i + 1].startswith("bir"):  # binbir: özel ad kalıbıyla karışır
                continue
            adaylar.append(i)
    secili = set(adaylar) if sec == "tam" else (set(sec) & set(adaylar))
    if not secili:
        return None
    out, i = [], 0
    while i < len(toks):
        s = toks[i]
        while i in secili:
            i += 1
            s += toks[i]
        out.append(s)
        i += 1
    return out


def bitistir_rastgele(rng, toks, spans):
    adaylar = []
    for a, n in spans:
        for i in range(a, a + n - 1):
            if toks[i] == "bin" and toks[i + 1].startswith("bir"):
                continue
            adaylar.append(i)
    if not adaylar:
        return None
    if rng.random() < 0.30:
        sec = "tam"
    else:
        sec = {i for i in adaylar if rng.random() < 0.5}
        if not sec:
            sec = {rng.choice(adaylar)}
    return bitistir(toks, spans, sec)


def _c2_cok_sozcuklu(n):
    return len(S.sayi_kelimeleri(n)) >= 2


def _c2_n(rng, lo=11, hi=99999):
    while True:
        r = rng.random()
        if r < 0.30:
            n = rng.randint(11, 99)
        elif r < 0.62:
            n = rng.choice([150, 250, 350, 450, 120, 125, 175]) if rng.random() < 0.3 else rng.randint(101, 999)
        elif r < 0.88:
            n = rng.randint(2, 99) * 1000 + rng.choice([0, 0, 500, 250, rng.randint(1, 999)])
        else:
            n = rng.choice([1200, 1300, 1450, 1700, 1750, 1850, 1950, 2020, 2500, 3600])
        if lo <= n <= hi and _c2_cok_sozcuklu(n):
            return n


def c2_kardinal(n, ek=None):
    v = V.kur_kardinal(n, "rakamla", ek)
    return v, [(0, len(v.sozlu.split()))]


def c2_para(n, kurus=None, birim="TL", ek=None):
    if birim == "TL":
        v = V.kur_para(lira=n, kurus=kurus, ek=ek)
    else:
        kurus = None
        v = V.kur_para(lira=n, birim=birim, ek=ek)
    toks = v.sozlu.split()
    spans = [(0, len(S.sayi_kelimeleri(n)))]
    if kurus:
        k = len(S.sayi_kelimeleri(kurus))
        spans.append((len(toks) - 1 - k, k))
    return v, spans


def c2_olcu(n, birim, ek=None, soz_idx=0):
    v = V.kur_olcu(n, "", birim, soz_idx, False, False, ek)
    return v, [(0, len(S.sayi_kelimeleri(n)))]


def c2_yuzde(n, ek=None):
    v = V.kur_yuzde(n, "", False, False, ek)
    return v, [(1, len(S.sayi_kelimeleri(n)))]


def c2_saat(h, m=None, ek=None):
    """m None: yalnız saat (saat on birde). Dakikalı: on dört otuz beşte."""
    if m is None:
        v = V.kur_saat(h, bicim="tam", ek=ek)
        return v, [(0, len(S.sayi_kelimeleri(h)))]
    v = V.kur_saat(h, m, False, "dk", ek)
    hk = len(S.sayi_kelimeleri(h))
    spans = [(0, hk)]
    if m >= 10:
        spans.append((hk, len(S.sayi_kelimeleri(m))))
    return v, spans


def c2_tarih(tur, gun=None, ay=None, yil=None, ek=None):
    if tur == "yil":
        v = V.kur_yil(yil, ek)
        return v, [(0, len(S.sayi_kelimeleri(yil)))]
    gk = len(S.sayi_kelimeleri(gun))
    if tur == "gunay":
        v = ay_duzelt(V.kur_tarih(gun, ay, None, ek, False), ay, ek)
        return v, [(0, gk)]
    v = V.kur_tarih(gun, ay, yil, ek, False)
    return v, [(0, gk), (gk + 1, len(S.sayi_kelimeleri(yil)))]


def c2_girdi(v, spans, sec):
    out = bitistir(v.sozlu.split(), spans, sec)
    return None if out is None else " ".join(out)


C2_AILE_AGIRLIK = {"kardinal": 700, "para": 700, "olcu": 500, "yuzde": 350, "saat": 400, "tarih": 350}


def c2_varlik(rng, aile, ek, alt):
    if aile == "kardinal":
        v, sp = c2_kardinal(_c2_n(rng), ek)
    elif aile == "para":
        r = rng.random()
        if r < 0.15:
            birim = _secim(rng, [("dolar", 45), ("avro", 30), ("euro", 10), ("sterlin", 15)])
            v, sp = c2_para(_c2_n(rng, 11, 5000), None, birim, ek)
        else:
            n = _c2_n(rng, 11, 99999)
            kurus = rng.choice([25, 50, 75, 90, 95, 99, 35, 45, 12, 15]) if rng.random() < 0.15 else None
            v, sp = c2_para(n, kurus, "TL", ek)
    elif aile == "olcu":
        birimler, w = _GRUP[alt or rng.choice(sorted(_GRUP))]
        b = rng.choices(birimler, w)[0]
        if b == "C":
            n = rng.randint(11, 45)
        elif b in ("g", "mL"):
            n = rng.choice([150, 250, 350, 450, 125, 175, 225, 275, 325, 375, 425, 475, 525, 575, 625, 675, 725, 775, 825, 875, 925, 975])
        elif b in ("W", "kW"):
            n = _c2_n(rng, 11, 2000) if b == "W" else rng.randint(11, 300)
            if not _c2_cok_sozcuklu(n):
                return None
        elif b in ("km", "m", "cm", "mm", "m2"):
            n = _c2_n(rng, 11, 900)
        elif b == "V":
            n = rng.choice([12, 24, 110, 220, 230, 380])
        elif b == "GB":
            n = rng.choice([16, 32, 64, 128, 256, 512])
        elif b in ("MB", "TB"):
            n = rng.randint(11, 900) if b == "MB" else rng.randint(11, 40)
        else:
            n = _c2_n(rng, 11, 80)
        if not _c2_cok_sozcuklu(n):
            return None
        v, sp = c2_olcu(n, b, ek, rng.randrange(2))
    elif aile == "yuzde":
        n = rng.choice([x for x in range(11, 100) if x % 10])
        v, sp = c2_yuzde(n, ek)
    elif aile == "saat":
        r = rng.random()
        if r < 0.40:
            h = rng.choice([11, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23])
            v, sp = c2_saat(h, None, ek)
        else:
            h = rng.randint(1, 23)
            m = rng.choice([x for x in range(11, 60) if x % 10 or x in (20, 30, 40, 50)])
            if not (_c2_cok_sozcuklu(h) or _c2_cok_sozcuklu(m)):
                m = rng.choice([x for x in range(11, 60) if x % 10 and x > 20])
            v, sp = c2_saat(h, m, ek)
    elif aile == "tarih":
        tur = alt or "tam"
        yil = rng.randint(1970, 2030)
        ay = rng.randint(1, 12)
        gun = rng.choice([x for x in range(11, calendar.monthrange(yil, ay)[1] + 1) if x % 10 or x == 31 or x in (20, 30)])
        if tur == "yil":
            v, sp = c2_tarih("yil", yil=yil, ek=ek)
        else:
            if tur == "gunay" and not _c2_cok_sozcuklu(gun):
                gun = rng.choice([11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28])
            v, sp = c2_tarih(tur, gun, ay, yil if tur == "tam" else None, ek)
    else:
        raise KeyError(aile)
    return v, [s for s in sp if s[1] >= 2]


def c2_tek(rng, aile, test, durum):
    sb = sablon_sec(rng, "bitisik", aile, test, rng.random() < 0.33)
    r = c2_varlik(rng, aile, sb.ek, sb.alt)
    if r is None:
        return None
    v, sp = r
    if not sp:
        return None
    toks = bitistir_rastgele(rng, v.sozlu.split(), sp)
    if toks is None:
        return None
    buyuk = rng.random() < 0.4
    g, h = kur_cumle(rng, sb, buyuk, [(" ".join(toks), v.yazili)])
    return g, h, sb, {"alt": aile, "ekli": sb.ek is not None, "ozdes": False}


# ======================================================================================
# C3 · saat deyişleri
# ======================================================================================
# fiil: (saat sayısının eki, kip). z: zarf-fiil (kala/geçe), p: şimdiki yüklem, d: geçmiş yüklem.
FIIL = {
    "kala": ("yonelme", "z"), "var": ("yonelme", "p"), "kalıyor": ("yonelme", "p"),
    "vardı": ("yonelme", "d"), "kalmıştı": ("yonelme", "d"), "kaldı": ("yonelme", "d"),
    "geçe": ("belirtme", "z"), "geçiyor": ("belirtme", "p"), "geçiyordu": ("belirtme", "d"),
    "geçmişti": ("belirtme", "d"), "geçti": ("belirtme", "d"),
}
C3_FIIL_AGIRLIK = {"kala": 560, "geçe": 560, "var": 480, "geçiyor": 420, "geçiyordu": 150, "kalmıştı": 100,
                   "vardı": 90, "geçmişti": 90, "kalıyor": 20, "kaldı": 15, "geçti": 15}
VAKIT = {"sabah": [5, 6, 7, 8, 9, 10, 11], "öğlen": [12, 1, 2], "öğleden sonra": [1, 2, 3, 4, 5, 6],
         "akşam": [4, 5, 6, 7, 8, 9, 10], "gece": [10, 11, 12, 1, 2, 3, 4]}
C3_DK = ([(15, 32), (5, 13), (10, 15), (20, 11), (25, 8), (1, 1), (2, 2), (3, 1), (4, 1), (6, 1), (7, 1), (8, 1), (9, 1)]
         + [(d, 0.75) for d in (11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29)])


def kur_saat_deyis(saat, dk, fiil, saat_sozcugu=False, dakika_sozcugu=False):
    """(girdi, hedef): saat 1-12 ve dakika rakam, `çeyrek` sözcük kalır; saat sayısı fiile göre yönelme/belirtme alır."""
    ek, _ = FIIL[fiil]
    hv = V.kur_saat(saat, bicim="tam", ek=ek)
    g, h = [hv.sozlu], [hv.yazili]
    if dk == 15:
        g.append("çeyrek")
        h.append("çeyrek")
    else:
        g += S.sayi_kelimeleri(dk)
        h.append(str(dk))
        if dakika_sozcugu:
            g.append("dakika")
            h.append("dakika")
    g.append(fiil)
    h.append(fiil)
    if saat_sozcugu:
        g.insert(0, "saat")
        h.insert(0, "saat")
    return " ".join(g), " ".join(h)


def c3_tek(rng, fiil, test, durum):
    _, kip = FIIL[fiil]
    etiketler = {"z": ["z"], "p": ["p", "y"], "d": ["d", "y"]}[kip]
    adaylar = [sb for t in etiketler for sb in sablon_havuzu("saat_deyis", t, test)]
    sb = rng.choice(adaylar)
    sabit, saatler = None, list(range(1, 13))
    if "{vakit}" in sb.metin:
        vakit = rng.choice(sorted(VAKIT))
        sabit, saatler = {"vakit": vakit}, VAKIT[vakit]
    h = durum.dengeli(rng, "saat", saatler)
    dk = _secim(rng, C3_DK)
    ent = kur_saat_deyis(h, dk, fiil, rng.random() < 0.38, dk != 15 and rng.random() < 0.12)
    buyuk = rng.random() < 0.4
    g, hd = kur_cumle(rng, sb, buyuk, [ent], sabit)
    return g, hd, sb, {"alt": fiil, "ekli": True, "ozdes": False, "saat": h, "dk": dk, "fiil": fiil}


# ======================================================================================
# C4 · ayın günü
# ======================================================================================
C4_EK_TURLERI = ["bulunma", "ayrilma", "yonelme", "belirtme", "iyelik3"]
C4_ONEKLER = [("ayın", 30), ("her ayın", 16), ("bu ayın", 12), ("gelecek ayın", 8), ("geçen ayın", 6),
              ("önümüzdeki ayın", 4)]
AY_GEN = DOLGU["ay_gen"]
AY_GUN = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def kur_ayin_gunu(onek, gun, ek):
    """('ayın on beşinde', "ayın 15'inde")."""
    gk = S.sayi_kelimeleri(gun)
    son, yaz = iyelik_durum(gk[-1], ek)
    return f"{onek} " + " ".join(gk[:-1] + [son]), f"{onek} {gun}'{yaz}"


def c4_tek(rng, ek, test, durum):
    sb = rng.choice([s for s in sablon_havuzu("tarih", ek, test)])
    if rng.random() < 0.24:
        ay = rng.randrange(12)
        onek, azami = AY_GEN[ay], AY_GUN[ay]
        tur = "ay"
    else:
        onek, azami, tur = _secim(rng, C4_ONEKLER), 31, "ayin"
    gun = durum.dengeli(rng, "gun", list(range(1, azami + 1)))
    ent = kur_ayin_gunu(onek, gun, ek)
    buyuk = rng.random() < 0.4
    g, h = kur_cumle(rng, sb, buyuk, [ent])
    return g, h, sb, {"alt": ek, "ekli": True, "ozdes": False, "gun": gun, "onek": tur}


# ======================================================================================
# Bölüm üretimi
# ======================================================================================

def _plan(rng, toplam, agirlik):
    k = kota(toplam, agirlik)
    plan = [a for a in agirlik for _ in range(k[a])]
    rng.shuffle(plan)
    return plan


def uret_bolum(bolum, toplam, seed, gorulen):
    """Bir bölümün kayıtlarını üretir (meta alanlı); `gorulen` bölümler arası hedef kümesidir."""
    test = bolum == "test"
    kat_sayilari = kota(toplam, KAT_AGIRLIK)
    kayitlar = []
    for kat in KATEGORILER:
        rng = random.Random(f"{seed}-v2c-{bolum}-{kat}")
        durum = Durum()
        if kat == "yari":
            plan, fn = _plan(rng, kat_sayilari[kat], C1_ALT_AGIRLIK), c1_tek
        elif kat == "bitisik":
            plan, fn = _plan(rng, kat_sayilari[kat], C2_AILE_AGIRLIK), c2_tek
        elif kat == "saat_deyis":
            plan, fn = _plan(rng, kat_sayilari[kat], C3_FIIL_AGIRLIK), c3_tek
        else:
            k = kota(kat_sayilari[kat], {e: 1 for e in C4_EK_TURLERI})
            plan = [e for e in C4_EK_TURLERI for _ in range(k[e])]
            rng.shuffle(plan)
            fn = c4_tek
        for oge in plan:
            for deneme in range(4000):
                r = fn(rng, oge, test, durum)
                if r is None:
                    continue
                g, h, sb, meta = r
                if len(g.encode("utf-8")) > BAYT_SINIRI or len(h.encode("utf-8")) > BAYT_SINIRI:
                    continue
                if h in gorulen:
                    continue
                gorulen.add(h)
                kayitlar.append({"girdi": g, "hedef": h, "kategori": kat, "sablon": sb.id, "_meta": meta})
                break
            else:
                raise RuntimeError(f"{bolum}/{kat}/{oge}: benzersiz örnek üretilemedi")
    rng = random.Random(f"{seed}-v2c-{bolum}-karistir")
    rng.shuffle(kayitlar)
    return kayitlar


def uret(seed=2203, train=14000, validation=400, test=500):
    """{'test','validation','train'} -> kayıt listesi. Test önce üretilir; hedefler bölümler arası ayrık kalır."""
    gorulen: set[str] = set()
    sonuc = {}
    for bolum, adet in (("test", test), ("validation", validation), ("train", train)):
        sonuc[bolum] = uret_bolum(bolum, adet, seed, gorulen)
    return sonuc


# ======================================================================================
# Ölçümler
# ======================================================================================

def ilk_sozcuk(s: str) -> str:
    t = lower_tr(s).split()
    return re.sub(r"[.,!?;:\"…]+$", "", t[0]) if t else ""


def olc(kayitlar) -> dict:
    n = len(kayitlar)
    sab = Counter(r["sablon"] for r in kayitlar)
    kat_sab = defaultdict(set)
    kat_say = Counter()
    for r in kayitlar:
        kat_sab[r["kategori"]].add(r["sablon"])
        kat_say[r["kategori"]] += 1
    ilk_g = Counter(ilk_sozcuk(r["girdi"]) for r in kayitlar)
    ilk_h = Counter(ilk_sozcuk(r["hedef"]) for r in kayitlar)
    o = {
        "satir": n, "kategori_satir": dict(kat_say),
        "sablon_sayisi": len(sab), "kategori_sablon": {k: len(v) for k, v in kat_sab.items()},
        "en_cok_sablon_pay": round(max(sab.values()) / n, 4) if n else 0,
        "en_cok_sablon": sab.most_common(1)[0] if n else None,
        "en_cok_ilk_sozcuk_girdi": (ilk_g.most_common(1)[0][0], round(ilk_g.most_common(1)[0][1] / n, 4)) if n else None,
        "en_cok_ilk_sozcuk_hedef": (ilk_h.most_common(1)[0][0], round(ilk_h.most_common(1)[0][1] / n, 4)) if n else None,
    }
    c1 = [r for r in kayitlar if r["kategori"] == "yari"]
    if c1:
        alt = Counter(r["_meta"]["alt"] for r in c1)
        o["c1_alt"] = dict(sorted(alt.items()))
        o["c1_ekli_pay"] = round(sum(r["_meta"]["ekli"] for r in c1) / len(c1), 4)
        o["c1_ozdes_pay"] = round(sum(r["girdi"] == r["hedef"] for r in c1) / len(c1), 4)
    c3 = [r for r in kayitlar if r["kategori"] == "saat_deyis"]
    if c3:
        o["c3_saat"] = dict(sorted(Counter(r["_meta"]["saat"] for r in c3).items()))
        sozc = Counter()
        for r in c3:
            for t in ("kala", "geçe", "var", "geçiyor", "çeyrek"):
                if t in r["girdi"].lower().replace(".", "").replace(",", "").split():
                    sozc[t] += 1
        o["c3_sozcuk"] = dict(sozc)
        o["c3_ceyrek_pay"] = round(sozc["çeyrek"] / len(c3), 4)
        o["c3_fiil"] = dict(Counter(r["_meta"]["fiil"] for r in c3))
    c4 = [r for r in kayitlar if r["kategori"] == "tarih"]
    if c4:
        o["c4_gun"] = dict(sorted(Counter(r["_meta"]["gun"] for r in c4).items()))
        o["c4_ek"] = dict(Counter(r["_meta"]["alt"] for r in c4))
    return o


def yaz_dosya(yol: Path, kayitlar) -> None:
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        for r in kayitlar:
            f.write(json.dumps({k: r[k] for k in ("girdi", "hedef", "kategori", "sablon")}, ensure_ascii=False) + "\n")


def ornekler(kayitlar, rng, adet=4):
    """Her alt biçimden rastgele örnekler (girdi => hedef)."""
    grup = defaultdict(list)
    for r in kayitlar:
        m = r["_meta"]
        grup[(r["kategori"], m["alt"] if r["kategori"] in ("yari", "bitisik") else ("tarih" if r["kategori"] == "tarih" else "saat_deyis"))].append(r)
    cikti = {}
    for k in sorted(grup):
        liste = grup[k]
        cikti[f"{k[0]}/{k[1]}"] = [f"{r['girdi']} => {r['hedef']}" for r in rng.sample(liste, min(adet, len(liste)))]
    return cikti


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v2")
    ap.add_argument("--seed", type=int, default=2203)
    ap.add_argument("--train", type=int, default=14000)
    ap.add_argument("--validation", type=int, default=400)
    ap.add_argument("--test", type=int, default=500)
    ap.add_argument("--rapor", action="store_true", help="ölçümleri ve örnekleri JSON olarak yazdır")
    a = ap.parse_args(argv)
    sonuc = uret(a.seed, a.train, a.validation, a.test)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for bolum, kayitlar in sonuc.items():
        yaz_dosya(out / f"c-{bolum}.jsonl", kayitlar)
    ozet = {b: dict(Counter(r["kategori"] for r in k)) for b, k in sonuc.items()}
    print(json.dumps({"adet": {b: len(k) for b, k in sonuc.items()}, "kategori": ozet}, ensure_ascii=False))
    if a.rapor:
        rap = {"olcum_train": olc(sonuc["train"]),
               "ornekler": ornekler(sonuc["train"], random.Random(f"{a.seed}-ornek"))}
        print(json.dumps(rap, ensure_ascii=False, indent=1))
    return 0


# ======================================================================================
# Taşıyıcı cümle şablonları
# ======================================================================================
# Sözdizimi: {E} · {E:ek} · {E.alt} · {E.alt:ek}  (ana varlık)
#            {e.sınıf_alt} (karışık cümlede rakamlı varlık) · {s.kategori_alt} (karışık cümlede sözlü varlık)
#            {dolgu} (DOLGU listesi) · {vakit} (yalnız saat deyişleri: sabah/akşam/gece...)
# Her satır bir şablondur; kimlik: v2c-<kategori>-<sınıf>-<sıra>.

TASLAK = {}

# ----------------------------------------------------------------------------- C1 yari
TASLAK[("yari", "para")] = """
Faturanın toplamı {E} tuttu
Bu ay elektriğe {E} ödedim
{E} borcum kaldı
Kiramız {E} oldu
Market alışverişi {E} tuttu
Biletin fiyatı kişi başı {E} idi
Müşteri hesabına {E} yatırdı
Telefon faturası bu ay {E} geldi
Servis için {E} ücret istediler
Kasadaki fark {E} çıktı
Maaşıma {E} zam geldi
Hediye çeki {E} değerinde
Tamirci bana {E} dedi
Düğün masrafı {E} civarında kaldı
Yarınki siparişin toplamı {E} olacak
Kargo dahil {E} ödeyeceksin
Bu ceketi {E:yonelme} aldım
Eski telefonu {E:yonelme} sattık
Gecelik ücretler {E:ayrilma} başlıyor
Bu işe {E:ayrilma} aşağı kimse bakmaz
Biletler {E:bulunma} satılıyor
Kitap internette {E:bulunma} listelenmiş
Kasiyer bana {E:belirtme} bozuk para olarak verdi
Annem {E:belirtme} cebime koydu
Hesaptan {E:belirtme} çektim
Pazara sadece {E:vasita} gittim
Tatile {E:vasita} çıktık
{E:lik} market alışverişi yaptık
Bana {E:lik} bir hediye çeki verdiler
{E:lik} fatura geldi bu ay
{E:ilgi} üzerindeki alışverişlerde kargo bedava
{E:ilgi} yarısını bugün ödedim
Borcun {E:iyelik3} ödendi
Müşterinin {E:iyelik3} henüz yatmadı
"""

TASLAK[("yari", "olcu")] = """
Sepete {E.agirlik} elma koydum
Kasap bana {E.agirlik} kıyma tarttı
Valizim {E.agirlik} geldi
Bu paket tam {E.agirlik} ağırlığında
Bebek doğduğunda {E.agirlik} idi
{E.agirlik:lik} bir çuval un aldım
Çantaya {E.agirlik:yonelme} kadar yük konabilir
Kargo {E.agirlik:ayrilma} ağır paketleri almıyor
Terazi {E.agirlik:belirtme} gösteriyor
Evimiz okula {E.mesafe} uzaklıkta
Sabah koşuda {E.mesafe} yol aldık
Otogara {E.mesafe} kaldı
{E.mesafe:lik} bir yürüyüş yaptık
Sahile {E.mesafe:yonelme} kadar yürüdük
Bir günde {E.mesafe:ayrilma} fazla yürüyemem
Bu depoyla {E.mesafe:belirtme} gidebilirsin
Masanın uzunluğu {E.uzunluk}
Perdeyi {E.uzunluk} kestirdim
Kumaştan {E.uzunluk} aldım
Çiviler {E.uzunluk} boyunda
{E.uzunluk:lik} bir şerit metre buldum
Çıtayı {E.uzunluk:yonelme} kadar kısalttım
Kablo {E.uzunluk:ayrilma} uzun olmamalı
Oğlumun boyu {E.boy} oldu
Takıma boyu {E.boy} olan oyuncular alınacak
{E.boy:lik} dolap kapağı lazım
Fidan {E.boy:yonelme} ulaştı
Depoya {E.hacim} benzin attım
Tarif için {E.hacim} süt gerekiyor
Şişenin hacmi {E.hacim}
{E.hacim:lik} bir kazan aldık
Bidonu {E.hacim:yonelme} kadar doldurdum
Bu kap {E.hacim:ayrilma} fazla almaz
Günde {E.hacim:belirtme} içmeye çalışıyorum
Telefonumda {E.veri} boş yer kaldı
Yeni bilgisayarın depolaması {E.veri}
Dosyanın boyutu {E.veri}
{E.veri:lik} bir bellek kartı aldım
Hafızayı {E.veri:yonelme} yükselttik
Paket ayda {E.veri:ayrilma} fazla internet vermiyor
Yedekleme {E.veri:belirtme} buldu
Dairemiz {E.alan} büyüklüğünde
Bahçe {E.alan} yer kaplıyor
{E.alan:lik} bir ofis kiraladık
Arsa {E.alan:ayrilma} küçük değil
Cihaz {E.guc} güç çekiyor
Şarj aleti {E.guc} çıkış veriyor
{E.guc:lik} bir ampul taktım
Priz {E.guc:ayrilma} fazlasını kaldırmaz
Cihaz {E.guc:belirtme} geçince devre dışı kalıyor
Oda sıcaklığı {E.sicaklik} civarında
Fırını {E.sicaklik:yonelme} ısıttım
Su {E.sicaklik:bulunma} kaynıyor
Fırın {E.sicaklik:ayrilma} fazla ısınmıyor
Ateşim {E.sicaklik} çıktı
"""

TASLAK[("yari", "yuzde")] = """
Okulda başarı oranı {E} oldu
Ürünlerde {E} indirim var
Enflasyon {E} olarak açıklandı
Bu yıl zam {E} oranında geldi
Bankadan {E} faizle kredi çektik
{E} kullanıcı bu özelliği beğendi
Havada nem oranı {E} civarında
Seçime katılım {E} oldu
Kampanya her üründe {E} indirim sunuyor
Pilin {E:iyelik3} kalmış
{E:iyelik3} henüz gelmedi
Öğrencilerin {E:iyelik3} sınavı geçti
Faiz oranı {E:yonelme} yükseldi
Zam oranı {E:ayrilma} aşağı olmayacak
Oy oranı {E:belirtme} geçen partiler Meclis'e girer
{E:ilgi} altında kalanlar elendi
Faiz oranı {E:bulunma} sabit kaldı
{E:lik} bir artış bekleniyor
Kampanyaya {E:vasita} başladık
"""

TASLAK[("yari", "sayi")] = """
Konsere {E} {kalabalik} katıldı
Stadyuma {E} {kalabalik} sığıyor
Bu hafta {E} {adet} sattık
Depoda {E} {adet} var
Köyde {E} {kalabalik} yaşıyor
Videoyu {E} {kalabalik} izlemiş
Hesabın {E} takipçisi var
Sınava {E} {kalabalik} girdi
{E} {adet} sipariş kargoya verildi
Etkinliğe {E} {kalabalik} kayıt oldu
Kütüphanede {E} kitap var
Yarışmaya {E} {kalabalik} başvurdu
Bu yıl {E} adım attım
Şirket {E} {kalabalik} çalıştırıyor
Maçı {E} {kalabalik} izledi
Şu an {E} {kalabalik} çevrimiçi
Hastane geçen yıl {E} {kalabalik} tedavi etti
Fabrikada günde {E} {adet} üretiliyor
Mahalle pazarında {E} {kalabalik} dolaşıyordu
Tren seferi sırasında {E} {kalabalik} taşındı
Okulda {E} {kalabalik} okuyor
Gişeden {E} {adet} çıktı
"""

TASLAK[("yari", "sayi_ek")] = """
Sayaç {E:yonelme} ulaştı
Takipçi sayımız {E:yonelme} çıktı
Kutudaki sayı {E:yonelme} yaklaştı
Üye sayısı {E:ayrilma} aşağı düşmedi
Biletler {E:ayrilma} başlayıp yükseldi
Satış rakamı {E:belirtme} geçti
Ziyaretçi sayısı bu yıl {E:belirtme} buldu
Toplam sayı {E:belirtme} aşmış
Sayaç dün {E:bulunma} kalmıştı
İlan sayısı {E:bulunma} duruyor
{E:ilgi} üzerindeki siparişler ayrıca incelenir
Mesaj sayısı {E:ilgi} altına düştü
Rakamlar {E:vasita} kapandı
"""

TASLAK[("yari", "saat")] = """
Toplantı saat {E:bulunma} başlıyor
Randevum saat {E:bulunma} idi
Uçak saat {E:bulunma} kalkacak
Konser saat {E:bulunma} başlar
Dersimiz saat {E:bulunma} bitiyor
Saat {E:yonelme} kadar bekledim
Mağaza saat {E:yonelme} kadar açık
Saat {E:ayrilma} sonra gelirsen görüşürüz
Çocuklar saat {E:ayrilma} beri bahçede
Saat {E:belirtme} çalmak üzere
Randevu saat {E} olarak verildi
Şu an saat {E}
Servis saat {E} hareket ediyor
Kapılar saat {E} açılacak
Yemek saat {E} hazır
Okulun zili saat {E:vasita} birlikte çalıyor
"""

TASLAK[("yari", "saat_ns")] = """
Toplantı {E:bulunma} başlıyor
Maç {E:bulunma} oynanacak
Otobüs {E:bulunma} kalkıyor
{E:yonelme} kadar buradayım
Dükkân {E:yonelme} kadar açık
{E:ayrilma} itibaren sınav başlıyor
Dün gece {E:ayrilma} beri uyumadım
Alarmı {E:yonelme} kurdum
Duvar saati {E:belirtme} gösteriyordu
Uçuş {E} için bilet aldım
Randevu {E} civarına kaldı
Film {E} bitiyor
"""

TASLAK[("yari", "tarih")] = """
Sınav {E} tarihinde yapılacak
Doğum günüm {E}
Fatura son ödeme tarihi {E}
Tatil {E} başlıyor
Randevu {E} için alındı
Belgeyi {E} tarihli olarak imzaladık
Toplantı {E:bulunma} yapıldı
Etkinlik {E:bulunma} başlayacak
Ödemeyi {E:yonelme} kadar yapın
Siparişi {E:yonelme} teslim edeceğiz
{E:ayrilma} itibaren geçerli olacak
Kayıtlar {E:ayrilma} sonra kapanıyor
Kayıt günü olarak {E:belirtme} seçtik
{E:ilgi} akşamı boş kalmayı düşünüyorum
Şirket {E.yil} yılında kuruldu
Ben {E.yil} yılında doğdum
Bu bina {E.yil} yılında yapılmış
Mezuniyet {E.yil} yılında oldu
"""

TASLAK[("yari", "derece")] = """
Sabah hava {E.sicaklik} idi
Dün gece termometre {E.sicaklik} gösterdi
Kuzeyde sıcaklığın {E.sicaklik} olması bekleniyor
Zirvede hava {E.sicaklik} civarındaydı
Dışarısı {E.sicaklik} buz gibi
Termometre {E.sicaklik:yonelme} düştü
Gece {E.sicaklik:bulunma} don olacak
Hava {E.sicaklik:ayrilma} aşağıya inmedi
Şehir {E.sicaklik:vasita} güne başladı
"""

TASLAK[("yari", "bakiye")] = """
Hesap bakiyem {E} görünüyor
Kartın bakiyesi {E} çıktı
Ay sonunda hesap {E} oldu
Bakiye {E:yonelme} düştü
Hesap {E:yonelme} indi
"""

TASLAK[("yari", "tel")] = """
Beni {E} numarasından arayın
Numaram {E} olarak kayıtlı
Müşteri hizmetleri {E} numarasında
Acil durumda {E} numaralı hattı arayın
Rehberde {E} yazıyor
{E:belirtme} arayıp randevu al
Şu numarayı {E:belirtme} kaydet
Bana {E:bulunma} ulaşabilirsiniz
Dün gece {E:ayrilma} bir arama geldi
{E:yonelme} bir mesaj gönderdim
Dün akşam {E:vasita} konuştum
"""

TASLAK[("yari", "kod")] = """
Kapı şifresi {E} olarak ayarlandı
Kartın PIN kodu {E}
Posta kodumuz {E.posta}
Doğrulama kodu {E} geldi
Takip numaranız {E}
Sipariş numaram {E} olarak görünüyor
Abone numarası {E} ile kayıt yaptırın
Güvenlik kodunu {E} girmeniz gerekiyor
Fatura numarası {E} olan belgeyi gönderin
Müşteri numaranızı {E} diye yazın
"""

TASLAK[("yari", "karisik")] = """
{e.sayi} {kalabalik} {s.kardinal_orta} dakika bekledi
Servise {e.sayi} {kalabalik} bindi, yolculuk {s.kardinal_orta} dakika sürdü
{e.para} tutan faturayı {s.kardinal_kucuk} günde ödedik
Pazardan {e.olcu_agirlik} elma aldım, {s.para_kucuk} verdim
Mağazada {e.yuzde} indirim var, ceket {s.para_tl} oldu
Toplantı {e.saat} başlayacak, {s.kardinal_orta} kişi katılacak
{e.tarih} tarihli sınava {s.kardinal_yuz} öğrenci girecek
Evimiz okula {e.olcu_mesafe}, yürüyerek {s.kardinal_orta} dakika sürüyor
Kampanya {e.yuzde} indirim ve {s.para_tl} değerinde hediye çeki içeriyor
Arabaya {e.olcu_hacim} benzin attım, yanında {s.para_kucuk} tutan su aldım
Hesabımda {e.para} var, {s.para_tl} daha gelecek
Bu hafta {e.sayi} adım attım, dün {s.kardinal_yuz} adım atmıştım
Şu an {e.sayi} {kalabalik} çevrimiçi, {s.kardinal_kucuk} yönetici de var
Telefonum {e.olcu_veri}, bilgisayarım {s.olcu_veri}
Kutu {e.olcu_agirlik}, içindeki ürün {s.olcu_agirlik} ağırlığında
Sınav {e.tarih} günü, sonuçlar {s.kardinal_orta} gün sonra
Numaram {e.tel}, dahili numaram {s.kardinal_yuz}
Okula {e.olcu_mesafe} yol var, otobüs {s.para_kucuk} alıyor
Bu {e.sayi} {adet} içinden {s.kardinal_orta} tanesi bozuk çıktı
Faizi {e.yuzde} olan krediyi {s.kardinal_orta} ayda ödedik
{e.sayi} {kalabalik} içinden {s.kardinal_orta} kişi seçildi
Hava {e.derece}, rüzgâr {s.kardinal_orta} gündür sürüyor
Fiyat {e.para} idi, {s.yuzde} indirimle aldık
Yolculuk {e.saat} başladı, {s.olcu_mesafe} gittik
Hesabıma {e.para:yonelme} para yatırdım, {s.para_kucuk} masraf çıktı
Salon {e.olcu_alan:lik} ama içeri {s.kardinal_yuz} kişi sığdı
Depoda {e.sayi} {adet} var, {s.kardinal_kucuk} palet boş
Bugün {e.sayi} {kalabalik} geldi, dün {s.kardinal_orta} kişi gelmişti
Ödemeyi {e.tarih:yonelme} kadar yapın, gecikmeye {s.yuzde} faiz işler
Çantam {e.olcu_agirlik:lik} ama {s.olcu_agirlik} daha sığdırdım
"""

# ----------------------------------------------------------------------------- C2 bitisik
TASLAK[("bitisik", "kardinal")] = """
Salonda {E} {kalabalik} oturuyordu
Rafta {E} {adet} kalmış
Bu sezon {E} {adet} dağıttık
Toplantıda {E} {kalabalik} söz aldı
Mahallede {E} {kalabalik} oy kullandı
Kitabın {E} sayfası eksik çıktı
Otelde {E} {kalabalik} konakladı
Pazar yerinde {E} {kalabalik} vardı
Yolda {E} araç gördüm
Depodan {E} {adet} çıkarıldı
Sitede {E} {kalabalik} yaşıyor
Kurs {E} {kalabalik} kabul ediyor
Deneme sınavına {E} {kalabalik} girdi
Sayaç {E:yonelme} kadar ilerledi
Sipariş sayısı {E:yonelme} fırladı
Bilet satışları {E:belirtme} aştı
Kapasite {E:ayrilma} aşağı inemez
Kayıtlar {E:bulunma} dondu
{E:ilgi} üzerindeki sayılar ayrıca raporlanır
Bahçeye {E:lik} bir kalabalık doldu
{E:lik} kutularda indirim var
Gelen kişi sayısı {E:belirtme} bulmuş
Hesap {E:bulunma} kapandı
"""

TASLAK[("bitisik", "para")] = """
Elektrik faturası {E} geldi
Çocuğun okul taksiti {E} oldu
Cüzdanımda {E} vardı
Lokantada hesap {E} tuttu
Bilet ücreti {E} çıktı
Tamir masrafı {E} tuttu
Aylık aidat {E} olarak belirlendi
Taksi ücreti {E} tuttu
Bu halıya {E:yonelme} anlaştık
Arabanın lastiklerini {E:yonelme} değiştirdik
Paketler {E:ayrilma} başlayan fiyatlarla satılıyor
Satıcı {E:belirtme} nakit istedi
Kız kardeşim {E:belirtme} bana ödünç verdi
Alışverişe {E:vasita} çıktık
{E:lik} bir yemek çeki aldım
{E:ilgi} üstü bahşiş olsun
Kitapçıda defter {E:bulunma} duruyor
Bu ücretin {E:iyelik3} peşin ödendi
{E:lik} bir dolum kartı yükledik
"""

TASLAK[("bitisik", "olcu")] = """
Kasaba {E.agirlik} domates gönderdik
Bebek ilk ayında {E.agirlik} aldı
{E.agirlik:lik} bir koli yolladılar
Bavula {E.agirlik:yonelme} kadar eşya sığar
Yolun uzunluğu {E.mesafe} tutuyor
Kamp yerine {E.mesafe} daha var
Bir turda {E.mesafe:ayrilma} fazla koşmam
Duvar {E.uzunluk} yüksekliğinde
Terzi paçayı {E.uzunluk} kıstı
Boyu {E.boy} olan fidanlar ayrıldı
Hazneye {E.hacim} su doldu
{E.hacim:lik} bir şişe aldım
Yeni telefon {E.veri} depolama sunuyor
Belleği {E.veri:yonelme} çıkardım
{E.veri:lik} bir yedek disk aldık
Mutfağımız {E.alan} geniş
{E.alan:lik} bir depo kiraladık
Elektrikli soba {E.guc} çekiyor
{E.guc:lik} bir şarj cihazı satın aldım
Hava {E.sicaklik} olunca ısıtıcıyı kapat
Tavayı {E.sicaklik:yonelme} kadar ısıt
Çay suyu {E.sicaklik:bulunma} kaynar
"""

TASLAK[("bitisik", "yuzde")] = """
Dükkândaki mallarda {E} indirim yapıldı
Mevduat faizi {E} oldu
Sınıfın başarı yüzdesi {E} çıktı
Çalışanlara {E} zam yapılacak
Maaşın {E:iyelik3} kesildi
Hasılatın {E:iyelik3} bağışlanacak
Faiz {E:yonelme} indi
Komisyon {E:ayrilma} aşağı kalmaz
Barajı {E:belirtme} aşan listeler girer
{E:ilgi} üstünde zam istiyorlar
Büyüme {E:bulunma} kaldı
{E:lik} bir pay ayırdık
Şirket yılı {E:vasita} kapattı
"""

TASLAK[("bitisik", "saat")] = """
Tören saat {E:bulunma} yapılacak
Müşteri saat {E:bulunma} geldi
Gemi saat {E:bulunma} limandan ayrıldı
Mesaiyi saat {E:yonelme} kadar uzattık
Nöbet saat {E:yonelme} kadar sürecek
Yağmur saat {E:ayrilma} bu yana yağıyor
Sınav saat {E:ayrilma} sonra başlar
Ekran saat {E:belirtme} gösteriyor
Kurs saat {E} bitecek
Kargo saat {E} dağıtıma çıktı
Yarın saat {E} havalimanında ol
Alarmı saat {E} kuruyorum
Doktor saat {E} bakacak
Müzik saat {E:vasita} birlikte başlıyor
"""

TASLAK[("bitisik", "tarih")] = """
Final maçı {E.tam} tarihinde oynanacak
Pasaportu {E.tam} tarihli olarak aldım
Yarışma {E.tam:bulunma} sona erdi
Zam {E.tam:ayrilma} itibaren yürürlükte
Teslimi {E.tam:yonelme} kadar erteledik
Yıl dönümümüz {E.gunay}
Kına gecesi {E.gunay:bulunma} yapılacak
Başvurular {E.gunay:yonelme} kadar alınacak
Takvim {E.gunay:belirtme} kırmızıyla işaretlemiş
Kontenjan {E.gunay:ayrilma} sonra açılır
Belediye {E.yil:bulunma} kuruldu
Tiyatro {E.yil:bulunma} açılmış
{E.yil:ayrilma} beri aynı evde oturuyoruz
{E.yil:yonelme} kadar sürecek
Kardeşim {E.yil} yılında mezun oldu
Köprü {E.yil} yılında hizmete girdi
"""

# ----------------------------------------------------------------------------- C3 saat_deyis
TASLAK[("saat_deyis", "z")] = """
{E} evden çıktık
{E} toplantıdan ayrıldım
{E} servis geldi
{E} dükkânı kapattık
{E} otobüse yetiştik
{E} uyandım
{E} yemeğe indik
{E} sizi arayacağım
{E} kapıdan çıkarsan yetişirsin
Dün {E} telefonum çaldı
{vakit} {E} kalktım
{vakit} {E} işe başladık
{vakit} {E} uykuya daldım
{vakit} {E} yola çıkarız
{vakit} {E} haber izledik
Bu akşam {E} buluşalım
Yarın {E} kapıda ol
Ben genelde {E} yatarım
Annem {E} eve geldi
Maç {E} başladı
Randevuya {E} gittik
Müdür {E} odasına girdi
Uçak {E} havalandı
Tren {E} peronda olur
Çocuklar {E} uykuya daldı
Seni {E} alırım
Toplantıyı {E} bitirelim
Kahvaltıyı {E} yaptık
Sinemaya {E} girdik
Derse {E} geldim
{isim} bizi {E} aradı
Hastaneye {E} vardık
Kargocu {E} kapıya geldi
Bugün {E} çıkabilirsin
Ofisten {E} ayrılırım
Pazara {E} gittik
Kızım okuldan {E} döndü
Misafirler {E} geldi
Biz {E} orada oluruz
"""

TASLAK[("saat_deyis", "p")] = """
{E} ama hâlâ gelen yok
Baksana, {E}
Acele et, {E}
{E} neredeyse geç kalıyoruz
Saatime baktım, {E}
Şu an {E}
Hadi çabuk, {E}
{E} bence artık çıkmalıyız
Telefona bak, {E}
Sen ne diyorsun, {E}
Hâlâ kimse yok, {E}
{E} toplantı başlamak üzere
Kapıyı kilitle, {E}
{vakit} {E} ve ortalık sessiz
Biraz daha bekleyelim, {E}
Kardeşim gelmedi, {E}
{E} ama yemek hâlâ hazır değil
Çayı koy, {E}
Maç başlamak üzere, {E}
Dükkân kapanıyor, {E}
Geç oldu, {E}
Saat kaç dedin, {E}
{isim} hâlâ uyuyor, {E}
Bakkal kapanmadan git, {E}
"""

TASLAK[("saat_deyis", "d")] = """
Eve girdiğimde {E}
Uyandığımda {E}
Seni aradığımda {E}
Kapıyı çaldıklarında {E}
Baktım ki {E}
Evden çıkarken {E}
Ben vardığımda {E}
Maç başladığında {E}
Telefon çaldığında {E}
Otobüse bindiğimde {E}
Mutfağa indiğimde {E}
{vakit} uyandım, {E}
Annem aradığında {E}
Saate baktığımda {E}
Toplantıdan çıktığımda {E}
Servise yetiştiğimde {E}
Kapıdan girdiğinde {E}
Dükkâna vardığımızda {E}
Hatırlıyorum, o zaman {E}
Gece yarısı olmuştu, {E}
"""

TASLAK[("saat_deyis", "y")] = """
Dediğim gibi, {E}
Sana söylemiştim, {E}
Saati sordum, {E}
Bir baktım, {E}
Öğrendiğimde {E}
Haberi duyduğumuzda {E}
Saatler geçti, {E}
Hatırlıyorum, {E}
Bana dediler ki {E}
Kimse bilmiyordu ama {E}
Saati sorunca dediler ki {E}
Fark ettiğimde {E}
"""

# ----------------------------------------------------------------------------- C4 tarih (ayın günü)
TASLAK[("tarih", "bulunma")] = """
Kira {E:bulunma} ödenir
Maaşlar {E:bulunma} yatıyor
Toplantı {E:bulunma} yapılacak
Aidat {E:bulunma} toplanıyor
Fatura {E:bulunma} geliyor
Taksit {E:bulunma} hesaptan çekilecek
Dersler {E:bulunma} başlıyor
Sınav {E:bulunma} yapıldı
Ödeme {E:bulunma} hesaba geçer
Düğün {E:bulunma} yapılacakmış
Kargo {E:bulunma} elinize ulaşır
Raporlar {E:bulunma} teslim edilir
{E:bulunma} evde olacağım
{E:bulunma} randevum var
Kurs {E:bulunma} sona eriyor
Servis {E:bulunma} gelecek
Doktor {E:bulunma} muayene edecek
"""

TASLAK[("tarih", "ayrilma")] = """
Yeni tarife {E:ayrilma} itibaren geçerli
Dersler {E:ayrilma} sonra başlayacak
{E:ayrilma} beri izinliyim
Kira {E:ayrilma} önce yatırılmalı
Sipariş {E:ayrilma} önce gelmez
Zamlar {E:ayrilma} itibaren uygulanıyor
Hastane {E:ayrilma} sonra randevu vermiyor
Kurs {E:ayrilma} bu yana devam ediyor
Kampanya {E:ayrilma} sonra bitiyor
Bakım çalışmaları {E:ayrilma} itibaren başlıyor
{E:ayrilma} önce haber verin
Burs ödemeleri {E:ayrilma} sonra yapılır
Sergi {E:ayrilma} beri açık
Fiyat farkı {E:ayrilma} itibaren yansıtılacak
Ders programı {E:ayrilma} sonra değişecek
Kapalı olacağız, {E:ayrilma} önce uğrayın
"""

TASLAK[("tarih", "yonelme")] = """
Ödemenizi {E:yonelme} kadar tamamlayın
Raporu {E:yonelme} kadar bitir
Başvurular {E:yonelme} kadar sürecek
Borcu {E:yonelme} kadar kapatmalıyız
Tatili {E:yonelme} erteledik
Toplantıyı {E:yonelme} aldılar
Sınavı {E:yonelme} bıraktılar
Randevumu {E:yonelme} değiştirdim
Teslimat {E:yonelme} kaldı
Kitabı {E:yonelme} kadar iade et
Formu {E:yonelme} kadar doldurun
Ev sahibi kirayı {E:yonelme} kadar bekleyecek
{E:yonelme} kadar buradayız
Misafirler {E:yonelme} kadar kalacak
Kayıt süresi {E:yonelme} kadar uzatıldı
Fatura {E:yonelme} kadar ödenmeli
Proje {E:yonelme} yetişmeli
"""

TASLAK[("tarih", "belirtme")] = """
Okul {E:belirtme} tatil ilan etti
Hepimiz {E:belirtme} iple çekiyoruz
{E:belirtme} unutma
Toplantı için {E:belirtme} seçtik
Müdür {E:belirtme} izinli saydı
Bu yıl {E:belirtme} kaçırmayalım
Kurs {E:belirtme} sınav günü olarak belirledi
Takvimde {E:belirtme} işaretledim
Şirket {E:belirtme} resmi tatil sayıyor
Ben {E:belirtme} boş bıraktım
Annem {E:belirtme} not etmiş
Muhasebe {E:belirtme} son gün olarak açıkladı
Doktor {E:belirtme} önerdi
Hocamız {E:belirtme} teslim günü yaptı
Biz {E:belirtme} sabırsızlıkla bekliyoruz
{E:belirtme} gözümüze kestirdik
"""

TASLAK[("tarih", "iyelik3")] = """
Sınav {E:iyelik3} cuma
Doğum günüm {E:iyelik3}
Toplantı günü {E:iyelik3}
Son ödeme günü {E:iyelik3}
Taksitin son günü {E:iyelik3}
Konser {E:iyelik3} akşamı
Düğün tarihimiz {E:iyelik3}
Bugün {E:iyelik3}
Randevum {E:iyelik3} salı
Teslim tarihi {E:iyelik3} olarak yazılmış
Tatilin ilk günü {E:iyelik3}
Mezuniyet töreni {E:iyelik3}
Son teslim günü {E:iyelik3}
Kurs sonu sınavı {E:iyelik3}
Evlilik yıl dönümümüz {E:iyelik3}
Fatura son günü {E:iyelik3} imiş
"""

_sablonlari_kur(TASLAK)


if __name__ == "__main__":
    raise SystemExit(main())
