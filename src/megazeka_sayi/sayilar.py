"""Sayıların Türkçe okunuşu (sözlüleştirme) ve yazılı biçim biçimleyicileri."""
from __future__ import annotations

BIRLER = ["sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
BASAMAKLAR = [(10**12, "trilyon"), (10**9, "milyar"), (10**6, "milyon"), (10**3, "bin")]

SIRA_EKLI = {
    "sıfır": "sıfırıncı", "bir": "birinci", "iki": "ikinci", "üç": "üçüncü", "dört": "dördüncü",
    "beş": "beşinci", "altı": "altıncı", "yedi": "yedinci", "sekiz": "sekizinci",
    "dokuz": "dokuzuncu", "on": "onuncu", "yirmi": "yirminci", "otuz": "otuzuncu",
    "kırk": "kırkıncı", "elli": "ellinci", "altmış": "altmışıncı", "yetmiş": "yetmişinci",
    "seksen": "sekseninci", "doksan": "doksanıncı", "yüz": "yüzüncü", "bin": "bininci",
    "milyon": "milyonuncu", "milyar": "milyarıncı", "trilyon": "trilyonuncu",
}


def _yuzlu(n: int) -> list[str]:
    s: list[str] = []
    y, r = divmod(n, 100)
    if y:
        if y > 1:
            s.append(BIRLER[y])
        s.append("yüz")
    o, b = divmod(r, 10)
    if o:
        s.append(ONLAR[o])
    if b:
        s.append(BIRLER[b])
    return s


def sayi_kelimeleri(n: int) -> list[str]:
    if n < 0 or n >= 10**15:
        raise ValueError("0..999 trilyon aralığı dışında")
    if n == 0:
        return ["sıfır"]
    k: list[str] = []
    for deger, ad in BASAMAKLAR:
        grup, n = divmod(n, deger)
        if grup:
            if ad == "bin" and grup == 1:
                k.append("bin")
            else:
                k += _yuzlu(grup) + [ad]
    if n:
        k += _yuzlu(n)
    return k


def sayi_oku(n: int) -> str:
    """Asal sayı okunuşu: 1000 -> "bin", 1_000_000 -> "bir milyon"."""
    return " ".join(sayi_kelimeleri(n))


def sira_kelimeleri(n: int) -> list[str]:
    k = sayi_kelimeleri(n)
    k[-1] = SIRA_EKLI[k[-1]]
    return k


def sira_oku(n: int) -> str:
    return " ".join(sira_kelimeleri(n))


def rakam_kelimeleri(rakamlar: str) -> list[str]:
    return [BIRLER[int(c)] for c in rakamlar]


def rakam_rakam_oku(rakamlar: str) -> str:
    return " ".join(rakam_kelimeleri(rakamlar))


def kesir_kelimeleri(kesir: str, rakam_rakam: bool = False) -> list[str]:
    """Virgülden sonraki basamaklar. Baştaki sıfırlar tek tek 'sıfır' okunur."""
    if rakam_rakam:
        return rakam_kelimeleri(kesir)
    z = len(kesir) - len(kesir.lstrip("0"))
    kalan = kesir.lstrip("0")
    k = ["sıfır"] * z
    if kalan:
        k += sayi_kelimeleri(int(kalan))
    return k


def ondalik_kelimeleri(tam: int, kesir: str, bucuk: bool = False, rakam_rakam: bool = False) -> list[str]:
    if bucuk and kesir == "5" and tam > 0:
        return sayi_kelimeleri(tam) + ["buçuk"]
    return sayi_kelimeleri(tam) + ["virgül"] + kesir_kelimeleri(kesir, rakam_rakam)


def ondalik_oku(tam: int, kesir: str, bucuk: bool = False, rakam_rakam: bool = False) -> str:
    return " ".join(ondalik_kelimeleri(tam, kesir, bucuk, rakam_rakam))


def grup_kelimeleri(rakamlar: str, mod: str) -> list[str]:
    """Telefon grubu: mod 'sayi' (yüz yirmi üç; 05 -> sıfır beş) ya da 'rakam' (bir iki üç)."""
    if mod == "rakam":
        return rakam_kelimeleri(rakamlar)
    z = len(rakamlar) - len(rakamlar.lstrip("0"))
    kalan = rakamlar.lstrip("0")
    return ["sıfır"] * z + (sayi_kelimeleri(int(kalan)) if kalan else [])


def telefon_gruplari(rakamlar: str) -> list[str]:
    """'05321234567' -> ['0532','123','45','67']"""
    return [rakamlar[:4], rakamlar[4:7], rakamlar[7:9], rakamlar[9:11]]


def telefon_kelimeleri(rakamlar: str, modlar=("sayi", "sayi", "sayi", "sayi"), arti90: bool = False) -> list[str]:
    if arti90:
        g = [rakamlar[1:4], rakamlar[4:7], rakamlar[7:9], rakamlar[9:11]]
        k = ["artı", "doksan"]
    else:
        g = telefon_gruplari(rakamlar)
        k = []
    for grup, mod in zip(g, modlar):
        k += grup_kelimeleri(grup, mod)
    return k


# ---- yazılı biçim ----

def yaz_sayi(n: int) -> str:
    """Binlik ayırıcı nokta: 1250 -> '1.250'."""
    return f"{n:,}".replace(",", ".")


def yaz_ondalik(tam: int, kesir: str) -> str:
    return f"{yaz_sayi(tam)},{kesir}"


def yaz_yil(n: int) -> str:
    return str(n)


def yaz_telefon(rakamlar: str, arti90: bool = False) -> str:
    if arti90:
        return f"+90 {rakamlar[1:4]} {rakamlar[4:7]} {rakamlar[7:9]} {rakamlar[9:11]}"
    return f"{rakamlar[:4]} {rakamlar[4:7]} {rakamlar[7:9]} {rakamlar[9:11]}"
