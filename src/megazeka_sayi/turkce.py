"""Türkçeye özgü küçük yardımcılar: harf büyütme/küçültme, ünlü uyumu, ek ekleme.

`str.lower/upper` Türkçede İ/ı harflerini bozar; bu modül onların yerine kullanılır.
"""
from __future__ import annotations

UNLULER = "aeıioöuü"
KALIN = "aıou"
SERT_UNSUZ = "fstkçşhp"  # fıstıkçı şahap

# Ünlüyle başlayan ek gelince yumuşayan (yalnız sözlü biçimde) sözcükler.
YUMUSAMA = {"dört": "dörd", "buçuk": "buçuğ", "çeyrek": "çeyreğ"}

# Ek türleri ve kalıpları. D: d/t, A: a/e, I: ı/i/u/ü, (x): kaynaştırma ünsüzü.
EKLER = {
    "bulunma": "DA",
    "ayrilma": "DAn",
    "yonelme": "(y)A",
    "belirtme": "(y)I",
    "ilgi": "(n)In",
    "iyelik3": "(s)I",
    "vasita": "(y)lA",
    "lik": "lIk",
    "cogul": "lAr",
    "cogul_bulunma": "lArDA",
    "bulunma_ki": "DAki",
}


def lower_tr(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def upper_tr(s: str) -> str:
    return s.replace("i", "İ").replace("ı", "I").upper()


def capitalize_tr(s: str) -> str:
    """İlk harf büyük, kalanı küçük (Türkçe kurallarıyla)."""
    return upper_tr(s[:1]) + lower_tr(s[1:])


def ilk_harfi_buyut(s: str) -> str:
    """Yalnız ilk harfi büyütür, kalanına dokunmaz."""
    return upper_tr(s[:1]) + s[1:]


def son_unlu(kelime: str) -> str:
    for c in reversed(lower_tr(kelime)):
        if c in UNLULER:
            return c
    return "e"


def unluyle_biter(kelime: str) -> bool:
    return bool(kelime) and lower_tr(kelime)[-1] in UNLULER


def ae(unlu: str) -> str:
    """İki yönlü uyum (a/e)."""
    return "a" if unlu in KALIN else "e"


def iiuu(unlu: str) -> str:
    """Dört yönlü uyum (ı/i/u/ü)."""
    if unlu in "aı":
        return "ı"
    if unlu in "ei":
        return "i"
    if unlu in "ou":
        return "u"
    return "ü"


def ek_uret(kok: str, ek: str) -> str:
    """`kok`a gelen ekin yalın biçimi (ör. ("dört","yonelme") -> "e")."""
    kalip = EKLER[ek]
    k = lower_tr(kok)
    unlu = son_unlu(k)
    onceki = k[-1]
    cikti = ""
    i = 0
    while i < len(kalip):
        c = kalip[i]
        if c == "(":
            j = kalip.index(")", i)
            tampon = kalip[i + 1:j]
            if onceki in UNLULER:
                cikti += tampon
                onceki = tampon
            i = j + 1
            continue
        if c == "D":
            ch = "t" if onceki in SERT_UNSUZ else "d"
        elif c == "A":
            ch = ae(unlu)
            unlu = ch
        elif c == "I":
            ch = iiuu(unlu)
            unlu = ch
        else:
            ch = c
        cikti += ch
        onceki = ch
        i += 1
    return cikti


def inflect(kelime: str, ek: str) -> tuple[str, str]:
    """(sözlü ekli sözcük, ek parçası). Çok sözcüklüyse son sözcüğe eklenir.

    Sözlü biçimde `dört` -> `dörd` yumuşaması uygulanır (ünlüyle başlayan ekte).
    """
    onceki, bosluk, son = kelime.rpartition(" ")
    parca = ek_uret(son, ek)
    kok = son
    if parca[0] in UNLULER and lower_tr(son) in YUMUSAMA:
        kok = YUMUSAMA[lower_tr(son)]
    return onceki + bosluk + kok + parca, parca


def written_suffix(kanonik_son_sozcuk: str, ek: str) -> str:
    """Kesme işaretinden sonraki yazılı ek; kanonik okunuşun son sözcüğüne göre.

    Yumuşama yok: 4'e, 4'ü, 4'ün, 4'ten. Örn. ("tele","yonelme") -> "ye".
    """
    return ek_uret(kanonik_son_sozcuk.rpartition(" ")[2], ek)
