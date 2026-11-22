# Gerçek metin ölçümü — v3e-base-best

Küme: `evaluation/gercek2.jsonl`, 150 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 64.0 | 64.7 | 0.0 (96) | 1.9 (54) | 53 |
| Kural tabanlı (saf) | 29.3 | 36.7 | 71.9 (96) | 51.9 (54) | 0 |
| Model (korumasız) | 92.0 | 94.7 | 5.2 (96) | 94.4 (54) | 0 |
| Model + koruma | 92.0 | 94.7 | 5.2 (96) | 94.4 (54) | 1 |

Koruma 1 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 0 | 14 | 14 |
| atasozu | 9 | 9 | 0 | 5 | 5 |
| buyuk | 1 | 0 | 0 | 1 | 1 |
| es_yazim | 25 | 25 | 16 | 25 | 25 |
| kalip | 26 | 26 | 5 | 26 | 26 |
| kardinal | 19 | 0 | 15 | 19 | 19 |
| kucuk_sayi | 14 | 14 | 5 | 13 | 13 |
| para | 8 | 0 | 5 | 6 | 6 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 4 | 3 | 3 | 4 | 4 |
| tarih | 7 | 0 | 4 | 7 | 7 |
| zamir | 20 | 20 | 0 | 20 | 20 |

## Model hataları (8; ham ya da korumalı çıktı yanlış)

```text
[2 · para]
GİRDİ: Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HAM  : Bankada 80,100 TL'si olduğu herkesçe muhakkak sayılırdı.
KORU : Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HEDEF: Bankada 80, 100.000 TL'si olduğu herkesçe muhakkak sayılırdı.
```

```text
[17 · para]
GİRDİ: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HAM  : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç TL…"
HEDEF: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden 3 TL…"
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
HAM  : Ayının bildiği 40 TL'ü, 40'ı da armut üstüne…
HEDEF: Ayının bildiği kırk türkü, kırkı da armut üstüne…
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
