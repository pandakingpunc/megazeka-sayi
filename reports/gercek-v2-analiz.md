# Gerçek metin ölçümü — v2.0 hata analizi (2026-11-16)

Sayılar `reports/gercek-v2.md` / `.json` dosyasından; sınıflandırma elle yapıldı.

## Küme

- Kaynak: Common Voice Türkçe cümle derlemi (CC0), 47.781 cümle. Sayı kökü içeren 9.363 cümleden sabit tohumla
  279'u seçildi (`evaluation/gercek_ornekle.py`): `bir` 30, `on` 30, öteki her kök en çok 10.
- Eğitimdeki doğal negatifler aynı derlemin yalnız sayı kökü **içermeyen** cümleleriydi; çakışma yok.
- Etiketler modelin çıktısı görülmeden, SPEC ve SPEC-v2'ye göre tek kişi tarafından yazıldı; çıktı görüldükten
  sonra değiştirilmedi. İkinci etiketleyici yok.
- 163 cümle değişmemeli, 116 cümle değişmeli. 19 cümlede şartnamenin açık bırakmadığı ikinci bir yazım `kabul`
  olarak işaretli (yalın `bin dokuz yüz otuz beş` yıl mı sayı mı, `yarın dokuzda`, `üçüncü günü`, `liram`).
- Sınır: derlem ağırlıklı olarak eski roman, atasözü ve altyazı cümlesi; güncel konuşma (fiyat, telefon, saat,
  yüzde) az. Köke göre katmanlı olduğu için oranlar derlemin doğal dağılımını değil, köklerin eşit temsilini gösterir.

## Sonuç

| Sistem | Esnek doğru | Yanlış dönüşüm (163 negatif) | Pozitifte doğru (116) |
|---|---:|---:|---:|
| Girdiyi kopyala | 170/279 (%60,9) | 0 | 7 |
| Kural tabanlı | 109/279 (%39,1) | 124 (%76,1) | 70 |
| Model, korumasız | 232/279 (%83,2) | 30 (%18,4) | 99 (%85,3) |
| Model + koruma | 247/279 (%88,5) | 18 (%11,0) | 102 (%87,9) |

Koruma 16 ham hatayı düzeltti, 1 doğru çıktıyı bozdu (`Kırk elli lira…` → geri alındı).

## Korumalı çıktıdaki 32 hata

| Sınıf | n | Satırlar | Örnek |
|---|---:|---|---|
| Atasözü / deyimde sayı rakama çevrildi | 9 | 60, 68, 87, 110, 113, 115, 163, 166, 167 | `Yaş 70, iş bitmiş.` · `1.000 atın varsa bin dinlen` |
| Küçük sayı politikası (bağlamsız 0–9 rakam oldu) | 7 | 2, 93, 98, 127, 150, 152, 200 | `8 kişi`, `4 katlı otel`, `Beş, dört, üç, iki…` → `5432…` |
| `bir` + sayı uydurma aralık oldu | 4 | 19, 22, 70, 146 | `bir yirmi beş kuruşluk` → `1-25 kuruşluk` |
| Sayı bozuldu / uyduruldu | 4 | 6, 13, 116, 117 | cümle başında `Kırk yaşında` → `1940 yaşında`; `yüz seksen öbür gün` → `184 gün` |
| Ek ya da kapsam | 3 | 43, 77, 112 | `50 TL'sinı`; `her biri` → `her 1'i`; `kırk okka` dönüşmedi |
| Kapanış tırnağından sonrası kesildi, koruma hepsini geri aldı | 2 | 27, 74 | `"…165 TL'dir.` (kapanış `"` ve ` dedi.` yok) |
| Zamir / `bir` sızıntısı | 2 | 243, 245 | `Bir gece 10'u çağırdım` · `1 müddet` |
| Koruma doğru çıktıyı geri aldı | 1 | 76 | `Kırk elli lira…` |

## Ne gösteriyor

1. **Ham model zamirde zayıf, yükü koruma taşıyor.** 30 gerçek `ona/onu/onun` cümlesinin 10'unda ham model
   `10'u`, `10'un` yazdı; koruma 8'ini kurtardı. Üreteç testlerinde bu görünmüyordu.
2. **Gizli küme 3'teki yanlış dönüşüm oranı gerçek metinde de aynı:** ham %18,4 (gizli küme 3: %18,5). O küme
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

## v3 için sıralama

1. Kod, eğitim yok: gidiş-dönüş denetimi; kapanış tırnağı kesilmesi (çıktı girdiden kısa bitiyorsa kuyruğu geri ekle).
2. Veri: gerçek cümlelerden zamir negatifleri (derlemde `on` köklü 2.126 cümle var), atasözü/deyim negatifleri,
   `bir` + sayı, küçük sayı + `kişi/yaş/saat/kat/gece`, cümle başında büyük harfli sayı.
3. Bu kümeyle çakışmayı önlemek için eğitim verisine alınacak gerçek cümlelerden `evaluation/gercek.jsonl`
   girdileri çıkarılmalı.
