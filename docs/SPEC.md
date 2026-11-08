# Megazeka-Sayı · Teknik şartname (v0)

Görev: Türkçe **ters metin normalleştirme (ITN)**. Ses tanıma (ASR) sisteminin yazıyla verdiği sayıları
TDK yazım kurallarına uygun rakam biçimine çevirmek. Sayı dışındaki her şey **bayt bayt aynı** kalır.

| Girdi (ASR) | Çıktı |
|---|---|
| toplam bin iki yüz elli lira elli kuruş | toplam 1.250,50 TL |
| yüzde on iki buçuk indirim | %12,5 indirim |
| iki buçuk kilogram domates | 2,5 kg domates |
| saat on dört otuzda görüşelim | saat 14.30'da görüşelim |
| sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi | 0532 123 45 67 |

Model: `google/byt5-small` + LoRA (Megazeka ile aynı altyapı; bayt düzeyi rakam ve ek için ideal).
Veri: tamamen sentetik ve **ters yönde** üretilir: önce doğru yazılı biçim (hedef) kurulur, sonra
deterministik bir sözlüleştirici (TN) ile konuşma biçimine (girdi) çevrilir. Böylece etiketler kusursuzdur.

## 1. Yazım kuralları (çıktı biçimi)

- Binlik ayırıcı nokta, ondalık virgül: `1.250`, `12.000.000`, `3,14`. Dört basamaklı sayılar da noktalı: `1.250`.
  **İstisna:** yıllar (`2026`), telefon, kod/PIN, posta kodu noktasız.
- Para: `lira` / `Türk lirası` → `TL`, kuruş ondalığa girer: `1.250,50 TL`. Yalnız kuruş: `50 kuruş`.
  Yabancı paralar sözcük kalır: `100 dolar`, `20 avro`, `15 sterlin`, `5 euro`.
- Yüzde: `%12,5`, `%50`, `%100`.
- Saat: `saat 14.30`, `09.05` değil `9.05` (konuşulduğu gibi), dakika iki hane: `14.05`. Yalnız saat: `saat 3'te`, `saat 14'te`.
  `saat üç buçuk` → `saat 3.30`.
- Tarih (TDK: belirli tarihte ay adı büyük): `8 Kasım 2026`, `29 Ekim 1923`. Tarih dışında ay adı küçük kalır (`kasımda`).
  Gün + ay: `8 Kasım`. Yıl tek başına: `2026`, `1990'lar`.
- Sıra sayısı (yalnız ardından ad geldiğinde): `3. kat`, `21. yüzyıl`, `2. madde`, `10. sınıf`.
  Yüklem olarak kalır: `birinci oldu`, `ikinci geldi`.
- Birimler (TDK kısaltmaları): kilogram/kilo → `kg`, gram → `g`, kilometre → `km`, metre → `m`,
  santimetre/santim → `cm`, milimetre → `mm`, litre → `L`, mililitre → `mL`, metrekare → `m²`,
  gigabayt → `GB`, megabayt → `MB`, terabayt → `TB`, kilovat → `kW`, vat → `W`, volt → `V`,
  derece santigrat → `°C`; yalnız `derece` sözcük kalır (`30 derece`).
- Ondalık: `virgül` → `,`: `üç virgül on dört` → `3,14`; `sıfır virgül beş` → `0,5`;
  `buçuk` = `,5`: `iki buçuk` → `2,5`, `on iki buçuk` → `12,5`.
- Büyük yuvarlak sayılar: `2,5 milyon`, `3 milyar TL`, `15 milyon`. Yuvarlak olmayan tam sayı: `1.200.000`.
  Sözlü biçim yazılı biçimden türetilir (`2,5 milyon` ↔ `iki buçuk milyon` / `iki virgül beş milyon`).
- Eksi: `eksi beş derece` → `-5 derece`.
- Telefon: `0532 123 45 67`. Sözlü biçim karışık gruplanabilir (`sıfır beş yüz otuz iki`, `sıfır beş üç iki`,
  `yüz yirmi üç`, `bir iki üç`, `kırk beş`, `dört beş`).
- Kod / PIN / numara rakam rakam: `kodu sıfır sekiz dört iki` → `kodu 0842`.
- Skor (yalnız maç bağlamında): `maç iki bir bitti` → `maç 2-1 bitti`.
- Yaklaşık aralık: `beş altı kişi` → `5-6 kişi`, `on on beş dakika` → `10-15 dakika`. İçinde `bir` geçen
  yaklaşık aralık sözcük kalır (`bir iki gün`).
- Kesirler sözcük kalır: `üçte bir`, `yarım kilo`, `çeyrek`.

### 1.1 Küçük sayı politikası (yapılandırılabilir, `KUCUK_SAYI_POLITIKASI`)

- `"yaziyla"` (varsayılan): bağlamsız tek sözcüklük 0–9 sözcük kalır (`iki kişi geldi`, `üç gün sonra`).
  10 ve üstü (`on iki kişi` → `12 kişi`) ve **her bağlamlı** sayı rakama çevrilir: birim, para, yüzde, saat,
  tarih, ondalık, sıra+ad, telefon, kod, skor, aralık (`iki kilo` → `2 kg`, `saat üçte` → `saat 3'te`).
- `"rakamla"`: bütün sayılar rakama (`2 kişi geldi`). Tek başına `bir` (belirsiz tanımlık) iki politikada
  da sözcük kalır: `bir adam`, `bir gün`, `bir şey`.

## 2. Ekler (en kritik kısım)

Ek, kesme işaretiyle rakama/kısaltmaya bağlanır. **Yazılı ekin biçimi, yazılı belirtecin kanonik
okunuşuna göre** hesaplanır; **sözlü ek ise gerçekten söylenen son sözcüğe göre**.

| Sözlü | Yazılı | Not |
|---|---|---|
| dörtte, dörde, dördü, dördün, dörtten, dörtle | 4'te, 4'e, 4'ü, 4'ün, 4'ten, 4'le | `dört` → `dörd` yumuşar (yalnız sözlüde) |
| ikide, ikiye, ikiyi, ikisi, ikinin, ikiden, ikiyle | 2'de, 2'ye, 2'yi, 2'si, 2'nin, 2'den, 2'yle | ünlüyle biten: kaynaştırma y/n/s |
| otuzda (saat) | 14.30'da | son sözcük `otuz` |
| liraya, liradan, liralık | TL'ye, TL'den, TL'lik | TL kanonik okunuşu `te le` (ince ünlü) |
| kilodan, kilogramdan | kg'dan | kg kanonik okunuşu `kilogram` |
| on iki buçukluk | %12,5'lik | `12,5` kanonik okunuşu `on iki virgül beş` |
| doksanlarda | 1990'larda | çoğul + bulunma |
| iki bin yirmi altıdaki | 2026'daki | `-ki` |

Ek türleri: bulunma `-DA`, ayrılma `-DAn`, yönelme `-(y)A`, belirtme `-(y)I`, ilgi `-(n)In`,
3. tekil iyelik `-(s)I`, vasıta `-(y)lA`, `-lIk`, çoğul `-lAr` (+ bulunma), `-DAki`.
Ünsüz benzeşmesi (fıstıkçı şahap: f s t k ç ş h p sonrası `D`→`t`): `üçte`, `beşte`, `kırkta`, `altmışta`.
Ünlü uyumu son ünlüye göre (2'li a/e, 4'lü ı/i/u/ü).
Sıra sayısına ek verilmez (veri üretilmez).

## 3. Değişmemesi gerekenler (negatif örnekler, eğitimin %35–40'ı)

- Eş yazımlı sözcükler: `yedi` (yemek fiili: "yemeğini yedi"), `altı/altında` (alt: "masanın altında"),
  `yüz` (surat, yüzmek: "yüzünü yıkadı", "denizde yüzdü"), `bin-` (binmek: "otobüse bin", "arabaya bindi"),
  `on-` zamir çekimleri (`ona, onu, onun, onda, ondan, onlar`), `kırk-` (kırkmak), `dört gözle`.
- Sayı sözcüklü kalıplar: `bir gün`, `bir şey`, `bir an`, `bir de`, `bir türlü`, `birden`, `birlikte`,
  `birkaç`, `bir sürü`, `birbirine`, `biri`, `ikisi de`, `ikimiz`, `üçümüz`, `onlarca`, `yüzlerce`,
  `binlerce`, `milyonlarca`, `kırk yılda bir`, `iki gözüm`, `yedi düvel`, `üçgen`, `beşik`, `sekizgen`,
  `birinci oldu`, `ikinci el` (deyim: `2. el` değil).
- Zaten yazılı biçimde gelen sayılar (girdi = hedef): `1.250,50 TL`, `%12,5`, `saat 14.30'da`
  (ASR bazen rakam verir; model dokunmamalı — idempotentlik).
- Sayı içermeyen gerçek Türkçe cümleler (Megazeka'nın Common Voice CC0 hedeflerinden, sayı sözcüğü
  içermeyenler).

## 4. Girdi biçimi

ASR çıktısı çoğunlukla küçük harf ve noktalamasız gelir; bazen (Whisper gibi) büyük harfli ve noktalı.
Veri iki biçimi de içerir (%60 küçük harf noktalamasız, %40 büyük harf + noktalı). Model büyük/küçük harf
ve noktalamayı **değiştirmez**; tek istisna belirli tarihteki ay adının büyük harfi.

## 5. Veri sözleşmesi

`data/{train,validation,test}.jsonl` — her satır:
`{"girdi": "...", "hedef": "...", "kategori": "para|yuzde|olcu|saat|tarih|sira|telefon|kod|skor|aralik|ondalik|kardinal|buyuk|eksi|karisik|negatif_es|negatif_kalip|negatif_yazili|negatif_dogal", "sablon": "<şablon kimliği>"}`

Test kümesi train/validation'da hiç kullanılmamış **taşıyıcı şablonlarla** üretilir (şablon kimliği
ayrık), böylece ezber değil genelleme ölçülür. Ayrıca elle yazılmış bir zorluk kümesi
(`evaluation/challenge.jsonl`) üreteçten bağımsızdır.

## 6. Ölçütler

Tam eşleşme, CER, sayı belirteci doğruluğu (hedefteki her sayısal belirtecin çıktıda birebir bulunması),
negatiflerde yanlış dönüşüm oranı (girdi = hedef olan örneklerde çıktının değişmesi), kategori kırılımı.
Karşılaştırma: "girdiyi kopyala" ve **saf kural tabanlı ITN** (bağlama bakmadan her sayı sözcüğünü çeviren)
taban çizgileri. Modelin değeri tam olarak eş yazımlı/bağlamlı örneklerde ölçülür.
