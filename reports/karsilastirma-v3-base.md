# Megazeka-Sayı ByT5-base deneyi

18 Kasım 2026 · **Yayın kararı: v2.5 kullanımda kalıyor.** Ana seçim kümesinde base beş hatayı düzeltti ve üç yeni hata yaptı. Dönüşüm gereken 54 cümlede iki model de 49 doğru yaptı. Diğer gerçek metin kümesinde base toplamda bir cümle geriledi. Zorluk ve üreteç testlerindeki kazanımlara rağmen gerçek metindeki net fark v3 yayınını gerekçelendirecek büyüklükte görülmedi.

## Korumalı çıkarım sonuçları

Gerçek kümelerde şartnamenin kabul ettiği alternatif yazımlar geçerlidir. Diğer satırlar birebir eşleşmedir. Küçük zorluk kümelerinde bir cümle birkaç yüzde puanına karşılık gelir.

| Küme veya ölçüt | v2.5 small | Base |
|---|---:|---:|
| Gerçek 2, birincil seçim | 140/150 (%93,3) | 142/150 (%94,7) |
| Gerçek 2, yanlış değiştirilen cümle | 5/96 | 3/96 |
| Gerçek 2, dönüşüm gerekenlerde doğru | 49/54 | 49/54 |
| Gerçek 1 | 267/279 (%95,7) | 266/279 (%95,3) |
| Gerçek 1, yanlış değiştirilen cümle | 8/163 | 5/163 |
| Gerçek 1, dönüşüm gerekenlerde doğru | 112/116 | 108/116 |
| Gizli zorluk 3 | 77/83 | 82/83 |
| Gizli zorluk 2 | 49/50 | 48/50 |
| İlk zorluk | 98/100 | 99/100 |
| Eski üreteç testi | 1.982/2.000 | 1.985/2.000 |
| Donmuş v1 | 1.993/2.000 | 1.995/2.000 |
| v2 yeni kaynakları | 1.368/1.400 | 1.385/1.400 |
| Güncel üreteç testi, 5.494 örnek | %97,6 | %98,3 |
| Aynı testte yanlış değiştirilenlerin oranı, 2.842 negatif | %2,5 | %1,5 |

Base “Adı çıktı dokuza, inmez sekize.” sözünü korudu. Ekli aralığı da düzeltti (“on yedi on sekizden” → “17-18'den”). Buna karşılık v2.5'in doğru çevirdiği “beş on adım” için “beş 10 adım” yazdı ve “kırk yaşlarında” ifadesini sözcük olarak bıraktı. Gerçek 1 önceki veri geliştirmesine yön vermişti. Gerçek 2 eğitimden ayrı tutuldu, önceki sürümün hata listesi bu deneyden önce biliniyordu. Bu deneyde veri, etiket ve koruma filtresi değiştirilmedi.

## Eğitim ve kaynaklar

Aynı 136.029 eğitim çifti ve 5.769 doğrulama örneği kullanıldı. ByT5-base + LoRA rank 32, batch 4 × birikim 4, etkin batch 16, tohum 42, RTX 4060 ve bf16. Eğitim 9.000 adımı 2 saat 48 dakikada tamamladı. Tepe GPU tensör belleği 3,76 GiB. Her 250 adımda sabit 512 örnekle doğrulama yapıldı. En iyi kayıt 8.000. adımda 508/512 (small 504/512). Karşılaştırmada bu kayıt kullanıldı. Aynı altı testin toplu değerlendirmesi small koşusunda 231 saniye, base koşusunda 283 saniye sürdü. Bu süreler iki ayrı koşuya aittir.

Yerel ağırlıklar: `models/checkpoints/v3-base-best`. [Ayarlar](../configs/v3-base.json) · [Eğitim geçmişi](history-v3-base.jsonl) · [Gerçek 2 small](gercek2-v2.5.md) · [Gerçek 2 base](gercek2-v3-base.md) · [Gerçek 1 small](gercek-v2.5.md) · [Gerçek 1 base](gercek-v3-base.md) · [Zorluk ve üreteç testleri small](degerlendirme-v2.5.md) · [Zorluk ve üreteç testleri base](degerlendirme-v3-base.md) · [5.494 örnekte small](../README.md) · [5.494 örnekte base](test-v3-base.json).
