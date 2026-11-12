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


# ---- koruma: on- zamir biçimleri ve ekli ay adı (v1.1) ---------------------------------------------------
def test_saat_ona_kadar_baglamda_korunur():
    assert koru('saat ona kadar bekle', "saat 10'a kadar bekle")[0] == "saat 10'a kadar bekle"
    assert koru('yüzde ona kadar düştü', "%10'a kadar düştü")[0] == "%10'a kadar düştü"
    # önceki sözcük sayı sözcüğü: "yirmi ona" gibi bölgede de zamir sayılmaz
    assert koru('saat yirmi ona kadar', "saat 20 10'a kadar")[0] == "saat 20 10'a kadar"


def test_ona_baglamsiz_geri_alinir():
    metin, uyari = koru('ona söyledim', "10'a söyledim")
    assert metin == 'ona söyledim' and uyari
    for g, h in [('onu gördüm', "10'u gördüm"), ('onun evi', "10'un evi"), ('ondan haber aldım', "10'dan haber aldım"),
                 ('onda bir şey var', "10'da bir şey var")]:
        assert koru(g, h)[0] == g, g
    assert not sayi_benzeri_mi('ona') and sayi_benzeri_mi('ona', 'saat') and not sayi_benzeri_mi('ona', 'ben')


def test_ekli_ay_adi_tarihte_buyuk_harfle_kabul_edilir():
    assert koru('sekiz kasımda toplanalım', "8 Kasım'da toplanalım")[0] == "8 Kasım'da toplanalım"
    assert koru('yirmi dokuz ekimde', "29 Ekim'de")[0] == "29 Ekim'de"
    assert koru('toplantı beş ocaktan sonra', "toplantı 5 Ocak'tan sonra")[0] == "toplantı 5 Ocak'tan sonra"


def test_sayisiz_ekli_ay_adi_degismez():
    # önünde çevrilen bir sayı yoksa ay adı olduğu gibi kalır
    g = 'kasımda tatile çıkacağız'
    assert koru(g, "Kasım'da tatile çıkacağız")[0] == g
    g = 'bu yıl ekimde döneriz'
    assert koru(g, "bu yıl Ekim'de döneriz")[0] == g


# ---- koruma: v2 biçimleri (yeni birimler, yarı normalleşmiş, bitişik, ayın günü, saat deyişleri) -------------
def _kabul(girdi, ham):
    metin, uyari = koru(girdi, ham)
    assert metin == ham and uyari == [], (girdi, ham, metin, uyari)


def test_yeni_birimler_kabul_edilir():
    _kabul('beş yüz miligram', '500 mg')
    _kabul('yirmi metreküp su', '20 m³ su')
    _kabul('üç yüz kilovatsaat', '300 kWh')
    _kabul('yedi yüz yetmiş üç kilovat saatlik batarya', "773 kWh'lik batarya")
    _kabul('beş yüz kırk sekiz kilometrekarelik alan', "548 km²'lik alan")
    _kabul('elli hertz', '50 Hz')
    _kabul('yüz iki megahertz hızında', '102 MHz hızında')
    _kabul('iki saat on beş dakikada', '2 saat 15 dakikada')


def test_yari_normallesmis_girdi_kabul_edilir():
    _kabul("saat 14:30'da buluşalım", "saat 14.30'da buluşalım")  # yalnız noktalama değişir
    _kabul('22500 liraya sattım', "22.500 TL'ye sattım")
    _kabul('eksi 12 derece', '-12 derece')
    _kabul("yüzde 60'ı geçti", "%60'ı geçti")
    _kabul('5 bin lira', '5.000 TL')
    _kabul('12 bin 500 lira', '12.500 TL')
    _kabul('yüzde 12 buçuk', '%12,5')
    _kabul('15 kasım 2026', '15 Kasım 2026')
    _kabul('0 532 123 45 67', '0532 123 45 67')
    _kabul('artı doksan beş yüz elli', '+90 550')


def test_yari_normallesmis_girdide_sayi_olmayan_degisiklik_geri_alinir():
    girdi = "22500 liraya ev aldım"
    assert koru(girdi, "22.500 TL'ye ev aldım ama")[0] == "22.500 TL'ye ev aldım"  # eklenen sözcük reddedilir
    assert koru(girdi, "22.500 TL'ye araba aldım")[0] == girdi  # sayıya bitişik sayı dışı değişiklik: bölge geri alınır
    girdi = 'eksi 12 derece hava'
    assert koru(girdi, '-12 derece sıcak')[0] == '-12 derece hava'
    # rakamlı sözcükte yalnız noktalama değişebilir: ek ayrılıp sözcük eklenirse özgün hâl kalır
    assert koru("saat 14:30'da", "saat 14.30 da")[0] == "saat 14:30'da"


def test_bitisik_yazilmis_sayilar_kabul_edilir():
    _kabul('yirmibeş', '25')
    _kabul('ikiyüz elli gram', '250 g')
    _kabul('üçbin beşyüz lira', '3.500 TL')
    _kabul('yüzde onbeş', '%15')
    _kabul('saat onbirde', "saat 11'de")
    _kabul('binyediyüz lira', '1.700 TL')
    _kabul('onbeş kişi', '15 kişi')


def test_bitisik_sayi_sayilmayan_sozcukler():
    for w in ['onbaşı', 'binbaşı', 'yüzbaşı', 'ondalık', 'kırkayak', 'yediveren', 'üçgen', 'beşik', 'altın', 'birlik',
              'ikiz', 'dörtgen', 'altıgen', 'yüzücü', 'birbirine', 'binbir', 'dörtnala', 'kırkmak']:
        assert not sayi_benzeri_mi(w), w
    for w in ['onbeş', 'yirmibeş', 'ikiyüzelli', 'üçbin', 'binyediyüz', 'onbirde', 'yüzelli', 'ikibinyirmialtıdaki']:
        assert sayi_benzeri_mi(w), w


def test_bitisik_sayi_olmayan_sozcuk_degisikligi_geri_alinir():
    for g, h in [('onbaşı geldi', '15 geldi'), ('binbaşı geldi', '1000 geldi'), ('kırkayak gördüm', '40 gördüm'),
                 ('üçgen çizdi', '3 çizdi'), ('beşik salladı', '5 salladı'), ('birlik oldu', '1 oldu')]:
        assert koru(g, h)[0] == g, g
    # sayı bitişik yazılmış, ama komşu sözcük değiştirilmiş: bölge geri alınır
    assert koru('onbeş kişi geldi', '15 hanım geldi')[0] == 'onbeş kişi geldi'


def test_ayin_gunu_kabul_edilir():
    _kabul('her ayın birinde ödeme var', "her ayın 1'inde ödeme var")
    _kabul('ayın on beşinde', "ayın 15'inde")
    _kabul('kurs geçen ayın yirmisinde bitiyor', "kurs geçen ayın 20'sinde bitiyor")
    _kabul('mayısın on dokuzunda', "mayısın 19'unda")
    _kabul('ayın üçüne kadar', "ayın 3'üne kadar")
    _kabul('taksit temmuzun altısında çekilecek', "taksit temmuzun 6'sında çekilecek")
    # ayın bağlamı yoksa zamir/sözcük kalır
    g = 'biri geldi'
    assert koru(g, "1'i geldi")[0] == g
    g = 'ikisini de gördüm'
    assert koru(g, "2'sini de gördüm")[0] == g


def test_saat_deyisleri_kabul_edilir():
    _kabul('beşe on kala', "5'e 10 kala")
    _kabul('üçe çeyrek var', "3'e çeyrek var")
    _kabul('dördü yirmi geçe', "4'ü 20 geçe")
    _kabul('bire on kala çıktık', "1'e 10 kala çıktık")
    _kabul('dün biri on geçe telefonum çaldı', "dün 1'i 10 geçe telefonum çaldı")
    _kabul('on ikiye çeyrek kala buluşalım', "12'ye çeyrek kala buluşalım")


def test_ekli_bicimler_baglamda_kabul_edilir():
    _kabul('dokuz yüzün bir fazlası', "900'ün bir fazlası")
    _kabul('yüzde yüzü buldu', "%100'ü buldu")
    _kabul('puanı yedi buçuğa yükseldi', "puanı 7,5'e yükseldi")
    _kabul('akşam ondan sonra', "akşam 10'dan sonra")
    _kabul('sabah onda işe çıktık', "sabah 10'da işe çıktık")
    _kabul('iki bin birin ilk günleri', "2001'in ilk günleri")
    _kabul('yetmiş biri bulan olmadı', "71'i bulan olmadı")


def test_baglamsiz_zamir_ve_esyazimlilar_geri_alinir():
    for g, h in [('yüzünü yıkadı', "100'ünü yıkadı"), ('biri geldi', "1'i geldi"), ('bindi gitti', "1000'di gitti"),
                 ('ona baktı', "10'a baktı"), ('onu gördüm', "10'u gördüm"),
                 ('masanın altında', 'masanın 6 yanında'), ('yüzdük denizde', '100 denizde')]:
        assert koru(g, h)[0] == g, g


def test_sayi_bolgesine_baska_sozcuk_sizdirilamaz():
    g = 'yirmi beş lira verdi'
    assert koru(g, '25 harika TL verdi')[0] == g
    assert koru('elli kuruş', '50 kuruş')[0] == '50 kuruş'


def test_sondaki_es_yazimli_sozcuk_sayiyla_eslenmez():
    # "yedi" fiili cümlenin sonunda kalır, baştaki "yedi yüz" ile karışmaz
    _kabul('yedi yüz gram yedi', '700 g yedi')
