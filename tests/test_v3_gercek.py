"""v3 D sözleşmesi, gerçek cümle süzgeci, karar örnekleri ve güvenli birleştirme."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "training"))

import v3_gercek as D  # noqa: E402
import v3_birlestir as B  # noqa: E402


@pytest.fixture(scope="module")
def uretim():
    # Eksik gerçek kaynak sessizce atlanmaz: bu fixture gerçek kotayı da denetler.
    sonuc, ek = D.uret_hepsi()
    ek["seed"] = 3303
    return sonuc, ek


@pytest.fixture(scope="module")
def veri(uretim):
    return uretim[0]


def hepsi(veri):
    return [r for s in veri.values() for r in s]


def test_sozlesme_ve_bayt(veri):
    for r in hepsi(veri):
        assert set(r) == {"girdi", "hedef", "kategori", "sablon"}, r
        assert re.match(r"v3d-d[1-8]-", r["sablon"]), r
        assert all(isinstance(v, str) and v for v in r.values()), r
        assert all(len(r[k].encode("utf-8")) <= 180 for k in ("girdi", "hedef")), r


def test_bolumler_arasi_girdi_hedef_ve_sablon_ayrikligi(veri):
    for alan in ("girdi", "hedef", "sablon"):
        kumeler = {b: {r[alan] for r in s} for b, s in veri.items()}
        for i, b in enumerate(D.BOLUMLER):
            for diger in D.BOLUMLER[i + 1:]:
                assert not kumeler[b] & kumeler[diger], (alan, b, diger)
    for s in veri.values():
        assert len({r["girdi"] for r in s}) == len(s)


def test_d1_bicimleri_ayni_bolumde_ve_md5e_gore(veri):
    sahip = {}
    ozgunler = {}
    for t in D.CV_YOLU.read_text(encoding="utf-8-sig").splitlines():
        ozgunler.setdefault(D.ozet(t.strip()), t.strip())
    for b, s in veri.items():
        for r in s:
            if D.olgu_of(r) != "D1":
                continue
            oz = D.ozet(r["girdi"])
            assert sahip.setdefault(oz, b) == b
            kova = int(hashlib.md5(ozgunler[oz].encode("utf-8")).hexdigest(), 16) % 100
            assert b == ("test" if kova < 6 else "validation" if kova < 12 else "train")
            assert r["girdi"] == r["hedef"]
            assert D.d1_grubu(r["girdi"]) is not None
    s = [r for r in veri["train"] if D.olgu_of(r) == "D1"]
    duz = sum(D.cv_duz(r["girdi"]) == r["girdi"] for r in s)
    assert .45 <= duz / len(s) <= .55


@pytest.mark.parametrize("girdi", [
    "Ona bir şey söylemedim.", "Onu burada bekliyorum.", "Onunla akşam buluştuk.",
    "Onlardan haber alamadık.", "Onlarınki evde kalmış.", "Biraz sonra birlikte geliriz.",
    "Birbirimizin sözünü kesmeyelim.", "Yüzünü usulca yıkadı.", "Masanın altında uyudu.",
    "Altın yüzük kaybolmuş.", "Benden önce yediler.", "Arabaya bindik.", "Binmeden önce bekledik.",
    "Yeni bina tamamlandı.", "Koyunları kırkmak kolay değil.", "Beşikte uyuyor.",
    "İkiz kardeşler bahçede.", "Dörtnala koşuyordu.", "Eksikleri sonra tamamlarız.",
    "Yarım ekmek aldım.", "Çeyrek altın hediye etti.", "Milyonlarca insan bekliyor.",
])
def test_d1_guvenli_bicimler(girdi):
    assert D.d1_grubu(girdi) is not None


@pytest.mark.parametrize("girdi", [
    "Yüz kişi geldi.", "Yedi çocuk kapıda.", "Altı adam geldi.", "Bin kişi bekliyor.",
    "Bine kadar saydım.", "Bini bana ver.", "İkinci maddeyi okudu.", "Altıncı sırada bekle.",
    "Sıfır kişi geldi.", "Elli gün geçti.", "Bir buçuk saat bekle.", "Bir milyon insan geldi.",
    "Bir yirmi dakika bekle.", "İki yüz metre yol var.", "Bir liraya aldım.", "Saat bir oldu.",
    "Saat ona kadar bekle.", "Ona kadar say.", "Her ayın biri burada olurum.", "Sayı içermiyor.",
    "Onbaşı geldi.", "Bir onbaşı geldi.", "Yüzü ve on kişi göründü.", "Yarın 5 kişi geliyor.",
])
def test_d1_belirsiz_ve_sayisal_bicimler_alinmaz(girdi):
    assert D.d1_grubu(girdi) is None


def test_dislamanin_butun_bicimleri(veri, tmp_path):
    dis = D.haric_yukle()
    assert dis
    assert all(D.ozet(r[k]) not in dis for r in hepsi(veri) for k in ("girdi", "hedef"))
    cv = tmp_path / "cv.txt"
    cv.write_text('Ona sessizce baktım.\nOnunla konuştum.\n', encoding="utf-8")
    h, sayim = D.d1_yukle(cv, {D.ozet('Ona sessizce baktım.')})
    assert sayim["haric"] == 1
    assert all(t != "Ona sessizce baktım." for v in h.values() for g in v.values() for _, t in g)


def test_dis_liste_hatasi_gizlenmez(tmp_path):
    with pytest.raises(FileNotFoundError):
        D.haric_yukle(tmp_path / "yok.txt")
    p = tmp_path / "bozuk.txt"
    p.write_text("cümle\n", encoding="utf-8")
    with pytest.raises(ValueError):
        D.haric_yukle(p)


def test_d2_soz_ayrikligi_ve_yalin_tasiyici(veri):
    assert len(D.SOZLER) >= 250
    assert len(D.SOZLER) == len(set(D.SOZLER))
    bol = D.soz_bolumleri(3303)
    assert len(bol["test"]) / len(D.SOZLER) >= .15
    for b in D.BOLUMLER:
        satirlar = [r for r in veri[b] if D.olgu_of(r) == "D2"]
        for no, soz in bol[b]:
            aday = [r for r in satirlar if r["sablon"].split("-")[2] == f"{no:03d}"]
            assert aday, (b, soz)
            assert any(r["sablon"].endswith("-01") for r in aday), (b, soz)
            if D.ozet(soz) not in D.haric_yukle():
                assert any(r["sablon"].endswith("-00") for r in aday), (b, soz)
            assert all(r["girdi"] == r["hedef"] for r in aday)


def test_esiklerin_tamami(uretim):
    sonuc, ek = uretim
    e = D.esikler(sonuc, ek)
    assert all(x["gecti"] for x in e.values()), {k: v for k, v in e.items() if not v["gecti"]}


def test_determinist_veri_ve_dosya(uretim, tmp_path):
    a, _ = D.uret_hepsi()
    assert a == uretim[0]
    for b, s in a.items():
        p, q = tmp_path / (b + "-a.jsonl"), tmp_path / (b + "-b.jsonl")
        D.yaz(p, s)
        D.yaz(q, uretim[0][b])
        assert hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256(q.read_bytes()).digest()
        assert b"\r" not in p.read_bytes()
    assert D.sablon_bolumleri(3303) != D.sablon_bolumleri(3304)


def test_sablon_kimlikleri_gercek_govdelere_karsilik_gelir():
    for o, lst in D.SABLONLAR.items():
        assert len(lst) == len({s.id for s in lst})
        # Aynı tür ve aynı taşıyıcı, yeni kimlikle şişirilmez.
        assert len(lst) == len({(s.tur, s.metin) for s in lst}), o
    for o in D.SABLONLAR:
        bol = D.sablon_bolumleri(3303)
        egitim = {D.lower_tr(s.metin) for b in ("train", "validation") for s in bol[b][o]}
        test = {D.lower_tr(s.metin) for s in bol["test"][o]}
        assert not egitim & test
        assert not test & D.ornekler(govdeler=True)[o]


def test_noktalama_ve_cumle_disindaki_metin_korunur(veri):
    for r in hepsi(veri):
        if D.olgu_of(r) == "D5":
            # Kesme, sıra noktası, ondalık ve aralık sayı gösteriminin parçasıdır.
            def iz(t):
                return re.sub(r"[^\"“”:!?…]", "", t)
            assert iz(r["girdi"]) == iz(r["hedef"]), r
            assert not re.fullmatch(r"\d{4}\.", r["hedef"]), r
    assert D.cek("saat", "bulunma") == ("saatte", "te")
    assert D.cek("saat", "ayrilma") == ("saatten", "ten")
    assert not any(re.search(r"\bsaat(?:ta|tan)\b", r["girdi"]) for r in hepsi(veri))


# Beklenen etiketler testte elle seçilir; üreteçte hedefler sayısal kuruculardan gelir.
ORNEKLER = {
    "D3": {
        "bir elli kuruş": "bir 50 kuruş", "bir yirmi beş kuruşluk": "bir 25 kuruşluk",
        "bir yüz liralık çıkardı": "bir 100 TL'lik çıkardı", "iki tane elli kuruşluk": "iki tane 50 kuruşluk",
        "bir elli boyunda": "1,50 boyunda", "bir yetmiş beş boyunda": "1,75 boyunda",
        "bir seksen boyundaki adam": "1,80 boyundaki adam", "bir buçuk iki saat": "1,5-2 saat",
        "iki buçuk üç kilo": "2,5-3 kg", "bir buçuk iki ay": "1,5-2 ay",
        "bir on dakika sonra": "bir 10 dakika sonra", "bir yirmi kişi kadar": "bir 20 kişi kadar",
        "beş on dakika": "5-10 dakika", "on on beş kişi": "10-15 kişi",
        "her biri üç liradan": "her biri 3 TL'den",
    },
    "D4": {
        "sekiz kişi iki gündür çatıda uğraşıyordu": "sekiz kişi iki gündür çatıda uğraşıyordu",
        "dört katlı otelin önünde durup biraz bekledik": "dört katlı otelin önünde durup biraz bekledik",
        "altı kişilik orkestra bütün gece prova yaptı": "altı kişilik orkestra bütün gece prova yaptı",
        "üç mektubunu cevapsız bıraktı ve sessizce uzaklaştı": "üç mektubunu cevapsız bıraktı ve sessizce uzaklaştı",
        "iki gece önce kapımızı çalıp yardım istedi": "iki gece önce kapımızı çalıp yardım istedi",
        "yolculuk dokuz saat sürdü sonunda eve vardık": "yolculuk dokuz saat sürdü sonunda eve vardık",
        "sekiz yaşında bir çocuk kapının önünde bekliyordu": "sekiz yaşında bir çocuk kapının önünde bekliyordu",
        "bu evde yedi sene oturdum sonra taşındım": "bu evde yedi sene oturdum sonra taşındım",
        "on iki kişi geldi ama kimse konuşmak istemedi": "12 kişi geldi ama kimse konuşmak istemedi",
        "kırk yaşında adam yavaşça ayağa kalkıp dışarı çıktı": "40 yaşında adam yavaşça ayağa kalkıp dışarı çıktı",
        "yirmi senedir burada oturuyorum ama kimseyi tanımıyorum": "20 senedir burada oturuyorum ama kimseyi tanımıyorum",
        "iki saat on beş dakika sürdü ve sonunda hepimiz eve döndük": "2 saat 15 dakika sürdü ve sonunda hepimiz eve döndük",
    },
    "D5": {
        '"Kırk yaşında adam böyle yapar mı?" dedi.': '"40 yaşında adam böyle yapar mı?" dedi.',
        "Yetmiş lira aylık…": "70 TL aylık…", "Şimdi ne istersin? Kırk beş mi?": "Şimdi ne istersin? 45 mi?",
        "Yüz ellisi benim elbette…": "150'si benim elbette…",
        'Yanındakine: "Elli adım var." dedi.': 'Yanındakine: "50 adım var." dedi.',
        "Yüz altmış dört.": "164.", "İki yüz on sekiz.": "218.",
    },
    "D6": {
        "Yarın dokuzda gelin.": "Yarın 9'da gelin.", "akşam yedide buluşalım": "akşam 7'de buluşalım",
        "Saat henüz dörttü.": "Saat henüz 4'tü.", "saat beşti": "saat 5'ti", "saat on ikiydi": "saat 12'ydi",
        "toplantı üçteymiş": "toplantı 3'teymiş",
        "yarın ona söylerim": "yarın ona söylerim", "akşam onu gördüm": "akşam onu gördüm",
        "sabah yedi ve çıktı": "sabah yedi ve çıktı",
    },
    "D7": {
        "yüz elli liram var": "150 TL'm var", "elli lirasını peşin aldı": "50 TL'sini peşin aldı",
        "borcun yüz altmış beş liradır": "borcun 165 TL'dir", "otuz beş kuruşum var": "35 kuruşum var",
        "on lirası kaldı": "10 TL'si kaldı", "beş liramız": "5 TL'miz", "fiyatı yirmi liraydı": "fiyatı 20 TL'ydi",
        "yirmi lira idi": "20 TL idi", "doksan para": "90 para", "kırk okka": "40 okka",
        "on beş arşın": "15 arşın", "yirmi dönüm": "20 dönüm", "elli mecidiye": "50 mecidiye", "otuz altın": "30 altın",
    },
    "D8": {
        **{t: t for t in ("üçüncü uykusuz geceyi", "ikinci büyük şehri", "ikinci kaptan", "birinci subay", "üçüncü kâtip",
                          "ikinci müdür", "altmışlık bir adam", "ellilik kadın", "yetmişlik ihtiyar", "kırklık",
                          "ellişer kuruşa", "altmışar kuruşla", "ikişer ikişer", "onar lira")},
        "üçüncü kat": "3. kat", "ikinci madde": "2. madde", "altmışlık bir kutu": "60'lık bir kutu",
        "yüzde ellilik": "%50'lik",
    },
}


@pytest.mark.parametrize("olgu", list(ORNEKLER))
def test_spec_ornekleri_birebir(olgu, veri):
    kurulan = {r["girdi"]: r["hedef"] for r in D.ornekler()[olgu]}
    uretilen = {r["girdi"]: r["hedef"] for r in hepsi(veri) if D.olgu_of(r) == olgu}
    dis = D.haric_yukle()
    for g, h in ORNEKLER[olgu].items():
        assert kurulan.get(g) == h, (olgu, g, kurulan.get(g))
        if D.ozet(g) in dis:
            # SPEC'in kendi örneği bağımsız ölçüm kümesindeyse dışlama (SPEC D1) üretimden önce gelir.
            assert g not in uretilen, (olgu, g)
        else:
            assert uretilen.get(g) == h, (olgu, g)


def test_d2_spec_sozleri():
    for t in ("kırk yılda bir", "bin bilsen de bir bilene danış", "iki cambaz bir ipte oynamaz",
              "dokuz köyden kovulur", "yüz yüze", "üç beş kuruş", "kırk yıl hatırı var",
              "bin nasihatten bir musibet yeğdir", "yedi kat yerin dibi", "otuz iki dişini göstermek"):
        assert t in D.SOZLER


@pytest.mark.parametrize("tur,yazili,sozlu", [
    ("m", "TL'm", "liram"), ("n", "TL'n", "liran"), ("si", "TL'si", "lirası"),
    ("miz", "TL'miz", "liramız"), ("niz", "TL'niz", "liranız"), ("leri", "TL'leri", "liraları"),
    ("sini", "TL'sini", "lirasını"), ("dir", "TL'dir", "liradır"),
    ("di", "TL'ydi", "liraydı"), ("mis", "TL'ymiş", "liraymış"),
    ("yonelme", "TL'ye", "liraya"), ("ayrilma", "TL'den", "liradan"), ("lik", "TL'lik", "liralık"),
])
def test_tl_ince_sesli_ve_kaynastirma(tur, yazili, sozlu):
    p = D.para(5, tur)
    assert p.yazili == "5 " + yazili
    assert p.sozlu == "beş " + sozlu


@pytest.mark.parametrize("n,ek,yaz,soz", [
    (4, "di", "4'tü", "dörttü"), (5, "di", "5'ti", "beşti"), (12, "di", "12'ydi", "on ikiydi"),
    (6, "mis", "6'ymış", "altıymış"), (9, "dir", "9'dur", "dokuzdur"),
    (3, "deymis", "3'teymiş", "üçteymiş"), (10, "deymis", "10'daymış", "ondaymış"),
    (4, "yonelme", "4'e", "dörde"), (6, "yonelme", "6'ya", "altıya"),
])
def test_saat_ekleri(n, ek, yaz, soz):
    p = D.sayi(n, ek)
    assert (p.yazili, p.sozlu) == (yaz, soz)


def satir(g, h=None, kaynak="a", kategori="kardinal"):
    return {"girdi": g, "hedef": g if h is None else h, "kategori": kategori, "sablon": "deneme", "kaynak": kaynak}


def test_birlestirme_iki_tarafli_celiski_dis_ozet_ve_bolum_korumasi():
    eski = {"train": [satir("elli kişi", "50 kişi"), satir("Ona bak."), satir("testte tut"),
                       satir("altmışlık bir adam", "60'lık bir adam"), satir("kalacak")],
            "validation": [satir("elli kişi", "elli kişi"), satir("doğrulamada tut")]}
    yeni = {"train": [satir("elli kişi", "50 kişi"), satir("ona bak"), satir("doğrulamada tut")],
            "validation": [], "test": [satir("testte tut")]}
    sonuc, rapor = B.birlestir(eski, yeni, {D.ozet("Ona bak.")})
    assert [r["girdi"] for r in sonuc["train"]] == ["kalacak"]
    assert {r["girdi"] for r in sonuc["validation"]} == {"doğrulamada tut"}
    assert {r["girdi"] for r in sonuc["test-v3"]} == {"testte tut"}
    assert all(r["kaynak"] == "d" for r in sonuc["test-v3"])
    assert rapor["celiskili_girdi"] == 1
    assert rapor["bolumler"]["train"]["elemeler"]["saptanan_celiskili"] == 2
    assert rapor["bolumler"]["train"]["elemeler"]["saptanan_dislanan"] == 2


@pytest.mark.parametrize("g,h,neden", [
    ("altmışlık bir adam", "60'lık bir adam", "yas_tahmini"),
    ("bir buçuk iki saat", "bir buçuk iki saat", "bucuklu_aralik"),
    ("bir elli boyunda", "bir elli boyunda", "birimsiz_boy"),
    ("ikinci büyük şehri", "2. büyük şehri", "anlatim_unvan"),
    ("ikinci kaptan", "2. kaptan", "anlatim_unvan"),
    ("dokuz saat sürdü", "9 saat sürdü", "kucuk_sure_yas"),
])
def test_eski_yeni_karar_ihlalleri(g, h, neden):
    assert B.eski_karar_ihlali(satir(g, h)) == neden


@pytest.mark.parametrize("g,h,kategori", [
    ("altmışlık bir kutu", "60'lık bir kutu", "kardinal"),
    ("iki saat on beş dakika", "2 saat 15 dakika", "bilesik"),
    ("saat dokuzda gel", "saat 9'da gel", "saat"),
    ("üçüncü kat", "3. kat", "sira"), ("bir buçuk iki saat", "1,5-2 saat", "aralik"),
    ("bir elli boyunda", "1,50 boyunda", "ondalik"), ("dokuz saat sürdü", "dokuz saat sürdü", "negatif_kalip"),
])
def test_eski_gecerli_satirlar_korunur(g, h, kategori):
    assert B.eski_karar_ihlali(satir(g, h, kategori=kategori)) is None


def test_birlestirme_yedegi_sabit_kuru_yazmaz_ve_tekrar_determinist(tmp_path):
    veri = tmp_path / "data"
    (veri / "v3").mkdir(parents=True)
    dis = veri / "v3/haric-md5.txt"
    dis.write_text("", encoding="utf-8")
    for b in ("train", "validation"):
        D.yaz(veri / f"{b}.jsonl", [satir(b + " eski")])
    for b in D.BOLUMLER:
        D.yaz(veri / "v3" / f"d-{b}.jsonl", [satir(b + " yeni")])
    for ad in ("test", "test-v1", "test-v2"):
        (veri / f"{ad}.jsonl").write_bytes(b"donmus\n")
    args = ["--data", str(veri), "--haric", str(dis)]
    assert B.main(args + ["--kuru"]) == 0
    assert not (veri / "train-v2.jsonl").exists()
    assert B.main(args) == 0
    yedek = (veri / "train-v2.jsonl").read_bytes()
    cikti = (veri / "train.jsonl").read_bytes()
    assert B.main(args) == 0
    assert (veri / "train-v2.jsonl").read_bytes() == yedek
    assert (veri / "train.jsonl").read_bytes() == cikti
    for ad in ("test", "test-v1", "test-v2"):
        assert (veri / f"{ad}.jsonl").read_bytes() == b"donmus\n"
    rapor = json.loads((veri / "metadata-v3.json").read_text(encoding="utf-8"))
    assert rapor["bolumler"]["train"]["kaynak"]["d"] == 1


def _soru_eki_sorunlari(metin):
    un = {"a": "mı", "ı": "mı", "e": "mi", "i": "mi", "o": "mu", "u": "mu", "ö": "mü", "ü": "mü"}
    return [m[0] for m in re.finditer(r"([^\W\d_]+) (mı|mi|mu|mü)\b", metin) if un[D.son_unlu(m[1])] != m[2]]


def test_d5_soru_eki_soylenen_sozcuge_uyar(veri):
    sayac = 0
    for r in hepsi(veri):
        if D.olgu_of(r) != "D5":
            continue
        assert not _soru_eki_sorunlari(r["girdi"]), r
        sayac += bool(re.search(r"\b(mı|mi|mu|mü)\b", r["girdi"]))
    assert sayac > 300
    # Girdide `lira mı`, hedefte `TL mi` (TL ince okunur).
    p = D.para(674)
    assert D.soru_eki(p.sozlu) == "mı"
    assert D.soru_eki("dokuz") == "mu" and D.soru_eki("yüz") == "mü"
    # Soru eki ayrı sözcüktür: hedefte girdidekiyle aynen kalır (`lira mı` → `TL mı`).
    assert any(re.search(r"lira mı\b", r["girdi"]) and re.search(r"TL mı\b", r["hedef"]) for r in veri["train"])
    for r in hepsi(veri):
        if D.olgu_of(r) == "D5":
            ek = r"\b(?:mı|mi|mu|mü)\b"
            assert re.findall(ek, r["girdi"]) == re.findall(ek, r["hedef"]), r


def test_d5_sayi_araliklari_ve_cumle_basi_onluklar(veri):
    yas, yil = [], []
    for r in veri["train"]:
        if D.olgu_of(r) != "D5":
            continue
        if m := re.search(r"(\d+) yaş", r["hedef"]):
            yas.append(int(m[1]))
        if m := re.search(r"(\d+) (?:yıl|sene)", r["hedef"]):
            yil.append(int(m[1]))
    assert yas and yil
    assert min(yas) >= 10 and max(yas) <= 95
    assert min(yil) >= 10 and max(yil) <= 80
    assert D.d5_basamak_payi(veri["train"]) >= .40
    assert len({r["sablon"] for r in veri["train"] if D.olgu_of(r) == "D5"}) >= 120


def test_d5_tasiyici_dilbilgisi(veri):
    for r in hepsi(veri):
        if D.olgu_of(r) == "D5":
            # İç cümleye nokta konup `diye düşündü` eklenmez.
            assert not re.search(r"\. diye ", r["girdi"]), r


def test_d3_d8_ust_dil_payi_sinirli(veri):
    for o in ("D3", "D8"):
        assert D.ust_dil_payi(veri["train"], o) <= .25, o
        sablonlar = D.SABLONLAR[o]
        assert sum(s.metin in D.UST_DIL for s in sablonlar) / len(sablonlar) <= .25, o


def test_d3_bir_ve_sayi_kaliplari_dogal(veri):
    for r in hepsi(veri):
        if D.olgu_of(r) != "D3":
            continue
        # `bir` + yüzlü sayı yalnız `bir yüz liralık` biçiminde; yaklaşıklıkta ve kuruşta yok.
        assert not re.search(r"\bbir (?:\w+ )?yüz (?:kuruş|gün|dakika|kişi|adım)", r["girdi"].lower()), r
        for m in re.finditer(r"\bbir (\d{3,})\b ?(\S*)", r["hedef"]):
            assert m[2].startswith("TL'lik"), r


def test_d7_dogal_olmayan_cogul_iyelik_yok(veri):
    for r in hepsi(veri):
        if D.olgu_of(r) == "D7":
            assert not re.search(r"liraları|TL'leri|kuruşları", r["girdi"] + r["hedef"]), r
            for m in re.finditer(r"(\d+) kuruş", r["hedef"]):
                assert int(m[1]) < 100, r  # kuruş 100'ün altında söylenir


def test_d6_belirsiz_saat_bicimleri_verilmez(veri):
    for r in hepsi(veri):
        if D.olgu_of(r) == "D6" and r["girdi"] != r["hedef"]:
            g = r["girdi"].lower()
            # `on birden sonra` (11'den sonra) geçerli; yalın `birden`/`ondan`/`ona` sözcük okunur.
            assert not re.search(r"(?<!on )\bbirden sonra\b|\bondan sonra\b|\bona kadar\b", g), r


def test_girdi_hedef_sayi_disinda_ayni(veri):
    for r in hepsi(veri):
        g, h = r["girdi"], r["hedef"]
        if g == h:
            continue
        i = 0
        while i < min(len(g), len(h)) and g[i] == h[i]:
            i += 1
        j = 0
        while j < min(len(g), len(h)) - i and g[-1 - j] == h[-1 - j]:
            j += 1
        assert re.search(r"[\d%]", h[i:len(h) - j]), r
        assert not re.search(r"\d", g[i:len(g) - j]), r
