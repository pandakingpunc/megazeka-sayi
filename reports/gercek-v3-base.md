# Gerçek metin ölçümü — v3-base

Küme: `evaluation/gercek.jsonl`, 279 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 58.4 | 59.9 | 0.0 (163) | 3.4 (116) | 112 |
| Kural tabanlı (saf) | 34.8 | 40.9 | 71.2 (163) | 57.8 (116) | 1 |
| Model (korumasız) | 94.6 | 95.0 | 3.7 (163) | 93.1 (116) | 8 |
| Model + koruma | 95.0 | 95.3 | 3.1 (163) | 93.1 (116) | 8 |

Koruma 1 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 17 | 0 | 0 | 16 | 16 |
| atasozu | 12 | 12 | 0 | 7 | 7 |
| buyuk | 8 | 0 | 0 | 7 | 7 |
| es_yazim | 35 | 35 | 19 | 35 | 35 |
| kalip | 53 | 53 | 18 | 52 | 53 |
| kardinal | 45 | 1 | 42 | 39 | 39 |
| kucuk_sayi | 30 | 30 | 10 | 30 | 30 |
| olcu | 4 | 0 | 2 | 4 | 4 |
| ondalik | 5 | 0 | 5 | 5 | 5 |
| para | 20 | 2 | 9 | 20 | 20 |
| saat | 4 | 0 | 2 | 4 | 4 |
| sira | 4 | 4 | 1 | 4 | 4 |
| tarih | 12 | 0 | 6 | 12 | 12 |
| zamir | 30 | 30 | 0 | 30 | 30 |

## Model hataları (14; ham ya da korumalı çıktı yanlış)

```text
[21 · kardinal]
GİRDİ: Ayın en çok on gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HAM  : Ayın en çok on gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HEDEF: Ayın en çok 10 gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
```

```text
[31 · buyuk]
GİRDİ: Bu iki milyon esir bu geceyi bekliyorlar değil mi?
HAM  : Bu iki milyon esir bu geceyi bekliyorlar değil mi?
HEDEF: Bu 2 milyon esir bu geceyi bekliyorlar değil mi?
```

```text
[42 · kardinal]
GİRDİ: Yol parası vermeyenlerle beraber beni de aldılar; ben seksen yaşındayım dedim ama, dinleyen olmadı.
HAM  : Yol parası vermeyenlerle beraber beni de aldılar; ben seksen yaşındayım dedim ama, dinleyen olmadı.
HEDEF: Yol parası vermeyenlerle beraber beni de aldılar; ben 80 yaşındayım dedim ama, dinleyen olmadı.
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
[116 · kardinal]
GİRDİ: "Kırk yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
HAM  : "Kırk yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
HEDEF: "40 yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
```

```text
[118 · kardinal]
GİRDİ: Sen bu usulü daha ziyade kırkını geçmiş memurlarla, lise talebesine tatbik edecektin.
HAM  : Sen bu usulü daha ziyade kırkını geçmiş memurlarla, lise talebesine tatbik edecektin.
HEDEF: Sen bu usulü daha ziyade 40'ını geçmiş memurlarla, lise talebesine tatbik edecektin.
```

```text
[147 · kardinal]
GİRDİ: Oyuncuların kağıtlarına bakarak: "Koz çek, yirmiyi söyle" diye karışmaya başlamış.
HAM  : Oyuncuların kağıtlarına bakarak: "Koz çek, yirmiyi söyle" diye karışmaya başlamış.
HEDEF: Oyuncuların kağıtlarına bakarak: "Koz çek, 20'yi söyle" diye karışmaya başlamış.
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
[167 · atasozu]
GİRDİ: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
HAM  : 1.000 atın varsa inişte in, bir atın varsa yokuşta bin.
HEDEF: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
```

```text
[179 · aralik]
GİRDİ: Ben iki üç akşamda bir uğruyor ve her defasında onu biraz daha çökmüş buluyordum.
HAM  : Ben iki üç akşamda bir uğruyor ve her defasında onu biraz daha çökmüş buluyordum.
HEDEF: Ben 2-3 akşamda bir uğruyor ve her defasında onu biraz daha çökmüş buluyordum.
```
