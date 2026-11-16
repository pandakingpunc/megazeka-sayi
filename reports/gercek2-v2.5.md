# Gerçek metin ölçümü — v3-small

Küme: `evaluation/gercek2.jsonl`, 150 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 64.0 | 64.7 | 0.0 (96) | 1.9 (54) | 53 |
| Kural tabanlı (saf) | 29.3 | 36.7 | 71.9 (96) | 51.9 (54) | 0 |
| Model (korumasız) | 90.0 | 92.0 | 6.2 (96) | 88.9 (54) | 1 |
| Model + koruma | 91.3 | 93.3 | 5.2 (96) | 90.7 (54) | 2 |

Koruma 3 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 0 | 12 | 13 |
| atasozu | 9 | 9 | 0 | 4 | 4 |
| buyuk | 1 | 0 | 0 | 1 | 1 |
| es_yazim | 25 | 25 | 16 | 25 | 25 |
| kalip | 26 | 26 | 5 | 26 | 26 |
| kardinal | 19 | 0 | 15 | 19 | 19 |
| kucuk_sayi | 14 | 14 | 5 | 13 | 14 |
| para | 8 | 0 | 5 | 6 | 6 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 4 | 3 | 3 | 3 | 3 |
| tarih | 7 | 0 | 4 | 7 | 7 |
| zamir | 20 | 20 | 0 | 20 | 20 |

## Model hataları (12; ham ya da korumalı çıktı yanlış)

```text
[2 · para]
GİRDİ: Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HAM  : Bankada 80,100.000 TL olduğu herkesçe muhakkak sayılırdı.
HEDEF: Bankada 80, 100.000 TL'si olduğu herkesçe muhakkak sayılırdı.
```

```text
[8 · sira]
GİRDİ: On ikinci maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra yetmiş yıldır.
HAM  : 12. maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
HEDEF: 12. maddenin 1. fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
```

```text
[17 · para]
GİRDİ: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HAM  : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, 150 TL…"
KORU : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HEDEF: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden 3 TL…"
```

```text
[25 · kucuk_sayi]
GİRDİ: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
HAM  : Bir, iki, 3, 4, 5, 6, 7, 8, 10.
KORU : Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
HEDEF: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
```

```text
[28 · atasozu]
GİRDİ: Adı çıktı dokuza, inmez sekize.
HAM  : Adı çıktı 9'a, inmez 8'e.
HEDEF: Adı çıktı dokuza, inmez sekize.
```

```text
[31 · aralik]
GİRDİ: Hiç de on yedi on sekizden yukarı göstermiyordu.
HAM  : Hiç de 17.18'den yukarı göstermiyordu.
HEDEF: Hiç de 17-18'den yukarı göstermiyordu.
```

```text
[48 · atasozu]
GİRDİ: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HAM  : Soğuk; 40 kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HEDEF: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
```

```text
[49 · atasozu]
GİRDİ: Ayının bildiği kırk türkü, kırkı da armut üstüne…
HAM  : Ayının bildiği 40 türkü, 40'ı da armut üstüne…
HEDEF: Ayının bildiği kırk türkü, kırkı da armut üstüne…
```

```text
[50 · atasozu]
GİRDİ: Baban bana öğüt verirken, ben inek gözünde kırk sinek saydım.
HAM  : Baban bana öğüt verirken, ben inek gözünde 40 sinek saydım.
HEDEF: Baban bana öğüt verirken, ben inek gözünde kırk sinek saydım.
```

```text
[61 · aralik]
GİRDİ: Onun kenarını takip ederek on beş yirmi adım daha gidince önü birdenbire açıldı.
HAM  : Onun kenarını takip ederek 15-20 adım daha gidince önü 1'denbire açıldı.
KORU : Onun kenarını takip ederek 15-20 adım daha gidince önü birdenbire açıldı.
HEDEF: Onun kenarını takip ederek 15-20 adım daha gidince önü birdenbire açıldı.
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
