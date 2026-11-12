"""Megazeka-Sayı v2 · A kaynağı: sayısal doğruluk (SPEC-v2 §A1–A8).

Kullanım:
    python training/v2_sayisal.py --out data/v2 --seed 2201 --train 16000 --validation 400 --test 500

Çıktı: `a-train.jsonl`, `a-validation.jsonl`, `a-test.jsonl`. Satır: {"girdi","hedef","kategori","sablon"}.
Önce yazılı biçim (hedef) `kur_*` kurucularıyla kurulur, girdi ondan deterministik türetilir; etiket elle yazılmaz.

Dışa açık işlevler (birleştirme betiği kullanır):
    telefon_ayrisimlari(sozcukler)      sözlü telefon dizisinin bütün geçerli 11 haneli ayrışımları
    telefon_satiri_belirsiz(girdi, hedef)  telefonlu satırın sözlü biçimi birden çok ayrışıyorsa True
"""
from __future__ import annotations

import argparse
import contextlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))

from megazeka_sayi import sablonlar as B  # noqa: E402
from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.turkce import lower_tr, written_suffix  # noqa: E402
from megazeka_sayi.varliklar import Varlik  # noqa: E402

BAYT_SINIRI = 180

# ======================================================================================================
# 1. TELEFON AYRIŞIMLARI (SPEC-v2 §A2 belirsizlik kuralı)
# ======================================================================================================
# Telefon: 0XXX XXX XX XX  (artı doksan ile: XXX XXX XX XX). Her grup ya sayı olarak (sayi: baştaki sıfırlar tek tek
# "sıfır", kalanı sayı) ya da rakam rakam okunur. Aşağıdaki sözlük (grup boyu, sözcük dizisi) -> rakam kümesidir.
_TEL_SOZLUK: dict[int, dict[tuple, set]] | None = None
_TEL_SOZCUKLERI = frozenset(S.BIRLER) | frozenset(S.ONLAR[1:]) | {"yüz", "artı"}
_TEL_KOKLERI = sorted(_TEL_SOZCUKLERI - {"artı"}, key=lambda s: -len(s)) + ["dörd"]


def _tel_sozluk() -> dict[int, dict[tuple, set]]:
    global _TEL_SOZLUK
    if _TEL_SOZLUK is None:
        d: dict[int, dict[tuple, set]] = {}
        for boy in (2, 3, 4):
            sz: dict[tuple, set] = defaultdict(set)
            for n in range(10 ** boy):
                r = f"{n:0{boy}d}"
                for mod in ("sayi", "rakam"):
                    sz[tuple(S.grup_kelimeleri(r, mod))].add(r)
            d[boy] = dict(sz)
        _TEL_SOZLUK = d
    return _TEL_SOZLUK


def _kok_adaylari(sozcuk: str) -> list[str]:
    """Ekli sözcüğün olası sayı kökleri: 'altmışa' -> ['altmış'], 'dörde' -> ['dört']."""
    s = lower_tr(sozcuk)
    if s in _TEL_SOZCUKLERI:
        return [s]
    adaylar = []
    for k in _TEL_KOKLERI:
        if s.startswith(k) and len(s) > len(k):
            adaylar.append("dört" if k == "dörd" else k)
    return adaylar


def telefon_ayrisimlari(sozcukler: list[str]) -> list[str]:
    """Sözlü telefon dizisinin (isteğe bağlı baştaki `artı doksan` dahil) `0XXX XXX XX XX` kalıbına uyan BÜTÜN
    ayrışımları; her biri baştaki 0 ile 11 haneli rakam dizisidir (`+90` kipinde de `0` eklenir).

    Son sözcük ekli olabilir (`yetmiş yediden`). Tek elemanlı sonuç = belirsiz değil; boş sonuç = kalıba uymuyor.
    """
    w = [lower_tr(x) for x in sozcukler]
    if not w:
        return []
    sonlar = [w[:-1] + [k] for k in _kok_adaylari(w[-1])]
    sonuc: set[str] = set()
    for dizi in sonlar:
        sonuc |= _ayristir(dizi)
    return sorted(sonuc)


def _ayristir(w: list[str]) -> set[str]:
    sz = _tel_sozluk()
    arti = w[:2] == ["artı", "doksan"]
    if arti:
        w = w[2:]
    boylar = (3, 3, 2, 2) if arti else (4, 3, 2, 2)
    sonuc: set[str] = set()
    n = len(w)

    def git(i: int, g: int, acc: str) -> None:
        if g == 4:
            if i == n:
                sonuc.add(("0" + acc) if arti else acc)
            return
        tablo = sz[boylar[g]]
        for uz in range(1, min(6, n - i) + 1):
            for r in tablo.get(tuple(w[i:i + uz]), ()):
                if g == 0 and not arti and r[0] != "0":
                    continue
                git(i + uz, g + 1, acc + r)

    git(0, 0, "")
    return sonuc


_TEL_HEDEF = re.compile(r"(?<![\d.,])(?:\+90 (\d{3})|(0\d{3})) (\d{3}) (\d{2}) (\d{2})(?!\d)")
_TOKEN = re.compile(r"[^\s.,!?;:\"…]+")


def _hedef_telefonlari(hedef: str) -> list[str]:
    out = []
    for m in _TEL_HEDEF.finditer(hedef):
        g1 = ("0" + m.group(1)) if m.group(1) else m.group(2)
        out.append(g1 + m.group(3) + m.group(4) + m.group(5))
    return out


def telefon_satiri_belirsiz(girdi: str, hedef: str) -> bool:
    """Satırda (hedefte yazılı) telefon varsa ve girdideki sözlü biçimi birden fazla ayrışıyorsa True.

    Girdide telefon zaten rakamla verilmişse (idempotent satırlar) ya da sözlü karşılığı bulunamazsa False.
    """
    hedefler = _hedef_telefonlari(hedef)
    if not hedefler:
        return False
    tok = [lower_tr(t) for t in _TOKEN.findall(girdi)]
    n = len(tok)
    duz_girdi = girdi.replace(" ", "")
    for rakam in hedefler:
        if rakam in duz_girdi:
            continue
        bulundu = None
        for i in range(n):
            if tok[i] not in ("sıfır", "artı"):
                continue
            j = i
            while j < n and tok[j] in _TEL_SOZCUKLERI:
                j += 1
            son = j + 1 if (j < n and _kok_adaylari(tok[j])) else j  # son sözcük ekli olabilir
            for k in range(i + 6, son + 1):
                olasi = telefon_ayrisimlari(tok[i:k])
                if rakam in olasi:
                    bulundu = olasi
                    break
            if bulundu is not None:
                break
        if bulundu is not None and len(bulundu) > 1:
            return True
    return False


# ======================================================================================================
# 2. BİRİMLER VE KURUCULAR
# ======================================================================================================
YENI_BIRIMLER = {
    # anahtar: (yazılı, kanonik okunuşun son sözcüğü, sözlü seçenekler, kip)
    "mg": ("mg", "miligram", [["miligram"]], "apostrof"),
    "m3": ("m³", "metreküp", [["metreküp"]], "apostrof"),
    "km2": ("km²", "kilometrekare", [["kilometrekare"]], "apostrof"),
    "kwh": ("kWh", "kilovatsaat", [["kilovatsaat"], ["kilovat", "saat"]], "apostrof"),
    "hz": ("Hz", "hertz", [["hertz"]], "apostrof"),
    "mhz": ("MHz", "megahertz", [["megahertz"]], "apostrof"),
    "ton": ("ton", "ton", [["ton"]], "sozcuk"),
    "inc": ("inç", "inç", [["inç"]], "sozcuk"),
    "kalori": ("kalori", "kalori", [["kalori"]], "sozcuk"),
    "hektar": ("hektar", "hektar", [["hektar"]], "sozcuk"),
    "donum": ("dönüm", "dönüm", [["dönüm"]], "sozcuk"),
    "beygir": ("beygir", "beygir", [["beygir"]], "sozcuk"),
    "piksel": ("piksel", "piksel", [["piksel"]], "sozcuk"),
    "karat": ("karat", "karat", [["karat"]], "sozcuk"),
    "saat": ("saat", "saat", [["saat"]], "sozcuk"),
    "dakika": ("dakika", "dakika", [["dakika"]], "sozcuk"),
    "saniye": ("saniye", "saniye", [["saniye"]], "sozcuk"),
    "gun": ("gün", "gün", [["gün"]], "sozcuk"),
    "hafta": ("hafta", "hafta", [["hafta"]], "sozcuk"),
    "ay": ("ay", "ay", [["ay"]], "sozcuk"),
    "yil": ("yıl", "yıl", [["yıl"]], "sozcuk"),
}
BIRIM2 = {**V.BIRIMLER, **YENI_BIRIMLER}


def _birim_varlik(sayi_k, sayi_yaz, anahtar, soz_idx, ek, kategori, son=True):
    yaz, kan, secenekler, kip = BIRIM2[anahtar]
    sozcukler = list(sayi_k) + secenekler[soz_idx % len(secenekler)]
    yazili = f"{sayi_yaz} {yaz}"
    if not (son and ek):
        return Varlik(yazili, " ".join(sozcukler), kategori)
    s, y = V._birlestir(sozcukler, yazili, kan, ek, kip)
    return Varlik(y, s, kategori)


def kur_olcu2(tam, kesir="", birim="kg", soz_idx=0, bucuk=False, rakam_rakam=False, ek=None, kategori="olcu"):
    """`V.kur_olcu` gibi, ama yeni birimleri (A6) de tanır."""
    return _birim_varlik(V._num_kelimeleri(tam, kesir, bucuk, rakam_rakam), V._num(tam, kesir), birim, soz_idx, ek,
                         kategori)


def kur_bilesik(parcalar, ek=None, soz_idx=None):
    """[(değer, birim), ...] -> `3 kg 200 g` ya da `2 saat 15 dakikada`. Bütün sayılar rakam; ek yalnız son birime."""
    sz, yz = [], []
    for i, (n, b) in enumerate(parcalar):
        idx = 0 if soz_idx is None else soz_idx[i]
        v = _birim_varlik(S.sayi_kelimeleri(n), str(n), b, idx, ek, "bilesik", son=(i == len(parcalar) - 1))
        sz.append(v.sozlu)
        yz.append(v.yazili)
    return Varlik(" ".join(yz), " ".join(sz), "bilesik")


def kur_yas(n, bicim="yaşında"):
    """`kırk yaşında` -> `40 yaşında` (sözcük kalır; ek sözcüğün parçasıdır)."""
    return Varlik(f"{n} {bicim}", " ".join(S.sayi_kelimeleri(n) + [bicim]), "olcu")


# ---- A1: iç sıfırlı sayılar ------------------------------------------------------------------------------

def grup_tipi(g: int) -> str:
    """Üç haneli binlik grubun türü: Z=000, A=00x, B=0x0, C=0xx, N=normal (100+)."""
    if g == 0:
        return "Z"
    if g < 10:
        return "A"
    if g < 100:
        return "B" if g % 10 == 0 else "C"
    return "N"


def ic_gruplar(n: int) -> list[int]:
    """En anlamlı grup hariç binlik grupların değerleri (soldan sağa)."""
    g = []
    while n:
        n, r = divmod(n, 1000)
        g.append(r)
    return g[-2::-1] if len(g) > 1 else []


# ======================================================================================================
# 3. ÖRNEKLEYİCİLER
# ======================================================================================================
class _Baglam:
    """Üretim sırasında örnekleyicilerin okuduğu/yazdığı durum (her üretimde sıfırlanır)."""

    def __init__(self):
        self.sifirla()

    def sifirla(self):
        self.tip_say = Counter()
        self.birim = None
        self.kod_uzunluk = None
        self.a8_kucuk = True


CTX = _Baglam()
ZTIP = ("Z", "A", "B", "C")


def _grup_degeri(rng, tip):
    if tip == "Z":
        return 0
    if tip == "A":
        return rng.randint(1, 9)
    if tip == "B":
        return rng.choice([10, 20, 30, 40, 50, 60, 70, 80, 90])
    if tip == "C":
        return rng.choice([n for n in range(11, 100) if n % 10])
    return rng.choice([100, 120, 150, 200, 250, 300, 400, 500, 750]) if rng.random() < 0.3 else rng.randint(100, 999)


def _ust_grup(rng):
    r = rng.random()
    if r < 0.12:
        return 1
    if r < 0.40:
        return rng.randint(2, 9)
    if r < 0.75:
        return rng.randint(10, 99)
    return rng.randint(100, 999)


def sifirli_sayi(rng, p3=0.2, uc_zorunlu=False):
    """En az bir iç grubu 000 / 00x / 0x0 / 0xx olan sayı. Tür sayaçlarıyla dengelenir."""
    say = CTX.tip_say
    k = 3 if (uc_zorunlu or rng.random() < p3) else 2
    en_az = min(say[t] for t in ZTIP)
    T = rng.choice([t for t in ZTIP if say[t] == en_az])
    if k == 2 and T == "Z" and rng.random() < 0.55:
        en_az2 = min(say[t] for t in ZTIP[1:])
        T = rng.choice([t for t in ZTIP[1:] if say[t] == en_az2])
    top = _ust_grup(rng)
    if k == 2:
        gruplar = [top, _grup_degeri(rng, T)]
    else:
        konum = 1 if (T == "Z" and rng.random() < 0.8) else rng.choice([1, 2])
        diger = rng.choices(["N", "A", "B", "C", "Z"], [32, 18, 18, 22, 10])[0]
        if T == "Z" and diger == "Z":
            diger = "C"
        g = [0, 0]
        g[konum - 1] = _grup_degeri(rng, T)
        g[2 - konum] = _grup_degeri(rng, diger)
        gruplar = [top, g[0], g[1]]
    n = 0
    for x in gruplar:
        n = n * 1000 + x
    for x in gruplar[1:]:
        say[grup_tipi(x)] += 1
    return n


_A1_OLCU = {
    "olcu": (["kg", "g", "km", "m", "cm", "m2", "L", "mL", "GB", "MB", "TB", "kW", "W", "V"], 0.04),
    "mesafe": (["km", "m"], 0.04),
    "agirlik": (["kg", "g"], 0.04),
    "veri": (["GB", "MB", "TB"], 0.08),
}


def ornekle_sifirli(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or "sayi"
    if alt in ("para", "tl"):
        n = sifirli_sayi(rng, 0.06)
        kurus = rng.choices(V._KURUS, V._KURUS_W)[0] if (alt == "tl" and rng.random() < 0.7) else None
        ad = "Türk lirası" if (ek is None and rng.random() < 0.15) else "lira"
        virgullu = kurus is not None and ad == "lira" and rng.random() < 0.06
        return V.kur_para(lira=n, kurus=kurus, ek=ek, ad=ad, virgullu=virgullu)
    if alt == "dolar":
        return V.kur_para(lira=sifirli_sayi(rng, 0.05), birim=rng.choice(["dolar", "avro", "euro", "sterlin"]), ek=ek)
    if alt in _A1_OLCU:
        birimler, p3 = _A1_OLCU[alt]
        return V.kur_olcu(sifirli_sayi(rng, p3), "", rng.choice(birimler), rng.randrange(2), False, False, ek)
    if alt == "kisi":
        return V.kur_kardinal(sifirli_sayi(rng, 0.30), politika, ek)
    if alt == "sayi":
        while True:
            n = sifirli_sayi(rng, 0.30)
            if not 1000 <= n <= 2100:  # bağlamsız yalın sayı yıl gibi okunabilir
                return V.kur_kardinal(n, politika, ek)
    if alt == "buyuk":
        return V.kur_buyuk_duz(sifirli_sayi(rng, 1.0, True), None, ek)
    if alt == "buyuktl":
        return V.kur_buyuk_duz(sifirli_sayi(rng, 1.0, True), "TL", ek)
    raise KeyError(alt)


# ---- A2: telefon ve kod ------------------------------------------------------------------------------

def _grup_rakam(rng, boy):
    r = rng.random()
    if boy == 3:
        if r < 0.35:
            return "".join(rng.choice("123456789") for _ in range(3))
        t = rng.choices(["x0y", "x00", "0xy", "00x", "xy0"], [28, 16, 24, 12, 20])[0]
        x, y = rng.choice("123456789"), rng.choice("123456789")
        return {"x0y": x + "0" + y, "x00": x + "00", "0xy": "0" + x + y, "00x": "00" + x, "xy0": x + y + "0"}[t]
    if r < 0.40:
        return "".join(rng.choice("123456789") for _ in range(2))
    t = rng.choices(["x0", "0x", "00"], [48, 38, 14])[0]
    x = rng.choice("123456789")
    return {"x0": x + "0", "0x": "0" + x, "00": "00"}[t]


def _tel_rakamlari(rng):
    if rng.random() < 0.8:
        g1 = "05" + rng.choice("345") + (rng.choice("123456789") if rng.random() > 0.2 else "0")
    else:
        g1 = "0" + rng.choice(["212", "216", "312", "232", "224", "242", "322", "352", "262", "282"])
    return g1 + _grup_rakam(rng, 3) + _grup_rakam(rng, 2) + _grup_rakam(rng, 2)


def ornekle_tel(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    while True:
        r = _tel_rakamlari(rng)
        modlar = tuple(rng.choices(["sayi", "rakam"], [72, 28])[0] for _ in range(4))
        x = rng.random()
        if x < 0.33:
            modlar = ("sayi",) * 4
        elif x < 0.40:
            modlar = ("rakam",) * 4
        arti = rng.random() < 0.10
        kelimeler = S.telefon_kelimeleri(r, modlar, arti)
        if telefon_ayrisimlari(kelimeler) == [r]:
            return V.kur_telefon(r, modlar, arti, ek)


_KOD_UZUNLUK_ARALIGI = {None: (3, 11), "kisa": (3, 5), "pin": (4, 6), "orta": (6, 9), "uzun": (8, 11), "tc": (11, 11),
                        "posta": (5, 5)}
_KOD_TORBA_AGIRLIK = {3: 8, 4: 14, 5: 11, 6: 11, 7: 8, 8: 12, 9: 9, 10: 10, 11: 13}


def kod_rakamlari(rng, n, ilk_sifirsiz=False):
    r = rng.random()
    if r < 0.42:
        ds = [rng.choice("0123456789") for _ in range(n)]
    elif r < 0.72:  # art arda yinelenen rakamlar: 991, 55555
        d = rng.choice("0123456789")
        uz = rng.randint(2, min(5, n))
        poz = rng.randint(0, n - uz)
        ds = [rng.choice("0123456789") for _ in range(n)]
        ds[poz:poz + uz] = [d] * uz
    elif r < 0.86:  # baştaki sıfırlar: 0007, 00842
        z = rng.randint(1, min(3, n - 1))
        ds = ["0"] * z + [rng.choice("0123456789") for _ in range(n - z)]
    else:  # ikili/üçlü tekrar deseni: 1212, 505050, 7007
        uz = rng.choice([2, 3]) if n >= 4 else 2
        parca = [rng.choice("0123456789") for _ in range(uz)]
        ds = (parca * n)[:n]
    if ilk_sifirsiz and ds[0] == "0":
        ds[0] = rng.choice("123456789")
    return "".join(ds)


def ornekle_kod2(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    lo, hi = _KOD_UZUNLUK_ARALIGI[alt]
    n = CTX.kod_uzunluk
    if n is None or not lo <= n <= hi:
        n = rng.randint(lo, hi)
    return V.kur_kod(kod_rakamlari(rng, n, ilk_sifirsiz=(alt == "tc")))


# ---- A3: aralık --------------------------------------------------------------------------------------

_SAYI_SOZ: dict[tuple, int] | None = None


def _sayi_sozlugu():
    global _SAYI_SOZ
    if _SAYI_SOZ is None:
        _SAYI_SOZ = {tuple(S.sayi_kelimeleri(n)): n for n in range(0, 10001)}
    return _SAYI_SOZ


def iki_sayi_ayrisimlari(sozcukler):
    """Sözcük dizisinin (a, b), a < b olacak biçimde iki sayıya bütün bölünmeleri."""
    d = _sayi_sozlugu()
    w = list(sozcukler)
    out = []
    for i in range(1, len(w)):
        a, b = d.get(tuple(w[:i])), d.get(tuple(w[i:]))
        if a is not None and b is not None and a < b:
            out.append((a, b))
    return out


def aralik_cifti(rng):
    while True:
        r = rng.random()
        if r < 0.40:  # onluk-onluk
            a = rng.choice(range(10, 100, 5)) if rng.random() < 0.5 else rng.choice(range(10, 100, 10))
            b = min(a + rng.choice([5, 5, 10, 10, 15, 20, 25, 30]), 100)
        elif r < 0.68:  # yüzlük-yüzlük
            a = rng.choice(range(100, 1000, 50))
            b = a + rng.choice([50, 50, 100, 100, 150, 200, 250, 300])
        elif r < 0.78:  # tek haneli
            a = rng.randint(2, 8)
            b = a + rng.choice([1, 1, 2, 3])
        elif r < 0.88:  # binlik
            a = rng.choice([1000, 1500, 2000, 2500, 3000, 4000, 5000])
            b = a + rng.choice([500, 500, 1000, 1000, 1500, 2000])
        else:
            a, b = rng.choice([(5, 10), (5, 15), (2, 20), (8, 12), (30, 100), (50, 100), (40, 200), (10, 100),
                               (20, 50), (100, 200), (200, 500), (500, 1000)])
        if b > 9999:
            continue
        sk = S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b)
        if "bir" in sk:
            continue
        if iki_sayi_ayrisimlari(sk) != [(a, b)]:
            continue
        return a, b


_ARALIK_BIRIM = {"tl": (["TL"], 1), "agirlik": (["kg", "g"], 2), "mesafe": (["km", "m"], 2), "sicaklik": (["derece", "C"], 3),
                 "hacim": (["L", "mL"], 4), "dolar": (["dolar"], 1), "cm": (["cm", "mm"], 5)}


def _aralik_uygun(birim, a, b):
    if birim in ("derece", "C"):
        return b <= 50
    if birim in ("g", "mL"):
        return a >= 50
    if birim in ("kg", "L", "km"):
        return b <= 500
    if birim in ("m", "cm", "mm"):
        return b <= 500
    return True


def ornekle_aralik2(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt is None:
        a, b = aralik_cifti(rng)
        return V.kur_aralik(a, b)
    birimler, _ = _ARALIK_BIRIM[alt]
    while True:
        a, b = aralik_cifti(rng)
        birim = rng.choice(birimler)
        if _aralik_uygun(birim, a, b):
            return V.kur_aralik(a, b, birim, rng.randrange(2), ek)


# ---- A4: birim x ek dengesi --------------------------------------------------------------------------

A4_BIRIMLER = ("GB", "MB", "kW", "V", "L", "mL", "m2", "C")
A4_EKLER = ("bulunma", "ayrilma", "yonelme", "belirtme", "lik", "vasita")
A4_GRUP = {"veri": ("GB", "MB"), "guc": ("kW", "V"), "hacim": ("L", "mL"), "alan": ("m2",), "sicaklik": ("C",),
           "any": A4_BIRIMLER}


def _olcu_deger_bucuk(rng, b):
    tam, kesir = V._olcu_degeri(rng, b)
    if tam == 0 and not kesir:
        tam = rng.randint(1, 30)
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.6
    rr = len(kesir) == 2 and kesir[0] != "0" and rng.random() < 0.1
    return tam, kesir, bucuk, rr


def ornekle_a4(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or "any"
    b = CTX.birim if CTX.birim in A4_GRUP[alt] else rng.choice(A4_GRUP[alt])
    tam, kesir, bucuk, rr = _olcu_deger_bucuk(rng, b)
    return V.kur_olcu(tam, kesir, b, rng.randrange(2), bucuk, rr, ek)


# ---- A5: bileşik ölçü ve süre --------------------------------------------------------------------------

def _ad(rng, lo, hi, adim):
    return rng.randrange(lo, hi + 1, adim)


def _g_deger(r):
    return r.choice([100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 750, 800, 900]) if r.random() < 0.7 else r.randint(10, 990)


def _dk_deger(r):
    return _ad(r, 5, 55, 5) if r.random() < 0.7 else r.randint(1, 59)


_ZINCIRLER = {
    "agirlik": [(("kg", lambda r: r.randint(1, 20)), ("g", _g_deger))],
    "ton": [(("ton", lambda r: r.randint(1, 20)), ("kg", lambda r: r.choice([50, 100, 200, 250, 300, 400, 500, 600, 750, 800, 900]) if r.random() < 0.7 else r.randint(10, 990)))],
    "boy": [(("m", lambda r: r.randint(1, 3)), ("cm", lambda r: r.randint(5, 99)))],
    "mesafe": [(("km", lambda r: r.randint(1, 60)), ("m", lambda r: _ad(r, 50, 950, 50) if r.random() < 0.7 else r.randint(10, 990)))],
    "hacim": [(("L", lambda r: r.randint(1, 10)), ("mL", lambda r: _ad(r, 50, 950, 50) if r.random() < 0.7 else r.randint(10, 990)))],
    "kucuk": [(("cm", lambda r: r.randint(1, 30)), ("mm", lambda r: r.randint(1, 9)))],
    "sure": [(("saat", lambda r: r.randint(1, 12)), ("dakika", _dk_deger)),
             (("dakika", lambda r: r.randint(1, 30)), ("saniye", _dk_deger)),
             (("saat", lambda r: r.randint(1, 6)), ("dakika", _dk_deger), ("saniye", _dk_deger))],
    "gun": [(("gun", lambda r: r.randint(1, 6)), ("saat", lambda r: r.randint(1, 23))),
            (("hafta", lambda r: r.randint(1, 4)), ("gun", lambda r: r.randint(1, 6))),
            (("ay", lambda r: r.randint(1, 11)), ("gun", lambda r: r.randint(1, 29))),
            (("yil", lambda r: r.randint(1, 30)), ("ay", lambda r: r.randint(1, 11)))],
}


def ornekle_bilesik(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    zincir = rng.choice(_ZINCIRLER[alt or "agirlik"])
    parcalar = [(f(rng), b) for b, f in zincir]
    return kur_bilesik(parcalar, ek, [rng.randrange(2) for _ in parcalar])


# ---- A6: yeni birimler ----------------------------------------------------------------------------------

KISA_YENI = ("mg", "m3", "km2", "kwh", "hz", "mhz")
FIZ_YENI = ("ton", "inc", "kalori", "hektar", "donum", "beygir", "piksel", "karat")
ZAMAN_YENI = ("saat", "dakika", "saniye", "gun", "hafta", "ay", "yil")
YENI_GRUP = {"kisa": KISA_YENI, "fiz": FIZ_YENI, "zaman": ZAMAN_YENI, "yas": ("yas",),
             "ksure": ("saniye", "dakika", "saat"), "usure": ("gun", "hafta", "ay", "yil")}
YENI_ETIKETLER = KISA_YENI + FIZ_YENI + ZAMAN_YENI + ("yas",)
_YAS_BICIMI = {None: "yaş", "bulunma": "yaşında", "yonelme": "yaşına", "ayrilma": "yaşından",
               "bulunma_ki": "yaşındaki", "belirtme": "yaşını"}


def _yeni_deger(rng, t):
    """(tam, kesir) — zaman birimleri ve yaş: 10 ve üstü (küçük sayı politikası, bkz. A8)."""
    if t == "mg":
        return (rng.choice([5, 10, 20, 25, 50, 100, 200, 250, 500, 750]), "") if rng.random() < 0.6 else V._ondalikli(rng, 1, 900, 0.1)
    if t == "m3":
        return V._ondalikli(rng, 1, 300, 0.2)
    if t == "km2":
        return V._ondalikli(rng, 2, 2500, 0.1)
    if t == "kwh":
        return V._ondalikli(rng, 1, 1500, 0.2)
    if t == "hz":
        return (rng.choice([50, 60, 100, 440, 1000, 2000, 5000, 20000]), "") if rng.random() < 0.6 else (rng.randint(20, 20000), "")
    if t == "mhz":
        return V._ondalikli(rng, 88, 108, 0.5) if rng.random() < 0.5 else (rng.choice([800, 1200, 1600, 2400, 3200, 4000]), "")
    if t == "ton":
        return V._ondalikli(rng, 2, 60, 0.2)
    if t == "inc":
        return (rng.choice([14, 15, 17, 19, 21, 24, 27, 32, 40, 43, 50, 55, 65, 75, 85]), "") if rng.random() < 0.7 else (rng.randint(5, 90), "")
    if t == "kalori":
        return (rng.choice([50, 100, 120, 150, 200, 250, 300, 400, 500, 800, 1200, 1500, 1800, 2000, 2200, 2500, 3000]), "") if rng.random() < 0.7 else (rng.randint(20, 3500), "")
    if t == "hektar":
        return V._ondalikli(rng, 2, 500, 0.1)
    if t == "donum":
        return rng.randint(2, 300), ""
    if t == "beygir":
        return (rng.choice([50, 60, 75, 90, 100, 110, 120, 150, 180, 200, 250, 300, 400, 500, 600]), "") if rng.random() < 0.8 else (rng.randint(30, 700), "")
    if t == "piksel":
        return (rng.choice([128, 256, 320, 480, 640, 720, 800, 1024, 1080, 1280, 1920, 2160, 3840, 4096]), "") if rng.random() < 0.7 else (rng.randint(100, 5000), "")
    if t == "karat":
        return (rng.choice([8, 14, 18, 22, 24]), "") if rng.random() < 0.4 else (rng.randint(2, 30), "")
    if t == "saat":
        return rng.randint(10, 72), ""
    if t == "dakika":
        return (_ad(rng, 10, 90, 5) if rng.random() < 0.6 else rng.randint(10, 90)), ""
    if t == "saniye":
        return (_ad(rng, 10, 120, 5) if rng.random() < 0.5 else rng.randint(10, 120)), ""
    if t == "gun":
        return rng.randint(10, 120), ""
    if t == "hafta":
        return rng.randint(10, 52), ""
    if t == "ay":
        return rng.randint(10, 48), ""
    if t == "yil":
        return rng.randint(10, 100), ""
    raise KeyError(t)


def ornekle_yeni(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or "kisa"
    grup = YENI_GRUP.get(alt, (alt,))
    t = CTX.birim if CTX.birim in grup else rng.choice(grup)
    if t == "yas":
        return kur_yas(rng.randint(10, 21) if ek is None else rng.randint(10, 95), _YAS_BICIMI[ek])
    tam, kesir = _yeni_deger(rng, t)
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.6
    rr = len(kesir) == 2 and kesir[0] != "0" and rng.random() < 0.1
    return kur_olcu2(tam, kesir, t, rng.randrange(2), bucuk, rr, ek)


# ---- A8: küçük sayı politikası -----------------------------------------------------------------------------

def ornekle_kucuk(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if CTX.a8_kucuk:
        n = rng.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [3, 8, 13, 13, 12, 12, 11, 10, 9, 9])[0]
    else:
        r = rng.random()
        n = rng.randint(10, 99) if r < 0.82 else rng.randint(100, 999) if r < 0.97 else rng.randint(1000, 9999)
    return V.kur_kardinal(n, "yaziyla", None)


_ORNEKLEYICILER2 = {
    "v2sifir": ornekle_sifirli, "v2tel": ornekle_tel, "v2kod": ornekle_kod2, "v2ar": ornekle_aralik2,
    "v2ol": ornekle_a4, "v2bil": ornekle_bilesik, "v2yeni": ornekle_yeni, "v2kc": ornekle_kucuk,
}

_FILLERS2 = {
    "v2_dukkan": ["bakkal", "manav", "kasap", "kırtasiye", "eczane", "fırın", "market", "büfe"],
    "v2_arac": ["otobüs", "tren", "minibüs", "vapur", "tır", "kamyon", "taksi", "servis"],
    "v2_gun": ["pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar"],
    "v2_hayvan": ["kedi", "köpek", "kuş", "balık", "tavşan", "at", "inek", "koyun"],
    "v2_hizmet": ["tamir", "montaj", "nakliyat", "temizlik", "bakım", "kargo", "tadilat"],
    "v2_oda": ["salon", "mutfak", "yatak odası", "balkon", "çocuk odası", "koridor", "depo"],
    "v2_okul": ["lise", "ilkokul", "ortaokul", "üniversite", "kurs", "yurt"],
    "v2_alet": ["matkap", "dizüstü bilgisayar", "tablet", "projeksiyon", "yazıcı", "kamera", "hoparlör", "klima"],
}


def kaydet():
    V.ORNEKLEYICILER.update(_ORNEKLEYICILER2)
    B.FILLERS.update(_FILLERS2)


def kaldir():
    for k in _ORNEKLEYICILER2:
        V.ORNEKLEYICILER.pop(k, None)
    for k in _FILLERS2:
        B.FILLERS.pop(k, None)


@contextlib.contextmanager
def kayitli():
    kaydet()
    try:
        yield
    finally:
        kaldir()


# ======================================================================================================
# 4. TAŞIYICI ŞABLONLAR
# ======================================================================================================
# Biçim: {ad}, {ad.alt}, {ad.alt:ek}. Taşıyıcı metinde sayı sözcüğü ya da eş yazımlı sözcük (yüz, bin, on, altı, yedi ...)
# bulunmaz: bunlar girdide değişmeden kalacağından etiketi bozar.
_A: dict[str, str] = {}

_A["sifir"] = """
Toplam tutar {v2sifir.tl} olarak hesaplandı
Faturanın son hali {v2sifir.tl} çıktı
Kira bedelini {v2sifir.para} olarak belirledik
Hesabıma bu sabah {v2sifir.tl} yattı
Sigortalı {esya} için ödenecek bedel {v2sifir.para} çıktı
Noterde {v2sifir.tl} harç ödedik
Aylık maaşı {v2sifir.para} olarak yazmışlar
{isim} tamirciye {v2sifir.tl} verdi
Arsanın değeri {v2sifir.para} civarında
Borcun kalan kısmı {v2sifir.tl} kaldı
Bağış kampanyasında {v2sifir.para} toplandı
Yıllık aidat {v2sifir.tl} tuttu
Çekilen kredi {v2sifir.para} idi
Kasada tam {v2sifir.tl} vardı
Dükkânın günlük cirosu {v2sifir.para} oldu
Evi {v2sifir.para:yonelme} sattık
Aracı {v2sifir.tl:ayrilma} aşağıya vermem
Peşinatı {v2sifir.para:belirtme} ödedim
Fiyat {v2sifir.para:bulunma} sabitlendi
{v2sifir.tl:lik} bir fatura geldi
Masrafı {v2sifir.para:vasita} karşıladık
Zamdan sonra bilet {v2sifir.tl:yonelme} çıktı
Faturayı {v2sifir.para:ilgi} altına düşürdük
Yurt dışından {v2sifir.dolar} gönderdiler
Hesapta {v2sifir.dolar} birikmişti
Sözleşme bedeli {v2sifir.dolar:yonelme} yükseldi
Yol toplam {v2sifir.mesafe} tuttu
Depo {v2sifir.agirlik} yük taşıyor
Dosya boyutu {v2sifir.veri} olmuş
Cihaz {v2sifir.olcu} değerine ulaştı
Kargo {v2sifir.agirlik} ağırlığında çıktı
Uçak toplam {v2sifir.mesafe} yol yaptı
Sunucuda {v2sifir.veri} yer kaldı
Ölçüm sonucu {v2sifir.olcu} gösterdi
Kamyon {v2sifir.agirlik:lik} bir yükle yola çıktı
Depolama alanını {v2sifir.veri:yonelme} çıkardık
Sayaç {v2sifir.mesafe:yonelme} ulaştı
Kablo {v2sifir.mesafe:ayrilma} uzun
Raporda {v2sifir.olcu:belirtme} yanlış yazmışlar
Yükü {v2sifir.agirlik:vasita} sınırladık
Stada {v2sifir.kisi} {kisi} geldi
Etkinliğe toplam {v2sifir.kisi} {kisi} katıldı
Kentte yaşayan {v2sifir.kisi} {kisi} oy kullandı
Sınava {v2sifir.kisi} {kisi} girdi
Şirkette {v2sifir.kisi} {kisi} çalışıyor
Festivali {v2sifir.kisi} {kisi} izledi
Anketimize {v2sifir.kisi} {kisi} cevap verdi
{sehir} gezisine {v2sifir.kisi} {kisi} kayıt oldu
Videonun izlenme sayısı {v2sifir.sayi} oldu
Sayaçta {v2sifir.sayi} yazıyordu
Kitabın tirajı {v2sifir.sayi} adet
Takipçi sayısı {v2sifir.sayi} oldu
Sitenin ziyaretçi sayısı {v2sifir.sayi} olmuş
Toplam {v2sifir.sayi} adet sipariş aldık
Oy sayısı {v2sifir.sayi:yonelme} ulaştı
Sıra numarası {v2sifir.sayi:bulunma} kaldı
Sipariş sayısı {v2sifir.sayi:ayrilma} fazla olamaz
Hedef sayıyı {v2sifir.sayi:belirtme} bulduk
Ülkenin nüfusu {v2sifir.buyuk} olarak açıklandı
Şehirde yaşayanların sayısı {v2sifir.buyuk} oldu
Şirketin cirosu {v2sifir.buyuktl} oldu
Bütçeden {v2sifir.buyuktl} ayrıldı
Kampanyaya {v2sifir.buyuktl} bağış geldi
Hazine {v2sifir.buyuktl:ayrilma} fazla borçlandı
Uygulamayı {v2sifir.buyuk} kez indirmişler
Bu rakam {v2sifir.buyuk:yonelme} ulaştı
"""

_A["tel"] = """
Yeni numaram {v2tel} oldu
Beni {v2tel} numarasından arayabilirsin
Randevu için {v2tel} numarasını arayın
{isim} bana {v2tel} diye bir numara verdi
Kuryenin telefonu {v2tel}
Rehbere {v2tel} olarak kaydetti
Servisin hattı {v2tel}
Acil durumda {v2tel} numarasına ulaşın
Müşteri temsilcisi {v2tel} üzerinden dönüş yapacak
Mesajı {v2tel} numarasına gönderdim
Kapıdaki notta {v2tel} yazıyordu
Ev sahibinin numarası {v2tel} imiş
Sipariş sorunları için {v2tel} hattını arayabilirsiniz
{v2tel} numaralı hattan çağrı geldi
Şikâyet hattı {v2tel} olarak değişti
Eczanenin nöbetçi numarası {v2tel}
Rezervasyon {v2tel} numarasından yapılıyor
Aradığınız kişinin telefonu {v2tel}
Resepsiyon {v2tel} numarasına bağlı
{v2tel} numarasına mesaj yazdım
Taksi durağını {v2tel} numarasından çağırdım
Sahibinden satılık ilanda iletişim {v2tel}
Okulun muhasebesi {v2tel} numarasında
Faturadaki iletişim numarası {v2tel} yazıyor
Not defterime {v2tel} yazmışım
Tamirciyi {v2tel} numarasından buldum
Doktorun sekreteri {v2tel} numarasını verdi
Kargo takibi için {v2tel} numarasını arayın
Misafir hattı {v2tel} olarak güncellendi
{isim} dün {v2tel} numarasından aradı
Numarayı {v2tel} diye kaydet
Toplantı bağlantısı {v2tel} numarasına gelecek
Yedek numaram {v2tel} olacak
Veteriner kliniği {v2tel} numarasında
{v2tel:yonelme} mesaj attım
{v2tel:ayrilma} bir arama kaçırdım
{v2tel:belirtme} defalarca aradım ama açmadı
{v2tel:vasita} konuşmak istiyorum
{v2tel:ilgi} sahibi kim acaba
Çağrı {v2tel:ayrilma} yapılmış
Dönüş yapmak için {v2tel:yonelme} ulaşın
Hattı {v2tel:belirtme} tanımladık
Haber vermek için {v2tel:vasita} irtibata geçti
Fatura {v2tel:ilgi} adına kesilmiş
Gelen arama {v2tel:ayrilma} değildi
Kaydı {v2tel:belirtme} güncelledim
Çocuğun okulu {v2tel:yonelme} haber verdi
Sipariş bilgisi {v2tel:yonelme} iletilecek
"""

_A["kod"] = """
Doğrulama kodunuz {v2kod}
Kapı şifresi {v2kod} olarak değiştirildi
Güvenlik kodunu {v2kod} diye girin
Kayıt kodunuz {v2kod} olarak oluşturuldu
İşlemin referans kodu {v2kod}
Kargo teslim kodu {v2kod} unutma
Kuponu {v2kod} koduyla kullanabilirsiniz
Dolabın şifresi {v2kod} mi
Aktivasyon kodu {v2kod}
Mesajdaki onay kodu {v2kod}
Ürün kodunu {v2kod} olarak yazın
Erişim anahtarı {v2kod} idi
Kasanın kodu {v2kod} değil mi
Garaj kapısının kodu {v2kod}
Randevu kodunuz {v2kod}
Fatura numarası {v2kod.orta}
Dosya numaranız {v2kod.orta} olarak kaydedildi
Abonelik kodu {v2kod.orta}
Parça numarası {v2kod.orta} olan filtreyi isteyin
Stok kodu {v2kod.orta}
Takip numaranız {v2kod.uzun}
Sipariş numarası {v2kod.uzun}
Abone numaranız {v2kod.uzun} olarak geçiyor
Müşteri numarası {v2kod.uzun}
Kargo takip numarası {v2kod.uzun} ile sorgulayın
Poliçe numarası {v2kod.uzun} idi
Başvuru numaranızı {v2kod.uzun} diye not edin
Sicil numarası {v2kod.uzun}
Tahsilat makbuzu numarası {v2kod.uzun}
Kimlik numaram {v2kod.tc}
Kimlik numarası {v2kod.tc} olan kişi aranıyor
Vatandaşlık numarasını {v2kod.tc} olarak yazın
Formda kimlik numarası {v2kod.tc} girilmiş
Hasta kimlik numarası {v2kod.tc}
Posta kodu {v2kod.posta}
Adresin posta kodu {v2kod.posta} olarak geçiyor
Kargo etiketinde posta kodu {v2kod.posta} yazıyor
Evimizin posta kodu {v2kod.posta}
Kartın pin kodu {v2kod.pin}
Telefon kilidinin şifresi {v2kod.pin}
Alarm kodu {v2kod.pin} olarak ayarlandı
Banka uygulamasının parolası {v2kod.pin}
Asansör kodu {v2kod.kisa}
Oda numarası {v2kod.kisa}
Hat kodu {v2kod.kisa} olarak girilecek
Kat şifresi {v2kod.kisa}
Dolap numarası {v2kod.kisa} olan kapıyı aç
Sınıf kodu {v2kod.kisa}
"""

_A["aralik"] = """
İş {v2ar} gün sürer
Toplantı {v2ar} dakika sürecek
Kargo {v2ar} iş günü içinde gelir
Salona {v2ar} {kisi} sığar
Yolculuk {v2ar} saat sürüyor
Sınıfta {v2ar} {kisi} eksikti
Sipariş {v2ar} gün içinde hazır olur
Kurs {v2ar} hafta devam ediyor
{v2ar} dakika sonra yanınızda olurum
Bahçeye {v2ar} fidan dikeceğiz
Tarifte {v2ar} dilim ekmek yazıyor
Her gün {v2ar} sayfa okuyorum
Başvuru sonucu {v2ar} gün içinde belli olur
{isim} {v2ar} yıldır burada çalışıyor
Garanti süresi {v2ar} ay arasında değişiyor
Fiyatlar {v2ar.tl} arasında değişiyor
Montun fiyatı {v2ar.tl} civarında
Bütçem {v2ar.tl} kadar
Tamir ücreti {v2ar.tl} tutar
Yemek başına {v2ar.tl} ödüyoruz
Çanta {v2ar.agirlik} geliyor
Paketin ağırlığı {v2ar.agirlik}
Sıcaklık {v2ar.sicaklik} olacak
Fırını {v2ar.sicaklik} ısıtın
Okula {v2ar.mesafe} var
Burası {v2ar.mesafe} ileride
Şişenin içine {v2ar.hacim} su sığar
Tarif için {v2ar.hacim} süt lazım
Her gün {v2ar.hacim} su içiyorum
Çöp bidonu {v2ar.cm} genişliğinde
Kablo {v2ar.cm} uzunluğunda
Sipariş {v2ar.dolar} tutuyor
Ücret {v2ar.dolar} arasında
Kutunun içinden {v2ar.agirlik:lik} bir paket çıktı
Çocuk {v2ar.tl:lik} bir hediye istiyor
{v2ar.hacim:lik} bir şişe lazım
Hedef bütçeyi {v2ar.tl:ayrilma} aşağı tutalım
Valiz {v2ar.agirlik:ayrilma} fazla olmasın
Tatili {v2ar.tl:yonelme} ayarladık
Yürüyüşü {v2ar.mesafe:yonelme} çıkardık
Sıcaklığı {v2ar.sicaklik:yonelme} getirdik
Tarifteki unu {v2ar.agirlik:belirtme} geçmeyin
Pazarlıkta fiyatı {v2ar.tl:yonelme} indirdiler
Koşuyu {v2ar.mesafe:vasita} tamamladı
Fiyat {v2ar.tl:ilgi} ortasında bir değer
Rakamı {v2ar.dolar:belirtme} kaçırdık
Masrafı {v2ar.tl:vasita} karşıladık
Kapının eni {v2ar.cm:ayrilma} dar olmamalı
Termos {v2ar.hacim:ayrilma} az su alıyor
Süre {v2ar.sicaklik:bulunma} sabit kalıyor
"""

_A["birim"] = """
Dosya {v2ol.veri:bulunma} takılıp kaldı
Yükleme {v2ol.veri:bulunma} yarıda kesildi
Dosya {v2ol.veri:ayrilma} büyük olmamalı
Paket {v2ol.veri:ayrilma} sonra yavaşlıyor
Kotayı {v2ol.veri:yonelme} çıkardık
Hafıza {v2ol.veri:yonelme} yükseltildi
Telefonda {v2ol.veri:belirtme} boşalttım
Yedekleme {v2ol.veri:belirtme} aştı
{v2ol.veri:lik} bir paket aldım
{v2ol.veri:lik} bir kart taktım
Depolamayı {v2ol.veri:vasita} genişlettik
Kayıtlar {v2ol.veri:vasita} sınırlı kaldı
Cihaz {v2ol.guc:bulunma} çalışıyor
Sistem {v2ol.guc:bulunma} stabil kaldı
Motor {v2ol.guc:ayrilma} fazla güç çekmez
Hat {v2ol.guc:ayrilma} sonra devre dışı kalır
Gerilim {v2ol.guc:yonelme} çıktı
Kapasiteyi {v2ol.guc:yonelme} yükselttik
Ölçü aleti {v2ol.guc:belirtme} gösterdi
Trafo {v2ol.guc:belirtme} aşmıyor
{v2ol.guc:lik} bir adaptör taktık
{v2ol.guc:lik} bir jeneratör aldık
Cihazı {v2ol.guc:vasita} besledik
Priz {v2ol.guc:vasita} sınırlı
Depo {v2ol.hacim:bulunma} doldu
Şişe {v2ol.hacim:bulunma} taştı
Kap {v2ol.hacim:ayrilma} az tutmaz
Reçetedeki ilaç {v2ol.hacim:ayrilma} fazla içilmez
Haznesi {v2ol.hacim:yonelme} genişletildi
Tank {v2ol.hacim:yonelme} kadar doldu
Kazan {v2ol.hacim:belirtme} aşmıyor
Şurubu {v2ol.hacim:belirtme} geçmemeli
{v2ol.hacim:lik} bir şişe aldım
{v2ol.hacim:lik} bir kap lazım
Tankı {v2ol.hacim:vasita} doldurdum
Kabı {v2ol.hacim:vasita} ölçtüm
Mağaza {v2ol.alan:bulunma} faaliyet gösteriyor
Atölye {v2ol.alan:bulunma} kurulu
Salon {v2ol.alan:ayrilma} küçük olmamalı
Arsa {v2ol.alan:ayrilma} büyük
Daireyi {v2ol.alan:yonelme} büyüttük
Alan {v2ol.alan:yonelme} genişledi
Villa {v2ol.alan:belirtme} buluyor
Bahçe {v2ol.alan:belirtme} geçiyor
{v2ol.alan:lik} bir daire arıyoruz
{v2ol.alan:lik} bir ofis kiraladık
Mutfak {v2ol.alan:vasita} yetinmek zorundayız
Depoyu {v2ol.alan:vasita} sınırladık
Su {v2ol.sicaklik:bulunma} kaynıyor
Fırın {v2ol.sicaklik:bulunma} pişirin
Sıcaklık {v2ol.sicaklik:ayrilma} fazla çıkmasın
Ortam {v2ol.sicaklik:ayrilma} aşağı inmemeli
Termostatı {v2ol.sicaklik:yonelme} ayarladık
Klima {v2ol.sicaklik:yonelme} getirildi
Termometre {v2ol.sicaklik:belirtme} gösterdi
Hava {v2ol.sicaklik:belirtme} buldu
{v2ol.sicaklik:lik} bir kış günüydü
{v2ol.sicaklik:lik} bir hava bekleniyor
Sıcaklığı {v2ol.sicaklik:vasita} sınırlayın
Gece {v2ol.sicaklik:vasita} soğudu
Ölçüm {v2ol.any:bulunma} durdu
Sayaç {v2ol.any:bulunma} kilitlendi
Cihaz {v2ol.any:bulunma} sabitlendi
Rapor {v2ol.any:bulunma} bitiyor
Değer {v2ol.any:ayrilma} fazla çıkmamalı
Limit {v2ol.any:ayrilma} sonra devreye giriyor
Okuma {v2ol.any:ayrilma} geriye düştü
Kayıt {v2ol.any:ayrilma} başlıyor
Sınırı {v2ol.any:yonelme} çektik
Eşik {v2ol.any:yonelme} yükseldi
Değeri {v2ol.any:yonelme} sabitledik
Ayar {v2ol.any:yonelme} getirildi
Tabloda {v2ol.any:belirtme} gördüm
Sensör {v2ol.any:belirtme} gösterdi
Formda {v2ol.any:belirtme} yazmışlar
Cihaz {v2ol.any:belirtme} aşmamalı
Etiketinde {v2ol.any:lik} bir ibare var
{v2ol.any:lik} bir kutu istiyorum
{v2ol.any:lik} bir model satıyorlar
Yeni sınır {v2ol.any:lik} bir değer
Ölçümü {v2ol.any:vasita} tamamladık
Raporu {v2ol.any:vasita} kapattık
Kaydı {v2ol.any:vasita} sınırladılar
Sonucu {v2ol.any:vasita} onayladık
"""

_A["bilesik"] = """
Pazardan {v2bil.agirlik} {urun} aldım
Bebek {v2bil.agirlik} doğdu
Valiz {v2bil.agirlik} çekti
Kargo {v2bil.agirlik} geldi
Yeni doğan kuzu {v2bil.agirlik} gelmiş
{isim} spor için {v2bil.agirlik} verdi
Yük arabası {v2bil.ton} taşıyor
Kamyonet {v2bil.ton} yükle yola çıktı
Kardeşimin boyu {v2bil.boy} oldu
Kapı {v2bil.boy} yüksekliğinde
Dolap {v2bil.boy} genişliğinde
Basketbolcunun boyu {v2bil.boy}
Okul servisi {v2bil.mesafe} yol yaptı
Köye {v2bil.mesafe} kaldı
Koşucu {v2bil.mesafe} koştu
Yürüyüş parkuru {v2bil.mesafe} uzunluğunda
Tarife {v2bil.hacim} süt yazıyor
Depoya {v2bil.hacim} yakıt aldık
Şişede {v2bil.hacim} su var
Hastaya {v2bil.hacim} serum verildi
Çizginin kalınlığı {v2bil.kucuk}
Tahta {v2bil.kucuk} kalınlığında
Film {v2bil.sure} sürdü
Toplantı {v2bil.sure} devam etti
Uçuş {v2bil.sure} sürecek
Yemeği {v2bil.sure} hazırladı
Pasta {v2bil.sure} pişti
Yarışı {v2bil.sure} bitirdi
Rekor {v2bil.sure} oldu
Fırında {v2bil.sure} bekletin
Kurs {v2bil.gun} sürecek
Bebek {v2bil.gun} oldu
Ev işleri {v2bil.gun} aldı
{isim} yurt dışında {v2bil.gun} kaldı
Proje {v2bil.gun} içinde bitti
İş {v2bil.gun} sürdü
Çocuk {v2bil.agirlik:lik} bir paket taşıdı
Hediye olarak {v2bil.agirlik:lik} bir koli yolladılar
{v2bil.hacim:lik} bir kap lazım
{v2bil.kucuk:lik} bir çıta kestik
{v2bil.mesafe:lik} bir yolu yürüdük
{v2bil.boy:lik} bir halı serdik
Dersi {v2bil.sure:lik} bir videoyla anlattı
Mola {v2bil.sure:lik} bir arayla bitti
Yemek {v2bil.sure:bulunma} hazır oldu
Kargo {v2bil.gun:bulunma} elimize ulaştı
Pasta {v2bil.sure:bulunma} soğudu
Yol {v2bil.sure:ayrilma} kısa sürmez
Şiir {v2bil.sure:ayrilma} fazla sürmedi
Bavul {v2bil.agirlik:ayrilma} ağır olmamalı
Çubuk {v2bil.boy:ayrilma} uzun
Proje {v2bil.gun:yonelme} kaldı
Filmi {v2bil.sure:belirtme} aşmayın
Kupayı {v2bil.sure:vasita} kazandı
Tarifi {v2bil.hacim:vasita} bitirdik
Süreyi {v2bil.sure:ilgi} üstüne taşıdı
Teslimat {v2bil.gun:ayrilma} geç olmaz
Yürüyüşü {v2bil.mesafe:yonelme} çıkardık
Rekora {v2bil.sure:yonelme} çıktı
Hamuru {v2bil.sure:vasita} dinlendirdik
"""

_A["yeni"] = """
Hastaya {v2yeni.mg} ilaç yazdı
Tablet başına {v2yeni.mg} etken madde düşüyor
Vitaminin içinde {v2yeni.mg} var
Doktor {v2yeni.mg:lik} bir doz önerdi
Etiketinde {v2yeni.mg:ayrilma} fazlası yazmıyor
İlaç {v2yeni.mg:yonelme} çıkarıldı
Havuz {v2yeni.m3} su alıyor
Kamyon {v2yeni.m3} kum taşıdı
Su sayacı {v2yeni.m3} gösteriyor
Apartman aylık {v2yeni.m3} doğalgaz yaktı
Silo {v2yeni.m3:lik} bir hacme sahip
Tank {v2yeni.m3:bulunma} doldu
Depo {v2yeni.m3:ayrilma} fazla alıyor
Barajın hacmi {v2yeni.m3:yonelme} yükseldi
İlin yüz ölçümü {v2yeni.km2}
Göl {v2yeni.km2} büyüklüğünde
Orman {v2yeni.km2} alanı kaplıyor
{sehir} {v2yeni.km2:lik} bir alana yayılmış
Yangın {v2yeni.km2:bulunma} etkili oldu
Ada {v2yeni.km2:ayrilma} büyük
Alan {v2yeni.km2:yonelme} genişletildi
Bu ay elektrik tüketimi {v2yeni.kwh} oldu
Güneş paneli günde {v2yeni.kwh} üretiyor
Pil kapasitesi {v2yeni.kwh} civarında
Fatura {v2yeni.kwh} üzerinden kesilmiş
Depo {v2yeni.kwh:lik} bir batarya taktık
Tüketim {v2yeni.kwh:bulunma} sabit kaldı
Sistem {v2yeni.kwh:ayrilma} fazla çekmez
Ev kullanımını {v2yeni.kwh:yonelme} indirdik
Hoparlör {v2yeni.hz} frekansta çalışıyor
Ses {v2yeni.hz} civarında yükseliyor
Şebeke {v2yeni.hz} olarak çalışıyor
Cihaz {v2yeni.hz:bulunma} titreşiyor
Frekansı {v2yeni.hz:yonelme} ayarladık
Ekran {v2yeni.hz:lik} bir yenileme hızıyla geliyor
Radyo {v2yeni.mhz} yayın yapıyor
İşlemci {v2yeni.mhz} hızında çalışıyor
Kanalı {v2yeni.mhz:yonelme} aldım
Yayın {v2yeni.mhz:bulunma} net geliyor
Vericiyi {v2yeni.mhz:belirtme} tuttu
Ürün {v2yeni.ton} yük kaldırıyor
Gemi {v2yeni.ton} yükle limandan ayrıldı
Vinç {v2yeni.ton:lik} bir yük kaldırır
Kamyonet {v2yeni.ton:ayrilma} fazla taşımaz
Çelik {v2yeni.ton:yonelme} çıktı
Televizyon {v2yeni.inc} ekranlı
Yeni aldığım monitör {v2yeni.inc}
Dizüstü {v2yeni.inc:lik} bir ekranla geliyor
Ekran {v2yeni.inc:ayrilma} büyük olmalı
Menü {v2yeni.kalori} içeriyor
Bir porsiyon {v2yeni.kalori} tutuyor
Günlük diyetim {v2yeni.kalori:lik} bir plan
Yemek {v2yeni.kalori:ayrilma} fazla değildi
Çiftlik {v2yeni.hektar} araziye sahip
Tarla {v2yeni.hektar} büyüklüğünde
Zeytinlik {v2yeni.hektar:lik} bir alana ekilmiş
Bahçe {v2yeni.donum} genişliğinde
Arazi {v2yeni.donum:lik} bir parsel
Arabanın gücü {v2yeni.beygir}
Traktör {v2yeni.beygir:lik} bir motor taşıyor
Kamera {v2yeni.piksel} çözünürlüğünde çekiyor
Fotoğraf {v2yeni.piksel} genişliğinde
Yüzük {v2yeni.karat} altından yapılmış
Bilezik {v2yeni.karat:lik} bir altın
Kuyumcu bu kolyenin {v2yeni.karat} olduğunu söyledi
Küpeler {v2yeni.karat} altından
Taşın ağırlığı {v2yeni.karat}
Pırlanta {v2yeni.karat:ayrilma} küçük değil
Araba {v2yeni.beygir:ayrilma} güçlü değil
Motor {v2yeni.beygir} üretiyor
Pickup {v2yeni.beygir} gücünde
Teknenin makinesi {v2yeni.beygir:lik}
Televizyonun boyu {v2yeni.inc} civarında
Telefon ekranı {v2yeni.inc} ölçüsünde
Tabletin ekranı {v2yeni.inc:lik}
Lastiğin çapı {v2yeni.inc}
Tarlanın alanı {v2yeni.donum}
Arsa {v2yeni.donum:ayrilma} küçük değil
Bahçe {v2yeni.donum:bulunma} kuruldu
Fotoğrafın boyutu {v2yeni.piksel}
Ekran {v2yeni.piksel:lik} bir genişliğe sahip
Görüntü {v2yeni.piksel:ayrilma} büyük olamaz
Çiftçi {v2yeni.hektar:belirtme} sulamış
Arazi {v2yeni.hektar:ayrilma} büyük
{v2yeni.ksure} sonra döneceğim
Yemek {v2yeni.ksure:bulunma} hazır olur
Toplantı {v2yeni.ksure:ayrilma} fazla sürmez
Mola {v2yeni.ksure} sürdü
Sınav {v2yeni.ksure:lik} bir süre veriyor
Ders {v2yeni.ksure:yonelme} uzadı
Bilet satışı {v2yeni.ksure:vasita} bitti
Tamirat {v2yeni.ksure:belirtme} aştı
Film {v2yeni.ksure:ilgi} üzerinde sürdü
Proje {v2yeni.usure} sürdü
Kitabı {v2yeni.usure} içinde bitirdim
Teslimat {v2yeni.usure:bulunma} yapılır
Sipariş {v2yeni.usure:ayrilma} önce verilmişti
Kurs {v2yeni.usure:lik} bir programla başladı
Ödemeyi {v2yeni.usure:yonelme} erteledik
Staj {v2yeni.usure} sürecek
Tatil planını {v2yeni.usure:belirtme} geçmesin
Tadilat {v2yeni.usure:vasita} tamamlandı
{isim} {v2yeni.yas:bulunma} bir adam
Müşterimiz {v2yeni.yas:bulunma} olup {sehir} sakini
Bu oyun {v2yeni.yas} ve üzeri için uygun
Dedem {v2yeni.yas:yonelme} girdi
{v2yeni.yas:ayrilma} sonra emekli olunur
Eşimin dedesi {v2yeni.yas:belirtme} doldurdu
{v2yeni.yas:bulunma_ki} bir çocuk kazayı gördü
Annemin arkadaşı {v2yeni.yas:bulunma} diye duydum
"""

_A["uzun"] = """
{tarih.gunay} günü saat {saat:bulunma} {sehir} otogarında buluşup, bilet için kişi başı {para.tam} ödeyeceğiz
Eve gelince {olcu.agirlik} {urun} aldığımı fark ettim, kasada ise {para.tl} ödemiştim
Doktor {tarih.gunay} tarihine randevu verdi, saat {saat} civarında orada olmamı söyledi
Sınıfımızda {kardinal.orta} öğrenci var, bunların {yuzde} kadarı sınavdan geçti
Yolun uzunluğu {olcu.mesafe} ve {aralik} saat sürüyor, benzin masrafı da {para.tam} tutuyor
{isim} {tarih.tam} tarihinde doğdu ve bugün tam {kardinal.yas} yaşında
Kargonuz {tarih.gunay} günü saat {saat:bulunma} teslim edilecek, tutar {para.tl} olarak hesaplandı
Hava bugün {eksi.derece} olacak, nem oranı {yuzde} civarında kalacak diyorlar
Yeni telefon {olcu.veri} hafızalı, ekranı çok güzel ama fiyatı {para.tam}
Maçı {skor} kazandık ama {kardinal.bin} {kisi} stadı terk ederken kimse konuşmadı
Toplantı {tarih.gunay} günü yapılacak, saat {saat} gibi başlayıp {aralik} saat sürecek
Mağazada {yuzde} indirim var, indirimli fiyat {para.tl} olunca hemen aldım
{olcu.mesafe} yol gittik ve yolda {para.kucuk} bozuk para harcadık
Evimiz {olcu.alan} büyüklüğünde ve kirası ayda {para.tam} tutuyor, komşular da memnun
Uçağımız {tarih.gunay} günü saat {saat:bulunma} kalkacak, bagaj hakkı ise {olcu.agirlik}
Sabah {saat.sabah:bulunma} kalktım, dışarıda hava {olcu.sicaklik} olduğu için kalın giyindim
{sira.kat} katta oturuyorum, evimin kirası {para.tam} ve bahçesi {olcu.alan}
Faturanız {tarih.gunay} tarihine kadar ödenmezse {yuzde} gecikme faizi eklenecek
Kurs ücreti {para.tam} ama peşin ödeyenlere {yuzde} indirim yapılıyor, bence kaçırmayın
Sınav {tarih.tam} tarihinde yapılacak, {kardinal.bin} aday {sehir} merkezinde ter döküyor
Çocuklar {olcu.boy} boyunda ve {olcu.agirlik} ağırlığında, doktor hepsinin sağlıklı olduğunu söyledi
Fabrikada {kardinal.bin} işçi çalışıyor, günlük üretim {olcu.agirlik} civarında
Bu sabah {saat.sabah:bulunma} ofise geldim, öğlene kadar {kardinal.orta} e-posta cevapladım
{isim} {olcu.mesafe} koştu ve süresi {aralik} dakika arasındaydı
Akşam {saat.aksam:bulunma} yemek yedik, hesap {para.tl} geldi ve bahşiş bıraktık
Ürün {olcu.agirlik} geliyor, kargo ücreti {para.kucuk} ve teslimat {tarih.gunay} günü yapılacak
Takım {skor} yenildi, taraftarın {yuzde} kadarı stadyumu terk etti
Cuma günü saat {saat:bulunma} randevum var, ücret {para.tam} ve süresi {aralik} dakika
{tarih.tam} tarihli sözleşmeye göre kira {para.tam} olarak ödenecek
Randevu {tarih.gunay} günü, bana {v2tel} numarasından ulaşabilirsiniz
Hastanın ateşi {olcu.sicaklik} çıktı, tansiyonu da normaldi, saat {saat} gibi taburcu oldu
Bu kitap {kardinal.yuz} sayfa, fiyatı {para.tl} ve {tarih.yil:bulunma} basılmış
Evden işe {olcu.mesafe} yol var, her gün {saat.sabah:ayrilma} önce çıkıyorum
Kutuda {kardinal.yuz} adet {urun} var, toplam ağırlığı {olcu.agirlik} ve değeri {para.tl}
Okulumuz {tarih.yil:ayrilma} beri açık, öğrenci sayısı {kardinal.bin} ve yıllık harç {para.tam}
Yolcu uçağı {olcu.mesafe} uçtu, {kardinal.yuz} yolcuyu taşıdı ve {saat} sularında indi
Dün gece {saat.gece:bulunma} uyudum, sabah {saat.sabah:bulunma} kalkınca hava {olcu.sicaklik} olmuştu
Nüfusun {yuzde} kadarı {sehir} şehrinde yaşıyor, kentin yüz ölçümü {olcu.alan} civarında
Mutfağa {olcu.hacim} su koydum, ocağı {olcu.sicaklik} ayarladım ve {aralik} dakika bekledim
Faturayı {tarih.gunay} günü yatırdım, tutarı {para.tl} idi ve dekontu sakladım
Sipariş {para.tam} tuttu, kargo {tarih.gunay} günü gelecek ve paket {olcu.agirlik} ağırlığında
Başvuru {tarih.gunay} günü bitiyor, ücreti {para.tam} ve gelen aday sayısı {kardinal.yuz}
Kampanya {yuzde} indirim sunuyor, fiyat {para.tl} oluyor ve stok sadece {kardinal.yuz} adet
Mağaza {saat.aralik} açık, giriş {para.tam} ve çocuklar ücretsiz
Merdivenin {sira.genel} basamağında durup, {olcu.boy} boyundaki çocuğa baktı
Ağırlığı {olcu.agirlik} olan bu çanta {para.tam} ediyor, yani oldukça pahalı
Şehirde sıcaklık {eksi.derece} ölçüldü, yollar kapandı ve {kardinal.yuz} araç mahsur kaldı
Takımın {kardinal.orta} oyuncusu sakat, sezon {tarih.gunay} günü başlıyor ve bilet {para.tam}
Dükkân sabah {saat.sabah:bulunma} açılıyor, kahve {para.kucuk} ve simit de {para.kucuk} tutuyor
Hesabıma {para.tl} yattı, bunun {yuzde} kadarını kredi borcuna ayırdım
{ondalik} puan alan öğrencilerin {yuzde} kadarı sınıfı geçti ve {kardinal.orta} kişi ödül aldı
Toplantı salonu {olcu.alan} büyüklüğünde, {kardinal.orta} kişi alıyor ve kirası {para.tam}
Bavulum {olcu.agirlik} çıktı, havayolu fazla bagaj için {para.tam} istedi, ben de ödedim
Köyümüz {olcu.mesafe} uzaklıkta ve minibüs günde {kardinal.orta} sefer yapıyor
Pazar günü saat {saat:bulunma} {sehir} yolunda olacağız, yolculuk {aralik} saat sürecek
Düğün {tarih.tam} tarihinde, davetli sayısı {kardinal.yuz} ve kişi başı maliyet {para.tam}
Depremin büyüklüğü {ondalik} olarak ölçüldü, saat {saat:bulunma} oldu ve {kardinal.yuz} bina hasar gördü
Yemek {olcu.agirlik} {urun} ile yapılıyor, {aralik} dakika pişiyor ve {kardinal.orta} kişiye yetiyor
Bilet {para.tam}, otobüs {saat:bulunma} kalkıyor ve yolculuk {olcu.mesafe} sürüyor
Maaşıma {yuzde} zam geldi, yeni maaşım {para.tam} oldu ve kira artışı da {yuzde} olmuş
Mağaza {tarih.gunay} tarihinde açılıyor, ilk gün {kardinal.bin} kişi bekleniyor ve indirim {yuzde}
{isim} {kardinal.yas} yaşında olmasına rağmen {olcu.mesafe} koştu, süresi {aralik} dakika
Sahilde sıcaklık {olcu.sicaklik} ve deniz {olcu.sicaklik} civarında, saat {saat.ogle:bulunma} gidelim
Tren {saat:bulunma} kalkıyor, bilet {para.tam} ve vagonda {kardinal.yuz} yolcu var
Kitapçıdan {kardinal.orta} kitap aldım, toplam {para.tl} ödedim ve {yuzde} indirim kazandım
Akvaryum {olcu.hacim} su alıyor, içinde {kardinal.orta} balık yaşıyor ve değeri {para.tam}
Evrak {tarih.tam} tarihli, ücreti {para.tl} ve işlem {aralik} gün sürecek
"""

_A["kucuk"] = """
Masada {v2kc} sandalye eksik
{v2kc} kişi geldi
{isim} bugün {v2kc} {nesne} aldı
Sepetine {v2kc} {urun} koydu
Sınıfta {v2kc} öğrenci eksik
Bahçede {v2kc} ağaç var
Bu hafta {v2kc} film izledim
{v2kc} gün sonra döneceğim
Çantamda {v2kc} kalem var
Raflarda {v2kc} kitap kalmış
Koridorda {v2kc} kişi bekliyordu
{sehir} yolunda {v2kc} mola verdik
Duvara {v2kc} tablo asılı
Mutfakta {v2kc} bardak kırıldı
{isim} bu ay {v2kc} kez dışarı çıktı
Servis {v2kc} durakta duruyor
Fırından {v2kc} ekmek aldım
Pazarda {v2kc} tezgâh açıktı
Arabada {v2kc} yolcu vardı
{v2kc} saat bekledik
Odada {v2kc} koltuk var
Tabakta {v2kc} zeytin kalmış
Dolapta {v2kc} {esya} duruyor
Kapıda {v2kc} {kisi} bekliyor
{isim} bana {v2kc} mektup yazdı
Sofraya {v2kc} {nesne} daha koyalım
Hafta sonu {v2kc} arkadaşım gelecek
Takımda {v2kc} yeni oyuncu var
Kitapta {v2kc} bölüm eksik
Okulda {v2kc} sınıf boş kalmış
Yarın {v2kc} toplantım var
{v2kc} bardak çay içtim
Çocuklar {v2kc} balon patlattı
Salonda {v2kc} {kisi} oturuyordu
{isim} dün {v2kc} {nesne} kırdı
Sokakta {v2kc} {v2_hayvan} gördüm
Evin önünde {v2kc} {v2_arac} duruyordu
{v2_dukkan} önünde {v2kc} kişi sıra bekliyor
Atölyede {v2kc} {v2_alet} çalışıyor
Gelecek ay {v2kc} {v2_okul} açılacak
{v2kc} haftadır yağmur yağmıyor
Yeni açılan {v2_dukkan} {v2kc} çalışanla başladı
Tatilde {v2kc} şehir gezdik
Bahçeye {v2kc} fidan diktim
{v2kc} aydır haber alamıyoruz
Mektubu {v2kc} defa okudum
Bu hafta {v2kc} gün işe gittim
Akşama {v2kc} misafir gelecek
Çarşıda {v2kc} saat dolaştık
Odama {v2kc} raf taktırdım
Fırında {v2kc} tepsi börek var
Kafede {v2kc} masa boştu
Yolda {v2kc} kez durdum
Dolaba {v2kc} askı daha lazım
Gazeteye {v2kc} haber yazdı
Kutuda {v2kc} parça eksik çıktı
Bahçıvan {v2kc} gündür gelmiyor
"""

SABLONLAR_A: dict[str, list[tuple[str, str]]] = {}
for _k, _v in _A.items():
    _satirlar = [s.strip() for s in _v.strip().splitlines() if s.strip()]
    SABLONLAR_A[_k] = [(f"v2a-{_k}-{i:03d}", s) for i, s in enumerate(_satirlar)]

ALT_BASLIKLAR = ["sifir", "tel", "kod", "aralik", "birim", "bilesik", "yeni", "uzun", "kucuk"]
# train kotası (rapor oranlarının tabanı); validation/test aynı oranlarda
KOTA_TRAIN = {"sifir": 3200, "tel": 1800, "kod": 1400, "aralik": 1300, "birim": 2000, "bilesik": 1800, "yeni": 1500,
              "uzun": 1800, "kucuk": 1200}
ALT_BASLIK_AD = {"sifir": "A1", "tel": "A2-tel", "kod": "A2-kod", "aralik": "A3", "birim": "A4", "bilesik": "A5",
                 "yeni": "A6", "uzun": "A7", "kucuk": "A8"}
KATEGORI = {"tel": "telefon", "kod": "kod", "aralik": "aralik", "birim": "olcu", "bilesik": "bilesik", "yeni": "olcu",
            "uzun": "karisik", "kucuk": "kardinal"}  # sifir: ilk varlığın kategorisi


def sablon_slotlari(metin):
    return [(ad, alt, ek) for ad, alt, ek in B.SLOT.findall(metin)]


def _katman(ab, metin):
    """Test ayrımı için katman: A4'te (birim grubu, ek), ötekilerde alt başlık."""
    if ab == "birim":
        _, alt, ek = sablon_slotlari(metin)[0]
        return (alt, ek)
    return None


def _test_secimi():
    rng = random.Random("v2a-sablon-bolunmesi")
    katmanlar = defaultdict(list)
    for ab, lst in SABLONLAR_A.items():
        for i, m in lst:
            katmanlar[(ab, _katman(ab, m))].append(i)
    secili = set()
    for key in sorted(katmanlar, key=str):
        ids = sorted(katmanlar[key])
        n = round(0.2 * len(ids)) if len(ids) >= 5 else (1 if len(ids) >= 3 else 0)
        secili.update(rng.sample(ids, n))
    return secili


TEST_SABLONLARI = _test_secimi()
SABLON_METNI = {i: m for lst in SABLONLAR_A.values() for i, m in lst}


def _dogrula_sablonlar():
    gecerli = set(V.ORNEKLEYICILER) | set(_ORNEKLEYICILER2)
    fillers = set(B.FILLERS) | set(_FILLERS2)
    from megazeka_sayi.turkce import EKLER
    for i, m in SABLON_METNI.items():
        for ad, alt, ek in sablon_slotlari(m):
            assert ad in gecerli or ad in fillers, (i, ad)
            if ek:
                assert ek in EKLER, (i, ek)
    # tüm ekli A4 şablonları A4_EKLER içinde olmalı
    for i, m in SABLONLAR_A["birim"]:
        ad, alt, ek = sablon_slotlari(m)[0]
        assert ad == "v2ol" and alt in A4_GRUP and ek in A4_EKLER, (i, m)


# ======================================================================================================
# 5. ÜRETİCİ
# ======================================================================================================

def paylastir(toplam, agirliklar):
    """En büyük kalan yöntemiyle alt başlık sayıları."""
    t = sum(agirliklar.values())
    ham = {k: toplam * w / t for k, w in agirliklar.items()}
    sayi = {k: int(v) for k, v in ham.items()}
    kalan = toplam - sum(sayi.values())
    for k in sorted(ham, key=lambda k: (-(ham[k] - sayi[k]), k))[:kalan]:
        sayi[k] += 1
    return sayi


def _kod_uyum(alt, uzunluk):
    lo, hi = _KOD_UZUNLUK_ARALIGI[alt]
    return lo <= uzunluk <= hi


def _yeni_uyum(alt, etiket):
    return etiket in YENI_GRUP.get(alt, (alt,))


class Uretici:
    def __init__(self, bolum, seed, gorulen):
        self.bolum = bolum
        self.test = bolum == "test"
        self.rng = random.Random(f"{seed}-a-{bolum}")
        self.havuz = {ab: [(i, m) for i, m in lst if (i in TEST_SABLONLARI) == self.test]
                      for ab, lst in SABLONLAR_A.items()}
        self.meta = {i: sablon_slotlari(m) for lst in self.havuz.values() for i, m in lst}
        self.g_gorulen, self.h_gorulen, self.cift = gorulen
        self.tukenen = Counter()

    def _kabul(self, ab, g, h, kalir, kats):
        if len(g.encode("utf-8")) > BAYT_SINIRI or len(h.encode("utf-8")) > BAYT_SINIRI:
            return False
        if g in self.g_gorulen or h in self.h_gorulen:
            return False
        if ab == "kucuk":
            if CTX.a8_kucuk != (g == h) or CTX.a8_kucuk != kalir:
                return False
        elif g == h:
            return False
        if ab == "uzun":
            if not 12 <= len(g.split()) <= 22 or len(set(kats)) < 2:
                return False
        return True

    def _tek(self, ab, sablon):
        sid, metin = sablon
        buyuk = self.rng.random() < 0.4
        g, h, kalir, n, kats = B.cumle_uret(metin, self.rng, buyuk, "yaziyla")
        if not self._kabul(ab, g, h, kalir, kats):
            return None
        self.g_gorulen.add(g)
        self.h_gorulen.add(h)
        kat = KATEGORI.get(ab) or kats[0]
        return {"girdi": g, "hedef": h, "kategori": kat, "sablon": sid}

    def _uygun(self, ab, kosul):
        havuz = [s for s in self.havuz[ab] if kosul(self.meta[s[0]])]
        return havuz

    def uret(self, ab, adet):
        rng = self.rng
        satirlar = []
        deneme = 0
        limit = adet * 600 + 3000
        # ön hazırlık: hücre/etiket torbaları
        torba = []
        ardisik = 0
        while len(satirlar) < adet:
            deneme += 1
            if deneme > limit:
                raise RuntimeError(f"{self.bolum}/{ab}: yeterli benzersiz satır üretilemedi ({len(satirlar)}/{adet})")
            sablon = None
            if ab == "birim":
                if not torba:
                    torba = [(u, e) for u in A4_BIRIMLER for e in A4_EKLER]
                    rng.shuffle(torba)
                u, e = torba[-1]
                uygun = self._uygun(ab, lambda m: m[0][2] == e and u in A4_GRUP[m[0][1]])
                if not uygun:
                    torba.pop()
                    continue
                CTX.birim = u
                sablon = rng.choice(uygun)
            elif ab == "kod":
                if not torba:
                    torba = [n for n, w in _KOD_TORBA_AGIRLIK.items() for _ in range(w)]
                    rng.shuffle(torba)
                uz = torba[-1]
                uygun = self._uygun(ab, lambda m: _kod_uyum(m[0][1] or None, uz))
                if not uygun:
                    torba.pop()
                    continue
                CTX.kod_uzunluk = uz
                sablon = rng.choice(uygun)
            elif ab == "yeni":
                if not torba:
                    for t in YENI_ETIKETLER:
                        torba += [t] * (3 if t == "yas" else 6)
                    rng.shuffle(torba)
                t = torba[-1]
                uygun = self._uygun(ab, lambda m: _yeni_uyum(m[0][1] or "kisa", t))
                if not uygun:
                    torba.pop()
                    continue
                CTX.birim = t
                sablon = rng.choice(uygun)
            elif ab == "kucuk":
                CTX.a8_kucuk = len(satirlar) % 2 == 0
                sablon = rng.choice(self.havuz[ab])
            else:
                sablon = rng.choice(self.havuz[ab])
            satir = self._tek(ab, sablon)
            if satir is None:
                if torba:
                    ardisik += 1
                    if ardisik > 150:  # bu hücre/etiket için yeni benzersiz satır çıkmıyor: vazgeç
                        torba.pop()
                        ardisik = 0
                        self.tukenen[ab] += 1
                continue
            ardisik = 0
            if ab in ("birim", "kod", "yeni") and torba:
                torba.pop()
            satirlar.append(satir)
        CTX.birim = None
        CTX.kod_uzunluk = None
        return satirlar


def uret_bolumler(train, validation, test, seed):
    """{'train': [...], 'validation': [...], 'test': [...]} döndürür. Deterministik."""
    _dogrula_sablonlar_kayitli()
    sonuc = {}
    gorulen = (set(), set(), set())  # girdi, hedef, (kullanılmıyor)
    with kayitli():
        CTX.sifirla()
        for bolum, toplam in (("test", test), ("validation", validation), ("train", train)):
            u = Uretici(bolum, seed, gorulen)
            satirlar = []
            CTX.tip_say = Counter()
            for ab, adet in paylastir(toplam, KOTA_TRAIN).items():
                satirlar += u.uret(ab, adet)
            u.rng.shuffle(satirlar)
            sonuc[bolum] = satirlar
        CTX.sifirla()
    return sonuc


def _dogrula_sablonlar_kayitli():
    with kayitli():
        _dogrula_sablonlar()


# ======================================================================================================
# 6. ÖLÇÜM / RAPOR
# ======================================================================================================
_SAYI_RE = re.compile(r"(?<![\d.,])\d{1,3}(?:\.\d{3})+")
_BIRIM_EK_RE = re.compile(r"(GB|MB|kW|V|L|mL|m²|°C)'([a-zçğıöşü]+)")
_KANONIK = {"GB": "gigabayt", "MB": "megabayt", "kW": "kilovat", "V": "volt", "L": "litre", "mL": "mililitre",
            "m²": "metrekare", "°C": "derece"}


def _oku(yol):
    return [json.loads(s) for s in Path(yol).read_text(encoding="utf-8").splitlines() if s.strip()]


def _alt_baslik(sablon):
    return sablon.split("-")[1]


def _ilk_sozcuk(g):
    t = _TOKEN.findall(lower_tr(g))
    return t[0] if t else ""


def olc(satirlar, test_sablonlar_disi=None):
    """Train dosyası için çeşitlilik ölçümleri; sözlük döndürür."""
    n = len(satirlar)
    m = {"satir": n}
    sab = Counter(r["sablon"] for r in satirlar)
    m["sablon_sayisi"] = len(sab)
    m["sablon_en_cok"] = (sab.most_common(1)[0][0], round(sab.most_common(1)[0][1] / n, 4))
    ab_sab = defaultdict(set)
    for r in satirlar:
        ab_sab[_alt_baslik(r["sablon"])].add(r["sablon"])
    m["alt_baslik_sablon"] = {ALT_BASLIK_AD[k]: len(ab_sab[k]) for k in ALT_BASLIKLAR}
    isoz = Counter(_ilk_sozcuk(r["girdi"]) for r in satirlar)
    m["ilk_sozcuk_en_cok"] = [(w, round(c / n, 4)) for w, c in isoz.most_common(3)]
    m["alt_baslik_satir"] = {ALT_BASLIK_AD[k]: sum(1 for r in satirlar if _alt_baslik(r["sablon"]) == k)
                             for k in ALT_BASLIKLAR}
    m["kategori"] = dict(sorted(Counter(r["kategori"] for r in satirlar).items()))
    # A1
    a1 = [r for r in satirlar if _alt_baslik(r["sablon"]) == "sifir"]
    tipler = Counter()
    ic_sifirsiz = 0
    for r in a1:
        var = set()
        for s in _SAYI_RE.findall(r["hedef"]):
            for g in s.split(".")[1:]:
                var.add(grup_tipi(int(g)))
        if not var & set(ZTIP):
            ic_sifirsiz += 1
        for t in var & set(ZTIP):
            tipler[t] += 1
    m["a1_tip_satir"] = {"000": tipler["Z"], "00x": tipler["A"], "0x0": tipler["B"], "0xx": tipler["C"]}
    m["a1_ic_sifirsiz_satir"] = ic_sifirsiz
    # A2
    tel = [r for r in satirlar if _alt_baslik(r["sablon"]) == "tel"]
    m["a2_tel_belirsiz"] = sum(1 for r in tel if telefon_satiri_belirsiz(r["girdi"], r["hedef"]))
    m["a2_tel_arti90"] = sum(1 for r in tel if "+90" in r["hedef"])
    m["a2_kod_uzunluk"] = dict(sorted(Counter(_kod_uz(r) for r in satirlar if _alt_baslik(r["sablon"]) == "kod").items()))
    # A4
    hucre = Counter()
    for r in satirlar:
        if _alt_baslik(r["sablon"]) != "birim":
            continue
        mm = _BIRIM_EK_RE.search(r["hedef"])
        if not mm:
            continue
        for e in A4_EKLER:
            if written_suffix(_KANONIK[mm.group(1)], e) == mm.group(2):
                hucre[(mm.group(1), e)] += 1
                break
    m["a4_hucre_en_az"] = min(hucre.values()) if len(hucre) == len(A4_BIRIMLER) * len(A4_EKLER) else 0
    m["a4_hucre_sayisi"] = len(hucre)
    # A7
    uz = [r for r in satirlar if _alt_baslik(r["sablon"]) == "uzun"]
    sw = [len(r["girdi"].split()) for r in uz]
    m["a7_sozcuk_aralik"] = (min(sw), max(sw)) if sw else None
    # A8
    ku = [r for r in satirlar if _alt_baslik(r["sablon"]) == "kucuk"]
    m["a8_girdi_esit_hedef"] = sum(1 for r in ku if r["girdi"] == r["hedef"])
    m["bayt_en_cok"] = max(max(len(r["girdi"].encode()), len(r["hedef"].encode())) for r in satirlar)
    m["buyuk_harf_orani"] = round(sum(1 for r in satirlar if r["girdi"][:1].isupper()) / n, 3)
    return m


def _kod_uz(r):
    ds = re.findall(r"(?<![\d.,])\d{3,11}(?!\d)(?!,\d)(?!\.\d)", r["hedef"])
    return len(ds[0]) if ds else 0


def eski_telefon_olc(yol):
    """Mevcut train dosyasında belirsiz telefon satırı sayısı (dosya değiştirilmez)."""
    sayim = Counter()
    for r in _oku(yol):
        if r["kategori"] in ("telefon", "karisik"):
            tel = bool(_hedef_telefonlari(r["hedef"]))
            if r["kategori"] == "telefon":
                sayim["telefon"] += 1
                if telefon_satiri_belirsiz(r["girdi"], r["hedef"]):
                    sayim["telefon_belirsiz"] += 1
            elif tel:
                sayim["karisik_telefonlu"] += 1
                if telefon_satiri_belirsiz(r["girdi"], r["hedef"]):
                    sayim["karisik_belirsiz"] += 1
    return dict(sayim)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v2")
    ap.add_argument("--seed", type=int, default=2201)
    ap.add_argument("--train", type=int, default=16000)
    ap.add_argument("--validation", type=int, default=400)
    ap.add_argument("--test", type=int, default=500)
    ap.add_argument("--eski-telefon", default=str(KOK / "data" / "train.jsonl"),
                    help="belirsiz telefon satırı ölçümü için mevcut train dosyası ('' = atla)")
    ap.add_argument("--rapor", action="store_true", help="üretim sonrası ölçümleri yazdır")
    a = ap.parse_args(argv)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sonuc = uret_bolumler(a.train, a.validation, a.test, a.seed)
    for bolum, satirlar in sonuc.items():
        with open(out / f"a-{bolum}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in satirlar:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"adet": {k: len(v) for k, v in sonuc.items()}}, ensure_ascii=False))
    if a.rapor:
        print(json.dumps(olc(sonuc["train"]), ensure_ascii=False, indent=1))
        if a.eski_telefon and Path(a.eski_telefon).exists():
            print("eski train telefon:", json.dumps(eski_telefon_olc(a.eski_telefon), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
