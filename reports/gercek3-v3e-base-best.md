# Gerçek metin ölçümü — v3e-base-best

Küme: `evaluation/gercek3.jsonl`, 198 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 60.6 | 63.1 | 0.0 (120) | 6.4 (78) | 73 |
| Kural tabanlı (saf) | 27.8 | 34.3 | 76.7 (120) | 51.3 (78) | 1 |
| Model (korumasız) | 91.9 | 93.9 | 6.7 (120) | 94.9 (78) | 2 |
| Model + koruma | 91.9 | 94.4 | 6.7 (120) | 96.2 (78) | 2 |

Koruma 1 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 1 | 14 | 14 |
| atasozu | 22 | 22 | 0 | 18 | 18 |
| es_yazim | 22 | 22 | 10 | 22 | 22 |
| kalip | 48 | 48 | 7 | 44 | 44 |
| kardinal | 38 | 3 | 28 | 35 | 36 |
| kucuk_sayi | 20 | 20 | 10 | 20 | 20 |
| olcu | 1 | 0 | 1 | 1 | 1 |
| para | 15 | 0 | 7 | 15 | 15 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 3 | 3 | 1 | 3 | 3 |
| tarih | 5 | 0 | 1 | 5 | 5 |
| zamir | 7 | 7 | 0 | 7 | 7 |

## Model hataları (12; ham ya da korumalı çıktı yanlış)

```text
[10 · atasozu]
GİRDİ: Kasım yüz elli, yaz belli.
HAM  : Kasım 150, yaz belli.
HEDEF: Kasım yüz elli, yaz belli.
```

```text
[19 · kalip]
GİRDİ: Birdenbire bu otuz beşlik kadının acıkmış dudaklarını yüzümde hissettim.
HAM  : Birdenbire bu 35'lik kadının acıkmış dudaklarını yüzümde hissettim.
HEDEF: Birdenbire bu otuz beşlik kadının acıkmış dudaklarını yüzümde hissettim.
```

```text
[22 · kalip]
GİRDİ: Doktor Mutena Cankurtaran otuz beşlik, sarı kıvırcık saçlı, altın gözlüklü, kibar halli biriydi.
HAM  : Doktor Mutena Cankurtaran 35'lik, sarı kıvırcık saçlı, altın gözlüklü, kibar halli biriydi.
HEDEF: Doktor Mutena Cankurtaran otuz beşlik, sarı kıvırcık saçlı, altın gözlüklü, kibar halli biriydi.
```

```text
[31 · aralik]
GİRDİ: Hele Çirkince… Hele bu yedi, sekiz yüz hanelik dağ köyü…
HAM  : Hele Çirkince… Hele bu yedi, 800 hanelik dağ köyü…
HEDEF: Hele Çirkince… Hele bu 7, 800 hanelik dağ köyü…
```

```text
[39 · atasozu]
GİRDİ: Sarımsağı gelin etmişler, kırk gün kokusu çıkmamış.
HAM  : Sarımsağı gelin etmişler, 40 gün kokusu çıkmamış.
HEDEF: Sarımsağı gelin etmişler, kırk gün kokusu çıkmamış.
```

```text
[48 · kardinal]
GİRDİ: Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "Kırk sene kahrını çektim…"
HAM  : Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "Kırk sene kahrını çektim…"
HEDEF: Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "40 sene kahrını çektim…"
```

```text
[56 · atasozu]
GİRDİ: Mart dokuzunda çıra yak, bağ buda.
HAM  : Mart 9'unda çıra yak, bağ buda.
HEDEF: Mart dokuzunda çıra yak, bağ buda.
```

```text
[91 · kardinal]
GİRDİ: Mest etmişti bin kazı.
HAM  : Mest 70'ti bin kazı.
KORU : Mest etmişti bin kazı.
HEDEF: Mest etmişti 1.000 kazı.
```

```text
[106 · kalip]
GİRDİ: Çoluk çocuk dört bir yanımda dolaşır.
HAM  : Çoluk çocuk 4-1 yanımda dolaşır.
HEDEF: Çoluk çocuk dört bir yanımda dolaşır.
```

```text
[128 · atasozu]
GİRDİ: Ağustosun on beşinden sonra ere kaftan, ata çul.
HAM  : Ağustosun 15'inden sonra ere kaftan, ata çul.
HEDEF: Ağustosun on beşinden sonra ere kaftan, ata çul.
```

```text
[152 · kardinal]
GİRDİ: On gündür de rıhtımda bekliyor, bu sabah mavnaya yüklettim, nerdeyse gemiye yanaşmıştır!
HAM  : On gündür de rıhtımda bekliyor, bu sabah mavnaya yüklettim, nerdeyse gemiye yanaşmıştır!
HEDEF: 10 gündür de rıhtımda bekliyor, bu sabah mavnaya yüklettim, nerdeyse gemiye yanaşmıştır!
```

```text
[167 · kalip]
GİRDİ: O zaman on para kıymeti olmazdı.
HAM  : O zaman 10 para kıymeti olmazdı.
HEDEF: O zaman on para kıymeti olmazdı.
```
