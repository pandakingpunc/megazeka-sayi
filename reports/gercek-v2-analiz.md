# Gerçek metin ölçümü — v2.0 hata analizi (2026-11-16)

Sayılar `reports/gercek-v2.md` / `.json` dosyasından; sınıflandırma elle yapıldı.

## Küme

- Kaynak: Common Voice Türkçe cümle derlemi (CC0), 47.781 cümle. Sayı kökü içeren 9.363 cümleden sabit tohumla
  279'u seçildi (`evaluation/gercek_ornekle.py`): `bir` 30, `on` 30, öteki her kök en çok 10.
- Eğitimdeki doğal negatifler aynı derlemin yalnız sayı kökü **içermeyen** cümleleriydi; çakışma yok.
- Etiketler modelin çıktısı görülmeden, SPEC ve SPEC-v2'ye göre tek kişi tarafından yazıldı; çıktı görüldükten
  sonra değiştirilmedi.
- İkinci göz: GPT-6 Astra (Codex CLI, salt okunur, `reports/` klasörünü görmeden) 279 etiketi şartnameye göre denetledi;
  ayrıntı aşağıda. Buradaki sayılar o denetimden sonraki etiketlerle.
- 162 cümle değişmemeli, 117 cümle değişmeli. 16 cümlede şartnamenin açık bırakmadığı ikinci bir yazım `kabul`
  olarak işaretli (yalın `bin dokuz yüz otuz beş` yıl mı sayı mı, `bir buçuk iki saat`, `ikinci kaptanı`, `kırk yıl evinde oturdum`).
- Sınır: derlem ağırlıklı olarak eski roman, atasözü ve altyazı cümlesi; güncel konuşma (fiyat, telefon, saat,
  yüzde) az. Köke göre katmanlı olduğu için oranlar derlemin doğal dağılımını değil, köklerin eşit temsilini gösterir.

## Sonuç

| Sistem | Esnek doğru | Yanlış dönüşüm (162 negatif) | Pozitifte doğru (117) |
|---|---:|---:|---:|
| Girdiyi kopyala | 168/279 (%60,2) | 0 | 6 |
| Kural tabanlı | 106/279 (%38,0) | 123 (%75,9) | 67 |
| Model, korumasız | 230/279 (%82,4) | 30 (%18,5) | 98 (%83,8) |
| Model + koruma | 245/279 (%87,8) | 18 (%11,1) | 101 (%86,3) |

Koruma 16 ham hatayı düzeltti, 1 doğru çıktıyı bozdu (`Kırk elli lira…` → geri alındı).

## Korumalı çıktıdaki 34 hata

| Sınıf | n | Satırlar | Örnek |
|---|---:|---|---|
| Atasözü / deyimde sayı rakama çevrildi | 9 | 60, 68, 87, 110, 113, 115, 163, 166, 167 | `Yaş 70, iş bitmiş.` · `1.000 atın varsa bin dinlen` |
| Küçük sayı politikası (bağlamsız 0–9 rakam oldu) | 7 | 2, 93, 98, 127, 150, 152, 200 | `8 kişi`, `4 katlı otel`, `Beş, dört, üç, iki…` → `5432…` |
| `bir` + sayı uydurma aralık oldu | 4 | 19, 22, 70, 146 | `bir yirmi beş kuruşluk` → `1-25 kuruşluk` |
| Sayı bozuldu / uyduruldu | 4 | 6, 13, 116, 117 | cümle başında `Kırk yaşında` → `1940 yaşında`; `yüz seksen öbür gün` → `184 gün` |
| Ek ya da kapsam | 3 | 43, 77, 112 | `50 TL'sinı`; `her biri` → `her 1'i`; `kırk okka` dönüşmedi |
| Kapanış tırnağından sonrası kesildi, koruma hepsini geri aldı | 2 | 27, 74 | `"…165 TL'dir.` (kapanış `"` ve ` dedi.` yok) |
| Saat bağlamı açıkken dönüşmedi | 2 | 120, 159 | `Yarın dokuzda gelin` · `Saat henüz dörttü.` |
| Zamir / `bir` sızıntısı | 2 | 243, 245 | `Bir gece 10'u çağırdım` · `1 müddet` |
| Koruma doğru çıktıyı geri aldı | 1 | 76 | `Kırk elli lira…` |

## Ne gösteriyor

1. **Ham model zamirde zayıf, yükü koruma taşıyor.** 30 gerçek `ona/onu/onun` cümlesinin 10'unda ham model
   `10'u`, `10'un` yazdı; koruma 8'ini kurtardı. Üreteç testlerinde bu görünmüyordu.
2. **Gizli küme 3'teki yanlış dönüşüm oranı gerçek metinde de aynı:** ham %18,5 (gizli küme 3: %18,5). O küme
   iyimser ya da kötümser değilmiş.
3. **En büyük tek sınıf atasözü/deyim (9/12 yanlış).** Eğitimde ~80 sabit deyim vardı; model listeyi öğrenmiş,
   "atasözü" kavramını değil. Bu bir politika sorusu da: `Otuz iki dişten çıkan` rakamla yazılırsa hata mı?
4. **Küçük sayı politikası gerçek cümlede tutmuyor** (30 cümlenin 6'sı, ayrıca `iki çeyrek`): model `kişi`, `yaş`,
   `saat`, `kat` gibi sözcükleri birim bağlamı sayıyor.
5. **Sessiz içerik kaybı var:** `1940 yaşında`, `184 gün`, `1,5 saat` (`iki` düştü), tırnaktan sonra kesilen cümle.
   Bunlar sayıyı ya da metni değiştiriyor ve koruma hepsini yakalamıyor (4'ü geçti). Gidiş-dönüş denetimi
   (çıktıyı yeniden sözlüleştirip girdiyle karşılaştırmak) bu dördünü ve korumanın zaten yakaladığı `41 pazarlık`,
   `2-0'a çocuk` gibilerini kuralsız yakalar.
6. `bir` + sayı (`bir elli kuruş`, `bir yirmi beş kuruşluk`) eğitimde hiç yok; model en yakın bildiği kalıba
   (aralık) çekiyor.

## İkinci göz denetimi (GPT-6 Astra, 2026-11-16)

279 satırın 10'una itiraz etti; sayı değeri, binlik ayırıcı, yıl, tarih, birim ve ek hatası bulmadı. Küçük sayı
yorumunu ve 12 atasözünün sözcük bırakılmasını (SPEC-v2 B6) doğru buldu.

| Satır | İtiraz | Karar |
|---|---|---|
| 74, 77 | `150 liram`, `50 lirasını` kabulden çıksın (iyelik TL'yi engellemez) | uygulandı |
| 120, 159 | `Yarın dokuzda`, `Saat henüz dörttü` olduğu gibi bırakılamaz, saat bağlamı açık | uygulandı; model ikisini de dönüştürmediği için 2 yeni hata |
| 171 | `Üçüncü günü` kabulden çıksın (sıra sayısı + ad) | uygulandı |
| 207 | `bir ikinci dansta` → hedef `bir 2. dansta` olmalı | uygulandı, sözcük biçimi kabulde kaldı |
| 15 | `üç buçuk kuruş` kalıp olabilir, sözcük biçimi kabule girsin | uygulandı |
| 157 | `Dört beş ajansı` saat de olabilir (`4.05 ajansı`) | kabule eklendi |
| 13 | `bir buçuk iki saat` sözcük kalmalı (`bir` içeren aralık) | uygulanmadı: `bir buçuk` 1,5'tir, kural yalın `bir` için; iki yazım da zaten kabul |
| 172 | `üçüncü uykusuz geceyi` rakamla tercih | değişmedi, iki yazım da kabul |

Etki: esnek sonuç 247 → 245 (%88,5 → %87,8). Şartnamede açık kalan sorular: yaş/süre sözcükleri küçük sayıyı ne zaman
rakama zorlar (A6 ile A8 arası); `bir buçuk` içeren aralık; sıra sayısı ile ad arasına sıfat girmesi ve `ikinci kaptan`
gibi görev adları; `bir elli boyunda`; `altmışlık`/`milyonluk` ile `-lık` eki arasındaki sınır.

## v3 için sıralama

1. Kod, eğitim yok: gidiş-dönüş denetimi; kapanış tırnağı kesilmesi (çıktı girdiden kısa bitiyorsa kuyruğu geri ekle).
2. Veri: gerçek cümlelerden zamir negatifleri (derlemde `on` köklü 2.126 cümle var), atasözü/deyim negatifleri,
   `bir` + sayı, küçük sayı + `kişi/yaş/saat/kat/gece`, cümle başında büyük harfli sayı.
3. Bu kümeyle çakışmayı önlemek için eğitim verisine alınacak gerçek cümlelerden `evaluation/gercek.jsonl`
   girdileri çıkarılmalı.

## Şartname kararları ve yeni koruma (2026-11-16, ikinci tur)

Yukarıdaki bölümler ilk ölçümün kaydıdır; güncel sayılar bu bölümdedir.

**Etiketler:** beş açık soru `docs/SPEC-v3-kararlar.md` ile kapandı ve kümeye işlendi (küçük sayı + yaş/süre satırlarında
rakamlı yazım da kabul; `bir buçuk iki saat` yalnız `1,5-2 saat`; `üçüncü uykusuz gece`, `ikinci kaptan`, `altmışlık`
yalnız yazıyla; `bir elli boyunda` yalnız `1,50 boyunda`). 163 değişmez, 116 değişir, 25 satır çok cevaplı.

**Koruma:** `src/megazeka_sayi/dogrula.py` çıktıdaki rakamların girdideki sayı sözcüklerinden türetilebildiğini denetler
(eğitim yok). Ayrıca bölge kenarındaki düşen noktalama girdiden tamamlanır, para/ölçü sözcüklerinde iyelik ve `-dır`
ekleri tanınır. Üreteç altın çiftlerinde (8.492 satır) yeni geri alma yok; rakamı bozulmuş 21.157 çıktının hepsi yakalandı
(eski koruma %2,2).

| Küme | Eski koruma | Yeni koruma |
|---|---:|---:|
| Gerçek metin (279, yeni etiketlerle) | 246 (%88,2) | 249 (%89,2) |
| test (2.000) | %98,6 | %98,6 |
| test-v2 (1.400) | %97,4 | %97,4 |
| test-v1 donmuş (2.000) | %99,8 | %99,8 |
| zorluk / gizli 2 / gizli 3 | %98 / %98 / %91,6 | %98 / %98 / %91,6 |

Gerçek metinde değişen satırlar: 27 (`165 TL'dir."`), 76 (`40-50 TL…`) düzeldi; 117 `1940 yıl` → girdi (kabul); 116
`1940 yaşında` ve 13 `1,5 saat` artık girdiye dönüyor (hâlâ yanlış ama içerik bozulmuyor). Bozulan satır yok.
Yeni açık: 74'te çıktı `150 TL var` oldu (`liram`daki iyelik düştü); eski koruma bunu girdiye döndürüyordu.

Kalan 30 hata: atasözü/deyim 9, `bir` + sayı 4, küçük sayı 4, dönüşmeyen/geri alınan sayı 4 (6, 13, 112, 116), ek 3,
saat 2, zamir 2, `altmışlık` → `60'lık` 1, `3. uykusuz` 1. Bunların çoğu eğitimde hiç bulunmayan kalıplar; koruma
değil veri işi.
