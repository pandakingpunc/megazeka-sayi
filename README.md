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

## Sonuçlar (v2.0)

"Girdiyi kopyala" hiçbir şeyi değiştirmeyen başlangıç değeridir. "Kural tabanlı" ise bağlama bakmadan her
sayı sözcüğü dizisini rakama çeviren saf bir taban çizgisidir
([`src/megazeka_sayi/kural_tabani.py`](src/megazeka_sayi/kural_tabani.py)). Yanlış dönüşüm, değişmemesi
gereken cümlelerden (girdi = hedef) kaçının bozulduğudur. Model sayıları koruma filtresiyle birliktedir.

**Elle yazılmış gizli kümeler** · en dürüst ölçüt. Her küme, o sürümün verisini yazan taraf görmeden,
üreteçten bağımsız elle yazıldı. Gizli küme 3 ([`evaluation/challenge3.jsonl`](evaluation/challenge3.jsonl))
v2.0'ın yeni biçimlerini (rakamlı girdi, bitişik sayı, saat deyişleri, yeni birimler) ve v1.0'ın bilinen
hatalarını ölçer; gizli küme 2 ([`evaluation/challenge2.jsonl`](evaluation/challenge2.jsonl)) v1.0 içindi.
Koruma filtresi de gizli küme 3 görülmeden güncellendi.

| Sistem | Gizli küme 3 (83) | Yanlış dönüşüm (27) | Gizli küme 2 (50) | Yanlış dönüşüm (21) |
|---|---:|---:|---:|---:|
| Girdiyi kopyala | %32,5 | %0 | %42,0 | %0 |
| Kural tabanlı | %43,4 | %63,0 | %56,0 | %52,4 |
| Megazeka-Sayı v1.0 | %49,4 | %37,0 | %94,0 | %9,5 |
| **Megazeka-Sayı v2.0** | **%91,6** | **%18,5** | **%98,0** | **%0** |

**Üreteç test kümeleri** · eğitimde hiç kullanılmamış taşıyıcı şablonlarla üretildi.

| Küme | Kural tabanlı | v1.0 | **v2.0** | v2.0 yanlış dönüşüm |
|---|---:|---:|---:|---:|
| v1.0 test kümesi (2.000) | %59,2 | %93,8 | **%98,6** | %2,6 (802) |
| İlk iç sürümün dondurulmuş testi (2.000) | %53,2 | %96,8 | **%99,8** | %0 (776) |
| v2.0 yeni kaynaklar testi (1.400) | %42,3 | — | **%97,4** | %5,3 (379) |

**İlk elle yazılmış küme (100 cümle):** %98 (kural tabanlı %53). Bu sayı **şişkindir**: v1.0, ilk sürümün
tam bu kümedeki hatalarına bakılarak geliştirildi.

Ham ölçümler ve hata örnekleri: [`reports/degerlendirme-v2.md`](reports/degerlendirme-v2.md). v1.0'ın
raporu: [`reports/degerlendirme-v1.1.md`](reports/degerlendirme-v1.1.md) (iç adı v1.1).

### v2.0'da ne değişti

- **Yeni girdi biçimleri:** yarı rakamlı girdi (`5 bin lira` → `5.000 TL`, `saat 14:30'da` → `saat 14.30'da`),
  bitişik yazılmış sayılar (`yirmibeş` → `25`), saat deyişleri (`beşe on kala` → `5'e 10 kala`),
  ayın günü (`ayın on beşinde` → `ayın 15'inde`).
- **Sayısal doğruluk:** iç sıfırlı sayılar (`bin doksan` artık `1.090`), bileşik ölçü (`3 kg 200 g`),
  aralıklar, birim ekleri (`GB'tan`), yeni birimler (`mg`, `m³`, `km²`, `kWh`, `Hz`, `MHz`).
- **Tuzaklar:** kısa `bin` emirleri, `ikinci el`, `bu yüzden`, `onbaşı` gibi sözcükler için 10.000 yeni çift.
- **Veri temizliği:** v1.0 verisindeki telefon satırlarının %8,8'i iki farklı numaraya çözülebiliyordu
  (`beş yüz kırk yedi yüz altmış altı` = `540 766` ya da `547 166`); bu satırlar çıkarıldı.
- **Koruma filtresi** yeni biçimleri tanıyacak şekilde yeniden yazıldı; artık hiçbir kümede ham modelin
  altına düşmüyor.

### Bilinen hatalar

- Bazı kısa emirlerde "bin": `motora bin arkama` → `motora 1.000 arkama`.
- Fiil olan "yedi" nadiren sayıya döner: `elmayı yedi sonra uyudu` → `elmayı 7 sonra uyudu`.
- Bağlamsız küçük sayı bazen rakama döner: `toplantıya yedi kişi katıldı` → `7 kişi`.
- Sayı içeren özel adlar ve deyimler: `dokuz eylül üniversitesi` → `9 Eylül`, `dört dörtlük` → `4-4'lük`.
- Aynı cümlede art arda iki para tutarı birleşebilir (`otuz iki bin liradan otuz sekiz bin dört yüz liraya`).
- Veri tamamen sentetiktir. Gerçek ASR çıktısındaki tanıma hatalarıyla (yanlış duyulmuş sözcükler)
  test edilmedi.

## Yazım kuralları

Ayrıntılı şartname: [`docs/SPEC.md`](docs/SPEC.md), v2.0 ekleri [`docs/SPEC-v2.md`](docs/SPEC-v2.md). Özetle:

- Binlik ayırıcı nokta, ondalık virgül: `1.250`, `3,14`. Yıl, telefon ve kodlar noktasız: `2026`, `0842`.
- Para: `lira` → `TL` (`1.250,50 TL`); dolar, avro gibi yabancı paralar sözcük kalır (`100 dolar`).
- Yüzde `%12,5`, saat `14.30`, tarih `8 Kasım 2026` (belirli tarihte ay adı büyük harfle).
- Birimler TDK kısaltmasıyla: `kg`, `g`, `mg`, `km`, `m`, `cm`, `L`, `m²`, `m³`, `GB`, `kWh`, `°C`.
- Sıra sayısı ardından ad gelirse: `3. kat`, `21. yüzyıl`. Yüklem olarak kalır: `birinci oldu`.
- Ekler kesmeyle ve rakamın okunuşuna göre: `4'e`, `2'ye`, `TL'ye`, `kg'dan`, `14.30'da`, `1990'larda`.
- **Küçük sayılar:** bağlamsız tek sözcüklük 0-9 sözcük kalır (`iki kişi geldi`). 10 ve üstü ile birim,
  para, saat, tarih vb. bağlamdaki her sayı rakama çevrilir (`on iki kişi` → `12 kişi`, `iki kilo` → `2 kg`).
  Tek başına `bir` (belirsiz tanımlık) her zaman sözcük kalır. Eğitim verisi `--politika rakamla` ile
  her sayıyı rakama çevirecek biçimde de üretilebilir.
- Kesirler ve deyimler sözcük kalır: `üçte bir`, `yarım kilo`, `dört gözle`, `kırk yılda bir`, `ikinci el`.

## Mimari

- **Model:** `google/byt5-small` + LoRA (r=32). Bayt düzeyinde çalıştığı
  için rakam ve Türkçe ekler için uygundur.
- **Veri:** tamamen sentetik ve **ters yönde** üretilir. Önce doğru yazılı cümle kurulur, sonra
  deterministik bir sözlüleştirici onu konuşma biçimine çevirir. Böylece etiketler kusursuzdur.
  109.622 eğitim çifti, yaklaşık %34'ü değişmemesi gereken cümleler: eş yazımlı sözcükler, deyimler, zaten
  rakamlı metinler ve Common Voice'tan (CC0) sayı içermeyen gerçek cümleler. Her olgu yüzlerce farklı
  cümlede geçer. İlk denemede tek bir sabit cümle kullanılmıştı ve model onu ezberleyip genelleyemedi.
- **Koruma filtresi:** model çıktısı sözcük düzeyinde girdiyle hizalanır. Sayı olmayan bir sözcüğün
  değiştiği bölge geri alınır, yani model "sayı dışındaki her şeye dokunmama" sözünü bozamaz.
- **Eğitim:** RTX 4060 8 GB'ta 9.000 adım, yaklaşık 65 dakika, tepe VRAM 3,6 GB, bf16.

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
PYTHONPATH=src python training/uret.py            # v1.0 akışı: data/{train,validation,test}.jsonl
PYTHONPATH=src python training/v2_sayisal.py --out data/v2 --seed 2201 --train 16000 --validation 400 --test 500
PYTHONPATH=src python training/v2_tuzak.py --out data/v2 --seed 2202 --train 10000 --validation 300 --test 400
PYTHONPATH=src python training/v2_bicim.py --out data/v2 --seed 2203 --train 14000 --validation 400 --test 500
PYTHONPATH=src python training/v2_birlestir.py    # hepsini birleştirir, belirsiz telefon satırlarını eler
PYTHONPATH=src python training/train.py --config configs/v2.json
PYTHONPATH=src python evaluation/evaluate.py --checkpoint best
PYTHONPATH=src python -m pytest -q                # 370 test
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
data. v2.0 also handles half-normalized input (`5 bin lira`, `saat 14:30`), run-together numerals (`yirmibeş`)
and clock idioms. On the newest held-out hand-written set (83 sentences) it reaches 92% exact match vs. 49%
for v1.0 and 43% for a context-free rule baseline.

## Lisans

Kod ve LoRA ağırlıkları [MIT](LICENSE). Temel model `google/byt5-small` Apache-2.0 lisanslıdır. Doğal
negatif cümleler Mozilla Common Voice Türkçe metinlerinden gelir (CC0-1.0).

Yazar: Mustafa Karatüm ([ORCID 0009-0006-7053-2872](https://orcid.org/0009-0006-7053-2872)).
