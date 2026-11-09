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

# Negatif ve ekli-sayı şablonları için ek dolgu listeleri (yer tutucu çeşitliliği)
FILLERS.update({
    "tasit_dat": ["otobüse", "vapura", "trene", "taksiye", "metroya", "uçağa", "minibüse", "tramvaya", "feribota",
                  "dolmuşa", "servise", "teleferiğe"],
    "binek_dat": ["ata", "bisiklete", "motosiklete", "deveye", "katıra", "tekneye", "eşeğe"],
    "yiyecek": ["çorba", "pilav", "makarna", "börek", "mantı", "salata", "kebap", "köfte", "tost", "simit", "dondurma",
                "kek", "menemen", "balık"],
    "yiyecek_acc": ["çorbayı", "pilavı", "makarnayı", "böreği", "mantıyı", "salatayı", "kebabı", "köfteyi", "tostu",
                    "simidi", "dondurmayı", "keki", "menemeni", "balığı", "tatlıyı", "pastayı", "karpuzu"],
    "yiyecek_gen": ["pastanın", "pizzanın", "karpuzun", "kavunun", "ekmeğin", "tatlının", "böreğin", "çikolatanın",
                    "kekin", "baklavanın"],
    "tabakli": ["pilav", "makarna", "mantı", "çorba", "salata", "börek", "meze"],
    "dilimli": ["pizza", "pasta", "karpuz", "kavun", "ekmek", "kek", "tart"],
    "zaman_gecmis": ["dün akşam", "dün gece", "geçen hafta", "bu sabah", "az önce", "geçen yaz", "pazar günü",
                     "bayramda", "dün", "öğle arasında", "cuma akşamı", "tatilde"],
    "zaman_gelecek": ["yarın", "haftaya", "önümüzdeki hafta", "bu akşam", "pazartesi günü", "yaz gelince",
                      "bayramdan sonra", "cumartesi günü"],
    "su_yeri": ["denizde", "havuzda", "gölde", "nehirde", "koyda", "kıyıda", "açık denizde", "sahilde",
                "dalgalı denizde"],
    "alt_gen": ["masanın", "yatağın", "koltuğun", "sandalyenin", "halının", "dolabın", "köprünün", "çatının",
                "kutunun", "tezgâhın", "arabanın", "minderin", "merdivenin"],
    "agac_gen": ["çınarın", "kavağın", "söğüdün", "ceviz ağacının", "dut ağacının", "çam ağacının"],
    "kucuk_nesne": ["kalem", "anahtar", "çorap", "mektup", "oyuncak", "gözlük", "küpe", "defter"],
    "kucuk_acc": ["kalemi", "anahtarı", "çorabı", "mektubu", "oyuncağı", "gözlüğü", "küpeyi", "defteri"],
    "yer_loc": ["bahçede", "kapıda", "markette", "durakta", "okulda", "parkta", "sahilde", "kafede", "istasyonda",
                "pazarda", "merdivende"],
    "sey_acc": ["kitabı", "anahtarı", "mektubu", "çiçeği", "paketi", "hediyeyi", "haberi", "çantayı"],
    "iyelikli": ["evi", "arabası", "sesi", "bahçesi", "fikri", "kitabı", "telefonu", "odası"],
    "ozellik": ["çok güzel bir ses", "büyük bir sabır", "ince bir zekâ", "ilginç bir yetenek", "tuhaf bir sakinlik",
                "eşsiz bir hafıza"],
    "mevsim_loc": ["baharda", "ilkbaharda", "yaz başında", "yaz gelmeden", "sıcaklar başlamadan"],
    "hayvan_acc": ["koyunları", "kuzuları", "davarları", "tiftik keçilerini"],
    "ikinci_el_esya": ["araba", "telefon", "bisiklet", "kamera", "bilgisayar", "koltuk", "motosiklet", "buzdolabı",
                       "tablet", "oyun konsolu", "fotoğraf makinesi", "kitap", "mont", "halı"],
    "mekan": ["otel", "restoran", "kafe", "berber", "tamirci", "lokanta", "pastane"],
    "malzeme": ["kumaş", "deri", "ahşap", "mermer", "boya", "yün"],
    "sure_birim": ["gün", "saat", "hafta", "dakika", "ay"],
    "beklenen": ["tatili", "bayramı", "sonucu", "mektubu", "haberi", "baharı", "maçı", "yazın gelmesini",
                 "bebeğin doğumunu"],
    "olay": ["bayram", "tatil", "haber", "misafir", "bahar", "mektup", "gün"],
    "kesir_nom": ["üçte biri", "dörtte biri", "dörtte üçü", "beşte ikisi", "beşte üçü", "beşte biri", "altıda biri",
                  "altıda beşi", "yedide ikisi", "sekizde üçü", "dokuzda biri", "onda biri", "onda dokuzu", "onda üçü",
                  "üçte ikisi"],
    "kesir_acc": ["üçte birini", "dörtte birini", "dörtte üçünü", "beşte ikisini", "beşte üçünü", "beşte birini",
                  "altıda birini", "altıda beşini", "yedide ikisini", "sekizde üçünü", "dokuzda birini", "onda birini",
                  "onda dokuzunu", "onda üçünü", "üçte ikisini"],
    "kesir_bare": ["üçte bir", "dörtte bir", "dörtte üç", "beşte iki", "beşte üç", "beşte bir", "altıda bir",
                   "altıda beş", "yedide iki", "sekizde üç", "dokuzda bir", "onda bir", "onda dokuz", "onda üç",
                   "üçte iki"],
    "kesir_dat": ["üçte birine", "dörtte üçüne", "beşte ikisine", "onda birine", "altıda birine"],
    "ay_ek": ["ocakta", "şubatta", "martta", "nisanda", "mayısta", "haziranda", "temmuzda", "ağustosta", "eylülde",
              "ekimde", "kasımda", "aralıkta"],
    "ay_abl": ["ocaktan", "şubattan", "marttan", "nisandan", "mayıstan", "hazirandan", "temmuzdan", "ağustostan",
               "eylülden", "ekimden", "kasımdan", "aralıktan"],
    "ay_dat": ["ocağa", "şubata", "marta", "nisana", "mayısa", "hazirana", "temmuza", "ağustosa", "eylüle", "ekime",
               "kasıma", "aralığa"],
    "ay_gen": ["ocağın", "şubatın", "martın", "nisanın", "mayısın", "haziranın", "temmuzun", "ağustosun", "eylülün",
               "ekimin", "kasımın", "aralığın"],
    "ay_bare": ["ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım",
                "aralık"],
    "urun_gen": ["elmanın", "domatesin", "peynirin", "zeytinin", "çayın", "kahvenin", "şekerin", "unun", "balın",
                 "tavuğun", "kıymanın"],
})

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

# ---- Ek çeşitliliği: kuruş / döviz / derece (sözcük kalan birim + yalın ek) ----
_RAW["para"] += """
Bu {urun} pazarda {para.kurus:yonelme} satılıyordu
{isim} yerde {para.kurus:belirtme} buldu
Aradaki {para.kurus:ilgi} farkı için pazarlık yaptık
{para.kurus:lik} bir şeker aldım
Fiyat {para.kurus:ayrilma} başlıyor
Çocuk {para.kurus:vasita} yetindi
Simidi {para.kurus:yonelme} aldım
{isim} bozukluğu {para.kurus:yonelme} tamamladı
Bu {urun} kasada {para.kurus:bulunma} duruyordu
Eskiden bir poşet {para.kurus:yonelme} satılırdı
Çay ocağında {para.kurus:ilgi} zam yapıldı
Bu {esya} {para.doviz:yonelme} satılıyor
{isim} bu {esya} için {para.doviz:ayrilma} fazla ödedi
Tatil bütçesi {para.doviz:ilgi} üzerine çıktı
{isim} {para.doviz:belirtme} cebine koydu
{para.doviz:lik} bir hediye aldım
Mağazada {para.doviz:vasita} alışveriş yaptım
Biletleri {para.doviz:yonelme} sattılar
Gece başına {para.doviz:yonelme} kalıyoruz
Kuru {para.doviz:ilgi} altına düşünce satış yaptık
Pazarlıkla fiyatı {para.doviz:yonelme} indirdiler
Cüzdanda {para.doviz:bulunma} kalmıştı
Yolculuk masrafı {para.doviz:ayrilma} başlıyor
Bu odayı {para.doviz:yonelme} kiraladık
{isim} bahşişi {para.doviz:belirtme} aştı
Menüdeki en pahalı yemek {para.doviz:yonelme} geliyor
{isim} borcunu {para.doviz:vasita} kapattı
"""

_RAW["olcu"] += """
Sıcaklık {olcu.sicaklik:yonelme} çıktı
Fırını {olcu.sicaklik:yonelme} getirin
Termometre {olcu.sicaklik:belirtme} gösteriyor
Hava {olcu.sicaklik:ilgi} altına düştü
Su {olcu.sicaklik:vasita} kaynadı
"""

# ---- Ek çeşitliliği: son sözcüğe göre dengelenmiş (altı/dokuz/otuz/kırk/on/sıfır ... x ek türü) ----
_RAW["kardinal"] += """
Hesap makinesine {kardinal.ekli:belirtme} yazdım
Kuponda {kardinal.ekli:belirtme} işaretledim
Ekranda {kardinal.ekli:belirtme} gördüm ve şaşırdım
Tabelada {kardinal.ekli:belirtme} okudum
Şifreye {kardinal.ekli:belirtme} ekle
{kardinal.ekli:ilgi} karesini hesapladım
Listedeki {kardinal.ekli:ilgi} yerine başka bir sayı yaz
{kardinal.ekli:ilgi} katlarını tabloya ekleyin
{kardinal.ekli:ilgi} bir fazlasını bulmamız gerekiyor
Soruda geçen {kardinal.ekli:ilgi} karekökünü bul
Gelenlerin {kardinal.ekli:iyelik3} çocuktu
Oyların {kardinal.ekli:iyelik3} bana geldi
Sınıftakilerin {kardinal.ekli:iyelik3} devamsızlık yapmıştı
Ankete katılanların {kardinal.ekli:iyelik3} kararsızdı
Misafirlerin {kardinal.ekli:iyelik3} erken ayrıldı
Toplamı {kardinal.ekli:vasita} çarpın
Sonucu {kardinal.ekli:vasita} bölün
Bu sayıyı {kardinal.ekli:vasita} toplayınca sonuç değişmiyor
Cevabı {kardinal.ekli:vasita} karşılaştırdım
Hesabı {kardinal.ekli:vasita} bitirdik
{kardinal.ekli:yonelme} kadar say
Sıra sonunda {kardinal.ekli:yonelme} geldi
Sayacı {kardinal.ekli:yonelme} getirdik
Sonuç {kardinal.ekli:yonelme} yuvarlandı
Puan tablosu {kardinal.ekli:yonelme} ulaştı
Sayaç şu an {kardinal.ekli:bulunma} duruyor
Sıra {kardinal.ekli:bulunma} kaldı
Takip numarası {kardinal.ekli:bulunma} bitiyor
Hesaplama {kardinal.ekli:bulunma} tıkandı
Başvurular {kardinal.ekli:bulunma} kapandı
Sayımı {kardinal.ekli:ayrilma} başlattık
Liste {kardinal.ekli:ayrilma} sonra devam ediyor
{kardinal.ekli:ayrilma} geriye doğru saydık
Numaralandırma {kardinal.ekli:ayrilma} başlıyor
Tablo {kardinal.ekli:ayrilma} itibaren tekrar ediyor
Numara {kardinal.ekli:bulunma} sıfırlanıyor
Kayıtlar {kardinal.ekli:bulunma} sona erdi
Kontenjan {kardinal.ekli:bulunma} doldu
Fiyat listesi {kardinal.ekli:ayrilma} sonra değişiyor
Bilet satışı {kardinal.ekli:ayrilma} başlayacak
Puanlar {kardinal.ekli:ayrilma} geriye sayılıyor
Rakam {kardinal.ekli:yonelme} ulaşınca alarm çalıyor
Sayfa numarası {kardinal.ekli:yonelme} atladı
Toplamı {kardinal.ekli:yonelme} tamamla
Katılımcı sayısını {kardinal.ekli:ilgi} üstüne taşıyalım
Seçilen sayının {kardinal.ekli:ilgi} tersi lazım
"""

_RAW["ondalik"] += """
Ateşi ölçtüm, {ondalik.ekli:belirtme} gördüm
Ekrana {ondalik.ekli:belirtme} yazdım
Hesap makinesinde {ondalik.ekli:belirtme} buldum
Notu {ondalik.ekli:belirtme} gören hoca şaşırdı
Terazi {ondalik.ekli:belirtme} gösterince fark ettim
{ondalik.ekli:ilgi} karesini aldım
{ondalik.ekli:ilgi} yuvarlanmış hâli lazım
Tabloda {ondalik.ekli:ilgi} altında kalan değerler eleniyor
Ölçümde {ondalik.ekli:ilgi} üstüne çıkmayın
Sınırı {ondalik.ekli:ilgi} bir tık altına çektik
Ortalamanın {ondalik.ekli:iyelik3} ders notundan geliyor
Sonucun {ondalik.ekli:iyelik3} hata payı
Puanın {ondalik.ekli:iyelik3} yazılıdan geldi
Değerin {ondalik.ekli:iyelik3} sabit tutuldu
Ölçümlerin {ondalik.ekli:iyelik3} tabloya girmedi
Sonucu {ondalik.ekli:vasita} çarpın
Bu değeri {ondalik.ekli:vasita} toplayın
Ölçümü {ondalik.ekli:vasita} karşılaştırdık
Notlar {ondalik.ekli:vasita} eşit çıktı
Katsayıyı {ondalik.ekli:vasita} hesapladık
Ortalamam {ondalik.ekli:yonelme} yükseldi
Değer {ondalik.ekli:yonelme} yuvarlandı
Ateş {ondalik.ekli:yonelme} çıktı
Not {ondalik.ekli:yonelme} düştü
Faiz {ondalik.ekli:yonelme} sabitlendi
Ateş {ondalik.ekli:bulunma} seyrediyor
Cihaz {ondalik.ekli:bulunma} kalibre edildi
Değer {ondalik.ekli:bulunma} sabitlendi
Ortalama {ondalik.ekli:bulunma} kaldı
Ölçüm {ondalik.ekli:bulunma} durdu
Ortalamam {ondalik.ekli:ayrilma} aşağı düşmedi
Değerler {ondalik.ekli:ayrilma} başlıyor
Sonuç {ondalik.ekli:ayrilma} fazla çıktı
Ölçüm {ondalik.ekli:ayrilma} itibaren geçerli
Ateşim {ondalik.ekli:ayrilma} yukarı çıkmadı
"""

_RAW["yuzde"] += """
Zam oranı {yuzde.ekli:belirtme} geçmedi
Partinin oyu {yuzde.ekli:belirtme} buldu
{yuzde.ekli:ilgi} üzerindeki faiz oranları yüksek sayılır
Zam oranı {yuzde.ekli:ilgi} altında kaldı
Mevcudun {yuzde.ekli:iyelik3} sınavı geçti
Bütçenin {yuzde.ekli:iyelik3} eğitime gidiyor
Kâr marjı {yuzde.ekli:vasita} sınırlı kaldı
Hedefi {yuzde.ekli:vasita} tutturduk
Oran {yuzde.ekli:yonelme} düştü
Katılım {yuzde.ekli:yonelme} ulaştı
Şarj {yuzde.ekli:bulunma} kaldı
Stok {yuzde.ekli:bulunma} bitti
Şarj {yuzde.ekli:ayrilma} aşağı düşünce uyardı
Bu oran {yuzde.ekli:ayrilma} fazla olmamalı
"""


# ----------------------------------------------------------------------------
# Negatif şablonlar (yer tutuculu; her olgu birden çok taşıyıcı yapıda ve kişi/zaman/kip çeşitliliğiyle)
# ----------------------------------------------------------------------------
_RAW["negatif_es"] = """
Hadi {tasit_dat} bin, geç kalıyoruz
{tasit_dat} bin hemen, {isim} seni bekliyor
{isim}, {tasit_dat} bin de gel
{yer_loc} bekleme, {tasit_dat} bin de buraya gel
Çocuklar, {tasit_dat} binin lütfen
{zaman_gecmis} {tasit_dat} bindik
{isim} {zaman_gecmis} {tasit_dat} bindi ve yola çıktı
{tasit_dat} binerek {sehir} şehrine gittik
{tasit_dat} binip eve döndüm
Yarın {tasit_dat} bineceğim
{isim} her sabah {tasit_dat} biniyor
Biz {tasit_dat} binmek istemiyoruz
{tasit_dat} binmeden önce bileti kontrol et
{zaman_gecmis} {tasit_dat} bindim, hemen uyudum
Onlar {tasit_dat} binmeye hazırlanıyordu
{isim} {tasit_dat} binmeyi hiç sevmez
Bu akşam {tasit_dat} binelim mi
Hepimiz {tasit_dat} binsek yer kalmaz
Sakın {tasit_dat} binme, bozuk
Sen {tasit_dat} bin, ben arkadan gelirim
Yolcular {tasit_dat} biniyor, kapılar kapanacak
Haydi {binek_dat} bin de gösterişini yap
{isim} {binek_dat} binmeyi küçük yaşta öğrendi
Çocuklar {zaman_gecmis} {binek_dat} bindi
Ben {binek_dat} binerek köye gittim
{zaman_gecmis} {binek_dat} binemedim, korktum
{zaman_gecmis} {su_yeri} bir saat yüzdük
{isim} {su_yeri} uzun süre yüzdü
Biz {su_yeri} saatlerce yüzdük
Ben {su_yeri} biraz yüzdüm
Çocuklar {su_yeri} sabaha kadar yüzdüler
{isim} her sabah {su_yeri} yüzüyor
Yarın {su_yeri} yüzmeye gidiyoruz
{isim} yüzmeyi çok iyi biliyor
Yüzmek isteyenler kıyıya gelsin
Hadi yüz biraz, su çok güzel
{su_yeri} yüzen çocuklar çok eğleniyordu
{isim} aynadaki yüzüne baktı
Sabahları yüzümü yıkamayı unutmam
{isim} utancından yüzünü kapattı
Yüzüne bakınca hemen anladım
Bu yüzden toplantıya gidemedik
{isim} yüzünden hepimiz geç kaldık
Yüzü kızaran {isim} hemen odadan çıktı
{isim} yüzüğünü {yer_loc} unutmuş
{isim} bana yüz çevirdi
Yüz yüze konuşmak daha iyi
{isim} {zaman_gecmis} {yiyecek_acc} yedi
Biz {zaman_gecmis} {yiyecek} yedik
Ben {yiyecek_acc} yedim ama hâlâ acıkmıştım
Çocuklar {zaman_gecmis} {yiyecek} yediler
Sen {zaman_gecmis} ne yedin
Siz {yiyecek_acc} yediniz mi
{isim} yemeğini yedi ve masadan kalktı
{isim} {tabakli} yedi, sonra çay içti
Az önce {sehir} lokantasında {yiyecek} yedik
{isim} iki tabak {tabakli} yedi
Dün iki dilim {dilimli} yedim
{agac_gen} altında oturup {yiyecek} yedik
Ne yedik ne içtik, hepsi boşa gitti
{alt_gen} altında bir {kucuk_nesne} buldum
{isim} {kucuk_acc} {alt_gen} altına sakladı
Kedi {alt_gen} altından çıktı
{alt_gen} altı çok tozlanmış
{alt_gen} altını silmeyi unutma
{zaman_gecmis} {alt_gen} altına bir şey düşürdüm
Bu işin altında başka bir iş var
Altı çizili cümleleri tekrar oku
{isim} bu yükün altından tek başına kalkamaz
{isim} {alt_gen} altında {kucuk_nesne} aradı
Bu raporun altına imzanızı atın
{isim} ona {sey_acc} verdi
Ona ne dedin
Onu {zaman_gecmis} {yer_loc} gördüm
Onun {iyelikli} çok güzelmiş
Onda {ozellik} var
Ondan {zaman_gecmis} haber aldım
Onlar {zaman_gelecek} {sehir} yolculuğuna çıkacak
Onları {yer_loc} bekledim
Onlara haberi ben verdim
Onlarla {zaman_gecmis} {yer_loc} buluştum
Onlardan hiçbiri gelmedi
{isim} onu ve beni aradı
Onca zahmete rağmen {isim} vazgeçmedi
Ona göre {isim} haklı
Onunla {yer_loc} konuştum
Çoban {mevsim_loc} {hayvan_acc} kırkar
{isim} dün {hayvan_acc} kırktı
Köylüler {hayvan_acc} kırkmak için toplandı
Berber müşterinin saçını kırktı
Biz {zaman_gecmis} koyunları kırktık
Kırkım mevsimi gelince herkes yaylaya çıkar
{isim} yarın tüm kuzuları kırkacak
Her yıl bu zamanlarda koyunlar kırkılır
{isim} {zaman_gecmis} ikinci el bir {ikinci_el_esya} aldı
Ben ikinci el bir {ikinci_el_esya} almayı düşünüyorum
İkinci el {ikinci_el_esya} satan bir dükkân açtılar
Bu {ikinci_el_esya} ikinci el ama çok temiz
İkinci el {ikinci_el_esya} ilanlarına baktım
Kullanılmış ikinci el bir {ikinci_el_esya} bulduk
{isim} ikinci el {ikinci_el_esya} alırken çok dikkatli davranır
Pazarda ikinci el {ikinci_el_esya} aradık
{isim} oradaki hizmeti birinci sınıf buldu
{sehir} yakınlarında birinci sınıf bir {mekan} bulduk
Bu {malzeme} birinci sınıf, hiç solmaz
Mobilyada birinci sınıf {malzeme} kullanılmış
Bu {urun} birinci sınıf kalitede
Garsonlar birinci sınıf hizmet veriyordu
"""

_RAW["negatif_kalip"] = """
Bu işi bir iki {sure_birim} içinde bitiririz
Bir iki {sure_birim} dinlenip yola devam ederiz
{isim} bir iki {sure_birim} sonra döner
{isim} bana bir iki kelime söyledi ve çıktı
Toplantıda bir iki {kisi} söz aldı
Çantamda bir iki {kucuk_nesne} var
Bir iki derken akşam oldu
Sınavda bir iki soru yanlış çıktı
Bir iki adım attı ve durdu
Bir iki kez denedim ama olmadı
Bir ya da iki {sure_birim} sürer
Bir iki bardak çay içip çıkarız
Bir kaç {sure_birim} sonra haber veririm
Birkaç {kisi} kapıda bekliyordu
{isim} birkaç {urun} aldı
Bir kaç gündür {isim} ortada yok
Bir gün {isim} bana {yer_loc} rastladı
{isim} bir şey söyleyecekti ama vazgeçti
{isim} bir an durup etrafına baktı
{isim} bir de {urun} istedi
Bir türlü {urun} bulamadım
Birden {yer_loc} ışıklar söndü
{isim} ve {isim} birlikte {sehir} yoluna çıktı
Masada bir sürü {urun} vardı
Yolcular birbirine yer açtı
Biri {yer_loc} seni arıyordu
İkisi de {zaman_gecmis} geç kaldı
İkimiz de {sehir} şehrinde doğduk
Üçümüz {zaman_gecmis} yola çıktık
Dördümüz aynı sınıftaydık
Beşimiz hep aynı masada otururduk
Onlarca {kisi} {yer_loc} toplanmıştı
Yüzlerce {kisi} {sehir} sokaklarında yürüdü
Binlerce {kisi} {sehir} meydanını doldurdu
Milyonlarca {kisi} bu haberi izledi
{takim} ligi birinci tamamladı
{isim} yarışta ikinci geldi
{isim} sınavda üçüncü oldu
Ödül töreninde {isim} birinci seçildi
Koşuda {isim} dördüncü oldu
Öğretmen tahtaya bir üçgen ve bir sekizgen çizdi
Bebeğin beşiği {yer_loc} duruyordu
{isim} sekizgen şeklinde bir masa aldı
Arıların petekleri altıgen biçimindedir
{isim} {yiyecek_gen} {kesir_acc} yedi
{isim} {yiyecek_gen} yarısını yedi
Sınıfın {kesir_nom} dün gelmedi
Nüfusun {kesir_nom} gençlerden oluşuyor
{isim} maaşının {kesir_acc} kiraya veriyor
Kitabın {kesir_acc} okudum
Tarlanın {kesir_nom} henüz ekilmedi
Havuzun {kesir_bare} kadarı doldu
Yolun {kesir_bare} kadarını yürüdük
Bütçenin {kesir_nom} eğitime ayrıldı
Hastaların {kesir_nom} taburcu edildi
Ormanın {kesir_nom} yandı
Okulun {kesir_nom} yeni öğrencilerden oluşuyor
Kazancın {kesir_dat} razıyım
Dersin {kesir_bare} kadarını dinledim
Maaşımın yarısı kiraya gidiyor
Salonun çeyreği boş kaldı
Çeyrek final maçı {zaman_gelecek} oynanacak
{isim} bakkaldan yarım kilo {urun} aldı
Çeyrek kilo {urun} yeter
{isim} ikide bir saatine bakıyor
Çocuk ikide bir {urun} istiyor
{isim} {beklenen} dört gözle bekliyor
Hepimiz {beklenen} dört gözle bekledik
Dört gözle beklediğimiz {olay} sonunda geldi
{isim} kırk yılda bir bizi arar
Kırk yılda bir {sehir} şehrine gidiyoruz
Böyle bir fırsat kırk yılda bir çıkar
Gelirsen iki gözüm üstüne
Evladım {isim}, iki gözüm, dikkat et
Yedi düvele karşı {sehir} halkı direndi
{takim} yedi düvele meydan okudu
Yedi düvel birleşse bu halkı yenemez
{isim} {yiyecek_acc} bir çırpıda yedi
Bu soruyu bir çırpıda çözdü
Bütün kitabı bir çırpıda okudum
Sokakta tek tük insan vardı
Ağaçlarda tek tük yaprak kalmıştı
Kafede tek tük müşteri oturuyordu
Yağmur tek tük damlalarla başladı
Fiyatlar üç aşağı beş yukarı aynı
{isim} üç aşağı beş yukarı {sure_birim} sürer dedi
Maaşlar üç aşağı beş yukarı bu civarda
Üç aşağı beş yukarı bir saatte varırız
{isim} iki dirhem bir çekirdek giyinip çıktı
Düğüne iki dirhem bir çekirdek gitti
Kız iki dirhem bir çekirdek süslenmişti
{isim} kırk dereden su getirip bahane buldu
Kırk dereden su getirmeye gerek yok
Kırk dereden su getiriyorsun ama sebep belli
Beni bekletip dokuz doğurttu
Bekleye bekleye dokuz doğurduk
Salonun ortasında sekiz köşeli bir masa vardı
{isim} sekiz köşeli yıldız desenini çizdi
Altı üstü bir {kucuk_nesne} için kavga ettiler
Altı üstü bir kahve içeceğiz, bu kadar telaşa gerek yok
Altı üstü iki adım yol, yürüyelim
O adam beş para etmez biri
Bu {esya} beş para etmez
Beş para etmez bir iş yüzünden geç kaldık
{isim} ay sonunda beş parasız kaldı
Beş parasız {sehir} sokaklarında dolaştım
Annemin on parmağında on marifet vardı
Kızın on parmağında on marifet var, her işi yapar
{isim} gibi birinin on parmağında on marifet olur
İki arada bir derede kaldık
Yedi iklim dört bucak dolaştı
{isim} dört bir yandan gelen seslere kulak verdi
At dört nala koştu
Bu iş bire bir aynı
Sıfır kilometre bir araba aldık, çok memnunuz
{ay_ek} tatile çıkacağız
Ben {ay_ek} yeni bir işe başladım
Okullar {ay_ek} açılacak diyorlar
Kardeşim {ay_ek} askerden dönecek
{isim} {ay_ek} {sehir} şehrine taşındı
Bu proje {ay_ek} tamamlanacak
{ay_abl} beri {isim} bize uğramadı
{ay_abl} sonra hava değişti
{ay_dat} kadar sabret
{ay_dat} doğru işler yoluna girer
{ay_gen} sonunda kira artacak
{ay_gen} başında toplantı yapalım
{ay_gen} ilk haftasında {isim} gelecek
Geçen {ay_bare} ayında çok yağmur yağdı
Her {ay_bare} ayında bu festival yapılır
{ay_bare} ayı bu yıl çok yoğun geçti
Liranın değeri son aylarda sürekli düşüyor
Dolara olan talep birden arttı
Avro ve sterlin hakkında {isim} bir şey bilmiyor
Kuruşu kuruşuna hesap yaptı
{isim} her kuruşunu biriktirdi
Bir kuruşunu bile boşa harcamaz
{urun_gen} kilosu kaç lira
Bu ay {urun_gen} kilosu çok arttı
Kilo vermek istiyorsan şekeri bırak
{isim} geçen yıl çok kilo aldı
Kiloyu korumak vermekten zor
Terzi metreyi boynuma doladı
Metreyi alıp odayı ölçtük
Kumaşın metresi kaç lira
Bu zeytinyağının litresi kaç para
Benzinin litresi bu ay çok arttı
Derecesi yüksek bir ateşle geldi
Ateşinin derecesi neydi
Fırının derecesini ayarla
Termometredeki dereceyi okudum
Milimetre hassasiyetinde ölçüm yapıldı
Gram gram altın biriktirdi
Saatlerce {yer_loc} bekledik
Dakikalarca uğraştı ama açamadı
Saatin kaç olduğunu bilmiyorum
Saat kaç oldu
Kolundaki saat çok şıktı
Saatim yine bozuldu, kurmayı unutmuşum
Yüzde kaç indirim var
Bu işin yüzde kaçı bitti
{isim} yüzde hesabını hiç sevmez
{isim} ikiyüzlü bir insan, ona güvenme
Yüzsüz biri olduğunu herkes biliyor
Babam bana altın bir saat hediye etti
Yeni projeye onay verildi
Köprünün onarımı {zaman_gelecek} başlıyor
Arabanın yedek lastiğini {yer_loc} unuttum
Binici atından düştü
Binanın girişinde bir kedi vardı
{isim} yüzücü olmak istiyor
{isim} ve {isim} sonunda bir araya geldi
Bir bakıma {isim} haklı
Bir ara {isim} ile bunu konuşmuştuk
Çocukları hep bir arada tuttu
Bir daha {yer_loc} böyle bir şey olmasın
Birçok {kisi} bu fikre katıldı
İkisini de {zaman_gecmis} {yer_loc} gördüm
Çocuklara ikişer {kucuk_nesne} dağıttı
Yüzbaşı {zaman_gecmis} toplantıya katıldı
Binbaşı {zaman_gelecek} nöbete gelecek
Bir dakika {isim}, hemen geliyorum
Biraz sonra {isim} gelir
Bir kez daha deneyelim, belki olur
Hep birlikte {sehir} yoluna çıktık
Birlik olursak her şeyi başarırız
{takim} taraftarı {zaman_gecmis} stadı doldurdu
{sehir} kış turizminde çok gözde
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
