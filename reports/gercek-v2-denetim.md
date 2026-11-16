# Gerçek metin ölçümü — v2-denetim

Küme: `evaluation/gercek.jsonl`, 279 Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.

| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |
|---|---:|---:|---:|---:|---:|
| Girdiyi kopyala | 58.4 | 59.9 | 0.0 (163) | 3.4 (116) | 112 |
| Kural tabanlı (saf) | 34.8 | 40.9 | 71.2 (163) | 57.8 (116) | 1 |
| Model (korumasız) | 81.7 | 82.8 | 17.8 (163) | 83.6 (116) | 3 |
| Model + koruma | 87.8 | 89.2 | 10.4 (163) | 88.8 (116) | 5 |

Koruma 21 örnekte en az bir bölgeyi geri aldı.

## Kategori kırılımı (esnek doğru / n)

| Kategori | n | Girdiyi kopyala | Kural tabanlı (saf) | Model (korumasız) | Model + koruma |
|---|---:|---:|---:|---:|---:|
| aralik | 17 | 0 | 0 | 15 | 16 |
| atasozu | 12 | 12 | 0 | 4 | 4 |
| buyuk | 8 | 0 | 0 | 8 | 8 |
| es_yazim | 35 | 35 | 19 | 34 | 35 |
| kalip | 53 | 53 | 18 | 49 | 50 |
| kardinal | 45 | 1 | 42 | 40 | 43 |
| kucuk_sayi | 30 | 30 | 10 | 25 | 27 |
| olcu | 4 | 0 | 2 | 3 | 3 |
| ondalik | 5 | 0 | 5 | 5 | 5 |
| para | 20 | 2 | 9 | 11 | 13 |
| saat | 4 | 0 | 2 | 2 | 2 |
| sira | 4 | 4 | 1 | 3 | 3 |
| tarih | 12 | 0 | 6 | 12 | 12 |
| zamir | 30 | 30 | 0 | 20 | 28 |

## Model hataları (48; ham ya da korumalı çıktı yanlış)

```text
[2 · kalip]
GİRDİ: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
HAM  : Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu 2 çeyrek yapsana!
KORU : Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu 2 çeyrek yapsana!"
HEDEF: Çocuk güğümünü olduğu yerde bırakarak ona koştu, parayı uzattı: "Şunu iki çeyrek yapsana!"
```

```text
[6 · para]
GİRDİ: Yarın yüz seksen öbür gün yüz doksan beş lira.
HAM  : Yarın 184 gün 195 TL.
KORU : Yarın yüz seksen öbür gün 195 TL.
HEDEF: Yarın 180 öbür gün 195 TL.
```

```text
[13 · aralik]
GİRDİ: Hatırladığıma göre yol bir buçuk iki saat çekiyordu.
HAM  : Hatırladığıma göre yol 1,5 saat çekiyordu.
KORU : Hatırladığıma göre yol bir buçuk iki saat çekiyordu.
HEDEF: Hatırladığıma göre yol 1,5-2 saat çekiyordu.
```

```text
[19 · para]
GİRDİ: Hiç olmazsa bir iki buçuk liralık koparmalıydı.
HAM  : Hiç olmazsa 1-2,5 TL'lik koparmalıydı.
HEDEF: Hiç olmazsa bir 2,5 TL'lik koparmalıydı.
```

```text
[21 · kardinal]
GİRDİ: Ayın en çok on gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HAM  : Ayın en çok 10 gününde aldığı en çok 60'ar kuruşla bunları doyuramıyordu.
KORU : Ayın en çok 10 gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
HEDEF: Ayın en çok 10 gününde aldığı en çok altmışar kuruşla bunları doyuramıyordu.
```

```text
[22 · olcu]
GİRDİ: Bir elli boyunda, altmışlık, kırçıl sakallı bir adam.
HAM  : 1-50 boyunda, 60'lık, kırçıl sakallı bir adam.
HEDEF: 1,50 boyunda, altmışlık, kırçıl sakallı bir adam.
```

```text
[24 · kalip]
GİRDİ: Yaşından da utanmaz, ak sakalına da bakmaz, yazıhanesine uğrayan altmışlık köylü karılarına saldırır.
HAM  : Yaşından da utanmaz, ak sakalına da bakmaz, yazıhanesine uğrayan 60'lık köylü karılarına saldırır.
HEDEF: Yaşından da utanmaz, ak sakalına da bakmaz, yazıhanesine uğrayan altmışlık köylü karılarına saldırır.
```

```text
[27 · para]
GİRDİ: Bir hafta sonra tekrar doğumevine gelen delikanlıya: "Şimdi borcun yüz altmış beş liradır."
HAM  : Bir hafta sonra tekrar doğumevine gelen delikanlıya: "Şimdi borcun 165 TL'dir.
KORU : Bir hafta sonra tekrar doğumevine gelen delikanlıya: "Şimdi borcun 165 TL'dir."
HEDEF: Bir hafta sonra tekrar doğumevine gelen delikanlıya: "Şimdi borcun 165 TL'dir."
```

```text
[43 · para]
GİRDİ: İçinde seksen portakal bulunan sandıklardan her biri üç liradan hesap edildi.
HAM  : İçinde 80 portakal bulunan sandıklardan her 1'i 3 TL'den hesap edildi.
KORU : İçinde 80 portakal bulunan sandıklardan her biri üç liradan hesap edildi.
HEDEF: İçinde 80 portakal bulunan sandıklardan her biri 3 TL'den hesap edildi.
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
[70 · para]
GİRDİ: Cebimden bir elli kuruş çıkarıp uzattım: "Kardeş misiniz?" diye sordum.
HAM  : Cebimden 1-50 kuruş çıkarıp uzattım: "Kardeş misiniz?" diye sordum.
HEDEF: Cebimden bir 50 kuruş çıkarıp uzattım: "Kardeş misiniz?" diye sordum.
```

```text
[74 · para]
GİRDİ: Yanındakine: "Yüz elli liram var, yol parası ile otel parası da içinde!" dedi.
HAM  : Yanındakine: "150 TL var, yol parası ile otel parası da içinde!
KORU : Yanındakine: "150 TL var, yol parası ile otel parası da içinde!" dedi.
HEDEF: Yanındakine: "150 TL'm var, yol parası ile otel parası da içinde!" dedi.
```

```text
[75 · kalip]
GİRDİ: Kısa bir pazarlıktan sonra ellişer kuruşa şoförün yanına binmek hususunda mutabık kaldık.
HAM  : 41 pazarlıktan sonra 50'şer kuruşa şoförün yanına binmek hususunda mutabık kaldık.
KORU : Kısa bir pazarlıktan sonra ellişer kuruşa şoförün yanına binmek hususunda mutabık kaldık.
HEDEF: Kısa bir pazarlıktan sonra ellişer kuruşa şoförün yanına binmek hususunda mutabık kaldık.
```

```text
[77 · para]
GİRDİ: Elli lirasını peşin aldım, yukarı kattaki odama çıktığım gibi, işe koyuldum.
HAM  : 50 TL'sinı peşin aldım, yukarı kattaki odama çıktığım gibi, işe koyuldum.
HEDEF: 50 TL'sini peşin aldım, yukarı kattaki odama çıktığım gibi, işe koyuldum.
```

```text
[87 · atasozu]
GİRDİ: Otuz iki dişten çıkan, otuz iki mahalleye yayılır.
HAM  : 32 dişten çıkan, 32 mahalleye yayılır.
HEDEF: Otuz iki dişten çıkan, otuz iki mahalleye yayılır.
```

```text
[93 · kucuk_sayi]
GİRDİ: Bunun için sekiz kişi iki gündür hep çatıda uğraşıyorlardı.
HAM  : Bunun için 8 kişi iki gündür hep çatıda uğraşıyorlardı.
HEDEF: Bunun için sekiz kişi iki gündür hep çatıda uğraşıyorlardı.
```

```text
[110 · atasozu]
GİRDİ: Bir deli kuyuya bir taş atar, kırk akıllı çıkaramaz.
HAM  : Bir deli kuyuya bir taş atar, 40 akıllı çıkaramaz.
HEDEF: Bir deli kuyuya bir taş atar, kırk akıllı çıkaramaz.
```

```text
[112 · kardinal]
GİRDİ: Biz dağlıyız, sizin boş çıkamadığınız bayıra biz kırk okka yükle çıkarız!
HAM  : Biz dağlıyız, sizin boş çıkamadığınız bayıra biz kırk okka yükle çıkarız!
HEDEF: Biz dağlıyız, sizin boş çıkamadığınız bayıra biz 40 okka yükle çıkarız!
```

```text
[113 · atasozu]
GİRDİ: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
HAM  : Dervişlik olaydı taç ile hırka, ben de alırdım 30'a 40'a.
HEDEF: Dervişlik olaydı taç ile hırka, ben de alırdım otuza kırka.
```

```text
[115 · atasozu]
GİRDİ: Sıtma ben tuttuğumu kırk yıl sonra tanırım demiş.
HAM  : Sıtma ben tuttuğumu 40 yıl sonra tanırım demiş.
HEDEF: Sıtma ben tuttuğumu kırk yıl sonra tanırım demiş.
```

```text
[116 · kardinal]
GİRDİ: "Kırk yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
HAM  : 1940 yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
KORU : "Kırk yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
HEDEF: "40 yaşında adam aklı başında oturmazsa işte böyle olur" diye başladı.
```

```text
[117 · kardinal]
GİRDİ: Kırk yıl evinde oturdum, koca öküz gibi çalıştım, bir gün doyunca yemek yemedim…
HAM  : 1940 yıl evinde oturdum, koca öküz gibi çalıştım, bir gün doyunca yemek yemedim…
KORU : Kırk yıl evinde oturdum, koca öküz gibi çalıştım, bir gün doyunca yemek yemedim…
HEDEF: 40 yıl evinde oturdum, koca öküz gibi çalıştım, bir gün doyunca yemek yemedim…
```

```text
[120 · saat]
GİRDİ: Yarın dokuzda gelin, öğrenirsiniz!
HAM  : Yarın dokuzda gelin, öğrenirsiniz!
HEDEF: Yarın 9'da gelin, öğrenirsiniz!
```

```text
[145 · para]
GİRDİ: Kerim Ağa yerinde doğrulmaya çalışarak, kısık sesiyle: "Yirmi kuruştan ver!"
HAM  : Kerim Ağa yerinde doğrulmaya çalışarak, kısık sesiyle: "20 kuruştan ver!
KORU : Kerim Ağa yerinde doğrulmaya çalışarak, kısık sesiyle: "20 kuruştan ver!"
HEDEF: Kerim Ağa yerinde doğrulmaya çalışarak, kısık sesiyle: "20 kuruştan ver!"
```

```text
[146 · para]
GİRDİ: Cebimden bir yirmi beş kuruşluk çıkardım.
HAM  : Cebimden 1-25 kuruşluk çıkardım.
HEDEF: Cebimden bir 25 kuruşluk çıkardım.
```

```text
[150 · kucuk_sayi]
GİRDİ: Dört katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
HAM  : 4 katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
HEDEF: Dört katlı otelin en üst penceresinden beyaz bir gölge sarkıyordu.
```

```text
[152 · kucuk_sayi]
GİRDİ: Beş, dört, üç, iki…
HAM  : 5432…
HEDEF: Beş, dört, üç, iki…
```

```text
[159 · saat]
GİRDİ: Saat henüz dörttü.
HAM  : Saat henüz dörttü.
HEDEF: Saat henüz 4'tü.
```

```text
[163 · kalip]
GİRDİ: Bin dert vardı başında.
HAM  : 1.000 dert vardı başında.
HEDEF: Bin dert vardı başında.
```

```text
[166 · atasozu]
GİRDİ: Bin atın varsa bin dinlen, bir atın varsa in dinlen.
HAM  : 1.000 atın varsa bin dinlen, bir atın varsa in dinlen.
HEDEF: Bin atın varsa bin dinlen, bir atın varsa in dinlen.
```

```text
[167 · atasozu]
GİRDİ: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
HAM  : 1.000 atın varsa inişte in, bir atın varsa yokuşta bin.
HEDEF: Bin atın varsa inişte in, bir atın varsa yokuşta bin.
```

```text
[172 · sira]
GİRDİ: Zavallı adam üçüncü uykusuz geceyi de yarılamak üzereydi ve direksiyondaki elleri titriyordu.
HAM  : Zavallı adam 3. uykusuz geceyi de yarılamak üzereydi ve direksiyondaki elleri titriyordu.
HEDEF: Zavallı adam üçüncü uykusuz geceyi de yarılamak üzereydi ve direksiyondaki elleri titriyordu.
```

```text
[173 · kucuk_sayi]
GİRDİ: Çoban gözlerini karşısındaki üç kişinin üzerinde bir müddet gezdirdikten sonra garip bir çekingenlikle:
HAM  : Çoban gözlerini karşısındaki üç kişinin üzerinde bir müddet gezdirdikten sonra garip bir çekingenlikle.
KORU : Çoban gözlerini karşısındaki üç kişinin üzerinde bir müddet gezdirdikten sonra garip bir çekingenlikle:
HEDEF: Çoban gözlerini karşısındaki üç kişinin üzerinde bir müddet gezdirdikten sonra garip bir çekingenlikle:
```

```text
[198 · aralik]
GİRDİ: Beş on adım gitmemiştim ki, arkamdan onun sesini duydum.
HAM  : 5-10 adım gitmemiştim ki, arkamdan 10'un sesini duydum.
KORU : 5-10 adım gitmemiştim ki, arkamdan onun sesini duydum.
HEDEF: 5-10 adım gitmemiştim ki, arkamdan onun sesini duydum.
```

```text
[209 · kucuk_sayi]
GİRDİ: İki sıska çocuk büyük bir ağacın dibinde ve birbirlerinin kucağında uyumuşlardı.
HAM  : 2-0'a çocuk büyük bir ağacın dibinde ve birbirlerinin kucağında uyumuşlardı.
KORU : İki sıska çocuk büyük bir ağacın dibinde ve birbirlerinin kucağında uyumuşlardı.
HEDEF: İki sıska çocuk büyük bir ağacın dibinde ve birbirlerinin kucağında uyumuşlardı.
```

```text
[210 · es_yazim]
GİRDİ: Arefe günü yalan söyleyenin, bayram günü yüzü kara çıkar.
HAM  : Arefe günü yalan söyleyenin, bayram günü 100'ü kara çıkar.
KORU : Arefe günü yalan söyleyenin, bayram günü yüzü kara çıkar.
HEDEF: Arefe günü yalan söyleyenin, bayram günü yüzü kara çıkar.
```

```text
[220 · zamir]
GİRDİ: Hayret edişim onu güldürdü:
HAM  : Hayret edişim 10'u güldürdü.
KORU : Hayret edişim onu güldürdü:
HEDEF: Hayret edişim onu güldürdü:
```

```text
[222 · zamir]
GİRDİ: Ondan sonra heyecan içinde neticeyi beklemeye başladı.
HAM  : 10'dan sonra heyecan içinde neticeyi beklemeye başladı.
KORU : Ondan sonra heyecan içinde neticeyi beklemeye başladı.
HEDEF: Ondan sonra heyecan içinde neticeyi beklemeye başladı.
```

```text
[233 · zamir]
GİRDİ: Bir taş var, onu söktürmek lazım.
HAM  : Bir taş var, 10'u söktürmek lazım.
KORU : Bir taş var, onu söktürmek lazım.
HEDEF: Bir taş var, onu söktürmek lazım.
```

```text
[234 · zamir]
GİRDİ: Onun herhangi bir şeye içi sıkıldığını söylemesi beni şaşırttı.
HAM  : 10'un herhangi bir şeye içi sıkıldığını söylemesi beni şaşırttı.
KORU : Onun herhangi bir şeye içi sıkıldığını söylemesi beni şaşırttı.
HEDEF: Onun herhangi bir şeye içi sıkıldığını söylemesi beni şaşırttı.
```

```text
[237 · zamir]
GİRDİ: Birkaç mahkumun pek açık alaylan onun kulağını bükmüştü.
HAM  : Birkaç mahkumun pek açık alaylan 10'un kulağını bükmüştü.
KORU : Birkaç mahkumun pek açık alaylan onun kulağını bükmüştü.
HEDEF: Birkaç mahkumun pek açık alaylan onun kulağını bükmüştü.
```

```text
[239 · zamir]
GİRDİ: Aradan geçen zamanın kısalığı onu korkuttu.
HAM  : Aradan geçen zamanın kısalığı 10'u korkuttu.
KORU : Aradan geçen zamanın kısalığı onu korkuttu.
HEDEF: Aradan geçen zamanın kısalığı onu korkuttu.
```

```text
[242 · zamir]
GİRDİ: Git onunla konuş.
HAM  : Git 10'unla konuş.
KORU : Git onunla konuş.
HEDEF: Git onunla konuş.
```

```text
[243 · zamir]
GİRDİ: Bir müddet onu seyrettiler.
HAM  : 1 müddet 10'u seyrettiler.
KORU : 1 müddet onu seyrettiler.
HEDEF: Bir müddet onu seyrettiler.
```

```text
[244 · zamir]
GİRDİ: Evet, onu anladım.
HAM  : Evet, 10'u anladım.
KORU : Evet, onu anladım.
HEDEF: Evet, onu anladım.
```

```text
[245 · zamir]
GİRDİ: Bir gece onu çağırdım, derenin alt başına gittik, kavak fidanlarının arasına oturduk.
HAM  : Bir gece 10'u çağırdım, derenin alt başına gittik, kavak fidanlarının arasına oturduk.
HEDEF: Bir gece onu çağırdım, derenin alt başına gittik, kavak fidanlarının arasına oturduk.
```
