# Gerçek metin ölçümü — v3e-base-best

Küme: `evaluation/gercek.jsonl`, 279 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 58.4 | 59.9 | 0.0 (163) | 3.4 (116) | 112 |
| Kural tabanlı (saf) | 34.8 | 40.9 | 71.2 (163) | 57.8 (116) | 1 |
| Model (korumasız) | 94.3 | 95.3 | 5.5 (163) | 96.6 (116) | 4 |
| Model + koruma | 95.0 | 96.1 | 4.3 (163) | 96.6 (116) | 4 |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 17 | 0 | 0 | 17 | 17 |
| atasozu | 12 | 12 | 0 | 7 | 7 |
| buyuk | 8 | 0 | 0 | 7 | 7 |
| es_yazim | 35 | 35 | 19 | 35 | 35 |
| kalip | 53 | 53 | 18 | 51 | 52 |
| kardinal | 45 | 1 | 42 | 43 | 43 |
| kucuk_sayi | 30 | 30 | 10 | 29 | 29 |
| olcu | 4 | 0 | 2 | 4 | 4 |
| ondalik | 5 | 0 | 5 | 4 | 4 |
| para | 20 | 2 | 9 | 20 | 20 |
| saat | 4 | 0 | 2 | 4 | 4 |
| sira | 4 | 4 | 1 | 4 | 4 |
| tarih | 12 | 0 | 6 | 12 | 12 |
| zamir | 30 | 30 | 0 | 29 | 30 |

## Model hataları (13; ham ya da korumalı çıktı yanlış)

```text
[2 · kalip]
GİRDİ: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
HAM  : Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu 2 çeyrek yapsana!"
HEDEF: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
```

```text
[8 · kucuk_sayi]
GİRDİ: Elde var sıfır.
HAM  : Elde var 0.
HEDEF: Elde var sıfır.
```

```text
[14 · ondalik]
GİRDİ: Daha bir buçuk ay önce aslanlar gibi kardeşimi öldürdü.
HAM  : Daha bir buçuk ay önce aslanlar gibi kardeşimi öldürdü.
HEDEF: Daha 1,5 ay önce aslanlar gibi kardeşimi öldürdü.
```

```text
[21 · kardinal]
GİRDİ: Ayın en çok on gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HAM  : Ayın en çok on gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HEDEF: Ayın en çok 10 gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
```

```text
[33 · buyuk]
GİRDİ: Bir milyon mu?
HAM  : Bir milyon mu?
HEDEF: 1 milyon mu?
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
[96 · atasozu]
GİRDİ: Hırsız sekiz, köşe dokuz.
HAM  : Hırsız 8, köşe dokuz.
HEDEF: Hırsız sekiz, köşe dokuz.
```

```text
[113 · atasozu]
GİRDİ: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
HAM  : Dervişlik olaydı taç ile hırka, ben de alırdım 30'a 40'a.
HEDEF: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
```

```text
[163 · kalip]
GİRDİ: Bin dert vardı başında.
HAM  : 1.004 vardı başında.
KORU : Bin dert vardı başında.
HEDEF: Bin dert vardı başında.
```

```text
[165 · kardinal]
GİRDİ: Belki bini de aşar.
HAM  : Belki bini de aşar.
HEDEF: Belki 1.000'i de aşar.
```

```text
[243 · zamir]
GİRDİ: Bir müddet onu seyrettiler.
HAM  : Bir müddet 10'u seyrettiler.
KORU : Bir müddet onu seyrettiler.
HEDEF: Bir müddet onu seyrettiler.
```
