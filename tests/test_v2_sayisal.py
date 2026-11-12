"""v2 A kaynağı (training/v2_sayisal.py) testleri: SPEC-v2 §A1–A8."""
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

import pytest  # noqa: E402

import v2_sayisal as A  # noqa: E402
from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.turkce import lower_tr  # noqa: E402


# ---------------------------------------------------------------- A1: iç sıfırlar

@pytest.mark.parametrize("n,sozlu,yazili", [
    (78_010_000, "yetmiş sekiz milyon on bin", "78.010.000"),
    (1_090, "bin doksan", "1.090"),
    (25_003, "yirmi beş bin üç", "25.003"),
    (12_062_000, "on iki milyon altmış iki bin", "12.062.000"),
    (1_005, "bin beş", "1.005"),
    (10_010, "on bin on", "10.010"),
    (300_007, "üç yüz bin yedi", "300.007"),
    (2_000_500, "iki milyon beş yüz", "2.000.500"),
    (40_000_040, "kırk milyon kırk", "40.000.040"),
    (1_001_001, "bir milyon bin bir", "1.001.001"),
])
def test_a1_ic_sifir_yazimi(n, sozlu, yazili):
    v = V.kur_buyuk_duz(n) if n >= 10**6 else V.kur_kardinal(n)
    assert (v.sozlu, v.yazili) == (sozlu, yazili)


def test_a1_para_kurus_ve_ek():
    v = V.kur_para(lira=1005, kurus=50)
    assert (v.sozlu, v.yazili) == ("bin beş lira elli kuruş", "1.005,50 TL")
    v = V.kur_para(lira=25003, ek="ayrilma")
    assert (v.sozlu, v.yazili) == ("yirmi beş bin üç liradan", "25.003 TL'den")
    v = V.kur_kardinal(77010, ek="belirtme")
    assert (v.sozlu, v.yazili) == ("yetmiş yedi bin onu", "77.010'u")


def test_a1_grup_tipleri():
    assert [A.grup_tipi(g) for g in (0, 5, 10, 40, 12, 99, 100, 505)] == list("ZABBCCNN")
    assert A.ic_gruplar(78_010_000) == [10, 0]
    assert A.ic_gruplar(1_005) == [5]
    assert A.ic_gruplar(999) == []


def test_a1_ornekleyici_her_zaman_ic_sifirli():
    rng = random.Random(5)
    A.CTX.sifirla()
    gorulen = Counter()
    for _ in range(400):
        n = A.sifirli_sayi(rng, rng.choice([0.05, 0.3, 1.0]), False)
        tipler = {A.grup_tipi(g) for g in A.ic_gruplar(n)}
        assert tipler & set("ZABC"), n
        gorulen |= Counter(tipler)
    assert {"Z", "A", "B", "C"} <= set(gorulen)


# ---------------------------------------------------------------- A2: telefon ve kod

def test_telefon_ayrisimlari_belirsiz():
    w = "sıfır beş yüz kırk yedi yüz altmış altı yirmi otuz".split()
    assert A.telefon_ayrisimlari(w) == ["05407662030", "05471662030"]
    assert len(A.telefon_ayrisimlari("sıfır beş yüz kırk yedi yüz altmış altı on beş yirmi".split())) == 2


def test_telefon_ayrisimlari_tek():
    r = "05321234567"
    for modlar in [("sayi",) * 4, ("rakam",) * 4, ("sayi", "rakam", "sayi", "rakam"), ("rakam", "sayi", "rakam", "sayi")]:
        w = S.telefon_kelimeleri(r, modlar)
        assert r in A.telefon_ayrisimlari(w), modlar
    # kesin tek ayrışımlı örnekler
    assert A.telefon_ayrisimlari(S.telefon_kelimeleri(r, ("rakam",) * 4)) == [r]
    assert A.telefon_ayrisimlari("sıfır beş üç iki yüz yirmi üç dört beş altı yedi".split()) == [r]
    assert A.telefon_ayrisimlari("artı doksan beş üç iki yüz yirmi üç kırk beş altmış yedi".split()) == [r]
    # SPEC'teki örnek satırın kendisi belirsizdir: 532 123 mü, 530 223 mü
    assert len(A.telefon_ayrisimlari("sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi".split())) == 2


def test_telefon_ayrisimlari_kalıba_uymayan_ve_ekli():
    assert A.telefon_ayrisimlari("iki bin yirmi altı".split()) == []
    assert A.telefon_ayrisimlari([]) == []
    # son sözcük ekli olabilir
    w = "sıfır beş üç iki yüz yirmi üç dört beş altı yedi".split()
    assert A.telefon_ayrisimlari(w[:-1] + ["yediden"]) == ["05321234567"]
    # sıfırlı gruplar: 0 yüz bir, 00 -> sıfır sıfır
    assert A.telefon_ayrisimlari("sıfır beş yüz otuz yüz bir sıfır yedi on".split()) == ["05301010710"]


def test_telefon_satiri_belirsiz():
    belirsiz = "sıfır beş yüz kırk yedi yüz altmış altı yirmi otuz"
    assert A.telefon_satiri_belirsiz("numaram " + belirsiz, "numaram 0547 166 20 30")
    assert A.telefon_satiri_belirsiz("Numaram " + belirsiz + " idi.", "Numaram 0540 766 20 30 idi.")
    # tek ayrışımlı
    v = V.kur_telefon("05321234567", ("rakam",) * 4)
    assert not A.telefon_satiri_belirsiz("numaram " + v.sozlu, "numaram " + v.yazili)
    # SPEC'teki 0532 123 45 67 (sayı sayı) örneği de belirsizdir: 532 123 / 530 223
    v = V.kur_telefon("05321234567")
    assert A.telefon_satiri_belirsiz("numaram " + v.sozlu, "numaram " + v.yazili)
    # ekli (son sözcük) ve +90
    v = V.kur_telefon("05321234567", ("rakam",) * 4, ek="ayrilma")
    assert not A.telefon_satiri_belirsiz(v.sozlu + " aradı", v.yazili + " aradı")
    v = V.kur_telefon("05471662030", ek="yonelme")
    assert A.telefon_satiri_belirsiz("mesaj attım " + v.sozlu, "mesaj attım " + v.yazili)
    # girdide zaten rakam / telefon yok
    assert not A.telefon_satiri_belirsiz("numaram 0547 166 20 30", "numaram 0547 166 20 30")
    assert not A.telefon_satiri_belirsiz("iki bin yirmi altı", "2026")
    # eski akıştaki gerçek belirsiz satır (beş yüz kırk yedi yüz altmış altı ...)
    g = "Yeni numaram sıfır beş yüz kırk yedi yüz altmış altı doksan sekiz doksan üç oldu."
    assert A.telefon_satiri_belirsiz(g, "Yeni numaram 0540 766 98 93 oldu.")


# ---------------------------------------------------------------- A3: aralık

@pytest.mark.parametrize("a,b,birim,sozlu,yazili", [
    (60, 75, None, "altmış yetmiş beş", "60-75"),
    (200, 250, None, "iki yüz iki yüz elli", "200-250"),
    (60, 65, None, "altmış altmış beş", "60-65"),
    (15, 20, None, "on beş yirmi", "15-20"),
    (100, 150, None, "yüz yüz elli", "100-150"),
    (1000, 1500, "TL", "bin bin beş yüz lira", "1.000-1.500 TL"),
])
def test_a3_ornekleri(a, b, birim, sozlu, yazili):
    v = A.kur_aralik2(a, b, birim)
    assert (v.sozlu, v.yazili) == (sozlu, yazili)
    assert A.iki_sayi_ayrisimlari(S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b)) == [(a, b)]


def test_a3_bir_gecen_aralik_uretilmez():
    rng = random.Random(3)
    for _ in range(300):
        a, b = A.aralik_cifti(rng)
        assert "bir" not in S.sayi_kelimeleri(a) + S.sayi_kelimeleri(b)
        assert a < b


# ---------------------------------------------------------------- A4: birim x ek

@pytest.mark.parametrize("birim,ek,sozlu,yazili", [
    ("GB", "ayrilma", "beş gigabayttan", "5 GB'tan"),
    ("MB", "ayrilma", "beş megabayttan", "5 MB'tan"),
    ("kW", "bulunma", "beş kilovatta", "5 kW'ta"),
    ("V", "ayrilma", "beş volttan", "5 V'tan"),
    ("L", "ayrilma", "beş litreden", "5 L'den"),
    ("mL", "yonelme", "beş mililitreye", "5 mL'ye"),
    ("m2", "lik", "beş metrekarelik", "5 m²'lik"),
    ("C", "bulunma", "beş derece santigratta", "5 °C'de"),
    ("GB", "belirtme", "beş gigabaytı", "5 GB'ı"),
    ("V", "vasita", "beş voltla", "5 V'la"),
])
def test_a4_birim_ek(birim, ek, sozlu, yazili):
    v = V.kur_olcu(5, "", birim, 0, ek=ek)
    assert (v.sozlu, v.yazili) == (sozlu, yazili)


def test_a4_ornekleyici_hucre_zorlama():
    rng = random.Random(1)
    A.CTX.sifirla()
    for u in A.A4_BIRIMLER:
        A.CTX.birim = u
        v = A.ornekle_a4(rng, "any", "ayrilma")
        assert v.yazili.split()[1].startswith(V.BIRIMLER[u][0]), (u, v.yazili)
    A.CTX.birim = None


# ---------------------------------------------------------------- A5: bileşik ölçü ve süre

@pytest.mark.parametrize("parcalar,sozlu,yazili", [
    ([(3, "kg"), (200, "g")], "üç kilo iki yüz gram", "3 kg 200 g"),
    ([(1, "m"), (80, "cm")], "bir metre seksen santim", "1 m 80 cm"),
    ([(2, "km"), (300, "m")], "iki kilometre üç yüz metre", "2 km 300 m"),
    ([(1, "L"), (250, "mL")], "bir litre iki yüz elli mililitre", "1 L 250 mL"),
    ([(2, "saat"), (15, "dakika")], "iki saat on beş dakika", "2 saat 15 dakika"),
    ([(1, "saat"), (45, "dakika"), (30, "saniye")], "bir saat kırk beş dakika otuz saniye", "1 saat 45 dakika 30 saniye"),
    ([(5, "dakika"), (20, "saniye")], "beş dakika yirmi saniye", "5 dakika 20 saniye"),
])
def test_a5_ornekleri(parcalar, sozlu, yazili):
    v = A.kur_bilesik(parcalar, soz_idx=[0] * len(parcalar))
    assert (v.sozlu, v.yazili) == (sozlu, yazili)


def test_a5_bilesik_ek_yalniz_son_birime():
    v = A.kur_bilesik([(3, "kg"), (200, "g")], "lik", [0, 0])
    assert (v.sozlu, v.yazili) == ("üç kilo iki yüz gramlık", "3 kg 200 g'lık")
    v = A.kur_bilesik([(2, "saat"), (15, "dakika")], "bulunma")
    assert (v.sozlu, v.yazili) == ("iki saat on beş dakikada", "2 saat 15 dakikada")
    v = A.kur_bilesik([(1, "m"), (80, "cm")], "ayrilma", [0, 0])
    assert v.yazili == "1 m 80 cm'den" and v.sozlu == "bir metre seksen santimden"
    v = A.kur_bilesik([(1, "kg"), (500, "g")], "yonelme", [1, 0])
    assert v.yazili == "1 kg 500 g'a" and v.sozlu == "bir kilogram beş yüz grama"


def test_a5_ornekleyici_hepsi_rakam():
    rng = random.Random(2)
    for zincir in A._ZINCIRLER:
        for _ in range(30):
            v = A.ornekle_bilesik(rng, zincir, None)
            assert len(v.yazili.split()) >= 4
            assert re.fullmatch(r"\d+ \D+( \d+ \D+)+", v.yazili), v.yazili


# ---------------------------------------------------------------- A6: yeni birimler

@pytest.mark.parametrize("birim,ek,sozlu,yazili", [
    ("mg", "ayrilma", "beş miligramdan", "5 mg'dan"),
    ("m3", "bulunma", "beş metreküpte", "5 m³'te"),
    ("km2", "lik", "beş kilometrekarelik", "5 km²'lik"),
    ("kwh", "bulunma", "beş kilovatsaatte", "5 kWh'te"),
    ("hz", "ayrilma", "beş hertzden", "5 Hz'den"),
    ("mhz", "yonelme", "beş megahertze", "5 MHz'e"),
    ("ton", "lik", "beş tonluk", "5 tonluk"),
    ("inc", "bulunma", "beş inçte", "5 inçte"),
    ("kalori", "belirtme", "beş kaloriyi", "5 kaloriyi"),
    ("hektar", "lik", "beş hektarlık", "5 hektarlık"),
    ("dakika", "bulunma", "beş dakikada", "5 dakikada"),
])
def test_a6_yeni_birim_ekleri(birim, ek, sozlu, yazili):
    v = A.kur_olcu2(5, "", birim, 0, ek=ek)
    assert (v.sozlu, v.yazili) == (sozlu, yazili)


def test_a6_kilovat_saat_iki_okunus():
    assert A.kur_olcu2(12, "", "kwh", 1).sozlu == "on iki kilovat saat"
    assert A.kur_olcu2(12, "", "kwh", 1).yazili == "12 kWh"
    assert A.kur_olcu2(12, "", "kwh", 1, ek="bulunma").sozlu == "on iki kilovat saatte"
    assert A.kur_olcu2(12, "", "kwh", 1, ek="lik").yazili == "12 kWh'lik"


# sözcük kipli birimler x ek: (bulunma, ayrilma, yonelme, belirtme, lik, vasita, ilgi); `saat` ince ünlülü istisnadır
_SOZCUK_TABLO = {
    "ton": "tonda tondan tona tonu tonluk tonla tonun",
    "inc": "inçte inçten inçe inçi inçlik inçle inçin",
    "kalori": "kaloride kaloriden kaloriye kaloriyi kalorilik kaloriyle kalorinin",
    "hektar": "hektarda hektardan hektara hektarı hektarlık hektarla hektarın",
    "donum": "dönümde dönümden dönüme dönümü dönümlük dönümle dönümün",
    "beygir": "beygirde beygirden beygire beygiri beygirlik beygirle beygirin",
    "piksel": "pikselde pikselden piksele pikseli piksellik pikselle pikselin",
    "karat": "karatta karattan karata karatı karatlık karatla karatın",
    "saat": "saatte saatten saate saati saatlik saatle saatin",
    "dakika": "dakikada dakikadan dakikaya dakikayı dakikalık dakikayla dakikanın",
    "saniye": "saniyede saniyeden saniyeye saniyeyi saniyelik saniyeyle saniyenin",
    "gun": "günde günden güne günü günlük günle günün",
    "hafta": "haftada haftadan haftaya haftayı haftalık haftayla haftanın",
    "ay": "ayda aydan aya ayı aylık ayla ayın",
    "yil": "yılda yıldan yıla yılı yıllık yılla yılın",
}
_EK_SIRASI = ("bulunma", "ayrilma", "yonelme", "belirtme", "lik", "vasita", "ilgi")


@pytest.mark.parametrize("birim", sorted(_SOZCUK_TABLO))
def test_a6_sozcuk_birim_ek_tablosu(birim):
    for ek, form in zip(_EK_SIRASI, _SOZCUK_TABLO[birim].split()):
        v = A.kur_olcu2(12, "", birim, 0, ek=ek)
        assert v.sozlu == "on iki " + form, (birim, ek, v.sozlu)
        assert v.yazili == "12 " + form, (birim, ek, v.yazili)


def test_a5_bilesik_saat_ince_ek():
    v = A.kur_bilesik([(1, "gun"), (3, "saat")], "bulunma")
    assert (v.sozlu, v.yazili) == ("bir gün üç saatte", "1 gün 3 saatte")
    v = A.kur_bilesik([(2, "saat"), (15, "dakika")], "lik")
    assert v.yazili == "2 saat 15 dakikalık"


def test_uretimde_kalin_saat_eki_yok(kucuk):
    kotu = re.compile(r"saat(?:ta|tan|a|ı|ın|la|lık|taki)")
    for r in _tum(kucuk):
        assert not kotu.search(r["girdi"]) and not kotu.search(r["hedef"]), r


def test_taşıyıcı_uyumu():
    # yemek/mola/sınav süreleri saat/gün/yıl almaz; "adam" öncesinde kişi adı yok
    for _, m in A.SABLONLAR_A["yeni"]:
        if re.search(r"^(Yemek|Mola|Sınav|Ders|Bilet)", m):
            assert not re.search(r"ksure|usure|zaman|saat", m), m
        assert not re.search(r"\{isim\} \{v2yeni\.yas[^}]*\} bir adam", m), m


def test_a6_yas_bicimleri():
    assert (A.kur_yas(40).sozlu, A.kur_yas(40).yazili) == ("kırk yaşında", "40 yaşında")
    rng = random.Random(4)
    A.CTX.sifirla()
    for ek, bicim in A._YAS_BICIMI.items():
        v = A.ornekle_yeni(rng, "yas", ek)
        assert v.yazili.endswith(bicim)


def test_a6_zaman_birimleri_10_ve_ustu():
    rng = random.Random(8)
    A.CTX.sifirla()
    for t in A.ZAMAN_YENI:
        for _ in range(40):
            A.CTX.birim = t
            v = A.ornekle_yeni(rng, "zaman", None)
            assert int(v.yazili.split()[0]) >= 10
    A.CTX.birim = None


# ---------------------------------------------------------------- A8

def test_a8_kucuk_sayi_politikasi():
    v = V.kur_kardinal(8)
    assert v.kalir and (v.yazili, v.sozlu) == ("sekiz", "sekiz")
    v = V.kur_kardinal(12)
    assert not v.kalir and (v.yazili, v.sozlu) == ("12", "on iki")
    rng = random.Random(6)
    A.CTX.sifirla()
    A.CTX.a8_kucuk = True
    assert all(A.ornekle_kucuk(rng).kalir for _ in range(50))
    A.CTX.a8_kucuk = False
    assert not any(A.ornekle_kucuk(rng).kalir for _ in range(50))
    A.CTX.sifirla()


# ---------------------------------------------------------------- şablonlar

def test_sablon_bolunmesi_ve_sayilari():
    for ab in A.ALT_BASLIKLAR:
        lst = A.SABLONLAR_A[ab]
        egitim = [i for i, _ in lst if i not in A.TEST_SABLONLARI]
        assert len(egitim) >= 37, ab  # train+validation havuzu: dosyada >= 30 ayrı şablon için pay
        assert all(i.startswith("v2a-") for i, _ in lst)
    toplam = sum(len(v) for v in A.SABLONLAR_A.values())
    assert len(A.TEST_SABLONLARI) / toplam >= 0.15
    assert toplam - len(A.TEST_SABLONLARI) >= 430
    # şablon metinleri ayrık
    metinler = [m for v in A.SABLONLAR_A.values() for _, m in v]
    assert len(metinler) == len(set(metinler))
    A._dogrula_sablonlar_kayitli()


def test_a4_her_birim_ek_hucresi_egitim_sablonuna_sahip():
    egitim = [(i, m) for i, m in A.SABLONLAR_A["birim"] if i not in A.TEST_SABLONLARI]
    for u in A.A4_BIRIMLER:
        for e in A.A4_EKLER:
            ok = [1 for _, m in egitim
                  if (lambda s: s[2] == e and u in A.A4_GRUP[s[1]])(A.sablon_slotlari(m)[0])]
            assert ok, (u, e)


def test_sablonlarda_sayi_sozcugu_yok():
    # girdide değişmeden kalacak taşıyıcı metinde, dönüştürülecek sayı sözcüğü bulunmamalı
    yasak = {"sıfır", "iki", "üç", "dört", "beş", "sekiz", "dokuz", "yirmi", "otuz", "kırk", "elli", "altmış",
             "yetmiş", "seksen", "doksan", "milyon", "milyar"}
    for i, m in A.SABLON_METNI.items():
        metin = re.sub(r"\{[^}]*\}", " ", m)
        for t in re.findall(r"[^\W\d_]+", lower_tr(metin)):
            assert t not in yasak, (i, t)


# ---------------------------------------------------------------- üretim sözleşmesi (küçük)

@pytest.fixture(scope="module")
def kucuk():
    return A.uret_bolumler(560, 80, 160, 2201)


def _tum(s):
    return [r for b in ("train", "validation", "test") for r in s[b]]


def test_uretim_adetleri_ve_alanlar(kucuk):
    assert {k: len(v) for k, v in kucuk.items()} == {"train": 560, "validation": 80, "test": 160}
    for r in _tum(kucuk):
        assert set(r) == {"girdi", "hedef", "kategori", "sablon"}
        assert r["sablon"].startswith("v2a-")
        assert len(r["girdi"].encode("utf-8")) <= 180 and len(r["hedef"].encode("utf-8")) <= 180


def test_uretim_sablon_ayrikligi(kucuk):
    egitim = {r["sablon"] for b in ("train", "validation") for r in kucuk[b]}
    test = {r["sablon"] for r in kucuk["test"]}
    assert not egitim & test
    assert test <= A.TEST_SABLONLARI
    assert not egitim & A.TEST_SABLONLARI


def test_uretim_yinelenme_yok(kucuk):
    satirlar = _tum(kucuk)
    ciftler = [(r["girdi"], r["hedef"]) for r in satirlar]
    assert len(ciftler) == len(set(ciftler))
    hedefler = [r["hedef"] for r in satirlar]
    assert len(hedefler) == len(set(hedefler))
    girdiler = [r["girdi"] for r in satirlar]
    assert len(girdiler) == len(set(girdiler))


def test_uretim_girdi_hedef_farki(kucuk):
    for r in _tum(kucuk):
        if r["girdi"] == r["hedef"]:
            # yalnız küçük sayı politikasında (A8) ve rakamsız
            assert r["sablon"].startswith("v2a-kucuk-"), r
            assert not re.search(r"\d", r["hedef"])
        else:
            assert r["girdi"] != r["hedef"]
    a8 = [r for r in kucuk["train"] if r["sablon"].startswith("v2a-kucuk-")]
    esit = sum(1 for r in a8 if r["girdi"] == r["hedef"])
    assert abs(esit - len(a8) / 2) <= 1


def test_uretim_sayi_disi_bayt_bayt_ayni(kucuk):
    # hedefteki dört harften uzun alfabetik sözcükler girdide aynen bulunmalı (birim kısaltmaları kısa/sembollü)
    for r in _tum(kucuk):
        g = Counter(re.findall(r"[^\W\d_]{4,}", lower_tr(r["girdi"])))
        h = Counter(re.findall(r"[^\W\d_]{4,}", lower_tr(r["hedef"])))
        # hedef sözcükleri (ek kesmeden sonrası hariç) girdinin içinde geçer
        for kelime in h:
            assert kelime in g, (r, kelime)


def test_uretim_buyuk_harf_ve_noktalama(kucuk):
    for r in kucuk["train"]:
        buyuk = r["girdi"][0].isupper()
        assert buyuk == r["hedef"][0].isupper() or r["hedef"][0].isdigit() or r["hedef"][0] in "+%-"
        if buyuk:
            assert r["girdi"][-1] in ".?!" and r["hedef"][-1] in ".?!"
        else:  # küçük harf kipinde noktalama yok
            assert not re.search(r"[,!?;:]", r["girdi"]) and not r["girdi"].endswith(".")
    oran = sum(r["girdi"][0].isupper() for r in kucuk["train"]) / 560
    assert 0.30 < oran < 0.50


def test_uretim_telefon_tek_ayrisim(kucuk):
    tel = [r for r in _tum(kucuk) if r["kategori"] == "telefon"]
    assert len(tel) > 40
    for r in tel:
        assert not A.telefon_satiri_belirsiz(r["girdi"], r["hedef"]), r
        assert re.search(r"(0\d{3}|\+90 \d{3}) \d{3} \d{2} \d{2}", r["hedef"])


def test_uretim_a7_sozcuk_ve_varlik(kucuk):
    a7 = [r for r in _tum(kucuk) if r["sablon"].startswith("v2a-uzun-")]
    assert len(a7) > 40
    for r in a7:
        assert 12 <= len(r["girdi"].split()) <= 22, r
        assert r["kategori"] == "karisik"
        assert len(re.findall(r"\d", r["hedef"])) >= 2


def test_uretim_a5_hepsi_rakam(kucuk):
    for r in _tum(kucuk):
        if r["sablon"].startswith("v2a-bilesik-"):
            assert r["kategori"] == "bilesik"
            assert len(re.findall(r"(?<![\d.,])\d+(?: |$|')", r["hedef"] + " ")) >= 2, r


def test_uretim_determinizm(kucuk):
    ikinci = A.uret_bolumler(560, 80, 160, 2201)
    assert ikinci == kucuk
    baska = A.uret_bolumler(560, 80, 160, 99)
    assert baska["train"] != kucuk["train"]


def test_kayit_temizligi():
    assert not any(k in V.ORNEKLEYICILER for k in A._ORNEKLEYICILER2)
    from megazeka_sayi import sablonlar as B
    assert not any(k in B.FILLERS for k in A._FILLERS2)


# ---------------------------------------------------------------- tam boy: çeşitlilik eşikleri

@pytest.fixture(scope="module")
def tam():
    return A.uret_bolumler(16000, 400, 500, 2201)


def test_tam_kota_ve_esikler(tam):
    train = tam["train"]
    n = len(train)
    assert (n, len(tam["validation"]), len(tam["test"])) == (16000, 400, 500)
    m = A.olc(train)
    assert m["alt_baslik_satir"] == {"A1": 3200, "A2-tel": 1800, "A2-kod": 1400, "A3": 1300, "A4": 2000, "A5": 1800,
                                     "A6": 1500, "A7": 1800, "A8": 1200}
    assert m["sablon_sayisi"] >= 350
    assert all(v >= 30 for v in m["alt_baslik_sablon"].values())
    assert m["sablon_en_cok"][1] <= 0.015
    assert m["ilk_sozcuk_en_cok"][0][1] <= 0.06
    assert all(v >= 400 for v in m["a1_tip_satir"].values())
    assert m["a1_ic_sifirsiz_satir"] == 0
    assert m["a2_tel_belirsiz"] == 0
    assert all(m["a2_kod_uzunluk"].get(k, 0) >= 60 for k in range(3, 12)) and 0 not in m["a2_kod_uzunluk"]
    assert m["a4_hucre_sayisi"] == 48 and m["a4_hucre_en_az"] >= 40
    assert m["a7_sozcuk_aralik"][0] >= 12 and m["a7_sozcuk_aralik"][1] <= 22
    assert m["a8_girdi_esit_hedef"] == 600
    assert m["bayt_en_cok"] <= 180


def test_tam_bolumler_arasi_yinelenme_yok(tam):
    satirlar = _tum(tam)
    assert len({r["hedef"] for r in satirlar}) == len(satirlar)
    assert len({(r["girdi"], r["hedef"]) for r in satirlar}) == len(satirlar)
    assert not {r["sablon"] for r in tam["train"]} & {r["sablon"] for r in tam["test"]}
    assert not {r["sablon"] for r in tam["validation"]} & {r["sablon"] for r in tam["test"]}
