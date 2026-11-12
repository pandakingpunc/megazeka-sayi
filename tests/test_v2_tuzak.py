"""v2 B kaynağı (tuzaklar) testleri: training/v2_tuzak.py"""
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

import pytest  # noqa: E402

import v2_tuzak as T  # noqa: E402

TRAIN, VAL, TEST = 10000, 300, 400


@pytest.fixture(scope="module")
def veri():
    sonuc, atilan = T.uret_hepsi(2202, TRAIN, VAL, TEST)
    return sonuc


def _hepsi(veri):
    return [(ad, r) for ad, s in veri.items() for r in s]


def _negatifler(veri):
    return [(ad, r) for ad, r in _hepsi(veri) if T.olgu_of(r["sablon"]) != "karsit"]


def _karsitlar(veri):
    return [(ad, r) for ad, r in _hepsi(veri) if T.olgu_of(r["sablon"]) == "karsit"]


def test_bolum_boyutlari(veri):
    assert {k: len(v) for k, v in veri.items()} == {"train": TRAIN, "validation": VAL, "test": TEST}


def test_satir_sozlesmesi_ve_sablon_kimligi(veri):
    for _, r in _hepsi(veri):
        assert set(r) == {"girdi", "hedef", "kategori", "sablon"}
        assert re.fullmatch(r"v2b-(bin|ikinciel|yuz|sira|onalti|deyim|ozelad|sozcuk|birim|kesir|karsit)-\d{3}",
                            r["sablon"]), r
    assert "v2b-bin-017" in T.SABLON_ID


def test_negatiflerde_girdi_esittir_hedef(veri):
    for _, r in _negatifler(veri):
        assert r["girdi"] == r["hedef"], r
        assert not re.search(r"[\d%]", r["girdi"]), r


def test_karsitlarda_girdi_farkli_ve_hedefte_rakam(veri):
    kar = _karsitlar(veri)
    assert kar
    for _, r in kar:
        assert r["girdi"] != r["hedef"], r
        assert re.search(r"\d", r["hedef"]), r
        assert not re.search(r"\d", r["girdi"]), r      # girdi Varlik.sozlu'dan: rakam yok


def test_kategori_alanlari(veri):
    es = {"bin", "yuz", "onalti"}
    pozitif = {"para", "olcu", "sira", "kardinal", "yuzde", "saat", "ondalik", "karisik"}
    for _, r in _hepsi(veri):
        olgu = T.olgu_of(r["sablon"])
        if olgu == "karsit":
            assert r["kategori"] in pozitif, r
        elif olgu in es:
            assert r["kategori"] == "negatif_es", r
        else:
            assert r["kategori"] == "negatif_kalip", r


def test_yanlis_negatif_denetimi_tum_negatifler(veri):
    for _, r in _negatifler(veri):
        assert T.denetle(r["girdi"]) == [], r


def test_denetim_kurallari_ihlali_yakalar():
    kotu = ["on iki kişi geldi", "iki kilo elma aldım", "saat üçte buluşalım", "üçüncü katta oturuyor",
            "beş altı kişi geldi", "yüz lira ver", "ikinci sınıf öğrencisi", "yüzde on indirim", "bin kişi geldi",
            "eksi beş derece", "otuz gün sonra", "ona kadar say", "iki yüz gram", "yirmi beş lira", "on dakika sürdü",
            "dokuz kuruş", "bir buçuk saat", "kırk kişi toplandı", "yüz metre koştu", "mayısın on beşinde"]
    for c in kotu:
        assert T.denetle(c), c


def test_denetim_kurallari_gecerli_cumleleri_kabul_eder():
    iyi = ["taksiye bin de gel", "üçüncü oldu", "ikinci el telefon", "üçte biri", "yemeğini yedi", "bu yüzden gelmedi",
           "masanın altında", "iki kişi geldi", "üç gün sonra", "onbaşı geldi", "ikide bir arıyor", "onlar geldi",
           "ona söyle", "dört dörtlük bir sunum", "kırk yılın başı geldin", "Dokuz Eylül Üniversitesi'nde okuyor",
           "koyunları kırk", "ikincisi daha güzel", "birincilik ödülü", "beşi birden girdi"]
    for c in iyi:
        assert T.denetle(c) == [], (c, T.denetle(c))


def test_bayt_siniri(veri):
    for _, r in _hepsi(veri):
        assert len(r["girdi"].encode("utf-8")) <= 180, r
        assert len(r["hedef"].encode("utf-8")) <= 180, r


def test_sablon_ayrikligi(veri):
    egitim = {r["sablon"] for ad, r in _hepsi(veri) if ad in ("train", "validation")}
    sinav = {r["sablon"] for ad, r in _hepsi(veri) if ad == "test"}
    assert egitim and sinav
    assert not (egitim & sinav)
    assert sinav <= T.TEST_SABLONLARI
    assert not (egitim & T.TEST_SABLONLARI)
    for olgu, lst in T.SABLONLAR.items():
        n_test = sum(1 for s in lst if s.id in T.TEST_SABLONLARI)
        assert n_test >= 0.15 * len(lst), (olgu, n_test, len(lst))
        assert any(r["sablon"].split("-")[1] == olgu for ad, r in _hepsi(veri) if ad == "test"), olgu


def test_yinelenme_yok(veri):
    ciftler = [(r["girdi"], r["hedef"]) for _, r in _hepsi(veri)]
    assert len(ciftler) == len(set(ciftler))
    hedefler = [r["hedef"] for _, r in _hepsi(veri)]
    assert len(hedefler) == len(set(hedefler))


def test_deterministik():
    a, _ = T.uret_hepsi(2202, 1500, 100, 150)
    b, _ = T.uret_hepsi(2202, 1500, 100, 150)
    c, _ = T.uret_hepsi(2203, 1500, 100, 150)
    assert a == b
    assert a != c


def test_harf_kipi_dagilimi(veri):
    tr = veri["train"]
    buyuk = [r for r in tr if r["girdi"][-1] in ".?!"]
    oran = len(buyuk) / len(tr)
    assert 0.34 <= oran <= 0.46, oran
    for r in tr:
        if r["girdi"][-1] in ".?!":
            assert r["girdi"][0] == T.ilk_harfi_buyut(r["girdi"][0]) or not r["girdi"][0].isalpha(), r
        else:
            assert not re.search(r"[.,!?;:\"…']", r["girdi"].replace("'", "")) or r["sablon"].startswith("v2b-karsit"), r
            assert r["girdi"] == T.lower_tr(r["girdi"]), r


def test_cesitlilik_esikleri_train(veri):
    tr = veri["train"]
    o = T.olcumler(tr)
    assert o["sablon_sayisi"] >= 400
    assert o["en_buyuk_sablon_payi"] <= 0.01
    assert o["en_buyuk_ilk_sozcuk_payi"] <= 0.06
    assert 0.25 <= o["kisa_2_5_payi"] <= 0.40, o["kisa_2_5_payi"]
    for olgu in ("bin", "ikinciel", "yuz", "sira", "onalti", "deyim", "ozelad", "sozcuk", "birim", "kesir"):
        assert o["olgu_satir"][olgu] >= 500, olgu
    assert o["ayri_deyim"] >= 80
    assert o["bin_cekim_sayisi"] >= 25
    assert 0.15 <= o["karsit_payi"] <= 0.20


def _normal(t):
    return " ".join(T.belirteclestir(t))


@pytest.fixture(scope="module")
def bolme_siz_cumleler():
    cikti = {}
    kars = {}
    for sb, (g, h, _, _) in T.tum_cumleler(tekrar=200):
        if sb.karsit:
            kars[_normal(g)] = h
        else:
            cikti[_normal(g)] = sb.olgu
    return cikti, kars


def _bulunur(ifade, cumleler):
    kalip = re.compile(r"(?<!\w)" + re.escape(_normal(ifade)))
    return any(kalip.search(c) for c in cumleler)


SPEC_B_ORNEKLERI = {
    "bin": ["taksiye bin de gel", "otobüse bin hemen", "hadi bin", "sen de bin", "bin şu arabaya", "atla bin",
            "binin", "binelim", "binsene", "binmeden önce"],
    "ikinciel": ["ikinci el telefonlar", "ikinci elden aldım", "ikinci ele düştü", "bu araba ikinci el"],
    "yuz": ["bu yüzden", "o yüzden", "senin yüzünden", "yüzüme", "yüzleşti", "yüzsüz", "güler yüzlü", "yüz yüze",
            "yüzdük", "yüzüyor", "yüzmeye gitti", "yüz bakalım"],
    "sira": ["üçüncü oldu", "birinci geldi", "ikincisi", "üçüncüsü daha iyi", "sonuncu", "birincilik"],
    "onalti": ["masanın altında", "altını", "altından", "yemeğini yedi", "yediler", "yedik", "ona ", "onu ",
               "onun ", "onda ", "ondan ", "onlar ", "kırk", "dokuz doğur"],
    "deyim": ["dört dörtlük", "iki arada bir derede", "kırk yılın başı", "kırk fırın ekmek", "yedi kat yabancı",
              "bir taşla iki kuş", "iki ayağını bir pabuca", "dokuz köyden kovulur", "bin pişman", "bin bir türlü",
              "yüz bul", "beş para etmez", "üç aşağı beş yukarı", "iki gözüm", "bir elin nesi var iki elin sesi var",
              "iki dirhem bir çekirdek", "dokuz canlı", "yedi düvel", "kırk yıllık dost",
              "on parmağında on marifet", "sıfırı tüket", "sıfırdan başla", "sıfır araba", "bire bir", "birebir",
              "bir an önce", "bir daha", "tek bir", "bir de", "birdenbire"],
    "ozelad": ["Dokuz Eylül Üniversitesi", "Ondokuz Mayıs Üniversitesi", "Yüzüncü Yıl Üniversitesi", "Beşiktaş",
               "Yedikule", "Üçkuyular", "Dörtyol", "Kırklareli", "Binali", "Altınordu", "Yedi Cüceler",
               "Üç Silahşörler", "Kırk Haramiler", "Binbir Gece Masalları", "Beş Hececiler", "Yediler",
               "Kırklar Dağı"],
    "sozcuk": ["onbaşı", "yüzbaşı", "binbaşı", "kırkayak", "üçgen", "dörtgen", "beşgen", "altıgen", "ikiz", "üçüz",
               "dörtnala", "yediveren", "ikilem", "ikili", "üçlü", "beşli", "onluk", "yüzlük", "binlik", "ikişer",
               "üçer", "beşer", "onar", "ikimiz", "üçümüz", "beşi birden", "onlarca", "yüzlerce", "binlerce"],
    "birim": ["tonlarca yük", "kalorisi düşük", "inç inç", "dakikalarca", "saniyesinde", "liranın değeri", "kasımda",
              "metrelerce"],
    "kesir": ["yarım saat", "yarım yamalak", "çeyrek altın", "çeyrek final", "üçte biri"],
}


@pytest.mark.parametrize("olgu", sorted(SPEC_B_ORNEKLERI))
def test_spec_b_ornekleri_uretilebilir(olgu, bolme_siz_cumleler):
    cumleler = [c for c, o in bolme_siz_cumleler[0].items()]
    eksik = [x for x in SPEC_B_ORNEKLERI[olgu] if not _bulunur(x, cumleler)]
    assert not eksik, eksik


def test_spec_b_karsit_ornekleri_uretilebilir(bolme_siz_cumleler):
    kars = bolme_siz_cumleler[1]
    beklenen = {"bin lira ver": "1.000 TL ver", "yüz metre yüzdü": "100 m yüzdü",
                "ikinci katta oturuyor": "2. katta oturuyor", "yedi yüz gram yedi": "700 g yedi",
                "on kişi ona baktı": "10 kişi ona baktı", "altı yüz liranın altında": "600 TL'nin altında"}
    for girdi, hedef in beklenen.items():
        bulundu = [(c, h) for c, h in kars.items() if c.startswith(girdi) or c.endswith(girdi) or f" {girdi} " in c]
        assert any(h.startswith(hedef) or h.endswith(hedef) or f" {hedef} " in h or hedef in h
                   for _, h in bulundu), (girdi, bulundu[:3])


def test_karsitlar_yalniz_kur_islevleriyle(veri):
    # her karşıt satırın hedefindeki sayısal parça Varlik.yazili'dir: girdiyle birlikte yeniden kurulabilir
    from megazeka_sayi import varliklar as V
    assert V.kur_para(lira=1000).yazili == "1.000 TL"
    for _, r in _karsitlar(veri)[:200]:
        assert re.search(r"\d", r["hedef"]) and r["girdi"] != r["hedef"]
    # her karşıt şablonun tüm slotları KS içinde; KS işlevleri Varlik döndürür
    import random
    rng = random.Random(1)
    for ad, f in T.KS.items():
        v = f(rng, None)
        assert isinstance(v, V.Varlik), ad


def test_karsit_ve_negatif_taşıyıcıları_ayri(veri):
    # karşıt taşıyıcı metinlerde dönüşmesi gereken ikinci bir sayı bulunmaz (denetim § işaretiyle)
    import random
    rng = random.Random(3)
    for sb in T.SABLONLAR["karsit"]:
        for i in range(30):
            _, _, _, ta = T.render(sb, rng, i % 2 == 0)
            assert T.denetle(ta) == [], (sb.id, ta)


def test_kisa_cumle_payi_hedef_olgularda(veri):
    o = T.olcumler(veri["train"])
    for olgu in ("bin", "ikinciel", "yuz"):
        assert 0.45 <= o["olgu_kisa_pay"][olgu] <= 0.60, (olgu, o["olgu_kisa_pay"][olgu])
    assert o["olgu_kisa_sablon"]["bin"] >= 60
    assert o["olgu_kisa_sablon"]["ikinciel"] >= 35
    assert o["olgu_kisa_sablon"]["yuz"] >= 35
    # hedef olgularda kısa cümleler sarmalayıcısızdır (açılış/kapanış eki yok)
    ekler = {x.lower() for x in T.ACILISLAR} | {x.lower() for x in T.KAPANISLAR}
    for r in veri["train"]:
        if T.olgu_of(r["sablon"]) in ("bin", "ikinciel", "yuz") and T.SABLON_ID[r["sablon"]].kisa:
            t = " ".join(T.belirteclestir(r["girdi"]))
            assert not any(t.startswith(e.lower() + " ") or t.endswith(" " + e.lower()) for e in ekler), r


def test_kisa_ornekler_bulunur(bolme_siz_cumleler):
    cumleler = list(bolme_siz_cumleler[0])
    for x in ["otobüse bin hemen", "taksiye bin de gel", "bin hadi gidiyoruz", "motora bin arkama",
              "bu yüzden geç kaldım", "bu telefon ikinci el mi", "arabayı ikinci elden aldık", "bu yüzden gelmedim"]:
        assert _bulunur(x, cumleler), x


def test_karsit_kisa_ornekler(bolme_siz_cumleler):
    kars = bolme_siz_cumleler[1]
    for g, h in {"bin lira ver": "1.000 TL ver", "yüz metre kaldı": "100 m kaldı",
                 "ikinci kat burası": "2. kat burası"}.items():
        assert kars.get(g) == h, (g, [c for c in kars if g.split()[0] in c][:3])


def test_onalti_tasiyici_cesitliligi(veri):
    o = T.olcumler(veri["train"])
    assert o["olgu_sablon"]["onalti"] >= 90
    assert o["onalti_en_buyuk_sablon_payi"] <= 0.03


def test_bucuk_yalniz_sayi_olmayan_kullanim(veri):
    bucuk = [r for r in veri["train"] if T.olgu_of(r["sablon"]) == "kesir" and "buçuk" in r["girdi"].lower()]
    assert bucuk
    for r in bucuk:
        t = T.belirteclestir(r["girdi"])
        for i, w in enumerate(t):
            if w.startswith("buçuk"):
                assert i == 0 or t[i - 1] not in T._KARD and t[i - 1] not in T.KARD_FORM, r
