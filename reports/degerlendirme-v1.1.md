# Megazeka-Sayı değerlendirmesi — v1.1

Kontrol noktası: `best` · süre: 173 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 94.2 | 0.5 | 1.3 | 97.2 | 4.6 (802) |
| Model + koruma | 2000 | 93.8 | 1.4 | 2.4 | 94.1 | 2.1 (802) |

Koruma 61 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 91.8 | 91.8 |
| buyuk | 40 | 0.0 | 0.0 | 75.0 | 95.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 98.9 | 93.8 |
| karisik | 49 | 0.0 | 77.6 | 73.5 | 73.5 |
| kod | 40 | 0.0 | 0.0 | 92.5 | 92.5 |
| negatif_dogal | 146 | 100.0 | 99.3 | 99.3 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 96.2 | 98.7 |
| negatif_kalip | 283 | 100.0 | 30.0 | 91.2 | 95.8 |
| negatif_yazili | 130 | 100.0 | 95.4 | 100.0 | 100.0 |
| olcu | 130 | 0.0 | 92.3 | 78.5 | 78.5 |
| ondalik | 130 | 0.0 | 91.5 | 100.0 | 87.7 |
| para | 129 | 0.0 | 88.4 | 95.3 | 95.3 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 40 | 0.0 | 0.0 | 90.0 | 90.0 |
| tarih | 97 | 0.0 | 10.3 | 100.0 | 96.9 |
| telefon | 49 | 0.0 | 0.0 | 75.5 | 71.4 |
| yuzde | 89 | 0.0 | 98.9 | 100.0 | 95.5 |

### Hata örnekleri (model_korumali; toplam 123 hata, ilk 25 gösterilir)

```text
[negatif_es/negatif_es-041]
GİRDİ: annem söyledi bu yüzden toplantıya gidemedik
ÇIKTI: annem söyledi bu %100'den toplantıya gidemedik
HEDEF: annem söyledi bu yüzden toplantıya gidemedik
```

```text
[para/para-011]
GİRDİ: cüzdanımda sadece yetmiş beş kuruş kaldı
ÇIKTI: cüzdanımda sadece yetmiş beş kuruş kaldı
HAM  : cüzdanımda 85 kuruş kaldı
HEDEF: cüzdanımda sadece 75 kuruş kaldı
```

```text
[buyuk/buyuk-006]
GİRDİ: stadyumun yapımı yetmiş sekiz milyon on bin lira tuttu
ÇIKTI: stadyumun yapımı 78.100 TL tuttu
HEDEF: stadyumun yapımı 78.010.000 TL tuttu
```

```text
[olcu/olcu-027]
GİRDİ: Yüklenecek dosya on altı gigabayttan büyük olmamalı.
ÇIKTI: Yüklenecek dosya 16 GB'dan büyük olmamalı.
HEDEF: Yüklenecek dosya 16 GB'tan büyük olmamalı.
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
HAM  : 900'ün bir fazlasını bulmamız gerekiyor
HEDEF: 900'ün bir fazlasını bulmamız gerekiyor
```

```text
[olcu/olcu-027]
GİRDİ: yüklenecek dosya dört gigabayttan büyük olmamalı
ÇIKTI: yüklenecek dosya 4 GB'dan büyük olmamalı
HEDEF: yüklenecek dosya 4 GB'tan büyük olmamalı
```

```text
[para/para-009]
GİRDİ: hesabınızdan dokuz yüz sekiz bin yirmi iki türk lirası doksan kuruş tahsil edilmiştir
ÇIKTI: hesabınızdan 908.202,90 TL tahsil edilmiştir
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
[negatif_kalip/negatif_kalip-037]
GİRDİ: sanırım esra sınavda üçüncü oldu
ÇIKTI: sanırım esra sınavda 3. oldu
HEDEF: sanırım esra sınavda üçüncü oldu
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş yüz otuz beş altı yüz on yetmiş beş kırk yedi diye kaydettim
ÇIKTI: numarayı 0535 615 75 47 diye kaydettim
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
[karisik/karisik-026]
GİRDİ: araç yüz altmış bir kilovat güçte fiyatı kırk türk lirası
ÇIKTI: araç yüz altmış bir kilovat güçte fiyatı 40 TL
HAM  : araç 161 kW'te fiyatı 40 TL
HEDEF: araç 161 kW güçte fiyatı 40 TL
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
ÇIKTI: mesaj gelirse 0559 999 90 03 numarasına yönlendir
HEDEF: mesaj gelirse 0550 909 90 03 numarasına yönlendir
```

```text
[olcu/olcu-027]
GİRDİ: yüklenecek dosya on altı gigabayttan büyük olmamalı
ÇIKTI: yüklenecek dosya 16 GB'dan büyük olmamalı
HEDEF: yüklenecek dosya 16 GB'tan büyük olmamalı
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş beş sıfır sıfır sekiz altı beş beş beş sekiz diye kaydettim
ÇIKTI: numarayı 0550 008 55 58 diye kaydettim
HEDEF: numarayı 0550 086 55 58 diye kaydettim
```

```text
[karisik/karisik-020]
GİRDİ: telefon sıfır beş yüz kırk üç dokuz sıfır bir yetmiş sekiz sıfır altı posta kodu bir dört bir iki sekiz
ÇIKTI: telefon 0543 901 78 06 posta kodu 1412 88
HEDEF: telefon 0543 901 78 06 posta kodu 14128
```

```text
[aralik/aralik-026]
GİRDİ: Koliyi altmış yetmiş beş günde teslim ederiz.
ÇIKTI: Koliyi 65 günde teslim ederiz.
HEDEF: Koliyi 60-75 günde teslim ederiz.
```

```text
[kardinal/kardinal-046]
GİRDİ: kırkın bir fazlasını bulmamız gerekiyor
ÇIKTI: kırkın bir fazlasını bulmamız gerekiyor
HAM  : 40'ın bir fazlasını bulmamız gerekiyor
HEDEF: 40'ın bir fazlasını bulmamız gerekiyor
```

```text
[ondalik/ondalik-018]
GİRDİ: Puanı yedi buçuğa yükseldi.
ÇIKTI: Puanı yedi buçuğa yükseldi.
HAM  : Puanı 7,5'e yükseldi.
HEDEF: Puanı 7,5'e yükseldi.
```

```text
[yuzde/yuzde-032]
GİRDİ: Mevcudun yüzde altmış biri sınavı geçti.
ÇIKTI: Mevcudun yüzde altmış biri sınavı geçti.
HAM  : Mevcudun %61'i sınavı geçti.
HEDEF: Mevcudun %61'i sınavı geçti.
```

```text
[ondalik/ondalik-039]
GİRDİ: Değerin yirmi dokuz virgül biri sabit tutuldu.
ÇIKTI: Değerin yirmi dokuz virgül biri sabit tutuldu.
HAM  : Değerin 29,1'i sabit tutuldu.
HEDEF: Değerin 29,1'i sabit tutuldu.
```

```text
[olcu/olcu-027]
GİRDİ: yüklenecek dosya yetmiş altı gigabayttan büyük olmamalı
ÇIKTI: yüklenecek dosya 76 GB'dan büyük olmamalı
HEDEF: yüklenecek dosya 76 GB'tan büyük olmamalı
```

```text
[olcu/olcu-027]
GİRDİ: yüklenecek dosya yedi yüz otuz üç megabayttan büyük olmamalı
ÇIKTI: yüklenecek dosya 733 MB'den büyük olmamalı
HEDEF: yüklenecek dosya 733 MB'tan büyük olmamalı
```

## Küme: test_v1_donmus (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 96.8 | 0.2 | 0.7 | 97.2 | 1.7 (776) |
| Model + koruma | 2000 | 96.8 | 0.7 | 1.2 | 95.6 | 0.8 (776) |

Koruma 25 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 90.0 | 90.0 |
| buyuk | 50 | 0.0 | 2.0 | 78.0 | 92.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 95.0 | 91.0 |
| karisik | 60 | 0.0 | 53.3 | 93.3 | 93.3 |
| kod | 50 | 0.0 | 0.0 | 88.0 | 88.0 |
| negatif_dogal | 180 | 100.0 | 98.9 | 99.4 | 100.0 |
| negatif_es | 200 | 100.0 | 30.0 | 97.5 | 100.0 |
| negatif_kalip | 220 | 100.0 | 30.9 | 99.5 | 99.5 |
| negatif_yazili | 160 | 100.0 | 93.1 | 99.4 | 100.0 |
| olcu | 160 | 0.0 | 64.4 | 97.5 | 97.5 |
| ondalik | 60 | 0.0 | 93.3 | 100.0 | 98.3 |
| para | 140 | 0.0 | 87.9 | 93.6 | 93.6 |
| saat | 130 | 0.0 | 33.1 | 100.0 | 97.7 |
| sira | 70 | 0.0 | 75.7 | 98.6 | 98.6 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 100.0 | 100.0 |
| telefon | 60 | 0.0 | 0.0 | 81.7 | 78.3 |
| yuzde | 100 | 0.0 | 97.0 | 100.0 | 97.0 |

### Hata örnekleri (model_korumali; toplam 64 hata, ilk 25 gösterilir)

```text
[kod/kod-014]
GİRDİ: Müşteri numarası dört altı beş üç iki dokuz sekiz yedi dört.
ÇIKTI: Müşteri numarası 4653298874.
HEDEF: Müşteri numarası 465329874.
```

```text
[telefon/telefon-000]
GİRDİ: Beni sıfır beş yüz otuz dört sekiz yüz yetmiş beş seksen kırk numarasından arayabilirsin.
ÇIKTI: Beni 0534 875 85 80 numarasından arayabilirsin.
HEDEF: Beni 0534 875 80 40 numarasından arayabilirsin.
```

```text
[aralik/aralik-011]
GİRDİ: iki yüz iki yüz elli yıl önce buraya taşındık
ÇIKTI: 2025 yıl önce buraya taşındık
HEDEF: 200-250 yıl önce buraya taşındık
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram sıfır beş yüz kırk sekiz yüz elli dört doksan on beş.
ÇIKTI: Telefon numaram 0548 854 91 15.
HEDEF: Telefon numaram 0548 154 90 15.
```

```text
[kod/kod-004]
GİRDİ: Sipariş numaranız yedi iki bir dokuz bir dört dokuz bir.
ÇIKTI: Sipariş numaranız 721914991.
HEDEF: Sipariş numaranız 72191491.
```

```text
[buyuk/buyuk-023]
GİRDİ: Kampanyaya on iki milyon altmış iki bin turist destek verdi.
ÇIKTI: Kampanyaya 12.62.000 turist destek verdi.
HEDEF: Kampanyaya 12.062.000 turist destek verdi.
```

```text
[telefon/telefon-000]
GİRDİ: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
ÇIKTI: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
HAM  : Beni +90 548 333 54 46 numarasından arayabilirsin.
HEDEF: Beni +90 548 335 44 06 numarasından arayabilirsin.
```

```text
[aralik/aralik-002]
GİRDİ: bu iş altmış altmış beş gün alır
ÇIKTI: bu iş 65-65 gün alır
HEDEF: bu iş 60-65 gün alır
```

```text
[karisik/karisik-000]
GİRDİ: pazardan yüz gram ekmek aldım hesap sekiz yüz doksan bir bin altı yüz elli dokuz lira elli beş kuruş tuttu
ÇIKTI: pazardan 190 g ekmek aldım hesap 891.659,55 TL tuttu
HEDEF: pazardan 100 g ekmek aldım hesap 891.659,55 TL tuttu
```

```text
[olcu/olcu-015]
GİRDİ: Bilgisayara bin doksan megabayt bellek ekledim.
ÇIKTI: Bilgisayara 1.90 MB bellek ekledim.
HEDEF: Bilgisayara 1.090 MB bellek ekledim.
```

```text
[karisik/karisik-027]
GİRDİ: yolcu sayısı yirmi beş bin üç gecikme otuz kırk dakika
ÇIKTI: yolcu sayısı 25.3 gecikme 30-40 dakika
HEDEF: yolcu sayısı 25.003 gecikme 30-40 dakika
```

```text
[kardinal/kardinal-015]
GİRDİ: masada sekiz sandalye eksik
ÇIKTI: masada 8 sandalye eksik
HEDEF: masada sekiz sandalye eksik
```

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram 0322 734 94 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[kod/kod-014]
GİRDİ: Müşteri numarası sıfır dokuz üç dört dokuz yedi üç yedi.
ÇIKTI: Müşteri numarası 093499737.
HEDEF: Müşteri numarası 09349737.
```

```text
[aralik/aralik-026]
GİRDİ: Koliyi altmış yetmiş beş günde teslim ederiz.
ÇIKTI: Koliyi 65 günde teslim ederiz.
HEDEF: Koliyi 60-75 günde teslim ederiz.
```

```text
[buyuk/buyuk-023]
GİRDİ: kampanyaya elli altı milyon kırk üç bin katılımcı destek verdi
ÇIKTI: kampanyaya 56.43.000 katılımcı destek verdi
HEDEF: kampanyaya 56.043.000 katılımcı destek verdi
```

```text
[yuzde/yuzde-019]
GİRDİ: kredi faizi yüzde seksen yedi buçuğa düştü
ÇIKTI: kredi faizi yüzde seksen yedi buçuğa düştü
HAM  : kredi faizi %87,5'e düştü
HEDEF: kredi faizi %87,5'e düştü
```

```text
[karisik/karisik-027]
GİRDİ: yolcu sayısı altmış beş bin yetmiş bir gecikme kırk elli dakika
ÇIKTI: yolcu sayısı 65.71 gecikme 40-50 dakika
HEDEF: yolcu sayısı 65.071 gecikme 40-50 dakika
```

```text
[buyuk/buyuk-023]
GİRDİ: kampanyaya üç milyon sekiz yüz kırk dokuz bin doksan bir turist destek verdi
ÇIKTI: kampanyaya 3.849.91 turist destek verdi
HEDEF: kampanyaya 3.849.091 turist destek verdi
```

```text
[ondalik/ondalik-017]
GİRDİ: Ortalamamı yirmi dokuz buçuğa çıkardım.
ÇIKTI: Ortalamamı yirmi dokuz buçuğa çıkardım.
HAM  : Ortalamamı 29,5'e çıkardım.
HEDEF: Ortalamamı 29,5'e çıkardım.
```

```text
[para/para-028]
GİRDİ: dokuz yüz elli iki bin yirmi sekiz lirayla bu ayı çıkaramayız
ÇIKTI: 952.228 TL'yle bu ayı çıkaramayız
HEDEF: 952.028 TL'yle bu ayı çıkaramayız
```

```text
[saat/saat-026]
GİRDİ: akşam ondan sonra trafik azalıyor
ÇIKTI: akşam ondan sonra trafik azalıyor
HAM  : akşam 10'dan sonra trafik azalıyor
HEDEF: akşam 10'dan sonra trafik azalıyor
```

```text
[telefon/telefon-007]
GİRDİ: lütfen sıfır beş yüz otuz beş altı yüz on yetmiş beş kırk yedi numarasına mesaj gönderin
ÇIKTI: lütfen 0535 610 15 47 numarasına mesaj gönderin
HEDEF: lütfen 0535 610 75 47 numarasına mesaj gönderin
```

```text
[kardinal/kardinal-015]
GİRDİ: Masada altı sandalye eksik.
ÇIKTI: Masada 6 sandalye eksik.
HEDEF: Masada altı sandalye eksik.
```

```text
[sira/sira-021]
GİRDİ: Birinci sınıf öğretmeni toplantı istedi.
ÇIKTI: Birinci sınıf öğretmeni toplantı istedi.
HEDEF: 1. sınıf öğretmeni toplantı istedi.
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 98.0 | 0.4 | 0.5 | 100.0 | 7.1 (28) |
| Model + koruma | 100 | 99.0 | 0.2 | 0.3 | 100.0 | 3.6 (28) |

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
| negatif_es | 9 | 100.0 | 11.1 | 88.9 | 88.9 |
| negatif_kalip | 14 | 100.0 | 35.7 | 92.9 | 100.0 |
| negatif_politika | 1 | 100.0 | 0.0 | 100.0 | 100.0 |
| negatif_yazili | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 10 | 0.0 | 80.0 | 100.0 | 100.0 |
| ondalik | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 10 | 0.0 | 70.0 | 100.0 | 100.0 |
| saat | 9 | 0.0 | 55.6 | 100.0 | 100.0 |
| saat_zor | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| sira | 5 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 4 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 1 hata, ilk 1 gösterilir)

```text
[negatif_es/elle]
GİRDİ: otobüse bin hemen
ÇIKTI: otobüse 1.000 hemen
HEDEF: otobüse bin hemen
```

## Küme: zorluk2_gizli (50 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 50 | 42.0 | 35.9 | 52.4 | 2.7 | 0.0 (21) |
| Kural tabanlı (saf) | 50 | 56.0 | 5.8 | 18.8 | 70.3 | 52.4 (21) |
| Model (korumasız) | 50 | 94.0 | 1.2 | 2.4 | 94.6 | 9.5 (21) |
| Model + koruma | 50 | 94.0 | 1.2 | 2.4 | 94.6 | 9.5 (21) |

Koruma 0 örnekte en az bir bölgeyi geri aldı.

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
| negatif_es | 8 | 100.0 | 50.0 | 87.5 | 87.5 |
| negatif_kalip | 10 | 100.0 | 50.0 | 90.0 | 90.0 |
| negatif_politika | 1 | 100.0 | 0.0 | 100.0 | 100.0 |
| negatif_yazili | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 3 | 0.0 | 100.0 | 66.7 | 66.7 |
| ondalik | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 4 | 0.0 | 75.0 | 100.0 | 100.0 |
| saat | 3 | 0.0 | 33.3 | 100.0 | 100.0 |
| sira | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 2 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 3 hata, ilk 3 gösterilir)

```text
[olcu/elle2]
GİRDİ: bebek üç kilo iki yüz gram doğdu
ÇIKTI: bebek 3,200 g doğdu
HEDEF: bebek 3 kg 200 g doğdu
```

```text
[negatif_es/elle2]
GİRDİ: taksiye bin de gel
ÇIKTI: taksiye 1.000 de gel
HEDEF: taksiye bin de gel
```

```text
[negatif_kalip/elle2]
GİRDİ: ikinci el telefonlar ucuzladı
ÇIKTI: 2. el telefonlar ucuzladı
HEDEF: ikinci el telefonlar ucuzladı
```
