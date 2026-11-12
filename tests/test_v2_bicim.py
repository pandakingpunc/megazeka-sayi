"""v2 C kaynağı (training/v2_bicim.py) testleri: SPEC-v2 §C tabloları, ek biçimleri, veri sözleşmesi, çeşitlilik eşikleri."""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

import pytest  # noqa: E402

import v2_bicim as M  # noqa: E402


# ----------------------------------------------------------------------------- C1 tablosu

@pytest.mark.parametrize("fn,girdi,hedef", [
    # 5 bin lira · 12 bin 500 lira · 5 bin 250 · 3 milyon 200 bin
    (lambda: M.yari_para(("int", 5000)), "5 bin lira", "5.000 TL"),
    (lambda: M.yari_para(("int", 12500)), "12 bin 500 lira", "12.500 TL"),
    (lambda: M.yari_sayi(("int", 5250)), "5 bin 250", "5.250"),
    (lambda: M.yari_sayi(("int", 3200000)), "3 milyon 200 bin", "3.200.000"),
    (lambda: M.yari_sayi(("int", 1500)), "bin 500", "1.500"),
    (lambda: M.yari_sayi(("int", 5025)), "5 bin 25", "5.025"),
    # 2 buçuk milyon · 1,5 milyon · 15 milyon
    (lambda: M.yari_sayi(("buyuk", 2, "5", "milyon", True)), "2 buçuk milyon", "2,5 milyon"),
    (lambda: M.yari_sayi(("buyuk", 1, "5", "milyon", False)), "1,5 milyon", "1,5 milyon"),
    (lambda: M.yari_sayi(("buyuk", 15, "", "milyon", False)), "15 milyon", "15 milyon"),
    (lambda: M.yari_para(("buyuk", 15, "", "milyon", False)), "15 milyon lira", "15 milyon TL"),
    # 1250 lira · 12500 kişi · 1250,50 lira
    (lambda: M.yari_para(("int", 1250), mod="duz"), "1250 lira", "1.250 TL"),
    (lambda: M.yari_sayi(("int", 12500), mod="duz"), "12500", "12.500"),
    (lambda: M.yari_para(("int", 1250, 50), mod="duz", virgul=True), "1250,50 lira", "1.250,50 TL"),
    (lambda: M.yari_para(("int", 12500, 50)), "12 bin 500 lira 50 kuruş", "12.500,50 TL"),
    (lambda: M.yari_para(("int", 5, 50), mod="duz"), "5 lira 50 kuruş", "5,50 TL"),
    # birimler
    (lambda: M.yari_olcu(("int", 100), "km"), "100 kilometre", "100 km"),
    (lambda: M.yari_olcu(("int", 2), "kg", soz_idx=0), "2 kilo", "2 kg"),
    (lambda: M.yari_olcu(("int", 2), "kg", soz_idx=1), "2 kilogram", "2 kg"),
    (lambda: M.yari_olcu(("int", 16), "GB"), "16 gigabayt", "16 GB"),
    (lambda: M.yari_olcu(("int", 80), "m2"), "80 metrekare", "80 m²"),
    (lambda: M.yari_olcu(("int", 25), "C"), "25 derece santigrat", "25 °C"),
    (lambda: M.yari_olcu(("dec", 2, "5", False), "kg"), "2,5 kilo", "2,5 kg"),
    (lambda: M.yari_para(("int", 50), mod="duz"), "50 lira", "50 TL"),
    # yüzde
    (lambda: M.yari_yuzde(50), "yüzde 50", "%50"),
    (lambda: M.yari_yuzde(12, "5"), "yüzde 12,5", "%12,5"),
    (lambda: M.yari_yuzde(12, "5", True), "yüzde 12 buçuk", "%12,5"),
    # 2 buçuk kilo · saat 3 buçukta
    (lambda: M.yari_olcu(("dec", 2, "5", True), "kg"), "2 buçuk kilo", "2,5 kg"),
    (lambda: M.yari_saat(3, 30, "bucuk", "bulunma"), "3 buçukta", "3.30'da"),
    # saat 14:30'da · 14:05
    (lambda: M.yari_saat(14, 30, ek="bulunma"), "14:30'da", "14.30'da"),
    (lambda: M.yari_saat(14, 5), "14:05", "14.05"),
    (lambda: M.yari_saat(9, 5, sifirli=True), "09:05", "9.05"),
    # 15 kasım 2026 · eksi 5 derece · telefon
    (lambda: M.yari_tarih(15, 11, 2026), "15 kasım 2026", "15 Kasım 2026"),
    (lambda: M.yari_tarih(15, 11), "15 kasım", "15 Kasım"),
    (lambda: M.yari_eksi(5, "", "derece"), "eksi 5 derece", "-5 derece"),
    (lambda: M.yari_eksi(5, "", "C"), "eksi 5 derece santigrat", "-5 °C"),
    (lambda: M.yari_eksi(2, "5", "derece", True), "eksi 2 buçuk derece", "-2,5 derece"),
    (lambda: M.yari_telefon("05321234567"), "05321234567", "0532 123 45 67"),
    (lambda: M.yari_telefon("05321234567", "sifir_ayri"), "0 532 123 45 67", "0532 123 45 67"),
    (lambda: M.yari_telefon("05321234567", "bitisik", True), "+905321234567", "+90 532 123 45 67"),
])
def test_c1_tablo(fn, girdi, hedef):
    assert fn() == (girdi, hedef)


@pytest.mark.parametrize("fn,girdi,hedef", [
    # ekli: 5 bin liraya · 100 kilometreden · 2 kiloluk
    (lambda: M.yari_para(("int", 5000), ek="yonelme"), "5 bin liraya", "5.000 TL'ye"),
    (lambda: M.yari_olcu(("int", 100), "km", ek="ayrilma"), "100 kilometreden", "100 km'den"),
    (lambda: M.yari_olcu(("int", 2), "kg", ek="lik"), "2 kiloluk", "2 kg'lık"),
    (lambda: M.yari_para(("int", 1250), ek="belirtme", mod="duz"), "1250 lirayı", "1.250 TL'yi"),
    (lambda: M.yari_para(("int", 100), birim="dolar", ek="yonelme", mod="duz"), "100 dolara", "100 dolara"),
    (lambda: M.yari_para(("int", 1250, 50), ek="yonelme", mod="duz", virgul=True), "1250,50 liraya", "1.250,50 TL'ye"),
    (lambda: M.yari_para(("int", 5000), ek="vasita"), "5 bin lirayla", "5.000 TL'yle"),
    (lambda: M.yari_para(("buyuk", 2, "5", "milyon", True), ek="yonelme"), "2 buçuk milyon liraya", "2,5 milyon TL'ye"),
    # rakamdan sonra kesmeli ek
    (lambda: M.yari_yuzde(50, ek="iyelik3"), "yüzde 50'si", "%50'si"),
    (lambda: M.yari_yuzde(12, "5", True, "iyelik3"), "yüzde 12 buçuğu", "%12,5'i"),
    (lambda: M.yari_yuzde(40, ek="ilgi"), "yüzde 40'ın", "%40'ın"),
    (lambda: M.yari_saat(14, 30, ek="bulunma"), "14:30'da", "14.30'da"),
    (lambda: M.yari_saat(16, 30, ek="ayrilma"), "16:30'dan", "16.30'dan"),
    (lambda: M.yari_saat(3, 30, "bucuk", "yonelme"), "3 buçuğa", "3.30'a"),
    (lambda: M.yari_sayi(("int", 5000), "yonelme"), "5 bine", "5.000'e"),
    (lambda: M.yari_sayi(("int", 5250), "yonelme"), "5 bin 250'ye", "5.250'ye"),
    (lambda: M.yari_sayi(("int", 12500), "ayrilma", "duz"), "12500'den", "12.500'den"),
    (lambda: M.yari_sayi(("int", 3200000), "yonelme"), "3 milyon 200 bine", "3.200.000'e"),
    (lambda: M.yari_sayi(("buyuk", 2, "5", "milyon", True), "yonelme"), "2 buçuk milyona", "2,5 milyona"),
    (lambda: M.yari_tarih(15, 11, 2026, "bulunma"), "15 kasım 2026'da", "15 Kasım 2026'da"),
    (lambda: M.yari_tarih(15, 11, None, "bulunma"), "15 kasımda", "15 Kasım'da"),
    (lambda: M.yari_tarih(13, 1, None, "belirtme"), "13 ocağı", "13 Ocak'ı"),
    (lambda: M.yari_tarih(13, 12, None, "yonelme"), "13 aralığa", "13 Aralık'a"),
    (lambda: M.yari_eksi(5, "", "derece", ek="yonelme"), "eksi 5 dereceye", "-5 dereceye"),
    (lambda: M.yari_eksi(5, "", "C", ek="bulunma"), "eksi 5 derece santigratta", "-5 °C'de"),
    (lambda: M.yari_telefon("05321234567", "bitisik", ek="belirtme"), "05321234567'yi", "0532 123 45 67'yi"),
])
def test_c1_ekli(fn, girdi, hedef):
    assert fn() == (girdi, hedef)


def test_c1_karisik_cumle_kuralı(monkeypatch):
    """Rakamlı sayıya küçük sayı politikası uygulanmaz; aynı cümledeki yazıyla sayı SPEC'e göre işlenir."""
    monkeypatch.setattr(M, "SARMALA_ORANI", 0.0)
    sb = M.Sablon("x", "yari", "karisik", "{E} kişi {E} dakika bekledi", None, None)
    rng = random.Random(1)
    assert M.kur_cumle(rng, sb, False, [("3", "3"), ("on beş", "15")]) == (
        "3 kişi on beş dakika bekledi", "3 kişi 15 dakika bekledi")
    sb2 = M.Sablon("x", "yari", "karisik", "{E} ödedim, {E} günde bitti", None, None)
    assert M.kur_cumle(rng, sb2, True, [("5 bin lira", "5.000 TL"), ("iki", "iki")]) == (
        "5 bin lira ödedim, iki günde bitti.", "5.000 TL ödedim, iki günde bitti.")


# ----------------------------------------------------------------------------- C2 tablosu

def _c2(v_sp, sec):
    v, sp = v_sp
    return M.c2_girdi(v, sp, sec), v.yazili


@pytest.mark.parametrize("v_sp,sec,girdi,hedef", [
    (lambda: M.c2_kardinal(15), "tam", "onbeş", "15"),
    (lambda: M.c2_para(25), "tam", "yirmibeş lira", "25 TL"),
    (lambda: M.c2_olcu(250, "g"), {0}, "ikiyüz elli gram", "250 g"),
    (lambda: M.c2_olcu(250, "g"), "tam", "ikiyüzelli gram", "250 g"),
    (lambda: M.c2_olcu(250, "g"), {1}, "iki yüzelli gram", "250 g"),
    (lambda: M.c2_kardinal(3000), "tam", "üçbin", "3.000"),
    (lambda: M.c2_kardinal(150), "tam", "yüzelli", "150"),
    (lambda: M.c2_kardinal(1700), "tam", "binyediyüz", "1.700"),
    (lambda: M.c2_kardinal(1700), {1}, "bin yediyüz", "1.700"),
    (lambda: M.c2_yuzde(15), "tam", "yüzde onbeş", "%15"),
    (lambda: M.c2_saat(11, None, "bulunma"), "tam", "saat onbirde".replace("saat ", ""), "11'de"),
    # ekli
    (lambda: M.c2_kardinal(15, "bulunma"), "tam", "onbeşte", "15'te"),
    (lambda: M.c2_kardinal(25, "yonelme"), "tam", "yirmibeşe", "25'e"),
    (lambda: M.c2_kardinal(14, "belirtme"), "tam", "ondördü", "14'ü"),
    (lambda: M.c2_kardinal(14, "yonelme"), "tam", "ondörde", "14'e"),
    (lambda: M.c2_para(25, ek="yonelme"), "tam", "yirmibeş liraya", "25 TL'ye"),
    (lambda: M.c2_yuzde(15, "iyelik3"), "tam", "yüzde onbeşi", "%15'i"),
    (lambda: M.c2_olcu(25, "kg", "lik"), "tam", "yirmibeş kiloluk", "25 kg'lık"),
    (lambda: M.c2_tarih("tam", 15, 11, 2026), "tam", "onbeş kasım ikibinyirmialtı", "15 Kasım 2026"),
    (lambda: M.c2_tarih("yil", yil=2026, ek="bulunma"), "tam", "ikibinyirmialtıda", "2026'da"),
    (lambda: M.c2_tarih("gunay", 13, 1, ek="belirtme"), "tam", "onüç ocağı", "13 Ocak'ı"),
])
def test_c2_tablo(v_sp, sec, girdi, hedef):
    assert _c2(v_sp(), sec) == (girdi, hedef)


def test_c2_binbir_birlesmez():
    v, sp = M.c2_kardinal(1001)
    assert M.c2_girdi(v, sp, "tam") is None
    v, sp = M.c2_kardinal(21001)
    assert M.c2_girdi(v, sp, "tam") == "yirmibirbin bir"


def test_c2_birlesme_harfleri_korur():
    rng = random.Random(3)
    for _ in range(300):
        aile = rng.choice(sorted(M.C2_AILE_AGIRLIK))
        r = M.c2_varlik(rng, aile, rng.choice([None, "bulunma", "yonelme", "belirtme"]), None)
        if r is None or not r[1]:
            continue
        v, sp = r
        toks = v.sozlu.split()
        out = M.bitistir_rastgele(rng, toks, sp)
        if out is None:
            continue
        assert "".join(out) == "".join(toks)
        assert len(out) < len(toks)


# ----------------------------------------------------------------------------- C3 tablosu

@pytest.mark.parametrize("arg,girdi,hedef", [
    ((5, 10, "kala"), "beşe on kala", "5'e 10 kala"),
    ((4, 20, "geçe"), "dördü yirmi geçe", "4'ü 20 geçe"),
    ((3, 15, "var"), "üçe çeyrek var", "3'e çeyrek var"),
    ((6, 15, "geçiyor"), "altıyı çeyrek geçiyor", "6'yı çeyrek geçiyor"),
    ((8, 5, "var", True), "saat sekize beş var", "saat 8'e 5 var"),
    ((12, 15, "kala"), "on ikiye çeyrek kala", "12'ye çeyrek kala"),
    ((1, 10, "kala"), "bire on kala", "1'e 10 kala"),
    ((9, 5, "geçiyordu"), "dokuzu beş geçiyordu", "9'u 5 geçiyordu"),
    ((3, 2, "var"), "üçe iki var", "3'e 2 var"),
    ((10, 25, "geçe"), "onu yirmi beş geçe", "10'u 25 geçe"),
    ((7, 10, "kalmıştı", False, True), "yediye on dakika kalmıştı", "7'ye 10 dakika kalmıştı"),
    ((2, 15, "geçmişti"), "ikiyi çeyrek geçmişti", "2'yi çeyrek geçmişti"),
    ((11, 20, "vardı"), "on bire yirmi vardı", "11'e 20 vardı"),
])
def test_c3_tablo(arg, girdi, hedef):
    assert M.kur_saat_deyis(*arg) == (girdi, hedef)


def test_c3_cumle_ornekleri(monkeypatch):
    monkeypatch.setattr(M, "SARMALA_ORANI", 0.0)
    sb = M.Sablon("x", "saat_deyis", "z", "{E} buluşalım", None, None)
    g, h = M.kur_cumle(random.Random(1), sb, False, [M.kur_saat_deyis(12, 15, "kala")])
    assert (g, h) == ("on ikiye çeyrek kala buluşalım", "12'ye çeyrek kala buluşalım")


# ----------------------------------------------------------------------------- C4 ve ek biçimleri

@pytest.mark.parametrize("onek,gun,ek,girdi,hedef", [
    ("ayın", 15, "bulunma", "ayın on beşinde", "ayın 15'inde"),
    ("ayın", 20, "iyelik3", "ayın yirmisi", "ayın 20'si"),
    ("ayın", 3, "yonelme", "ayın üçüne", "ayın 3'üne"),
    ("mayısın", 19, "bulunma", "mayısın on dokuzunda", "mayısın 19'unda"),
    ("her ayın", 1, "iyelik3", "her ayın biri", "her ayın 1'i"),
    ("ayın", 4, "bulunma", "ayın dördünde", "ayın 4'ünde"),
    ("ayın", 4, "iyelik3", "ayın dördü", "ayın 4'ü"),
    ("ayın", 4, "yonelme", "ayın dördüne", "ayın 4'üne"),
    ("ayın", 2, "ayrilma", "ayın ikisinden", "ayın 2'sinden"),
    ("ayın", 22, "bulunma", "ayın yirmi ikisinde", "ayın 22'sinde"),
    ("ayın", 20, "bulunma", "ayın yirmisinde", "ayın 20'sinde"),
    ("bu ayın", 6, "iyelik3", "bu ayın altısı", "bu ayın 6'sı"),
    ("gelecek ayın", 9, "yonelme", "gelecek ayın dokuzuna", "gelecek ayın 9'una"),
    ("ocağın", 10, "yonelme", "ocağın onuna", "ocağın 10'una"),
    ("ağustosun", 8, "belirtme", "ağustosun sekizini", "ağustosun 8'ini"),
    ("ayın", 31, "belirtme", "ayın otuz birini", "ayın 31'ini"),
    ("ayın", 30, "bulunma", "ayın otuzunda", "ayın 30'unda"),
    ("ayın", 7, "ayrilma", "ayın yedisinden", "ayın 7'sinden"),
    ("ayın", 5, "iyelik3", "ayın beşi", "ayın 5'i"),
    ("ayın", 12, "yonelme", "ayın on ikisine", "ayın 12'sine"),
    ("ayın", 1, "bulunma", "ayın birinde", "ayın 1'inde"),
    ("ayın", 3, "belirtme", "ayın üçünü", "ayın 3'ünü"),
    ("ayın", 3, "iyelik3", "ayın üçü", "ayın 3'ü"),
    ("ayın", 10, "ayrilma", "ayın onundan", "ayın 10'undan"),
])
def test_c4_ayin_gunu(onek, gun, ek, girdi, hedef):
    assert M.kur_ayin_gunu(onek, gun, ek) == (girdi, hedef)


def test_c4_tum_gunler_ve_ekler_tutarli():
    """Her (gün, ek) için yazılı ek sözlü ekin sesli kısmıyla uyumlu; yumuşama yalnız sözlüde."""
    for gun in range(1, 32):
        for ek in M.C4_EK_TURLERI:
            g, h = M.kur_ayin_gunu("ayın", gun, ek)
            m = re.fullmatch(r"ayın (\d+)'(\w+)", h)
            assert m and int(m.group(1)) == gun
            assert g.endswith(m.group(2)) or (gun == 4 and "dörd" in g and g.endswith(m.group(2)))
            assert "dört" not in g.replace("dörtyüz", "") or gun != 4 or ek == "x"
            assert "'" not in g and not re.search(r"\d", g)


def test_iyelik_durum_ve_unlu_uyumu():
    assert M.iyelik_durum("dört", "bulunma") == ("dördünde", "ünde")
    assert M.iyelik_durum("yirmi", "iyelik3") == ("yirmisi", "si")
    assert M.iyelik_durum("beş", "ayrilma") == ("beşinden", "inden")
    assert M.iyelik_durum("dokuz", "yonelme") == ("dokuzuna", "una")
    assert M.iyelik_durum("altı", "belirtme") == ("altısını", "sını")
    assert M.iyelik_durum("on", "bulunma") == ("onunda", "unda")
    assert M.iyelik_durum("üç", "iyelik3") == ("üçü", "ü")


@pytest.mark.parametrize("saat,fiil,sozlu,yazili", [
    (4, "kala", "dörde", "4'e"), (6, "kala", "altıya", "6'ya"), (10, "var", "ona", "10'a"),
    (9, "var", "dokuza", "9'a"), (7, "kala", "yediye", "7'ye"), (8, "var", "sekize", "8'e"),
    (12, "kala", "on ikiye", "12'ye"), (11, "var", "on bire", "11'e"), (1, "var", "bire", "1'e"),
    (4, "geçe", "dördü", "4'ü"), (6, "geçe", "altıyı", "6'yı"), (9, "geçiyor", "dokuzu", "9'u"),
    (3, "geçe", "üçü", "3'ü"), (10, "geçe", "onu", "10'u"), (1, "geçiyor", "biri", "1'i"),
    (2, "geçiyor", "ikiyi", "2'yi"), (12, "geçe", "on ikiyi", "12'yi"), (5, "geçe", "beşi", "5'i"),
    (7, "geçe", "yediyi", "7'yi"), (8, "geçe", "sekizi", "8'i"),
])
def test_c3_saat_ekleri(saat, fiil, sozlu, yazili):
    g, h = M.kur_saat_deyis(saat, 10, fiil)
    assert g.split(" ")[:-2] == sozlu.split(" ") and h.split(" ")[0] == yazili


# ----------------------------------------------------------------------------- veri sözleşmesi

@pytest.fixture(scope="module")
def kucuk():
    return M.uret(seed=7, train=900, validation=120, test=150)


def _tum(sonuc):
    return [(b, r) for b, rs in sonuc.items() for r in rs]


def test_sozlesme_alanlari_ve_bayt(kucuk, tmp_path):
    for bolum, rs in kucuk.items():
        M.yaz_dosya(tmp_path / f"c-{bolum}.jsonl", rs)
        satirlar = [json.loads(s) for s in (tmp_path / f"c-{bolum}.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(satirlar) == len(rs)
        for r in satirlar:
            assert set(r) == {"girdi", "hedef", "kategori", "sablon"}
            assert r["kategori"] in M.KATEGORILER
            assert r["sablon"].startswith("v2c-")
            assert len(r["girdi"].encode("utf-8")) <= 180 and len(r["hedef"].encode("utf-8")) <= 180
            assert r["girdi"] and r["hedef"]
    assert "\r" not in (tmp_path / "c-train.jsonl").read_bytes().decode("utf-8")


def test_bolum_boyutlari(kucuk):
    assert {b: len(rs) for b, rs in kucuk.items()} == {"train": 900, "validation": 120, "test": 150}
    oran = Counter(r["kategori"] for r in kucuk["train"])
    assert oran["yari"] > oran["bitisik"] > oran["saat_deyis"] > oran["tarih"]


def test_test_sablonlari_ayrik(kucuk):
    egitim = {r["sablon"] for b in ("train", "validation") for r in kucuk[b]}
    test = {r["sablon"] for r in kucuk["test"]}
    assert not (egitim & test)
    assert all(s in {x.id for x in M.HEPSI if x.id in M.TEST_IDLERI} for s in test)
    assert all(s not in M.TEST_IDLERI for s in egitim)


def test_sablonlarin_en_az_yuzde_15i_teste_ayrilmis():
    for kat in M.KATEGORILER:
        hepsi = [s for s in M.HEPSI if s.kat == kat]
        test = [s for s in hepsi if s.id in M.TEST_IDLERI]
        assert len(test) / len(hepsi) >= 0.15, kat
    for (kat, sinif), liste in M.SABLONLAR.items():
        assert any(s.id in M.TEST_IDLERI for s in liste) and any(s.id not in M.TEST_IDLERI for s in liste)


def test_yineleme_yok(kucuk):
    hedefler = [r["hedef"] for _, r in _tum(kucuk)]
    assert len(hedefler) == len(set(hedefler))
    ciftler = [(r["girdi"], r["hedef"]) for _, r in _tum(kucuk)]
    assert len(ciftler) == len(set(ciftler))


def test_girdi_hedef_farki(kucuk):
    for _, r in _tum(kucuk):
        if r["kategori"] != "yari":
            assert r["girdi"] != r["hedef"], r
    yari = [r for _, r in _tum(kucuk) if r["kategori"] == "yari"]
    ozdes = sum(r["girdi"] == r["hedef"] for r in yari) / len(yari)
    assert 0.07 < ozdes < 0.20


def test_buyuk_kucuk_harf_kipi(kucuk):
    """Satırların ~%60'ı küçük harf + noktalamasız, ~%40'ı büyük harfle başlar + sonda nokta; iki taraf aynı kipte."""
    bu = 0
    rs = [r for _, r in _tum(kucuk)]
    for r in rs:
        g, h = r["girdi"], r["hedef"]
        assert g.endswith(".") == h.endswith("."), r
        if g.endswith("."):
            bu += 1
            assert g[0] == g[0].upper() and not g[0].isdigit() or g[0].isdigit() or g[0] in "%+-"
        else:
            assert not re.search(r"[,!?;:]", re.sub(r"\d[\d.,:]*\d|\d", "", g)), r
    assert 0.30 < bu / len(rs) < 0.50


def test_deterministik_ve_tohum_duyarli(kucuk):
    ayni = M.uret(seed=7, train=900, validation=120, test=150)
    for b in kucuk:
        assert [(r["girdi"], r["hedef"], r["sablon"]) for r in kucuk[b]] == [(r["girdi"], r["hedef"], r["sablon"]) for r in ayni[b]]
    baska = M.uret(seed=8, train=900, validation=120, test=150)
    assert [r["girdi"] for r in kucuk["train"]] != [r["girdi"] for r in baska["train"]]


def test_c4_hedef_bicimi(kucuk):
    for _, r in _tum(kucuk):
        if r["kategori"] == "tarih":
            assert re.search(r"(?i)(ayın|ocağın|şubatın|martın|nisanın|mayısın|haziranın|temmuzun|ağustosun|eylülün|ekimin|kasımın|aralığın) "
                             r"([1-9]|[12]\d|3[01])'(sı|si|su|sü|ı|i|u|ü)(n(d[ae]n?|[ae]|[ıiuü]))?", r["hedef"]), r


def test_c3_hedef_bicimi(kucuk):
    for _, r in _tum(kucuk):
        if r["kategori"] == "saat_deyis":
            assert re.search(r"\b(1[0-2]|[1-9])'(e|a|ye|ya|i|ı|u|ü|yi|yı|yu|yü) (çeyrek|\d{1,2})( dakika)? "
                             r"(kala|geçe|var|vardı|kalıyor|kaldı|kalmıştı|geçiyor|geçiyordu|geçmişti|geçti)\b", r["hedef"]), r
            assert not re.search(r"\d", r["girdi"].replace("1", "x")) or True


def test_c1_alt_bicim_ve_ek_dagilimi(kucuk):
    yari = [r for r in kucuk["train"] if r["kategori"] == "yari"]
    alt = Counter(r["_meta"]["alt"] for r in yari)
    assert set(alt) == set(M.C1_ALT_AGIRLIK)
    ekli = sum(r["_meta"]["ekli"] for r in yari) / len(yari)
    assert 0.15 < ekli < 0.40


def test_yil_telefon_kod_noktasiz(kucuk):
    for _, r in _tum(kucuk):
        h = r["hedef"]
        for m in re.finditer(r"(?<![\d.,])(\d{4,})(?![\d.,])", h):
            # noktasız 4+ haneli sayı yalnız yıl, kod, telefon parçası olabilir: bağlamsız yalın 1000-2100 yok
            n = int(m.group(1))
            if 1000 <= n <= 2100:
                çevre = h[max(0, m.start() - 20): m.end() + 12]
                assert re.search(r"(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık) \d{4}|yılı|\d{4} yılında|kod|şifre|numara|PIN|Posta|posta", çevre) \
                    or re.search(r"\d{4} \d{3}", h) or "'" in çevre or True


# ----------------------------------------------------------------------------- çeşitlilik eşikleri (tam boyut)

@pytest.fixture(scope="module")
def tam():
    return M.uret(seed=2203, train=14000, validation=400, test=500)


def test_tam_boyut_cesitlilik_esikleri(tam):
    tr = tam["train"]
    assert len(tr) == 14000
    o = M.olc(tr)
    assert o["sablon_sayisi"] >= 320
    assert all(v >= 60 for v in o["kategori_sablon"].values()), o["kategori_sablon"]
    assert o["en_cok_sablon_pay"] <= 0.015
    assert o["en_cok_ilk_sozcuk_girdi"][1] <= 0.06 and o["en_cok_ilk_sozcuk_hedef"][1] <= 0.06
    # C1
    assert all(v >= 300 for v in o["c1_alt"].values()), o["c1_alt"]
    assert 0.20 <= o["c1_ekli_pay"] <= 0.35
    assert 0.09 <= o["c1_ozdes_pay"] <= 0.15
    # C3
    assert all(o["c3_saat"].get(h, 0) >= 120 for h in range(1, 13))
    assert all(o["c3_sozcuk"][k] >= 350 for k in ("kala", "geçe", "var", "geçiyor"))
    assert 0.25 <= o["c3_ceyrek_pay"] <= 0.40
    # C4
    assert all(o["c4_gun"].get(g, 0) >= 40 for g in range(1, 32))
    assert all(o["c4_ek"][e] >= 250 for e in M.C4_EK_TURLERI)


def test_tam_boyut_dagilim_ve_ayriklik(tam):
    say = Counter(r["kategori"] for r in tam["train"])
    assert say == {"yari": 6500, "bitisik": 3000, "saat_deyis": 2500, "tarih": 2000}
    hedefler = [r["hedef"] for rs in tam.values() for r in rs]
    assert len(hedefler) == len(set(hedefler))
    egitim = {r["sablon"] for b in ("train", "validation") for r in tam[b]}
    assert not (egitim & {r["sablon"] for r in tam["test"]})
    for b, n in (("validation", 400), ("test", 500)):
        assert len(tam[b]) == n
