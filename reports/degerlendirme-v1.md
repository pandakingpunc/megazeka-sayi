# Megazeka-Sayı değerlendirmesi — v1

Kontrol noktası: `best` · süre: 82 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 94.1 | 0.5 | 1.3 | 97.6 | 2.8 (776) |
| Model + koruma | 2000 | 93.8 | 1.3 | 2.4 | 95.0 | 2.1 (776) |

Koruma 39 örnekte en az bir bölgeyi geri aldı.

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
| saat | 130 | 0.0 | 33.1 | 98.5 | 85.4 |
| sira | 70 | 0.0 | 75.7 | 100.0 | 100.0 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 99.2 | 99.2 |
| telefon | 60 | 0.0 | 0.0 | 86.7 | 83.3 |
| yuzde | 100 | 0.0 | 97.0 | 99.0 | 96.0 |

### Hata örnekleri (model_korumali; toplam 123 hata, ilk 25 gösterilir)

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
[saat/saat-021]
GİRDİ: kapı saat on dokuz ondan sonra kapanıyor
ÇIKTI: kapı saat on dokuz ondan sonra kapanıyor
HAM  : kapı saat 19.10'dan sonra kapanıyor
HEDEF: kapı saat 19.10'dan sonra kapanıyor
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
[saat/saat-023]
GİRDİ: sabah on onda işe çıktık
ÇIKTI: sabah on onda işe çıktık
HAM  : sabah 10.10'da işe çıktık
HEDEF: sabah 10.10'da işe çıktık
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
[saat/saat-012]
GİRDİ: yemek saat on beş onda hazır olur
ÇIKTI: yemek saat on beş onda hazır olur
HAM  : yemek saat 15.10'da hazır olur
HEDEF: yemek saat 15.10'da hazır olur
```

```text
[saat/saat-021]
GİRDİ: Kapı saat sekiz ondan sonra kapanıyor.
ÇIKTI: Kapı saat sekiz ondan sonra kapanıyor.
HAM  : Kapı saat 8.10'dan sonra kapanıyor.
HEDEF: Kapı saat 8.10'dan sonra kapanıyor.
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
[saat/saat-023]
GİRDİ: sabah altı onda işe çıktık
ÇIKTI: sabah altı onda işe çıktık
HAM  : sabah 6.10'da işe çıktık
HEDEF: sabah 6.10'da işe çıktık
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
[saat/saat-021]
GİRDİ: Kapı saat ondan sonra kapanıyor.
ÇIKTI: Kapı saat ondan sonra kapanıyor.
HAM  : Kapı saat 10'dan sonra kapanıyor.
HEDEF: Kapı saat 10'dan sonra kapanıyor.
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

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 93.0 | 1.3 | 2.1 | 100.0 | 21.4 (28) |
| Model + koruma | 100 | 93.0 | 1.3 | 2.1 | 98.9 | 14.3 (28) |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 3 | 0.0 | 33.3 | 100.0 | 100.0 |
| buyuk_harf | 4 | 25.0 | 25.0 | 100.0 | 75.0 |
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
| saat | 9 | 0.0 | 55.6 | 100.0 | 88.9 |
| saat_zor | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| sira | 5 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 5 | 0.0 | 0.0 | 100.0 | 80.0 |
| telefon | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 4 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 7 hata, ilk 7 gösterilir)

```text
[saat/elle]
GİRDİ: saat ona kadar çalışıyoruz
ÇIKTI: saat ona kadar çalışıyoruz
HAM  : saat 10'a kadar çalışıyoruz
HEDEF: saat 10'a kadar çalışıyoruz
```

```text
[tarih/elle]
GİRDİ: on beş kasımda saat on dokuzda konser var
ÇIKTI: 15 kasımda saat 19'da konser var
HAM  : 15 Kasım'da saat 19'da konser var
HEDEF: 15 Kasım'da saat 19'da konser var
```

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

```text
[buyuk_harf/elle]
GİRDİ: Yirmi dokuz ekimde bayram var.
ÇIKTI: 29 ekimde bayram var.
HAM  : 29 Ekim'de bayram var.
HEDEF: 29 Ekim'de bayram var.
```
