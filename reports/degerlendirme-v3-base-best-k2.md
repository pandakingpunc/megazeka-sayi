# Megazeka-Sayı değerlendirmesi — v3-base-best-k2

Kontrol noktası: `v3-base-best` · süre: 356 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 99.4 | 0.1 | 0.2 | 99.2 | 0.5 (802) |
| Model + koruma | 2000 | 99.2 | 0.3 | 0.5 | 98.6 | 0.5 (802) |

Koruma 5 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 98.9 | 97.8 |
| karisik | 49 | 0.0 | 77.6 | 95.9 | 95.9 |
| kod | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 146 | 100.0 | 99.3 | 100.0 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 100.0 | 100.0 |
| negatif_kalip | 283 | 100.0 | 30.0 | 98.6 | 98.6 |
| negatif_yazili | 130 | 100.0 | 95.4 | 100.0 | 100.0 |
| olcu | 130 | 0.0 | 92.3 | 100.0 | 100.0 |
| ondalik | 130 | 0.0 | 91.5 | 100.0 | 100.0 |
| para | 129 | 0.0 | 88.4 | 100.0 | 100.0 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 96.5 | 96.5 |
| skor | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 97 | 0.0 | 10.3 | 100.0 | 100.0 |
| telefon | 49 | 0.0 | 0.0 | 93.9 | 93.9 |
| yuzde | 89 | 0.0 | 98.9 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 15 hata, ilk 15 gösterilir)

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz.
ÇIKTI: 1 kuruşunu bile boşa harcamaz.
HEDEF: Bir kuruşunu bile boşa harcamaz.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: bir kuruşunu bile boşa harcamaz
ÇIKTI: 1 kuruşunu bile boşa harcamaz
HEDEF: bir kuruşunu bile boşa harcamaz
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş beş sıfır sıfır sekiz altı beş beş beş sekiz diye kaydettim
ÇIKTI: numarayı sıfır beş beş sıfır sıfır sekiz altı beş beş beş sekiz diye kaydettim
HAM  : numarayı 0550 008 65 58 diye kaydettim
HEDEF: numarayı 0550 086 55 58 diye kaydettim
```

```text
[kardinal/kardinal-070]
GİRDİ: Kırktan geriye doğru saydık.
ÇIKTI: Kırktan geriye doğru saydık.
HEDEF: 40'tan geriye doğru saydık.
```

```text
[kardinal/kardinal-066]
GİRDİ: Hesaplama onda tıkandı.
ÇIKTI: Hesaplama onda tıkandı.
HAM  : Hesaplama 10'da tıkandı.
HEDEF: Hesaplama 10'da tıkandı.
```

```text
[kardinal/kardinal-030]
GİRDİ: Doktor hastanın kırk yaşında olduğunu söyledi.
ÇIKTI: Doktor hastanın kırk yaşında olduğunu söyledi.
HEDEF: Doktor hastanın 40 yaşında olduğunu söyledi.
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
HAM  : şifreye 10'u ekle
HEDEF: şifreye 10'u ekle
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
[sira/sira-024]
GİRDİ: bu festival dördüncü kez düzenleniyor
ÇIKTI: bu festival dördüncü kez düzenleniyor
HEDEF: bu festival 4. kez düzenleniyor
```

```text
[telefon/telefon-014]
GİRDİ: numarayı sıfır beş yüz elli dört yüz bir elli sekiz yetmiş bir diye kaydettim
ÇIKTI: numarayı 0550 401 58 71 diye kaydettim
HEDEF: numarayı 0554 101 58 71 diye kaydettim
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz, ama neyse.
ÇIKTI: 1 kuruşunu bile boşa harcamaz, ama neyse.
HEDEF: Bir kuruşunu bile boşa harcamaz, ama neyse.
```

```text
[telefon/telefon-014]
GİRDİ: Numarayı sıfır beş yüz kırk altı yüz seksen üç on dört seksen beş diye kaydettim.
ÇIKTI: Numarayı sıfır beş yüz kırk altı yüz seksen üç on dört seksen beş diye kaydettim.
HAM  : Numarayı 0546 683 14 85 diye kaydettim.
HEDEF: Numarayı 0540 683 14 85 diye kaydettim.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: kısacası bir kuruşunu bile boşa harcamaz
ÇIKTI: kısacası 1 kuruşunu bile boşa harcamaz
HEDEF: kısacası bir kuruşunu bile boşa harcamaz
```

## Küme: test_v2_yeni_kaynaklar (1400 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 1400 | 27.1 | 35.2 | 48.2 | 6.8 | 0.0 (379) |
| Kural tabanlı (saf) | 1400 | 42.3 | 9.2 | 22.8 | 58.0 | 52.0 (379) |
| Model (korumasız) | 1400 | 98.9 | 0.1 | 0.3 | 98.9 | 1.3 (379) |
| Model + koruma | 1400 | 98.9 | 0.6 | 1.0 | 98.4 | 1.1 (379) |

Koruma 8 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 41 | 0.0 | 0.0 | 100.0 | 100.0 |
| bilesik | 56 | 0.0 | 76.8 | 100.0 | 100.0 |
| bitisik | 107 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 9 | 0.0 | 33.3 | 88.9 | 88.9 |
| kardinal | 91 | 20.9 | 58.2 | 97.8 | 97.8 |
| karisik | 56 | 0.0 | 42.9 | 100.0 | 100.0 |
| kod | 44 | 0.0 | 0.0 | 93.2 | 93.2 |
| negatif_es | 100 | 100.0 | 61.0 | 99.0 | 99.0 |
| negatif_kalip | 232 | 100.0 | 42.2 | 99.1 | 99.6 |
| olcu | 138 | 0.0 | 58.7 | 100.0 | 100.0 |
| para | 55 | 0.0 | 69.1 | 100.0 | 100.0 |
| saat | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| saat_deyis | 89 | 0.0 | 100.0 | 100.0 | 100.0 |
| sira | 11 | 0.0 | 100.0 | 100.0 | 100.0 |
| tarih | 72 | 0.0 | 70.8 | 100.0 | 100.0 |
| telefon | 56 | 0.0 | 0.0 | 91.1 | 91.1 |
| yari | 232 | 12.1 | 12.5 | 99.1 | 99.1 |
| yuzde | 5 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 15 hata, ilk 15 gösterilir)

```text
[kod/v2a-kod-016]
GİRDİ: dosya numaranız sıfır üç üç beş yedi dört bir iki olarak kaydedildi
ÇIKTI: dosya numaranız 0335 74 12 olarak kaydedildi
HEDEF: dosya numaranız 03357412 olarak kaydedildi
```

```text
[kod/v2a-kod-027]
GİRDİ: sicil numarası sıfır sıfır beş beş dört altı üç üç üç
ÇIKTI: sicil numarası sıfır sıfır beş beş dört altı üç üç üç
HAM  : sicil numarası 00554 633 33
HEDEF: sicil numarası 005546333
```

```text
[buyuk/v2a-sifir-065]
GİRDİ: Bu rakam dört milyon yedi yüz on üçe ulaştı.
ÇIKTI: Bu rakam dört milyon yedi yüz on üçe ulaştı.
HAM  : Bu rakam 4.713'e ulaştı.
HEDEF: Bu rakam 4.000.713'e ulaştı.
```

```text
[telefon/v2a-tel-006]
GİRDİ: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
ÇIKTI: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
HAM  : servisin hattı 0552 607 98 84
HEDEF: servisin hattı 0552 600 79 84
```

```text
[telefon/v2a-tel-018]
GİRDİ: resepsiyon sıfır beş beş sekiz dört yüz altı yedi altı dört numarasına bağlı
ÇIKTI: resepsiyon sıfır beş beş sekiz dört yüz altı yedi altı dört numarasına bağlı
HAM  : resepsiyon 0558 406 76 64 numarasına bağlı
HEDEF: resepsiyon 0558 400 67 64 numarasına bağlı
```

```text
[telefon/v2a-tel-016]
GİRDİ: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
ÇIKTI: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
HAM  : rezervasyon 0551 750 58 00 numarasından yapılıyor
HEDEF: rezervasyon 0551 750 80 70 numarasından yapılıyor
```

```text
[kardinal/v2a-kucuk-012]
GİRDİ: Duvara beş tablo asılı.
ÇIKTI: Duvara 5 tablo asılı.
HEDEF: Duvara beş tablo asılı.
```

```text
[kod/v2a-kod-027]
GİRDİ: Sicil numarası bir iki dokuz dört dört üç iki iki iki.
ÇIKTI: Sicil numarası bir iki dokuz dört dört üç iki iki iki.
HAM  : Sicil numarası 12944322.
HEDEF: Sicil numarası 129443222.
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
[telefon/v2a-tel-007]
GİRDİ: acil durumda sıfır beş yüz kırk altı iki yüz elli yedi seksen yedi sıfır numarasına ulaşın
ÇIKTI: acil durumda sıfır beş yüz kırk altı iki yüz elli yedi seksen yedi sıfır numarasına ulaşın
HAM  : acil durumda 0546 257 87 00 numarasına ulaşın
HEDEF: acil durumda 0546 257 80 70 numarasına ulaşın
```

```text
[negatif_es/v2b-bin-095]
GİRDİ: Bin şuraya.
ÇIKTI: 1.000 şuraya.
HEDEF: Bin şuraya.
```

```text
[negatif_kalip/v2b-deyim-116]
GİRDİ: Sofrada bin bir çeşit börek vardı.
ÇIKTI: Sofrada 1.001 çeşit börek vardı.
HEDEF: Sofrada bin bir çeşit börek vardı.
```

```text
[yari/v2c-yari-karisik-023]
GİRDİ: yolculuk 02:15 başladı altmış üç kilometre gittik
ÇIKTI: yolculuk 02.15 başladı 63 km gittik
HEDEF: yolculuk 2.15 başladı 63 km gittik
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
| Model (korumasız) | 2000 | 99.8 | 0.0 | 0.1 | 99.7 | 0.1 (776) |
| Model + koruma | 2000 | 99.8 | 0.1 | 0.2 | 99.7 | 0.1 (776) |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 50 | 0.0 | 2.0 | 100.0 | 100.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 99.0 | 98.0 |
| karisik | 60 | 0.0 | 53.3 | 98.3 | 98.3 |
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

### Hata örnekleri (model_korumali; toplam 5 hata, ilk 5 gösterilir)

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram sıfır beş yüz kırk sekiz yüz elli dört doksan on beş.
ÇIKTI: Telefon numaram 0540 854 90 15.
HEDEF: Telefon numaram 0548 154 90 15.
```

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram 0322 734 9 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[karisik/karisik-000]
GİRDİ: pazardan yedi yüz yetmiş beş gram süt aldım hesap iki yüz otuz bin altı yüz seksen yedi türk lirası beş kuruş tuttu
ÇIKTI: pazardan 775 g süt aldım hesap iki yüz otuz bin altı yüz seksen yedi türk lirası beş kuruş tuttu
HAM  : pazardan 775 g süt aldım hesap 230.687,85 TL tuttu
HEDEF: pazardan 775 g süt aldım hesap 230.687,05 TL tuttu
```

```text
[kardinal/kardinal-033]
GİRDİ: ben de xbox onu aldım
ÇIKTI: ben de xbox onu aldım
HAM  : ben de xbox 10'u aldım
HEDEF: ben de xbox 10'u aldım
```

```text
[kardinal/kardinal-015]
GİRDİ: Masada beş sandalye eksik.
ÇIKTI: Masada 5 sandalye eksik.
HEDEF: Masada beş sandalye eksik.
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 99.0 | 0.3 | 0.3 | 98.9 | 0.0 (28) |
| Model + koruma | 100 | 99.0 | 0.3 | 0.3 | 98.9 | 0.0 (28) |

Koruma 0 örnekte en az bir bölgeyi geri aldı.

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
| olcu | 10 | 0.0 | 80.0 | 100.0 | 100.0 |
| ondalik | 2 | 0.0 | 100.0 | 100.0 | 100.0 |
| para | 10 | 0.0 | 70.0 | 100.0 | 100.0 |
| saat | 9 | 0.0 | 55.6 | 100.0 | 100.0 |
| saat_zor | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| sira | 5 | 0.0 | 100.0 | 80.0 | 80.0 |
| skor | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| telefon | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| yuzde | 4 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 1 hata, ilk 1 gösterilir)

```text
[sira/elle]
GİRDİ: otobüse binip altıncı durakta indim
ÇIKTI: otobüse binip altıncı durakta indim
HEDEF: otobüse binip 6. durakta indim
```

## Küme: zorluk2_gizli (50 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 50 | 42.0 | 35.9 | 52.4 | 2.7 | 0.0 (21) |
| Kural tabanlı (saf) | 50 | 56.0 | 5.8 | 18.8 | 70.3 | 52.4 (21) |
| Model (korumasız) | 50 | 96.0 | 0.8 | 1.4 | 97.3 | 4.8 (21) |
| Model + koruma | 50 | 96.0 | 0.8 | 1.4 | 97.3 | 4.8 (21) |

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
| negatif_kalip | 10 | 100.0 | 50.0 | 90.0 | 90.0 |
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

### Hata örnekleri (model_korumali; toplam 2 hata, ilk 2 gösterilir)

```text
[skor/elle2]
GİRDİ: derbi bir bir berabere bitti
ÇIKTI: derbi bir bir berabere bitti
HEDEF: derbi 1-1 berabere bitti
```

```text
[negatif_kalip/elle2]
GİRDİ: bu iş beş para etmez
ÇIKTI: bu iş 5 para etmez
HEDEF: bu iş beş para etmez
```

## Küme: zorluk3_gizli_v2 (83 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 83 | 32.5 | 35.9 | 51.9 | 5.9 | 0.0 (27) |
| Kural tabanlı (saf) | 83 | 43.4 | 12.1 | 27.6 | 61.2 | 63.0 (27) |
| Model (korumasız) | 83 | 98.8 | 0.4 | 0.5 | 100.0 | 0.0 (27) |
| Model + koruma | 83 | 98.8 | 0.4 | 0.5 | 100.0 | 0.0 (27) |

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
| karisik | 3 | 0.0 | 0.0 | 66.7 | 66.7 |
| karsit | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 7 | 100.0 | 28.6 | 100.0 | 100.0 |
| negatif_kalip | 17 | 100.0 | 41.2 | 100.0 | 100.0 |
| negatif_politika | 2 | 100.0 | 0.0 | 100.0 | 100.0 |
| olcu | 7 | 0.0 | 57.1 | 100.0 | 100.0 |
| saat_deyis | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| telefon | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| yari | 12 | 8.3 | 8.3 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 1 hata, ilk 1 gösterilir)

```text
[karisik/elle3]
GİRDİ: On beş kilometrelik parkuru bir saat yirmi dakikada koştum ve yüz kırk kişi arasında on ikinci oldum.
ÇIKTI: 15 km'lik parkuru 1 saat 20 dakikada koştum ve 140 kişi arasında 12. oldum.
HEDEF: 15 km'lik parkuru 1 saat 20 dakikada koştum ve 140 kişi arasında on ikinci oldum.
```
