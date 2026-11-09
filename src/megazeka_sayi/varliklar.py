"""Varlık örnekleyicileri: önce yazılı biçim (hedef), sonra deterministik sözlü biçim (girdi).

Her `kur_*` işlevi açık değerlerle çalışır (testlerde kullanılır); her `ornekle_*` işlevi
gerçekçi dağılımlardan değer seçip `kur_*`u çağırır. Hepsi `Varlik(yazili, sozlu, kategori)` döndürür.
"""
from __future__ import annotations

import calendar
import random
from dataclasses import dataclass

from . import sayilar as S
from .turkce import ilk_harfi_buyut, inflect, lower_tr, written_suffix


@dataclass(frozen=True)
class Varlik:
    yazili: str
    sozlu: str
    kategori: str
    kalir: bool = False  # True: yazılı == sözlü (küçük sayı politikası)


AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

# anahtar: (yazılı kısaltma, kanonik okunuşun son sözcüğü, sözlü seçenekler, kip)
# kip "apostrof": ek kesmeyle kısaltmaya; "sozcuk": birim sözcük kalır, ek sözcüğe bitişir.
BIRIMLER = {
    "kg": ("kg", "kilogram", [["kilo"], ["kilogram"]], "apostrof"),
    "g": ("g", "gram", [["gram"]], "apostrof"),
    "km": ("km", "kilometre", [["kilometre"]], "apostrof"),
    "m": ("m", "metre", [["metre"]], "apostrof"),
    "cm": ("cm", "santimetre", [["santim"], ["santimetre"]], "apostrof"),
    "mm": ("mm", "milimetre", [["milimetre"]], "apostrof"),
    "L": ("L", "litre", [["litre"]], "apostrof"),
    "mL": ("mL", "mililitre", [["mililitre"]], "apostrof"),
    "m2": ("m²", "metrekare", [["metrekare"]], "apostrof"),
    "GB": ("GB", "gigabayt", [["gigabayt"]], "apostrof"),
    "MB": ("MB", "megabayt", [["megabayt"]], "apostrof"),
    "TB": ("TB", "terabayt", [["terabayt"]], "apostrof"),
    "kW": ("kW", "kilovat", [["kilovat"]], "apostrof"),
    "W": ("W", "vat", [["vat"]], "apostrof"),
    "V": ("V", "volt", [["volt"]], "apostrof"),
    # kanonik okunuş "santigrat derece": yazılı ek "derece"den gelir (°C'de)
    "C": ("°C", "derece", [["derece", "santigrat"]], "apostrof"),
    "derece": ("derece", "derece", [["derece"]], "sozcuk"),
    "TL": ("TL", "tele", [["lira"]], "apostrof"),
    "dolar": ("dolar", "dolar", [["dolar"]], "sozcuk"),
}


def _birlestir(sozcukler, yazili, kanonik_son, ek, kip="apostrof"):
    """Ek varsa sözlü son sözcüğe, yazılıda kanonik okunuşa göre uygular."""
    if not ek:
        return " ".join(sozcukler), yazili
    son, _ = inflect(sozcukler[-1], ek)
    sozlu = " ".join(sozcukler[:-1] + [son])
    if kip == "apostrof":
        return sozlu, yazili + "'" + written_suffix(kanonik_son, ek)
    assert yazili.endswith(sozcukler[-1]), (yazili, sozcukler)
    return sozlu, yazili[: -len(sozcukler[-1])] + son


def _sayili_birim(sayi_k, sayi_yaz, birim, soz_idx, ek, kategori):
    yaz, kan, secenekler, kip = BIRIMLER[birim]
    if kip == "sozcuk" and ek is None:
        pass
    soz = secenekler[soz_idx % len(secenekler)]
    sozcukler = list(sayi_k) + soz
    yazili = f"{sayi_yaz} {yaz}"
    if kip == "sozcuk":
        # yazılı birim sözcüğü sözlü son sözcükle aynı olmalı
        s, y = _birlestir(sozcukler, yazili, kan, ek, "sozcuk")
    else:
        s, y = _birlestir(sozcukler, yazili, kan, ek, "apostrof")
    return Varlik(y, s, kategori)


def _num(tam, kesir):
    return S.yaz_sayi(tam) + ("," + kesir if kesir else "")


def _num_kelimeleri(tam, kesir, bucuk=False, rakam_rakam=False):
    if kesir:
        return S.ondalik_kelimeleri(tam, kesir, bucuk, rakam_rakam)
    return S.sayi_kelimeleri(tam)


def _kanonik_son(tam, kesir):
    return _num_kelimeleri(tam, kesir)[-1]


# ---- Ekli sayılarda son sözcük dengesi (ünlü uyumu çeşitliliği) -----------------------------------------
# Her (son sözcük x ek türü) bileşimi eşit sıklıkta görünsün diye örnekleyici en az kullanılan son sözcüğü seçer.
_SON_TAM = ["bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz", "kırk", "elli",
            "altmış", "yetmiş", "seksen", "doksan", "yüz", "bin"]
_SON_KESIR = {"sıfır": "0", "bir": "1", "iki": "2", "üç": "3", "dört": "4", "beş": "5", "altı": "6", "yedi": "7",
              "sekiz": "8", "dokuz": "9", "on": "10", "yirmi": "20", "otuz": "30", "kırk": "40", "elli": "50",
              "altmış": "60", "yetmiş": "70", "seksen": "80", "doksan": "90"}
_RAKAM_SOZ = {"bir": 1, "iki": 2, "üç": 3, "dört": 4, "beş": 5, "altı": 6, "yedi": 7, "sekiz": 8, "dokuz": 9}
_ONLAR_SOZ = {"on": 10, "yirmi": 20, "otuz": 30, "kırk": 40, "elli": 50, "altmış": 60, "yetmiş": 70, "seksen": 80,
              "doksan": 90}


def _dengeli_son(rng, adaylar, ek, grup):
    """(grup, ek) başına sayaçla en az kullanılan adayı seçer; eşitlikte rastgele."""
    sayac = rng.__dict__.setdefault("_ekli_sayac", {})
    w = min(adaylar, key=lambda a: (sayac.get((grup, ek, a), 0), rng.random()))
    sayac[(grup, ek, w)] = sayac.get((grup, ek, w), 0) + 1
    return w


def _tam_sayi_son(rng, son, azami=None):
    if son in _RAKAM_SOZ:
        d = _RAKAM_SOZ[son]
        r = rng.random()
        n = 10 * rng.randint(1, 9) + d if r < 0.75 else 100 * rng.randint(1, 9) + 10 * rng.randint(0, 9) + d
        if azami and n > azami:
            n = 10 * rng.randint(1, azami // 10 - 1) + d
        return n
    if son in _ONLAR_SOZ:
        t = _ONLAR_SOZ[son]
        if azami or rng.random() < 0.6:
            return t
        return 100 * rng.randint(1, 9) + t
    if son == "yüz":
        return 100 if azami else rng.choice([100, 200, 300, 400, 500, 600, 700, 800, 900])
    return rng.choice([1000, 2000, 3000, 4000, 5000, 6000, 8000, 10000, 20000, 25000, 50000])  # bin


# ======================= PARA =======================

def kur_para(lira=None, kurus=None, birim="TL", ek=None, ad="lira", virgullu=False):
    if birim in ("dolar", "avro", "euro", "sterlin"):
        sz = S.sayi_kelimeleri(lira) + [birim]
        return _para_sozcuk(sz, f"{S.yaz_sayi(lira)} {birim}", ek)
    if lira is None:
        sz = S.sayi_kelimeleri(kurus) + ["kuruş"]
        return _para_sozcuk(sz, f"{kurus} kuruş", ek)
    ad_k = ["Türk", "lirası"] if ad == "Türk lirası" else ["lira"]
    if ad_k != ["lira"]:
        ek = None
    if kurus is None:
        sz = S.sayi_kelimeleri(lira) + ad_k
        yaz = f"{S.yaz_sayi(lira)} TL"
    elif virgullu:
        sz = S.sayi_kelimeleri(lira) + ["virgül"] + S.kesir_kelimeleri(f"{kurus:02d}") + ad_k
        yaz = f"{S.yaz_sayi(lira)},{kurus:02d} TL"
    else:
        sz = S.sayi_kelimeleri(lira) + ad_k + S.sayi_kelimeleri(kurus) + ["kuruş"]
        yaz = f"{S.yaz_sayi(lira)},{kurus:02d} TL"
    s, y = _birlestir(sz, yaz, "tele", ek, "apostrof")
    return Varlik(y, s, "para")


def _para_sozcuk(sz, yaz, ek):
    s, y = _birlestir(sz, yaz, sz[-1], ek, "sozcuk")
    return Varlik(y, s, "para")


def _lira(rng, kucuk=False):
    if kucuk:
        return rng.randint(1, 99)
    r = rng.random()
    if r < 0.18:
        return rng.randint(2, 99)
    if r < 0.42:
        return rng.choice([100, 120, 150, 200, 250, 300, 350, 400, 450, 500, 600, 750, 800, 900]) if rng.random() < 0.6 else rng.randint(100, 999)
    if r < 0.72:
        return rng.choice([1000, 1250, 1500, 2000, 2500, 3000, 3500, 4500, 5000, 7500, 8000, 9000]) if rng.random() < 0.6 else rng.randint(1000, 9999)
    if r < 0.9:
        return rng.choice([10000, 12500, 15000, 18500, 20000, 25000, 35000, 45000, 50000]) if rng.random() < 0.6 else rng.randint(10000, 99999)
    return rng.randint(100, 999) * 1000 if rng.random() < 0.7 else rng.randint(100000, 999999)


_KURUS = [50, 90, 99, 75, 25, 95, 5, 10, 45, 80, 60, 20, 40, 30, 15, 85, 55, 70]
_KURUS_W = [20, 14, 14, 8, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 1, 1]


def ornekle_para(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or rng.choices(["tl", "tam", "kucuk", "kurus", "doviz"], [40, 20, 18, 6, 16])[0]
    if alt == "doviz":
        birim = rng.choices(["dolar", "avro", "euro", "sterlin"], [48, 25, 12, 15])[0]
        n = rng.choice([5, 10, 15, 20, 25, 50, 100, 150, 200, 250, 500, 1000, 1500, 2000, 3000]) if rng.random() < 0.8 else rng.randint(2, 4999)
        return kur_para(lira=n, birim=birim, ek=ek)
    if alt == "kurus":
        return kur_para(kurus=rng.choice([5, 10, 15, 20, 25, 30, 40, 50, 75, 90]) if rng.random() < 0.8 else rng.randint(1, 99), ek=ek)
    lira = _lira(rng, kucuk=(alt == "kucuk"))
    if alt == "tl":
        kuruslu = rng.random() < 0.55
    elif alt == "kucuk":
        kuruslu = rng.random() < 0.7
    else:
        kuruslu = False
    kurus = rng.choices(_KURUS, _KURUS_W)[0] if kuruslu else None
    ad = "Türk lirası" if (ek is None and rng.random() < 0.2) else "lira"
    virgullu = kurus is not None and ad == "lira" and rng.random() < 0.07
    return kur_para(lira=lira, kurus=kurus, ek=ek, ad=ad, virgullu=virgullu)


# ======================= YÜZDE =======================

def kur_yuzde(tam, kesir="", bucuk=False, rakam_rakam=False, ek=None):
    yaz = "%" + _num(tam, kesir)
    sz = ["yüzde"] + _num_kelimeleri(tam, kesir, bucuk, rakam_rakam)
    s, y = _birlestir(sz, yaz, _kanonik_son(tam, kesir), ek, "apostrof")
    return Varlik(y, s, "yuzde")


_YUZDE_INT = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 20, 25, 30, 35, 40, 45, 50, 60, 70, 75, 80, 90, 95, 99, 100]


def ornekle_yuzde(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt == "ekli":
        son = _dengeli_son(rng, _SON_TAM[:-1], ek, "yuzde")
        return kur_yuzde(_tam_sayi_son(rng, son, azami=100), ek=ek)
    if rng.random() < 0.68:
        tam = rng.choice(_YUZDE_INT) if rng.random() < 0.75 else rng.randint(1, 100)
        if ek and tam == 1:
            tam = 2
        return kur_yuzde(tam, ek=ek)
    tam = rng.randint(0, 40) if rng.random() < 0.85 else rng.randint(41, 150)
    kesir = rng.choices(["5", "25", "75", "2", "3", "1", "8", "05", "15"], [48, 8, 6, 8, 8, 6, 6, 5, 5])[0]
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.55
    rr = len(kesir) == 2 and kesir[0] != "0" and rng.random() < 0.12
    return kur_yuzde(tam, kesir, bucuk, rr, ek=ek)


# ======================= ÖLÇÜ =======================

def kur_olcu(tam, kesir="", birim="kg", soz_idx=0, bucuk=False, rakam_rakam=False, ek=None):
    return _sayili_birim(_num_kelimeleri(tam, kesir, bucuk, rakam_rakam), _num(tam, kesir), birim, soz_idx, ek, "olcu")


def _ondalikli(rng, lo, hi, p, adim=1):
    tam = rng.randrange(lo, hi + 1, adim)
    kesir = ""
    if rng.random() < p:
        kesir = rng.choices(["5", "25", "75", "2", "3", "4", "6", "8", "1", "05"], [40, 8, 8, 6, 6, 4, 4, 4, 4, 2])[0]
        if tam == 0 and kesir.startswith("0"):
            kesir = "5"
    return tam, kesir


def _olcu_degeri(rng, b):
    if b == "kg":
        return _ondalikli(rng, 1, 80, 0.3)
    if b == "g":
        return rng.randrange(50, 1000, 25), ""
    if b == "km":
        return _ondalikli(rng, 1, 800, 0.15)
    if b == "m":
        return _ondalikli(rng, 1, 500, 0.12)
    if b == "cm":
        return _ondalikli(rng, 5, 210, 0.08)
    if b == "mm":
        return _ondalikli(rng, 1, 100, 0.12)
    if b == "L":
        return _ondalikli(rng, 1, 60, 0.3)
    if b == "mL":
        return rng.randrange(50, 1001, 25), ""
    if b == "m2":
        return _ondalikli(rng, 20, 500, 0.06)
    if b == "GB":
        return (rng.choice([1, 2, 4, 8, 16, 32, 64, 128, 256, 512]), "") if rng.random() < 0.75 else _ondalikli(rng, 1, 100, 0.2)
    if b == "MB":
        return _ondalikli(rng, 5, 2000, 0.1)
    if b == "TB":
        return _ondalikli(rng, 1, 8, 0.25)
    if b == "kW":
        return _ondalikli(rng, 1, 300, 0.1)
    if b == "W":
        return rng.randrange(5, 2001, 5), ""
    if b == "V":
        return (rng.choice([3, 5, 9, 12, 24, 110, 220, 230, 380]), "") if rng.random() < 0.7 else _ondalikli(rng, 1, 40, 0.5)
    if b in ("C", "derece"):
        return _ondalikli(rng, 0, 45, 0.12)
    raise KeyError(b)


_OLCU_GRUP = {
    "agirlik": (["kg", "g"], [70, 30]),
    "uzunluk": (["km", "m", "cm", "mm"], [35, 25, 30, 10]),
    "mesafe": (["km", "m"], [70, 30]),
    "boy": (["cm"], [1]),
    "hacim": (["L", "mL"], [70, 30]),
    "alan": (["m2"], [1]),
    "veri": (["GB", "MB", "TB"], [45, 40, 15]),
    "guc": (["kW", "W", "V"], [30, 40, 30]),
    "sicaklik": (["C", "derece"], [55, 45]),
}


def _olcu_birimi(rng, alt):
    alt = alt or rng.choice(sorted(_OLCU_GRUP))
    b, w = _OLCU_GRUP[alt]
    return rng.choices(b, w)[0]


def ornekle_olcu(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    b = _olcu_birimi(rng, alt)
    if alt == "boy":
        tam, kesir = rng.randint(50, 195), ""
    else:
        tam, kesir = _olcu_degeri(rng, b)
    if tam == 0 and not kesir:
        tam = rng.randint(1, 30)
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.6
    rr = len(kesir) == 2 and kesir[0] != "0" and rng.random() < 0.1
    return kur_olcu(tam, kesir, b, rng.randrange(2), bucuk, rr, ek)


# ======================= SAAT =======================

def _dk_kelimeleri(m):
    if m == 0:
        return ["sıfır", "sıfır"]
    if m < 10:
        return ["sıfır", S.BIRLER[m]]
    return S.sayi_kelimeleri(m)


def kur_saat(saat, dakika=0, bucuk=False, bicim="dk", ek=None):
    saat_k = S.sayi_kelimeleri(saat)
    if bicim == "tam":
        s, y = _birlestir(saat_k, str(saat), saat_k[-1], ek)
        return Varlik(y, s, "saat")
    kan = saat_k + _dk_kelimeleri(dakika)
    sz = saat_k + ["buçuk"] if (bucuk and dakika == 30) else kan
    s, y = _birlestir(sz, f"{saat}.{dakika:02d}", kan[-1], ek)
    return Varlik(y, s, "saat")


def _saat_dk(rng, bicim):
    h = rng.choices(range(1, 24), [1, 1, 1, 2, 3, 4, 6, 8, 9, 9, 8, 8, 9, 9, 9, 8, 8, 9, 8, 6, 4, 2, 1])[0]
    if bicim == "tam":
        return h, 0
    m = rng.choices([30, 15, 45, 5, 10, 20, 25, 35, 40, 50, 55, 0], [25, 12, 12, 5, 7, 6, 4, 4, 4, 4, 3, 4])[0]
    return h, m


# sabah/öğlen/akşam/gece bağlamı: konuşulduğu gibi 12 saatlik saat
_GUNUN_VAKTI = {
    "sabah": [5, 6, 7, 8, 9, 10, 11],
    "ogle": [12, 1, 2],
    "aksam": [4, 5, 6, 7, 8, 9, 10],
    "gece": [10, 11, 12, 1, 2, 3, 4],
}


def ornekle_saat(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt == "aralik":
        h1, m1 = _saat_dk(rng, "tam" if rng.random() < 0.7 else "dk")
        h2 = min(23, h1 + rng.randint(1, 9))
        m2 = 0 if m1 == 0 else rng.choice([0, 30])
        a = kur_saat(h1, m1, rng.random() < 0.5, "tam" if m1 == 0 else "dk", "ayrilma")
        b = kur_saat(h2, m2, rng.random() < 0.5, "tam" if m2 == 0 else "dk", "yonelme")
        return Varlik(a.yazili + " " + b.yazili, a.sozlu + " " + b.sozlu, "saat")
    if alt in _GUNUN_VAKTI:
        h = rng.choice(_GUNUN_VAKTI[alt])
        m = rng.choices([0, 30, 15, 45, 10, 20, 40], [38, 34, 8, 8, 4, 4, 4])[0]
        return kur_saat(h, m, m == 30 and rng.random() < 0.55, "tam" if m == 0 else "dk", ek)
    bicim = alt if alt in ("tam", "dk") else rng.choices(["tam", "dk"], [40, 60])[0]
    h, m = _saat_dk(rng, bicim)
    if bicim == "dk" and m == 0 and rng.random() < 0.7:
        m = 30
    bucuk = m == 30 and h <= 12 and rng.random() < 0.55
    return kur_saat(h, m, bucuk, bicim, ek)


# ======================= TARİH =======================

def kur_tarih(gun, ay, yil=None, ek=None, ay_buyuk=False):
    ay_ad = AYLAR[ay - 1]
    gun_k = S.sayi_kelimeleri(gun)
    if yil is None:
        yaz = f"{gun} {ay_ad}"
        if ek:
            son, _ = inflect(lower_tr(ay_ad), ek)
            if ay_buyuk:
                son = ilk_harfi_buyut(son)
            return Varlik(yaz + "'" + written_suffix(lower_tr(ay_ad), ek), " ".join(gun_k + [son]), "tarih")
        return Varlik(yaz, " ".join(gun_k + [ay_ad if ay_buyuk else lower_tr(ay_ad)]), "tarih")
    yil_k = S.sayi_kelimeleri(yil)
    sz = gun_k + [ay_ad if ay_buyuk else lower_tr(ay_ad)] + yil_k
    s, y = _birlestir(sz, f"{gun} {ay_ad} {yil}", yil_k[-1], ek)
    return Varlik(y, s, "tarih")


def kur_yil(yil, ek=None):
    yk = S.sayi_kelimeleri(yil)
    s, y = _birlestir(yk, str(yil), yk[-1], ek)
    return Varlik(y, s, "tarih")


def kur_onyil(yil, ek="cogul", uzun=False):
    """yil: 1920, 1930, ... 1990. 'doksanlarda' -> 1990'larda."""
    d = (yil % 100) // 10
    kelime = S.ONLAR[d]
    on = S.sayi_kelimeleri(yil - yil % 100) if uzun else []
    son, _ = inflect(kelime, ek)
    return Varlik(f"{yil}'" + written_suffix(kelime, ek), " ".join(on + [son]), "tarih")


def _yil(rng):
    if rng.random() < 0.7:
        return rng.randint(1970, 2030)
    return rng.randint(1900, 2035)


def _gun_ay_yil(rng):
    yil = _yil(rng)
    ay = rng.randint(1, 12)
    gun = rng.randint(1, calendar.monthrange(yil, ay)[1])
    return gun, ay, yil


def ornekle_tarih(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or rng.choices(["tam", "gunay", "yil", "onyil"], [40, 22, 28, 10])[0]
    ay_buyuk = buyuk_harf and rng.random() < 0.5
    if alt == "yil":
        return kur_yil(_yil(rng), ek)
    if alt == "onyil":
        return kur_onyil(rng.choice(range(1920, 2000, 10)), ek or "cogul", rng.random() < 0.2)
    gun, ay, yil = _gun_ay_yil(rng)
    if alt == "gunay":
        if gun == 1:  # "bir aralik" belirsiz
            gun = rng.randint(2, 28)
        return kur_tarih(gun, ay, None, ek, ay_buyuk)
    return kur_tarih(gun, ay, yil, ek, ay_buyuk)


# ======================= SIRA =======================

def kur_sira(n):
    return Varlik(f"{n}.", S.sira_oku(n), "sira")


_SIRA_ARALIK = {"kat": (1, 25), "sinif": (1, 12), "yuzyil": (5, 21), "madde": (1, 150), "genel": (1, 60)}


def ornekle_sira(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    lo, hi = _SIRA_ARALIK[alt or "genel"]
    n = rng.randint(lo, hi)
    if rng.random() < 0.15 and hi >= 100:
        n = rng.choice([100, 101, 110, 120])
    return kur_sira(n)


# ======================= TELEFON / KOD =======================

def kur_telefon(rakamlar, modlar=("sayi",) * 4, arti90=False, ek=None):
    sz = S.telefon_kelimeleri(rakamlar, modlar, arti90)
    kan = S.telefon_kelimeleri(rakamlar, ("sayi",) * 4, arti90)[-1]
    s, y = _birlestir(sz, S.yaz_telefon(rakamlar, arti90), kan, ek)
    return Varlik(y, s, "telefon")


def _telefon_rakamlari(rng):
    if rng.random() < 0.75:
        alan = "05" + rng.choice("345") + rng.choice("0123456789")
    else:
        alan = "0" + rng.choice(["212", "216", "312", "232", "224", "242", "322", "352"])
    return alan + "".join(rng.choice("0123456789") for _ in range(7))


def ornekle_telefon(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    r = _telefon_rakamlari(rng)
    modlar = tuple(rng.choices(["sayi", "rakam"], [75, 25])[0] for _ in range(4))
    if rng.random() < 0.35:
        modlar = ("sayi", "sayi", "sayi", "sayi")
    if rng.random() < 0.1:
        modlar = ("rakam",) * 4
    return kur_telefon(r, modlar, rng.random() < 0.08, ek)


def kur_kod(rakamlar):
    return Varlik(rakamlar, S.rakam_rakam_oku(rakamlar), "kod")


def ornekle_kod(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    n = {"posta": 5, "uzun": rng.randint(8, 10), "kisa": 3}.get(alt) or rng.choices([4, 5, 6, 3, 7, 8], [40, 15, 25, 8, 6, 6])[0]
    r = "".join(rng.choice("0123456789") for _ in range(n))
    if alt == "posta":
        r = rng.choice("0123456789"[1:]) + r[1:]
    return kur_kod(r)


# ======================= SKOR / ARALIK =======================

def kur_skor(a, b, ek=None):
    sz = S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b)
    s, y = _birlestir(sz, f"{a}-{b}", sz[-1], ek)
    return Varlik(y, s, "skor")


def ornekle_skor(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt == "basket":
        a = rng.randint(60, 115)
        b = a + rng.choice([-1, 1]) * rng.randint(1, 20)
        return kur_skor(a, b)
    a = rng.choices(range(6), [20, 28, 24, 14, 9, 5])[0]
    b = a if alt == "berabere" else rng.choices(range(6), [22, 28, 22, 14, 9, 5])[0]
    if alt == "galip" and a <= b:
        a, b = b + 1, a
    if ek in ("lik", "vasita", "ayrilma", "yonelme"):
        if a == b and alt != "berabere":
            a += 1
    return kur_skor(a, b, ek)


def kur_aralik(a, b, birim=None, soz_idx=0, ek=None):
    sk = S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b)
    yaz = f"{a}-{b}"
    if birim is None:
        return Varlik(yaz, " ".join(sk), "aralik")
    v = _sayili_birim(sk, yaz, birim, soz_idx, ek, "aralik")
    return v


def _aralik_cifti(rng):
    while True:
        r = rng.random()
        if r < 0.55:
            a = rng.randint(2, 9)
            b = a + rng.choice([1, 1, 1, 2, 3])
            if b > 10:
                continue
        elif r < 0.8:
            a = rng.choice([10, 15, 20, 25, 30, 40, 45, 50, 60, 5])
            b = a + rng.choice([5, 5, 10, 10, 15])
        elif r < 0.93:
            a = rng.choice([100, 150, 200, 250, 300, 400, 500])
            b = a + rng.choice([50, 100, 100, 200])
        else:
            a = rng.choice([2, 3, 4, 5, 6, 8])
            b = rng.choice([10, 12, 15, 20])
        if "bir" not in S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b):
            return a, b


def ornekle_aralik(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    a, b = _aralik_cifti(rng)
    if alt is None:
        return kur_aralik(a, b)
    if alt == "agirlik":
        return kur_aralik(a, b, rng.choice(["kg", "g"]) if a >= 50 else "kg", rng.randrange(2), ek)
    if alt == "sicaklik":
        a, b = rng.choice([(15, 20), (20, 25), (25, 30), (30, 35), (10, 15), (5, 10)]) if rng.random() < 0.8 else (a, b)
        return kur_aralik(a, b, "derece", 0, ek)
    if alt == "mesafe":
        return kur_aralik(a, b, "km", 0, ek)
    if alt == "para":
        a, b = rng.choice([(50, 100), (100, 150), (200, 300), (500, 750), (1000, 1500), (20, 30), (10, 15)])
        return kur_aralik(a, b, "TL", 0, ek)
    raise KeyError(alt)


# ======================= ONDALIK / KARDİNAL / BÜYÜK / EKSİ =======================

def kur_ondalik(tam, kesir, bucuk=False, rakam_rakam=False, ek=None):
    sz = S.ondalik_kelimeleri(tam, kesir, bucuk, rakam_rakam)
    s, y = _birlestir(sz, _num(tam, kesir), _kanonik_son(tam, kesir), ek)
    return Varlik(y, s, "ondalik")


def ornekle_ondalik(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt == "ekli":
        son = _dengeli_son(rng, list(_SON_KESIR), ek, "ondalik")
        kesir = _SON_KESIR[son]
        tam = rng.randint(1, 45) if rng.random() < 0.8 else rng.choice([0, 100, 120, 250])
        if kesir == "0":
            tam = rng.randint(1, 45)
        bucuk = kesir == "5" and tam > 0 and rng.random() < 0.4
        return kur_ondalik(tam, kesir, bucuk, False, ek)
    r = rng.random()
    if alt == "buyuk" or r < 0.04:
        tam = rng.choice([12, 45, 120, 250, 1250, 3400, 15000, 999])
    elif r < 0.3:
        tam = 0
    else:
        tam = rng.randint(1, 30)
    kesir = rng.choices(["5", "25", "75", "2", "3", "4", "6", "7", "8", "9", "1", "05", "14", "35", "125", "008", "45", "65"],
                        [36, 5, 5, 6, 6, 4, 4, 3, 4, 3, 4, 3, 4, 3, 2, 1, 4, 3])[0]
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.55
    rr = len(kesir) >= 2 and kesir[0] != "0" and rng.random() < 0.12
    return kur_ondalik(tam, kesir, bucuk, rr, ek)


def kur_kardinal(n, politika="yaziyla", ek=None):
    sk = S.sayi_kelimeleri(n)
    if politika == "yaziyla" and n < 10:
        assert ek is None
        sz = " ".join(sk)
        return Varlik(sz, sz, "kardinal", kalir=True)
    s, y = _birlestir(sk, S.yaz_sayi(n), sk[-1], ek)
    return Varlik(y, s, "kardinal")


_ORTA_YUV = [10, 12, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90]


def ornekle_kardinal(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    if alt == "ekli":
        son = _dengeli_son(rng, _SON_TAM, ek, "kardinal")
        return kur_kardinal(_tam_sayi_son(rng, son), politika, ek)
    alt = alt or rng.choices(["kucuk", "orta", "yuz", "bin"], [20, 40, 22, 18])[0]
    if alt == "yas":
        n = rng.choices(range(2, 91), [3] * 8 + [1] * 81)[0] if rng.random() < 0.25 else rng.randint(10, 90)
    elif alt == "model":
        n = rng.randint(10, 30)
    elif alt == "kucuk":
        n = rng.randint(2, 9)
    elif alt == "orta":
        n = rng.choice(_ORTA_YUV) if rng.random() < 0.45 else rng.randint(10, 99)
    elif alt == "yuz":
        n = rng.choice([100, 150, 200, 250, 300, 500, 600, 800]) if rng.random() < 0.4 else rng.randint(100, 999)
    else:
        n = rng.choice([1000, 1500, 2000, 2500, 3000, 5000, 10000, 20000, 50000]) if rng.random() < 0.35 else rng.randint(1000, 99999)
    if ek and n < 10:
        n = rng.randint(10, 99)
    return kur_kardinal(n, politika, ek)


def kur_buyuk_yuvarlak(tam, kesir="", buyukluk="milyon", bucuk=False, rakam_rakam=False, birim=None, ek=None):
    yaz_sayi = _num(tam, kesir) + " " + buyukluk
    sz = _num_kelimeleri(tam, kesir, bucuk, rakam_rakam) + [buyukluk]
    if birim:
        return _sayili_birim(sz, yaz_sayi.rsplit(" ", 1)[0] + " " + buyukluk, birim, 0, ek, "buyuk")
    s, y = _birlestir(sz, yaz_sayi, buyukluk, ek, "sozcuk")
    return Varlik(y, s, "buyuk")


def kur_buyuk_duz(n, birim=None, ek=None):
    sk = S.sayi_kelimeleri(n)
    if birim:
        return _sayili_birim(sk, S.yaz_sayi(n), birim, 0, ek, "buyuk")
    s, y = _birlestir(sk, S.yaz_sayi(n), sk[-1], ek)
    return Varlik(y, s, "buyuk")


_MANTIS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 500]


def ornekle_buyuk(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or rng.choice(["yuvarlak", "tl", "duz", "nufus"])
    if alt == "tl":
        alt = "tl_yuvarlak" if rng.random() < 0.7 else "tl_duz"
    elif alt == "nufus":
        alt = "yuvarlak" if rng.random() < 0.8 else "duz"
    birim = "TL" if alt.startswith("tl") else None
    if alt.endswith("duz"):
        n = rng.choice([1, 2, 3, 4, 5, 7, 8, 12, 15, 23, 34, 48, 56, 67, 78, 91, 120, 245]) * 10**6 + rng.randint(1, 999) * 1000
        if rng.random() < 0.3:
            n += rng.randint(1, 999)
        return kur_buyuk_duz(n, birim, ek)
    buyukluk = "milyar" if alt == "milyar" else rng.choices(["milyon", "milyar", "trilyon"], [68, 29, 3])[0]
    tam = rng.choice(_MANTIS) if buyukluk == "milyon" else rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 50])
    kesir = ""
    if rng.random() < 0.22:
        kesir = rng.choices(["5", "25", "75", "2", "3", "8"], [60, 8, 8, 8, 8, 8])[0]
    bucuk = kesir == "5" and tam > 0 and rng.random() < 0.55
    rr = len(kesir) == 2 and rng.random() < 0.15
    return kur_buyuk_yuvarlak(tam, kesir, buyukluk, bucuk, rr, birim, ek)


def kur_eksi(tam, kesir="", birim=None, bucuk=False, ek=None):
    nk = ["eksi"] + _num_kelimeleri(tam, kesir, bucuk)
    ny = "-" + _num(tam, kesir)
    if birim:
        v = _sayili_birim(nk, ny, birim, 0, ek, "eksi")
        return v
    s, y = _birlestir(nk, ny, _kanonik_son(tam, kesir), ek)
    return Varlik(y, s, "eksi")


def ornekle_eksi(rng, alt=None, ek=None, politika="yaziyla", buyuk_harf=False):
    alt = alt or rng.choice(["derece", "santigrat", "tl", "sayi"])
    if alt in ("derece", "santigrat"):
        tam, kesir = _ondalikli(rng, 1, 35, 0.15)
        if alt == "santigrat" and rng.random() < 0.3:
            tam = rng.choice([18, 20, 40, 50, 80])
            kesir = ""
        bucuk = kesir == "5" and rng.random() < 0.5
        return kur_eksi(tam, kesir, "derece" if alt == "derece" else "C", bucuk, ek)
    if alt == "tl":
        return kur_eksi(rng.choice([50, 100, 250, 500, 1250, 2000, 4000]) if rng.random() < 0.7 else rng.randint(10, 9999), "", "TL", False, ek)
    tam, kesir = _ondalikli(rng, 1, 20, 0.2)
    return kur_eksi(tam, kesir, None, kesir == "5" and rng.random() < 0.5, ek)


ORNEKLEYICILER = {
    "para": ornekle_para, "yuzde": ornekle_yuzde, "olcu": ornekle_olcu, "saat": ornekle_saat,
    "tarih": ornekle_tarih, "sira": ornekle_sira, "telefon": ornekle_telefon, "kod": ornekle_kod,
    "skor": ornekle_skor, "aralik": ornekle_aralik, "ondalik": ornekle_ondalik,
    "kardinal": ornekle_kardinal, "buyuk": ornekle_buyuk, "eksi": ornekle_eksi,
}
