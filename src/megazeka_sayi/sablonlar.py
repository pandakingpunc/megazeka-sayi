"""Taşıyıcı cümle şablonları, dolgu sözcükleri ve cümle üretimi.

Şablon sözdizimi: `{ad}`, `{ad.alt}`, `{ad.alt:ek}`. `ad` bir varlık kategorisi
(varliklar.ORNEKLEYICILER) ya da dolgu listesi (FILLERS) olabilir. Şablon metinleri
noktalamasız bitirilir; büyük harfli kipte sona nokta eklenir.
"""
from __future__ import annotations

import random
import re

from . import varliklar as V
from .turkce import ilk_harfi_buyut, lower_tr

KUCUK_SAYI_POLITIKASI = "yaziyla"  # "yaziyla" | "rakamla"

FILLERS = {
    "isim": ["Ali", "Ayşe", "Mehmet", "Zeynep", "Fatma", "Ahmet", "Elif", "Mustafa", "Emre", "Selin", "Deniz", "Burak",
             "Merve", "Cem", "Esra", "Kemal", "Hülya", "Ece", "Murat", "Seda", "Hakan", "Gizem", "Okan", "Büşra",
             "Yusuf", "İrem", "Onur", "Tuğba", "Baran", "Nazlı", "Sinan", "Pınar"],
    "sehir": ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Adana", "Trabzon", "Samsun", "Eskişehir",
              "Gaziantep", "Kayseri", "Mersin", "Diyarbakır", "Erzurum", "Van", "Edirne", "Bolu", "Rize", "Muğla",
              "Denizli", "Sivas", "Malatya", "Bingöl", "Dörtyol"],
    "takim": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Konyaspor", "Sivasspor", "Altay",
              "Altınordu", "Bursaspor"],
    "urun": ["elma", "domates", "peynir", "süt", "ekmek", "zeytin", "makarna", "pirinç", "çay", "kahve", "şeker", "un",
             "tereyağı", "portakal", "muz", "patates", "soğan", "biber", "salatalık", "bal", "yoğurt", "tavuk", "kıyma",
             "balık", "üzüm", "mercimek"],
    "esya": ["ceket", "ayakkabı", "kazak", "pantolon", "çanta", "televizyon", "kulaklık", "koltuk", "halı", "bisiklet",
             "tablet", "mont", "gözlük", "bilgisayar", "telefon", "buzdolabı", "çamaşır makinesi", "süpürge", "lamba"],
    "kisi": ["kişi", "öğrenci", "yolcu", "seyirci", "işçi", "hasta", "misafir", "katılımcı", "çocuk", "öğretmen",
             "oyuncu", "turist", "sürücü", "aday", "üye"],
    "nesne": ["sandalye", "kitap", "defter", "kalem", "bilet", "koli", "paket", "ağaç", "araba", "daire", "oda", "soru",
              "bardak", "tabak", "fincan", "masa", "çanta", "dosya"],
    "marka": ["iPhone", "Galaxy", "PlayStation", "Windows", "Pixel", "Xbox"],
}

# ----------------------------------------------------------------------------
# Pozitif şablonlar
# ----------------------------------------------------------------------------
_RAW: dict[str, str] = {}

_RAW["para"] = """
Toplam tutar {para.tl} oldu
Faturam bu ay {para.tl} geldi
{urun} kilosu {para.kucuk} olmuş
Market alışverişi için {para.tl} harcadım
Kargo ücreti {para.kucuk} olarak hesaplandı
Bu {esya} {para.tam} etiketiyle satılıyor
Kasaya {para.tam} yatırdım
Bilet fiyatı {para.tam} olacak
{isim} her ay kiraya {para.tam} ödüyor
Hesabınızdan {para.tl} tahsil edilmiştir
Sepetinizdeki ürünlerin toplamı {para.tl} tutuyor
Cüzdanımda sadece {para.kurus} kaldı
Bozuk para olarak {para.kurus} verdim
Taksimetre {para.tl} gösteriyordu
Tamirci arabanın bakımı için {para.tam} istedi
Doktor muayene ücreti olarak {para.tam} aldı
Çay ocağında hesap {para.kucuk} tuttu
Yurt dışına gitmeden önce {para.doviz} bozdurdum
Tatil için {para.doviz} ayırdım
Bu ceketi {para.doviz} karşılığında aldım
Kurye teslimat için {para.doviz} istedi
Bu telefonu {para.tl:ayrilma} aşağıya satmam
Kira {para.tam:yonelme} yükseldi
Ürünün fiyatı {para.tam:yonelme} düştü
Aynı model başka yerde {para.tam:bulunma} satılıyor
{para.tam:ilgi} üzerindeki alışverişlerde kargo ücretsiz
{para.tam:lik} bir hediye çeki aldım
{isim} bana borcunu {para.tam:belirtme} geri verdi
{para.tam:vasita} bu ayı çıkaramayız
{isim} maaşının {para.tam:iyelik3} kiraya gidiyor
Okul servisi için ayda {para.tam} ödüyoruz
Hesapta {para.tl} var
"""

_RAW["yuzde"] = """
Bu üründe {yuzde} indirim var
Enflasyon {yuzde} olarak açıklandı
Telefonun şarjı {yuzde} seviyesinde
Ankete katılanların {yuzde} evet cevabı verdi
Okulda başarı oranı {yuzde} oldu
Bankadan {yuzde} faizle kredi çektim
Bu hafta nem oranı {yuzde} civarında
Maaşlara {yuzde} zam geldi
Faiz oranı {yuzde} seviyesine çıktı
Seçimde katılım {yuzde} olarak gerçekleşti
Sütün yağ oranı {yuzde} olarak yazılmış
Projenin {yuzde} tamamlandı
Bu kazak {yuzde} pamuktan yapılmış
Kampanyada {yuzde} oranında indirim uygulanıyor
Mağaza tüm {urun} ürünlerinde {yuzde} indirim yapıyor
Yeni sezon fiyatlarında {yuzde} artış bekleniyor
Havadaki nem {yuzde} ölçüldü
{yuzde:lik} bir indirim kuponu aldım
{yuzde:lik} zam teklifini kabul etmedik
Kredi faizi {yuzde:yonelme} düştü
Zam oranı {yuzde:yonelme} kadar çıkabilir
Enflasyonun {yuzde:belirtme} aşacağını düşünüyorum
{yuzde:ilgi} üzerindeki faiz oranlarına dikkat et
Hedefimizin {yuzde:iyelik3} gerçekleşti
Biz {yuzde:ayrilma} fazla kâr elde ettik
Dersi {yuzde:vasita} geçtim
Kartla ödeme yapanlara {yuzde} ek indirim veriliyor
Dükkanın kârı geçen yıla göre {yuzde} arttı
"""

_RAW["olcu"] = """
Tarif için {olcu.agirlik} {urun} lazım
Pazardan {olcu.agirlik} {urun} aldım
Bu paket {olcu.agirlik} geliyor
Valizim {olcu.agirlik} çekti
Bebek {olcu.agirlik} doğdu
Evimiz {olcu.alan} büyüklüğünde
Deponun alanı {olcu.alan}
{sehir} buraya {olcu.mesafe} uzaklıkta
Okulumuz evimize {olcu.mesafe} mesafede
Bu duvarın uzunluğu {olcu.uzunluk}
Kardeşimin boyu {olcu.boy} oldu
Şişenin hacmi {olcu.hacim}
Her gün {olcu.hacim} su içmeye çalışıyorum
Telefonumun hafızası {olcu.veri}
Bu dosya {olcu.veri} yer kaplıyor
Bilgisayara {olcu.veri} bellek ekledim
Cihazın gücü {olcu.guc}
Şarj aleti {olcu.guc} çıkış veriyor
Dışarıda hava {olcu.sicaklik}
Yarın sıcaklık {olcu.sicaklik} olacak
Fırını {olcu.sicaklik} ısıtın
{olcu.agirlik:lik} bir paket {urun} aldık
{olcu.hacim:lik} bir şişe su aldım
{olcu.mesafe:lik} yolu yürüyerek gittik
Bu asansör {olcu.agirlik:ayrilma} fazla yük taşımaz
Evden okula {olcu.mesafe:yonelme} kadar yürüdük
Koşucu {olcu.mesafe:ayrilma} sonra yoruldu
Yüklenecek dosya {olcu.veri:ayrilma} büyük olmamalı
Sıcaklık {olcu.sicaklik:yonelme} düştü
Su {olcu.sicaklik:ayrilma} sonra kaynamaya başlar
Koltuk {olcu.alan:lik} bir odaya sığmaz
Yoğurdu {olcu.sicaklik:bulunma} mayalayın
"""

_RAW["saat"] = """
Toplantı saat {saat:bulunma} başlayacak
Otobüs saat {saat:bulunma} kalkıyor
Randevum saat {saat:bulunma}
Yarın saat {saat:bulunma} buluşalım
Konser saat {saat:bulunma} başlıyor
Film saat {saat:bulunma} bitiyor
Mağaza saat {saat:ayrilma} itibaren açık
Ders saat {saat:yonelme} kadar sürecek
Saat {saat} sularında evde olurum
Saat {saat} civarında seni arayacağım
Uçağımız saat {saat:bulunma} {sehir} havalimanına inecek
Doktor saat {saat:bulunma} muayeneye alacak
Yemek saat {saat:bulunma} hazır olur
Sınav saat {saat} itibarıyla başlamıştır
Mağaza saat {saat.aralik} kadar açık
Kargo saat {saat:ayrilma} önce gelmez
Saat {saat.tam:belirtme} biraz geçiyor
Saat {saat.tam:vasita} birlikte yağmur başladı
Kuaför saat {saat.tam:yonelme} randevu verdi
Saat {saat:bulunma_ki} toplantıya geç kalma
Bugün saat {saat:bulunma} {isim} gelecek
Kapı saat {saat:ayrilma} sonra kapanıyor
Sabah {saat.sabah:bulunma} kalktım
Sabah {saat.sabah:bulunma} işe çıktık
Öğlen {saat.ogle:bulunma} yemek molası veriyoruz
Akşam {saat.aksam:bulunma} yemeğe çıkacağız
Akşam {saat.aksam:ayrilma} sonra trafik azalıyor
Gece {saat.gece:bulunma} telefonum çaldı
Gece {saat.gece:bulunma} uyandım ve su içtim
Servis sabah {saat.sabah:bulunma} kalkıyor
"""

_RAW["tarih"] = """
Doğum günüm {tarih.gunay}
{isim} {tarih.tam} tarihinde doğdu
Sınav {tarih.gunay} tarihinde yapılacak
Toplantı {tarih.gunay} tarihine ertelendi
Bu belge {tarih.tam:bulunma} düzenlenmiş
Evlilik {tarih.tam:bulunma} gerçekleşti
Fatura son ödeme tarihi {tarih.tam}
Kitap {tarih.yil} yılında yayımlandı
Şirket {tarih.yil} yılında kuruldu
{tarih.yil:bulunma} yeni bir okul açıldı
Evi {tarih.yil:bulunma} satın aldık
{tarih.yil:ilgi} ilk günlerinde işe başladım
{tarih.yil:ayrilma} beri burada çalışıyor
{tarih.yil:yonelme} kadar bekleyin
{tarih.yil:bulunma_ki} seçimlerde oy kullanmıştım
{tarih.onyil:cogul_bulunma} {sehir} çok farklıydı
Babam {tarih.onyil:cogul_bulunma} gençti
{tarih.onyil:cogul} müziğini çok severim
Başvuru son tarihi {tarih.gunay}
Kargo {tarih.gunay} tarihinde teslim edilecek
Tatil {tarih.gunay} tarihinde başlıyor
Konser biletleri {tarih.gunay} tarihinde satışa çıkacak
Sözleşme {tarih.tam} tarihinde imzalandı
Maç {tarih.gunay} akşamı oynanacak
{tarih.tam} tarihli belgeyi getirin
Sınav sonuçları {tarih.gunay} günü açıklanacak
Mezuniyet töreni {tarih.gunay} günü yapılacak
Sınav {tarih.gunay:bulunma} yapılacak
Kitaplar {tarih.gunay:yonelme} kadar iade edilmeli
Kurs {tarih.gunay:ayrilma} itibaren başlıyor
"""

_RAW["sira"] = """
Ofisimiz {sira.kat} katta
Asansör {sira.kat} kata çıkmıyor
Kızım {sira.sinif} sınıfa gidiyor
{isim} {sira.sinif} sınıf öğrencisi
Bu konu {sira.madde} maddede anlatılıyor
Sözleşmenin {sira.madde} maddesini okuyun
{sira.yuzyil} yüzyılda yaşamış bir şair
Kitabın {sira.genel} bölümünü bitirdim
Lütfen {sira.genel} sayfayı açın
Evimiz {sira.genel} sokakta
{sira.genel} caddede yeni bir kafe açıldı
{sira.genel} yıl dönümümüz kutlu olsun
{isim} {sira.genel} yaş gününü kutladı
Takım {sira.genel} haftada yenildi
Bugün {sira.genel} dersimiz matematik
Yarışın {sira.genel} etabını kazandı
Kuyrukta {sira.genel} sırada bekliyorum
Bu yıl {sira.genel} Cumhuriyet Bayramını kutlayacağız
Rapor {sira.genel} sayfadan başlıyor
Dairemiz {sira.kat} katın sol tarafında
{sira.kat} kattaki odayı kiraladık
{sira.sinif} sınıf öğretmeni toplantı istedi
Sözleşmenin {sira.madde} maddesi değişti
{sira.yuzyil} yüzyıl sanatı üzerine bir sergi açıldı
Bu festival {sira.genel} kez düzenleniyor
Müdür {sira.genel} bölümde konuşma yaptı
Çocuk {sira.sinif} sınıfı bu yıl bitirdi
Hastane {sira.genel} sokak üzerinde
"""

_RAW["telefon"] = """
Beni {telefon} numarasından arayabilirsin
Telefon numaram {telefon}
Acil durumda {telefon} numarasını ara
{isim} bana {telefon} numarasını verdi
Müşteri hizmetleri {telefon} numaralı hatta
{telefon} numaralı telefonu aradım ama açmadılar
Eczanenin numarası {telefon}
Lütfen {telefon} numarasına mesaj gönderin
Rezervasyon için {telefon} numarasını arayınız
Kurye bana {telefon} numarasından ulaştı
Not al {telefon}
Cep telefonum {telefon} lütfen kaydedin
Hat {telefon} numarasına tanımlandı
Doktorun asistanı {telefon} numarasını verdi
Numarayı {telefon} diye kaydettim
Ev telefonu {telefon}
Siparişiniz için {telefon} numaralı hattı arayın
Mesaj gelirse {telefon} numarasına yönlendir
{telefon:yonelme} mesaj attım
{telefon:ayrilma} arama geldi
{telefon:belirtme} aradım ama kimse açmadı
Aramak isterseniz {telefon}
Sahibine ulaşmak için {telefon} numarasını çevir
Yeni numaram {telefon} oldu
Teknik servis {telefon} numarasından cevap veriyor
{isim} {telefon:vasita} görüşmek istediğini söyledi
"""

_RAW["kod"] = """
Doğrulama kodunuz {kod}
Kapı şifresi {kod}
Kartın pin kodu {kod}
Posta kodu {kod.posta}
Sipariş numaranız {kod.uzun}
Takip numarası {kod.uzun}
Dolabın şifresi {kod}
Güvenlik kodunu {kod} olarak girin
Sana gelen mesajdaki kod {kod}
Tek kullanımlık şifre {kod}
Alarm kodu {kod}
Ürün kodu {kod}
Kupon kodu {kod}
Otopark giriş kodu {kod}
Müşteri numarası {kod.uzun}
Randevu numarası {kod}
Bagaj etiketi numarası {kod.uzun}
Lütfen kodu {kod} diye girin
Telefona {kod} kodlu bir mesaj geldi
Evin kapı kodu {kod} olarak değişti
Hesap şifrem {kod}
Kargo teslim kodu {kod}
Kayıt numaranızı {kod.uzun} olarak not alın
Adresin posta kodu {kod.posta} olarak geçiyor
Bilet rezervasyon kodu {kod}
Kasa şifresi {kod.kisa}
"""

_RAW["skor"] = """
Maç {skor} bitti
Derbi {skor} sona erdi
İlk yarı {skor} tamamlandı
Skor {skor} oldu
{takim} maçı {skor} kazandı
{takim} deplasmanda {skor} yenildi
Takımımız {skor.galip} öne geçti
Karşılaşma {skor.berabere} berabere bitti
Hakem düdüğü çalınca durum {skor} idi
Dün akşamki maç {skor} sonuçlandı
Final maçı {skor.galip} bitti ve kupa bizim
Voleybol maçını {skor.galip} kazandık
Basketbolda maç {skor.basket} sona erdi
Bu sezonki ilk maç {skor} geçti
{takim} ile {takim} maçı {skor} sonuçlandı
{skor:lik} bir galibiyetle başladık
{skor:lik} yenilgiden sonra teknik direktör istifa etti
Maçı {skor.galip:vasita} kazandık
{takim} {skor.galip:ayrilma} geri döndü
Tabela {skor} gösteriyordu
Çocuklarla oynadığımız maç {skor} bitti
Haber spikeri maçı {skor} diye duyurdu
{takim} ilk devreyi {skor} geride kapattı
Rövanşta durum {skor.galip:yonelme} geldi
Gençlerin maçı {skor.basket} bitti
Okul turnuvasında final {skor} sonuçlandı
"""

_RAW["aralik"] = """
Yarın {aralik} {kisi} gelecek
Toplantı {aralik} dakika sürer
Bu iş {aralik} gün alır
Yol {aralik} saat sürüyor
Sınıfta {aralik} öğrenci var
Tarif için {aralik} yumurta lazım
Beni {aralik} dakika bekleyin
{aralik} ay içinde bitiririz
Her gün {aralik} bardak su içiyorum
Bu yolculuk {aralik} saatlik bir yol
Odaya {aralik} sandalye sığar
{aralik} yıl önce buraya taşındık
Yemeği {aralik} kişilik hazırladım
Kargo {aralik} iş günü içinde gelir
Misafirler {aralik} saat sonra gelir
Fiyatlar {aralik.para} arasında değişiyor
{isim} {aralik.agirlik} vermiş
Her gün {aralik.agirlik} {urun} yiyor
Sıcaklık {aralik.sicaklik} olacak
Burası {aralik.mesafe} ileride
Evden okula {aralik.mesafe} var
Bagaj {aralik.agirlik:ayrilma} ağır olmamalı
Sınavda {aralik} soru yanlış yaptım
Bu oyuncak {aralik} yaş arası çocuklar için
{aralik.mesafe:yonelme} kadar yürüdük
Bahçede {aralik} ağaç var
Koliyi {aralik} günde teslim ederiz
"""

_RAW["ondalik"] = """
Sınav ortalamam {ondalik} çıktı
Dönem ortalaması {ondalik} puan
Bu oyun {ondalik} puan aldı
Yolculuk {ondalik} saat sürdü
Film {ondalik} saat sürüyor
{isim} {ondalik} yıl yurt dışında kaldı
Takımın maç başına gol ortalaması {ondalik}
Bu dersin ağırlık katsayısı {ondalik}
Deprem {ondalik} büyüklüğünde olmuş
Ortalama {ondalik} kez doktora gidiyor
Test sonucu {ondalik} çıktı
Bu işlem {ondalik} saniye sürdü
Hasta {ondalik} gündür ateşli
Kitap {ondalik} ay boyunca listede kaldı
Yarışmada jüri {ondalik} puan verdi
Kredi notu {ondalik} olarak hesaplandı
Notunu {ondalik} seviyesinden yükseltti
Ortalamamı {ondalik:yonelme} çıkardım
Puanı {ondalik:yonelme} yükseldi
Ortalamam {ondalik:ayrilma} aşağı düşmedi
{ondalik:ilgi} üzerindeki notlar geçer sayılıyor
Bu katsayıyı {ondalik:vasita} çarpın
Sistemin sürümü {ondalik} olarak güncellendi
Değerlendirme puanı {ondalik} civarında
Ankette memnuniyet puanı {ondalik} bulundu
Haftada ortalama {ondalik} gün spor yapıyorum
"""

_RAW["kardinal"] = """
Salonda {kardinal.orta} {kisi} vardı
Sınıfta {kardinal.orta} {kisi} var
Sepetime {kardinal.orta} {nesne} ekledim
Depoda {kardinal.bin} {nesne} kaldı
{sehir} maçına {kardinal.bin} {kisi} geldi
Etkinliğe {kardinal.yuz} {kisi} katıldı
Her gün {kardinal.orta} sayfa kitap okuyorum
Bu hafta {kardinal.orta} {nesne} sattık
Kütüphanede {kardinal.bin} kitap var
Bugün {kardinal.yuz} {kisi} aradı
Toplantı {kardinal.orta} dakika sürdü
Projeyi {kardinal.orta} günde tamamladık
Kurs {kardinal.orta} hafta sürecek
Yolculuk {kardinal.orta} saat sürdü
Kapıda {kardinal.kucuk} {kisi} seni bekliyor
Masada {kardinal.kucuk} sandalye eksik
{kardinal.kucuk} gün sonra döneceğim
Bu işi {kardinal.kucuk} saatte bitiririz
Çantamda {kardinal.kucuk} kalem var
{kardinal.orta:yonelme} kadar sayalım
{kardinal.orta:ayrilma} fazla {kisi} gelmedi
{kardinal.yuz:ilgi} üzerinde bir rakam bu
Elimde {kardinal.orta:lik} bir kutu var
Puanı {kardinal.orta:belirtme} bulan olmadı
Bunu {kardinal.orta:vasita} çarpın
Sınıfın {kardinal.orta:iyelik3} kız
{isim} {kardinal.yas} yaşında
Dedem {kardinal.yas} yaşına girdi
Annem bu yıl {kardinal.yas} yaşını doldurdu
{kardinal.yas} yaşındaki bir çocuk kazayı gördü
Doktor hastanın {kardinal.yas} yaşında olduğunu söyledi
Bu oyun {kardinal.yas} yaş ve üzeri için uygun
Yeni {marka} {kardinal.model} çıktı
Ben de {marka} {kardinal.model:belirtme} aldım
Geçen hafta {marka} {kardinal.model:yonelme} geçtim
{isim} {marka} {kardinal.model:ayrilma} memnun değil
Bu {marka} {kardinal.model:bulunma} kamera çok iyi
{marka} {kardinal.model:ilgi} fiyatı düştü
"""

_RAW["buyuk"] = """
Şehrin nüfusu {buyuk.nufus}
Şirketin yıllık cirosu {buyuk.tl}
Bütçe {buyuk.tl} olarak belirlendi
Videoyu {buyuk.yuvarlak} {kisi} izledi
Bu proje için {buyuk.tl} yatırım yapıldı
Ülkenin nüfusu yaklaşık {buyuk.yuvarlak} {kisi}
Stadyumun yapımı {buyuk.tl} tuttu
Şirket {buyuk.tl} zarar açıkladı
Hükümet eğitime {buyuk.tl} ayırdı
Şehir geçen yıl {buyuk.yuvarlak} turist ağırladı
Oyun çıktığı gün {buyuk.duz} kopya sattı
Tablo müzayedede {buyuk.tl} değer buldu
Bağış kampanyasında {buyuk.tl} toplandı
Satışlar {buyuk.tl:yonelme} yükseldi
İzlenme {buyuk.yuvarlak:yonelme} ulaştı
Satışlar {buyuk.duz:yonelme} ulaştı
Şirketin değeri {buyuk.tl:belirtme} aştı
Toplam {buyuk.duz} {kisi} başvurdu
{buyuk.tl:lik} bir yatırım planı açıklandı
Dünya nüfusu {buyuk.milyar} kişiyi aştı
Albüm {buyuk.duz} kez dinlendi
Yatırımcılar {buyuk.tl:ayrilma} fazla para topladı
Müzenin ziyaretçi sayısı {buyuk.yuvarlak} oldu
Kampanyaya {buyuk.duz} {kisi} destek verdi
Şehre {buyuk.tl} değerinde bir köprü yapılacak
Uygulama {buyuk.yuvarlak} kez indirildi
Piyasa değeri {buyuk.tl} seviyesinde
Kasım ayı gelirleri {buyuk.tl} olarak kaydedildi
"""

_RAW["eksi"] = """
Dışarıda hava {eksi.derece}
Yarın sıcaklık {eksi.derece} olacak
Gece sıcaklık {eksi.derece} civarında
Zirvede termometre {eksi.derece} gösteriyor
Sıcaklık {eksi.derece:yonelme} düştü
Dondurucu {eksi.santigrat} sıcaklığa ayarlı
Hesap bakiyem {eksi.tl}
Bakiye {eksi.tl} görünüyor
Takımın averajı {eksi.sayi}
Puan farkı {eksi.sayi}
Hava {eksi.derece:ayrilma} aşağı düşmedi
Dağda sıcaklık {eksi.derece:ayrilma} aşağı iniyor
Termometre {eksi.derece:yonelme} kadar indi
Bu kış ilk kez {eksi.derece:belirtme} gördük
Bakiyem {eksi.tl:yonelme} düştü
Sabah termometre {eksi.derece} gösterdi
Soğuk hava dalgası geliyor ve sıcaklık {eksi.derece}
Buzdolabı {eksi.santigrat} değerinde çalışıyor
Dün gece {eksi.derece} ölçüldü
Kamp alanında sıcaklık {eksi.derece} idi
Dondurucu {eksi.santigrat:bulunma} saklayın
Hava durumu raporuna göre sıcaklık {eksi.derece}
Kuzeyde gece sıcaklıkları {eksi.santigrat:yonelme} kadar düşecek
Kredi kartı borcum yüzünden hesap {eksi.tl} oldu
"""

_RAW["karisik"] = """
Pazardan {olcu.agirlik} {urun} aldım, hesap {para.tl} tuttu
Toplantı {tarih.gunay} tarihinde saat {saat:bulunma} başlayacak
Bu ürün {yuzde} indirimle {para.tl} oldu
{tarih.gunay} günü saat {saat} civarında {telefon} numarasını ara
Sınıfta {kardinal.orta} öğrenci var, bunların {yuzde} devamsız
Maç {skor} bitti, stat {kardinal.bin} seyirciyle doldu
Hava {eksi.derece}, yol {olcu.mesafe} kadar sürüyor
Kargo {tarih.gunay} tarihinde saat {saat:bulunma} gelecek
{sira.kat} katta {olcu.alan} bir daire kiraladım
{para.tl} değerindeki ürünü {yuzde} indirimle aldım
Randevu {tarih.gunay} saat {saat}, kod {kod}
Uçuş saat {saat:bulunma}, bagaj hakkı {olcu.agirlik}
Doğum günü {tarih.gunay}, hediye bütçesi {para.tam}
Bu telefon {olcu.veri} hafızalı ve {para.tam}
Bugün sıcaklık {olcu.sicaklik}, nem {yuzde}
{aralik} {kisi} için {olcu.hacim} süt yeter
Final {skor} bitti, galibiyet primi {para.tam}
{isim} {olcu.boy} boyunda ve {olcu.agirlik} ağırlığında
Eve {olcu.mesafe} var, saat {saat:bulunma} orada olurum
Hesabımda {para.tl} var, faiz oranı {yuzde}
Telefon {telefon}, posta kodu {kod.posta}
{tarih.yil:bulunma} {kardinal.bin} {kisi} bu şehre taşındı
{sira.genel} haftada ders çalışmak için {aralik} saat ayır
Kar yağışı {olcu.uzunluk} kalınlığa ulaştı, sıcaklık {eksi.derece}
Konser {tarih.gunay} saat {saat:bulunma}, bilet {para.tam}
Şirket {buyuk.tl} kâr etti, hisse {yuzde} yükseldi
Araç {olcu.guc} güçte, fiyatı {para.tam}
Yolcu sayısı {kardinal.bin}, gecikme {aralik} dakika
Sabah {saat.sabah:bulunma} çıktım, hava {olcu.sicaklik}
{isim} {kardinal.yas} yaşında ve boyu {olcu.boy}
"""

# ----------------------------------------------------------------------------
# Negatif şablonlar
# ----------------------------------------------------------------------------
_RAW["negatif_es"] = """
{isim} akşam yemeğini erkenden yedi
Kedi bütün mamasını bir çırpıda yedi
Çocuk elmayı yedi, çekirdeğini attı
Dün akşam ne yedin
Köpek bahçede bulduğu kemiği yedi
Sabah kahvaltıda peynir ve zeytin yedik
Bütün tatlıyı tek başına yedi
Bu yemeği yedim ve çok beğendim
Masanın altında bir kalem buldum
Ayakkabılarını yatağın altına koydu
Köprünün altından küçük bir dere geçiyor
Ağacın altı yazın çok serin olur
Halının altına bir not bırakmış
Kediniz sandalyenin altında uyuyor
Bu işin altında başka bir şey olmalı
Altı çizili kelimeleri tekrar oku
Kutunun altını kontrol edin
Yağmurdan korunmak için çatının altına girdik
{isim} yüzünü yıkayıp çıktı
Yüzü gülüyordu ama gözleri yorgundu
Yazın denizde saatlerce yüzerim
Havuzda yüzmeyi yeni öğrendi
Yüzme kursuna haftada bir gün gidiyor
{isim} ile yüz yüze konuşmak istiyorum
Sabahları yüzümü soğuk suyla yıkarım
Yüzüğünü masanın üstünde unutmuş
Otobüse bin, ben seni bekleyeceğim
Son trene zor yetişip bindik
{isim} vapura binip karşıya geçti
Çocuk ata binmeyi çok seviyor
Bisiklete binerek okula gidiyorum
Taksiye binmeden önce fiyatı sor
Binanın girişinde bir kedi vardı
Ona bir şey söylemedim
Onu dün sokakta gördüm
Onun evine ilk kez gidiyorum
Onda bu yetenek var
Ondan hiç haber alamadık
Onlar yarın akşam gelecekmiş
Onlarla uzun uzun konuştum
Onları kapıda karşıladım
Onca yoldan geldik, bir çay bile yok
Çoban koyunları baharda kırkar
Berber çocuğun saçını kırktı
{isim} soframızın altına bakıp yüzünü buruşturdu
Havuzdan çıkınca yüzüm üşüdü
Annem bana ve ona aynı hediyeyi aldı
Ona sorarsan yarın gelir
"""

_RAW["negatif_kalip"] = """
Bir gün hepsi anlaşılacak
Bir şey söyleyeceğim
Bir an durup düşündü
Bir de sen gel, hep beraber gidelim
Bir türlü uyuyamadım
Birden ışıklar söndü
Hep birlikte yemek yedik
Mutfakta birkaç tabak kalmış
Bir sürü iş birikti
Çocuklar birbirine sarıldı
Biri kapıyı çaldı
İkisi de çok yorgundu
İkimiz de aynı okula gittik
Üçümüz birlikte yola çıktık
Onlarca insan meydanda toplanmıştı
Yüzlerce kuş gökyüzünde döndü
Binlerce kişi alanı doldurdu
Milyonlarca insan bu yayını izledi
Kırk yılda bir böyle fırsat çıkar
Seni gördüğüme iki gözüm çok sevindi
Yedi düvele karşı savaşmışlar
Tahtaya bir üçgen çizdi
Bebeğin beşiği odada duruyor
Sekizgen şeklinde bir masa aldık
{takim} yarışmada birinci oldu
Koşuda {isim} ikinci geldi
Sınavda {isim} üçüncü oldu
Kullanılmış ikinci el bir araba aldım
{isim} tatili dört gözle bekliyor
At dört nala koştu
Dört bir yandan ses geliyordu
Bu iş bire bir aynı
Sıfır kilometre araba aldık
Beş para etmez bir adam bu
Altı üstü bir kâğıt parçası
Bir iki gün dinlen
Bir iki dakika bekleyin
Biraz sonra döneceğim
Bir kez daha deneyelim
Bir dakika, hemen geliyorum
Bir araya geldik
Bir bakıma haklısın
Bir ara bunu konuşmuştuk
Hepsini bir arada tuttu
Bir daha olmasın
Birçok kişi bu fikre katıldı
İkisini de beğendim
Çocuklar ikişer ikişer sıraya girdi
Çocuklara üçer elma verdi
Yüzbaşı toplantıya katıldı
Binbaşı sabah nöbete geldi
Dörtlü koltuk takımı aldık
Üçlü sohbet çok eğlenceliydi
İkinci bir şansı hak ediyor
Kasımda hava soğur
Mart ayında kar yağdı
Nisan yağmuru bereket getirir
Haziranda deniz ısınır
Ekim ayı yağmurlu geçti
Şubat kısa ama soğuk bir aydır
Eylülde okullar açılır
Mayıs ayında çiçekler açar
{takim} taraftarı stadı doldurdu
{takim} takımı geçen hafta kazandı
{sehir} kış turizminde çok gözde
Hep birlikte {sehir} yoluna çıktık
Birlik olursak her şeyi başarırız
"""


# ----------------------------------------------------------------------------
# Şablon kayıtları
# ----------------------------------------------------------------------------
POZITIF_KATEGORILER = ["para", "yuzde", "olcu", "saat", "tarih", "sira", "telefon", "kod", "skor", "aralik",
                       "ondalik", "kardinal", "buyuk", "eksi", "karisik"]
SABLONLAR: dict[str, list[tuple[str, str]]] = {}
for _k, _v in _RAW.items():
    _satirlar = [s.strip() for s in _v.strip().splitlines() if s.strip()]
    SABLONLAR[_k] = [(f"{_k}-{i:03d}", s) for i, s in enumerate(_satirlar)]

SLOT = re.compile(r"\{(\w+)(?:\.(\w+))?(?::(\w+))?\}")


def _test_secimi() -> set[str]:
    rng = random.Random("megazeka-sayi-sablon-bolunmesi")
    secili: set[str] = set()
    for k in sorted(SABLONLAR):
        idler = [i for i, _ in SABLONLAR[k]]
        n = max(2, round(0.15 * len(idler)))
        secili.update(rng.sample(idler, n))
    return secili


TEST_SABLONLARI: set[str] = _test_secimi()
SABLON_METNI = {i: m for lst in SABLONLAR.values() for i, m in lst}


def sablonlar(kategori: str, test: bool) -> list[tuple[str, str]]:
    return [(i, m) for i, m in SABLONLAR[kategori] if (i in TEST_SABLONLARI) == test]


def _dogrula():
    for lst in SABLONLAR.values():
        for i, m in lst:
            for ad, alt, ek in SLOT.findall(m):
                assert ad in FILLERS or ad in V.ORNEKLEYICILER, (i, ad)
                if ek:
                    from .turkce import EKLER
                    assert ek in EKLER, (i, ek)


_dogrula()

# ----------------------------------------------------------------------------
# Cümle üretimi
# ----------------------------------------------------------------------------
_NOKTALAMA = str.maketrans("", "", '.,!?;:"…')


ACILISLAR = ["Bugün", "Sonra", "Sanırım", "Bence", "Açıkçası", "Neyse", "Yine de", "Gerçekten", "Baksana",
              "Hatırlıyor musun", "Tabii", "Evet", "Hayır", "Aslında", "Maalesef", "Şunu söyleyeyim", "Geçen hafta",
              "Bu arada", "Öğretmen dedi ki", "Annem söyledi", "Hepimiz biliyoruz ki", "Kısacası", "Önce şunu bil"]
KAPANISLAR = ["galiba", "sence de öyle değil mi", "diye düşündüm", "dedi bana", "ama neyse", "herkes biliyor", "yani",
              "öyle sanıyorum", "bunu unutma"]


def sarmala(metin: str, rng: random.Random) -> str:
    """Statik negatif cümlelere açılış/kapanış ekleyerek çeşitlilik sağlar."""
    if rng.random() < 0.6:
        ilk = metin if metin.startswith("{") else lower_tr(metin[:1]) + metin[1:]
        metin = rng.choice(ACILISLAR) + ", " + ilk
    if rng.random() < 0.35 and not metin.rstrip().endswith(("?", "!")):
        metin = metin + ", " + rng.choice(KAPANISLAR)
    return metin


def cumle_uret(metin: str, rng: random.Random, buyuk_harf: bool, politika: str | None = None,
               yazili_mod: bool = False, sarmalayici: bool = False):
    """(girdi, hedef, kalir_mi, varlik_sayisi, varlik_kategorileri) döndürür.

    yazili_mod=True: sözlü yerine yazılı biçim iki tarafa da konur (negatif_yazili).
    """
    politika = politika or KUCUK_SAYI_POLITIKASI
    if sarmalayici:
        metin = sarmala(metin, rng)
    parcalar = []
    son_bitis = 0
    kullanilan: dict[str, set] = {}
    for m in SLOT.finditer(metin):
        if m.start() > son_bitis:
            parcalar.append(("m", metin[son_bitis:m.start()], metin[son_bitis:m.start()]))
        ad, alt, ek = m.group(1), m.group(2) or None, m.group(3) or None
        if ad in FILLERS:
            havuz = [x for x in FILLERS[ad] if x not in kullanilan.setdefault(ad, set())]
            s = rng.choice(havuz)
            kullanilan[ad].add(s)
            parcalar.append(("m", s, s))
        else:
            v = V.ORNEKLEYICILER[ad](rng, alt, ek, politika, buyuk_harf)
            parcalar.append(("v", v, None))
        son_bitis = m.end()
    if son_bitis < len(metin):
        parcalar.append(("m", metin[son_bitis:], metin[son_bitis:]))

    girdi, hedef = [], []
    kalir = True
    kategoriler = []
    for tur, a, b in parcalar:
        if tur == "m":
            if not buyuk_harf:
                a = lower_tr(a).translate(_NOKTALAMA)
                b = a
            girdi.append(a)
            hedef.append(b)
        else:
            v = a
            kategoriler.append(v.kategori)
            if not v.kalir:
                kalir = False
            if yazili_mod:
                girdi.append(v.yazili)
            else:
                girdi.append(v.sozlu if buyuk_harf else lower_tr(v.sozlu))
            hedef.append(v.yazili)
    g, h = "".join(girdi), "".join(hedef)
    if buyuk_harf:
        if g[-1] not in ".?!":
            g += "."
            h += "."
        g, h = ilk_harfi_buyut(g), ilk_harfi_buyut(h)
    g = re.sub(r" {2,}", " ", g).strip()
    h = re.sub(r" {2,}", " ", h).strip()
    return g, h, kalir, len(kategoriler), kategoriler
