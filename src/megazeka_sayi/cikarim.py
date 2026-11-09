"""Çıkarım motoru: ByT5-small + LoRA ve "yalnız sayı sözcüklerini değiştir" korumasi.

Koruma (``koru``): model çıktısı ile girdi sözcük düzeyinde hizalanır (difflib, Türkçe katlanmış
sözcükler). Değişen/eklenen/silinen her bölge için
  * girdi tarafı yalnızca "sayı benzeri" sözcüklerden oluşmalı (sayılar, ekli biçimleri, sıra sayıları,
    virgül/buçuk/yüzde/eksi, lira/kuruş, birim sözcükleri, ay adları; ``saat`` değiştirilemez) ve
  * çıktı tarafı en az bir rakam, ``%`` ya da birim kısaltması içermeli;
aksi hâlde bölge girdideki özgün hâline döndürülür. Değişmeyen (eşit) bölgeler girdiden alınır, böylece
büyük/küçük harf ve noktalama bayt bayt korunur (tek istisna: tarihte ay adının büyük harfi).

CLI:  python -m megazeka_sayi.cikarim "yüzde on iki buçuk indirim"
"""
from difflib import SequenceMatcher
import re

# ---- Türkçe katlama -------------------------------------------------------------------------------
_KATLA = str.maketrans('çğıöşüâîû', 'cgiosuaiu')


def kucult(metin):
    return metin.translate(str.maketrans({'I': 'ı', 'İ': 'i'})).lower()


def fold(sozcuk):
    """Büyük/küçük harf, aksan ve noktalamadan bağımsız anahtar (rakam ve harf kalır)."""
    return ''.join(c for c in kucult(sozcuk).translate(_KATLA) if c.isalnum())


# ---- Sayı benzeri sözcük sözlüğü (katlanmış: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u) ------------------------
_KOKLER = ('sifir', 'bir', 'iki', 'uc', 'dort', 'dord', 'bes', 'alti', 'yedi', 'sekiz', 'dokuz', 'on', 'yirmi', 'otuz',
           'kirk', 'elli', 'altmis', 'yetmis', 'seksen', 'doksan', 'yuz', 'bin', 'milyon', 'milyar', 'trilyon',
           'yarim', 'ceyrek', 'virgul', 'bucuk', 'yuzde', 'eksi', 'lira', 'kurus', 'turk', 'lirasi',
           'kilogram', 'kilo', 'gram', 'kilometre', 'santimetre', 'santim', 'milimetre', 'metrekare', 'metre',
           'mililitre', 'litre', 'gigabayt', 'megabayt', 'terabayt', 'kilovat', 'vat', 'volt', 'derece', 'santigrat',
           'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim',
           'aralik')
# Kökten sonra gelebilecek ek dizileri (hâl, iyelik, çoğul, -lik, -ki, sıra sayısı eki).
_EK = re.compile(r'^(?:y?[ae]|y?[iu]|n?in|n?un|s[iu]|[dt][ae]n?|[dt][ae]ki|ki|y?l[ae]|l[ae]r|li[kg]|lu[kg]|'
                 r'inci|nci|uncu|ncu|d[ae]n)+$')
# Sayı gibi görünen ama eş yazımlı/kalıp sözcükler (EK ile eşleşse de sayı sayılmaz).
_SAYI_DEGIL = re.compile(r'^(?:on(?:a|u|un|da|dan|lar\w*|unla)|(?:on|yuz|bin|milyon|milyar)l[ae]r\w*|'
                         r'yuz(?:u|un|um|unu|une|unde|unden|le|me\w*|du\w*)|bin(?:e|di\w*|m\w*|ec\w*|en|ip|is\w*)|'
                         r'bir(?:i|in|ini|ine|inde|inden|isi|iyle)|kirk(?:in|ma\w*)?(?:ar|ti|mak)?)$')


# "on" sayısının zamir gibi okunabilen çekimleri; yalnız saat/yüzde/ay/sayı bağlamında sayı sayılır.
_ON_ZAMIR_BICIM = {'ona', 'onu', 'onun', 'onda', 'ondan'}
_SAYI_SOZ = {'sifir', 'bir', 'iki', 'uc', 'dort', 'bes', 'alti', 'yedi', 'sekiz', 'dokuz', 'on', 'yirmi', 'otuz', 'kirk',
             'elli', 'altmis', 'yetmis', 'seksen', 'doksan', 'yuz', 'bin', 'milyon', 'milyar', 'trilyon'}


def _on_baglami_mi(onceki):
    """``onceki`` (girdideki bir önceki sözcük) saat/yüzde/ay adı ya da sayı sözcüğü/rakamı mı?"""
    if onceki is None:
        return False
    f = fold(onceki)
    return f in ('saat', 'yuzde') or f in _AY_ADLARI or f in _SAYI_SOZ or (f.isdigit() and bool(f))


def sayi_benzeri_mi(sozcuk, onceki=None):
    """Sözcük (noktalama temizlenerek) bir sayı/para/birim/ay sözcüğü ya da eklenmiş biçimi mi?"""
    f = fold(sozcuk)
    if not f:
        return True  # yalnız noktalama (örn. "-") bölgeyi bozmasın
    if f == 'saat':
        return False
    if f.isdigit() or f in _KOKLER:
        return True
    if f in _ON_ZAMIR_BICIM and _on_baglami_mi(onceki):
        return True
    if _SAYI_DEGIL.match(f):
        return False
    return any(f.startswith(k) and _EK.match(f[len(k):]) for k in _KOKLER)


_BIRIMLER = {'kg', 'g', 'km', 'm', 'cm', 'mm', 'l', 'ml', 'm²', 'gb', 'mb', 'tb', 'kw', 'w', 'v', '°c', 'tl', 'kr'}
_AY_ADLARI = {'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik'}


def _cikti_sayi_iceriyor(sozcukler):
    for s in sozcukler:
        if any(c.isdigit() for c in s) or '%' in s:
            return True
        cekirdek = kucult(s.split("'")[0].strip('.,;:!?()"“”'))
        if cekirdek in _BIRIMLER:
            return True
    return False


def _ekli_ay_tarihi(a, b, i, j, x, y):
    """``kasımda`` → ``Kasım'da``: çıktı büyük harfli ay adı + kesme + ek olmalı ve hemen öncesinde,
    girdide sözcük olan sayı çıktıda rakama çevrilmiş olmalı (tarih bağlamı)."""
    if "'" not in y or y.count("'") != 1 or not y[:1].isupper():
        return False
    kok, ek = y.split("'")
    if not ek or fold(kok) not in _AY_ADLARI or kucult(kok + ek) != kucult(x):
        return False
    if i == 0 or j == 0:
        return False
    onceki_cikti, onceki_girdi = b[j - 1], a[i - 1]
    return any(c.isdigit() for c in onceki_cikti) and not any(c.isdigit() for c in onceki_girdi)


def koru(girdi, ham):
    """(metin, uyarılar). ``ham`` modelin ürettiği metin; yalnız sayı bölgelerindeki değişiklikler kabul edilir."""
    uyarilar = []
    a, b = girdi.split(), ham.split()
    if not b:
        return girdi, ['model boş çıktı üretti; girdi korundu']
    if not a:
        return girdi, []
    esleyici = SequenceMatcher(None, [fold(w) for w in a], [fold(w) for w in b], autojunk=False)
    sonuc = []
    for etiket, i1, i2, j1, j2 in esleyici.get_opcodes():
        if etiket == 'equal':
            for k, (x, y) in enumerate(zip(a[i1:i2], b[j1:j2])):
                # Özgün sözcük korunur; tek istisna: tarihte ay adının büyük harfi
                # (ekliyse "Kasım'da": gün sayısı bu çıktıda rakama çevrilmişse).
                ay = fold(x) in _AY_ADLARI and x != y and kucult(x) == kucult(y)
                if not ay and x != y and _ekli_ay_tarihi(a, b, i1 + k, j1 + k, x, y):
                    ay = True
                sonuc.append(y if ay else x)
            continue
        eski, yeni = a[i1:i2], b[j1:j2]
        if not eski:
            uyarilar.append(f'eklenen "{" ".join(yeni)}" reddedildi (girdide karşılığı yok)')
            continue
        if not yeni:
            uyarilar.append(f'silinen "{" ".join(eski)}" geri alındı')
            sonuc.extend(eski)
            continue
        girdi_ok = all(sayi_benzeri_mi(w, a[i1 + k - 1] if i1 + k > 0 else None) for k, w in enumerate(eski))
        cikti_ok = _cikti_sayi_iceriyor(yeni)
        if girdi_ok and cikti_ok:
            sonuc.extend(yeni)
        else:
            neden = 'sayı olmayan sözcük değişti' if not girdi_ok else 'çıktıda rakam/birim yok'
            uyarilar.append(f'"{" ".join(eski)}" → "{" ".join(yeni)}" geri alındı ({neden})')
            sonuc.extend(eski)
    if sonuc == a:
        return girdi, uyarilar
    return ' '.join(sonuc), uyarilar


def _parcala(metin, sinir):
    """Çok uzun girdiyi sözcük sınırlarında ``sinir`` bayttan kısa parçalara böler."""
    parcalar, mevcut = [], []
    for w in metin.split():
        if mevcut and len(' '.join(mevcut + [w]).encode()) > sinir:
            parcalar.append(' '.join(mevcut)); mevcut = []
        mevcut.append(w)
    if mevcut:
        parcalar.append(' '.join(mevcut))
    return parcalar


class SayiDonusturucu:
    """ByT5-small + LoRA (``models/checkpoints/<ad>``) ile ITN; çıktı korumadan geçirilir."""

    def __init__(self, kontrol_noktasi='best', isin=1, max_bayt=192, aygit=None):
        from . import depolama
        depolama.yapilandir()
        import torch
        from peft import PeftModel
        self.torch, self.isin, self.max_bayt = torch, isin, max_bayt
        self.aygit = aygit or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.bfloat16 if self.aygit == 'cuda' and torch.cuda.is_bf16_supported() else torch.float32
        self.tokenizer, taban, self.kaynak = depolama.temel_model_yukle(self.dtype)
        if kontrol_noktasi != 'base':
            yol = depolama.ROOT / 'models/checkpoints' / kontrol_noktasi
            if not (yol / 'adapter_config.json').exists():
                raise RuntimeError(f'Eğitilmiş model bulunamadı: {yol}. Önce training/train.py çalıştırın.')
            taban = PeftModel.from_pretrained(taban, yol, local_files_only=True)
        self.model = taban.to(self.aygit).eval()
        self.model.config.use_cache = True
        self.kontrol_noktasi = kontrol_noktasi

    def ham(self, metinler, grup=32):
        """Koruma olmadan model çıktıları (girdi sırasıyla). Uzun girdiler bölünüp birleştirilir."""
        parcalar, harita = [], []
        for n, m in enumerate(metinler):
            p = [m] if len(m.encode()) < self.max_bayt else _parcala(m, self.max_bayt - 8)
            harita.append((len(parcalar), len(p)))
            parcalar.extend(p)
        sira = sorted(range(len(parcalar)), key=lambda i: len(parcalar[i]))
        cikti = [''] * len(parcalar)
        for k in range(0, len(sira), grup):
            idx = sira[k:k + grup]
            x = self.tokenizer([parcalar[i] for i in idx], return_tensors='pt', padding=True).to(self.aygit)
            with self.torch.inference_mode():
                uretim = self.model.generate(**x, max_new_tokens=self.max_bayt + 8, do_sample=False, num_beams=self.isin)
            for i, t in zip(idx, self.tokenizer.batch_decode(uretim, skip_special_tokens=True)):
                cikti[i] = t
        return [' '.join(cikti[s:s + n]) if n > 1 else cikti[s] for s, n in harita]

    def donustur(self, metinler, koruma=True, grup=32):
        """[(metin, uyarılar)] döndürür."""
        tek = isinstance(metinler, str)
        liste = [metinler] if tek else list(metinler)
        hamlar = self.ham(liste, grup)
        sonuc = [koru(g, h) if koruma else (h, []) for g, h in zip(liste, hamlar)]
        return sonuc[0] if tek else sonuc

    __call__ = donustur


def ana():
    import argparse
    import sys
    ap = argparse.ArgumentParser(description='Türkçe ters metin normalleştirme (sözlü sayı → rakam)')
    ap.add_argument('metin', nargs='*', help='dönüştürülecek metin(ler)')
    ap.add_argument('--checkpoint', default='best', choices=['best', 'latest', 'base'])
    ap.add_argument('--isin', type=int, default=1, help='ışın sayısı (1 = açgözlü)')
    ap.add_argument('--korumasiz', action='store_true', help='koruma süzgecini kapat')
    ap.add_argument('--ham', action='store_true', help='ham model çıktısını da göster')
    args = ap.parse_args()
    metinler = args.metin or [s.rstrip('\n') for s in sys.stdin if s.strip()]
    motor = SayiDonusturucu(args.checkpoint, isin=args.isin)
    hamlar = motor.ham(metinler)
    for girdi, ham in zip(metinler, hamlar):
        metin, uyari = (ham, []) if args.korumasiz else koru(girdi, ham)
        print(metin)
        if args.ham:
            print('  ham:', ham)
        for u in uyari:
            print('  uyarı:', u)


if __name__ == '__main__':
    ana()
