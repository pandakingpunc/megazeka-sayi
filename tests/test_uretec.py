import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

import pytest  # noqa: E402

import uret  # noqa: E402
from megazeka_sayi import sablonlar as B  # noqa: E402
from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.turkce import capitalize_tr, inflect, lower_tr, upper_tr, written_suffix  # noqa: E402


def test_turkce_harf():
    assert lower_tr("İSTANBUL IĞDIR") == "istanbul ığdır"
    assert upper_tr("istanbul ığdır") == "İSTANBUL IĞDIR"
    assert capitalize_tr("ıspanak") == "Ispanak"


def test_spec_tablosu_5_ornek():
    assert V.kur_para(1250, 50).sozlu == "bin iki yüz elli lira elli kuruş"
    assert V.kur_para(1250, 50).yazili == "1.250,50 TL"
    y = V.kur_yuzde(12, "5", bucuk=True)
    assert (y.sozlu, y.yazili) == ("yüzde on iki buçuk", "%12,5")
    o = V.kur_olcu(2, "5", "kg", soz_idx=1, bucuk=True)
    assert (o.sozlu, o.yazili) == ("iki buçuk kilogram", "2,5 kg")
    s = V.kur_saat(14, 30, ek="bulunma")
    assert (s.sozlu, s.yazili) == ("on dört otuzda", "14.30'da")
    t = V.kur_telefon("05321234567")
    assert t.sozlu == "sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi"
    assert t.yazili == "0532 123 45 67"


@pytest.mark.parametrize("kok,ek,sozlu,yazili", [
    ("dört", "bulunma", "dörtte", "te"), ("dört", "yonelme", "dörde", "e"), ("dört", "belirtme", "dördü", "ü"),
    ("dört", "ilgi", "dördün", "ün"), ("dört", "ayrilma", "dörtten", "ten"), ("dört", "vasita", "dörtle", "le"),
    ("iki", "bulunma", "ikide", "de"), ("iki", "yonelme", "ikiye", "ye"), ("iki", "belirtme", "ikiyi", "yi"),
    ("iki", "iyelik3", "ikisi", "si"), ("iki", "ilgi", "ikinin", "nin"), ("iki", "ayrilma", "ikiden", "den"),
    ("iki", "vasita", "ikiyle", "yle"), ("otuz", "bulunma", "otuzda", "da"),
    ("üç", "bulunma", "üçte", "te"), ("beş", "bulunma", "beşte", "te"), ("kırk", "bulunma", "kırkta", "ta"),
    ("altmış", "bulunma", "altmışta", "ta"), ("altı", "bulunma_ki", "altıdaki", "daki"),
    ("doksan", "cogul_bulunma", "doksanlarda", "larda"), ("buçuk", "lik", "buçukluk", "luk"),
])
def test_ek_tablosu(kok, ek, sozlu, yazili):
    assert inflect(kok, ek) == (sozlu, yazili)


def test_yazili_ek_kanonik():
    assert written_suffix("tele", "yonelme") == "ye"
    assert written_suffix("tele", "ayrilma") == "den"
    assert written_suffix("tele", "lik") == "lik"
    assert written_suffix("kilogram", "ayrilma") == "dan"
    assert written_suffix("beş", "lik") == "lik"
    assert written_suffix("doksan", "cogul_bulunma") == "larda"
    assert written_suffix("dört", "yonelme") == "e"  # yumuşama yok
    assert written_suffix("derece", "bulunma") == "de"


def test_spec_ek_satirlari_varlik():
    assert V.kur_para(100, ek="yonelme").yazili == "100 TL'ye"
    assert V.kur_para(100, ek="yonelme").sozlu == "yüz liraya"
    assert V.kur_para(100, ek="ayrilma").sozlu == "yüz liradan"
    assert V.kur_para(100, ek="lik").yazili == "100 TL'lik"
    assert V.kur_olcu(5, "", "kg", 0, ek="ayrilma").sozlu == "beş kilodan"
    assert V.kur_olcu(5, "", "kg", 0, ek="ayrilma").yazili == "5 kg'dan"
    assert V.kur_olcu(5, "", "kg", 1, ek="ayrilma").sozlu == "beş kilogramdan"
    assert V.kur_yuzde(12, "5", True, ek="lik").sozlu == "yüzde on iki buçukluk"
    assert V.kur_yuzde(12, "5", True, ek="lik").yazili == "%12,5'lik"
    assert V.kur_onyil(1990, "cogul_bulunma").yazili == "1990'larda"
    assert V.kur_onyil(1990, "cogul_bulunma").sozlu == "doksanlarda"
    assert V.kur_yil(2026, "bulunma_ki").yazili == "2026'daki"
    assert V.kur_yil(2026, "bulunma_ki").sozlu == "iki bin yirmi altıdaki"
    c = V.kur_olcu(30, "", "C", ek="bulunma")
    assert (c.sozlu, c.yazili) == ("otuz derece santigratta", "30 °C'de")
    assert V.kur_tarih(29, 10, None, "bulunma").yazili == "29 Ekim'de"
    assert V.kur_tarih(29, 10, None, "bulunma").sozlu == "yirmi dokuz ekimde"
    for ek, yz in [("bulunma", "4'te"), ("yonelme", "4'e"), ("belirtme", "4'ü"), ("ilgi", "4'ün"),
                   ("ayrilma", "4'ten"), ("vasita", "4'le")]:
        assert V.kur_saat(4, bicim="tam", ek=ek).yazili == yz
    assert V.kur_saat(4, bicim="tam", ek="belirtme").sozlu == "dördü"


def test_sayi_oku():
    assert S.sayi_oku(0) == "sıfır"
    assert S.sayi_oku(1000) == "bin"
    assert S.sayi_oku(1_000_000) == "bir milyon"
    assert S.sayi_oku(100) == "yüz"
    assert S.sayi_oku(1250) == "bin iki yüz elli"
    assert S.sayi_oku(101_000) == "yüz bir bin"
    assert S.sayi_oku(2_001_000) == "iki milyon bin"
    assert S.sayi_oku(999_000_000_000_000) == "dokuz yüz doksan dokuz trilyon"
    assert S.yaz_sayi(1_000_000) == "1.000.000"
    assert S.yaz_sayi(1250) == "1.250"


def test_siralar():
    assert [S.sira_oku(n) for n in (1, 2, 3, 4, 10, 20, 100, 1000)] == [
        "birinci", "ikinci", "üçüncü", "dördüncü", "onuncu", "yirminci", "yüzüncü", "bininci"]
    assert S.sira_oku(21) == "yirmi birinci"
    assert V.kur_sira(21).yazili == "21."


def test_ondalik_ve_buyuk():
    assert S.ondalik_oku(3, "14") == "üç virgül on dört"
    assert S.ondalik_oku(3, "05") == "üç virgül sıfır beş"
    assert S.ondalik_oku(0, "5") == "sıfır virgül beş"
    assert S.ondalik_oku(2, "5", bucuk=True) == "iki buçuk"
    assert V.kur_ondalik(3, "14").yazili == "3,14"
    b = V.kur_buyuk_yuvarlak(2, "5", "milyon", bucuk=True)
    assert (b.yazili, b.sozlu) == ("2,5 milyon", "iki buçuk milyon")
    b = V.kur_buyuk_yuvarlak(3, "", "milyar", birim="TL")
    assert (b.yazili, b.sozlu) == ("3 milyar TL", "üç milyar lira")
    d = V.kur_buyuk_duz(1_200_000)
    assert (d.yazili, d.sozlu) == ("1.200.000", "bir milyon iki yüz bin")


def test_yil_telefon_kod_skor_aralik_eksi():
    assert V.kur_yil(2026).yazili == "2026"
    assert V.kur_tarih(8, 11, 2026).yazili == "8 Kasım 2026"
    assert V.kur_tarih(8, 11, 2026).sozlu == "sekiz kasım iki bin yirmi altı"
    t = V.kur_telefon("05321234567", ("rakam", "rakam", "rakam", "rakam"))
    assert t.sozlu.startswith("sıfır beş üç iki bir iki üç dört beş")
    assert V.kur_telefon("05321234567", arti90=True).yazili == "+90 532 123 45 67"
    k = V.kur_kod("0842")
    assert (k.yazili, k.sozlu) == ("0842", "sıfır sekiz dört iki")
    assert V.kur_skor(2, 1).sozlu == "iki bir" and V.kur_skor(2, 1).yazili == "2-1"
    assert V.kur_aralik(5, 6).yazili == "5-6"
    assert V.kur_aralik(10, 15).sozlu == "on on beş"
    e = V.kur_eksi(5, "", "derece")
    assert (e.yazili, e.sozlu) == ("-5 derece", "eksi beş derece")
    assert V.kur_saat(9, 5).yazili == "9.05"
    assert V.kur_saat(3, 30, bucuk=True).sozlu == "üç buçuk"
    assert V.kur_para(kurus=50).yazili == "50 kuruş"
    assert V.kur_para(lira=100, birim="dolar").yazili == "100 dolar"


def test_kucuk_sayi_politikasi():
    assert V.kur_kardinal(3, "yaziyla").kalir
    assert V.kur_kardinal(3, "yaziyla").yazili == "üç"
    assert V.kur_kardinal(3, "rakamla").yazili == "3"
    assert V.kur_kardinal(12, "yaziyla").yazili == "12"
    assert V.kur_kardinal(35).sozlu == "otuz beş"


def test_sablon_kayitlari():
    for k in B.POZITIF_KATEGORILER:
        assert len(B.SABLONLAR[k]) >= 24, k
        assert B.sablonlar(k, True), k
    assert len(B.SABLONLAR["negatif_es"]) >= 40
    assert not {i for i, _ in B.sablonlar("para", False)} & B.TEST_SABLONLARI


@pytest.fixture(scope="module")
def veri():
    cv = uret.cv_yukle(uret.CV_YOLU)
    return uret.uret_bolumler(1500, 150, 150, 7, "yaziyla", cv)


def test_belirlenimcilik():
    cv = {"train": [], "validation": [], "test": []}
    a = uret.uret_bolumler(300, 30, 30, 99, "yaziyla", cv)
    b = uret.uret_bolumler(300, 30, 30, 99, "yaziyla", cv)
    c = uret.uret_bolumler(300, 30, 30, 100, "yaziyla", cv)
    assert a == b
    assert a != c


def test_sizinti_ve_sablon_ayriligi(veri):
    held = B.TEST_SABLONLARI | {"yazili:" + i for i in B.TEST_SABLONLARI}
    assert not any(r["sablon"] in held for r in veri["train"] + veri["validation"])
    assert all(r["sablon"] in held or r["sablon"] == "dogal-cv" for r in veri["test"])
    th = {r["hedef"] for r in veri["test"]}
    assert not any(r["hedef"] in th for r in veri["train"] + veri["validation"])
    vh = {r["hedef"] for r in veri["validation"]}
    assert not any(r["hedef"] in vh for r in veri["train"])


def test_bayt_siniri_ve_negatifler(veri):
    for s in veri.values():
        for r in s:
            assert len(r["girdi"].encode()) <= 180 and len(r["hedef"].encode()) <= 180
            assert set(r) == {"girdi", "hedef", "kategori", "sablon"}
            if r["kategori"].startswith("negatif"):
                assert r["girdi"] == r["hedef"]
            elif r["kategori"] != "kardinal":
                assert r["girdi"] != r["hedef"]
            if r["kategori"] != "negatif_yazili":
                assert not any(ch.isdigit() for ch in r["girdi"])
    tr = veri["train"]
    neg = sum(r["kategori"].startswith("negatif") for r in tr) / len(tr)
    assert 0.34 <= neg <= 0.42


def test_ay_adi_buyuk_harf(veri):
    tarihler = [r for r in veri["train"] if r["kategori"] == "tarih" and "Kasım" in r["hedef"]]
    assert tarihler
    assert any(r["kategori"] == "negatif_kalip" and "mayıs ayında" in r["hedef"].lower() for r in veri["train"])
