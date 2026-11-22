# Gerçek metin ölçümü — v3-base-best-k2

Küme: `evaluation/gercek2.jsonl`, 150 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 64.0 | 64.7 | 0.0 (96) | 1.9 (54) | 53 |
| Kural tabanlı (saf) | 29.3 | 36.7 | 71.9 (96) | 51.9 (54) | 0 |
| Model (korumasız) | 92.7 | 94.0 | 4.2 (96) | 90.7 (54) | 2 |
| Model + koruma | 93.3 | 94.7 | 3.1 (96) | 90.7 (54) | 3 |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 0 | 13 | 13 |
| atasozu | 9 | 9 | 0 | 7 | 7 |
| buyuk | 1 | 0 | 0 | 1 | 1 |
| es_yazim | 25 | 25 | 16 | 25 | 25 |
| kalip | 26 | 26 | 5 | 26 | 26 |
| kardinal | 19 | 0 | 15 | 18 | 18 |
| kucuk_sayi | 14 | 14 | 5 | 12 | 13 |
| para | 8 | 0 | 5 | 7 | 7 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 4 | 3 | 3 | 3 | 3 |
| tarih | 7 | 0 | 4 | 7 | 7 |
| zamir | 20 | 20 | 0 | 20 | 20 |

## Model hataları (9; ham ya da korumalı çıktı yanlış)

```text
[8 · sira]
GİRDİ: On ikinci maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra yetmiş yıldır.
HAM  : 12. maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
HEDEF: 12. maddenin 1. fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
```

```text
[17 · para]
GİRDİ: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HAM  : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, 150şerden 3 TL…"
KORU : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HEDEF: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden 3 TL…"
```

```text
[25 · kucuk_sayi]
GİRDİ: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
HAM  : Bir, iki, üç, dört, beş, altı, yedi, sekiz, on.
KORU : Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
HEDEF: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
```

```text
[48 · atasozu]
GİRDİ: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HAM  : Soğuk; 40 kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HEDEF: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
```

```text
[51 · kardinal]
GİRDİ: İçeri kırk yaşlarında, kesik saçları kulaklarına ve yüzüne dökülmüş, şişmanca bir kadın girdi.
HAM  : İçeri kırk yaşlarında, kesik saçları kulaklarına ve yüzüne dökülmüş, şişmanca bir kadın girdi.
HEDEF: İçeri 40 yaşlarında, kesik saçları kulaklarına ve yüzüne dökülmüş, şişmanca bir kadın girdi.
```

```text
[55 · aralik]
GİRDİ: Ders verdiği yedi çocuk ellerinde çantaları ile beş on adım ilerden gidiyorlardı.
HAM  : Ders verdiği yedi çocuk ellerinde çantaları ile beş 10 adım ilerden gidiyorlardı.
HEDEF: Ders verdiği yedi çocuk ellerinde çantaları ile 5-10 adım ilerden gidiyorlardı.
```

```text
[69 · aralik]
GİRDİ: Sonra da burun kanamadan, üç dört kişiden alamayacağın bir para…
HAM  : Sonra da burun kanamadan, üç dört kişiden alamayacağın bir para…
HEDEF: Sonra da burun kanamadan, 3-4 kişiden alamayacağın bir para…
```

```text
[73 · atasozu]
GİRDİ: Nereye gitsen okka dört yüz dirhem.
HAM  : Nereye gitsen okka 400 dirhem.
HEDEF: Nereye gitsen okka dört yüz dirhem.
```

```text
[106 · kucuk_sayi]
GİRDİ: Ve sazını, iki kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
HAM  : Ve sazını, 2 kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
HEDEF: Ve sazını, iki kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
```
