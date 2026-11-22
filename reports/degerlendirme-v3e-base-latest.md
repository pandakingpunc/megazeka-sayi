# Megazeka-Sayı değerlendirmesi — v3e-base-latest

Kontrol noktası: `v3e-base-latest` · süre: 313 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 99.3 | 0.1 | 0.2 | 99.3 | 0.5 (802) |
| Model + koruma | 2000 | 99.3 | 0.5 | 0.7 | 98.3 | 0.4 (802) |

Koruma 8 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 99.4 | 98.9 |
| karisik | 49 | 0.0 | 77.6 | 89.8 | 89.8 |
| kod | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 146 | 100.0 | 99.3 | 100.0 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 100.0 | 100.0 |
| negatif_kalip | 283 | 100.0 | 30.0 | 98.9 | 98.9 |
| negatif_yazili | 130 | 100.0 | 95.4 | 99.2 | 100.0 |
| olcu | 130 | 0.0 | 92.3 | 100.0 | 100.0 |
| ondalik | 130 | 0.0 | 91.5 | 100.0 | 100.0 |
| para | 129 | 0.0 | 88.4 | 100.0 | 100.0 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 98.2 | 98.2 |
| skor | 40 | 0.0 | 0.0 | 97.5 | 97.5 |
| tarih | 97 | 0.0 | 10.3 | 100.0 | 100.0 |
| telefon | 49 | 0.0 | 0.0 | 95.9 | 95.9 |
| yuzde | 89 | 0.0 | 98.9 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 14 hata, ilk 14 gösterilir)

```text
[karisik/karisik-026]
GİRDİ: Araç iki volt güçte, fiyatı dört bin altı yüz üç Türk lirası.
ÇIKTI: Araç iki volt güçte, fiyatı 4.603 TL.
HAM  : Araç 2 V 3'te, fiyatı 4.603 TL.
HEDEF: Araç 2 V güçte, fiyatı 4.603 TL.
```

```text
[negatif_kalip/negatif_kalip-021]
GİRDİ: geçen hafta birden istasyonda ışıklar söndü
ÇIKTI: geçen hafta 1'den istasyonda ışıklar söndü
HEDEF: geçen hafta birden istasyonda ışıklar söndü
```

```text
[kardinal/kardinal-066]
GİRDİ: Hesaplama onda tıkandı.
ÇIKTI: Hesaplama onda tıkandı.
HAM  : Hesaplama 10'da tıkandı.
HEDEF: Hesaplama 10'da tıkandı.
```

```text
[skor/skor-024]
GİRDİ: Gençlerin maçı yüz yedi yüz bir bitti.
ÇIKTI: Gençlerin maçı 100-701 bitti.
HEDEF: Gençlerin maçı 107-101 bitti.
```

```text
[sira/sira-024]
GİRDİ: Bu festival birinci kez düzenleniyor.
ÇIKTI: Bu festival birinci kez düzenleniyor.
HEDEF: Bu festival 1. kez düzenleniyor.
```

```text
[kardinal/kardinal-042]
GİRDİ: şifreye onu ekle
ÇIKTI: şifreye onu ekle
HEDEF: şifreye 10'u ekle
```

```text
[karisik/karisik-026]
GİRDİ: Araç otuz dört volt güçte, fiyatı yedi yüz elli lira.
ÇIKTI: Araç otuz dört volt güçte, fiyatı 750 TL.
HAM  : Araç 34 V 3'te, fiyatı 750 TL.
HEDEF: Araç 34 V güçte, fiyatı 750 TL.
```

```text
[negatif_kalip/negatif_kalip-064]
GİRDİ: deniz ikide bir saatine bakıyor
ÇIKTI: deniz 2'de bir saatine bakıyor
HEDEF: deniz ikide bir saatine bakıyor
```

```text
[karisik/karisik-020]
GİRDİ: Telefon sıfır beş yüz kırk yedi yedi yüz altmış bir bir dokuz bir üç, posta kodu üç iki dört sıfır beş.
ÇIKTI: Telefon sıfır beş yüz kırk yedi yedi yüz altmış bir bir dokuz bir üç, posta kodu üç iki dört sıfır beş.
HAM  : Telefon 0547 761 19 13.
HEDEF: Telefon 0547 761 19 13, posta kodu 32405.
```

```text
[karisik/karisik-020]
GİRDİ: telefon sıfır beş yüz otuz üç yüz otuz dokuz seksen bir sıfır altı posta kodu altı üç beş altı altı
ÇIKTI: telefon 0530 339 81 06 posta kodu 63566
HEDEF: telefon 0533 139 81 06 posta kodu 63566
```

```text
[negatif_kalip/negatif_kalip-112]
GİRDİ: At dört nala koştu.
ÇIKTI: At 4 nala koştu.
HEDEF: At dört nala koştu.
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş yüz elli dört yüz bir elli sekiz yetmiş bir diye kaydettim
ÇIKTI: numarayı sıfır beş yüz elli dört yüz bir elli sekiz yetmiş bir diye kaydettim
HAM  : numarayı 0554 401 58 71 diye kaydettim
HEDEF: numarayı 0554 101 58 71 diye kaydettim
```

```text
[telefon/telefon-014]
GİRDİ: Numarayı sıfır beş yüz kırk altı yüz seksen üç on dört seksen beş diye kaydettim.
ÇIKTI: Numarayı sıfır beş yüz kırk altı yüz seksen üç on dört seksen beş diye kaydettim.
HAM  : Numarayı 0546 683 14 85 diye kaydettim.
HEDEF: Numarayı 0540 683 14 85 diye kaydettim.
```

```text
[karisik/karisik-020]
GİRDİ: Telefon artı doksan iki yüz yirmi dört beş yüz yedi doksan dört seksen üç, posta kodu beş sekiz üç altı iki.
ÇIKTI: Telefon artı doksan iki yüz yirmi dört beş yüz yedi doksan dört seksen üç, posta kodu beş sekiz üç altı iki.
HAM  : Telefon +90 224 507 94 83.
HEDEF: Telefon +90 224 507 94 83, posta kodu 58362.
```

## Küme: test_v2_yeni_kaynaklar (1400 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 1400 | 27.1 | 35.2 | 48.2 | 6.8 | 0.0 (379) |
| Kural tabanlı (saf) | 1400 | 42.3 | 9.2 | 22.8 | 58.0 | 52.0 (379) |
| Model (korumasız) | 1400 | 98.9 | 0.1 | 0.3 | 99.1 | 1.1 (379) |
| Model + koruma | 1400 | 98.9 | 0.6 | 0.8 | 98.7 | 0.8 (379) |

Koruma 8 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 41 | 0.0 | 0.0 | 100.0 | 100.0 |
| bilesik | 56 | 0.0 | 76.8 | 100.0 | 100.0 |
| bitisik | 107 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 9 | 0.0 | 33.3 | 100.0 | 100.0 |
| kardinal | 91 | 20.9 | 58.2 | 96.7 | 96.7 |
| karisik | 56 | 0.0 | 42.9 | 100.0 | 100.0 |
| kod | 44 | 0.0 | 0.0 | 93.2 | 93.2 |
| negatif_es | 100 | 100.0 | 61.0 | 100.0 | 100.0 |
| negatif_kalip | 232 | 100.0 | 42.2 | 99.6 | 100.0 |
| olcu | 138 | 0.0 | 58.7 | 97.8 | 97.8 |
| para | 55 | 0.0 | 69.1 | 100.0 | 100.0 |
| saat | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| saat_deyis | 89 | 0.0 | 100.0 | 98.9 | 98.9 |
| sira | 11 | 0.0 | 100.0 | 100.0 | 100.0 |
| tarih | 72 | 0.0 | 70.8 | 100.0 | 100.0 |
| telefon | 56 | 0.0 | 0.0 | 92.9 | 92.9 |
| yari | 232 | 12.1 | 12.5 | 99.6 | 99.6 |
| yuzde | 5 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 15 hata, ilk 15 gösterilir)

```text
[kod/v2a-kod-001]
GİRDİ: Kapı şifresi beş altı altı altı altı altı dört sekiz sekiz altı iki olarak değiştirildi.
ÇIKTI: Kapı şifresi beş altı altı altı altı altı dört sekiz sekiz altı iki olarak değiştirildi.
HAM  : Kapı şifresi 5666648862 olarak değiştirildi.
HEDEF: Kapı şifresi 56666648862 olarak değiştirildi.
```

```text
[kod/v2a-kod-016]
GİRDİ: Dosya numaranız beş beş sekiz sekiz sekiz sekiz olarak kaydedildi.
ÇIKTI: Dosya numaranız beş beş sekiz sekiz sekiz sekiz olarak kaydedildi.
HAM  : Dosya numaranız 5588888 olarak kaydedildi.
HEDEF: Dosya numaranız 558888 olarak kaydedildi.
```

```text
[telefon/v2a-tel-006]
GİRDİ: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
ÇIKTI: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
HAM  : servisin hattı 0552 607 99 84
HEDEF: servisin hattı 0552 600 79 84
```

```text
[telefon/v2a-tel-018]
GİRDİ: resepsiyon sıfır beş beş sekiz dört yüz altı yedi altı dört numarasına bağlı
ÇIKTI: resepsiyon sıfır beş beş sekiz dört yüz altı yedi altı dört numarasına bağlı
HAM  : resepsiyon 0558 406 76 44 numarasına bağlı
HEDEF: resepsiyon 0558 400 67 64 numarasına bağlı
```

```text
[telefon/v2a-tel-016]
GİRDİ: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
ÇIKTI: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
HAM  : rezervasyon 0551 758 00 70 numarasından yapılıyor
HEDEF: rezervasyon 0551 750 80 70 numarasından yapılıyor
```

```text
[kardinal/v2a-kucuk-034]
GİRDİ: Nazlı dün dört soru kırdı.
ÇIKTI: Nazlı dün 4 soru kırdı.
HEDEF: Nazlı dün dört soru kırdı.
```

```text
[kardinal/v2a-kucuk-012]
GİRDİ: Duvara beş tablo asılı.
ÇIKTI: Duvara 5 tablo asılı.
HEDEF: Duvara beş tablo asılı.
```

```text
[kod/v2a-kod-005]
GİRDİ: kargo teslim kodu sıfır sıfır sıfır altı altı sekiz altı üç beş unutma
ÇIKTI: kargo teslim kodu sıfır sıfır sıfır altı altı sekiz altı üç beş unutma
HAM  : kargo teslim kodu 00668635 unutma
HEDEF: kargo teslim kodu 000668635 unutma
```

```text
[kardinal/v2a-kucuk-012]
GİRDİ: duvara beş tablo asılı
ÇIKTI: duvara 5 tablo asılı
HEDEF: duvara beş tablo asılı
```

```text
[telefon/v2a-tel-018]
GİRDİ: Resepsiyon sıfır beş üç yedi sekiz yüz kırk seksen yedi numarasına bağlı.
ÇIKTI: Resepsiyon 0537 840 87 numarasına bağlı.
HEDEF: Resepsiyon 0537 800 40 87 numarasına bağlı.
```

```text
[olcu/v2b-karsit-042]
GİRDİ: yedi yüz gram yedi
ÇIKTI: 700 g 7
HEDEF: 700 g yedi
```

```text
[olcu/v2b-karsit-042]
GİRDİ: yedi yüz elli gram yedi
ÇIKTI: 750 g 7
HEDEF: 750 g yedi
```

```text
[olcu/v2b-karsit-042]
GİRDİ: yedi yüz yirmi beş gram yedi
ÇIKTI: 725 g 7
HEDEF: 725 g yedi
```

```text
[saat_deyis/v2c-saat_deyis-z-027]
GİRDİ: Kahvaltıyı altıyı çeyrek geçe yaptık.
ÇIKTI: Kahvaltıyı altıyı çeyrek geçe yaptık.
HAM  : Kahv6'yı 6'yı çeyrek geçe yaptık.
HEDEF: Kahvaltıyı 6'yı çeyrek geçe yaptık.
```

```text
[yari/v2c-yari-sayi_ek-010]
GİRDİ: 6063'ün üzerindeki siparişler ayrıca incelenir
ÇIKTI: 6063'ün üzerindeki siparişler ayrıca incelenir
HEDEF: 6.063'ün üzerindeki siparişler ayrıca incelenir
```

## Küme: test_v1_donmus (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 99.9 | 0.0 | 0.0 | 99.8 | 0.0 (776) |
| Model + koruma | 2000 | 99.9 | 0.2 | 0.2 | 99.4 | 0.0 (776) |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 50 | 0.0 | 2.0 | 100.0 | 100.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 99.0 | 99.0 |
| karisik | 60 | 0.0 | 53.3 | 100.0 | 100.0 |
| kod | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 180 | 100.0 | 98.9 | 100.0 | 100.0 |
| negatif_es | 200 | 100.0 | 30.0 | 100.0 | 100.0 |
| negatif_kalip | 220 | 100.0 | 30.9 | 100.0 | 100.0 |
| negatif_yazili | 160 | 100.0 | 93.1 | 100.0 | 100.0 |
| olcu | 160 | 0.0 | 64.4 | 100.0 | 100.0 |
| ondalik | 60 | 0.0 | 93.3 | 100.0 | 100.0 |
| para | 140 | 0.0 | 87.9 | 100.0 | 100.0 |
| saat | 130 | 0.0 | 33.1 | 100.0 | 100.0 |
| sira | 70 | 0.0 | 75.7 | 100.0 | 100.0 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 100.0 | 100.0 |
| telefon | 60 | 0.0 | 0.0 | 96.7 | 96.7 |
| yuzde | 100 | 0.0 | 97.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 3 hata, ilk 3 gösterilir)

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
HAM  : telefon numaram 0322 734 99 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[kardinal/kardinal-033]
GİRDİ: ben de xbox onu aldım
ÇIKTI: ben de xbox onu aldım
HEDEF: ben de xbox 10'u aldım
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram artı doksan beş yüz elli beş yüz yetmiş altı elli dört yirmi altı.
ÇIKTI: Telefon numaram artı doksan beş yüz elli beş yüz yetmiş altı elli dört yirmi altı.
HAM  : Telefon numaram +90 555 576 54 26.
HEDEF: Telefon numaram +90 550 576 54 26.
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 97.0 | 0.5 | 0.8 | 96.7 | 0.0 (28) |
| Model + koruma | 100 | 97.0 | 2.9 | 3.7 | 93.3 | 0.0 (28) |

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
| negatif_es | 9 | 100.0 | 11.1 | 100.0 | 100.0 |
| negatif_kalip | 14 | 100.0 | 35.7 | 100.0 | 100.0 |
| negatif_politika | 1 | 100.0 | 0.0 | 100.0 | 100.0 |
| negatif_yazili | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 10 | 0.0 | 80.0 | 90.0 | 90.0 |
| ondalik | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 10 | 0.0 | 70.0 | 100.0 | 100.0 |
| saat | 9 | 0.0 | 55.6 | 100.0 | 100.0 |
| saat_zor | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| sira | 5 | 0.0 | 100.0 | 80.0 | 80.0 |
| skor | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 3 | 0.0 | 0.0 | 66.7 | 66.7 |
| yuzde | 4 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 3 hata, ilk 3 gösterilir)

```text
[olcu/elle]
GİRDİ: bir kilo un iki litre süt al
ÇIKTI: bir kg un 2 L süt al
HEDEF: 1 kg un 2 L süt al
```

```text
[sira/elle]
GİRDİ: otobüse binip altıncı durakta indim
ÇIKTI: otobüse binip altıncı durakta indim
HEDEF: otobüse binip 6. durakta indim
```

```text
[telefon/elle]
GİRDİ: numaram sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi
ÇIKTI: numaram sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi
HAM  : numaram 0532 223 45 67
HEDEF: numaram 0532 123 45 67
```

## Küme: zorluk2_gizli (50 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 50 | 42.0 | 35.9 | 52.4 | 2.7 | 0.0 (21) |
| Kural tabanlı (saf) | 50 | 56.0 | 5.8 | 18.8 | 70.3 | 52.4 (21) |
| Model (korumasız) | 50 | 98.0 | 0.5 | 1.0 | 97.3 | 0.0 (21) |
| Model + koruma | 50 | 98.0 | 0.5 | 1.0 | 97.3 | 0.0 (21) |

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
| negatif_es | 8 | 100.0 | 50.0 | 100.0 | 100.0 |
| negatif_kalip | 10 | 100.0 | 50.0 | 100.0 | 100.0 |
| negatif_politika | 1 | 100.0 | 0.0 | 100.0 | 100.0 |
| negatif_yazili | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| olcu | 3 | 0.0 | 100.0 | 100.0 | 100.0 |
| ondalik | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 4 | 0.0 | 75.0 | 100.0 | 100.0 |
| saat | 3 | 0.0 | 33.3 | 100.0 | 100.0 |
| sira | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| skor | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| tarih | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 1 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 2 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 1 hata, ilk 1 gösterilir)

```text
[skor/elle2]
GİRDİ: derbi bir bir berabere bitti
ÇIKTI: derbi bir bir berabere bitti
HEDEF: derbi 1-1 berabere bitti
```

## Küme: zorluk3_gizli_v2 (83 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 83 | 32.5 | 35.9 | 51.9 | 5.9 | 0.0 (27) |
| Kural tabanlı (saf) | 83 | 43.4 | 12.1 | 27.6 | 61.2 | 63.0 (27) |
| Model (korumasız) | 83 | 97.6 | 0.6 | 0.8 | 100.0 | 7.4 (27) |
| Model + koruma | 83 | 97.6 | 0.6 | 0.8 | 100.0 | 7.4 (27) |

Koruma 0 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| ayin_gunu | 4 | 0.0 | 100.0 | 100.0 | 100.0 |
| bilesik | 4 | 0.0 | 100.0 | 100.0 | 100.0 |
| bitisik | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| ic_sifir | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| kardinal | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| karisik | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| karsit | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 7 | 100.0 | 28.6 | 85.7 | 85.7 |
| negatif_kalip | 17 | 100.0 | 41.2 | 94.1 | 94.1 |
| negatif_politika | 2 | 100.0 | 0.0 | 100.0 | 100.0 |
| olcu | 7 | 0.0 | 57.1 | 100.0 | 100.0 |
| saat_deyis | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| telefon | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| yari | 12 | 8.3 | 8.3 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 2 hata, ilk 2 gösterilir)

```text
[negatif_es/elle3]
GİRDİ: elmayı yedi sonra uyudu
ÇIKTI: elmayı 7 sonra uyudu
HEDEF: elmayı yedi sonra uyudu
```

```text
[negatif_kalip/elle3]
GİRDİ: bu iş dört dörtlük oldu
ÇIKTI: bu iş 4-4'lük oldu
HEDEF: bu iş dört dörtlük oldu
```
