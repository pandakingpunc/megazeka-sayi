# Megazeka-Sayı · v2 ek şartnamesi

`docs/SPEC.md` geçerlidir; bu belge yalnız v2'de eklenenleri ve netleştirilenleri tanımlar.
v2 verisi = v1.1 eğitim akışı (dosya olarak sabit, yeniden üretilmez) + üç ayrı tohumlu yeni kaynak.

| Kaynak | Betik | Çıktı öneki | İçerik |
|---|---|---|---|
| A · sayısal doğruluk | `training/v2_sayisal.py` | `data/v2/a-` | iç sıfırlar, telefon/kod, aralık, birim × ek, bileşik ölçü, yeni birimler, uzun çok varlıklı cümle, küçük sayı politikası |
| B · tuzaklar | `training/v2_tuzak.py` | `data/v2/b-` | değişmemesi gereken cümleler (+ en çok %20 karşıt pozitif) |
| C · yeni girdi biçimleri | `training/v2_bicim.py` | `data/v2/c-` | yarı normalleşmiş (rakamlı) girdi, bitişik yazılmış sayı, saat deyişleri, ayın günü |

Her kaynak `train`, `validation`, `test` dosyası yazar (`a-train.jsonl` …). Satır sözleşmesi SPEC §5 ile aynıdır:
`{"girdi", "hedef", "kategori", "sablon"}`. `sablon` kimliği `v2a-`, `v2b-`, `v2c-` ile başlar. Test dosyası,
train/validation'da hiç kullanılmayan şablonlarla üretilir (şablonların en az %15'i teste ayrılır). Üç bölüm arasında
aynı `(girdi, hedef)` çifti ve aynı `hedef` yinelenmez. Girdi ve hedef en çok 180 bayt (UTF-8).
Girdi biçimi SPEC §4: yaklaşık %60 küçük harf + noktalamasız, %40 büyük harfle başlar + sonda nokta.
Etiketler elle yazılmaz: hedef (yazılı biçim) kurulur, girdi ondan deterministik olarak türetilir.

## A. Sayısal doğruluk

### A1. İç sıfırlı sayılar
v1.1 hataları: `yetmiş sekiz milyon on bin` → `78.100` (doğrusu `78.010.000`), `bin doksan` → `1.90` (`1.090`),
`yirmi beş bin üç` → `25.3` (`25.003`), `on iki milyon altmış iki bin` → `12.62.000` (`12.062.000`).
Her binlik grup üç hanedir; sözlüde söylenmeyen grup `000`, tek/çift haneli grup `00x`/`0xx` olarak yazılır.
Örnekleme bilinçli olarak sıfır ağırlıklıdır: en az bir grubu `000`, `00x` ya da `0x0`/`0xx` olan sayılar
(`1.005`, `10.010`, `300.007`, `2.000.500`, `40.000.040`, `1.001.001`). Para (kuruşlu ve kuruşsuz), ölçü, kişi sayısı
ve yalın sayı taşıyıcılarında, ekli ve eksiz.

### A2. Telefon ve kod
- **Belirsizlik kuralı:** sözlü telefon dizisi, `0XXX XXX XX XX` kalıbına birden fazla biçimde ayrışabiliyorsa
  belirsizdir (`beş yüz kırk yedi yüz altmış altı` = `540 766` ya da `547 166`). v2 üreteci yalnız **tek ayrışımı
  olan** sözlü biçimler üretir; gerçek konuşmacı da böyle durumda rakam rakam söyler. `telefon_ayrisimlari(sozcukler)`
  işlevi bütün geçerli ayrışımları döndürür; birleştirme sırasında eski akıştaki belirsiz telefon satırları bu işlevle elenir.
- Okuma kipleri eskisi gibi: grup sayı olarak (`beş yüz otuz iki`, `kırk beş`) ya da rakam rakam (`beş üç iki`, `dört beş`),
  gruplar arasında karışık. `+90` → `artı doksan`. İçinde `0` geçen gruplar ağırlıklı (`yüz bir`, `sıfır yedi`, `on`, `doksan`).
- Kod / numara: rakam rakam, 3–11 hane; yinelenen rakamlar (`991`, `0007`, `55555`) ve uzun diziler (TC kimlik no 11 hane,
  takip/sipariş/abone/müşteri no 8–11 hane) ağırlıklı. Çıktı boşluksuz ve noktasız.

### A3. Yaklaşık aralık
Onluk–onluk ve yüzlük–yüzlük çiftler ağırlıklı: `altmış yetmiş beş gün` → `60-75 gün`, `iki yüz iki yüz elli` → `200-250`,
`altmış altmış beş` → `60-65`, `on beş yirmi` → `15-20`, `yüz yüz elli` → `100-150`, `bin bin beş yüz lira` → `1.000-1.500 TL`.
İçinde `bir` geçen aralık üretilmez (sözcük kalır, SPEC §1).

### A4. Birim × ek dengesi
`GB'tan`, `MB'tan`, `kW'ta`, `V'tan`, `L'den`, `mL'ye`, `m²'lik`, `°C'de` … Her (birim, ek türü) bileşimi en az 40 kez.
Yazılı ek kanonik okunuşun son sözcüğüne göredir (SPEC §2): gigabayt, megabayt, terabayt, kilovat, vat, volt, litre …

### A5. Bileşik ölçü ve süre
Art arda iki birimli ifade iki ayrı sayı olarak yazılır, **bütün sayılar rakam** (`bir` dahil, bağlam birimdir):
`üç kilo iki yüz gram` → `3 kg 200 g`, `bir metre seksen santim` → `1 m 80 cm`, `iki kilometre üç yüz metre` → `2 km 300 m`,
`bir litre iki yüz elli mililitre` → `1 L 250 mL`, `iki saat on beş dakika` → `2 saat 15 dakika`,
`bir saat kırk beş dakika otuz saniye` → `1 saat 45 dakika 30 saniye`, `beş dakika yirmi saniye` → `5 dakika 20 saniye`.
Ek yalnız son birime gelir (`3 kg 200 g'lık`, `2 saat 15 dakikada`). Para bileşiği eskisi gibi tek sayıdır (`5,50 TL`).

### A6. Yeni birimler
Kısaltmalı (kesmeli ek): miligram → `mg`, metreküp → `m³`, kilometrekare → `km²`, kilovatsaat / kilovat saat → `kWh`,
hertz → `Hz`, megahertz → `MHz`. Kanonik okunuş birimin tam adıdır.
Sözcük kalan (ek sözcüğe bitişik, kesmesiz): `ton`, `inç`, `kalori`, `hektar`, `dönüm`, `beygir`, `piksel`, `karat`,
`saat`, `dakika`, `saniye`, `gün`, `hafta`, `ay`, `yıl`, `yaş` (`50 tonluk`, `55 inç`, `2.000 kalori`, `15 dakikada`, `40 yaşında`).

### A7. Uzun, çok varlıklı cümleler
12–22 sözcük, 2–3 farklı türde varlık (para + tarih + saat, ölçü + yüzde + kardinal …), ≤ 180 bayt. Bağlaçlı ve
virgüllü doğal konuşma cümleleri; varlıklar cümlenin başında, ortasında ve sonunda.

### A8. Küçük sayı politikası pekiştirmesi
Bağlamsız tek sözcüklük 0–9 sözcük kalır (`masada sekiz sandalye eksik`, `altı kişi geldi`, `üç gün sonra`);
aynı taşıyıcıda 10 ve üstü rakama çevrilir (`masada on iki sandalye eksik` → `12`). İki durum da aynı şablonlardan üretilir.

## B. Tuzaklar (girdi = hedef)

Cümle değil **kalıp** öğretilir: her olgu çok sayıda farklı taşıyıcıda, cümlenin başında/ortasında/sonunda,
**sarmalayıcısız kısa cümleler dahil** (2–5 sözcük) görünür. Olgular:

1. `bin-` (binmek) bütün çekimler; özellikle kısa emirler: `taksiye bin de gel`, `otobüse bin hemen`, `hadi bin`,
   `sen de bin`, `bin şu arabaya`, `atla bin`, `binin`, `binelim`, `binsene`, `binmeden önce`.
2. `ikinci el` her konumda ve ekli (`ikinci el telefonlar`, `ikinci elden aldım`, `ikinci ele düştü`, `bu araba ikinci el`).
3. `yüz` ad/fiil: `bu yüzden`, `o yüzden`, `senin yüzünden`, `yüzüme`, `yüzleşti`, `yüzsüz`, `güler yüzlü`, `yüz yüze`,
   yüzmek çekimleri (`yüzdük`, `yüzüyor`, `yüzmeye gitti`, `yüz bakalım`).
4. Sıra sayısı yüklem/zamir: `üçüncü oldu`, `birinci geldi`, `ikincisi`, `üçüncüsü daha iyi`, `sonuncu`, `birincilik`.
5. `on-` zamirleri, `altı/altında/altını/altından`, `yedi/yediler/yedik` (yemek), `kırk-` (kırkmak), `dokuz doğurmak`.
6. Deyim, atasözü ve kalıplar (en az 80 ayrı): `dört dörtlük`, `iki arada bir derede`, `kırk yılın başı`, `kırk fırın ekmek`,
   `yedi kat yabancı`, `bir taşla iki kuş`, `iki ayağını bir pabuca`, `dokuz köyden kovulur`, `bin pişman`, `bin bir türlü`,
   `yüz bulmak`, `beş para etmez`, `üç aşağı beş yukarı`, `iki gözüm`, `bir elin nesi var iki elin sesi var`,
   `iki dirhem bir çekirdek`, `dokuz canlı`, `yedi düvel`, `kırk yıllık dost`, `on parmağında on marifet`, `sıfırı tüketti`,
   `sıfırdan başladı`, `sıfır araba`, `bire bir`, `birebir`, `bir an önce`, `bir daha`, `tek bir`, `bir de`, `birdenbire`.
7. Özel adlar ve eser adları: `Dokuz Eylül Üniversitesi`, `Ondokuz Mayıs Üniversitesi`, `Yüzüncü Yıl Üniversitesi`,
   `Beşiktaş`, `Yedikule`, `Üçkuyular`, `Dörtyol`, `Kırklareli`, `Binali`, `Altınordu`, `Yedi Cüceler`, `Üç Silahşörler`,
   `Kırk Haramiler`, `Binbir Gece Masalları`, `Beş Hececiler`, `Yediler`, `Kırklar Dağı`.
8. İçinde sayı kökü geçen sözcükler: `onbaşı`, `yüzbaşı`, `binbaşı`, `kırkayak`, `üçgen`, `dörtgen`, `beşgen`, `altıgen`,
   `ikiz`, `üçüz`, `dörtnala`, `yediveren`, `ikilem`, `ikili`, `üçlü`, `beşli`, `onluk`, `yüzlük`, `binlik`,
   üleştirme (`ikişer`, `üçer`, `beşer`, `onar`), topluluk (`ikimiz`, `üçümüz`, `beşi birden`), belgisiz (`onlarca`, `yüzlerce`, `binlerce`).
9. Sayısız birim / para / ay sözcükleri (yeni birimler dahil): `tonlarca yük`, `kalorisi düşük`, `inç inç`, `dakikalarca`,
   `saniyesinde`, `liranın değeri`, `kasımda`, `metrelerce`. Kesme işareti almazlar.
10. `yarım`, `çeyrek`, `buçuk`, kesirler: `yarım saat`, `yarım yamalak`, `çeyrek altın`, `çeyrek final`, `üçte biri`.

**Karşıt pozitifler (en çok %20):** aynı sözcüğün sayı olduğu kısa cümleler, hedefleri yalnız mevcut `kur_*`
işlevleriyle kurulur: `bin lira ver` → `1.000 TL ver`, `yüz metre yüzdü` → `100 m yüzdü`, `ikinci katta oturuyor` → `2. katta`…
(sıra sayısına ek verilmediği için ekli sıra karşıtı üretilmez; `ikinci kat` gibi yalın biçim kullanılır).
Böylece model "kısa cümle = dokunma" kestirmesini öğrenmez.

Çeşitlilik eşikleri (train dosyasında ölçülür): ≥ 400 ayrı şablon; hiçbir şablon satırların %1'inden fazlası değil;
hiçbir ilk sözcük %6'dan fazla değil; 2–5 sözcüklük cümle payı %20–35; her olgu (1–10) en az 500 satır.

## C. Yeni girdi biçimleri

### C1. Yarı normalleşmiş girdi (`kategori: "yari"`)
ASR (ör. Whisper) sayıları kısmen rakamla verir. Hedef SPEC biçimidir; girdi aşağıdaki kısmi biçimlerden biridir:

| Girdi | Hedef |
|---|---|
| `5 bin lira` | `5.000 TL` |
| `12 bin 500 lira` · `5 bin 250` | `12.500 TL` · `5.250` |
| `3 milyon 200 bin` | `3.200.000` |
| `2 buçuk milyon` · `1,5 milyon` · `15 milyon` | `2,5 milyon` · `1,5 milyon` · `15 milyon` (yuvarlak büyük sayı SPEC §1) |
| `1250 lira` · `12500 kişi` · `1250,50 lira` | `1.250 TL` · `12.500 kişi` · `1.250,50 TL` |
| `100 kilometre` · `2 kilo` · `16 gigabayt` · `50 lira` | `100 km` · `2 kg` · `16 GB` · `50 TL` |
| `yüzde 50` · `yüzde 12,5` · `yüzde 12 buçuk` | `%50` · `%12,5` · `%12,5` |
| `2 buçuk kilo` · `saat 3 buçukta` | `2,5 kg` · `saat 3.30'da` |
| `saat 14:30'da` · `14:05` | `saat 14.30'da` · `14.05` |
| `15 kasım 2026` | `15 Kasım 2026` |
| `eksi 5 derece` | `-5 derece` |
| `05321234567` · `0 532 123 45 67` | `0532 123 45 67` |
| `5 bin liraya` · `100 kilometreden` · `2 kiloluk` | `5.000 TL'ye` · `100 km'den` · `2 kg'lık` |

Kurallar: binlik noktası para/birim/kişi gibi bir bağlamla gelen 4+ haneli sayılara konur; yıl (`2026 yılında`, `1990'da`),
telefon, kod ve posta kodu noktasız kalır. Üreteç bağlamsız yalın 1000–2100 arası sayı üretmez (yıl belirsizliği).
Girdide rakam olduğunda küçük sayı politikası uygulanmaz: rakam rakam kalır (`3 kişi` → `3 kişi`).
Bu kategorinin yaklaşık %12'si girdi = hedef olan zaten doğru biçimlerdir (`5.000 TL`, `%50`, `2026 yılında`, `3 kişi`).

### C2. Bitişik yazılmış sayılar (`kategori: "bitisik"`)
Sözlü sayının sözcükleri kısmen ya da tamamen bitişik: `onbeş kişi` → `15 kişi`, `yirmibeş lira` → `25 TL`,
`ikiyüz elli gram` → `250 g`, `üçbin` → `3.000`, `yüzelli` → `150`, `binyediyüz` → `1.700`, `yüzde onbeş` → `%15`,
`saat onbirde` → `saat 11'de`. Yalnız sayı sözcükleri birleşir; birim/para sözcüğü ayrı kalır. Tek sözcüklük sayılar
(`beş`) bu kategoriye girmez.

### C3. Saat deyişleri (`kategori: "saat_deyis"`)
Sözcükler korunur, saat ve dakika rakama çevrilir (10'dan küçük olsa da, `bir` dahil; bağlam saattir). `çeyrek` sözcük kalır.

| Girdi | Hedef |
|---|---|
| `beşe on kala` | `5'e 10 kala` |
| `dördü yirmi geçe` | `4'ü 20 geçe` |
| `üçe çeyrek var` | `3'e çeyrek var` |
| `altıyı çeyrek geçiyor` | `6'yı çeyrek geçiyor` |
| `saat sekize beş var` | `saat 8'e 5 var` |
| `on ikiye çeyrek kala buluşalım` | `12'ye çeyrek kala buluşalım` |
| `bire on kala çıktık` | `1'e 10 kala çıktık` |
| `dokuzu beş geçiyordu` | `9'u 5 geçiyordu` |

Saat 1–12, dakika {5, 10, 15→çeyrek, 20, 25} ağırlıklı, öteki dakikalar da var (`üçe iki var` → `3'e 2 var`).
Ek biçimi SPEC §2 (saat sayısının okunuşuna göre: `4'e`, `6'ya`, `9'u`, `10'a`, `3'ü`).

### C4. Ayın günü (`kategori: "tarih"`)
`ayın on beşinde` → `ayın 15'inde`, `ayın yirmisi` → `ayın 20'si`, `ayın üçüne kadar` → `ayın 3'üne kadar`,
`mayısın on dokuzunda` → `mayısın 19'unda` (ay adı küçük kalır: gün + ay sırası değil), `her ayın biri` → `her ayın 1'i`.
İyelik + durum ekleri: `-(s)I`, `-(s)InDA`, `-(s)InA`, `-(s)InDAn`, `-(s)InI`. Gün 1–31, hepsi rakam.

## Ortak kurallar

- Mevcut dosyalar değiştirilmez: `src/megazeka_sayi/*.py`, `training/uret.py`, `training/train.py`, `data/*.jsonl`,
  `evaluation/*`, `tests/test_*.py` (yeni test dosyası eklenir). Yardımcılar içe aktarılarak kullanılır
  (`megazeka_sayi.sayilar`, `.turkce`, `.varliklar`, `.sablonlar`).
- `evaluation/*.jsonl` dosyaları **okunmaz**: bunlar bağımsız ölçüm kümeleridir.
- Üretim deterministiktir (`--seed`); aynı tohum aynı dosyayı verir.
