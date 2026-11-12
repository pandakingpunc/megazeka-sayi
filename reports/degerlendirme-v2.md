# Megazeka-Sayı değerlendirmesi — v2

Kontrol noktası: `best` · süre: 243 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 98.5 | 0.2 | 0.3 | 99.4 | 3.0 (802) |
| Model + koruma | 2000 | 96.9 | 1.0 | 1.5 | 96.6 | 2.6 (802) |

Koruma 37 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 98.0 | 98.0 |
| buyuk | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 100.0 | 94.9 |
| karisik | 49 | 0.0 | 77.6 | 100.0 | 98.0 |
| kod | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 146 | 100.0 | 99.3 | 100.0 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 97.4 | 98.3 |
| negatif_kalip | 283 | 100.0 | 30.0 | 94.0 | 94.3 |
| negatif_yazili | 130 | 100.0 | 95.4 | 99.2 | 99.2 |
| olcu | 130 | 0.0 | 92.3 | 100.0 | 100.0 |
| ondalik | 130 | 0.0 | 91.5 | 100.0 | 87.7 |
| para | 129 | 0.0 | 88.4 | 100.0 | 100.0 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 98.2 | 98.2 |
| skor | 40 | 0.0 | 0.0 | 95.0 | 95.0 |
| tarih | 97 | 0.0 | 10.3 | 100.0 | 96.9 |
| telefon | 49 | 0.0 | 0.0 | 95.9 | 91.8 |
| yuzde | 89 | 0.0 | 98.9 | 100.0 | 95.5 |

### Hata örnekleri (model_korumali; toplam 62 hata, ilk 25 gösterilir)

```text
[kardinal/kardinal-046]
GİRDİ: dokuz yüzün bir fazlasını bulmamız gerekiyor
ÇIKTI: dokuz yüzün bir fazlasını bulmamız gerekiyor
HAM  : 900'ün bir fazlasını bulmamız gerekiyor
HEDEF: 900'ün bir fazlasını bulmamız gerekiyor
```

```text
[yuzde/yuzde-029]
GİRDİ: partinin oyu yüzde yüzü buldu
ÇIKTI: partinin oyu yüzde yüzü buldu
HAM  : partinin oyu %100'ü buldu
HEDEF: partinin oyu %100'ü buldu
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz.
ÇIKTI: 1 kuruşunu bile boşa harcamaz.
HEDEF: Bir kuruşunu bile boşa harcamaz.
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
ÇIKTI: mesaj gelirse 0559 109 90 03 numarasına yönlendir
HEDEF: mesaj gelirse 0550 909 90 03 numarasına yönlendir
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: bir kuruşunu bile boşa harcamaz
ÇIKTI: 1 kuruşunu bile boşa harcamaz
HEDEF: bir kuruşunu bile boşa harcamaz
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
[negatif_kalip/negatif_kalip-001]
GİRDİ: bir iki dakika dinlenip yola devam ederiz yani
ÇIKTI: 1-2 dakika dinlenip yola devam ederiz yani
HEDEF: bir iki dakika dinlenip yola devam ederiz yani
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
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz, herkes biliyor.
ÇIKTI: 1 kuruşunu bile boşa harcamaz, herkes biliyor.
HEDEF: Bir kuruşunu bile boşa harcamaz, herkes biliyor.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Şunu söyleyeyim, bir kuruşunu bile boşa harcamaz, herkes biliyor.
ÇIKTI: Şunu söyleyeyim, 1 kuruşunu bile boşa harcamaz, herkes biliyor.
HEDEF: Şunu söyleyeyim, bir kuruşunu bile boşa harcamaz, herkes biliyor.
```

```text
[negatif_es/negatif_es-054]
GİRDİ: zeynep meze yedi sonra çay içti
ÇIKTI: zeynep meze 7 sonra çay içti
HEDEF: zeynep meze yedi sonra çay içti
```

```text
[ondalik/ondalik-031]
GİRDİ: Yedi virgül onun karesini aldım.
ÇIKTI: Yedi virgül onun karesini aldım.
HAM  : 7,10'un karesini aldım.
HEDEF: 7,10'un karesini aldım.
```

```text
[yuzde/yuzde-032]
GİRDİ: mevcudun yüzde yüzü sınavı geçti
ÇIKTI: mevcudun yüzde yüzü sınavı geçti
HAM  : mevcudun %100'ü sınavı geçti
HEDEF: mevcudun %100'ü sınavı geçti
```

```text
[negatif_kalip/negatif_kalip-021]
GİRDİ: geçen hafta birden istasyonda ışıklar söndü
ÇIKTI: geçen hafta 1'den istasyonda ışıklar söndü
HEDEF: geçen hafta birden istasyonda ışıklar söndü
```

```text
[kardinal/kardinal-083]
GİRDİ: Seçilen sayının kırkın tersi lazım.
ÇIKTI: Seçilen sayının kırkın tersi lazım.
HAM  : Seçilen sayının 40'ın tersi lazım.
HEDEF: Seçilen sayının 40'ın tersi lazım.
```

```text
[aralik/aralik-011]
GİRDİ: on on beş yıl önce buraya taşındık
ÇIKTI: 15 yıl önce buraya taşındık
HEDEF: 10-15 yıl önce buraya taşındık
```

```text
[ondalik/ondalik-048]
GİRDİ: ateş yirmi virgül ona çıktı
ÇIKTI: ateş yirmi virgül ona çıktı
HAM  : ateş 20,10'a çıktı
HEDEF: ateş 20,10'a çıktı
```

```text
[telefon/telefon-003]
GİRDİ: yusuf bana artı doksan beş yüz elli bir iki yüz doksan yedi seksen bir altmış üç numarasını verdi
ÇIKTI: yusuf bana artı doksan beş yüz elli bir iki yüz doksan yedi seksen bir altmış üç numarasını verdi
HAM  : yusuf bana +90 551 297 81 63 numarasını verdi
HEDEF: yusuf bana +90 551 297 81 63 numarasını verdi
```

```text
[kardinal/kardinal-066]
GİRDİ: Hesaplama onda tıkandı.
ÇIKTI: Hesaplama onda tıkandı.
HAM  : Hesaplama 10'da tıkandı.
HEDEF: Hesaplama 10'da tıkandı.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Öğretmen dedi ki, bir kuruşunu bile boşa harcamaz.
ÇIKTI: Öğretmen dedi ki, 1 kuruşunu bile boşa harcamaz.
HEDEF: Öğretmen dedi ki, bir kuruşunu bile boşa harcamaz.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz, yani.
ÇIKTI: 1 kuruşunu bile boşa harcamaz, yani.
HEDEF: Bir kuruşunu bile boşa harcamaz, yani.
```

## Küme: test_v2_yeni_kaynaklar (1400 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 1400 | 27.1 | 35.2 | 48.2 | 6.8 | 0.0 (379) |
| Kural tabanlı (saf) | 1400 | 42.3 | 9.2 | 22.8 | 58.0 | 52.0 (379) |
| Model (korumasız) | 1400 | 96.9 | 0.4 | 0.7 | 98.9 | 6.9 (379) |
| Model + koruma | 1400 | 80.1 | 5.8 | 7.4 | 80.0 | 5.3 (379) |

Koruma 208 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 41 | 0.0 | 0.0 | 100.0 | 100.0 |
| bilesik | 56 | 0.0 | 76.8 | 98.2 | 98.2 |
| bitisik | 107 | 0.0 | 0.0 | 100.0 | 6.5 |
| buyuk | 9 | 0.0 | 33.3 | 100.0 | 88.9 |
| kardinal | 91 | 20.9 | 58.2 | 96.7 | 96.7 |
| karisik | 56 | 0.0 | 42.9 | 92.9 | 91.1 |
| kod | 44 | 0.0 | 0.0 | 97.7 | 97.7 |
| negatif_es | 100 | 100.0 | 61.0 | 93.0 | 96.0 |
| negatif_kalip | 232 | 100.0 | 42.2 | 92.7 | 94.0 |
| olcu | 138 | 0.0 | 58.7 | 99.3 | 87.7 |
| para | 55 | 0.0 | 69.1 | 100.0 | 100.0 |
| saat | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| saat_deyis | 89 | 0.0 | 100.0 | 98.9 | 88.8 |
| sira | 11 | 0.0 | 100.0 | 100.0 | 100.0 |
| tarih | 72 | 0.0 | 70.8 | 100.0 | 56.9 |
| telefon | 56 | 0.0 | 0.0 | 89.3 | 82.1 |
| yari | 232 | 12.1 | 12.5 | 99.1 | 64.7 |
| yuzde | 5 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 279 hata, ilk 25 gösterilir)

```text
[olcu/v2a-yeni-017]
GİRDİ: konya beş yüz kırk sekiz kilometrekarelik bir alana yayılmış
ÇIKTI: konya beş yüz kırk sekiz kilometrekarelik bir alana yayılmış
HAM  : konya 548 km²'lik bir alana yayılmış
HEDEF: konya 548 km²'lik bir alana yayılmış
```

```text
[olcu/v2a-yeni-017]
GİRDİ: İstanbul bin beş yüz elli dört kilometrekarelik bir alana yayılmış.
ÇIKTI: İstanbul bin beş yüz elli dört kilometrekarelik bir alana yayılmış.
HAM  : İstanbul 1.554 km²'lik bir alana yayılmış.
HEDEF: İstanbul 1.554 km²'lik bir alana yayılmış.
```

```text
[olcu/v2a-yeni-017]
GİRDİ: Trabzon bin yedi yüz altmış sekiz kilometrekarelik bir alana yayılmış.
ÇIKTI: Trabzon bin yedi yüz altmış sekiz kilometrekarelik bir alana yayılmış.
HAM  : Trabzon 1.768 km²'lik bir alana yayılmış.
HEDEF: Trabzon 1.768 km²'lik bir alana yayılmış.
```

```text
[telefon/v2a-tel-026]
GİRDİ: Doktorun sekreteri sıfır iki bir altı yüz altı elli dört otuz numarasını verdi.
ÇIKTI: Doktorun sekreteri 0216 54 30 numarasını verdi.
HEDEF: Doktorun sekreteri 0216 106 54 30 numarasını verdi.
```

```text
[bilesik/v2a-bilesik-033]
GİRDİ: Deniz yurt dışında bir yıl on bir ay kaldı.
ÇIKTI: Deniz yurt dışında bir yıl 11 ay kaldı.
HEDEF: Deniz yurt dışında 1 yıl 11 ay kaldı.
```

```text
[telefon/v2a-tel-021]
GİRDİ: Sahibinden satılık ilanda iletişim artı doksan beş yüz elli iki yedi yüz elli doksan bir sıfır yedi.
ÇIKTI: Sahibinden satılık ilanda iletişim artı doksan beş yüz elli iki yedi yüz elli doksan bir sıfır yedi.
HAM  : Sahibinden satılık ilanda iletişim +90 552 750 91 07.
HEDEF: Sahibinden satılık ilanda iletişim +90 552 750 91 07.
```

```text
[telefon/v2a-tel-006]
GİRDİ: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
ÇIKTI: servisin hattı 0552 607 98 84
HEDEF: servisin hattı 0552 600 79 84
```

```text
[olcu/v2a-yeni-036]
GİRDİ: işlemci yüz iki megahertz hızında çalışıyor
ÇIKTI: işlemci yüz iki megahertz hızında çalışıyor
HAM  : işlemci 102 MHz hızında çalışıyor
HEDEF: işlemci 102 MHz hızında çalışıyor
```

```text
[olcu/v2a-birim-079]
GİRDİ: Yeni sınır otuz bir derece santigratlık bir değer.
ÇIKTI: Yeni sınır 31 °C'ylik bir değer.
HEDEF: Yeni sınır 31 °C'lik bir değer.
```

```text
[karisik/v2a-uzun-068]
GİRDİ: altıncı katta oturan komşumuz altmış bin dört yüz yirmi yedi lira kira veriyor evi ise yüz doksan dört metrekare büyüklüğünde
ÇIKTI: 6. katta oturan komşumuz altmış bin dört yüz yirmi yedi lira kira veriyor evi ise 194 m² büyüklüğünde
HAM  : 6. katta oturan komşumuz 60.427 TL veriyor evi ise 194 m² büyüklüğünde
HEDEF: 6. katta oturan komşumuz 60.427 TL kira veriyor evi ise 194 m² büyüklüğünde
```

```text
[telefon/v2a-tel-018]
GİRDİ: resepsiyon sıfır beş beş sekiz dört yüz altı yedi altı dört numarasına bağlı
ÇIKTI: resepsiyon 0558 406 76 numarasına bağlı
HEDEF: resepsiyon 0558 400 67 64 numarasına bağlı
```

```text
[olcu/v2a-yeni-017]
GİRDİ: dörtyol iki bin üç yüz otuz bir kilometrekarelik bir alana yayılmış
ÇIKTI: dörtyol iki bin üç yüz otuz bir kilometrekarelik bir alana yayılmış
HAM  : dörtyol 2.331 km²'lik bir alana yayılmış
HEDEF: dörtyol 2.331 km²'lik bir alana yayılmış
```

```text
[telefon/v2a-tel-016]
GİRDİ: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
ÇIKTI: rezervasyon 0551 758 070 numarasından yapılıyor
HEDEF: rezervasyon 0551 750 80 70 numarasından yapılıyor
```

```text
[olcu/v2a-yeni-025]
GİRDİ: Depo yedi yüz yetmiş üç kilovat saatlik bir batarya taktık.
ÇIKTI: Depo yedi yüz yetmiş üç kilovat saatlik bir batarya taktık.
HAM  : Depo 773 kWh'lik bir batarya taktık.
HEDEF: Depo 773 kWh'lik bir batarya taktık.
```

```text
[olcu/v2a-yeni-017]
GİRDİ: Antalya sekiz yüz altmış beş kilometrekarelik bir alana yayılmış.
ÇIKTI: Antalya sekiz yüz altmış beş kilometrekarelik bir alana yayılmış.
HAM  : Antalya 865 km²'lik bir alana yayılmış.
HEDEF: Antalya 865 km²'lik bir alana yayılmış.
```

```text
[telefon/v2a-tel-026]
GİRDİ: Doktorun sekreteri artı doksan beş yüz kırk beş sıfır yirmi beş dört sıfır sekiz sekiz numarasını verdi.
ÇIKTI: Doktorun sekreteri artı doksan beş yüz kırk beş sıfır yirmi beş dört sıfır sekiz sekiz numarasını verdi.
HAM  : Doktorun sekreteri +90 545 025 40 88 numarasını verdi.
HEDEF: Doktorun sekreteri +90 545 025 40 88 numarasını verdi.
```

```text
[karisik/v2a-uzun-037]
GİRDİ: nüfusun yüzde yedi buçuk kadarı gaziantep şehrinde yaşıyor kentin yüz ölçümü elli sekiz metrekare civarında
ÇIKTI: nüfusun %7,5 kadarı gaziantep şehrinde yaşıyor kentin 100 ölçümü 58 m² civarında
HEDEF: nüfusun %7,5 kadarı gaziantep şehrinde yaşıyor kentin yüz ölçümü 58 m² civarında
```

```text
[kardinal/v2a-sifir-040]
GİRDİ: Stada otuz yedi milyon iki öğrenci geldi.
ÇIKTI: Stada 37.002 öğrenci geldi.
HEDEF: Stada 37.000.002 öğrenci geldi.
```

```text
[telefon/v2a-tel-031]
GİRDİ: toplantı bağlantısı artı doksan iki yüz seksen iki üç yüz elli dokuz on yirmi numarasına gelecek
ÇIKTI: toplantı bağlantısı artı doksan iki yüz seksen iki üç yüz elli dokuz on yirmi numarasına gelecek
HAM  : toplantı bağlantısı +90 282 359 10 20 numarasına gelecek
HEDEF: toplantı bağlantısı +90 282 359 10 20 numarasına gelecek
```

```text
[telefon/v2a-tel-016]
GİRDİ: rezervasyon artı doksan beş üç dört yüz yirmi doksan sekiz yetmiş numarasından yapılıyor
ÇIKTI: rezervasyon artı doksan beş üç dört yüz yirmi doksan sekiz yetmiş numarasından yapılıyor
HAM  : rezervasyon +90 534 120 98 70 numarasından yapılıyor
HEDEF: rezervasyon +90 534 120 98 70 numarasından yapılıyor
```

```text
[olcu/v2a-yeni-017]
GİRDİ: mersin iki bin dört yüz elli kilometrekarelik bir alana yayılmış
ÇIKTI: mersin iki bin dört yüz elli kilometrekarelik bir alana yayılmış
HAM  : mersin 2.450 km²'lik bir alana yayılmış
HEDEF: mersin 2.450 km²'lik bir alana yayılmış
```

```text
[kardinal/v2a-kucuk-012]
GİRDİ: Duvara beş tablo asılı.
ÇIKTI: Duvara 5 tablo asılı.
HEDEF: Duvara beş tablo asılı.
```

```text
[olcu/v2a-yeni-025]
GİRDİ: Depo bin üç yüz otuz dokuz kilovat saatlik bir batarya taktık.
ÇIKTI: Depo bin üç yüz otuz dokuz kilovat saatlik bir batarya taktık.
HAM  : Depo 1.339 kWh'lik bir batarya taktık.
HEDEF: Depo 1.339 kWh'lik bir batarya taktık.
```

```text
[karisik/v2a-uzun-036]
GİRDİ: Dün gece dört otuzda uyudum, sabah onda kalkınca hava on bir derece santigrat olmuştu.
ÇIKTI: Dün gece 4.30'da uyudum, sabah onda kalkınca hava 11 °C olmuştu.
HAM  : Dün gece 4.30'da uyudum, sabah 10'da kalkınca hava 11 °C olmuştu.
HEDEF: Dün gece 4.30'da uyudum, sabah 10'da kalkınca hava 11 °C olmuştu.
```

```text
[buyuk/v2a-sifir-065]
GİRDİ: Bu rakam yetmiş milyon yedi bine ulaştı.
ÇIKTI: Bu rakam yetmiş milyon yedi bine ulaştı.
HAM  : Bu rakam 70.007.000'e ulaştı.
HEDEF: Bu rakam 70.007.000'e ulaştı.
```

## Küme: test_v1_donmus (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 99.7 | 0.0 | 0.1 | 99.7 | 0.4 (776) |
| Model + koruma | 2000 | 99.2 | 0.5 | 0.7 | 98.0 | 0.0 (776) |

Koruma 18 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 50 | 0.0 | 2.0 | 100.0 | 100.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 100.0 | 96.0 |
| karisik | 60 | 0.0 | 53.3 | 100.0 | 100.0 |
| kod | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 180 | 100.0 | 98.9 | 100.0 | 100.0 |
| negatif_es | 200 | 100.0 | 30.0 | 98.5 | 100.0 |
| negatif_kalip | 220 | 100.0 | 30.9 | 100.0 | 100.0 |
| negatif_yazili | 160 | 100.0 | 93.1 | 100.0 | 100.0 |
| olcu | 160 | 0.0 | 64.4 | 100.0 | 100.0 |
| ondalik | 60 | 0.0 | 93.3 | 100.0 | 98.3 |
| para | 140 | 0.0 | 87.9 | 100.0 | 100.0 |
| saat | 130 | 0.0 | 33.1 | 100.0 | 97.7 |
| sira | 70 | 0.0 | 75.7 | 100.0 | 100.0 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 100.0 | 100.0 |
| telefon | 60 | 0.0 | 0.0 | 95.0 | 90.0 |
| yuzde | 100 | 0.0 | 97.0 | 100.0 | 97.0 |

### Hata örnekleri (model_korumali; toplam 17 hata, ilk 17 gösterilir)

```text
[telefon/telefon-000]
GİRDİ: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
ÇIKTI: Beni artı doksan beş dört sekiz üç üç beş dört dört sıfır altı numarasından arayabilirsin.
HAM  : Beni +90 548 335 44 06 numarasından arayabilirsin.
HEDEF: Beni +90 548 335 44 06 numarasından arayabilirsin.
```

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram 0322 734 94 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[yuzde/yuzde-019]
GİRDİ: kredi faizi yüzde seksen yedi buçuğa düştü
ÇIKTI: kredi faizi yüzde seksen yedi buçuğa düştü
HAM  : kredi faizi %87,5'e düştü
HEDEF: kredi faizi %87,5'e düştü
```

```text
[ondalik/ondalik-017]
GİRDİ: Ortalamamı yirmi dokuz buçuğa çıkardım.
ÇIKTI: Ortalamamı yirmi dokuz buçuğa çıkardım.
HAM  : Ortalamamı 29,5'e çıkardım.
HEDEF: Ortalamamı 29,5'e çıkardım.
```

```text
[saat/saat-026]
GİRDİ: akşam ondan sonra trafik azalıyor
ÇIKTI: akşam ondan sonra trafik azalıyor
HAM  : akşam 10'dan sonra trafik azalıyor
HEDEF: akşam 10'dan sonra trafik azalıyor
```

```text
[kardinal/kardinal-033]
GİRDİ: ben de xbox onu aldım
ÇIKTI: ben de xbox onu aldım
HAM  : ben de xbox 10'u aldım
HEDEF: ben de xbox 10'u aldım
```

```text
[kardinal/kardinal-023]
GİRDİ: puanı yetmiş biri bulan olmadı
ÇIKTI: puanı yetmiş biri bulan olmadı
HAM  : puanı 71'i bulan olmadı
HEDEF: puanı 71'i bulan olmadı
```

```text
[telefon/telefon-001]
GİRDİ: telefon numaram artı doksan beş dört üç dokuz yüz on sıfır üç üç sıfır
ÇIKTI: telefon numaram artı doksan beş dört üç dokuz yüz on sıfır üç üç sıfır
HAM  : telefon numaram +90 543 910 03 30
HEDEF: telefon numaram +90 543 910 03 30
```

```text
[saat/saat-023]
GİRDİ: Sabah onda işe çıktık.
ÇIKTI: Sabah onda işe çıktık.
HAM  : Sabah 10'da işe çıktık.
HEDEF: Sabah 10'da işe çıktık.
```

```text
[kardinal/kardinal-023]
GİRDİ: puanı elli biri bulan olmadı
ÇIKTI: puanı elli biri bulan olmadı
HAM  : puanı 51'i bulan olmadı
HEDEF: puanı 51'i bulan olmadı
```

```text
[yuzde/yuzde-019]
GİRDİ: kredi faizi yüzde yirmi buçuğa düştü
ÇIKTI: kredi faizi yüzde yirmi buçuğa düştü
HAM  : kredi faizi %20,5'e düştü
HEDEF: kredi faizi %20,5'e düştü
```

```text
[saat/saat-023]
GİRDİ: sabah onda işe çıktık
ÇIKTI: sabah onda işe çıktık
HAM  : sabah 10'da işe çıktık
HEDEF: sabah 10'da işe çıktık
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram artı doksan iki yüz otuz iki yedi yüz otuz dokuz yetmiş üç kırk dört.
ÇIKTI: Telefon numaram artı doksan iki yüz otuz iki yedi yüz otuz dokuz yetmiş üç kırk dört.
HAM  : Telefon numaram +90 232 739 73 44.
HEDEF: Telefon numaram +90 232 739 73 44.
```

```text
[kardinal/kardinal-033]
GİRDİ: Ben de Windows yirmi biri aldım.
ÇIKTI: Ben de Windows yirmi biri aldım.
HAM  : Ben de Windows 21'i aldım.
HEDEF: Ben de Windows 21'i aldım.
```

```text
[yuzde/yuzde-023]
GİRDİ: hedefimizin yüzde yüzü gerçekleşti
ÇIKTI: hedefimizin yüzde yüzü gerçekleşti
HAM  : hedefimizin %100'ü gerçekleşti
HEDEF: hedefimizin %100'ü gerçekleşti
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram artı doksan beş yüz elli beş yüz yetmiş altı elli dört yirmi altı.
ÇIKTI: Telefon numaram artı doksan beş yüz elli beş yüz yetmiş altı elli dört yirmi altı.
HAM  : Telefon numaram +90 555 576 54 26.
HEDEF: Telefon numaram +90 550 576 54 26.
```

```text
[telefon/telefon-016]
GİRDİ: siparişiniz için sıfır beş yüz otuz üç yüz altmış yedi seksen dokuz dört sekiz numaralı hattı arayın
ÇIKTI: siparişiniz için 0533 167 89 48 numaralı hattı arayın
HEDEF: siparişiniz için 0530 367 89 48 numaralı hattı arayın
```

## Küme: zorluk (100 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 100 | 28.0 | 51.1 | 66.0 | 3.3 | 0.0 (28) |
| Kural tabanlı (saf) | 100 | 53.0 | 7.1 | 21.4 | 74.4 | 67.9 (28) |
| Model (korumasız) | 100 | 98.0 | 0.7 | 0.8 | 98.9 | 3.6 (28) |
| Model + koruma | 100 | 98.0 | 0.7 | 0.8 | 98.9 | 3.6 (28) |

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
| negatif_kalip | 14 | 100.0 | 35.7 | 92.9 | 92.9 |
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

### Hata örnekleri (model_korumali; toplam 2 hata, ilk 2 gösterilir)

```text
[sira/elle]
GİRDİ: otobüse binip altıncı durakta indim
ÇIKTI: otobüse binip altıncı durakta indim
HEDEF: otobüse binip 6. durakta indim
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
| Model (korumasız) | 83 | 90.4 | 2.4 | 3.6 | 97.6 | 22.2 (27) |
| Model + koruma | 83 | 75.9 | 6.9 | 9.5 | 81.2 | 18.5 (27) |

Koruma 12 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| ayin_gunu | 4 | 0.0 | 100.0 | 100.0 | 75.0 |
| bilesik | 4 | 0.0 | 100.0 | 100.0 | 100.0 |
| bitisik | 5 | 0.0 | 0.0 | 100.0 | 0.0 |
| ic_sifir | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| kardinal | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| karisik | 3 | 0.0 | 0.0 | 33.3 | 33.3 |
| karsit | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 7 | 100.0 | 28.6 | 57.1 | 71.4 |
| negatif_kalip | 17 | 100.0 | 41.2 | 88.2 | 88.2 |
| negatif_politika | 2 | 100.0 | 0.0 | 50.0 | 50.0 |
| olcu | 7 | 0.0 | 57.1 | 100.0 | 57.1 |
| saat_deyis | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| telefon | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| yari | 12 | 8.3 | 8.3 | 100.0 | 66.7 |

### Hata örnekleri (model_korumali; toplam 20 hata, ilk 20 gösterilir)

```text
[olcu/elle3]
GİRDİ: hasta günde beş yüz miligram ilaç alıyor
ÇIKTI: hasta günde beş yüz miligram ilaç alıyor
HAM  : hasta günde 500 mg ilaç alıyor
HEDEF: hasta günde 500 mg ilaç alıyor
```

```text
[olcu/elle3]
GİRDİ: depoya yirmi metreküp su sığıyor
ÇIKTI: depoya yirmi metreküp su sığıyor
HAM  : depoya 20 m³ su sığıyor
HEDEF: depoya 20 m³ su sığıyor
```

```text
[olcu/elle3]
GİRDİ: bu ay üç yüz kilovatsaat elektrik harcadık
ÇIKTI: bu ay üç yüz kilovatsaat elektrik harcadık
HAM  : bu ay 300 kWh elektrik harcadık
HEDEF: bu ay 300 kWh elektrik harcadık
```

```text
[yari/elle3]
GİRDİ: toplantı saat 14:30'da başlayacak
ÇIKTI: toplantı saat 14:30'da başlayacak
HAM  : toplantı saat 14.30'da başlayacak
HEDEF: toplantı saat 14.30'da başlayacak
```

```text
[yari/elle3]
GİRDİ: Maaşlar 22500 liraya yükseldi.
ÇIKTI: Maaşlar 22500 TL'ye yükseldi.
HAM  : Maaşlar 22.500 TL'ye yükseldi.
HEDEF: Maaşlar 22.500 TL'ye yükseldi.
```

```text
[yari/elle3]
GİRDİ: hava eksi 12 derece
ÇIKTI: hava eksi 12 derece
HAM  : hava -12 derece
HEDEF: hava -12 derece
```

```text
[yari/elle3]
GİRDİ: nüfusun yüzde 60'ı şehirde yaşıyor
ÇIKTI: nüfusun yüzde 60'ı şehirde yaşıyor
HAM  : nüfusun %60'ı şehirde yaşıyor
HEDEF: nüfusun %60'ı şehirde yaşıyor
```

```text
[bitisik/elle3]
GİRDİ: sınıfta yirmibeş öğrenci var
ÇIKTI: sınıfta yirmibeş öğrenci var
HAM  : sınıfta 25 öğrenci var
HEDEF: sınıfta 25 öğrenci var
```

```text
[bitisik/elle3]
GİRDİ: bana ikiyüz elli gram peynir ver
ÇIKTI: bana ikiyüz elli gram peynir ver
HAM  : bana 250 g peynir ver
HEDEF: bana 250 g peynir ver
```

```text
[bitisik/elle3]
GİRDİ: Fatura üçbin beşyüz lira gelmiş.
ÇIKTI: Fatura üçbin beşyüz lira gelmiş.
HAM  : Fatura 3.500 TL gelmiş.
HEDEF: Fatura 3.500 TL gelmiş.
```

```text
[bitisik/elle3]
GİRDİ: indirim yüzde onbeş
ÇIKTI: indirim yüzde onbeş
HAM  : indirim %15
HEDEF: indirim %15
```

```text
[bitisik/elle3]
GİRDİ: otobüs saat onbirde kalkıyor
ÇIKTI: otobüs saat onbirde kalkıyor
HAM  : otobüs saat 11'de kalkıyor
HEDEF: otobüs saat 11'de kalkıyor
```

```text
[ayin_gunu/elle3]
GİRDİ: kirayı her ayın birinde ödüyorum
ÇIKTI: kirayı her ayın birinde ödüyorum
HAM  : kirayı her ayın 1'inde ödüyorum
HEDEF: kirayı her ayın 1'inde ödüyorum
```

```text
[karisik/elle3]
GİRDİ: geçen ay yüzde yirmi zam geldi maaşım otuz iki bin liradan otuz sekiz bin dört yüz liraya çıktı
ÇIKTI: geçen ay %20 zam geldi maaşım 32.000,30 TL'ye çıktı
HEDEF: geçen ay %20 zam geldi maaşım 32.000 TL'den 38.400 TL'ye çıktı
```

```text
[karisik/elle3]
GİRDİ: On beş kilometrelik parkuru bir saat yirmi dakikada koştum ve yüz kırk kişi arasında on ikinci oldum.
ÇIKTI: 15 km'lik parkuru 1 saat 20 dakikada koştum ve 140 kişi arasında 12. oldum.
HEDEF: 15 km'lik parkuru 1 saat 20 dakikada koştum ve 140 kişi arasında on ikinci oldum.
```

```text
[negatif_politika/elle3]
GİRDİ: toplantıya yedi kişi katıldı
ÇIKTI: toplantıya 7 kişi katıldı
HEDEF: toplantıya yedi kişi katıldı
```

```text
[negatif_es/elle3]
GİRDİ: motora bin arkama
ÇIKTI: motora 1.000 arkama
HEDEF: motora bin arkama
```

```text
[negatif_es/elle3]
GİRDİ: elmayı yedi sonra uyudu
ÇIKTI: elmayı 7 sonra uyudu
HEDEF: elmayı yedi sonra uyudu
```

```text
[negatif_kalip/elle3]
GİRDİ: abim dokuz eylül üniversitesinde okuyor
ÇIKTI: abim 9 Eylül üniversitesinde okuyor
HEDEF: abim dokuz eylül üniversitesinde okuyor
```

```text
[negatif_kalip/elle3]
GİRDİ: bu iş dört dörtlük oldu
ÇIKTI: bu iş 4-4'lük oldu
HEDEF: bu iş dört dörtlük oldu
```
