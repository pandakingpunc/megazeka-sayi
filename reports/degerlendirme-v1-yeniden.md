# Megazeka-Sayı değerlendirmesi — v1-yeniden

Kontrol noktası: `v1` · süre: 156 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 92.2 | 0.9 | 1.8 | 97.1 | 8.1 (802) |
| Model + koruma | 2000 | 93.0 | 1.5 | 2.3 | 94.4 | 3.4 (802) |

Koruma 63 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 93.9 | 93.9 |
| buyuk | 40 | 0.0 | 0.0 | 65.0 | 90.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 93.8 | 90.4 |
| karisik | 49 | 0.0 | 77.6 | 91.8 | 91.8 |
| kod | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 146 | 100.0 | 99.3 | 100.0 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 88.1 | 95.3 |
| negatif_kalip | 283 | 100.0 | 30.0 | 88.3 | 94.7 |
| negatif_yazili | 130 | 100.0 | 95.4 | 97.7 | 100.0 |
| olcu | 130 | 0.0 | 92.3 | 99.2 | 99.2 |
| ondalik | 130 | 0.0 | 91.5 | 98.5 | 86.2 |
| para | 129 | 0.0 | 88.4 | 70.5 | 70.5 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 40 | 0.0 | 0.0 | 97.5 | 97.5 |
| tarih | 97 | 0.0 | 10.3 | 96.9 | 93.8 |
| telefon | 49 | 0.0 | 0.0 | 73.5 | 69.4 |
| yuzde | 89 | 0.0 | 98.9 | 97.8 | 93.3 |

### Hata örnekleri (model_korumali; toplam 139 hata, ilk 25 gösterilir)

```text
[para/para-011]
GİRDİ: cüzdanımda sadece yirmi kuruş kaldı
ÇIKTI: cüzdanımda sadece 20 TL kaldı
HEDEF: cüzdanımda sadece 20 kuruş kaldı
```

```text
[kardinal/kardinal-046]
GİRDİ: elli binin bir fazlasını bulmamız gerekiyor
ÇIKTI: 50.001 fazlasını bulmamız gerekiyor
HEDEF: 50.000'in bir fazlasını bulmamız gerekiyor
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece otuz kuruş kaldı
ÇIKTI: cüzdanımda sadece 30 TL kaldı
HEDEF: cüzdanımda sadece 30 kuruş kaldı
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece yetmiş beş kuruş kaldı
ÇIKTI: cüzdanımda sadece 75 TL kaldı
HEDEF: cüzdanımda sadece 75 kuruş kaldı
```

```text
[buyuk/buyuk-006]
GİRDİ: stadyumun yapımı yetmiş sekiz milyon on bin lira tuttu
ÇIKTI: stadyumun yapımı 78.110.000 TL tuttu
HEDEF: stadyumun yapımı 78.010.000 TL tuttu
```

```text
[aralik/aralik-026]
GİRDİ: koliyi on yirmi günde teslim ederiz
ÇIKTI: koliyi 12 günde teslim ederiz
HEDEF: koliyi 10-20 günde teslim ederiz
```

```text
[para/para-012]
GİRDİ: Bozuk para olarak elli kuruş verdim.
ÇIKTI: Bozuk para olarak 50 TL verdim.
HEDEF: Bozuk para olarak 50 kuruş verdim.
```

```text
[negatif_es/negatif_es-101]
GİRDİ: pazarda ikinci el motosiklet aradık
ÇIKTI: pazarda 2. el motosiklet aradık
HEDEF: pazarda ikinci el motosiklet aradık
```

```text
[kardinal/kardinal-046]
GİRDİ: dokuz yüzün bir fazlasını bulmamız gerekiyor
ÇIKTI: dokuz yüzün bir fazlasını bulmamız gerekiyor
HAM  : 901 fazlasını bulmamız gerekiyor
HEDEF: 900'ün bir fazlasını bulmamız gerekiyor
```

```text
[para/para-009]
GİRDİ: hesabınızdan dokuz yüz sekiz bin yirmi iki türk lirası doksan kuruş tahsil edilmiştir
ÇIKTI: hesabınızdan 98.222,90 TL tahsil edilmiştir
HEDEF: hesabınızdan 908.022,90 TL tahsil edilmiştir
```

```text
[yuzde/yuzde-029]
GİRDİ: partinin oyu yüzde yüzü buldu
ÇIKTI: partinin oyu yüzde yüzü buldu
HAM  : partinin oyu %100'ü buldu
HEDEF: partinin oyu %100'ü buldu
```

```text
[para/para-041]
GİRDİ: Eskiden bir poşet elli kuruşa satılırdı.
ÇIKTI: Eskiden bir poşet 50 TL'ye satılırdı.
HEDEF: Eskiden bir poşet 50 kuruşa satılırdı.
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş yüz otuz beş altı yüz on yetmiş beş kırk yedi diye kaydettim
ÇIKTI: numarayı 0535 611 75 47 diye kaydettim
HEDEF: numarayı 0535 610 75 47 diye kaydettim
```

```text
[tarih/tarih-011]
GİRDİ: iki bin birin ilk günlerinde işe başladım
ÇIKTI: iki bin birin ilk günlerinde işe başladım
HAM  : 2001'in ilk günlerinde işe başladım
HEDEF: 2001'in ilk günlerinde işe başladım
```

```text
[ondalik/ondalik-020]
GİRDİ: Yirmi bir virgül birin üzerindeki notlar geçer sayılıyor.
ÇIKTI: Yirmi bir virgül birin üzerindeki notlar geçer sayılıyor.
HAM  : 21,1'in üzerindeki notlar geçer sayılıyor.
HEDEF: 21,1'in üzerindeki notlar geçer sayılıyor.
```

```text
[telefon/telefon-017]
GİRDİ: mesaj gelirse sıfır beş yüz elli dokuz yüz dokuz doksan sıfır üç numarasına yönlendir
ÇIKTI: mesaj gelirse 0559 199 90 03 numarasına yönlendir
HEDEF: mesaj gelirse 0550 909 90 03 numarasına yönlendir
```

```text
[negatif_es/negatif_es-101]
GİRDİ: pazarda ikinci el buzdolabı aradık
ÇIKTI: pazarda 2. el buzdolabı aradık
HEDEF: pazarda ikinci el buzdolabı aradık
```

```text
[karisik/karisik-026]
GİRDİ: araç iki yüz otuz volt güçte fiyatı yedi yüz seksen yedi lira
ÇIKTI: araç 230 W güçte fiyatı 787 TL
HEDEF: araç 230 V güçte fiyatı 787 TL
```

```text
[para/para-012]
GİRDİ: Bozuk para olarak yetmiş beş kuruş verdim.
ÇIKTI: Bozuk para olarak 75 TL verdim.
HEDEF: Bozuk para olarak 75 kuruş verdim.
```

```text
[negatif_es/negatif_es-101]
GİRDİ: neyse pazarda ikinci el mont aradık
ÇIKTI: neyse pazarda 2. el mont aradık
HEDEF: neyse pazarda ikinci el mont aradık
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş beş sıfır sıfır sekiz altı beş beş beş sekiz diye kaydettim
ÇIKTI: numarayı 0550 086 55 55 diye kaydettim
HEDEF: numarayı 0550 086 55 58 diye kaydettim
```

```text
[para/para-041]
GİRDİ: eskiden bir poşet otuz kuruşa satılırdı
ÇIKTI: eskiden 1 poşet 30 TL'ye satılırdı
HEDEF: eskiden bir poşet 30 kuruşa satılırdı
```

```text
[negatif_es/negatif_es-100]
GİRDİ: Onur ikinci el motosiklet alırken çok dikkatli davranır.
ÇIKTI: Onur 2. el motosiklet alırken çok dikkatli davranır.
HEDEF: Onur ikinci el motosiklet alırken çok dikkatli davranır.
```

```text
[negatif_es/negatif_es-100]
GİRDİ: Seda ikinci el telefon alırken çok dikkatli davranır.
ÇIKTI: Seda 2. el telefon alırken çok dikkatli davranır.
HEDEF: Seda ikinci el telefon alırken çok dikkatli davranır.
```

```text
[para/para-012]
GİRDİ: bozuk para olarak yirmi beş kuruş verdim
ÇIKTI: bozuk para olarak 25 TL verdim
HEDEF: bozuk para olarak 25 kuruş verdim
```

## Küme: test_v1_donmus (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 94.1 | 0.5 | 1.3 | 97.6 | 2.8 (776) |
| Model + koruma | 2000 | 94.5 | 1.2 | 2.1 | 95.8 | 2.1 (776) |

Koruma 25 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 50 | 0.0 | 2.0 | 68.0 | 98.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 91.0 | 88.0 |
| karisik | 60 | 0.0 | 53.3 | 83.3 | 83.3 |
| kod | 50 | 0.0 | 0.0 | 94.0 | 94.0 |
| negatif_dogal | 180 | 100.0 | 98.9 | 99.4 | 100.0 |
| negatif_es | 200 | 100.0 | 30.0 | 97.5 | 99.5 |
| negatif_kalip | 220 | 100.0 | 30.9 | 96.8 | 96.8 |
| negatif_yazili | 160 | 100.0 | 93.1 | 99.4 | 100.0 |
| olcu | 160 | 0.0 | 64.4 | 92.5 | 92.5 |
| ondalik | 60 | 0.0 | 93.3 | 98.3 | 96.7 |
| para | 140 | 0.0 | 87.9 | 70.7 | 70.7 |
| saat | 130 | 0.0 | 33.1 | 98.5 | 96.2 |
| sira | 70 | 0.0 | 75.7 | 100.0 | 100.0 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 99.2 | 99.2 |
| telefon | 60 | 0.0 | 0.0 | 86.7 | 83.3 |
| yuzde | 100 | 0.0 | 97.0 | 99.0 | 96.0 |

### Hata örnekleri (model_korumali; toplam 109 hata, ilk 25 gösterilir)

```text
[telefon/telefon-000]
GİRDİ: Beni sıfır beş yüz otuz dört sekiz yüz yetmiş beş seksen kırk numarasından arayabilirsin.
ÇIKTI: Beni 0534 875 80 80 numarasından arayabilirsin.
HEDEF: Beni 0534 875 80 40 numarasından arayabilirsin.
```

```text
[saat/saat-012]
GİRDİ: yemek saat on yirmide hazır olur
ÇIKTI: yemek saat 12'de hazır olur
HEDEF: yemek saat 10.20'de hazır olur
```

```text
[olcu/olcu-021]
GİRDİ: elli iki kiloluk bir paket tavuk aldık
ÇIKTI: 52 kg'luk bir paket tavuk aldık
HEDEF: 52 kg'lık bir paket tavuk aldık
```

```text
[para/para-028]
GİRDİ: İki bin lirayla bu ayı çıkaramayız.
ÇIKTI: 2.000 TL'yla bu ayı çıkaramayız.
HEDEF: 2.000 TL'yle bu ayı çıkaramayız.
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram sıfır beş yüz kırk sekiz yüz elli dört doksan on beş.
ÇIKTI: Telefon numaram 0548 854 91 15.
HEDEF: Telefon numaram 0548 154 90 15.
```

```text
[buyuk/buyuk-023]
GİRDİ: Kampanyaya on iki milyon altmış iki bin turist destek verdi.
ÇIKTI: Kampanyaya 12.622.000 turist destek verdi.
HEDEF: Kampanyaya 12.062.000 turist destek verdi.
```

```text
[negatif_kalip/negatif_kalip-025]
GİRDİ: Koşuda Ali ikinci geldi.
ÇIKTI: Koşuda Ali 2. geldi.
HEDEF: Koşuda Ali ikinci geldi.
```

```text
[telefon/telefon-000]
GİRDİ: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
ÇIKTI: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
HAM  : Beni +90 548 333 54 46 numarasından arayabilirsin.
HEDEF: Beni +90 548 335 44 06 numarasından arayabilirsin.
```

```text
[karisik/karisik-000]
GİRDİ: pazardan yüz gram ekmek aldım hesap sekiz yüz doksan bir bin altı yüz elli dokuz lira elli beş kuruş tuttu
ÇIKTI: pazardan yüz gram ekmek aldım hesap sekiz yüz doksan bir bin altı yüz elli dokuz lira elli beş kuruş tuttu
HAM  : pazardan 191.659,55 TL tuttu
HEDEF: pazardan 100 g ekmek aldım hesap 891.659,55 TL tuttu
```

```text
[karisik/karisik-027]
GİRDİ: yolcu sayısı yirmi beş bin üç gecikme otuz kırk dakika
ÇIKTI: yolcu sayısı 25.03 gecikme 30 dakika
HAM  : yolcu sayısı 25.03 Gecikme 30 dakika
HEDEF: yolcu sayısı 25.003 gecikme 30-40 dakika
```

```text
[kardinal/kardinal-029]
GİRDİ: yedi yaşındaki bir çocuk kazayı gördü
ÇIKTI: 7 yaşındaki bir çocuk kazayı gördü
HEDEF: yedi yaşındaki bir çocuk kazayı gördü
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece doksan kuruş kaldı
ÇIKTI: cüzdanımda sadece 90 TL kaldı
HEDEF: cüzdanımda sadece 90 kuruş kaldı
```

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram 0322 734 94 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[olcu/olcu-008]
GİRDİ: okulumuz evimize yüz dokuz virgül üç kilometre mesafede
ÇIKTI: okulumuz evimize 199,3 km mesafede
HEDEF: okulumuz evimize 109,3 km mesafede
```

```text
[para/para-011]
GİRDİ: Cüzdanımda sadece beş kuruş kaldı.
ÇIKTI: Cüzdanımda sadece 5 TL kaldı.
HEDEF: Cüzdanımda sadece 5 kuruş kaldı.
```

```text
[saat/saat-012]
GİRDİ: yemek saat on yirmi beşte hazır olur
ÇIKTI: yemek saat 12.25'te hazır olur
HEDEF: yemek saat 10.25'te hazır olur
```

```text
[yuzde/yuzde-019]
GİRDİ: kredi faizi yüzde seksen yedi buçuğa düştü
ÇIKTI: kredi faizi yüzde seksen yedi buçuğa düştü
HAM  : kredi faizi %87,5'e düştü
HEDEF: kredi faizi %87,5'e düştü
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece yirmi kuruş kaldı
ÇIKTI: cüzdanımda sadece 20 TL kaldı
HEDEF: cüzdanımda sadece 20 kuruş kaldı
```

```text
[para/para-028]
GİRDİ: bin beş yüz lirayla bu ayı çıkaramayız
ÇIKTI: 1.500 TL'yla bu ayı çıkaramayız
HEDEF: 1.500 TL'yle bu ayı çıkaramayız
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece beş kuruş kaldı
ÇIKTI: cüzdanımda sadece 5 TL kaldı
HEDEF: cüzdanımda sadece 5 kuruş kaldı
```

```text
[olcu/olcu-021]
GİRDİ: Otuz beş kiloluk bir paket soğan aldık.
ÇIKTI: 35 kg'luk bir paket soğan aldık.
HEDEF: 35 kg'lık bir paket soğan aldık.
```

```text
[karisik/karisik-027]
GİRDİ: yolcu sayısı altmış beş bin yetmiş bir gecikme kırk elli dakika
ÇIKTI: yolcu sayısı 65.71 gecikme 40-50 dakika
HAM  : yolcu sayısı 65.71 Gecikme 40-50 dakika
HEDEF: yolcu sayısı 65.071 gecikme 40-50 dakika
```

```text
[para/para-028]
GİRDİ: Yirmi bin lirayla bu ayı çıkaramayız.
ÇIKTI: 20.000 TL'yla bu ayı çıkaramayız.
HEDEF: 20.000 TL'yle bu ayı çıkaramayız.
```

```text
[olcu/olcu-021]
GİRDİ: altmış iki kiloluk bir paket salatalık aldık
ÇIKTI: 62 kg'luk bir paket salatalık aldık
HEDEF: 62 kg'lık bir paket salatalık aldık
```

```text
[olcu/olcu-021]
GİRDİ: Yetmiş kiloluk bir paket peynir aldık.
ÇIKTI: 70 kg'luk bir paket peynir aldık.
HEDEF: 70 kg'lık bir paket peynir aldık.
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 93.0 | 1.3 | 2.1 | 100.0 | 21.4 (28) |
| Model + koruma | 100 | 96.0 | 0.9 | 1.3 | 100.0 | 14.3 (28) |

Koruma 1 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 3 | 0.0 | 33.3 | 100.0 | 100.0 |
| buyuk_harf | 4 | 25.0 | 25.0 | 100.0 | 100.0 |
| eksi | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| kardinal | 8 | 0.0 | 100.0 | 100.0 | 100.0 |
| karisik | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 9 | 100.0 | 11.1 | 66.7 | 77.8 |
| negatif_kalip | 14 | 100.0 | 35.7 | 78.6 | 85.7 |
| negatif_politika | 1 | 100.0 | 0.0 | 100.0 | 100.0 |
| negatif_yazili | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 10 | 0.0 | 80.0 | 100.0 | 100.0 |
| ondalik | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 10 | 0.0 | 70.0 | 90.0 | 100.0 |
| saat | 9 | 0.0 | 55.6 | 100.0 | 100.0 |
| saat_zor | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| sira | 5 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 4 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 4 hata, ilk 4 gösterilir)

```text
[negatif_es/elle]
GİRDİ: otobüse bin hemen
ÇIKTI: otobüse 1.000 hemen
HEDEF: otobüse bin hemen
```

```text
[negatif_es/elle]
GİRDİ: pastanın üçte birini yedim
ÇIKTI: pastanın 3'te birini yedim
HEDEF: pastanın üçte birini yedim
```

```text
[negatif_kalip/elle]
GİRDİ: ikinci el araba aldım
ÇIKTI: 2. el araba aldım
HEDEF: ikinci el araba aldım
```

```text
[negatif_kalip/elle]
GİRDİ: bir iki gün içinde döneriz
ÇIKTI: 1-2 gün içinde döneriz
HEDEF: bir iki gün içinde döneriz
```

## Küme: zorluk2_gizli (50 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 50 | 42.0 | 35.9 | 52.4 | 2.7 | 0.0 (21) |
| Kural tabanlı (saf) | 50 | 56.0 | 5.8 | 18.8 | 70.3 | 52.4 (21) |
| Model (korumasız) | 50 | 80.0 | 2.9 | 6.2 | 91.9 | 33.3 (21) |
| Model + koruma | 50 | 84.0 | 2.4 | 5.3 | 91.9 | 28.6 (21) |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk_harf | 4 | 25.0 | 50.0 | 100.0 | 100.0 |
| eksi | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| kardinal | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| karisik | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| kod | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 8 | 100.0 | 50.0 | 75.0 | 87.5 |
| negatif_kalip | 10 | 100.0 | 50.0 | 60.0 | 60.0 |
| negatif_politika | 1 | 100.0 | 0.0 | 0.0 | 0.0 |
| negatif_yazili | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 3 | 0.0 | 100.0 | 66.7 | 66.7 |
| ondalik | 1 | 0.0 | 100.0 | 0.0 | 0.0 |
| para | 4 | 0.0 | 75.0 | 100.0 | 100.0 |
| saat | 3 | 0.0 | 33.3 | 100.0 | 100.0 |
| sira | 2 | 0.0 | 100.0 | 50.0 | 100.0 |
| skor | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 2 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 8 hata, ilk 8 gösterilir)

```text
[olcu/elle2]
GİRDİ: bebek üç kilo iki yüz gram doğdu
ÇIKTI: bebek 3,200 g doğdu
HEDEF: bebek 3 kg 200 g doğdu
```

```text
[ondalik/elle2]
GİRDİ: termometre otuz sekiz virgül altıyı gösteriyor
ÇIKTI: termometre 38,6'yi gösteriyor
HEDEF: termometre 38,6'yı gösteriyor
```

```text
[negatif_es/elle2]
GİRDİ: taksiye bin de gel
ÇIKTI: taksiye 1.000 de gel
HEDEF: taksiye bin de gel
```

```text
[negatif_kalip/elle2]
GİRDİ: üç aşağı beş yukarı aynı fiyat
ÇIKTI: 3-6 aşağı beş yukarı aynı fiyat
HEDEF: üç aşağı beş yukarı aynı fiyat
```

```text
[negatif_kalip/elle2]
GİRDİ: bir iki kelime etmek istiyorum
ÇIKTI: 1-2 kelime etmek istiyorum
HEDEF: bir iki kelime etmek istiyorum
```

```text
[negatif_kalip/elle2]
GİRDİ: ikinci el telefonlar ucuzladı
ÇIKTI: 2. el telefonlar ucuzladı
HEDEF: ikinci el telefonlar ucuzladı
```

```text
[negatif_kalip/elle2]
GİRDİ: bu iş beş para etmez
ÇIKTI: bu iş 5 para etmez
HEDEF: bu iş beş para etmez
```

```text
[negatif_politika/elle2]
GİRDİ: üç kedimiz var
ÇIKTI: 3 kedimiz var
HEDEF: üç kedimiz var
```
