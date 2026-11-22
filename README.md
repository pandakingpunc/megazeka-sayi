# Megazeka-Sayı · Türkçe sayı normalleştirici

Ses tanıma (ASR) sistemlerinin **yazıyla verdiği sayıları** TDK yazım kurallarına uygun **rakam biçimine**
çeviren bir model. Sayı dışındaki metni olduğu gibi bırakmayı amaçlar. Yerelde eğitilmiş **ByT5-base +
LoRA (r=32)** modeli, ağırlıklar indirildikten sonra çevrimdışı çalışır. Kardeş projesi
[Megazeka](https://github.com/pandakingpunc/megazeka) (Türkçe yazım düzeltici) ile aynı altyapıyı kullanır.

| Ses sisteminden çıkan metin | Megazeka-Sayı |
|---|---|
| toplam bin iki yüz elli lira elli kuruş | toplam 1.250,50 TL |
| yüzde on iki buçuk indirim | %12,5 indirim |
| iki buçuk kilogram domates | 2,5 kg domates |
| saat on dört otuzda görüşelim | saat 14.30'da görüşelim |
| sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi | 0532 123 45 67 |
| sekiz kasım iki bin yirmi altıda doğdu | 8 Kasım 2026'da doğdu |
| saat yedide yemek **yedik** | saat 7'de yemek **yedik** |
| akşam yemeğini **yedi** | akşam yemeğini **yedi** (değişmez) |
| masanın **altında** / **ona** söyledim / **dört gözle** | değişmez |

Asıl zorluk bağlamdır. "yedi" hem sayı hem fiil, "altı" hem sayı hem "alt", "ona" hem 10'a hem zamir,
"bin" hem 1.000 hem "binmek". Bağlama bakmadan her sayı sözcüğünü çeviren bir kural sistemi bu
cümleleri bozar ("yemeğini 7").

## Sonuçlar (v3.0)

"Girdiyi kopyala" hiçbir şeyi değiştirmeyen başlangıç değeridir. "Kural tabanlı" bağlama bakmadan her sayı
sözcüğü dizisini rakama çevirir. Yanlış dönüşüm, değişmemesi gereken cümlelerin (girdi = hedef) ne kadarının
değiştirildiğidir; parantezdeki sayı bu ölçüme giren cümle sayısıdır. Kural tabanlı taban çizgisi:
[`src/megazeka_sayi/kural_tabani.py`](src/megazeka_sayi/kural_tabani.py). Bütün model sonuçları koruma
filtresiyle ölçüldü; v2.5 ve 18 Kasım ByT5-base adayının ağırlıkları v3.0 filtresiyle yeniden ölçüldü.

**Gerçek metin.** Common Voice Türkçe'den (CC0) sayı sözcüğü içeren cümleler örneklendi ve şartnameye göre
elle etiketlendi. Üreteç şablonu kullanılmadı. Hedef yazımla veya kabul edilen öteki yazımla eşleşen
çıktılar doğru sayıldı.

| Küme | Girdiyi kopyala | Kural tabanlı | v2.5 | **v3.0** | Yanlış dönüşüm v2.5 → v3.0 (negatif n) |
|---|---:|---:|---:|---:|---:|
| Gerçek küme 3 (198), yeni, seçim kümesi | %63,1 | %34,3 | %92,4 (183) | **%95,5 (189)** | %9,2 → %5,0 (120) |
| Gerçek küme 2 (150), geliştirme | %64,7 | %36,7 | %93,3 (140) | **%96,7 (145)** | %5,2 → %2,1 (96) |
| Gerçek küme 1 (279), geliştirme | %59,9 | %40,9 | %95,7 (267) | **%96,1 (268)** | %4,9 → %3,7 (163) |

Üç kümedeki toplam 627 cümleden v2.5 590'ını, v3.0 602'sini doğru verdi. 18 Kasım'daki ara ByT5-base
adayı aynı filtreyle 594 doğru verdi.

Gerçek küme 3 v3.0 için yeni örneklendi. Bu 198 cümle eğitim, test ve öteki gerçek kümelerle çakışmaz
ve model çıktısına bakılmadan etiketlendi. Yine de tamamen kör değildir: eski modellerin bu kümedeki hataları
v3.0 verisi yazılmadan önce görüldü (benzer şablonlar ayrıca ayıklandı), ayrıca 7.500. ve 9.000. adımlardaki
kontrol noktaları arasında seçim bu kümeyle yapıldı. Bu yüzden buradaki sonuç hafif iyimserdir.

Gerçek küme 2 v2.5 için **görülmemiş** kümeydi. v3.0'ın yeni verisi, önceki ByT5-base adayının gerçek
küme 1 ve 2'deki hata sınıflarına bakılarak tasarlandı. Cümlelerin kendisi ve onlara benzeyen şablonlar
eğitimden çıkarıldı. Yine de bu iki küme artık geliştirme kümesidir ve sonuçları şişkin olabilir.
Etiketler depoda yer alır. [Gerçek küme 1](evaluation/gercek.jsonl), [gerçek küme 2](evaluation/gercek2.jsonl),
[gerçek küme 3](evaluation/gercek3.jsonl).

**Elle yazılmış gizli kümeler.** Her küme, o sürümün verisini yazan taraf görmeden, üreteçten bağımsız
elle yazıldı. Gizli küme 3 v2.0'ın yeni biçimlerini ölçer. Gizli küme 2 v1.0 içindi. Doğru saymak için
hedefle tam eşleşme gerekir. [Gizli küme 3](evaluation/challenge3.jsonl), [gizli küme 2](evaluation/challenge2.jsonl).

| Sistem | Gizli küme 3 (83) | Yanlış dönüşüm (27) | Gizli küme 2 (50) | Yanlış dönüşüm (21) |
|---|---:|---:|---:|---:|
| Girdiyi kopyala | %32,5 | %0 | %42,0 | %0 |
| Kural tabanlı | %43,4 | %63,0 | %56,0 | %52,4 |
| Megazeka-Sayı v1.0 | %49,4 | %37,0 | %94,0 | %9,5 |
| Megazeka-Sayı v2.0 | %91,6 | %18,5 | %98,0 | %0 |
| Megazeka-Sayı v2.5 | %92,8 | %7,4 | %98,0 | %0 |
| **Megazeka-Sayı v3.0** | **%97,6** | **%7,4** | **%98,0** | **%0** |

**Üreteç test kümeleri.** Eğitimde hiç kullanılmamış taşıyıcı şablonlarla üretildi. Sonuçlar tam eşleşmedir.

| Küme | Kural tabanlı | v2.5 | **v3.0** | v3.0 yanlış dönüşüm (negatif n) |
|---|---:|---:|---:|---:|
| v1.0 test kümesi (2.000) | %59,2 | %99,1 | **%99,3** | %0,4 (802) |
| İlk iç sürümün dondurulmuş testi (2.000) | %53,2 | %99,7 | **%99,8** | %0 (776) |
| v2.0 yeni kaynaklar testi (1.400) | %42,3 | %97,7 | **%98,9** | %0,8 (379) |
| v2.5 testi (5.494) | %35,5 | %97,6 | **%98,9** | %0,8 (2.842), v2.5'te %2,5 |

**İlk elle yazılmış küme (100 cümle).** v3.0 %97, v2.5 %98. Bu küme **şişkindir** çünkü v1.0, ilk
sürümün bu kümedeki hatalarına bakılarak geliştirildi. v3.0 burada iki yeni hata yaptı.
`bir kilo un iki litre süt al` girdisinden `bir kg un 2 L süt al` çıktı ve `altıncı durakta` yazıyla kaldı.

Ham ölçümler ve hata örnekleri raporlarda yer alır. [Üreteç ve gizli kümeler](reports/degerlendirme-v3e-base-latest.md),
[gerçek küme 3](reports/gercek3-v3e-base-latest.md), [gerçek küme 2](reports/gercek2-v3e-base-latest.md),
[gerçek küme 1](reports/gercek-v3e-base-latest.md).

Eski ağırlıkların yeni filtreyle yeniden ölçümleri `*-k2.md` raporlarında yer alır. Gerçek küme 3'ün
yeniden ölçümleri ayrı raporlardadır. [v2.5](reports/gercek3-v2.5.md),
[18 Kasım ByT5-base adayı](reports/gercek3-v3-base-best.md).

Gerçek metin çalışmasının ayrıntıları ve önceki sonuçlar da depoda yer alır.
[Gerçek metin analizi](reports/gercek-v2-analiz.md), [v2.0 değerlendirmesi](reports/degerlendirme-v2.md),
[v1.1 değerlendirmesi](reports/degerlendirme-v1.1.md).

### v3.0'da ne değişti

- **Taban model ByT5-base oldu.** LoRA r=32 ile 21,5 milyon parametre eğitildi. Adaptör 86 MB. Yayınlanan
  ağırlık 9.000. adımdan.
- **Hedefli veri kaynağı (E).** Elle etiketlenen 453 gerçek Common Voice cümlesi noktalamalı ve düz (ASR'ye
  benzer) biçimleriyle eklendi; eğitim dosyasında bu satırlar iki kez yer alır.
  Yaş ve iyelik eki (`kırkını geçmiş` → `40'ını geçmiş`, `seksen yaşındayım` → `80 yaşındayım`), yan yana
  aralık (`beş on adım` → `5-10 adım`, `üç dört kişi` → `3-4 kişi`) ve resmî metinde art arda sıra sayıları
  (`on ikinci maddenin birinci fıkrası` → `12. maddenin 1. fıkrası`) için şablonlar ve 29 yeni deyim eklendi.
  Ölçüm kümelerine benzeyen şablonlar elle ayıklandı.
- **Koruma filtresi iyelik ekli onlukları tanıyor.** `ellisinden` ve `kırkını` artık sayı olarak tanınıyor.
  Önceden model `50'sinden` biçimini doğru üretse bile filtre dönüşümü geri alıyordu.
- **Yaşla ilgili şartname kararları.** Yaş tahmini olan `-lık` biçimleri yazıyla kalır (`otuz beşlik kadın`).
  Küçük sayı yaş veya süre bildiren bir sözcükle kullanıldığında rakamlı yazım da doğru sayılır
  (`sekiz yaşında` ve `8 yaşında`). [Şartname kararları](docs/SPEC-v3-kararlar.md).

v2.5'te bilinen hatalardan bazıları düzeldi. `on ikinci maddenin birinci fıkrası` artık `12. maddenin 1. fıkrası`,
`on yedi on sekizden` artık `17-18'den`, `üç dört kişiden` ise `3-4 kişiden` biçiminde çıkıyor.
`Adı çıktı dokuza, inmez sekize` değişmeden kalıyor.

### Bilinen hatalar

- Bazı atasözleri ve deyimler hâlâ değişiyor. `Kasım yüz elli, yaz belli` → `Kasım 150`,
  `Yaş yetmiş, iş bitmiş` → `Yaş 70`, `Otuz iki dişten çıkan` → `32 dişten`,
  `Mart dokuzunda çıra yak` → `Mart 9'unda`.
- Aralık kuralı fazla genelleşebiliyor. `dört dörtlük` → `4-4'lük`, `dört bir yanımda` → `4-1 yanımda`.
- Fiil olan `yedi` bazen sayıya dönüşüyor. `elmayı yedi sonra uyudu` → `elmayı 7 sonra uyudu`.
- Yaşın `-lık` biçimi bazen rakama dönüşüyor. `otuz beşlik kadın` → `35'lik`.
- Virgülle ayrılmış kaba tutarlar birleşebiliyor. `seksen, yüz bin lirası` → `80,100.000 TL'si`.
- `bin` bazen çevrilmiyor. `Belki bini de aşar` cümlesinde `bini` kalıyor (doğrusu `1.000'i`).
  `bir buçuk ay` da yazıyla kalıyor.
- Veri sentetik ve gerçek cümle karışımıdır, ama gerçek ASR çıktısındaki tanıma hatalarıyla (yanlış
  duyulmuş sözcükler) test edilmedi. Gerçek kümeler edebî ağırlıklı Common Voice cümleleridir; haber,
  finans ya da konuşma dili için ayrı ölçüm yok.

## Yazım kuralları

Ayrıntılı yazım kuralları şartnamede ve eklerinde yer alır. [Temel şartname](docs/SPEC.md),
[v2.0 ekleri](docs/SPEC-v2.md), [v3.0 kararları](docs/SPEC-v3-kararlar.md).

- Binlik ayırıcı nokta, ondalık ayırıcı virgüldür (`1.250`, `3,14`). Yıl, telefon ve kodlar noktasızdır
  (`2026`, `0842`).
- Lira `TL` olarak yazılır (`1.250,50 TL`). Dolar ve avro gibi yabancı paralar sözcük kalır (`100 dolar`).
- Yüzde `%12,5`, saat `14.30`, tarih `8 Kasım 2026` biçiminde yazılır. Belirli tarihte ay adı büyük harfle başlar.
- Birimler TDK kısaltmasıyla yazılır (`kg`, `g`, `mg`, `km`, `m`, `cm`, `L`, `m²`, `m³`, `GB`, `kWh`, `°C`).
- Sıra sayısı ardından ad gelirse rakamla yazılır (`3. kat`, `21. yüzyıl`). Yüklem olarak sözcük kalır
  (`birinci oldu`).
- Ekler kesmeyle ayrılır ve rakamın okunuşuna uyar (`4'e`, `2'ye`, `TL'ye`, `kg'dan`, `14.30'da`, `1990'larda`).
- Bağlamsız tek sözcüklük 0–9 sayıları sözcük kalır (`iki kişi geldi`). 10 ve üstü ile birim, para, saat,
  tarih gibi bağlamlardaki sayılar rakama çevrilir (`on iki kişi` → `12 kişi`, `iki kilo` → `2 kg`).
  Belirsiz tanımlık olan `bir` her zaman sözcük kalır. Eğitim verisi `--politika rakamla` ile her sayıyı
  rakama çevirecek biçimde de üretilebilir.
- Kesirler ve deyimler sözcük kalır (`üçte bir`, `yarım kilo`, `dört gözle`, `kırk yılda bir`, `ikinci el`).

## Mimari

- **Model.** `google/byt5-base` + LoRA (r=32). Bayt düzeyinde çalıştığı için rakam ve Türkçe ekler için uygundur.
- **Veri.** Büyük bölümü sentetik ve **ters yönde** üretilir. Önce doğru yazılı cümle kurulur, sonra
  belirlenimci bir sözlüleştirici onu konuşma biçimine çevirir. Eğitim verisi 142.439 satırdır ve 6.422'si
  E kaynağından gelir. Yaklaşık %38'i değişmemesi gereken cümlelerdir. Bunlar eş yazımlı sözcükler, deyimler,
  zaten rakamlı metinler ve Common Voice'tan (CC0) gerçek cümleler içerir. Doğrulama kümesi 6.265 satırdır.
- **Koruma filtresi.** Model çıktısı sözcük düzeyinde girdiyle hizalanır. Sayı dışı bir sözcüğün değiştiğini
  veya rakamın girdideki sayı sözcüklerinden türemediğini saptadığında o bölgeyi geri alır. Düşen cümle sonu
  noktalamasını geri koyar.
- **Eğitim.** RTX 4060 8 GB'ta 9.000 adım yaklaşık 3 saat 40 dakika sürdü. Yığın boyutu 4, gradyan birikimi 4.
  bf16 kullanıldı ve tepe VRAM kullanımı 3,8 GB oldu.

## Kurulum ve kullanım

Python 3.11-3.13. PyTorch'u kendi donanımınıza göre kurun (https://pytorch.org), sonra:

```bash
pip install -r requirements.txt
```

`cikarim.py` bir Hugging Face depo adıyla çağrıldığında taban modeli adaptörün yapılandırmasından okur.
İlk çalıştırmada adaptör ve ByT5-base (yaklaşık 2,3 GB) indirilir.

```bash
PYTHONPATH=src python -m megazeka_sayi.cikarim --checkpoint pandakingpunc/megazeka-sayi-byt5-tr-itn "yüzde on iki buçuk indirim"
```

Modeli `transformers` ve `peft` ile doğrudan da kullanabilirsiniz. Bu örnekte koruma filtresi devreye girmez.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

tok = AutoTokenizer.from_pretrained("google/byt5-base")
base = AutoModelForSeq2SeqLM.from_pretrained("google/byt5-base")
model = PeftModel.from_pretrained(base, "pandakingpunc/megazeka-sayi-byt5-tr-itn").eval()

x = tok(["toplam bin iki yüz elli lira elli kuruş"], return_tensors="pt")
y = model.generate(**x, max_new_tokens=200, do_sample=False)
print(tok.batch_decode(y, skip_special_tokens=True))  # ['toplam 1.250,50 TL']
```

Model girdiyi tek parça olarak işler; 190 bayttan uzun metinleri cümle cümle verin
(`cikarim.py` bunu sözcük sınırından bölerek kendisi yapar).

### Veriyi üretmek ve yeniden eğitmek

```bash
PYTHONPATH=src python training/uret.py            # v1.0 akışı: data/{train,validation,test}.jsonl
PYTHONPATH=src python training/v2_sayisal.py --out data/v2 --seed 2201 --train 16000 --validation 400 --test 500
PYTHONPATH=src python training/v2_tuzak.py --out data/v2 --seed 2202 --train 10000 --validation 300 --test 400
PYTHONPATH=src python training/v2_bicim.py --out data/v2 --seed 2203 --train 14000 --validation 400 --test 500
PYTHONPATH=src python training/v2_birlestir.py    # hepsini birleştirir, belirsiz telefon satırlarını eler
PYTHONPATH=src python training/v3_gercek.py --cv <common-voice-cümleleri> --out data/v3   # v2.5 kaynağı
PYTHONPATH=src python training/v3_birlestir.py    # v2.0 verisine ekler
PYTHONPATH=src python training/v3e_hedefli.py      # v3.0'ın E kaynağı: data/v3/e-{train,validation}.jsonl
PYTHONPATH=src python training/v3e_birlestir.py    # E'yi v2.5 akışına ekler
PYTHONPATH=src python training/train.py --config configs/v3e-base.json --ad v3e-base
PYTHONPATH=src python evaluation/evaluate.py --checkpoint v3e-base-latest
PYTHONPATH=src python evaluation/gercek_olc.py --checkpoint v3e-base-latest --kume gercek3
PYTHONPATH=src python -m pytest -q                # 642 test
```

Doğal negatifler için Megazeka'nın Common Voice verisi `MEGAZEKA_CV` ortam değişkeni ya da `--cv` ile
verilir. Bu veri yoksa doğal negatif kotası deyim şablonlarına aktarılır. E kaynağındaki gerçek cümleleri
yeniden üretirken aynı Common Voice dosyasını `training/v3e_hedefli.py` komutuna `--cv` ile verebilirsiniz.
[Hugging Face veri kümesi](https://huggingface.co/datasets/pandakingpunc/megazeka-sayi-tr-itn-pairs).

## Bağlantılar

- [Hugging Face modeli](https://huggingface.co/pandakingpunc/megazeka-sayi-byt5-tr-itn)
- [Hugging Face veri kümesi](https://huggingface.co/datasets/pandakingpunc/megazeka-sayi-tr-itn-pairs)
- [Kardeş proje Megazeka](https://github.com/pandakingpunc/megazeka)
- [v3.0 sürüm notu](https://github.com/pandakingpunc/megazeka-sayi/releases/tag/v3.0)

## English summary

Megazeka-Sayı v3.0 is a Turkish inverse text normalization (ITN) model for ASR. It converts spelled-out
numbers to TDK-style written forms, such as `yüzde on iki buçuk` → `%12,5`. It uses ByT5-base with
LoRA (r=32), trained on 142,439 pairs. With the protection filter, v3.0 gets 602 of 627 hand-labelled
Common Voice sentences right, up from 590 for v2.5 with the same filter. On the new checkpoint-selection
set, it gets 189 of 198 right (95.5%) and false conversions fall from 9.2% to 5.0%. The other two real-text
sets informed the training data. Exact match on the 83-sentence hand-written set is 97.6%.

## Lisans

Kod ve LoRA ağırlıkları [MIT](LICENSE). Temel model `google/byt5-base` Apache-2.0 lisanslıdır. Doğal
negatif cümleler Mozilla Common Voice Türkçe metinlerinden gelir (CC0-1.0).

Yazar: Mustafa Karatüm ([ORCID 0009-0006-7053-2872](https://orcid.org/0009-0006-7053-2872)).
