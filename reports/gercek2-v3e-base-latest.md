# Gerçek metin ölçümü — v3e-base-latest

Küme: `evaluation/gercek2.jsonl`, 150 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 64.0 | 64.7 | 0.0 (96) | 1.9 (54) | 53 |
| Kural tabanlı (saf) | 29.3 | 36.7 | 71.9 (96) | 51.9 (54) | 0 |
| Model (korumasız) | 94.7 | 96.7 | 2.1 (96) | 94.4 (54) | 1 |
| Model + koruma | 94.7 | 96.7 | 2.1 (96) | 94.4 (54) | 1 |

Koruma 0 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 0 | 14 | 14 |
| atasozu | 9 | 9 | 0 | 7 | 7 |
| buyuk | 1 | 0 | 0 | 1 | 1 |
| es_yazim | 25 | 25 | 16 | 25 | 25 |
| kalip | 26 | 26 | 5 | 26 | 26 |
| kardinal | 19 | 0 | 15 | 19 | 19 |
| kucuk_sayi | 14 | 14 | 5 | 14 | 14 |
| para | 8 | 0 | 5 | 6 | 6 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 4 | 3 | 3 | 4 | 4 |
| tarih | 7 | 0 | 4 | 7 | 7 |
| zamir | 20 | 20 | 0 | 20 | 20 |

## Model hataları (5; ham ya da korumalı çıktı yanlış)

```text
[2 · para]
GİRDİ: Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HAM  : Bankada 80,100.000 TL'si olduğu herkesçe muhakkak sayılırdı.
HEDEF: Bankada 80, 100.000 TL'si olduğu herkesçe muhakkak sayılırdı.
```

```text
[17 · para]
GİRDİ: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HAM  : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HEDEF: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden 3 TL…"
```

```text
[48 · atasozu]
GİRDİ: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HAM  : Soğuk; 40 kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
HEDEF: Soğuk; kırk kat keçe, ben ondan geçe; bir kat deri, ben ondan geri demiş.
```

```text
[55 · aralik]
GİRDİ: Ders verdiği yedi çocuk ellerinde çantaları ile beş on adım ilerden gidiyorlardı.
HAM  : Ders verdiği 7 çocuk ellerinde çantaları ile 5-10 adım ilerden gidiyorlardı.
HEDEF: Ders verdiği yedi çocuk ellerinde çantaları ile 5-10 adım ilerden gidiyorlardı.
```

```text
[73 · atasozu]
GİRDİ: Nereye gitsen okka dört yüz dirhem.
HAM  : Nereye gitsen okka 400 dirhem.
HEDEF: Nereye gitsen okka dört yüz dirhem.
```
