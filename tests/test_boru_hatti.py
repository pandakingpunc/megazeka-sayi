"""Ölçüm, kural tabanı ve koruma süzgeci testleri (model gerektirmez)."""
import pytest

from megazeka_sayi.cikarim import koru, sayi_benzeri_mi
from megazeka_sayi.kural_tabani import donustur
from megazeka_sayi.olcum import kategori_kirilimi, olc, sayi_belirteci_dogrulugu, sayi_belirtecleri


# ---- olcum ------------------------------------------------------------------------------------------
def satir(girdi, hedef, cikti, kategori='x'):
    return {'girdi': girdi, 'hedef': hedef, 'cikti': cikti, 'kategori': kategori}


def test_tam_eslesme_ve_cer():
    m = olc([satir('a', 'abcd', 'abcd'), satir('b', 'abcd', 'abxd')])
    assert m['tam_eslesme'] == 0.5
    assert m['cer'] == pytest.approx(1 / 8)
    assert m['wer'] == pytest.approx(0.5)


def test_sayi_belirtecleri_kenar_noktalamasi():
    assert sayi_belirtecleri('toplam 1.250,50 TL, %12,5 ve 3. kat (14.30)') == ['1.250,50', '%12,5', '3.', '14.30']


def test_sayi_belirteci_dogrulugu_coklu_kume():
    # hedefte "5" iki kez var, çıktıda bir kez -> 2/3
    r = [satir('', 'a 5 b 5 c 12', 'a 5 b c 12')]
    assert sayi_belirteci_dogrulugu(r) == pytest.approx(2 / 3)
    assert sayi_belirteci_dogrulugu([satir('', 'sayı yok', 'sayı yok')]) is None


def test_yanlis_donusum_orani_yalniz_negatiflerde():
    rows = [satir('yemeğini yedi', 'yemeğini yedi', 'yemeğini 7', 'negatif_es'),
            satir('iki gün', 'iki gün', 'iki gün', 'negatif_kalip'),
            satir('on lira', '10 TL', '10 TL', 'para')]
    m = olc(rows)
    assert m['negatif_ornek'] == 2 and m['yanlis_donusum_orani'] == 0.5


def test_kategori_kirilimi():
    rows = [satir('on lira', '10 TL', '10 TL', 'para'), satir('yüzde on', '%10', '10', 'yuzde')]
    k = kategori_kirilimi(rows)
    assert k['para']['tam_eslesme'] == 1.0 and k['yuzde']['tam_eslesme'] == 0.0


# ---- kural tabanı -----------------------------------------------------------------------------------
@pytest.mark.parametrize('girdi,beklenen', [
    ('toplam bin iki yüz elli lira elli kuruş', 'toplam 1.250,50 TL'),
    ('yüzde on iki buçuk indirim', '%12,5 indirim'),
    ('iki buçuk kilogram domates', '2,5 kg domates'),
    ('üç virgül on dört', '3,14'),
    ('eksi beş derece', '-5 derece'),
    ('dörde kadar', "4'e kadar"),
    ('yüz yirmi üç kilodan', "123 kg'dan"),
    ('elli liraya', "50 TL'ye"),
    ('yirmi birinci yüzyıl', '21. yüzyıl'),
])
def test_kural_tabani_donusumleri(girdi, beklenen):
    assert donustur(girdi) == beklenen


def test_kural_tabani_baglama_bakmaz_ve_yedi_yi_yanlis_cevirir():
    # BEKLENEN HATA: taban çizgisi bağlamsızdır; modelin değeri tam olarak bu eş yazımlılarda ölçülür.
    assert donustur('yemeğini yedi') == 'yemeğini 7'
    assert donustur('masanın altı') == 'masanın 6'


def test_kural_tabani_sayi_olmayan_metne_dokunmaz():
    assert donustur('bugün hava çok güzel') == 'bugün hava çok güzel'


# ---- koruma ----------------------------------------------------------------------------------------
def test_dogru_sayi_degisikligi_korunur():
    metin, uyari = koru('toplam bin iki yüz elli lira elli kuruş', 'toplam 1.250,50 TL')
    assert metin == 'toplam 1.250,50 TL' and uyari == []


def test_yuzde_ve_ek_korunur():
    assert koru('yüzde on iki buçuk indirim', '%12,5 indirim')[0] == '%12,5 indirim'
    assert koru('saat on dört otuzda görüşelim', "saat 14.30'da görüşelim")[0] == "saat 14.30'da görüşelim"


def test_sayi_olmayan_sozcuk_degisirse_geri_alinir():
    girdi = 'masanın altında yedi kişi'
    metin, uyari = koru(girdi, 'masanın üstünde 7 kişi')
    # "altında" sayı benzeri değil -> bölge geri alınır
    assert metin == girdi and uyari


def test_sayiyla_bitisik_sayi_disi_degisiklik_butun_bolgeyi_geri_alir():
    # Sayı ve komşu sözcük aynı değiştirme bölgesinde: ihtiyatlı davranıp bölge özgün hâline döner.
    girdi = 'iki yüz lira ödedim'
    metin, uyari = koru(girdi, '200 TL verdim')
    assert metin == girdi and uyari


def test_eklenen_sozcuk_reddedilir_silinen_geri_alinir():
    girdi = 'bugün on lira verdim'
    assert koru(girdi, 'bugün 10 TL verdim ve gittim')[0] == 'bugün 10 TL verdim'
    metin, uyari = koru(girdi, '10 TL verdim')  # "bugün" silindi
    assert metin == girdi and uyari


def test_saat_degistirilemez():
    # "saat" sayı benzeri sayılmaz; "saat" → "sa." gibi bir değişiklik geri alınır.
    assert not sayi_benzeri_mi('saat')
    metin, _ = koru('saat üçte', 'sa 3 te')
    assert metin.split()[0] == 'saat'


def test_buyuk_kucuk_harf_ve_noktalama_degistirilmez():
    girdi = 'Bugün hava güzel, yüz lira verdim.'
    metin, _ = koru(girdi, 'bugün hava güzel yüz lira verdim')  # model harf/noktalama değiştirdi
    assert metin == girdi


def test_ay_adi_buyuk_harf_istisnasi():
    metin, _ = koru('8 kasım 2026', '8 Kasım 2026')
    assert metin == '8 Kasım 2026'


def test_degismeyen_negatif_aynen_doner():
    girdi = 'yemeğini yedi ve gitti'
    assert koru(girdi, girdi) == (girdi, [])


def test_homograf_sozcukler_sayi_benzeri_degil():
    for w in ['yüzünü', 'ona', 'onlar', 'binlerce', 'bindi', 'altında', 'masanın']:
        assert not sayi_benzeri_mi(w), w
    for w in ['dörde', 'otuzda', 'liradan', 'kilogramdan', 'doksanlarda', 'dördüncü', 'buçuk', 'yüzde']:
        assert sayi_benzeri_mi(w), w
