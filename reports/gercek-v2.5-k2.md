# Gerçek metin ölçümü — v2.5-k2

Küme: `evaluation/gercek.jsonl`, 279 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 58.4 | 59.9 | 0.0 (163) | 3.4 (116) | 112 |
| Kural tabanlı (saf) | 34.8 | 40.9 | 71.2 (163) | 57.8 (116) | 1 |
| Model (korumasız) | 93.9 | 95.0 | 5.5 (163) | 95.7 (116) | 4 |
| Model + koruma | 94.6 | 95.7 | 4.9 (163) | 96.6 (116) | 4 |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 17 | 0 | 0 | 17 | 17 |
| atasozu | 12 | 12 | 0 | 7 | 7 |
| buyuk | 8 | 0 | 0 | 7 | 7 |
| es_yazim | 35 | 35 | 19 | 35 | 35 |
| kalip | 53 | 53 | 18 | 50 | 51 |
| kardinal | 45 | 1 | 42 | 41 | 42 |
| kucuk_sayi | 30 | 30 | 10 | 29 | 29 |
| olcu | 4 | 0 | 2 | 4 | 4 |
| ondalik | 5 | 0 | 5 | 5 | 5 |
| para | 20 | 2 | 9 | 20 | 20 |
| saat | 4 | 0 | 2 | 4 | 4 |
| sira | 4 | 4 | 1 | 4 | 4 |
| tarih | 12 | 0 | 6 | 12 | 12 |
| zamir | 30 | 30 | 0 | 30 | 30 |

## Model hataları (14; ham ya da korumalı çıktı yanlış)

```text
[2 · kalip]
GİRDİ: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
HAM  : Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu 2 çeyrek yapsana!"
HEDEF: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
```

```text
[33 · buyuk]
GİRDİ: Bir milyon mu?
HAM  : Bir milyon mu?
HEDEF: 1 milyon mu?
```

```text
[46 · kardinal]
GİRDİ: Onun sırtına giyeceği yoktu ve mal sahibi seksen kat üst üste giyebilirdi.
HAM  : 10'un sırtına giyeceği yoktu ve mal sahibi 80 kat üst üste giyebilirdi.
KORU : Onun sırtına giyeceği yoktu ve mal sahibi 80 kat üst üste giyebilirdi.
HEDEF: Onun sırtına giyeceği yoktu ve mal sahibi 80 kat üst üste giyebilirdi.
```

```text
[60 · atasozu]
GİRDİ: Yaş yetmiş, iş bitmiş.
HAM  : Yaş 70, iş bitmiş.
HEDEF: Yaş yetmiş, iş bitmiş.
```

```text
[68 · atasozu]
GİRDİ: Yerinden oynayan yetmiş kazaya uğrar; en küçüğü ölüm.
HAM  : Yerinden oynayan 70 kazaya uğrar; en küçüğü ölüm.
HEDEF: Yerinden oynayan yetmiş kazaya uğrar; en küçüğü ölüm.
```

```text
[87 · atasozu]
GİRDİ: Otuz iki dişten çıkan, otuz iki mahalleye yayılır.
HAM  : 32 dişten çıkan, 32 mahalleye yayılır.
HEDEF: Otuz iki dişten çıkan, otuz iki mahalleye yayılır.
```

```text
[113 · atasozu]
GİRDİ: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
HAM  : Dervişlik olaydı taç ile hırka, ben de alırdım 30'a 40'a.
HEDEF: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
```

```text
[118 · kardinal]
GİRDİ: Sen bu usulü daha ziyade kırkını geçmiş memurlarla, lise talebesine tatbik edecektin.
HAM  : Sen bu usulü daha ziyade kırkını geçmiş memurlarla, lise talebesine tatbik edecektin.
HEDEF: Sen bu usulü daha ziyade 40'ını geçmiş memurlarla, lise talebesine tatbik edecektin.
```

```text
[150 · kucuk_sayi]
GİRDİ: Dört katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
HAM  : 4 katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
HEDEF: Dört katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
```

```text
[156 · kalip]
GİRDİ: Dört elle işe sarılmaya ve işsizliğin doğurduğu sıkıntılı vehimlerden bu şekilde kurtulmaya azmetmiştim.
HAM  : 4-50 işe sarılmaya ve işsizliğin doğurduğu sıkıntılı vehimlerden bu şekilde kurtulmaya azmetmiştim.
KORU : Dört elle işe sarılmaya ve işsizliğin doğurduğu sıkıntılı vehimlerden bu şekilde kurtulmaya azmetmiştim.
HEDEF: Dört elle işe sarılmaya ve işsizliğin doğurduğu sıkıntılı vehimlerden bu şekilde kurtulmaya azmetmiştim.
```

```text
[158 · kardinal]
GİRDİ: Hadi, sen durma, köyüne git, dört yüzü tamamla…
HAM  : Hadi, sen durma, köyüne git, dört yüzü tamamla…
HEDEF: Hadi, sen durma, köyüne git, 400'ü tamamla…
```

```text
[163 · kalip]
GİRDİ: Bin dert vardı başında.
HAM  : 1.000 dert vardı başında.
HEDEF: Bin dert vardı başında.
```

```text
[165 · kardinal]
GİRDİ: Belki bini de aşar.
HAM  : Belki bini de aşar.
HEDEF: Belki 1.000'i de aşar.
```

```text
[167 · atasozu]
GİRDİ: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
HAM  : 1.000 atın varsa inişte in, bir atın varsa yokuşta bin.
HEDEF: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
```
