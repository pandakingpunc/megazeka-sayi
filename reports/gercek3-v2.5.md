# Gerçek metin ölçümü — v2.5

Küme: `evaluation/gercek3.jsonl`, 198 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 60.6 | 63.1 | 0.0 (120) | 6.4 (78) | 73 |
| Kural tabanlı (saf) | 27.8 | 34.3 | 76.7 (120) | 51.3 (78) | 1 |
| Model (korumasız) | 88.4 | 91.9 | 9.2 (120) | 93.6 (78) | 3 |
| Model + koruma | 88.9 | 92.4 | 9.2 (120) | 94.9 (78) | 3 |

Koruma 2 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 1 | 13 | 13 |
| atasozu | 22 | 22 | 0 | 15 | 15 |
| es_yazim | 22 | 22 | 10 | 22 | 22 |
| kalip | 48 | 48 | 7 | 44 | 44 |
| kardinal | 38 | 3 | 28 | 36 | 36 |
| kucuk_sayi | 20 | 20 | 10 | 20 | 20 |
| olcu | 1 | 0 | 1 | 1 | 1 |
| para | 15 | 0 | 7 | 15 | 15 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 3 | 3 | 1 | 2 | 3 |
| tarih | 5 | 0 | 1 | 5 | 5 |
| zamir | 7 | 7 | 0 | 7 | 7 |

## Model hataları (16; ham ya da korumalı çıktı yanlış)

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
HAM  : Doktor Mutena Cankurtaran 35'lik, sarı kıvırcık saçlı, altın gözlüklü, kibar halli 1'iydi.
KORU : Doktor Mutena Cankurtaran 35'lik, sarı kıvırcık saçlı, altın gözlüklü, kibar halli biriydi.
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
[40 · atasozu]
GİRDİ: Bir koyun başı pişinceye kadar, kırk kuzu başı pişer.
HAM  : Bir koyun başı pişinceye kadar, 40 kuzu başı pişer.
HEDEF: Bir koyun başı pişinceye kadar, kırk kuzu başı pişer.
```

```text
[48 · kardinal]
GİRDİ: Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "Kırk sene kahrını çektim…"
HAM  : Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "Kırk sene kahrını çektim…"
HEDEF: Hacer kadın, aradığını bulamadığına kızmışa benziyordu: "40 sene kahrını çektim…"
```

```text
[49 · atasozu]
GİRDİ: Boğaz dokuz boğumdur.
HAM  : Boğaz 9 boğumdur.
HEDEF: Boğaz dokuz boğumdur.
```

```text
[56 · atasozu]
GİRDİ: Mart dokuzunda çıra yak, bağ buda.
HAM  : Mart 9'unda çıra yak, bağ buda.
HEDEF: Mart dokuzunda çıra yak, bağ buda.
```

```text
[71 · sira]
GİRDİ: Nihayet, yirmi beşinci günü, onu kürküne sardım, koluna girerek merdivenlerden indirdim.
HAM  : Nihayet, 25. günü, 10'u kürküne sardım, koluna girerek merdivenlerden indirdim.
KORU : Nihayet, 25. günü, onu kürküne sardım, koluna girerek merdivenlerden indirdim.
HEDEF: Nihayet, 25. günü, onu kürküne sardım, koluna girerek merdivenlerden indirdim.
```

```text
[87 · aralik]
GİRDİ: Melek yavaşça elindeki çantayı açtı, içinden dört beş altın bilezikle bir çift küpe aldı.
HAM  : Melek yavaşça elindeki çantayı açtı, içinden dört beş altın bilezikle bir çift küpe aldı.
HEDEF: Melek yavaşça elindeki çantayı açtı, içinden 4-5 altın bilezikle bir çift küpe aldı.
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
[155 · kardinal]
GİRDİ: On sene mi?
HAM  : On sene mi?
HEDEF: 10 sene mi?
```

```text
[159 · atasozu]
GİRDİ: On para on arslanın ağzında.
HAM  : 10 para 10 arslanın ağzında.
HEDEF: On para on arslanın ağzında.
```

```text
[167 · kalip]
GİRDİ: O zaman on para kıymeti olmazdı.
HAM  : O zaman 10 para kıymeti olmazdı.
HEDEF: O zaman on para kıymeti olmazdı.
```
