# Megazeka-Sayı · Türkçe sayı normalleştirici

Ses tanıma (ASR) sistemlerinin **yazıyla verdiği sayıları** TDK yazım kurallarına uygun **rakam biçimine**
çeviren küçük bir model. Sayı dışındaki her şeye dokunmaz. Yerelde eğitilmiş **ByT5-small + LoRA**
modelidir; çalışırken ağ bağlantısı ya da ücretli bir yapay zekâ API'si kullanmaz. Kardeş projesi
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
cümleleri bozar ("yemeğini 7"). Megazeka-Sayı'nın değeri tam olarak burada ölçülür.

## Sonuçlar (v1.0)

Dört kümede ölçüldü. "Girdiyi kopyala" hiçbir şeyi değiştirmeyen başlangıç değeridir. "Kural tabanlı"
ise bağlama bakmadan her sayı sözcüğü dizisini rakama çeviren saf bir taban çizgisidir
([`src/megazeka_sayi/kural_tabani.py`](src/megazeka_sayi/kural_tabani.py)). Yanlış dönüşüm, değişmemesi
gereken cümlelerden (girdi = hedef) kaçının bozulduğudur.

**Gizli elle yazılmış küme (50 cümle)** · en dürüst ölçüt. v1.0'ın verisi yazılırken üreteci yazan
taraf bu kümeyi görmedi; üreteçten bağımsız, elle yazıldı
([`evaluation/challenge2.jsonl`](evaluation/challenge2.jsonl)).

| Sistem | Tam eşleşme ↑ | CER ↓ | Yanlış dönüşüm ↓ (21 cümle) |
|---|---:|---:|---:|
| Girdiyi kopyala | %42,0 | 0,359 | %0 |
| Kural tabanlı | %56,0 | 0,058 | %52,4 |
| İç sürüm v1 (önceki deneme) | %84,0 | 0,024 | %28,6 |
| **Megazeka-Sayı v1.0** | **%94,0** | **0,012** | **%9,5** |

**Üreteç test kümesi (2.000 çift)** · eğitimde hiç kullanılmamış taşıyıcı şablonlarla üretildi.

| Sistem | Tam eşleşme ↑ | CER ↓ | Sayı belirteci doğruluğu ↑ | Yanlış dönüşüm ↓ (802) |
|---|---:|---:|---:|---:|
| Girdiyi kopyala | %40,1 | 0,299 | %9,6 | %0 |
| Kural tabanlı | %59,2 | 0,043 | %73,5 | %46,8 |
| Megazeka-Sayı v1.0 (korumasız) | %94,2 | 0,005 | %97,2 | %4,6 |
| **Megazeka-Sayı v1.0 (korumalı)** | **%93,8** | 0,014 | %94,1 | **%2,1** |

İlk iç sürümün dondurulmuş test kümesinde (2.000 çift) v1.0 %96,8 tam eşleşme yapar (v1 %94,5).

**İlk elle yazılmış küme (100 cümle):** %99 (kural tabanlı %53). Bu sayı **şişkindir**: v1.0, ilk sürümün
tam bu kümedeki hatalarına bakılarak geliştirildi. Bu yüzden asıl ölçüt yukarıdaki gizli kümedir.

Ham ölçümler ve hata örnekleri: [`reports/degerlendirme-v1.1.md`](reports/degerlendirme-v1.1.md)
(iç adı v1.1, yayın adı v1.0).

### Bilinen hatalar

- Kısa emir cümlelerinde "bin": `taksiye bin de gel` → `taksiye 1.000 de gel`.
- Cümle başında "ikinci el": `ikinci el telefonlar ucuzladı` → `2. el telefonlar ucuzladı`.
- Bileşik ölçüler: `üç kilo iki yüz gram` → `3,200 g` (doğrusu `3 kg 200 g`).
- Veri tamamen sentetiktir. Gerçek ASR çıktısındaki tanıma hatalarıyla (yanlış duyulmuş sözcükler)
  test edilmedi.

## Yazım kuralları

Ayrıntılı şartname: [`docs/SPEC.md`](docs/SPEC.md). Özetle:

- Binlik ayırıcı nokta, ondalık virgül: `1.250`, `3,14`. Yıl, telefon ve kodlar noktasız: `2026`, `0842`.
- Para: `lira` → `TL` (`1.250,50 TL`); dolar, avro gibi yabancı paralar sözcük kalır (`100 dolar`).
- Yüzde `%12,5`, saat `14.30`, tarih `8 Kasım 2026` (belirli tarihte ay adı büyük harfle).
- Birimler TDK kısaltmasıyla: `kg`, `g`, `km`, `m`, `cm`, `L`, `m²`, `GB`, `°C`.
- Sıra sayısı ardından ad gelirse: `3. kat`, `21. yüzyıl`. Yüklem olarak kalır: `birinci oldu`.
- Ekler kesmeyle ve rakamın okunuşuna göre: `4'e`, `2'ye`, `TL'ye`, `kg'dan`, `14.30'da`, `1990'larda`.
- **Küçük sayılar:** bağlamsız tek sözcüklük 0-9 sözcük kalır (`iki kişi geldi`). 10 ve üstü ile birim,
  para, saat, tarih vb. bağlamdaki her sayı rakama çevrilir (`on iki kişi` → `12 kişi`, `iki kilo` → `2 kg`).
  Tek başına `bir` (belirsiz tanımlık) her zaman sözcük kalır. Eğitim verisi `--politika rakamla` ile
  her sayıyı rakama çevirecek biçimde de üretilebilir.
- Kesirler ve deyimler sözcük kalır: `üçte bir`, `yarım kilo`, `dört gözle`, `kırk yılda bir`, `ikinci el`.

## Mimari

- **Model:** `google/byt5-small` + LoRA (r=16, 6,3 milyon eğitilebilir parametre). Bayt düzeyinde çalıştığı
  için rakam ve Türkçe ekler için uygundur.
- **Veri:** tamamen sentetik ve **ters yönde** üretilir. Önce doğru yazılı cümle kurulur, sonra
  deterministik bir sözlüleştirici onu konuşma biçimine çevirir. Böylece etiketler kusursuzdur.
  70.000 eğitim çifti, yaklaşık %40'ı değişmemesi gereken cümleler: eş yazımlı sözcükler, deyimler, zaten
  rakamlı metinler ve Common Voice'tan (CC0) sayı içermeyen gerçek cümleler. Her olgu yüzlerce farklı
  cümlede geçer. İlk denemede tek bir sabit cümle kullanılmıştı ve model onu ezberleyip genelleyemedi.
- **Koruma filtresi:** model çıktısı sözcük düzeyinde girdiyle hizalanır. Sayı olmayan bir sözcüğün
  değiştiği bölge geri alınır, yani model "sayı dışındaki her şeye dokunmama" sözünü bozamaz.
- **Eğitim:** RTX 4060 8 GB'ta 5.000 adım, yaklaşık 31 dakika, tepe VRAM 3,4 GB, bf16.

## Kurulum ve kullanım

Python 3.11-3.13. PyTorch'u kendi donanımınıza göre kurun (https://pytorch.org), sonra:

```bash
pip install -r requirements.txt
```

Yayınlanmış modelle (Hugging Face'ten iner, ilk çalıştırmada ByT5-small de iner):

```bash
PYTHONPATH=src python -m megazeka_sayi.cikarim --checkpoint pandakingpunc/megazeka-sayi-byt5-tr-itn "yüzde on iki buçuk indirim"
```

Yalnız `transformers` + `peft` ile (koruma filtresi olmadan):

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

tok = AutoTokenizer.from_pretrained("google/byt5-small")
base = AutoModelForSeq2SeqLM.from_pretrained("google/byt5-small")
model = PeftModel.from_pretrained(base, "pandakingpunc/megazeka-sayi-byt5-tr-itn").eval()

x = tok(["toplam bin iki yüz elli lira elli kuruş"], return_tensors="pt")
y = model.generate(**x, max_new_tokens=200, do_sample=False)
print(tok.batch_decode(y, skip_special_tokens=True))  # ['toplam 1.250,50 TL']
```

Model girdiyi tek parça olarak işler; 190 bayttan uzun metinleri cümle cümle verin
(`cikarim.py` bunu sözcük sınırından bölerek kendisi yapar).

### Veriyi üretmek ve yeniden eğitmek

```bash
PYTHONPATH=src python training/uret.py            # data/{train,validation,test}.jsonl
PYTHONPATH=src python training/train.py --config configs/medium.json
PYTHONPATH=src python evaluation/evaluate.py --checkpoint best
PYTHONPATH=src python -m pytest -q                # 70 test
```

Doğal negatifler için Megazeka'nın Common Voice verisi `MEGAZEKA_CV` ortam değişkeni ya da `--cv` ile
verilir. Dosya yoksa bu kota deyim şablonlarına aktarılır. Hazır üretilmiş veri:
[Hugging Face veri kümesi](https://huggingface.co/datasets/pandakingpunc/megazeka-sayi-tr-itn-pairs).

## Bağlantılar

- Model: https://huggingface.co/pandakingpunc/megazeka-sayi-byt5-tr-itn
- Veri: https://huggingface.co/datasets/pandakingpunc/megazeka-sayi-tr-itn-pairs
- Kardeş proje: https://github.com/pandakingpunc/megazeka

## English summary

Megazeka-Sayı is a small Turkish inverse text normalization (ITN) model: it turns spelled-out numbers in
ASR output into TDK-style written forms (`bin iki yüz elli lira elli kuruş` → `1.250,50 TL`, `saat on dört
otuzda` → `saat 14.30'da`) and leaves everything else untouched, including homographs such as *yedi*
("ate" / seven) or *ona* ("to him" / to ten). ByT5-small + LoRA, trained on fully synthetic, reverse-generated
data. On a held-out hand-written set it reaches 94% exact match vs. 56% for a context-free rule baseline.

## Lisans

Kod ve LoRA ağırlıkları [MIT](LICENSE). Temel model `google/byt5-small` Apache-2.0 lisanslıdır. Doğal
negatif cümleler Mozilla Common Voice Türkçe metinlerinden gelir (CC0-1.0).

Yazar: Mustafa Karatüm ([ORCID 0009-0006-7053-2872](https://orcid.org/0009-0006-7053-2872)).
