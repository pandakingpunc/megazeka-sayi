# Megazeka-Sayı · v3 için netleşen kurallar (2026-11-16)

`docs/SPEC.md` ve `docs/SPEC-v2.md` geçerlidir. Gerçek metin ölçümünde (`evaluation/gercek.jsonl`) iki şartnamenin
yanıt vermediği beş durum çıktı; aşağıdaki kararlar bunları kapatır. Kaynak: kullanıcının 2026-11-16'da aktardığı
öneri (Opus); kullanıcı kendi yazım tercihinin olmadığını belirtip bunları benimsedi.

| # | Durum | Karar | Örnek |
|---|---|---|---|
| 1 | Küçük sayı (0–9) + yaş ya da süre sözcüğü (`yaş`, `saat`, `gün`, `gece`, `ay`, `yıl`, `sene`) | Yazıyla kalır (küçük sayı politikası). **Değerlendirmede rakamlı yazım da doğru sayılır.** | `sekiz yaşında`, `dokuz saat sürdü` (kabul: `8 yaşında`, `9 saat`) |
| 2 | `bir buçuk` içeren yaklaşık aralık | Rakam: ölçülen bir süre/miktar. "İçinde `bir` geçen aralık sözcük kalır" kuralı yalın `bir` içindir. | `bir buçuk iki saat` → `1,5-2 saat` |
| 3 | Sıra sayısı ile ad arasında sıfat; unvan/görev adı | Yazıyla: anlatım ya da unvandır, sıralanan madde değildir. | `üçüncü uykusuz gece`, `ikinci kaptan` |
| 4 | Birimi söylenmemiş boy ölçüsü | Rakam, ondalık virgülle. | `bir elli boyunda` → `1,50 boyunda` |
| 5 | Kaba yaş tahmini olarak `-lık` | Yazıyla. Sayılabilir nesnede `-lık` rakama bağlanır. | `altmışlık adam` (ama `altmışlık bir kutu` → `60'lık bir kutu`) |

Notlar:
- 1. kararın kapsamı yalnız tek sözcüklük 0–9 sayılardır; 10 ve üstü eskisi gibi rakam (`40 yaşında`), bileşik süre
  eskisi gibi tamamen rakam (`2 saat 15 dakika`, SPEC-v2 A5), `kişi`/`kat`/`adım` gibi adlarda yalnız yazıyla doğru.
- 3. kararın dışında kalan yalın "sıra sayısı + ad" eskisi gibi rakamdır (`3. kat`, `2. madde`). Anlatı cümlelerinde
  (`üçüncü günü akşama doğru`, `bir ikinci dansta`) iki denetçi ayrıştığı için ölçüm kümesinde iki yazım da kabul.
