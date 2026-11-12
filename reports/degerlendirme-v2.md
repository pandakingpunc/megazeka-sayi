# Megazeka-Sayı değerlendirmesi — v2

Kontrol noktası: `best` · süre: 213 sn · “Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. “Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.

## Küme: test (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 40.1 | 29.9 | 40.7 | 9.6 | 0.0 (802) |
| Kural tabanlı (saf) | 2000 | 59.2 | 4.3 | 15.0 | 73.5 | 46.8 (802) |
| Model (korumasız) | 2000 | 98.5 | 0.2 | 0.3 | 99.4 | 3.0 (802) |
| Model + koruma | 2000 | 98.6 | 0.2 | 0.3 | 99.3 | 2.6 (802) |

Koruma 4 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 49 | 0.0 | 0.0 | 98.0 | 98.0 |
| buyuk | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| eksi | 24 | 0.0 | 66.7 | 100.0 | 100.0 |
| kardinal | 178 | 4.5 | 88.8 | 100.0 | 98.9 |
| karisik | 49 | 0.0 | 77.6 | 100.0 | 100.0 |
| kod | 40 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 146 | 100.0 | 99.3 | 100.0 | 100.0 |
| negatif_es | 235 | 100.0 | 31.1 | 97.4 | 98.3 |
| negatif_kalip | 283 | 100.0 | 30.0 | 94.0 | 94.3 |
| negatif_yazili | 130 | 100.0 | 95.4 | 99.2 | 99.2 |
| olcu | 130 | 0.0 | 92.3 | 100.0 | 100.0 |
| ondalik | 130 | 0.0 | 91.5 | 100.0 | 100.0 |
| para | 129 | 0.0 | 88.4 | 100.0 | 100.0 |
| saat | 105 | 0.0 | 35.2 | 100.0 | 100.0 |
| sira | 57 | 0.0 | 100.0 | 98.2 | 98.2 |
| skor | 40 | 0.0 | 0.0 | 95.0 | 95.0 |
| tarih | 97 | 0.0 | 10.3 | 100.0 | 100.0 |
| telefon | 49 | 0.0 | 0.0 | 95.9 | 95.9 |
| yuzde | 89 | 0.0 | 98.9 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 29 hata, ilk 25 gösterilir)

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz.
ÇIKTI: 1 kuruşunu bile boşa harcamaz.
HEDEF: Bir kuruşunu bile boşa harcamaz.
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
[negatif_kalip/negatif_kalip-001]
GİRDİ: bir iki dakika dinlenip yola devam ederiz yani
ÇIKTI: 1-2 dakika dinlenip yola devam ederiz yani
HEDEF: bir iki dakika dinlenip yola devam ederiz yani
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
[negatif_kalip/negatif_kalip-021]
GİRDİ: geçen hafta birden istasyonda ışıklar söndü
ÇIKTI: geçen hafta 1'den istasyonda ışıklar söndü
HEDEF: geçen hafta birden istasyonda ışıklar söndü
```

```text
[aralik/aralik-011]
GİRDİ: on on beş yıl önce buraya taşındık
ÇIKTI: 15 yıl önce buraya taşındık
HEDEF: 10-15 yıl önce buraya taşındık
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

```text
[negatif_es/negatif_es-054]
GİRDİ: açıkçası cem mantı yedi sonra çay içti
ÇIKTI: açıkçası cem mantı 7 sonra çay içti
HEDEF: açıkçası cem mantı yedi sonra çay içti
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
HAM  : şifreye 10'u ekle
HEDEF: şifreye 10'u ekle
```

```text
[negatif_kalip/negatif_kalip-008]
GİRDİ: Bir iki adım attı ve durdu.
ÇIKTI: 1-2 adım attı ve durdu.
HEDEF: Bir iki adım attı ve durdu.
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: şunu söyleyeyim bir kuruşunu bile boşa harcamaz yani
ÇIKTI: şunu söyleyeyim 1 kuruşunu bile boşa harcamaz yani
HEDEF: şunu söyleyeyim bir kuruşunu bile boşa harcamaz yani
```

```text
[negatif_es/negatif_es-054]
GİRDİ: fatma börek yedi sonra çay içti
ÇIKTI: fatma börek 7 sonra çay içti
HEDEF: fatma börek yedi sonra çay içti
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: neyse bir kuruşunu bile boşa harcamaz diye düşündüm
ÇIKTI: neyse 1 kuruşunu bile boşa harcamaz diye düşündüm
HEDEF: neyse bir kuruşunu bile boşa harcamaz diye düşündüm
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: baksana bir kuruşunu bile boşa harcamaz
ÇIKTI: baksana 1 kuruşunu bile boşa harcamaz
HEDEF: baksana bir kuruşunu bile boşa harcamaz
```

```text
[negatif_yazili/yazili:kod-009]
GİRDİ: tek kullanımlık şifre 25355706
ÇIKTI: tek kullanımlık şifre 253555706
HEDEF: tek kullanımlık şifre 25355706
```

```text
[negatif_kalip/negatif_kalip-136]
GİRDİ: Bir kuruşunu bile boşa harcamaz, ama neyse.
ÇIKTI: 1 kuruşunu bile boşa harcamaz, ama neyse.
HEDEF: Bir kuruşunu bile boşa harcamaz, ama neyse.
```

```text
[negatif_es/negatif_es-054]
GİRDİ: seda meze yedi sonra çay içti
ÇIKTI: seda meze 7 sonra çay içti
HEDEF: seda meze yedi sonra çay içti
```

```text
[telefon/telefon-014]
GİRDİ: Numarayı sıfır beş yüz kırk altı yüz seksen üç on dört seksen beş diye kaydettim.
ÇIKTI: Numarayı 0546 183 14 85 diye kaydettim.
HEDEF: Numarayı 0540 683 14 85 diye kaydettim.
```

## Küme: test_v2_yeni_kaynaklar (1400 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 1400 | 27.1 | 35.2 | 48.2 | 6.8 | 0.0 (379) |
| Kural tabanlı (saf) | 1400 | 42.3 | 9.2 | 22.8 | 58.0 | 52.0 (379) |
| Model (korumasız) | 1400 | 96.9 | 0.4 | 0.7 | 98.9 | 6.9 (379) |
| Model + koruma | 1400 | 97.4 | 0.4 | 0.7 | 98.6 | 5.3 (379) |

Koruma 10 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 41 | 0.0 | 0.0 | 100.0 | 100.0 |
| bilesik | 56 | 0.0 | 76.8 | 98.2 | 98.2 |
| bitisik | 107 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 9 | 0.0 | 33.3 | 100.0 | 100.0 |
| kardinal | 91 | 20.9 | 58.2 | 96.7 | 96.7 |
| karisik | 56 | 0.0 | 42.9 | 92.9 | 92.9 |
| kod | 44 | 0.0 | 0.0 | 97.7 | 97.7 |
| negatif_es | 100 | 100.0 | 61.0 | 93.0 | 96.0 |
| negatif_kalip | 232 | 100.0 | 42.2 | 92.7 | 94.0 |
| olcu | 138 | 0.0 | 58.7 | 99.3 | 99.3 |
| para | 55 | 0.0 | 69.1 | 100.0 | 100.0 |
| saat | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| saat_deyis | 89 | 0.0 | 100.0 | 98.9 | 98.9 |
| sira | 11 | 0.0 | 100.0 | 100.0 | 100.0 |
| tarih | 72 | 0.0 | 70.8 | 100.0 | 100.0 |
| telefon | 56 | 0.0 | 0.0 | 89.3 | 89.3 |
| yari | 232 | 12.1 | 12.5 | 99.1 | 99.1 |
| yuzde | 5 | 0.0 | 100.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 37 hata, ilk 25 gösterilir)

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
[telefon/v2a-tel-006]
GİRDİ: servisin hattı sıfır beş beş iki altı yüz yedi dokuz seksen dört
ÇIKTI: servisin hattı 0552 607 98 84
HEDEF: servisin hattı 0552 600 79 84
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
[telefon/v2a-tel-016]
GİRDİ: rezervasyon sıfır beş yüz elli bir yedi yüz elli sekiz sıfır yetmiş numarasından yapılıyor
ÇIKTI: rezervasyon 0551 758 070 numarasından yapılıyor
HEDEF: rezervasyon 0551 750 80 70 numarasından yapılıyor
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
[kardinal/v2a-kucuk-012]
GİRDİ: Duvara beş tablo asılı.
ÇIKTI: Duvara 5 tablo asılı.
HEDEF: Duvara beş tablo asılı.
```

```text
[karisik/v2a-uzun-068]
GİRDİ: birinci katta oturan komşumuz altmış yedi lira kira veriyor evi ise dört yüz kırk sekiz metrekare büyüklüğünde
ÇIKTI: 1. katta oturan komşumuz altmış yedi lira kira veriyor evi ise 448 m² büyüklüğünde
HAM  : 1. katta oturan komşumuz 67 TL veriyor evi ise 448 m² büyüklüğünde
HEDEF: 1. katta oturan komşumuz 67 TL kira veriyor evi ise 448 m² büyüklüğünde
```

```text
[kardinal/v2a-kucuk-012]
GİRDİ: duvara beş tablo asılı
ÇIKTI: duvara 5 tablo asılı
HEDEF: duvara beş tablo asılı
```

```text
[karisik/v2a-uzun-068]
GİRDİ: sekizinci katta oturan komşumuz iki yüz elli lira kira veriyor evi ise dört yüz doksan dört metrekare büyüklüğünde
ÇIKTI: 8. katta oturan komşumuz iki yüz elli lira kira veriyor evi ise 494 m² büyüklüğünde
HAM  : 8. katta oturan komşumuz 250 TL veriyor evi ise 494 m² büyüklüğünde
HEDEF: 8. katta oturan komşumuz 250 TL kira veriyor evi ise 494 m² büyüklüğünde
```

```text
[telefon/v2a-tel-018]
GİRDİ: Resepsiyon sıfır beş üç yedi sekiz yüz kırk seksen yedi numarasına bağlı.
ÇIKTI: Resepsiyon 0537 840 87 numarasına bağlı.
HEDEF: Resepsiyon 0537 800 40 87 numarasına bağlı.
```

```text
[kod/v2a-kod-027]
GİRDİ: sicil numarası dört beş dokuz dört beş dokuz dört beş dokuz dört beş
ÇIKTI: sicil numarası 45945945
HEDEF: sicil numarası 45945945945
```

```text
[telefon/v2a-tel-007]
GİRDİ: acil durumda sıfır beş yüz kırk altı iki yüz elli yedi seksen yedi sıfır numarasına ulaşın
ÇIKTI: acil durumda 0546 257 87 70 numarasına ulaşın
HEDEF: acil durumda 0546 257 80 70 numarasına ulaşın
```

```text
[negatif_kalip/v2b-ozelad-008]
GİRDİ: kemal yüzüncü yıl üniversitesinde asistan oldu
ÇIKTI: kemal 100. yıl üniversitesinde asistan oldu
HEDEF: kemal yüzüncü yıl üniversitesinde asistan oldu
```

```text
[negatif_es/v2b-bin-095]
GİRDİ: Bin şuraya.
ÇIKTI: 1.000 şuraya.
HEDEF: Bin şuraya.
```

```text
[negatif_kalip/v2b-ozelad-008]
GİRDİ: selin yüzüncü yıl üniversitesinde asistan oldu
ÇIKTI: selin 100. yıl üniversitesinde asistan oldu
HEDEF: selin yüzüncü yıl üniversitesinde asistan oldu
```

```text
[negatif_es/v2b-bin-099]
GİRDİ: Bin içeri.
ÇIKTI: 1.000 içeri.
HEDEF: Bin içeri.
```

```text
[negatif_es/v2b-bin-095]
GİRDİ: bin şuraya sinan
ÇIKTI: 1.000 şuraya sinan
HEDEF: bin şuraya sinan
```

```text
[negatif_kalip/v2b-deyim-012]
GİRDİ: cem bize yedi kat yabancı davrandı
ÇIKTI: cem bize 7 kat yabancı davrandı
HEDEF: cem bize yedi kat yabancı davrandı
```

```text
[negatif_kalip/v2b-ozelad-049]
GİRDİ: kırklar dağı
ÇIKTI: 1940'lar dağı
HEDEF: kırklar dağı
```

```text
[negatif_kalip/v2b-deyim-116]
GİRDİ: Sofrada bin bir çeşit börek vardı.
ÇIKTI: Sofrada 1.001 çeşit börek vardı.
HEDEF: Sofrada bin bir çeşit börek vardı.
```

```text
[negatif_kalip/v2b-kesir-032]
GİRDİ: esra maaşının altıda beşini kiraya veriyor
ÇIKTI: esra maaşının altıda 5'ini kiraya veriyor
HEDEF: esra maaşının altıda beşini kiraya veriyor
```

## Küme: test_v1_donmus (2000 örnek)

| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |
|---|---:|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 2000 | 38.8 | 33.6 | 47.0 | 11.6 | 0.0 (776) |
| Kural tabanlı (saf) | 2000 | 53.2 | 4.1 | 16.7 | 67.5 | 41.4 (776) |
| Model (korumasız) | 2000 | 99.7 | 0.0 | 0.1 | 99.7 | 0.4 (776) |
| Model + koruma | 2000 | 99.8 | 0.0 | 0.1 | 99.7 | 0.0 (776) |

Koruma 4 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 60 | 0.0 | 0.0 | 100.0 | 100.0 |
| buyuk | 50 | 0.0 | 2.0 | 100.0 | 100.0 |
| eksi | 30 | 0.0 | 80.0 | 100.0 | 100.0 |
| kardinal | 100 | 16.0 | 72.0 | 100.0 | 99.0 |
| karisik | 60 | 0.0 | 53.3 | 100.0 | 100.0 |
| kod | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_dogal | 180 | 100.0 | 98.9 | 100.0 | 100.0 |
| negatif_es | 200 | 100.0 | 30.0 | 98.5 | 100.0 |
| negatif_kalip | 220 | 100.0 | 30.9 | 100.0 | 100.0 |
| negatif_yazili | 160 | 100.0 | 93.1 | 100.0 | 100.0 |
| olcu | 160 | 0.0 | 64.4 | 100.0 | 100.0 |
| ondalik | 60 | 0.0 | 93.3 | 100.0 | 100.0 |
| para | 140 | 0.0 | 87.9 | 100.0 | 100.0 |
| saat | 130 | 0.0 | 33.1 | 100.0 | 100.0 |
| sira | 70 | 0.0 | 75.7 | 100.0 | 100.0 |
| skor | 50 | 0.0 | 0.0 | 100.0 | 100.0 |
| tarih | 120 | 0.0 | 4.2 | 100.0 | 100.0 |
| telefon | 60 | 0.0 | 0.0 | 95.0 | 95.0 |
| yuzde | 100 | 0.0 | 97.0 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 4 hata, ilk 4 gösterilir)

```text
[telefon/telefon-001]
GİRDİ: telefon numaram sıfır üç yüz yirmi iki yedi yüz otuz dört dokuz kırk dokuz
ÇIKTI: telefon numaram 0322 734 94 49
HEDEF: telefon numaram 0322 730 49 49
```

```text
[kardinal/kardinal-033]
GİRDİ: ben de xbox onu aldım
ÇIKTI: ben de xbox onu aldım
HAM  : ben de xbox 10'u aldım
HEDEF: ben de xbox 10'u aldım
```

```text
[telefon/telefon-001]
GİRDİ: Telefon numaram artı doksan beş yüz elli beş yüz yetmiş altı elli dört yirmi altı.
ÇIKTI: Telefon numaram +90 555 576 54 26.
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
| Model + koruma | 83 | 91.6 | 2.1 | 3.1 | 97.6 | 18.5 (27) |

Koruma 1 örnekte en az bir bölgeyi geri aldı.

### Kategori kırılımı

| Kategori | n | Girdiyi kopyala (tam %) | Kural tabanlı (saf) (tam %) | Model (korumasız) (tam %) | Model + koruma (tam %) |
|---|---:|---:|---:|---:|---:|
| aralik | 3 | 0.0 | 0.0 | 100.0 | 100.0 |
| ayin_gunu | 4 | 0.0 | 100.0 | 100.0 | 100.0 |
| bilesik | 4 | 0.0 | 100.0 | 100.0 | 100.0 |
| bitisik | 5 | 0.0 | 0.0 | 100.0 | 100.0 |
| ic_sifir | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| kardinal | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| karisik | 3 | 0.0 | 0.0 | 33.3 | 33.3 |
| karsit | 2 | 0.0 | 50.0 | 100.0 | 100.0 |
| kod | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| negatif_es | 7 | 100.0 | 28.6 | 57.1 | 71.4 |
| negatif_kalip | 17 | 100.0 | 41.2 | 88.2 | 88.2 |
| negatif_politika | 2 | 100.0 | 0.0 | 50.0 | 50.0 |
| olcu | 7 | 0.0 | 57.1 | 100.0 | 100.0 |
| saat_deyis | 6 | 0.0 | 100.0 | 100.0 | 100.0 |
| telefon | 2 | 0.0 | 0.0 | 100.0 | 100.0 |
| yari | 12 | 8.3 | 8.3 | 100.0 | 100.0 |

### Hata örnekleri (model_korumali; toplam 7 hata, ilk 7 gösterilir)

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
