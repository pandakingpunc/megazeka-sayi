"""v3 D kaynağı: güvenli Common Voice negatifleri ve hedeflerden sözlüleştirilen kalıplar.

    python training/v3_gercek.py --seed 3303 --out data/v3

Ölçüm kümeleri okunmaz; yalnız cv_duz özetlerinden oluşan dışlama listesi kullanılır.
Şablon kimliği gerçek taşıyıcı yapıyı belirtir; harf/noktalama varyantları yeni şablon değildir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.sablonlar import FILLERS  # noqa: E402
from megazeka_sayi.turkce import (  # noqa: E402
    SERT_UNSUZ, UNLULER, ae, ek_uret, iiuu, ilk_harfi_buyut, inflect, lower_tr, son_unlu,
)
from uret import SAYI_KOKLERI, cv_duz  # noqa: E402

CV_YOLU = KOK.parent / "proje/megazeka/data/raw/common_voice_tr.txt"
HARIC_YOLU = KOK / "data/v3/haric-md5.txt"
BAYT_SINIRI = 180
BOLUMLER = ("train", "validation", "test")
KOTALAR = {"D1": 8000, "D2": 4000, "D3": 3000, "D4": 4000,
           "D5": 3000, "D6": 1500, "D7": 2000, "D8": 1500}


def ozet(metin: str) -> str:
    return hashlib.md5(cv_duz(metin).encode("utf-8")).hexdigest()


def haric_yukle(yol: Path = HARIC_YOLU) -> set[str]:
    """Eksik/bozuk dışlama dosyası sessizce boş listeye dönüşmez."""
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    if any(not re.fullmatch("[0-9a-f]{32}", s.strip()) for s in satirlar if s.strip()):
        raise ValueError("Dışlama dosyasında geçersiz md5")
    return {s.strip() for s in satirlar if s.strip()}


def sozcukler(metin: str) -> list[str]:
    return re.findall(r"[^\W\d_]+", lower_tr(metin))


ZAMIRLER = {"o", "ona", "onu", "onun", "onda", "ondan", "onunla", "onca", "onsuz", "onsuzluk",
            "onlar", "onlara", "onları", "onların", "onlarda", "onlardan", "onlarla", "onlarsız",
            "onlarınki", "onlarınkini", "onlarınkine", "onunki", "onunkini", "onunkine"}
BIR_BICIMLERI = {"bir", "biraz", "birkaç", "birçok", "birden", "birdenbire", "birlikte", "biri", "birisi",
                 "birer", "birtakım", "birlik", "biricik", "birini", "birine", "birinin", "birinde", "birinden",
                 "biriyle", "birisini", "birisine", "birisinin", "birisinde", "birisinden", "birisiyle"}
BIRBIRI = {"birbiri", "birbirini", "birbirine", "birbirinin", "birbirinde", "birbirinden", "birbiriyle",
           "birbirleri", "birbirlerini", "birbirlerine", "birbirlerinin", "birbirlerinden", "birbirleriyle",
           "birbirimiz", "birbirimizi", "birbirimize", "birbirimizin", "birbirimizden", "birbirimizle",
           "birbiriniz", "birbirinizi", "birbirinize", "birbirinizin", "birbirinizden", "birbirinizle"}
YUZ_BICIMLERI = {"yüzü", "yüzüm", "yüzün", "yüzünü", "yüzüne", "yüzünde", "yüzünden", "yüzler", "yüzlerce",
                 "yüzey", "yüzük", "yüzme", "yüzmek", "yüzdü", "yüzüyor", "yüzsüz"}
BIN_BICIMLERI = {"binmek", "binip", "binen", "binlerce"}


def guvenli_sozcuk(w: str) -> bool:
    """D1'in kapalı izin listesi. Belirsiz kökler ve bilinmeyen çekimler alınmaz."""
    if w.startswith("altıncı"):
        return False
    return (w in ZAMIRLER | BIR_BICIMLERI | BIRBIRI | YUZ_BICIMLERI | BIN_BICIMLERI
            or w in {"altüst", "ikilem", "üçgen", "dörtnala", "milyonlarca", "milyoner", "onlarca", "sekizgen"}
            or w.startswith(("birleş", "birik", "yüzleş", "altın", "yedir", "yediği", "yedikten",
                             "bindi", "binme", "biner", "binecek", "binmiş", "bina", "kırkma", "ikiz",
                             "beşik", "eksik", "eksil", "yarım", "çeyrek"))
            or w in {"yedim", "yedin", "yedik", "yediniz", "yediler"})


def d1_grubu(metin: str) -> str | None:
    """Kök içeren her sözcük güvenli ve bağlamı da sayısızsa grubu döndürür."""
    if re.search(r"\d|[%&@#/+=*<>°²]", metin) or len(metin.encode("utf-8")) > 180:
        return None
    tk = sozcukler(metin)
    koklu = [w for w in tk if w.startswith(SAYI_KOKLERI) or w in {"o", "altüst"}]
    if not koklu or any(not guvenli_sozcuk(w) for w in koklu):
        return None
    for i, w in enumerate(tk):
        once = tk[i - 1] if i else ""
        sonra = tk[i + 1] if i + 1 < len(tk) else ""
        # Komşu, güvenli bir sözcükse (ona, onu, yarım …) sayı sayılmaz.
        if w == "bir" and any(x.startswith(SAYI_KOKLERI) and not guvenli_sozcuk(x) for x in (once, sonra)):
            return None
        # İzin listesi biçimden ibaret: bu bağlamlarda aynı biçim sayı olabilir.
        if w in {"ona", "onu", "onun", "onda", "ondan"} and (
                once in {"saat", "sayı", "yüzde", "eksi"} or sonra in {"kadar", "doğru", "dek", "kala"}):
            return None
        if w == "bir" and sonra.startswith(("lira", "kuruş", "kilo", "metre", "gram", "litre", "santim")):
            return None
        if w == "bir" and once in {"saat", "yüzde", "eksi"}:
            return None
        if w in {"biri", "birisi"} and (once.endswith("ayın") or once in {"ayın", "mayısın", "kasımın"}):
            return None
        if w.startswith(("yarım", "çeyrek")) and once and once in S.BIRLER + S.ONLAR:
            return None
    if any(w in ZAMIRLER for w in tk):
        return "zamir"
    if any(w.startswith("bir") for w in tk):
        return "bir"
    return "diger"


def d1_yukle(cv: Path, haric: set[str], seed: int = 3303) -> tuple[dict, dict]:
    """Düzleştirilmiş cümle özeti hem biçimleri hem bölüm atamasını bir arada tutar."""
    havuz = {b: {g: [] for g in ("zamir", "bir", "diger")} for b in BOLUMLER}
    gorulen, sayim = set(), Counter()
    for t in cv.read_text(encoding="utf-8-sig").splitlines():
        t = t.strip()
        oz = ozet(t)
        if oz in haric:
            sayim["haric"] += 1
            continue
        if oz in gorulen:
            continue
        gorulen.add(oz)
        grup = d1_grubu(t)
        if grup is None:
            continue
        kova = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16) % 100
        b = "test" if kova < 6 else "validation" if kova < 12 else "train"
        havuz[b][grup].append((oz, t))
    for b in BOLUMLER:
        for g in havuz[b]:
            random.Random(f"{seed}-D1-{b}-{g}").shuffle(havuz[b][g])
    return havuz, dict(sayim)


def cek(kok: str, ek: str) -> tuple[str, str]:
    """'saat' ince çekilir; src değiştirilmeden yerel sarmalayıcı kullanılır."""
    if kok == "saat":
        # Son ünsüz serttir, son ünlü işlevsel olarak incedir: saatte/saatten/saate.
        ekler = {"bulunma": "te", "ayrilma": "ten", "yonelme": "e", "belirtme": "i",
                 "ilgi": "in", "iyelik3": "i", "vasita": "le", "lik": "lik",
                 "cogul": "ler", "cogul_bulunma": "lerde", "bulunma_ki": "teki"}
        return kok + ekler[ek], ekler[ek]
    return inflect(kok, ek)


def ek_parcasi(kok: str, tur: str) -> str:
    """İyelik ve ek-fiil; sayı/para eklerinde kullanılan açık kalıp kümesi."""
    u = son_unlu(kok)
    ince = iiuu(u)
    sesli = kok[-1] in UNLULER
    d = "t" if kok[-1] in SERT_UNSUZ else "d"
    if tur in {"m", "n", "miz", "niz"}:
        return ("" if sesli else ince) + {"m": "m", "n": "n", "miz": "m" + ince + "z",
                                              "niz": "n" + ince + "z"}[tur]
    if tur == "si":
        return ("s" if sesli else "") + ince
    if tur == "leri":
        return "l" + ae(u) + "r" + ("ı" if ae(u) == "a" else "i")
    if tur == "sini":
        return ek_parcasi(kok, "si") + "n" + ince
    if tur == "dir":
        return d + ince + "r"
    if tur == "di":
        return ("y" if sesli else "") + d + ince
    if tur == "mis":
        return ("y" if sesli else "") + "m" + ince + "ş"
    if tur == "deymis":
        return ek_uret(kok, "bulunma") + "ym" + ("ı" if ae(u) == "a" else "i") + "ş"
    return cek(kok, tur)[1]


def sayi(n: int, ek: str | None = None, kucuk: bool = False) -> V.Varlik:
    """Önce yazılı sayı; sözlü biçim hedefin sayısal değerinden türetilir."""
    if kucuk and n < 10:
        yaz = S.sayi_oku(n)
        return V.Varlik(yaz, yaz, "negatif_kalip")
    yaz = S.yaz_sayi(n)
    soz = S.sayi_oku(int(yaz.replace(".", "")))
    if ek:
        parca = ek_parcasi(soz.split()[-1], ek)
        yaz += "'" + parca
        if ek in {"yonelme", "belirtme", "ilgi", "iyelik3"}:
            soz = inflect(soz, ek)[0]
        else:
            soz += parca
    return V.Varlik(yaz, soz, "kardinal")


def para(n: int, ek: str | None = None, kurus: bool = False) -> V.Varlik:
    birim = "kuruş" if kurus else "TL"
    kok = "kuruş" if kurus else "le"
    yaz = f"{S.yaz_sayi(n)} {birim}"
    parca = ek_parcasi(kok, ek) if ek else ""
    yaz += ("" if kurus or not ek else "'") + parca
    deger = int(yaz.split()[0].replace(".", ""))
    soz = S.sayi_oku(deger) + " " + ("kuruş" if kurus else "lira")
    soz += ek_parcasi("kuruş" if kurus else "lira", ek) if ek else ""
    return V.Varlik(yaz, soz, "para")


def boy(cm: int) -> V.Varlik:
    if not 10 <= cm <= 99:
        raise ValueError("Boy yalnız bir + onluk[+birlik] biçiminde")
    yaz = f"1,{cm:02d}"
    return V.Varlik(yaz, "bir " + S.sayi_oku(int(yaz.split(",")[1])), "ondalik")


def aralik(a: int, b: int, birim: str, bucuk: bool = False) -> V.Varlik:
    yaz = f"{a}{',5' if bucuk else ''}-{b} {birim}"
    sol, sag = yaz.split()[0].split("-")
    if not bucuk and "bir" in S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b):
        raise ValueError("Yalın bir içeren aralık üretilmez")
    soz = S.sayi_oku(int(sol.split(",")[0])) + (" buçuk" if "," in sol else "")
    soz += " " + S.sayi_oku(int(sag)) + " " + {"kg": "kilo"}.get(birim, birim)
    return V.Varlik(yaz, soz, "aralik")


def bilesik(h: int, m: int) -> V.Varlik:
    yaz = f"{h} saat {m} dakika"
    tk = yaz.split()
    return V.Varlik(yaz, S.sayi_oku(int(tk[0])) + " saat " + S.sayi_oku(int(tk[2])) + " dakika", "karisik")


def olgu_of(r: dict) -> str:
    return r["sablon"].split("-")[1].upper()


# Sözler kendi bilgimizle seçildi; salt çekim değişiklikleri ayrı söz sayılmaz.
SOZLER = tuple(s.strip() for s in """
kırk yılda bir
bin bilsen de bir bilene danış
iki cambaz bir ipte oynamaz
dokuz köyden kovulur
yüz yüze
üç beş kuruş
kırk yıl hatırı var
bin nasihatten bir musibet yeğdir
yedi kat yerin dibi
otuz iki dişini göstermek
bir elin nesi var iki elin sesi var
bir taşla iki kuş vurmak
iki arada bir derede kalmak
iki ayağını bir pabuca sokmak
iki dirhem bir çekirdek
iki gözü iki çeşme
iki yakası bir araya gelmemek
iki eli kanda olsa gelmek
iki lafın belini kırmak
iki büklüm olmak
iki gözüm
iki cihan saadeti
iki elim yakanda
iki cami arasında kalmış beynamaz
iki ucu keskin bıçak
iki paralık etmek
iki paralık olmak
iki çift laf etmek
iki satır yazı
iki yüzlü olmak
iki ateş arasında kalmak
iki baş bir kazanda kaynamaz
iki karpuz bir koltuğa sığmaz
iki dinle bir söyle
iki gönül bir olunca samanlık seyran olur
iki testi çarpışınca biri kırılır
iki el bir baş içindir
iki kaptan bir gemiyi batırır
üç aşağı beş yukarı
üç günlük dünya
dört dörtlük
dört başı mamur
dört elle sarılmak
dört gözle beklemek
dört bir yana dağılmak
dört duvar arasında kalmak
dört ayak üstüne düşmek
dört köşe olmak
dört dönmek
beş para etmez
beş parasız kalmak
beş benzemez
beş aşağı beş yukarı
beş parmak bir olmaz
beşikte öğrenilen mezarda unutulmaz
altı üstü
altından çapanoğlu çıkmak
altın anahtar her kapıyı açar
altın yere düşmekle pul olmaz
altın bilezik
altın yumurtlayan tavuğu kesmek
yedi düvel
yedi iklim dört bucak
yedi sülalesini saymak
yedi kat yabancı
yedi cihana duyurmak
yedi mahalle duymak
yedisinden yetmişine
sekiz köşe olmak
dokuz canlı
dokuz doğurmak
dokuz yorgan eskitmek
dokuz ölç bir biç
on parmağında on marifet
on para etmez
on paralık etmek
on beşinde kız ya erde gerek ya yerde
otuz iki kısım tekmili birden
kırk dereden su getirmek
kırk fırın ekmek yemek
kırk yıllık dost
kırk yılın başı
kırk gün kırk gece
kırkından sonra azanı teneşir paklar
kırk kapının ipini çekmek
kırk tarakta bezi olmak
yetmiş iki millete bir gözle bakmak
yüz bulmak
yüz vermek
yüz çevirmek
yüz göz olmak
yüz karası
yüz akı
yüz kızartmak
yüzü kızarmak
yüzü gülmek
yüzü düşmek
yüzü suyu hürmetine
yüzüne bakmamak
yüzüne vurmak
yüzüne gözüne bulaştırmak
yüzünü ağartmak
yüzünü kara çıkarmak
yüzünü şeytan görsün
yüzünü görmemek
yüz görümlüğü
yüzüne bir daha bakmamak
yüzünü ekşitmek
yüzüne gülmek
yüzünden düşen bin parça
yüzüne tükürseler yağmur yağıyor sanmak
yüzü kasap süngeriyle silinmiş
yüzü yerde olmak
yüzü tutmamak
yüzü kalmamak
yüz bulunca astarını istemek
yüzüne renk gelmek
yüzüne kan gelmek
yüzüne kapıyı kapatmak
yüzüne hasret kalmak
yüzünden okunmak
yüzüne karşı söylemek
bin pişman olmak
bin bir türlü
bin bir çeşit
bin dereden su getirmek
bin tarakta bezi olmak
bin derde deva
bin can ile
bin kalıba girmek
bin yaşa
bin düşünüp bir söylemek
bin dost az bir düşman çok
bin tasa bir borç ödemez
bin atın varsa inişte in bir atın varsa yokuşta bin
bir musibet bin nasihatten iyidir
bir deli kuyuya taş atar kırk akıllı çıkaramaz
bir fincan kahvenin kırk yıl hatırı vardır
bir ağızdan söylemek
bir ayağı çukurda olmak
bir baltaya sap olmak
bir bardak suda fırtına koparmak
bir çuval inciri berbat etmek
bir çırpıda bitirmek
bir dediğini iki etmemek
bir deri bir kemik kalmak
bir dikili ağacı olmamak
bir dokun bin ah işit
bir el atmak
bir eli yağda bir eli balda olmak
bir eliyle verdiğini öbür eliyle almak
bir gömlek üstün olmak
bir içim su
bir kalemde silmek
bir kaşık suda boğmak
bir kılına zarar gelmemek
bir köşeye çekilmek
bir kulağından girip öbüründen çıkmak
bir lokma bir hırka
bir pire için yorgan yakmak
bir solukta okumak
bir sözünü iki etmemek
bir tahtası eksik olmak
bir ucundan tutmak
bir yaşıma daha girdim
bir yastıkta kocamak
bir yolunu bulmak
birbirine düşmek
birbirine girmek
birbirini yemek
birbirini tutmamak
birbirine sırt çevirmek
birbirine kenetlenmek
birbirinden aşağı kalmamak
birlikten kuvvet doğar
birlikte rahmet ayrılıkta azap vardır
bir koltuğa iki karpuz sığmaz
bir sürçen atın başı kesilmez
bir çiçekle bahar olmaz
bir çöplükte iki horoz ötmez
bir akçelik eşeğin bin akçelik sıpası olur
bir baş soğan bir kazanı kokutur
bir bulutla kış olmaz
bir dirhem et bin ayıp örter
bir felaket bin nasihatten yeğdir
bir koyundan iki post çıkmaz
bir selam bin hatır yapar
bir söyle on dinle
bir yiğit kırk yılda meydana gelir
bir zamanlar
bir varmış bir yokmuş
bir an önce
bir daha
bir türlü
bir yana bırakmak
bir bakıma
bir hayli
bir nebze
bir anda
bir hamlede
bir arada
bir tek
bir tanem
bir ara
bir zahmet
bir dahaki sefere
bir şeyler çevirmek
bir sürü
bir iki derken
bir bir saymak
bir o yana bir bu yana
bir ileri bir geri
bir aşağı bir yukarı
bir sağa bir sola
bir var bir yok
bir laf etmek
bir de bakmışsın
bir kere olsun
bir kereden bir şey olmaz
bir an olsun
bir arpa boyu yol gitmek
bir damla suya muhtaç olmak
bir lokma ekmeğe muhtaç olmak
bir çift söz söylemek
bir avuç insan
bir fiske vurmak
bir sinekten yağ çıkarmak
bir kenara atmak
bir ayağı içeride bir ayağı dışarıda
bir kaşık aşım kaygısız başım
bir göz oda
bir ipte iki cambaz oynamaz
bir ayağı mezarda olmak
bir ömür boyu
bir öyle bir böyle
bir o eksikti
bir sen eksiktin
bir ayak üstünde kırk yalan söylemek
bir kapı kapanır bir kapı açılır
yediği önünde yemediği arkasında
yediği kaba pislemek
yediği naneye bak
altını üstüne getirmek
altından kalkmak
altını çizmek
altına imza atmak
altından girip üstünden çıkmak
altında kalmamak
altında ezilmek
altın çağını yaşamak
altın tepside sunmak
binbir surat
binbir güçlükle
sıfırı tüketmek
sıfırdan başlamak
sıfıra sıfır elde var sıfır
sıfır araba
yarım ağızla konuşmak
yarım yamalak
yarım elma gönül alma
yarım hekim candan yarım hoca dinden eder
yarım akıllı
yarım kulak dinlemek
ikide bir
bire bir
birebir görüşmek
iki lafı bir araya getirememek
dört yol ağzı
bir kuruşun hesabını yapmak
bir can borcu olmak
bir uçtan bir uca
bir çatı altında
bir parmak bal çalmak
bir araya gelmek
bir çekidüzen vermek
bir baştan bir başa
bir iki demeden
bir kolu kanadı kırılmak
bir tatlı söz
bir hoş seda bırakmak
bir köroğlu bir ayvaz
bir ayağı üzengide olmak
bir kararda durmamak
bir kalıba sığmamak
bir çıkmaz sokağa girmek
bir elden yönetmek
bir hayra vesile olmak
bir günün beyliği beyliktir
bir kılını kıpırdatmamak
bir kaşık suda boğulmak
birbirinin kuyusunu kazmak
birbirinin gözünü oymak
birbirinin dilinden anlamak
birbirine omuz vermek
birbirine kol kanat germek
birbirinin yarasına merhem olmak
birbirinin yüzüne bakamamak
birbirini aratmamak
birbirinin ağzının içine bakmak
birbirini çekememek
birbirine laf atmak
birbirinin ekmeğine yağ sürmek
birbirinin ipliğini pazara çıkarmak
birbirine düşman kesilmek
birbirini gözden çıkarmak
birbirine arka çıkmak
birbirine gönül vermek
iki eli böğründe kalmak
iki gözümün çiçeği
ikili oynamak
üçler yediler kırklar
kırklara karışmak
yedi ceddine rahmet
yedi ceddine sövmek
yüzüstü bırakmak
yüzüstü kalmak
yüzüstü kapaklanmak
yüzsuyu dökmek
yüzsüzlük etmek
yüzüne bakacak hâli olmamak
bir hatır için iki hatır çiğnenmez
bir evde iki kız biri çuvaldız biri biz
""".strip().splitlines())


@dataclass(frozen=True)
class Sablon:
    id: str
    olgu: str
    tur: str
    metin: str
    ayar: str = ""


# Adlar sözlük biçiminde (büyük harfli) tutulur; düz kipte şablonla birlikte küçültülür.
ISIMLER = tuple(FILLERS["isim"])
ZAMANLAR = ("yarın", "bugün", "akşam", "sabah", "öğleden sonra", "pazartesi", "salı", "çarşamba",
            "perşembe", "cuma", "cumartesi", "pazar", "bu akşam", "yarın sabah", "yarın akşam")
SABLONLAR: dict[str, list[Sablon]] = {f"D{i}": [] for i in range(3, 9)}
# Kalıbın kendisinden söz eden (üst-dil) taşıyıcılar; D3 ve D8'de payı sınırlıdır.
UST_DIL: set[str] = set()


def ekle(olgu: str, tur: str, metin: str, ayar: str = "") -> None:
    lst = SABLONLAR[olgu]
    for i, s in enumerate(lst):
        if (s.tur, s.metin) == (tur, metin):
            ayarlar = list(dict.fromkeys(s.ayar.split("|") + ayar.split("|")))
            lst[i] = Sablon(s.id, s.olgu, s.tur, s.metin, "|".join(ayarlar))
            return
    lst.append(Sablon(f"v3d-{olgu.lower()}-{len(lst):04d}", olgu, tur, metin, ayar))


def ekle_ust(olgu: str, tur: str, metin: str, ayar: str = "") -> None:
    UST_DIL.add(metin)
    ekle(olgu, tur, metin, ayar)


# ---------------------------------------------------------------- D3
# Her tür kendi doğal taşıyıcılarını taşır; sayı öbeği cümlede dilbilgisel yerindedir.
D3_DOGAL = {
    "madeni": (
        "{v}", "cebinden {v} çıkarıp uzattı", "elinde {v} vardı", "bana {v} verdi",
        "masanın üstünde {v} duruyordu", "kasada {v} kalmıştı", "çekmecede {v} bulduk",
        "yerde {v} buldum", "kasiyer {v} geri verdi", "komşumuz {v} getirdi",
        "annem cüzdanından {v} ayırdı", "dilenciye {v} bırakıp yürüdü", "tezgâhın üstüne {v} koydu",
        "sonunda {v} bulabildi", "çocuk şapkaya {v} attı", "{isim} cebinden {v} çıkardı",
        "çantada {v} unutmuşum", "kumbaradan {v} çıktı", "{isim} bana {v} uzattı, sonra güldü",
    ),
    "boy_sifat": (
        "{v}", "kapıda {v} zayıf bir adam duruyordu", "{v} esmer bir genç içeri girdi",
        "gelen kişi {v} sarışın bir kadındı", "{v} iri yarı bir polis yolumuzu kesti",
        "tezgâhın başında {v} bir kadın bekliyordu", "köşedeki masada {v}, gözlüklü bir adam oturuyordu",
        "karşımıza {v} yaşlı bir amca çıktı",
    ),
    "boy_ad": (
        "{v}", "{v} kapıyı çaldı", "pencerenin önünde {v} sigara içiyordu", "{v} bana yol sordu",
        "dün akşam {v} bizi aradı", "otobüste {v} yanıma oturdu", "{v} yavaşça içeri girdi",
    ),
    "boy_yuklem": (
        "{v}", "oğlu o zaman daha {v}", "kız kardeşim ancak {v}", "delikanlı en fazla {v}",
        "{isim} {v}, ama çok güçlüydü", "babam gençken {v}",
    ),
    "aralik_sure": (
        "{v}", "yol {v} sürdü", "toplantı {v} sürer", "burada {v} bekledik", "ameliyat {v} sürdü",
        "{isim} {v} uyudu", "kek fırında {v} pişer", "sınav {v} sürecek",
    ),
    "aralik_uzun": (
        "{v}", "kargo {v} içinde gelir", "inşaat {v} sürdü", "tatil {v} sürecek", "{isim} burada {v} kaldı",
        "bu iş için {v} ayırdım",
    ),
    "aralik_kilo": (
        "{v}", "pazardan {v} elma aldım", "{isim} sepete {v} domates koydu", "fırına {v} un yeter",
        "çuvalda {v} patates kalmıştı", "bu tarif için {v} kıyma lazım",
    ),
    "aralik_kisi": (
        "{v}", "kapıda {v} bekliyordu", "salonda {v} oturuyordu", "düğüne {v} geldi",
        "toplantıya {v} katıldı", "otobüste {v} vardı", "köy meydanında {v} toplanmıştı",
    ),
    "yaklasik_zaman": (
        "{v}", "{v} yola çıkarız", "{v} döndü", "{v} yeniden aradı", "{v} haber veririm",
        "{isim} {v} uyandı", "{v} kapıyı çaldılar",
    ),
    "yaklasik_kisi": (
        "{v}", "düğünde {v} vardık", "salonda {v} oturuyordu", "kapıda {v} toplanmıştı",
        "toplantıya {v} katıldı", "kafeye {v} geldi",
    ),
    "yaklasik_mesafe": (
        "{v}", "{v} küçük bir çeşme var", "{v} bir kapı gördü", "{v} sağa dönmemiz gerekiyor",
        "{isim} {v} durup bekledi",
    ),
    "paylasim_sat": (
        "{v}", "pazarda {v} satılıyor", "tezgâhta {v} satılıyordu", "bakkal {v} veriyor",
        "bunlar çarşıda {v} satılıyor",
    ),
    "paylasim_hic": ("{v}", "{v} ucuz değil", "bakın, {v} ucuz değil", "dükkânda {v} ucuz değil"),
}
for _tur, _lst in D3_DOGAL.items():
    for _m in _lst:
        ekle("D3", _tur, _m)
D3_UST = ('soruda "{v}" denmiş', 'yazar "{v}" demiş', 'sözlükte "{v}" örneğini gördüm',
          'metinde "{v}" ifadesi geçiyor', 'cümlede "{v}" kalıbını gördük', 'örnekte "{v}" deniyor')
for _tur in ("madeni", "boy_ad", "aralik_sure", "aralik_uzun", "yaklasik_zaman"):
    for _m in D3_UST:
        ekle_ust("D3", _tur, _m)


# ---------------------------------------------------------------- D4
# Ad + yüklem birlikteliği seçilir; rastgele ad/yüklem eşleştirmesi yapılmaz.
ADLI = """
kişi|salonda sessizce oturuyordu
çocuk|bahçede neşeyle oynuyordu
adam|köşede sabırla bekliyordu
kadın|pencerenin yanında sohbet ediyordu
öğrenci|sabah erkenden okula geldi
öğretmen|toplantı için bahçede buluştu
yolcu|durakta yağmur altında bekledi
misafir|akşam yemeğine biraz erken geldi
işçi|çatıda sabahtan beri uğraşıyordu
köylü|tarlada sessizce çalışıyordu
komşu|kapının önünde beni bekliyordu
kardeş|aynı odada birlikte kalıyordu
arkadaş|yol boyunca bizimle yürüdü
oyuncu|sahne arkasında sırasını bekliyordu
seyirci|gösteri bitince salondan ayrıldı
turist|eski sokaklarda dolaşıp fotoğraf çekti
usta|atölyede akşama kadar çalıştı
balıkçı|kıyıda gün doğmasını bekliyordu
asker|karakolun önünde nöbet tutuyordu
doktor|hastanede sabaha kadar çalıştı
hemşire|koridorda sessizce bekliyordu
memur|dilekçeleri sabah masaya bıraktı
şoför|garajda motorun sesini dinliyordu
ressam|sahilde yan yana resim yapıyordu
müzisyen|kuliste son hazırlıkları yapıyordu
kedi|duvarın üstünde güneşe uzanmıştı
köpek|bahçenin kapısında sessizce bekliyordu
kuş|pencerenin önünde usulca ötüyordu
at|ahırın önünde sakin sakin duruyordu
koyun|yamaçta otlayıp duruyordu
kitap|rafların arasında kaybolup gitmişti
defter|masanın üstünde açık duruyordu
kalem|çekmecenin içinde unutulup kalmıştı
mektup|yıllarca aynı çekmecede saklı kaldı
satır|sayfanın altında okunaksız biçimde duruyordu
sayfa|rüzgâr çıkınca bahçeye savruldu
cümle|o akşam herkesin aklında kaldı
fotoğraf|eski sandığın dibinden çıktı
tablo|duvarda yan yana asılı duruyordu
sandalye|salonda kimse gelmeden hazır bekliyordu
masa|bahçenin gölgelik köşesinde duruyordu
oda|gün boyunca bomboş kaldı
ev|tepenin yamacında yalnız başına duruyordu
köy|kış boyunca dış dünyadan uzak kaldı
ağaç|fırtınada kökünden sökülüp devrildi
fidan|bahçede yağmuru bekleyip durdu
çiçek|pencerenin önünde usulca açıyordu
elma|sepette akşama kadar bekledi
ekmek|sofrada el değmeden kaldı
tabak|tezgâhın üstünde sabaha kadar durdu
bardak|masanın kenarında unutulup kalmıştı
fincan|dolabın üst rafında duruyordu
çanta|kapının yanında sessizce duruyordu
bavul|yola çıkmadan önce hazırlandı
kutu|kilerde üst üste yığılı duruyordu
paket|akşam olmadan kapıya bırakıldı
anahtar|çekmecenin dibinde unutulup kalmıştı
bilet|cebinin içinde buruşup kalmıştı
düğme|ceketin üstünden kopup düşmüştü
kapı|rüzgâr yüzünden açık kalmıştı
pencere|gece boyunca açık kaldı
basamak|avlunun sonundaki merdivende eksikti
adım|attıktan sonra durup çevresine baktı
kez|denedikten sonra sonunda başardı
defa|sordu ama kimse cevap vermedi
gün|boyunca evden dışarı çıkmadım
gece|boyunca yağmur hiç dinmedi
hafta|boyunca onu sabırla bekledim
ay|boyunca aynı odada kaldım
yıl|boyunca o köyde yaşadım
sene|boyunca bu sokakta oturdum
saat|boyunca pencereden dışarı baktım
katlı|otelin önünde sessizce durup bekledik
kişilik|orkestra salonda akşama kadar prova yaptı
yaşında|bir çocuk kapıyı usulca araladı
senedir|aynı evde sessiz sakin oturuyorum
"""
D4_GOVDELER = (
    "o gün, {v} {ad} {son}", "hatırlıyorum, {v} {ad} {son}", "anlaşılan, {v} {ad} {son}",
    "biliyorsun, {v} {ad} {son}", "orada, {v} {ad} {son}", "meğer, {v} {ad} {son}",
    "duydum ki, {v} {ad} {son}", "galiba, {v} {ad} {son}", "ne yazık ki, {v} {ad} {son}",
    "öyle ya, {v} {ad} {son}", "bana kalırsa, {v} {ad} {son}", "sonra, {v} {ad} {son}",
    '"{v} {ad} {son}," dedi {isim}', 'bana şunu anlattı: "{v} {ad} {son}"',
)
# Sayı + ad birlikteliği gerçekçi kalsın diye üst sınırlar (10 ve üstü karşıtlar için).
D4_UST = {"yaşında": 90, "katlı": 40, "kişilik": 150, "yıl": 80, "sene": 60, "senedir": 60, "saat": 48,
          "gün": 100, "gece": 40, "hafta": 40, "ay": 60,
          # küçük eşya ve hayvanlar
          "anahtar": 50, "bilet": 60, "düğme": 60, "kalem": 60, "fincan": 40, "bardak": 50, "tabak": 60,
          "defter": 60, "mektup": 60, "çanta": 50, "bavul": 50, "kedi": 50, "köpek": 50, "tablo": 50,
          "köy": 50, "oda": 60, "kapı": 60, "pencere": 60, "masa": 80, "fotoğraf": 120, "at": 100, "ev": 100,
          "usta": 100, "doktor": 60, "hemşire": 60, "memur": 100, "ressam": 60, "müzisyen": 60, "şoför": 60,
          "kardeş": 20, "komşu": 40, "misafir": 100, "turist": 150, "oyuncu": 60}
D4_ADAY = (10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 24, 25, 30, 32, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 150)
for _satir in ADLI.strip().splitlines():
    _ad, _son = _satir.split("|")
    for _g in D4_GOVDELER:
        ekle("D4", "ad", _g.replace("{ad}", _ad).replace("{son}", _son), _ad)
for _g in ("yolculuk {v} sürdü, sonunda eve vardık", "o gün {v} bekledik, sonra yola çıktık",
           "yürüyüş {v} sürdü, ardından sessizce geri döndük", "{isim} {v} çalıştı, sonra biraz dinlendi",
           "hazırlık {v} sürdü, ama herkes sonuçtan memnundu", "durakta {v} bekledik, kimse gelip bizi aramadı",
           "çalışma {v} sürdü, nihayet herkes rahatladı", "tartışma {v} sürdü, sonra ortalık sessizleşti",
           "biz {v} yürüdük, sonunda köye vardık", "{isim} ile {v} konuştuk, sonra vedalaştık",
           "{v} yol aldık, ama hâlâ varamamıştık", "{v} uğraştık, sonunda kapıyı açabildik"):
    ekle("D4", "sure", _g)
for _g in ("{v} diye sayarken çocuklar da bana katıldı", "oyun başlamadan {v} diye birlikte saydık",
           "kapının arkasından {v} diyen bir ses geldi", "{isim} {v} diye saydı sonra hepimiz sustuk",
           "bahçede {v} diye sayan çocukları duydum", "{v} diye sayarken birden gülmeye başladık",
           "biz {v} diye saydık ama kimse çıkmadı", "{isim} oyun için {v} diye geri saydı"):
    ekle("D4", "sayma", _g)


# ---------------------------------------------------------------- D5
# (ad, soru eki, yüklem): sayı + ad doğal bir yüklemle birlikte gelir.
D5_KARDINAL = (
    ("kişi", "mi", "geldi"), ("kişi", "mi", "bekliyordu"), ("adım", "mı", "kaldı"), ("kitap", "mı", "okumuş"),
    ("öğrenci", "mi", "sınıfta kaldı"), ("koyun", "mu", "kaybolmuş"), ("sayfa", "mı", "kaldı"),
    ("bilet", "mi", "sattık"), ("sandalye", "mi", "eksik"), ("basamak", "mı", "çıktık"),
    ("fidan", "mı", "diktik"), ("balık", "mı", "yakaladı"), ("bardak", "mı", "kırıldı"),
    ("çocuk", "mu", "oynuyordu"), ("misafir", "mi", "geldi"), ("ağaç", "mı", "kesildi"),
    ("kilometre", "mi", "yürüdük"), ("kutu", "mu", "açtı"),
)
for _n, _mi, _y in D5_KARDINAL:
    for _m in ("{v} {n} {y}.", '"{v} {n} {y}." dedi.', '“{v} {n} {y}!” diye bağırdı.', "{v} {n} {mi} {y}?",
               'yanındakine: "{v} {n} {y}." dedi.', '"{v} {n} {y}?" diye sordu.'):
        ekle("D5", "kardinal", _m.replace("{n}", _n).replace("{y}", _y).replace("{mi}", _mi))
for _m in ("{v}.", "{v}!", "{v}?", "{v}…", "evet, {v}.", "yok, {v} değil.", "{v} {mi}"):
    ekle("D5", "kardinal", _m)
for _m in ("{v} aylık…", "{v} yeter!", "{v} kaldı.", "{v} {mi}", '"{v} yeter." dedi.', "“{v} kaldı!” diye bağırdı.",
           "ücreti: {v}.", "cevap: {v}!", "{v} bile yetmez.", "{v} ödedim.", '"{v} ister misin?" diye sordu.',
           "bana {v} lazım.", "{v} fazla değil mi?", "bugün yalnız {v} kazandık.", 'kasiyer: "{v} tutuyor." dedi.',
           "toplam {v} tuttu…", "{v} tutarında bir fatura geldi.", "kaç lira? {v}.", "hesap ne kadar? {v} {mi}",
           "{v} desen verirler.", "“{v} olur mu?” dedi.", "{v} versen alırım!", "{v} bile bulamadım…",
           "{v} sayıp masaya bıraktı.", "{v} yeter de artar bile.", "{v} {mi} diye sordu.",
           '"{v}!" diye bağırdı satıcı.', "tek isteğim {v}."):
    ekle("D5", "para", _m)
for _m in ('"{v} yaşında adam böyle yapar mı?" dedi.', "{v} yaşında bir adam…", "{v} yaşındaydı.", "{v} yaşına geldi!",
           "“{v} yaşındayım.” dedi.", "yaşı: {v}.", 'bana: "{v} yaşındayım!" dedi.', "{v} yaşında mı?",
           "{v} yaşındaki çocuk uyandı.", "{v} yaşındaki kadın içeri girdi.", "kaç yaşındasın? {v} yaşındayım.",
           '"{v} yaşını geçti," dedi annem.', "{v} yaşında olmasına rağmen çok çevikti.",
           "{v} yaşına girdiğinde köyden ayrıldı.", "“{v} yaşında bir adamım!” diye bağırdı.",
           "{v} yaşındayken babasını kaybetmiş.", "şimdi {v} yaşında olurdu.",
           "doktor: {v} yaşında bir hasta geldi.", "{v} yaşında bile olsa çalışıyordu.",
           "{v} yaşındaki komşumuz bahçeyle uğraşıyor.", '"{v} yaşındaydı," diye düşündü.'):
    ekle("D5", "yas", _m)
for _m in ("{v} yıl geçti.", "{v} sene bekledik…", '"{v} yıl oldu." dedi.', "“{v} sene!” diye ekledi.",
           "geçen süre: {v} yıl.", "{v} yıl mı?", "{v} yıldır buradayım.", "{v} senedir görüşmüyoruz.",
           "kaç yıl oldu? {v} yıl.", "{v} yıl önce bu köye gelmişti.", '"{v} yıl sonra yine buluşuruz," dedi.',
           "tam {v} yıl sürdü.", "{v} yıldır aynı işte çalışıyor.", "{v} sene sonra hepsi değişmişti.",
           "{v} yıl önce bu sokak çamurdu…", "{v} yıl bu kadar çabuk geçer mi?"):
    ekle("D5", "yil", _m)
for _m in ("{v} kumaş kaldı.", "{v} yol var!", "{v} {mi}", '"{v} yeter." dedi.', "“{v} kaldı…” dedi.", "ölçüsü: {v}.",
           'notta: "{v}" yazıyor.', "{v} daha yürümemiz lazım.", "{v} uzunluğunda bir ip aldım.",
           "{v} ötede bir çeşme vardı.", "bahçenin boyu {v}.", "{v} kadar gitti."):
    ekle("D5", "olcu", _m)
for _m in ("{v} kişi geldi.", "{v} dakika sürdü!", '"{v} kişi var." dedi.', "“{v} dakika!” diye seslendi.",
           "tahmini: {v} kişi.", "{v} kişi mi?", "{v} gün sonra döner.", "{v} adım ileride durdu.",
           "{v} gündür yağmur yağıyor.", '"{v} dakika bekleyin," dedi.', "{v} kişi daha gelecek…", "{v} saat uyudu."):
    ekle("D5", "aralik", _m)
for _m in ("{v} benim elbette…", "{v} burada!", '"{v} benim." dedi.', "{v} kayıp mı?", "“{v} kaldı.” dedi.",
           "{v} bile yetmedi…", "{v} bize yeter.", "{v} sana kalsın.", '"{v} yeterli değil." dedi.',
           "{v} çoktan bitmişti.", "bana {v} lazım.", "{v} yarın gelecek."):
    ekle("D5", "iyelik", _m)


# ---------------------------------------------------------------- D6
D6_SAAT_ARALIGI = {"öğleden sonra": (1, 6), "sabah": (6, 11), "akşam": (5, 11), "bu akşam": (5, 11),
                   "yarın sabah": (6, 11), "yarın akşam": (5, 11)}
D6_GELECEK = {"yarın", "yarın sabah", "yarın akşam"}
for _z in ZAMANLAR:
    for _eylem, _ek in (("gelin", "bulunma"), ("buluşalım", "bulunma"), ("görüşürüz", "bulunma"),
                       ("sonra gel", "ayrilma"), ("kadar bekleyelim", "yonelme"),
                       ("başlıyoruz", "bulunma"), ("toplanalım", "bulunma"), ("kalkıyoruz", "bulunma"),
                       ("sonra ararım", "ayrilma"), ("kadar uyuyacağım", "yonelme")):
        ekle("D6", "zaman", _z + " {v} " + _eylem, _ek)
    gelecek = ("ona söylerim", "onu çağırırız", "onunla konuşurum", "ondan haber alırım")
    gecmis = ("ona söyledim", "onu gördüm", "ondan haber aldım", "onunla konuştum", "yedi ve çıktı")
    _havuz = gelecek if _z in D6_GELECEK else gelecek + gecmis
    # Her zaman sözcüğü beş olumsuz kalıbı taşır; kalıplar sözcükler arasında dönerek dağılır.
    _k = ZAMANLAR.index(_z)
    for _neg in [_havuz[(_k + j) % len(_havuz)] for j in range(min(5, len(_havuz)))]:
        ekle("D6", "negatif", _z + " " + _neg)
        ekle("D6", "negatif", _z + " " + _neg + ", {kapanis}")
for _saat in ("saat", "saat henüz", "duvardaki saat", "salondaki saat", "eski saat", "kolumdaki saat",
              "mutfaktaki saat", "odadaki saat", "istasyondaki saat", "cebimdeki saat"):
    for _ek in ("di", "mis", "dir"):
        ekle("D6", "yuklem", _saat + " {v}", _ek)
for _metin in ("toplantı {v}", "ders {v}", "randevu {v}", "buluşma {v}", "kalkış {v}", "başlangıç {v}"):
    ekle("D6", "yuklem", _metin, "deymis")


# ---------------------------------------------------------------- D7
D7_EK_GOVDE = {
    "m": ("{v} var", "cebimde {v} kaldı", "{v} olsa yeter", "bugün yalnız {v} var"),
    "n": ("{v} var mı", "cebinde {v} kaldı mı", "{v} olsa ne alırsın", "yalnız {v} mı var"),
    "si": ("{v} kaldı", "{v} vardı", "cebinde {v} var", "{v} bile yokmuş"),
    "miz": ("{v} var", "{v} kaldı", "yalnız {v} var", "{v} olsa yeter"),
    "niz": ("{v} var mı", "{v} kaldı mı", "bugün {v} var mı", "{v} olsa ne yaparsınız"),
    "sini": ("{v} peşin aldı", "{v} cebine koydu", "{v} bana verdi", "{v} geri istedi"),
    "dir": ("borcun {v}", "fiyatı {v}", "toplam {v}", "ücreti {v}"),
    "di": ("fiyatı {v}", "ücreti {v}", "o zaman {v}", "borcum {v}"),
    "mis": ("fiyatı {v}", "borcu {v}", "ücreti {v}", "meğer toplam {v}"),
    "idi": ("fiyatı {v}", "borcu {v}", "ücreti {v}", "o gün toplam {v}"),
}
for _ek, _lst in D7_EK_GOVDE.items():
    for _metin in _lst:
        ekle("D7", "para", _metin, _ek)
for _birim in ("para", "okka", "arşın", "dönüm", "mecidiye", "altın"):
    for _metin in ("{v} {birim}", "defterde {v} {birim} yazıyor", "{v} {birim} kaldı",
                   "{v} {birim} diye not düştü", "hesapta {v} {birim} görünüyor", "toplam {v} {birim} var"):
        ekle("D7", "eski", _metin.replace("{birim}", _birim), _birim)
D7_SAYILAR = (5, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 75, 80, 90, 100, 120, 150, 165, 175, 200, 250, 300)


# ---------------------------------------------------------------- D8
# (taşıyıcı, uyumlu öbekler): öbek taşıyıcıdaki ekin gerektirdiği çekimle verilir.
SIRALAR = ("ikinci", "üçüncü", "dördüncü", "beşinci", "altıncı", "yedinci", "sekizinci", "dokuzuncu")


def _sifat(ad: str, sirala=SIRALAR) -> tuple[str, ...]:
    return tuple(f"{o} {ad}" for o in sirala)


D8_SIFAT = (
    ("{v} de pencerenin önünde geçirdi", _sifat("uykusuz geceyi") + _sifat("soğuk geceyi")),
    ("{isim} {v} kitap okuyarak atlattı", _sifat("uykusuz geceyi") + _sifat("uzun geceyi")),
    ("hasta {v} inleyerek geçirdi", _sifat("uykusuz geceyi") + _sifat("karanlık geceyi")),
    ("ada {v} yine kuş sesleriyle karşıladı", _sifat("sessiz sabahı") + _sifat("sisli sabahı")),
    ("{isim} {v} bahçede çay içerek geçirdi", _sifat("sessiz sabahı") + _sifat("serin sabahı")),
    ("gezi boyunca {v} da yürüyerek gezdik", _sifat("büyük şehri", SIRALAR[:5]) + _sifat("eski şehri", SIRALAR[:5])),
    ("{isim} {v} uzaktan seyretti", _sifat("büyük şehri", SIRALAR[:5]) + _sifat("güzel şehri", SIRALAR[:5])),
    ("{isim} {v} hiç unutmadı", _sifat("uzun yolculuğu") + _sifat("zor yolculuğu")),
    ("o yıl {v} trenle yaptık", _sifat("uzun yolculuğu") + _sifat("güzel yolculuğu")),
    ("öğrenci {v} da çözemedi", _sifat("zor soruyu") + _sifat("karışık soruyu")),
    ("{v} hiç kimse cevaplayamadı", _sifat("zor soruyu") + _sifat("uzun soruyu")),
)
# Unvan öbekleri: (ad, yalın, ile, belirtme, yönelme) çekimleri el ile yazılmıştır.
UNVANLAR = {"kaptan": ("kaptan", "kaptanla", "kaptanı", "kaptana"), "subay": ("subay", "subayla", "subayı", "subaya"),
            "müdür": ("müdür", "müdürle", "müdürü", "müdüre"), "kâtip": ("kâtip", "kâtiple", "kâtibi", "kâtibe"),
            "başkan": ("başkan", "başkanla", "başkanı", "başkana"),
            "mühendis": ("mühendis", "mühendisle", "mühendisi", "mühendise")}


def _unvan(bicim: int, siralar=("birinci", "ikinci", "üçüncü"), adlar=tuple(UNVANLAR)) -> tuple[str, ...]:
    return tuple(f"{o} {UNVANLAR[a][bicim]}" for o in siralar for a in adlar)


D8_UNVAN = (
    ("gemide {v} konuştum", _unvan(1, adlar=("kaptan", "subay", "mühendis"))),
    ("kamarada {v} bekliyorduk", _unvan(2, adlar=("kaptan", "subay", "mühendis"))),
    ("kapıdan {v} girdi", _unvan(0, adlar=("kaptan", "subay", "mühendis"))),
    ("dün akşam {v} bizi yemeğe çağırdı", _unvan(0, adlar=("kaptan", "subay", "mühendis"))),
    ("{v} dosyayı imzaladı", _unvan(0, adlar=("müdür", "kâtip", "başkan"))),
    ("dilekçeyi {v} teslim ettik", _unvan(3, adlar=("müdür", "kâtip", "başkan"))),
    ("{isim} {v} selam verdi", _unvan(3)),
    ("{v} haber getirdi", _unvan(0)),
    ("toplantıyı {v} yönetti", _unvan(0, adlar=("müdür", "başkan", "mühendis"))),
    ("{isim} {v} tanıştı", _unvan(1)),
)
D8_SIRA = (
    ("{v} boş bırakılmış", ("kat", "sayfa", "soru", "madde", "bölüm")),
    ("{v} geçersiz sayılacak", ("madde", "soru", "bölüm")),
    ("raporda {v} eksik", ("madde", "bölüm", "sayfa")),
    ("{v} bu hafta açılacak", ("kat", "sınıf", "bölüm")),
    ("{isim} {v} tek başına temizledi", ("kat", "sınıf")),
    ("bence {v} en ilginç olanıydı", ("bölüm", "soru", "madde")),
    ("{v} yanlış numaralanmış", ("sayfa", "madde", "soru", "bölüm")),
    ("sınav kâğıdında {v} çok zordu", ("soru",)),
)
D8_YASLIK = ("karşıdan {v} geliyordu", "kapıda {v} bekliyordu", "bankta {v} oturuyordu", "mağazaya {v} girdi",
             "{v} bastonuna dayanarak yürüdü", "pencerenin önünde {v} duruyordu")
D8_NESNELIK = ("raftan {v} aldım", "{isim} bana {v} uzattı", "dolapta {v} duruyordu", "bakkaldan {v} istedik",
               "masanın üstüne {v} bıraktı", "çantadan {v} çıkardı")
D8_YUZDELIK = ("mağaza {v} indirim ilan etti", "maaşlara {v} zam yapıldı", "fiyatlarda {v} artış bekleniyor",
               "bankalar {v} kesinti yaptı", "{v} bir indirimden yararlandık")
_ONAR = ("onar", "yirmişer", "otuzar", "kırkar", "ellişer", "altmışar", "yetmişer", "seksener", "doksanar", "yüzer")
D8_ULESTIRME = (
    ("hepsine {v} verdi", tuple(f"{x} lira" for x in _ONAR) + ("beşer lira",)),
    ("çocuklara {v} dağıttı", tuple(f"{x} lira" for x in _ONAR[:6]) + tuple(f"{x} kuruş" for x in _ONAR[:6])),
    ("karpuzları {v} sattı", ("ellişer kuruşa", "altmışar kuruşa", "yüzer liraya", "onar liraya", "yirmişer liraya",
                              "otuzar liraya", "kırkar kuruşa", "yetmişer kuruşa")),
    ("çocuklar {v} dondurma aldı", ("ellişer kuruşla", "altmışar kuruşla", "yirmişer kuruşla", "kırkar kuruşla",
                                   "yetmişer kuruşla", "otuzar kuruşla")),
    ("öğrenciler {v} sıraya girdi", ("ikişer ikişer", "üçer üçer", "beşer beşer", "dörder dörder", "altışar altışar")),
    ("{v} yürüyerek bahçeye çıktılar", ("ikişer ikişer", "üçer üçer", "beşer beşer", "dörder dörder")),
    ("sıralar {v} dizilmişti", ("dörder dörder", "altışar altışar", "yedişer yedişer", "sekizer sekizer")),
    ("masaya {v} bardak koydu", ("üçer", "beşer", "dörder", "ikişer", "altışar")),
    ("her yarışmacıya {v} kitap verildi", ("ikişer", "üçer", "beşer", "dörder")),
    ("{isim} kasadan {v} aldı", ("onar lira", "ellişer lira", "yüzer lira", "yirmişer lira")),
)
for _tur, _tablo in (("sifat", D8_SIFAT), ("unvan", D8_UNVAN), ("sira", D8_SIRA), ("ulestirme", D8_ULESTIRME)):
    for _m, _ayar in _tablo:
        ekle("D8", _tur, _m, "|".join(_ayar))
for _m in D8_YASLIK:
    ekle("D8", "yaslik", _m)
for _m in D8_NESNELIK:
    ekle("D8", "nesnelik", _m)
for _m in D8_YUZDELIK:
    ekle("D8", "yuzdelik", _m)
for _tur in ("sifat", "unvan", "sira", "yaslik", "nesnelik", "yuzdelik", "ulestirme"):
    ekle("D8", _tur, "{v}")
D8_UST = ('metinde "{v}" sözü geçiyor', 'notta "{v}" yazıyordu', 'sözlükte "{v}" örneğini gördüm',
          'yazar "{v}" demiş')
for _tur in ("sifat", "sira", "nesnelik", "ulestirme", "yaslik"):
    for _m in D8_UST:
        ekle_ust("D8", _tur, _m)


def sablon_bolumleri(seed: int) -> dict[str, dict[str, list[Sablon]]]:
    """%20 test, %8 validation; aynı taşıyıcı bütün karşıt türleriyle aynı bölümdedir."""
    sonuc = {b: {o: [] for o in SABLONLAR} for b in BOLUMLER}
    ayrilmis = ornekler(govdeler=True)
    for o, lst in SABLONLAR.items():
        zorunlu_train = {s.metin for s in lst if lower_tr(s.metin) in ayrilmis[o]}
        aday = sorted({s.metin for s in lst} - zorunlu_train)
        random.Random(f"{seed}-{o}-bol").shuffle(aday)
        nt = max(1, round(len(aday) * .20))
        nv = max(1, round(len(aday) * .08))
        for b, parca in (("test", aday[:nt]), ("validation", aday[nt:nt + nv]), ("train", aday[nt + nv:])):
            metinler = set(parca)
            if b == "train":
                metinler |= zorunlu_train
            sonuc[b][o] = [s for s in lst if s.metin in metinler]
    return sonuc


def _sabit(t: str) -> V.Varlik:
    return V.Varlik(t, t, "negatif_kalip")


def soru_eki(sozcuk: str) -> str:
    """Soru eki söylenen son sözcüğün son ünlüsüne uyar."""
    u = son_unlu(sozcuk)
    return {"a": "mı", "ı": "mı", "e": "mi", "i": "mi", "o": "mu", "u": "mu", "ö": "mü", "ü": "mü"}[u]


def d5_sayi(rng: random.Random, tur: str, sb_metin: str) -> int:
    if tur == "yas":
        return rng.randint(10, 95)
    if tur == "yil":
        return rng.randint(10, 80)
    while True:
        # İki basamaklılar (onluk, onluk + birlik) cümle başında da çoğunluktadır.
        n = rng.randint(10, 99) if rng.random() < .55 else rng.randint(100, 999)
        # `onu`, `yüzü` başka sözcükle (zamir, surat) karıştığı için iyelikte alınmaz.
        if tur == "iyelik" and (n == 10 or n % 100 == 0):
            continue
        return n


def d3_slot(sb: Sablon, rng: random.Random) -> V.Varlik:
    t = sb.tur
    if t == "madeni":
        if rng.random() < .5:
            p = para(rng.choice((5, 10, 25, 50)), rng.choice((None, "lik")), True)
        else:
            p = para(rng.choice((5, 10, 20, 50, 100)), "lik")
        on = rng.choice(("bir ", "bir ", "iki tane ", "üç tane ", "bir tane "))
        return V.Varlik(on + p.yazili, on + p.sozlu, "para")
    if t.startswith("boy"):
        p = boy(rng.randint(50, 99))
        son = {"boy_sifat": " boyunda",
               "boy_ad": rng.choice((" boyundaki adam", " boyundaki kadın", " boyundaki genç", " boyundaki çocuk")),
               "boy_yuklem": rng.choice((" boyundaydı", " boyundaymış"))}[t]
        return V.Varlik(p.yazili + son, p.sozlu + son, p.kategori)
    if t in {"aralik_sure", "aralik_uzun"}:
        uzun = t == "aralik_uzun"
        if rng.random() < .55:
            a = rng.randint(1, 4)
            return aralik(a, a + 1, rng.choice(("ay", "hafta", "gün")) if uzun else "saat", True)
        a, b = rng.choice(((5, 10), (10, 15), (15, 20), (20, 30), (30, 40), (40, 50)))
        return aralik(a, b, "gün" if uzun else "dakika")
    if t == "aralik_kilo":
        a = rng.randint(1, 4)
        return aralik(a, a + 1, "kg", True)
    if t == "aralik_kisi":
        a, b = rng.choice(((5, 10), (10, 15), (15, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (80, 90)))
        return aralik(a, b, "kişi")
    if t.startswith("yaklasik"):
        # `bir` + sayı yalnız onluklar ve yaygın yarım onluklarla (bir yüz ... üretilmez).
        if t == "yaklasik_zaman":
            birim, aday = rng.choice((("dakika sonra", (10, 15, 20, 25, 30, 40, 45, 50)),
                                      ("gün sonra", (10, 15, 20, 30, 40))))
        elif t == "yaklasik_kisi":
            birim, aday = "kişi kadar", (10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90)
        else:
            birim, aday = "adım ileride", (10, 15, 20, 30, 40, 50)
        p = sayi(rng.choice(aday))
        return V.Varlik(f"bir {p.yazili} {birim}", f"bir {p.sozlu} {birim}", "kardinal")
    once = rng.choice(("her biri ", "ikisi de ", "birer tane ")) if t == "paylasim_sat" else "hiçbiri "
    p = para(rng.randint(2, 9), "ayrilma")
    return V.Varlik(once + p.yazili, once + p.sozlu, "para")


def d4_slot(sb: Sablon, rng: random.Random, i: int) -> V.Varlik:
    if sb.tur == "sure":
        return bilesik(rng.randint(1, 4), rng.choice((5, 10, 15, 20, 30, 45)))
    if sb.tur == "sayma":
        return _sabit(rng.choice(("beş, dört, üç, iki…", "dokuz, sekiz, yedi, altı…", "bir, iki, üç, dört…")))
    if i % 5 < 3:
        return sayi(rng.randint(1, 9), kucuk=True)
    ust = D4_UST.get(sb.ayar, 200)
    return sayi(rng.choice([n for n in D4_ADAY if n <= ust and (n >= 10)]), kucuk=True)


def d6_slot(sb: Sablon, rng: random.Random) -> V.Varlik:
    if sb.tur == "negatif":
        return _sabit("")
    ek = rng.choice(sb.ayar.split("|"))
    lo, hi = D6_SAAT_ARALIGI.get(sb.metin.split(" {v}")[0], (1, 12))
    # `birden`, `ondan`, `ona` sayıdan çok sözcük okunur: bu eklerle saat verilmez.
    aday = [n for n in range(lo, hi + 1)
            if not (ek == "ayrilma" and n in (1, 10)) and not (ek == "yonelme" and n == 10)]
    p = sayi(rng.choice(aday), ek)
    return V.Varlik(p.yazili, p.sozlu, "saat")


def d7_slot(sb: Sablon, rng: random.Random) -> V.Varlik:
    n = rng.choice(D7_SAYILAR)
    if sb.tur == "eski":
        return sayi(n)
    ek = rng.choice(sb.ayar.split("|"))
    if ek == "idi":
        p = para(n)
        return V.Varlik(p.yazili + " idi", p.sozlu + " idi", "para")
    kurus = rng.random() < .25
    if kurus:
        # Kuruş 100'ün altında söylenir; üstü liraya döner.
        n = rng.choice([x for x in D7_SAYILAR if x < 100])
    return para(n if rng.random() < .7 else rng.randint(2, 9), ek, kurus)


def d8_slot(sb: Sablon, rng: random.Random) -> V.Varlik:
    t = sb.tur
    secenek = [x for x in sb.ayar.split("|") if x]
    if t in {"sifat", "unvan", "ulestirme"}:
        if secenek:
            return _sabit(rng.choice(secenek))
        havuz = {"sifat": [x for _, a in D8_SIFAT for x in a], "unvan": [x for _, a in D8_UNVAN for x in a],
                 "ulestirme": [x for _, a in D8_ULESTIRME for x in a]}[t]
        return _sabit(rng.choice(havuz))
    if t == "sira":
        ad = rng.choice(secenek or ["kat", "madde", "sınıf", "sayfa", "bölüm", "soru"])
        n = rng.randint(2 if ad == "sınıf" else 1, 20)
        p = V.kur_sira(n)
        return V.Varlik(p.yazili + " " + ad, p.sozlu + " " + ad, "sira")
    if t == "yuzdelik":
        return V.kur_yuzde(rng.choice((10, 15, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90)), ek="lik")
    if t == "yaslik":
        n = rng.choice((40, 50, 60, 70, 80, 90))
        ad = rng.choice((" bir adam", " bir kadın", " bir ihtiyar", " kadın", " adam", " ihtiyar"))
        if sb.metin == "{v}":
            ad = rng.choice((ad, ""))
        return _sabit(inflect(S.sayi_oku(n), "lik")[0] + ad)
    n = rng.choice((10, 12, 15, 20, 24, 25, 30, 40, 50, 60, 70, 80, 90, 100))
    p = sayi(n, "lik")
    son = rng.choice((" bir kutu", " bir paket", " bir şişe", " bir kasa", " bir torba"))
    return V.Varlik(p.yazili + son, p.sozlu + son, "kardinal")


def slot(sb: Sablon, rng: random.Random, i: int) -> V.Varlik:
    """Sayı değerleri önce yazılı belirtece, sonra sözlü girdiye dönüşür."""
    if sb.olgu == "D3":
        return d3_slot(sb, rng)
    if sb.olgu == "D4":
        return d4_slot(sb, rng, i)
    if sb.olgu == "D5":
        n = d5_sayi(rng, sb.tur, sb.metin)
        if sb.tur == "para":
            return para(n)
        if sb.tur == "olcu":
            return V.kur_olcu(n, birim="m")
        if sb.tur == "aralik":
            a, b = rng.choice(((5, 10), (10, 15), (20, 30), (30, 40), (40, 50), (60, 70)))
            return V.Varlik(f"{a}-{b}", S.sayi_oku(a) + " " + S.sayi_oku(b), "aralik")
        return sayi(n, "iyelik3" if sb.tur == "iyelik" else None)
    if sb.olgu == "D6":
        return d6_slot(sb, rng)
    if sb.olgu == "D7":
        return d7_slot(sb, rng)
    return d8_slot(sb, rng)


SON_ISARETLER = (".", "!", "?", "…", '"', "”")
SORU_EKLERI = {"mı", "mi", "mu", "mü"}


def render(sb: Sablon, rng: random.Random, i: int, noktalama: bool | None = None) -> dict:
    """Taşıyıcı bir kez kurulur; girdi ve hedef yalnız sayı öbeğinde ayrılır."""
    p = slot(sb, rng, i)
    govde = sb.metin.format(v="§", mi="¶", isim=rng.choice(ISIMLER),
                           kapanis=rng.choice(("dedi arkadaşım", "diye anlattı annem", "diye duydum",
                                              "dedi komşumuz", "diye aktardı", "demişti annem")))
    if sb.olgu == "D5":
        # D5 her zaman noktalamalıdır; noktalama girdide de hedefte de aynen kalır.
        noktalama = True
    elif sb.metin in UST_DIL:
        # Tırnak, üst-dil taşıyıcıda anlamın parçasıdır; düz kipte de korunur.
        noktalama = True
    else:
        noktalama = (i % 2 == 0) if noktalama is None else noktalama
    if noktalama:
        govde = ilk_harfi_buyut(govde)
        if not govde.endswith(SON_ISARETLER):
            sozc = sozcukler(govde)
            govde += "?" if govde.endswith("¶") or (sozc and sozc[-1] in SORU_EKLERI) else "."
    else:
        # Düz kip: noktalama ve büyük harf taşıyıcıdan kalkar, sayı öbeğine dokunulmaz.
        govde = lower_tr(re.sub(r"[^\w\s§¶]", "", govde))
    ozel = ilk_harfi_buyut(p.sozlu)
    bas = govde.find("§")
    onek = govde[:bas] if bas >= 0 else govde
    buyut = noktalama and (onek == "" or (sb.olgu in {"D4", "D5"} and onek.endswith(('"', "“"))) or
                           re.search(r'[.!?…]["”]?\s+["“]?$', onek) is not None)
    g = govde.replace("§", ozel if buyut else p.sozlu)
    # Büyük harf iki tarafta da aynıdır (`Bir elli kuruş` / `Bir 50 kuruş`; rakamda etkisiz).
    h = govde.replace("§", ilk_harfi_buyut(p.yazili) if buyut else p.yazili)
    if sb.olgu == "D5" and "¶" in govde:
        # Soru eki ayrı sözcüktür: hedefte girdideki haliyle aynen kalır (`lira mı` → `TL mı`).
        ek = soru_eki(p.sozlu)
        g, h = g.replace("¶", ek), h.replace("¶", ek)
    return {"girdi": g, "hedef": h, "kategori": p.kategori if g != h else "negatif_kalip", "sablon": sb.id}


def cumle(kalip: str, p: V.Varlik, olgu: str, no: int) -> dict:
    """El ile etiket yok: aynı hedef taşıyıcısına yazılı varlık ve onun TN'si yerleşir."""
    g = kalip.format(v=p.sozlu)
    h = kalip.format(v=p.yazili)
    return {"girdi": g, "hedef": h, "kategori": p.kategori if g != h else "negatif_kalip",
            "sablon": f"v3d-{olgu.lower()}-ornek-{no:03d}"}


def ornekler(govdeler: bool = False) -> dict:
    """Şartnamedeki sınır örnekleri de aynı sözlüleştiricilerden elde edilir."""
    s: dict[str, list[dict]] = {f"D{i}": [] for i in range(3, 9)}
    kaliplar = {o: set() for o in s}

    def koy(o, kalip, p):
        kaliplar[o].add(lower_tr(kalip))
        if o == "D6" and p.yazili != p.sozlu:
            p = V.Varlik(p.yazili, p.sozlu, "saat")
        s[o].append(cumle(kalip, p, o, len(s[o])))

    koy("D3", "bir {v}", para(50, kurus=True))
    koy("D3", "bir {v}", para(25, "lik", True))
    koy("D3", "bir {v} çıkardı", para(100, "lik"))
    koy("D3", "iki tane {v}", para(50, "lik", True))
    for n, son in ((50, "boyunda"), (75, "boyunda"), (80, "boyundaki adam")):
        koy("D3", "{v} " + son, boy(n))
    for a, b, birim in ((1, 2, "saat"), (2, 3, "kg"), (1, 2, "ay")):
        koy("D3", "{v}", aralik(a, b, birim, True))
    koy("D3", "bir {v} dakika sonra", sayi(10))
    koy("D3", "bir {v} kişi kadar", sayi(20))
    koy("D3", "{v}", aralik(5, 10, "dakika"))
    koy("D3", "{v}", aralik(10, 15, "kişi"))
    koy("D3", "her biri {v}", para(3, "ayrilma"))
    for n, kalip in ((12, "{v} kişi geldi ama kimse konuşmak istemedi"),
                     (40, "{v} yaşında adam yavaşça ayağa kalkıp dışarı çıktı"),
                     (20, "{v} senedir burada oturuyorum ama kimseyi tanımıyorum")):
        koy("D4", kalip, sayi(n, kucuk=True))
    koy("D4", "{v} kişi iki gündür çatıda uğraşıyordu", sayi(8, kucuk=True))
    koy("D4", "raporda {v} hata var ama yine kontrol edelim", sayi(0, kucuk=True))
    for n, kalip in ((4, "{v} katlı otelin önünde durup biraz bekledik"),
                     (6, "{v} kişilik orkestra bütün gece prova yaptı"),
                     (3, "{v} mektubunu cevapsız bıraktı ve sessizce uzaklaştı"),
                     (2, "{v} gece önce kapımızı çalıp yardım istedi"),
                     (9, "yolculuk {v} saat sürdü sonunda eve vardık"),
                     (8, "{v} yaşında bir çocuk kapının önünde bekliyordu"),
                     (7, "bu evde {v} sene oturdum sonra taşındım")):
        koy("D4", kalip, sayi(n, kucuk=True))
    koy("D4", "{v} sürdü ve sonunda hepimiz eve döndük", bilesik(2, 15))
    for kalip, p in (
            ('"{v} yaşında adam böyle yapar mı?" dedi.', sayi(40)),
            ("{v} aylık…", para(70)), ("Şimdi ne istersin? {v} mi?", sayi(45)),
            ("{v} benim elbette…", sayi(150, "iyelik3")),
            ('Yanındakine: "{v} adım var." dedi.', sayi(50)), ("{v}.", sayi(164)), ("{v}.", sayi(218))):
        # Büyük harf yalnız varlığa uygulanır; komşu metin aynen kalır.
        p = V.Varlik(p.yazili, ilk_harfi_buyut(p.sozlu), p.kategori)
        koy("D5", kalip, p)
    for kalip, n, ek in (("Yarın {v} gelin.", 9, "bulunma"), ("akşam {v} buluşalım", 7, "bulunma"),
                          ("Saat henüz {v}.", 4, "di"), ("saat {v}", 5, "di"),
                          ("saat {v}", 12, "di"), ("toplantı {v}", 3, "deymis")):
        koy("D6", kalip, sayi(n, ek))
    for t in ("yarın ona söylerim", "akşam onu gördüm", "sabah yedi ve çıktı"):
        koy("D6", "{v}", _sabit(t))
    for kalip, n, ek, kr in (("{v} var", 150, "m", False), ("{v} peşin aldı", 50, "sini", False),
                            ("borcun {v}", 165, "dir", False), ("{v} var", 35, "m", True),
                            ("{v} kaldı", 10, "si", False), ("{v}", 5, "miz", False),
                            ("fiyatı {v}", 20, "di", False)):
        koy("D7", kalip, para(n, ek, kr))
    # Birimsiz 'lira idi' dönüşümü SPEC §3'le çelişir; burada sayı bağlamı vardır.
    p = para(20)
    koy("D7", "{v} idi", p)
    for n, b in ((90, "para"), (40, "okka"), (15, "arşın"), (20, "dönüm"), (50, "mecidiye"), (30, "altın")):
        koy("D7", "{v} " + b, sayi(n))
    for t in ("üçüncü uykusuz geceyi", "ikinci büyük şehri", "ikinci kaptan", "birinci subay", "üçüncü kâtip",
              "ikinci müdür", "altmışlık bir adam", "ellilik kadın", "yetmişlik ihtiyar", "kırklık",
              "ellişer kuruşa", "altmışar kuruşla", "ikişer ikişer", "onar lira"):
        koy("D8", "{v}", _sabit(t))
    for n, b in ((3, "kat"), (2, "madde")):
        koy("D8", "{v} " + b, V.kur_sira(n))
    koy("D8", "{v} bir kutu", sayi(60, "lik"))
    koy("D8", "{v}", V.kur_yuzde(50, ek="lik"))
    return kaliplar if govdeler else s


# Test için kullanılan taşıyıcılar eğitimdekilerden metin olarak da farklıdır.
DEYIM_TASIYICILARI = {
    "train": ("{v}", 'dedem hep "{v}" derdi', 'ne demişler: "{v}"', '"{v}" diye bir söz var',
              'annem konuşurken "{v}" dedi', 'bana göre "{v}" sözü yerinde', 'eski defterde "{v}" yazıyor',
              'komşumuz sohbet arasında "{v}" diye ekledi'),
    "validation": ("{v}", 'teyzem hep "{v}" der', 'radyoda "{v}" sözünü duydum',
                   '"{v}" sözünü burada hatırladım', 'bu duruma "{v}" derler',
                   'kitabın kenarında "{v}" yazılıydı', 'öğrenci "{v}" sözünü seçti', 'usta "{v}" diyerek gülümsedi'),
    "test": ("{v}", 'ninem eskiden "{v}" derdi', 'sohbet uzayınca "{v}" sözü aklıma geldi',
             '"{v}" sözünü babamdan öğrendim', 'anlatıcı tam burada "{v}" dedi',
             'kardeşim kulağıma "{v}" diye fısıldadı', 'yol arkadaşımın sözü şuydu: "{v}"',
             'romanda birden "{v}" sözüyle karşılaştım'),
}


def soz_bolumleri(seed: int) -> dict[str, list[tuple[int, str]]]:
    aday = list(enumerate(SOZLER))
    random.Random(f"{seed}-sozler").shuffle(aday)
    nt, nv = (len(aday) * 15 + 99) // 100, round(len(aday) * .06)
    return {"test": aday[:nt], "validation": aday[nt:nt + nv], "train": aday[nt + nv:]}


def ilk_sozcuk(t: str) -> str:
    tk = sozcukler(t)
    return tk[0] if tk else ""


def uret_hepsi(seed: int = 3303, cv: Path = CV_YOLU, haric: Path = HARIC_YOLU) -> tuple[dict, dict]:
    dis = haric_yukle(haric)
    havuz, d1_sayim = d1_yukle(cv, dis, seed)
    sonuc = {b: [] for b in BOLUMLER}
    atilan = Counter()
    gorulen_girdi, gorulen_hedef = set(), set()
    sinir_ornekleri = ornekler()
    ayrilmis = {ozet(r["girdi"]) for lst in sinir_ornekleri.values() for r in lst}

    def kabul(b, r):
        if max(len(r[k].encode("utf-8")) for k in ("girdi", "hedef")) > BAYT_SINIRI:
            atilan["uzun"] += 1
            return False
        if ozet(r["girdi"]) in dis or ozet(r["hedef"]) in dis:
            atilan["haric"] += 1
            return False
        if r["girdi"] in gorulen_girdi or r["hedef"] in gorulen_hedef:
            atilan["yinelenen"] += 1
            return False
        gorulen_girdi.add(r["girdi"])
        gorulen_hedef.add(r["hedef"])
        sonuc[b].append(r)
        return True

    # Atasözleri önce kabul edilir: derlemde aynen geçen bir söz D2'den düşmez, D1'den düşer.
    sozler = soz_bolumleri(seed)
    for b in BOLUMLER:
        # Her söz yalın + taşıyıcı, özgün + düz; hiçbir söz kota yüzünden yarım kalmaz.
        for no, soz in sozler[b]:
            for ti, metin in enumerate(DEYIM_TASIYICILARI[b]):
                if ti == 0 and ozet(soz) in dis:
                    continue
                tam = metin.format(v=soz)
                ilk = re.search(r"[^\W\d_]", tam)
                if ilk:
                    j = ilk.start()
                    tam = tam[:j] + ilk_harfi_buyut(tam[j:])
                tam += "."
                for t in (tam, cv_duz(tam)):
                    kabul(b, {"girdi": t, "hedef": t, "kategori": "negatif_kalip",
                              "sablon": f"v3d-d2-{no:03d}-{ti:02d}"})

    d1_olcum = {}
    for b in BOLUMLER:
        bir_sayisi = zamir_sayisi = 0
        # Zamir önceliği; toplam bir ailesi (örtüşen zamirler dahil) en çok 3.000.
        limit = 3000 if b == "train" else 100000
        d1_say = 0
        for grup in ("zamir", "diger", "bir"):
            for oz, t in havuz[b][grup]:
                if oz in ayrilmis:
                    atilan["d1_sinir_ornegi"] += 1
                    continue
                bicimler = list(dict.fromkeys((t, cv_duz(t))))
                birli = any(w.startswith("bir") for w in sozcukler(t))
                if birli and bir_sayisi + len(bicimler) > limit:
                    continue
                for metin in bicimler:
                    r = {"girdi": metin, "hedef": metin, "kategori": "negatif_dogal", "sablon": "v3d-d1-" + oz}
                    if kabul(b, r):
                        d1_say += 1
                        bir_sayisi += int(birli)
                        zamir_sayisi += int(grup == "zamir")
        d1_olcum[b] = {"bir_ailesi": bir_sayisi, "zamir": zamir_sayisi}

    dagilim = sablon_bolumleri(seed)
    for b in BOLUMLER:
        ilkler = Counter(ilk_sozcuk(r["girdi"]) for r in sonuc[b] if olgu_of(r) == "D2")
        for o, ornek in sinir_ornekleri.items():
            # Sınır örnekleri eğitimde; testte ayrı taşıyıcılar kullanılır.
            if b == "train":
                for r in ornek:
                    if kabul(b, r):
                        ilkler[ilk_sozcuk(r["girdi"])] += 1
        for o in SABLONLAR:
            kota = KOTALAR[o] if b == "train" else max(150, round(KOTALAR[o] * (.08 if b == "validation" else .24)))
            hazir = sum(olgu_of(r) == o for r in sonuc[b])
            rng = random.Random(f"{seed}-{b}-{o}")
            sbler = list(dagilim[b][o])
            rng.shuffle(sbler)
            # D6 negatifleri en az %25; D4 karşıtları tüm taşıyıcılarda döner.
            ilk_limit = max(30, int((sum(KOTALAR[x] for x in SABLONLAR) +
                                    sum(olgu_of(r) == "D2" for r in sonuc[b])) *
                                   (1 if b == "train" else .28) * .048))
            i = 0
            while hazir < kota and i < kota * 250:
                sb = sbler[i % len(sbler)]
                r = render(sb, rng, i // len(sbler))
                i += 1
                ilk = ilk_sozcuk(r["girdi"])
                if ilkler[ilk] >= ilk_limit:
                    atilan["ilk_sozcuk"] += 1
                    continue
                if kabul(b, r):
                    hazir += 1
                    ilkler[ilk] += 1
            if hazir < kota:
                raise ValueError(f"{b}/{o} kotası dolmadı: {hazir}/{kota}")
        random.Random(f"{seed}-{b}-karistir").shuffle(sonuc[b])
    return sonuc, {"d1_havuz": {b: {g: len(x) for g, x in h.items()} for b, h in havuz.items()},
                   "d1": d1_olcum, "d1_elemesi": d1_sayim, "atilan": dict(atilan)}


def olcumler(satirlar: list[dict]) -> dict:
    rapor = {}
    for o in KOTALAR:
        s = [r for r in satirlar if olgu_of(r) == o]
        sb = Counter(r["sablon"] for r in s)
        ilk = Counter(ilk_sozcuk(r["girdi"]) for r in s)
        rapor[o] = {"satir": len(s), "sablon": len(sb),
                    "negatif_payi": sum(r["girdi"] == r["hedef"] for r in s) / max(1, len(s)),
                    "en_buyuk_sablon_payi": max(sb.values(), default=0) / max(1, len(s)),
                    "en_buyuk_ilk_sozcuk_payi": max(ilk.values(), default=0) / max(1, len(s))}
    s = [r for r in satirlar if olgu_of(r) != "D1"]
    sb, ilk = Counter(r["sablon"] for r in s), Counter(ilk_sozcuk(r["girdi"]) for r in s)
    rapor["genel"] = {"satir": len(satirlar), "d2_d8_sablon": len(sb),
                       "d2_d8_en_buyuk_sablon_payi": max(sb.values(), default=0) / max(1, len(s)),
                       "d2_d8_en_buyuk_ilk_sozcuk_payi": max(ilk.values(), default=0) / max(1, len(s)),
                       "negatif_payi": sum(r["girdi"] == r["hedef"] for r in satirlar) / max(1, len(satirlar))}
    return rapor


def ust_dil_payi(satirlar: list[dict], olgu: str) -> float:
    """Kalıbın kendisinden söz eden taşıyıcıların satır payı."""
    metin = {s.id: s.metin for s in SABLONLAR[olgu]}
    s = [r for r in satirlar if olgu_of(r) == olgu]
    return sum(metin.get(r["sablon"]) in UST_DIL for r in s) / max(1, len(s))


def d5_basamak_payi(satirlar: list[dict]) -> float:
    """Cümle başındaki (ya da tırnak sonrası) sayılar içinde iki basamaklıların payı."""
    bas = [r["hedef"] for r in satirlar if olgu_of(r) == "D5" and re.match(r'^["“]?\d', r["hedef"])]
    return sum(bool(re.match(r'^["“]?\d{2}(?!\d)', h)) for h in bas) / max(1, len(bas))


def esikler(sonuc: dict, ek: dict) -> dict:
    tr = sonuc["train"]
    m = olcumler(tr)
    g = m["genel"]
    e = {}

    def ekle_esik(ad, deger, alt=None, ust=None):
        e[ad] = {"deger": deger, "alt": alt, "ust": ust,
                 "gecti": (alt is None or deger >= alt) and (ust is None or deger <= ust)}

    for o, kota in KOTALAR.items():
        # D1 satırı derlemin elverdiği kadardır (SPEC: ~8.000); alt sınır 7.000.
        ekle_esik(o + "_satir", m[o]["satir"], 7000 if o == "D1" else kota * .8)
    ekle_esik("sablon", g["d2_d8_sablon"], 600)
    ekle_esik("sablon_en_cok", g["d2_d8_en_buyuk_sablon_payi"], ust=.01)
    ekle_esik("ilk_sozcuk_en_cok", g["d2_d8_en_buyuk_ilk_sozcuk_payi"], ust=.05)
    ekle_esik("negatif_payi", g["negatif_payi"], .55, .70)
    ekle_esik("D1_zamir", ek["d1"]["train"]["zamir"], 4500)
    ekle_esik("D1_bir", ek["d1"]["train"]["bir_ailesi"], ust=3000)
    d2 = [r for r in tr if olgu_of(r) == "D2"]
    ekle_esik("D2_soz", len({r["sablon"].split("-")[2] for r in d2}), 250)
    ekle_esik("D2_test_soz_payi", len(soz_bolumleri(ek["seed"])["test"]) / len(SOZLER), .15)
    d4 = [r for r in tr if olgu_of(r) == "D4"]
    ekle_esik("D4_pozitif", sum(r["girdi"] != r["hedef"] for r in d4) / len(d4), .30)
    ekle_esik("D4_ad", len({s.ayar for s in sablon_bolumleri(ek["seed"])["train"]["D4"] if s.tur == "ad"}), 60)
    ekle_esik("D4_6_18_sozcuk", sum(6 <= len(r["girdi"].split()) <= 18 for r in d4) / len(d4), .99)
    ekle_esik("D4_noktalama", sum(bool(re.search('[,"…]', r["girdi"])) for r in d4) / len(d4), .45, .60)
    d5 = [r for r in tr if olgu_of(r) == "D5"]
    ekle_esik("D5_sablon", len({r["sablon"] for r in d5}), 120)
    ekle_esik("D5_cumle_basi_iki_basamak", d5_basamak_payi(tr), .40)
    for o in ("D3", "D8"):
        ekle_esik(o + "_ust_dil", ust_dil_payi(tr, o), ust=.25)
    ekle_esik("D5_baslangic", sum(bool(re.match(r'^["“]?\d', r["hedef"])) for r in d5) / len(d5), .50)
    d6 = [r for r in tr if olgu_of(r) == "D6"]
    ekle_esik("D6_negatif", sum(r["girdi"] == r["hedef"] for r in d6) / len(d6), .25)
    for o in ("D1", "D2"):
        ekle_esik(o + "_negatif", m[o]["negatif_payi"], 1, 1)
    return e


def yaz(yol: Path, satirlar: list[dict]) -> None:
    with yol.open("w", encoding="utf-8", newline="\n") as f:
        for r in satirlar:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=3303)
    ap.add_argument("--cv", type=Path, default=CV_YOLU)
    ap.add_argument("--haric", type=Path, default=HARIC_YOLU)
    ap.add_argument("--out", type=Path, default=KOK / "data/v3")
    a = ap.parse_args(argv)
    sonuc, ek = uret_hepsi(a.seed, a.cv, a.haric)
    ek["seed"] = a.seed
    rapor = {"seed": a.seed, "bolumler": {b: olcumler(s) for b, s in sonuc.items()},
             "esikler": esikler(sonuc, ek), "uretim": ek,
             "uretilmeyen": ["Birimsiz 'lira idi → TL idi': SPEC §3 sayısız birim korumasıyla çelişir; yalnız sayılı üretilir.",
                             "D1 kapalı listesinin dışındaki çekimler ve bağlamı belirsiz on-/bir biçimleri alınmaz."]}
    a.out.mkdir(parents=True, exist_ok=True)
    for b, s in sonuc.items():
        yaz(a.out / f"d-{b}.jsonl", s)
    # Örnekler inceleme içindir; gözle okunduğu iddiası içermez.
    inceleme = {}
    for o in KOTALAR:
        aday = [r for r in sonuc["train"] if olgu_of(r) == o]
        inceleme[o] = random.Random(f"{a.seed}-inceleme-{o}").sample(aday, 40)
    (a.out / "d-inceleme.json").write_text(json.dumps(inceleme, ensure_ascii=False, indent=2), encoding="utf-8")
    (a.out / "d-rapor.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    return 0 if all(v["gecti"] for v in rapor["esikler"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
