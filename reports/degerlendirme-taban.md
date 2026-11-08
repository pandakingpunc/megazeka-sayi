# Megazeka-Sayı değerlendirmesi — taban

Kontrol noktası: `yok (yalnız taban çizgileri)` · süre: 0 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) |
|---|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 |
| buyuk | 50 | 0.0 | 2.0 |
| eksi | 30 | 0.0 | 80.0 |
| kardinal | 100 | 16.0 | 72.0 |
| karisik | 60 | 0.0 | 53.3 |
| kod | 50 | 0.0 | 0.0 |
| negatif_dogal | 180 | 100.0 | 98.9 |
| negatif_es | 200 | 100.0 | 30.0 |
| negatif_kalip | 220 | 100.0 | 30.9 |
| negatif_yazili | 160 | 100.0 | 93.1 |
| olcu | 160 | 0.0 | 64.4 |
| ondalik | 60 | 0.0 | 93.3 |
| para | 140 | 0.0 | 87.9 |
| saat | 130 | 0.0 | 33.1 |
| sira | 70 | 0.0 | 75.7 |
| skor | 50 | 0.0 | 0.0 |
| tarih | 120 | 0.0 | 4.2 |
| telefon | 60 | 0.0 | 0.0 |
| yuzde | 100 | 0.0 | 97.0 |

### Hata örnekleri (kural; toplam 936 hata, ilk 25 gösterilir)

```text
[kod/kod-014]
GİRDİ: Müşteri numarası dört altı beş üç iki dokuz sekiz yedi dört.
ÇIKTI: Müşteri numarası 4 6 5 3 2 9 8 7 4.
HEDEF: Müşteri numarası 465329874.
```

```text
[negatif_es/negatif_es-040]
GİRDİ: evet onları kapıda karşıladım
ÇIKTI: evet 10'ları kapıda karşıladım
HEDEF: evet onları kapıda karşıladım
```

```text
[tarih/tarih-008]
GİRDİ: şirket bin dokuz yüz otuz bir yılında kuruldu
ÇIKTI: şirket 1.931 yılında kuruldu
HEDEF: şirket 1931 yılında kuruldu
```

```text
[sira/sira-006]
GİRDİ: On üçüncü yüzyılda yaşamış bir şair.
ÇIKTI: 13. yüzyılda yaşamış 1 şair.
HEDEF: 13. yüzyılda yaşamış bir şair.
```

```text
[tarih/tarih-001]
GİRDİ: nazlı on beş ekim bin dokuz yüz doksan üç tarihinde doğdu
ÇIKTI: nazlı 15 ekim 1.993 tarihinde doğdu
HEDEF: nazlı 15 Ekim 1993 tarihinde doğdu
```

```text
[negatif_kalip/negatif_kalip-008]
GİRDİ: baksana bir sürü iş birikti
ÇIKTI: baksana 1 sürü iş birikti
HEDEF: baksana bir sürü iş birikti
```

```text
[telefon/telefon-000]
GİRDİ: Beni sıfır beş yüz otuz dört sekiz yüz yetmiş beş seksen kırk numarasından arayabilirsin.
ÇIKTI: Beni 0 534 875 80 40 numarasından arayabilirsin.
HEDEF: Beni 0534 875 80 40 numarasından arayabilirsin.
```

```text
[sira/sira-006]
GİRDİ: On beşinci yüzyılda yaşamış bir şair.
ÇIKTI: 15. yüzyılda yaşamış 1 şair.
HEDEF: 15. yüzyılda yaşamış bir şair.
```

```text
[saat/saat-012]
GİRDİ: Yemek saat yirmi iki yirmide hazır olur.
ÇIKTI: Yemek saat 22 20'de hazır olur.
HEDEF: Yemek saat 22.20'de hazır olur.
```

```text
[olcu/olcu-031]
GİRDİ: Yoğurdu kırk iki derece santigratta mayalayın.
ÇIKTI: Yoğurdu 42 °C'ta mayalayın.
HEDEF: Yoğurdu 42 °C'de mayalayın.
```

```text
[negatif_es/negatif_es-047]
GİRDİ: kısacası ona sorarsan yarın gelir
ÇIKTI: kısacası 10'a sorarsan yarın gelir
HEDEF: kısacası ona sorarsan yarın gelir
```

```text
[negatif_kalip/negatif_kalip-059]
GİRDİ: Şubat kısa ama soğuk bir aydır, herkes biliyor.
ÇIKTI: Şubat kısa ama soğuk 1 aydır, herkes biliyor.
HEDEF: Şubat kısa ama soğuk bir aydır, herkes biliyor.
```

```text
[aralik/aralik-026]
GİRDİ: koliyi yedi dokuz günde teslim ederiz
ÇIKTI: koliyi 7 9 günde teslim ederiz
HEDEF: koliyi 7-9 günde teslim ederiz
```

```text
[olcu/olcu-021]
GİRDİ: dokuz yüz yetmiş beş gramlık bir paket zeytin aldık
ÇIKTI: 975 g'lık 1 paket zeytin aldık
HEDEF: 975 g'lık bir paket zeytin aldık
```

```text
[olcu/olcu-021]
GİRDİ: otuz altı kilogramlık bir paket un aldık
ÇIKTI: 36 kg'lık 1 paket un aldık
HEDEF: 36 kg'lık bir paket un aldık
```

```text
[olcu/olcu-031]
GİRDİ: Yoğurdu on dokuz derece santigratta mayalayın.
ÇIKTI: Yoğurdu 19 °C'ta mayalayın.
HEDEF: Yoğurdu 19 °C'de mayalayın.
```

```text
[saat/saat-012]
GİRDİ: yemek saat on bir otuzda hazır olur
ÇIKTI: yemek saat 11 30'da hazır olur
HEDEF: yemek saat 11.30'da hazır olur
```

```text
[kod/kod-003]
GİRDİ: Posta kodu dört sıfır dört yedi iki.
ÇIKTI: Posta kodu 4 0 4 7 2.
HEDEF: Posta kodu 40472.
```

```text
[skor/skor-017]
GİRDİ: Maçı üç sıfırla kazandık.
ÇIKTI: Maçı 3 0'la kazandık.
HEDEF: Maçı 3-0'la kazandık.
```

```text
[negatif_kalip/negatif_kalip-002]
GİRDİ: şunu söyleyeyim bir an durup düşündü
ÇIKTI: şunu söyleyeyim 1 an durup düşündü
HEDEF: şunu söyleyeyim bir an durup düşündü
```

```text
[olcu/olcu-021]
GİRDİ: Otuz dokuz buçuk kilogramlık bir paket biber aldık.
ÇIKTI: 39,5 kg'lık 1 paket biber aldık.
HEDEF: 39,5 kg'lık bir paket biber aldık.
```

```text
[negatif_es/negatif_es-019]
GİRDİ: yüzü gülüyordu ama gözleri yorgundu ama neyse
ÇIKTI: 100'ü gülüyordu ama gözleri yorgundu ama neyse
HEDEF: yüzü gülüyordu ama gözleri yorgundu ama neyse
```

```text
[negatif_kalip/negatif_kalip-008]
GİRDİ: gerçekten bir sürü iş birikti
ÇIKTI: gerçekten 1 sürü iş birikti
HEDEF: gerçekten bir sürü iş birikti
```

```text
[saat/saat-026]
GİRDİ: akşam altı yirmiden sonra trafik azalıyor
ÇIKTI: akşam 6 20'den sonra trafik azalıyor
HEDEF: akşam 6.20'den sonra trafik azalıyor
```

```text
[buyuk/buyuk-023]
GİRDİ: Kampanyaya yirmi üç milyon üç yüz elli bir bin katılımcı destek verdi.
ÇIKTI: Kampanyaya 23 1.000.351 1.000 katılımcı destek verdi.
HEDEF: Kampanyaya 23.351.000 katılımcı destek verdi.
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) |
|---|---:|---:|---:|
| aralik | 2 | 0.0 | 0.0 |
| buyuk | 3 | 0.0 | 33.3 |
| buyuk_harf | 4 | 25.0 | 25.0 |
| eksi | 1 | 0.0 | 100.0 |
| kardinal | 8 | 0.0 | 100.0 |
| karisik | 1 | 0.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 |
| negatif_es | 9 | 100.0 | 11.1 |
| negatif_kalip | 14 | 100.0 | 35.7 |
| negatif_politika | 1 | 100.0 | 0.0 |
| negatif_yazili | 3 | 100.0 | 100.0 |
| olcu | 10 | 0.0 | 80.0 |
| ondalik | 2 | 0.0 | 100.0 |
| para | 10 | 0.0 | 70.0 |
| saat | 9 | 0.0 | 55.6 |
| saat_zor | 2 | 0.0 | 50.0 |
| sira | 5 | 0.0 | 100.0 |
| skor | 2 | 0.0 | 0.0 |
| tarih | 5 | 0.0 | 0.0 |
| telefon | 3 | 0.0 | 0.0 |
| yuzde | 4 | 0.0 | 100.0 |

### Hata örnekleri (kural; toplam 47 hata, ilk 25 gösterilir)

```text
[para/elle]
GİRDİ: bu ay kiraya on sekiz bin beş yüz lira verdim
ÇIKTI: bu ay kiraya 18 1.500 TL verdim
HEDEF: bu ay kiraya 18.500 TL verdim
```

```text
[para/elle]
GİRDİ: elli kuruşa simit mi kaldı
ÇIKTI: 50 kuruş'a simit mi kaldı
HEDEF: 50 kuruşa simit mi kaldı
```

```text
[para/elle]
GİRDİ: dolar kırk iki lira on beş kuruşa çıktı
ÇIKTI: dolar 42,15 TL'e çıktı
HEDEF: dolar 42,15 TL'ye çıktı
```

```text
[olcu/elle]
GİRDİ: otuz beş metrekarelik bir oda
ÇIKTI: 35 m²'lik 1 oda
HEDEF: 35 m²'lik bir oda
```

```text
[olcu/elle]
GİRDİ: su otuz derece santigratta ısınır
ÇIKTI: su 30 °C'ta ısınır
HEDEF: su 30 °C'de ısınır
```

```text
[saat/elle]
GİRDİ: saat on dört otuzda görüşelim
ÇIKTI: saat 14 30'da görüşelim
HEDEF: saat 14.30'da görüşelim
```

```text
[saat/elle]
GİRDİ: saat üç buçukta buluşalım
ÇIKTI: saat 3,5'ta buluşalım
HEDEF: saat 3.30'da buluşalım
```

```text
[saat/elle]
GİRDİ: tren saat on yedi kırk beşte kalkıyor
ÇIKTI: tren saat 17 45'te kalkıyor
HEDEF: tren saat 17.45'te kalkıyor
```

```text
[saat/elle]
GİRDİ: saat on dokuz sıfır beşte çıktı
ÇIKTI: saat 19 0 5'te çıktı
HEDEF: saat 19.05'te çıktı
```

```text
[saat_zor/elle]
GİRDİ: gece on bir buçukta yatarım
ÇIKTI: gece 11,5'ta yatarım
HEDEF: gece 11.30'da yatarım
```

```text
[tarih/elle]
GİRDİ: sekiz kasım iki bin yirmi altıda doğdu
ÇIKTI: 8 kasım 2.026'da doğdu
HEDEF: 8 Kasım 2026'da doğdu
```

```text
[tarih/elle]
GİRDİ: yirmi dokuz ekim bin dokuz yüz yirmi üçte cumhuriyet ilan edildi
ÇIKTI: 29 ekim 1.923'te cumhuriyet ilan edildi
HEDEF: 29 Ekim 1923'te cumhuriyet ilan edildi
```

```text
[tarih/elle]
GİRDİ: on beş kasımda saat on dokuzda konser var
ÇIKTI: 15 kasımda saat 19'da konser var
HEDEF: 15 Kasım'da saat 19'da konser var
```

```text
[tarih/elle]
GİRDİ: bin dokuz yüz doksanlarda çok popülerdi
ÇIKTI: 1.990'larda çok popülerdi
HEDEF: 1990'larda çok popülerdi
```

```text
[tarih/elle]
GİRDİ: iki bin yirmi beşteki seçimler
ÇIKTI: 2.025'teki seçimler
HEDEF: 2025'teki seçimler
```

```text
[telefon/elle]
GİRDİ: numaram sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi
ÇIKTI: numaram 0 532 123 45 67
HEDEF: numaram 0532 123 45 67
```

```text
[telefon/elle]
GİRDİ: sıfır iki yüz on iki dört yüz elli altı yetmiş sekiz doksan
ÇIKTI: 0 212 456 78 90
HEDEF: 0212 456 78 90
```

```text
[telefon/elle]
GİRDİ: beni sıfır beş üç iki bir iki üç dört beş altı yedi numaradan ara
ÇIKTI: beni 0 5 3 2 1 2 3 4 5 6 7 numaradan ara
HEDEF: beni 0532 123 45 67 numaradan ara
```

```text
[kod/elle]
GİRDİ: doğrulama kodu sıfır sekiz dört iki
ÇIKTI: doğrulama kodu 0 8 4 2
HEDEF: doğrulama kodu 0842
```

```text
[kod/elle]
GİRDİ: şifre dört beş bir dokuz
ÇIKTI: şifre 4 5 1 9
HEDEF: şifre 4519
```

```text
[skor/elle]
GİRDİ: maç iki bir bitti
ÇIKTI: maç 2 1 bitti
HEDEF: maç 2-1 bitti
```

```text
[skor/elle]
GİRDİ: galatasaray maçı üç sıfır kazandı
ÇIKTI: galatasaray maçı 3 0 kazandı
HEDEF: galatasaray maçı 3-0 kazandı
```

```text
[aralik/elle]
GİRDİ: beş altı kişi gelecek
ÇIKTI: 5 6 kişi gelecek
HEDEF: 5-6 kişi gelecek
```

```text
[aralik/elle]
GİRDİ: on on beş dakika sonra çıkarım
ÇIKTI: 10 15 dakika sonra çıkarım
HEDEF: 10-15 dakika sonra çıkarım
```

```text
[buyuk/elle]
GİRDİ: şirket iki buçuk milyon lira zarar etti
ÇIKTI: şirket 2,5 1.000.000 TL zarar etti
HEDEF: şirket 2,5 milyon TL zarar etti
```
