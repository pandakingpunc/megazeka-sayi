"""Gidiş-dönüş (değer) denetimi (``dogrula``) ve bölge kenarı noktalama/ek düzeltmeleri (model gerektirmez)."""
import pytest

from megazeka_sayi.cikarim import koru, sayi_benzeri_mi
from megazeka_sayi.dogrula import deger_tutuyor_mu


def _tutar(girdi, cikti, onceki=None, sonraki=None):
    return deger_tutuyor_mu(girdi.split(), cikti.split(), onceki, sonraki)


# ---- gerçek metinde görülen hata türleri: bölge girdideki hâline döner ----------------------------------
@pytest.mark.parametrize('girdi,ham', [
    ('Otuz yaşında adam', '1930 yaşında adam'),                     # uydurma rakam
    ('yol iki buçuk üç saat sürdü', 'yol 2,5 saat sürdü'),            # bir sayı düştü
    ('yetmiş sekiz milyon on bin', '78.100'),                         # iç sıfır kaybı
    ('bin doksan', '1.90'),
    ('yirmi beş bin üç', '25.3'),
    ('on iki milyon altmış iki bin', '12.62.000'),
    ('yedi bin beş', '7.5'),
])
def test_hatali_deger_geri_alinir(girdi, ham):
    metin, uyari = koru(girdi, ham)
    assert metin == girdi
    assert len(uyari) == 1 and 'sayı değeri tutmuyor' in uyari[0] and 'geri alındı' in uyari[0]


@pytest.mark.parametrize('girdi,ham', [
    ('Otuz yaşında adam', '30 yaşında adam'),
    ('yetmiş sekiz milyon on bin', '78.010.000'),
    ('bin doksan', '1.090'),
    ('yedi bin beş', '7.005'),
    ('yol iki buçuk saat sürdü', 'yol 2,5 saat sürdü'),
])
def test_dogru_deger_gecer(girdi, ham):
    assert koru(girdi, ham) == (ham, [])


# ---- meşru biçimlerin hepsi geçer; bozulmuş biçimleri geri alınır ----------------------------------------
GECEN = [
    # para
    ('beş lira beş kuruş', '5,05 TL', None),
    ('bin iki yüz elli lira elli kuruş', '1.250,50 TL', None),
    ('12 bin 500 lira 50 kuruş', '12.500,50 TL', None),
    ('on beş lira', '15 TL', None),
    # saat
    ('on dört beş', '14.05', 'saat'),
    ('on dört otuzda', "14.30'da", 'saat'),
    ('üç buçuk', '3.30', 'saat'),
    ('üç buçukta', "3.30'da", 'saat'),
    ('3 buçukta', "3.30'da", 'saat'),
    ('02:15', '2.15', None),
    # ondalık, buçuk, büyük sayı
    ('sıfır virgül sıfır beş', '0,05', None),
    ('üç virgül on dört', '3,14', None),
    ('iki buçuk', '2,5', None),
    ('yüzde on iki buçuk', '%12,5', None),
    ('iki buçuk milyon', '2,5 milyon', None),
    ('iki milyon üç yüz bin', '2.300.000', None),
    ('2 buçuk milyon', '2,5 milyon', None),
    ('1,5 milyon', '1,5 milyon', None),
    ('15 milyon', '15 milyon', None),
    # telefon / kod / skor / aralık / eksi / sıra / yüzde
    ('sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi', '0532 123 45 67', None),
    ('sıfır beş üç iki bir iki üç dört beş altı yedi', '0532 123 45 67', None),
    ('artı doksan beş yüz otuz iki', '+90 532', None),
    ('kodu sıfır sekiz dört iki', 'kodu 0842', None),
    ('iki bir', '2-1', None),
    ('beş altı', '5-6', None),
    ('on on beş', '10-15', None),
    ('yüz yedi yüz bir', '107-101', None),
    ('dokuz yüz bin elli', '900-1.050', None),
    ('eksi beş', '-5', None),
    ('yirmi ikinci', '22.', None),
    ('yüzde on beş', '%15', None),
    ('yüzde yüz', '%100', None),
    ('dört yüzde', "400'de", None),            # yüz + de eki
    ('beş yüzden', "500'den", None),
    # tarih, on yılı, ayın günü, saat deyişi
    ('yirmi dokuz ekim bin dokuz yüz yirmi üç', '29 Ekim 1923', None),
    ('doksanlarda', "1990'larda", None),
    ('yetmişlerde', "1970'lerde", None),
    ('on beşinde', "15'inde", 'ayın'),
    ('beşe on kala', "5'e 10 kala", None),
    ('on ikiye çeyrek kala', "12'ye çeyrek kala", None),
    # bitişik yazım ve yarı rakamlı girdi
    ('onbeş', '15', None),
    ('ikiyüzelli', '250', None),
    ('binyediyüz', '1.700', None),
    ('5 bin lira', '5.000 TL', None),
    ('12 bin 500', '12.500', None),
    ('05321234567', '0532 123 45 67', None),
    ('14:30\'da', "14.30'da", None),
    # birim üsleri rakam sayılmaz
    ('yetmiş metrekare', '70 m²', None),
    ('iki kilometrekare', '2 km²', None),
    ('üç metreküp', '3 m³', None),
    # bileşik ölçü (her sayı ayrı)
    ('üç kilo iki yüz gram', '3 kg 200 g', None),
    ('bir metre seksen santim', '1 m 80 cm', None),
]


@pytest.mark.parametrize('girdi,cikti,onceki', GECEN)
def test_mesru_bicim_gecer(girdi, cikti, onceki):
    assert _tutar(girdi, cikti, onceki), (girdi, cikti)


BOZUK = [
    ('beş lira beş kuruş', '5,5 TL', None),
    ('on dört beş', '14.5', 'saat'),
    ('sıfır virgül sıfır beş', '0,5', None),
    ('sıfır virgül sıfır beş', '0,005', None),
    ('yüzde on iki buçuk', '%12,6', None),
    ('iki buçuk milyon', '2,5 bin', None),
    ('iki buçuk kilo', '2,30 kg', None),
    ('beş bin lira', '50.000 TL', None),
    ('beş yüz on', '5110', None),                 # katsayıyı çarpanından ayıran bölünme
    ('yirmi beş', '205', None),                   # ayraçsız bitişik: sol grup tek rakam değil
    ('üç bin yedi', '3.1007', None),
    ('sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi', '0532 123 45 76', None),
    ('05321234567', '0532 123 45 68', None),
    ('12 bin 500', '12.50', None),
    ('yirmi ikinci', '2.', None),
    ('beşe on kala', "5'e 1 kala", None),
    ('on beşinde', "51'inde", 'ayın'),
    ('doksanlarda', "1900'larda", None),
    ('yetmiş metrekare', '702 m²', None),
    ('on virgül yedi', '1,7', None),              # virgül grubu böler
    ('yüzde otuz dokuz', '%139', None),           # yüz + de yorumu ekli sözcükten sonra sayıyı sürdüremez
    ('yüzde on beş', '%115', None),
    ('eksi beş', '-6', None),
    ('iki bir', '2-2', None),
    ('on beş milyar', '150 milyar', None),
    ('iki yüz on', '', None),                     # tüm rakamlar düşmüş
    ('lira', '5 TL', None),                       # girdide sayı yokken rakam uydurma
]


@pytest.mark.parametrize('girdi,cikti,onceki', BOZUK)
def test_bozuk_deger_geri_alinir(girdi, cikti, onceki):
    assert not _tutar(girdi, cikti, onceki), (girdi, cikti)


def test_kuruş_bolge_disinda_ise_tek_hane_doldurulmaz():
    assert _tutar('beş', '5', sonraki='kuruş')


def test_ayri_sayilar_kardinal_birlesmez():
    # "yirmi lira beş kuruş" → 20 ve 5; 25 olamaz (lira sözcüğü grubu böler)
    assert _tutar('yirmi lira beş kuruş', '20,05 TL')
    assert not _tutar('yirmi lira beş kuruş', '25 TL')


# ---- İş 2a: bölge kenarındaki noktalama tamamlanır -----------------------------------------------------------
def test_acilis_tirnagi_tamamlanir():
    assert koru('"Otuz yaşında', '30 yaşında') == ('"30 yaşında', [])
    assert koru('"Otuz yaşında adam"', '30 yaşında adam"')[0] == '"30 yaşında adam"'


def test_kapanis_tirnagi_tamamlanir():
    assert koru('Dedi ki "iki yüz on lira."', 'Dedi ki 210 TL.') == ('Dedi ki "210 TL."', [])
    assert koru('Dedi ki "iki yüz on lira."', 'Dedi ki 210 TL')[0] == 'Dedi ki "210 TL."'


@pytest.mark.parametrize('girdi,ham,beklenen', [
    ('(on lira)', '10 TL', '(10 TL)'),
    ('on lira…', '10 TL', '10 TL…'),
    ('Şu: yirmi lira!', 'Şu: 20 TL', 'Şu: 20 TL!'),
    ('“iki yüz elli lira”', '250 TL', '“250 TL”'),
    ('Kaç lira? yirmi lira, dedi.', 'Kaç lira? 20 TL dedi.', 'Kaç lira? 20 TL, dedi.'),
])
def test_kenar_noktalamasi_tamamlanir(girdi, ham, beklenen):
    assert koru(girdi, ham)[0] == beklenen


def test_kenar_noktalamasi_olan_cikti_degismez_ve_ek_kesme_eklenmez():
    assert koru('iki yüz on lira.', '210 TL.')[0] == '210 TL.'
    assert koru('Borcun iki yüz on liradır.', "Borcun 210 TL'dir.")[0] == "Borcun 210 TL'dir."
    # kesme işareti ve ek noktalama sayılmaz; sayı içi nokta/virgül korunur
    assert koru('bin liram var', "1.000 TL'm var")[0] == "1.000 TL'm var"
    assert koru('sonuç yüz yirmi, dedi', 'sonuç 120, dedi')[0] == 'sonuç 120, dedi'


# ---- İş 2b: doğru çıktılar artık geri alınmıyor ---------------------------------------------------------------
@pytest.mark.parametrize('girdi,ham', [
    ('Borcun iki yüz on liradır.', "Borcun 210 TL'dir."),
    ('Fiyatı on beş lira idi.', 'Fiyatı 15 TL idi.'),
    ('"Üç yüz liram var!" dedi.', '"300 TL\'m var!" dedi.'),
    ('Otuz kırk lira…', '30-40 TL…'),
    ('Bu elli liranız.', "Bu 50 TL'niz."),
    ('Hesap beş yüz liradır', "Hesap 500 TL'dir"),
])
def test_dogru_cikti_geri_alinmaz(girdi, ham):
    assert koru(girdi, ham) == (ham, [])


def test_fiyati_sozcugu_silinirse_geri_alinir():
    # Model "Fiyatı" sözcüğünü düşürürse silinen sözcük sayı bölgesiyle tek bölge olur ve bölge bütünüyle girdideki
    # hâline döner (doğru çıktı "Fiyatı 15 TL idi." yukarıda geçiyor).
    metin, uyari = koru('Fiyatı on beş lira idi.', '15 TL idi.')
    assert metin == 'Fiyatı on beş lira idi.' and uyari


@pytest.mark.parametrize('kelime', ['liram', 'liranız', 'liradır', 'kilom', 'gramın', 'litredir', 'derecedir'])
def test_para_olcu_iyelik_ve_dir_ekleri_sayi_benzeri(kelime):
    assert sayi_benzeri_mi(kelime), kelime


@pytest.mark.parametrize('kelime', ['yedim', 'birim', 'bindir', 'yüzünüz', 'beşim', 'onum', 'yüzdürmek'])
def test_sayi_koklerine_iyelik_ve_dir_eklenmez(kelime):
    assert not sayi_benzeri_mi(kelime), kelime


@pytest.mark.parametrize('girdi,ham', [
    ('ona git', "10'a git"),
    ('yüzünü yıka', "100'ünü yıka"),
    ('arabaya bindi', 'arabaya 1000 di'),
    ('masanın altında oturdu', 'masanın 6 inde oturdu'),
    ('yemeğini yedim', '7im'),
])
def test_es_yazimli_koruma_gevsemedi(girdi, ham):
    metin, uyari = koru(girdi, ham)
    assert metin == girdi and uyari
