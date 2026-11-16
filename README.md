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

## Sonuçlar (v2.5)

"Girdiyi kopyala" hiçbir şeyi değiştirmeyen başlangıç değeridir. "Kural tabanlı" ise bağlama bakmadan her
sayı sözcüğü dizisini rakama çeviren saf bir taban çizgisidir
([`src/megazeka_sayi/kural_tabani.py`](src/megazeka_sayi/kural_tabani.py)). Yanlış dönüşüm, değişmemesi
gereken cümlelerden (girdi = hedef) kaçının bozulduğudur. Model sayıları koruma filtresiyle birliktedir.

**Gerçek metin** · v2.5'in asıl hedefi. Common Voice Türkçe'den (CC0) sayı sözcüğü içeren gerçek cümleler
örneklendi ve şartnameye göre elle etiketlendi; hiçbiri üreteç şablonundan gelmez. Şartnamenin açık
bırakmadığı yerlerde eşit derecede savunulabilir ikinci yazım da doğru sayılır. v2.0 sütunu, v2.0
ağırlıklarının v2.5 koruma filtresiyle ölçümüdür.

| Küme | Girdiyi kopyala | Kural tabanlı | v2.0 | **v2.5** | Yanlış dönüşüm v2.0 → v2.5 |
|---|---:|---:|---:|---:|---:|
| Gerçek küme 2 (150), **görülmemiş** | %64,7 | %36,7 | %90,7 | **%93,3** | %9,4 → %5,2 (96) |
| Gerçek küme 1 (279), geliştirme | %59,9 | %40,9 | %89,2 | **%95,7** | %10,4 → %4,9 (163) |

Gerçek küme 1 **şişkindir**: v2.5'in yeni verisi, v2.0'ın tam bu kümedeki hata sınıflarına bakılarak
tasarlandı (cümlelerin kendisi eğitim verisinden çıkarıldı). Dürüst ölçüt gerçek küme 2'dir: veri ve koruma
filtresi yazılırken hataları incelenmedi, cümleleri eğitim verisinden çıkarıldı. İki kümenin etiketleri
depoda: [`evaluation/gercek.jsonl`](evaluation/gercek.jsonl), [`evaluation/gercek2.jsonl`](evaluation/gercek2.jsonl).

**Elle yazılmış gizli kümeler** · her küme, o sürümün verisini yazan taraf görmeden, üreteçten bağımsız
elle yazıldı. Gizli küme 3 ([`evaluation/challenge3.jsonl`](evaluation/challenge3.jsonl)) v2.0'ın yeni
biçimlerini ölçer; gizli küme 2 ([`evaluation/challenge2.jsonl`](evaluation/challenge2.jsonl)) v1.0 içindi.

| Sistem | Gizli küme 3 (83) | Yanlış dönüşüm (27) | Gizli küme 2 (50) | Yanlış dönüşüm (21) |
|---|---:|---:|---:|---:|
| Girdiyi kopyala | %32,5 | %0 | %42,0 | %0 |
| Kural tabanlı | %43,4 | %63,0 | %56,0 | %52,4 |
| Megazeka-Sayı v1.0 | %49,4 | %37,0 | %94,0 | %9,5 |
| Megazeka-Sayı v2.0 | %91,6 | %18,5 | %98,0 | %0 |
| **Megazeka-Sayı v2.5** | **%92,8** | **%7,4** | **%98,0** | **%0** |

**Üreteç test kümeleri** · eğitimde hiç kullanılmamış taşıyıcı şablonlarla üretildi.

| Küme | Kural tabanlı | v1.0 | v2.0 | **v2.5** | v2.5 yanlış dönüşüm |
|---|---:|---:|---:|---:|---:|
| v1.0 test kümesi (2.000) | %59,2 | %93,8 | %98,6 | **%99,1** | %0,6 (802) |
| İlk iç sürümün dondurulmuş testi (2.000) | %53,2 | %96,8 | %99,8 | **%99,7** | %0 (776) |
| v2.0 yeni kaynaklar testi (1.400) | %42,3 | — | %97,4 | **%97,7** | %2,9 (379) |
| v2.5 testi, yeni kaynak dahil (5.494) | — | — | %78,1 | **%97,6** | %2,5 (2.842) |

Son satırda v2.0 ile karşılaştırma adil değildir: bu küme v2.5'in yeni şartname kararlarını ve yeni
kalıplarını içerir, v2.0 bunları hiç görmedi.

**İlk elle yazılmış küme (100 cümle):** %98 (kural tabanlı %53). Bu sayı **şişkindir**: v1.0, ilk sürümün
tam bu kümedeki hatalarına bakılarak geliştirildi.

Ham ölçümler ve hata örnekleri: [`reports/degerlendirme-v2.5.md`](reports/degerlendirme-v2.5.md),
[`reports/gercek-v2.5.md`](reports/gercek-v2.5.md), [`reports/gercek2-v2.5.md`](reports/gercek2-v2.5.md)
(raporların içinde modelin iç adı `v3-small` geçer). Gerçek metin çalışmasının ayrıntısı:
[`reports/gercek-v2-analiz.md`](reports/gercek-v2-analiz.md). Önceki sürümler:
[`reports/degerlendirme-v2.md`](reports/degerlendirme-v2.md), [`reports/degerlendirme-v1.1.md`](reports/degerlendirme-v1.1.md).

### v2.5'te ne değişti

- **Gerçek metinde ölçüm:** ilk kez üreteç dışı, gerçek cümlelerde ölçüldü. v2.0 üreteç testlerinde %98
  alırken gerçek cümlelerde %89-91'de kalıyordu; hataların çoğu atasözleri, `bir` ile başlayan sayılar,
  küçük sayılar ve zamir olan `ona`, `onun`, `onlar` idi.
- **Gerçek cümlelerden veri:** 26.747 yeni eğitim çifti. Common Voice'tan sayı sözcüğü içeren ama
  değişmemesi gereken gerçek cümleler (zamirler, eş yazımlılar, deyimler), atasözleri ve deyimler,
  `bir buçuk iki saat` → `1,5-2 saat`, `bir elli boyunda` → `1,50 boyunda`, cümle başında ve tırnak içinde
  sayılar, ek almış para tutarları (`liraymış`, `liram`), eski birimler (`okka`, `kuruş`).
- **Yeni şartname kararları** ([`docs/SPEC-v3-kararlar.md`](docs/SPEC-v3-kararlar.md)): küçük sayı + yaş
  ya da süre sözcük kalır (`sekiz yaşında`), anlatımdaki sıra sayıları ve unvanlar sözcük kalır
  (`ikinci kaptan`), `altmışlık adam` sözcük kalır. Soru eki girdideki gibi kalır (`493 TL mı`).
- **Koruma filtresi sayı değerini de denetliyor:** çıktıdaki rakamların girdideki sayı sözcüklerinden
  türeyip türemediği eğitimsiz bir gidiş-dönüş denetimiyle ölçülür; tutmuyorsa o bölge geri alınır.
  Düşen cümle sonu noktalaması geri konur.
- **Yanlış dönüşüm yarıya indi:** gerçek küme 2'de %9,4 → %5,2, gizli küme 3'te %18,5 → %7,4.

v2.0'da ne değiştiği: [v2.0 sürüm notu](https://github.com/pandakingpunc/megazeka-sayi/releases/tag/v2.0).

### Bilinen hatalar

- **Görmediği atasözleri ve deyimler:** `inek gözünde kırk sinek saydım` → `40 sinek`,
  `Adı çıktı dokuza, inmez sekize` → `9'a, 8'e`. Gerçek küme 2'deki 10 hatanın 5'i böyle.
- Bazı kısa emirlerde "bin": `motora bin arkama` → `motora 1.000 arkama`.
- Ek almış aralıklar: `on yedi on sekizden yukarı` → `17.18'den` (doğrusu `17-18'den`).
- Resmî metinde art arda sıra sayıları: `on ikinci maddenin birinci fıkrası` → `12. maddenin birinci fıkrası`.
- Virgülle ayrılmış kaba tutarlar: `seksen, yüz bin lirası` → `80,100.000 TL`.
- Veri sentetik ve gerçek cümle karışımıdır, ama gerçek ASR çıktısındaki tanıma hatalarıyla (yanlış
  duyulmuş sözcükler) test edilmedi. Gerçek kümeler edebî ağırlıklı Common Voice cümleleridir; haber,
  finans ya da konuşma dili için ayrı ölçüm yok.

## Yazım kuralları

Ayrıntılı şartname: [`docs/SPEC.md`](docs/SPEC.md), v2.0 ekleri [`docs/SPEC-v2.md`](docs/SPEC-v2.md), v2.5 kararları
[`docs/SPEC-v3-kararlar.md`](docs/SPEC-v3-kararlar.md). Özetle:

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
- **Veri:** büyük bölümü sentetik ve **ters yönde** üretilir. Önce doğru yazılı cümle kurulur, sonra
  deterministik bir sözlüleştirici onu konuşma biçimine çevirir. Böylece etiketler kusursuzdur.
  136.029 eğitim çifti, yaklaşık %39'u değişmemesi gereken cümleler: eş yazımlı sözcükler, deyimler, zaten
  rakamlı metinler ve Common Voice'tan (CC0) gerçek cümleler (sayı içermeyenler ve sayı sözcüğü zamir, eş
  yazımlı ya da deyim olanlar). Her olgu yüzlerce farklı
  cümlede geçer. İlk denemede tek bir sabit cümle kullanılmıştı ve model onu ezberleyip genelleyemedi.
- **Koruma filtresi:** model çıktısı sözcük düzeyinde girdiyle hizalanır. Sayı olmayan bir sözcüğün
  değiştiği ya da rakamın değeri girdideki sayı sözcükleriyle tutmadığı bölge geri alınır, yani model
  "sayı dışındaki her şeye dokunmama" sözünü bozamaz.
- **Eğitim:** RTX 4060 8 GB'ta 9.000 adım, yaklaşık 77 dakika, tepe VRAM 3,5 GB, bf16.

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
PYTHONPATH=src python training/v3_gercek.py --cv <common-voice-cümleleri> --out data/v3   # v2.5 kaynağı
PYTHONPATH=src python training/v3_birlestir.py    # v2.0 verisine ekler
PYTHONPATH=src python training/train.py --config configs/v3-small.json --ad v3-small
PYTHONPATH=src python evaluation/evaluate.py --checkpoint v3-small-best
PYTHONPATH=src python evaluation/gercek_olc.py --checkpoint v3-small-best --kume gercek2
PYTHONPATH=src python -m pytest -q                # 636 test
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
data plus real Common Voice sentences. It also handles half-normalized input (`5 bin lira`, `saat 14:30`),
run-together numerals (`yirmibeş`) and clock idioms. v2.5 is the first version measured on real text: on 150
held-out, hand-labelled Common Voice sentences it reaches 93.3% (v2.0: 90.7%, context-free rule baseline:
36.7%) and halves false conversions (9.4% → 5.2%). On the held-out hand-written set (83 sentences) it
reaches 93% vs. 49% for v1.0.

## Lisans

Kod ve LoRA ağırlıkları [MIT](LICENSE). Temel model `google/byt5-small` Apache-2.0 lisanslıdır. Doğal
negatif cümleler Mozilla Common Voice Türkçe metinlerinden gelir (CC0-1.0).

Yazar: Mustafa Karatüm ([ORCID 0009-0006-7053-2872](https://orcid.org/0009-0006-7053-2872)).
