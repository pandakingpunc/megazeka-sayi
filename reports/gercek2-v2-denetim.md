# Gerçek metin ölçümü — v2-denetim

Küme: `evaluation/gercek2.jsonl`, 150 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 64.0 | 64.7 | 0.0 (96) | 1.9 (54) | 53 |
| Kural tabanlı (saf) | 29.3 | 36.7 | 71.9 (96) | 51.9 (54) | 0 |
| Model (korumasız) | 80.0 | 82.7 | 18.8 (96) | 85.2 (54) | 0 |
| Model + koruma | 88.0 | 90.7 | 9.4 (96) | 90.7 (54) | 2 |

Koruma 7 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 15 | 0 | 0 | 12 | 14 |
| atasozu | 9 | 9 | 0 | 4 | 4 |
| buyuk | 1 | 0 | 0 | 1 | 1 |
| es_yazim | 25 | 25 | 16 | 23 | 24 |
| kalip | 26 | 26 | 5 | 23 | 26 |
| kardinal | 19 | 0 | 15 | 17 | 18 |
| kucuk_sayi | 14 | 14 | 5 | 11 | 11 |
| para | 8 | 0 | 5 | 6 | 6 |
| saat | 2 | 0 | 2 | 2 | 2 |
| sira | 4 | 3 | 3 | 3 | 3 |
| tarih | 7 | 0 | 4 | 7 | 7 |
| zamir | 20 | 20 | 0 | 15 | 20 |

## Model hataları (26; ham ya da korumalı çıktı yanlış)

```text
[2 · para]
GİRDİ: Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HAM  : Bankada 80-1.000 TL olduğu herkesçe muhakkak sayılırdı.
KORU : Bankada seksen, yüz bin lirası olduğu herkesçe muhakkak sayılırdı.
HEDEF: Bankada 80, 100.000 TL'si olduğu herkesçe muhakkak sayılırdı.
```

```text
[8 · sira]
GİRDİ: On ikinci maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra yetmiş yıldır.
HAM  : 12. maddenin birinci fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
HEDEF: 12. maddenin 1. fıkrasındaki hallerde koruma süresi, eserin aleniyet tarihinden sonra 70 yıldır.
```

```text
[15 · kardinal]
GİRDİ: O zaman iki Mehmetler, aralarında yüz elli adım mesafe olduğu halde, birbirlerine şöyle bakıştılar.
HAM  : O zaman 2 Mehmetler, aralarında 150 adım mesafe olduğu halde, birbirlerine şöyle bakıştılar.
HEDEF: O zaman iki Mehmetler, aralarında 150 adım mesafe olduğu halde, birbirlerine şöyle bakıştılar.
```

```text
[17 · para]
GİRDİ: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HAM  : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, 150'şerden 3 TL……"
KORU : Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden üç lira…"
HEDEF: Öteki omuzlarını silkti: "İki şarap şişesi kırıldı, yüz ellişerden 3 TL…"
```

```text
[25 · kucuk_sayi]
GİRDİ: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
HAM  : 1234 567 89 10.
HEDEF: Bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz, on.
```

```text
[28 · atasozu]
GİRDİ: Adı çıktı dokuza, inmez sekize.
HAM  : Adı çıktı dokuza, inmez 8'e.
HEDEF: Adı çıktı dokuza, inmez sekize.
```

```text
[31 · aralik]
GİRDİ: Hiç de on yedi on sekizden yukarı göstermiyordu.
HAM  : Hiç de 17.18'den yukarı göstermiyordu.
HEDEF: Hiç de 17-18'den yukarı göstermiyordu.
```

```text
[46 · kardinal]
GİRDİ: Kırk okka yükle dört saatlik dağa çıkan adama eğri bakacak babayiğit bizim obamızda yoktur.
HAM  : 40 Okka yükle dört saatlik dağa çıkan adama eğri bakacak babayiğit bizim obamızda yoktur.
KORU : 40 okka yükle dört saatlik dağa çıkan adama eğri bakacak babayiğit bizim obamızda yoktur.
HEDEF: 40 okka yükle dört saatlik dağa çıkan adama eğri bakacak babayiğit bizim obamızda yoktur.
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
[50 · atasozu]
GİRDİ: Baban bana öğüt verirken, ben inek gözünde kırk sinek saydım.
HAM  : Baban bana öğüt verirken, ben inek gözünde 40 sinek saydım.
HEDEF: Baban bana öğüt verirken, ben inek gözünde kırk sinek saydım.
```

```text
[61 · aralik]
GİRDİ: Onun kenarını takip ederek on beş yirmi adım daha gidince önü birdenbire açıldı.
HAM  : 10'un kenarını takip ederek 15-20 adım daha gidince önü 1'den1'e açıldı.
KORU : Onun kenarını takip ederek 15-20 adım daha gidince önü birdenbire açıldı.
HEDEF: Onun kenarını takip ederek 15-20 adım daha gidince önü birdenbire açıldı.
```

```text
[73 · atasozu]
GİRDİ: Nereye gitsen okka dört yüz dirhem.
HAM  : Nereye gitsen okka 400 dirhem.
HEDEF: Nereye gitsen okka dört yüz dirhem.
```

```text
[87 · kucuk_sayi]
GİRDİ: Bir eylül sabahı üç ressam rıhtımda birbirleriyle göz göze gelmekten kaçınarak dolaşıyorlardı.
HAM  : 1 Eylül sabahı üç ressam rıhtımda birbirleriyle göz göze gelmekten kaçınarak dolaşıyorlardı.
HEDEF: Bir eylül sabahı üç ressam rıhtımda birbirleriyle göz göze gelmekten kaçınarak dolaşıyorlardı.
```

```text
[101 · aralik]
GİRDİ: "Büyük" meclislerde saz çalıp beş on kuruş alacağını ümit ediyordu.
HAM  : Büyük" meclislerde saz çalıp 5-10 kuruş alacağını ümit ediyordu.
KORU : "Büyük" meclislerde saz çalıp 5-10 kuruş alacağını ümit ediyordu.
HEDEF: "Büyük" meclislerde saz çalıp 5-10 kuruş alacağını ümit ediyordu.
```

```text
[106 · kucuk_sayi]
GİRDİ: Ve sazını, iki kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
HAM  : Ve sazını, 2 kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
HEDEF: Ve sazını, iki kuvvetli vuruştan sonra, yanına bırakarak başını kaldırdı.
```

```text
[110 · es_yazim]
GİRDİ: Bir müddet sabit nazarlarla yüzüne baktım, gözlerini benden çevirdi.
HAM  : 1 müddet sabit nazarlarla yüzüne baktım, gözlerini benden çevirdi.
HEDEF: Bir müddet sabit nazarlarla yüzüne baktım, gözlerini benden çevirdi.
```

```text
[111 · es_yazim]
GİRDİ: Yüzüme dikkatle baktıktan sonra, ters bir tavırla:
HAM  : Yüzüme dikkatle baktıktan sonra, ters bir tavırla.
KORU : Yüzüme dikkatle baktıktan sonra, ters bir tavırla:
HEDEF: Yüzüme dikkatle baktıktan sonra, ters bir tavırla:
```

```text
[120 · zamir]
GİRDİ: Fakat çobanı onun elinden kim kurtarabilirdi?
HAM  : Fakat çobanı 10'un elinden kim kurtarabilirdi?
KORU : Fakat çobanı onun elinden kim kurtarabilirdi?
HEDEF: Fakat çobanı onun elinden kim kurtarabilirdi?
```

```text
[124 · zamir]
GİRDİ: Ben anlamayarak ona doğru bakarken yanıma yaklaşmış bulundu.
HAM  : Ben anlamayarak 10'a doğru bakarken yanıma yaklaşmış bulundu.
KORU : Ben anlamayarak ona doğru bakarken yanıma yaklaşmış bulundu.
HEDEF: Ben anlamayarak ona doğru bakarken yanıma yaklaşmış bulundu.
```

```text
[129 · zamir]
GİRDİ: Onun bu duraklayışının farkına varan arkadaşı: "Yok canım" dedi, "evini filan soymam."
HAM  : Onun bu duraklayışının farkına varan arkadaşı: "Yok canım" dedi, "evini filan soymam.
KORU : Onun bu duraklayışının farkına varan arkadaşı: "Yok canım" dedi, "evini filan soymam."
HEDEF: Onun bu duraklayışının farkına varan arkadaşı: "Yok canım" dedi, "evini filan soymam."
```

```text
[130 · zamir]
GİRDİ: Birdenbire durdu; odadaki sessizlik onu şaşırttı.
HAM  : Birdenbire durdu; odadaki sessizlik 10'u şaşırttı.
KORU : Birdenbire durdu; odadaki sessizlik onu şaşırttı.
HEDEF: Birdenbire durdu; odadaki sessizlik onu şaşırttı.
```

```text
[135 · zamir]
GİRDİ: Onu buradan çıkar.
HAM  : 10'u buradan çıkar.
KORU : Onu buradan çıkar.
HEDEF: Onu buradan çıkar.
```

```text
[138 · kalip]
GİRDİ: Bir şeyler düşündü, sonra çapkınca bir gülüşle:
HAM  : Bir şeyler düşündü, sonra çapkınca bir gülüşle.
KORU : Bir şeyler düşündü, sonra çapkınca bir gülüşle:
HEDEF: Bir şeyler düşündü, sonra çapkınca bir gülüşle:
```

```text
[141 · kalip]
GİRDİ: Yanındakilerden biri: "Sen de kendini avrat mı sayıyon?"
HAM  : Yanındakilerden biri: "Sen de kendini avrat mı sayıyon?
KORU : Yanındakilerden biri: "Sen de kendini avrat mı sayıyon?"
HEDEF: Yanındakilerden biri: "Sen de kendini avrat mı sayıyon?"
```

```text
[147 · kalip]
GİRDİ: Birkaç gün uğramayıp tekrar göründüğü zamanlar genç adamın ilk sözü:
HAM  : Birkaç gün uğramayıp tekrar göründüğü zamanlar genç adamın ilk sözü.
KORU : Birkaç gün uğramayıp tekrar göründüğü zamanlar genç adamın ilk sözü:
HEDEF: Birkaç gün uğramayıp tekrar göründüğü zamanlar genç adamın ilk sözü:
```
