# Megazeka-Sayı · v3 veri kaynağı D (gerçek cümleler ve eksik kalıplar)

`docs/SPEC.md`, `docs/SPEC-v2.md` ve `docs/SPEC-v3-kararlar.md` geçerlidir. v3 verisi = v2 eğitim akışı (dosya olarak
sabit, yeniden üretilmez) + bu belgede tanımlanan tek yeni kaynak.

| Kaynak | Betik | Çıktı | Birleştirme |
|---|---|---|---|
| D · gerçek cümleler ve eksik kalıplar | `training/v3_gercek.py` | `data/v3/d-{train,validation,test}.jsonl` | `training/v3_birlestir.py` |

Neden: v2.0 gerçek metinde (Common Voice cümleleri) %89 tam eşleşme veriyor, üreteç testinde %98,6. Fark şu
olgulardan geliyor (hepsi eğitimde hiç yok ya da yalnız kısa şablonlarla var):

- ham model gerçek `ona/onu/onun/ondan` cümlelerinin üçte birinde `10'u`, `10'un` yazıyor;
- eğitimdeki ~80 sabit deyimin dışındaki atasözü ve deyimlerde sayıyı rakama çeviriyor;
- `bir` + sayı + para/ölçü kalıbını aralık sanıyor (`bir yirmi beş kuruşluk` → `1-25 kuruşluk`);
- bağlamsız küçük sayıyı `kişi`, `kat`, `gece` gibi adların önünde rakama çeviriyor;
- cümle başındaki büyük harfli sayıda ve tırnak içinde rakam uyduruyor (`"Kırk yaşında adam` → `1940 yaşında adam`);
- `saat` sözcüğü olmayan ya da yüklem ekli saatleri dönüştürmüyor (`Yarın dokuzda gelin`, `Saat henüz dörttü.`);
- ekli para sözcüklerinde eki düşürüyor ya da bozuyor (`liram`, `lirasını`, `liradır`).

Satır sözleşmesi SPEC §5: `{"girdi", "hedef", "kategori", "sablon"}`; `sablon` kimliği `v3d-` ile başlar. Girdi ve
hedef en çok 180 bayt. Üretim deterministiktir (`--seed`). Test dosyası train/validation'da hiç kullanılmayan
şablonlarla (D1 için: hiç kullanılmayan cümlelerle) kurulur; üç bölüm arasında aynı girdi yinelenmez.
Etiketler elle yazılmaz: sentetik olgularda hedef kurulur, girdi ondan deterministik türetilir (mevcut yardımcılar:
`megazeka_sayi.sayilar`, `.turkce`, `.varliklar`, `.sablonlar`); gerçek cümlelerde yalnız "hiçbir şey değişmez"
etiketi verilir ve bu, aşağıdaki güvenli biçim listesiyle garanti edilir.

## D1. Gerçek cümle negatifleri (girdi = hedef) · ~8.000 satır (derlemin elverdiği kadar)

Kaynak: Common Voice Türkçe cümle derlemi (CC0), `--cv` ile verilir (varsayılan
`../proje/megazeka/data/raw/common_voice_tr.txt`, satır başına bir cümle, 47.781 cümle). v2 verisindeki doğal
negatifler bu derlemin yalnız sayı kökü İÇERMEYEN cümleleriydi; burada tersine sayı kökü İÇEREN ama içindeki her sayı
köklü sözcüğün **kesin olarak sayı olmadığı** cümleler alınır.

Güvenli biçimler (cümledeki sayı köküyle başlayan HER sözcük bu listede olmalı; biri bile dışındaysa cümle alınmaz):
- `on-` zamirleri: `o`, `ona`, `onu`, `onun`, `onda`, `ondan`, `onunla`, `onca`, `onlar` ve bütün çekimleri, `onsuz`.
- `bir` ailesi: `bir`, `biraz`, `birkaç`, `birçok`, `birden`, `birdenbire`, `birlikte`, `birbiri` çekimleri, `biri`,
  `birisi`, `birer`, `birtakım`, `hiçbir` (zaten `hiç` ile başlar), `birlik`, `birleş-`, `birik-`, `biricik`.
  Dikkat: `bir` sayı sözcüğü komşusuysa (öncesinde/sonrasında başka sayı kökü, `buçuk`, `milyon` …) cümle alınmaz.
- `yüz` ad/fiil: `yüzü`, `yüzüm`, `yüzün`, `yüzünü`, `yüzüne`, `yüzünde`, `yüzünden`, `yüzler`, `yüzlerce`, `yüzey`,
  `yüzük`, `yüzme`, `yüzmek`, `yüzdü`, `yüzüyor`, `yüzsüz`, `yüzleş-`. Yalın `yüz` belirsizdir: alınmaz.
- `altı` → yalnız `altın*`, `altında`, `altına`, `altından`, `altındaki`, `altını` (ama `altını` + sayı bağlamı yoksa),
  `altüst`. Yalın `altı` alınmaz.
- `yedi` → yalnız çekimli fiil: `yedim`, `yedin`, `yedik`, `yediniz`, `yediler`, `yediği`, `yedir-`, `yedikten`.
  Yalın `yedi` alınmaz.
- `bin` → yalnız `bindi*`, `binmek`, `binme*`, `binip`, `binen`, `biner*`, `binecek*`, `binmiş*`, `bina*`, `binlerce`.
  Yalın `bin` ve `bine`, `bini` alınmaz.
- `kırk` → `kırkma*`; `elli`, `yirmi` … yalın sayılar alınmaz. `üç-` → `üçgen`; `beş-` → `beşik*`; `iki-` → `ikiz*`,
  `ikilem`, `ikinci` ALINMAZ (sıra sayısı belirsiz); `dokuz`, `sekiz`, `dört` yalın alınmaz; `dörtnala` alınır.
- `eksi-` → `eksik*`, `eksil-`; `yarım*`; `çeyrek*`; `milyonlarca`, `milyoner`; `sıfır` ALINMAZ.

Her seçilen cümle iki biçimde kullanılabilir: özgün (büyük harf + noktalama) ve düzleştirilmiş (küçük harf,
noktalamasız; `training/uret.py` içindeki `cv_duz`). Oran yaklaşık yarı yarıya; aynı cümlenin iki biçimi aynı bölümde
(train/validation/test) kalır. Bölüm, cümlenin md5'ine göre atanır (test %6, validation %6).
Hedef dağılım: zamir (`on-`) cümleleri en az 4.500 satır, `bir` ailesi en çok 3.000, kalanı öteki eş yazımlılar.

**Dışlama (zorunlu):** `data/v3/haric-md5.txt` dosyasında bağımsız ölçüm kümelerindeki cümlelerin özetleri var
(satır başına `md5(cv_duz(cümle))`, UTF-8). Özeti bu listede olan hiçbir cümle D1'e (hiçbir biçimde) alınmaz.

## D2. Atasözü ve deyimler (girdi = hedef) · ~4.000 satır

İçinde sayı sözcüğü geçen en az 250 ayrı Türkçe atasözü, deyim ve kalıplaşmış söz (kendi bilginle yaz; emin
olmadığın sözü uydurma). Sayı her zaman yazıyla kalır (SPEC-v2 B6), 10 ve üstü dahil: `kırk yılda bir`,
`bin bilsen de bir bilene danış`, `iki cambaz bir ipte oynamaz`, `dokuz köyden kovulur`, `yüz yüze`, `üç beş kuruş`,
`kırk yıl hatırı var`, `bin nasihatten bir musibet yeğdir`, `yedi kat yerin dibi`, `otuz iki dişini göstermek` …
Her söz hem yalın hem taşıyıcı içinde görünür (`dedem hep … derdi`, `ne demişler: …`, `… diye bir söz var`, cümle
ortasında deyim olarak); büyük harfli + noktalı ve düzleştirilmiş biçim. Sözlerin en az %15'i yalnız teste ayrılır.
D2 sözlerinin `cv_duz` özeti de `haric-md5.txt` ile karşılaştırılır; eşleşen söz yalın biçimde kullanılmaz.

## D3. `bir` + sayı kalıpları ve ölçü kararları · ~3.000 satır

- Madeni para/banknot: `bir elli kuruş` → `bir 50 kuruş`, `bir yirmi beş kuruşluk` → `bir 25 kuruşluk`,
  `bir yüz liralık çıkardı` → `bir 100 TL'lik çıkardı`, `iki tane elli kuruşluk` → `iki tane 50 kuruşluk`.
- Boy (karar 4): `bir elli boyunda` → `1,50 boyunda`, `bir yetmiş beş boyunda` → `1,75 boyunda`,
  `bir seksen boyundaki adam` → `1,80 boyundaki adam` (yalnız `bir` + onluk[+birlik] + `boy*`).
- `buçuk`lu aralık (karar 2): `bir buçuk iki saat` → `1,5-2 saat`, `iki buçuk üç kilo` → `2,5-3 kg`,
  `bir buçuk iki ay` → `1,5-2 ay`.
- `bir` belirsiz tanımlık + ardından gelen bağımsız sayı: `bir on dakika sonra` → `bir 10 dakika sonra`,
  `bir yirmi kişi kadar` → `bir 20 kişi kadar` (yaklaşıklık bildiren `bir`; aralık DEĞİL).
- Karşıt: gerçek aralık `beş on dakika` → `5-10 dakika`, `on on beş kişi` → `10-15 kişi` aynı taşıyıcılarda.
- `her biri`, `hiçbiri`, `ikisi de`, `birer` sayı yanında sözcük kalır: `her biri üç liradan` → `her biri 3 TL'den`.

## D4. Küçük sayı + ad, uzun gerçekçi cümlede · ~4.000 satır

Bağlamsız tek sözcüklük 0–9 yazıyla kalır (SPEC §1.1; karar 1): `sekiz kişi iki gündür çatıda uğraşıyordu`,
`dört katlı otelin`, `altı kişilik orkestra`, `üç mektubunu cevapsız bıraktı`, `iki gece önce`, `dokuz saat sürdü`,
`sekiz yaşında bir çocuk`, `yedi sene oturdum`, sayma/geri sayım `beş, dört, üç, iki…`.
Adlar en az 60 çeşit (kişi, çocuk, adam, kadın, gün, gece, hafta, ay, yıl, sene, saat, kat, katlı, kişilik, oda, kez,
defa, adım, satır, mektup, kardeş, ev, köy, at, kitap …). Cümleler 6–18 sözcük, roman/gündelik konuşma üslubunda,
yarısında virgül, tırnak ya da `…` var. Aynı taşıyıcılarda karşıt pozitif (en az %30): 10 ve üstü rakam olur
(`on iki kişi` → `12 kişi`, `kırk yaşında` → `40 yaşında`, `yirmi senedir` → `20 senedir`), bileşik süre tamamen rakam.

## D5. Cümle başı, tırnak ve noktalama içinde sayı · ~3.000 satır

Sayı büyük harfle cümleyi açar ya da tırnak/iki nokta/üç noktanın yanındadır; noktalama aynen korunur:
`"Kırk yaşında adam böyle yapar mı?" dedi.` → `"40 yaşında adam böyle yapar mı?" dedi.`,
`Yetmiş lira aylık…` → `70 TL aylık…`, `Şimdi ne istersin? Kırk beş mi?` → `Şimdi ne istersin? 45 mi?`,
`Yüz ellisi benim elbette…` → `150'si benim elbette…`, `Yanındakine: "Elli adım var." dedi.` → `…: "50 adım var." dedi.`,
tek başına sayı cümlesi `Yüz altmış dört.` → `164.`, `İki yüz on sekiz.` → `218.`.
Kardinal, para, yaş, yıl sayısı, ölçü ve aralık; 10–999 ağırlıklı, cümle başı payı en az %50. Tırnak işaretleri
`"…"`, `“…”` ve tırnaksız `:`; cümle sonu `.`, `!`, `?`, `…`. Yalın yıl (`Bin dokuz yüz otuz beş.`) üretilmez.
Soru eki (`mı/mi/mu/mü`) ayrı sözcüktür: hedefte girdideki haliyle aynen kalır (`Dört yüz doksan üç lira mı?` → `493 TL mı?`); yalnız kesme işaretiyle rakama ya da kısaltmaya bağlanan ekler kanonik okunuşa göre değişir.

## D6. `saat` sözcüksüz ve yüklem ekli saat · ~1.500 satır

`Yarın dokuzda gelin.` → `Yarın 9'da gelin.`, `akşam yedide buluşalım` → `akşam 7'de buluşalım`,
`Saat henüz dörttü.` → `Saat henüz 4'tü.`, `saat beşti` → `saat 5'ti`, `saat on ikiydi` → `saat 12'ydi`,
`toplantı üçteymiş` → `toplantı 3'teymiş`. Zaman zarfı (yarın, bugün, akşam, sabah, öğleden sonra, pazartesi …) +
bulunma/ayrılma/yönelme ekli saat; `saat` + sayı + `-DI`/`-(y)mIş`/`-DIr`. Ek, sayının okunuşuna göre (SPEC §2).
Karşıt negatif (en az %25): aynı zarflarla saat olmayan kullanım (`yarın ona söylerim`, `akşam onu gördüm`,
`sabah yedi ve çıktı`: değişmez).

## D7. Ekli para ve eski birimler · ~2.000 satır

İyelik ve ek-fiil: `yüz elli liram var` → `150 TL'm var`, `elli lirasını peşin aldı` → `50 TL'sini peşin aldı`,
`borcun yüz altmış beş liradır` → `165 TL'dir`, `otuz beş kuruşum var` → `35 kuruşum var`, `on lirası kaldı` →
`10 TL'si kaldı`, `beş liramız` → `5 TL'miz`, `fiyatı yirmi liraydı` → `20 TL'ydi`, `lira idi` → `TL idi`.
`TL`nin kanonik okunuşu `te le` (ince, ünlüyle biter): `TL'm`, `TL'n`, `TL'si`, `TL'miz`, `TL'niz`, `TL'leri`,
`TL'sini`, `TL'dir`, `TL'ydi`, `TL'ymiş`. `kuruş` sözcük kalır, ek bitişik.
Sözcük kalan eski/yerel birim ve para (sayı rakam olur, 10 ve üstü ya da bağlamlı): `doksan para` → `90 para`,
`kırk okka` → `40 okka`, `on beş arşın` → `15 arşın`, `yirmi dönüm`, `elli mecidiye`, `otuz altın`.

## D8. Sıra sayısı, `-lık` ve üleştirme kararları · ~1.500 satır

- Karar 3: sıra sayısı + sıfat + ad yazıyla kalır (`üçüncü uykusuz geceyi`, `ikinci büyük şehri`); unvan/görev adı
  yazıyla (`ikinci kaptan`, `birinci subay`, `üçüncü kâtip`, `ikinci müdür`). Karşıt: yalın sıra + ad rakam
  (`üçüncü kat` → `3. kat`, `ikinci madde` → `2. madde`).
- Karar 5: yaş tahmini `-lık` yazıyla (`altmışlık bir adam`, `ellilik kadın`, `yetmişlik ihtiyar`, `kırklık`);
  karşıt: nesnede rakam (`altmışlık bir kutu` → `60'lık bir kutu`, `yüzde ellilik` → `%50'lik`).
- Üleştirme yazıyla: `ellişer kuruşa`, `altmışar kuruşla`, `ikişer ikişer`, `onar lira` (SPEC-v2 B8).

## Çeşitlilik eşikleri (train dosyasında ölçülür, testle doğrulanır)

- D2–D8 toplamında en az 600 ayrı şablon; hiçbir şablon D2–D8 satırlarının %1'inden fazlası değil.
- Hiçbir ilk sözcük D2–D8 satırlarının %5'inden fazlası değil.
- Girdi = hedef satırlarının payı D genelinde %55–70 (D1 ve D2 tamamen negatif).
- Her alt olgu (D1 … D8) yukarıdaki satır sayısının en az %80'i.
- Eşikler olgu bazında yazılır; ayrıca her olgudan 40 rastgele satır gözle okunup rapora konur (v2'de `saatta`
  hatasını hiçbir eşik yakalamadı; `turkce.inflect` `saat` sözcüğünü kalın çekiyor, sarmalayıcıyla düzelt).

## Birleştirme (`training/v3_birlestir.py`)

- İlk çalıştırmada `data/train.jsonl` → `data/train-v2.jsonl`, `data/validation.jsonl` → `data/validation-v2.jsonl`
  kopyalanır (varsa dokunulmaz); v2 akışı hep bu dosyalardan okunur.
- `train.jsonl` = v2 train + D train, `validation.jsonl` = v2 validation + D validation (karıştırılmış, sabit tohum).
  Yeni satırlara `kaynak: "d"` yazılır. `data/test-v3.jsonl` = D test. `data/test.jsonl`, `test-v1.jsonl`,
  `test-v2.jsonl` donmuş kalır.
- Aynı girdiye farklı hedef veren satırlar iki taraftan da çıkarılır ve sayısı raporlanır. D'nin yeni kararlarıyla
  çelişen eski v2 satırları (ör. `altmışlık bir adam` → `60'lık`, `bir buçuk iki` sözcük) taranır; bulunanlar eski
  akıştan çıkarılır ve sayılır.
- `cv_duz` özeti `haric-md5.txt` içinde olan her satır (kaynağı ne olursa olsun) çıkarılır.
- `data/metadata-v3.json`: kaynak ve kategori sayıları, negatif payı, çıkarılan satır sayıları, tohum.
