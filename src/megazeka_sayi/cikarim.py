"""Çıkarım motoru: ByT5-small + LoRA ve "yalnız sayı sözcüklerini değiştir" korumasi.

Koruma (``koru``): model çıktısı ile girdi sözcük düzeyinde hizalanır (difflib, Türkçe katlanmış
sözcükler). Değişen/eklenen/silinen her bölge için
  * girdi tarafı yalnızca "sayı benzeri" sözcüklerden oluşmalı: sayı kökleri ve ekli biçimleri, sıra sayıları,
    rakamlı sözcükler (``22500``, ``60'ı``), bitişik yazılmış sayılar (``onbeş``, ``ikiyüzelli``: yalnız sayı
    köklerinin art arda dizilimi + ek; ``onbaşı``, ``kırkayak``, ``üçgen``, ``birlik`` sayı değildir),
    virgül/buçuk/yüzde/eksi/artı, lira/kuruş, birim sözcükleri (``miligram``, ``metreküp``, ``kilometrekare``,
    ``kilovat saat``, ``hertz`` ... dahil), ay adları; ``saat`` değiştirilemez (``kilovat saat`` hariç);
  * eş yazımlı biçimler (``ona/onu/onda/ondan``, ``yüzü/yüzün``, ``biri/birinde``, ``bine``) ve iyelik + n'li ekler
    (``altısına``, ``yirmisinde``) yalnız sayı bağlamında sayı sayılır: önceki sözcük ``saat``/``yüzde``/``virgül``/
    ``ayın``/ay adı (ya da tamlayanlı hâli)/gün zamanı (``sabah``, ``akşam`` ...)/sayı sözcüğü/rakam ise ya da sözcüğü
    ``<sayı> geçe/kala/var`` izliyorsa (``biri on geçe``); ``yedi``, ``altında``, ``yüzünü``, ``bindi`` gibi
    sözcükler bağlamdan bağımsız sayı değildir;
  * çıktı tarafı en az bir rakam, ``%`` ya da birim kısaltması içermeli ve her çıktı sözcüğü rakam/``%``/birim
    kısaltması ya da girdi bölgesinden gelen sözcük olmalı (bölgeye başka sözcük sızdırılamaz);
aksi hâlde bölge girdideki özgün hâline döndürülür. Değişmeyen (eşit) bölgeler girdiden alınır, böylece
büyük/küçük harf ve noktalama bayt bayt korunur. İstisnalar: tarihte ay adının büyük harfi (``kasımda`` →
``Kasım'da``; girdide gün zaten rakamsa da) ve yarı normalleşmiş girdide rakamlı sözcüğün yalnız noktalama/işaret
farkı (``14:30'da`` → ``14.30'da``). Fold'u eşit ama biçimi farklı rakamlı sözcük (``12``/``-12``, ``60'ı``/
``%60'ı``) komşu değişiklikle (``eksi``, ``yüzde``, ``liraya``) tek bölge olarak değerlendirilir. Hizalamadan önce
ortak baş/son sözcükler ayrılır (``yedi yüz gram yedi`` → ``700 g yedi`` sondaki fiille eşlenmez).

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
# Sayı kökleri: bitişik yazılmış sayılar (``onbeş``, ``ikiyüzelli``) yalnız bunların art arda dizilimidir.
_SAYI_KOKLERI = ('sifir', 'bir', 'iki', 'uc', 'dort', 'dord', 'bes', 'alti', 'yedi', 'sekiz', 'dokuz', 'on', 'yirmi', 'otuz',
                 'kirk', 'elli', 'altmis', 'yetmis', 'seksen', 'doksan', 'yuz', 'bin', 'milyon', 'milyar', 'trilyon')
_KOKLER = _SAYI_KOKLERI + (
    'yarim', 'ceyrek', 'virgul', 'bucuk', 'bucug', 'yuzde', 'eksi', 'arti', 'lira', 'kurus', 'turk', 'lirasi',
    'kilogram', 'miligram', 'kilo', 'gram', 'kilometrekare', 'kilometre', 'santimetre', 'santim', 'milimetre',
    'metrekare', 'metrekup', 'metre', 'mililitre', 'litre', 'gigabayt', 'megabayt', 'terabayt', 'kilovatsaat', 'kilovat',
    'vat', 'volt', 'megahertz', 'kilohertz', 'hertz', 'derece', 'santigrat',
    'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim',
    'aralik')
# Kökten sonra gelebilecek ek dizileri (hâl, iyelik, çoğul, -lik, -ki, sıra sayısı eki).
_EK_GOVDE = (r'y?[ae]|y?[iu]|n?in|n?un|s[iu]|[dt][ae]n?|[dt][ae]ki|ki|y?l[ae]|l[ae]r|li[kg]|lu[kg]|'
             r'inci|nci|uncu|ncu|d[ae]n')
_EK_DESEN = r'(?:' + _EK_GOVDE + r')+'
# İyelik + zamir n'si (``altısına``, ``yirmisinde``): ``ikisini de`` gibi sözcük kalıplarıyla karışmasın diye
# yalnız sayı bağlamında (``ayın``, ay adı, ``saat``, önceki sayı sözcüğü ...) ek sayılır.
_EK_DESEN_N = r'(?:' + _EK_GOVDE + r'|s[iu]n(?:[ae]|d[ae]n?|i))+'
_EK = re.compile(r'^' + _EK_DESEN + r'$')
_EK_N = re.compile(r'^' + _EK_DESEN_N + r'$')
# Bitişik yazılmış sayı: yalnız sayı köklerinin art arda dizilimi (en az iki kök) + isteğe bağlı ek.
_KOK_DESEN = '(?:' + '|'.join(sorted(_SAYI_KOKLERI, key=len, reverse=True)) + r'){2,}'
_BITISIK = re.compile(r'^' + _KOK_DESEN + r'(?:' + _EK_DESEN + r')?$')
_BITISIK_N = re.compile(r'^' + _KOK_DESEN + r'(?:' + _EK_DESEN_N + r')?$')
# Sayı gibi görünen ama eş yazımlı/kalıp sözcükler (EK ile eşleşse de sayı sayılmaz), bağlama bakılmaksızın.
_SAYI_DEGIL = re.compile(r'^(?:(?:on|yuz|bin|milyon|milyar)l[ae]r\w*|on(?:unla|lar\w*)|yuz(?:me\w*|du\w*)|'
                         r'bin(?:di\w*|m\w*|ec\w*|en|ip|is\w*)|bir(?:lik|lig\w*|likte|ler\w*)|'
                         r'kirk(?:ma\w*|ar|ti\w*|mak\w*)|birbir\w*|binbir\w*|yuzuc\w*|ondal\w*)$')
# Yalnız sayı bağlamında (``saat``, ``yüzde``, ay adı, öncesinde sayı sözcüğü/rakamı ...) sayı sayılan zamir/ad çekimleri.
_BAGLAMLI = re.compile(r'^(?:on(?:a|u|un|da|dan)|yuz(?:u|un|um|unu|une|unde|unden|le)|bine|'
                       r'bir(?:i|in|ini|ine|inde|inden|isi|iyle))$')
_SAYI_SOZ = frozenset(_SAYI_KOKLERI)
# Saat deyişleri: "bire on kala", "biri on geçe", "ona çeyrek var".
_SAAT_YUKLEM = frozenset({'gece', 'geciyor', 'geciyordu', 'gececek', 'kala', 'kalmisti', 'kalir', 'var', 'vardi', 'varken'})
_AY_ADLARI = frozenset({'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim',
                        'aralik'})
# Ayın günü: "ayın birinde", "mayısın on beşinde" (``ayın`` ya da ay adı + tamlayan eki).
_AY_TAMLAYAN = frozenset({'ayin'} | {(m[:-1] + 'g' if m in ('ocak', 'aralik') else m) + e
                                      for m in _AY_ADLARI for e in ('in', 'un')})
_GUN_ZAMANI = frozenset({'sabah', 'aksam', 'gece', 'ogle', 'ogleden', 'oglen', 'ikindi', 'sabahin', 'aksamin', 'gecenin'})
_BAGLAM_SOZ = frozenset({'saat', 'yuzde', 'virgul', 'eksi', 'arti'})


def _on_baglami_mi(onceki):
    """``onceki`` (girdideki bir önceki sözcük) saat/yüzde/ay/gün zamanı ya da sayı sözcüğü/rakamı mı?"""
    if onceki is None:
        return False
    f = fold(onceki)
    return bool(f) and (f in _BAGLAM_SOZ or f in _AY_ADLARI or f in _AY_TAMLAYAN or f in _GUN_ZAMANI or f in _SAYI_SOZ
                        or f[0].isdigit())


def _saat_deyisi_mi(sonraki):
    """``sonraki`` (girdide sözcüğü izleyen sözcükler): bir ya da birkaç sayı/``çeyrek`` + geçe/kala/var mı?"""
    n = 0
    for w in sonraki:
        f = fold(w)
        if f == 'ceyrek' or f in _SAYI_SOZ or (f[:1].isdigit() and f.isdigit()):
            n += 1
        else:
            return n > 0 and f in _SAAT_YUKLEM
    return False


def _rakamli_ek_mi(f):
    """Rakamla başlayan sözcük (``60'ı``, ``22500``, ``900'ün``): rakamlardan sonra yalnız ek kalmalı."""
    k = 0
    while k < len(f) and f[k].isdigit():
        k += 1
    return k > 0 and (k == len(f) or bool(_EK.match(f[k:])))


def sayi_benzeri_mi(sozcuk, onceki=None, sonraki=()):
    """Sözcük (noktalama temizlenerek) bir sayı/para/birim/ay sözcüğü ya da eklenmiş biçimi mi?

    ``onceki``/``sonraki``: girdide sözcükten önceki sözcük / sonraki sözcükler. ``ona``, ``yüzü``, ``biri`` gibi eş yazımlı biçimler yalnız
    sayı bağlamında (saat, yüzde, ay adı/ayın, sayı sözcüğü ya da rakamı, virgül, ``biri on geçe`` gibi saat deyişi ...) sayı sayılır;
    ``kilovat`` + ``saat`` birimin parçasıdır."""
    f = fold(sozcuk)
    if not f:
        return True  # yalnız noktalama (örn. "-") bölgeyi bozmasın
    if f.startswith('saat'):  # yalnız "kilovat saat(lik)" birimin parçasıdır
        return fold(onceki or '') in ('kilovat', 'megavat') and (f == 'saat' or bool(_EK.match(f[4:])))
    if f.isdigit() or f in _KOKLER:
        return True
    if f[0].isdigit():
        return _rakamli_ek_mi(f)
    if _BAGLAMLI.match(f):
        return _on_baglami_mi(onceki) or _saat_deyisi_mi(sonraki)
    if _SAYI_DEGIL.match(f):
        return False
    if any(f.startswith(k) and _EK.match(f[len(k):]) for k in _KOKLER) or _BITISIK.match(f):
        return True
    if _on_baglami_mi(onceki):
        return any(f.startswith(k) and _EK_N.match(f[len(k):]) for k in _KOKLER) or bool(_BITISIK_N.match(f))
    return False


_BIRIMLER = {'kg', 'g', 'km', 'm', 'cm', 'mm', 'l', 'ml', 'm²', 'gb', 'mb', 'tb', 'kw', 'w', 'v', '°c', 'tl', 'kr',
             'mg', 'm³', 'km²', 'kwh', 'hz', 'mhz', 'khz'}


def _sayisal_sozcuk_mu(s):
    cekirdek = kucult(s.split("'")[0].strip('.,;:!?()"“”'))
    return any(c.isdigit() for c in s) or '%' in s or cekirdek in _BIRIMLER


def _cikti_sayi_iceriyor(sozcukler):
    return any(_sayisal_sozcuk_mu(s) for s in sozcukler)


def _cikti_temiz_mi(eski, yeni):
    """Bölge çıktısındaki her sözcük rakam/%/birim kısaltması ya da girdi bölgesinden gelen sözcük olmalı
    (``30 kuruş``, ``5 euro``, ``Kasım'da``); aksi hâlde sayı bölgesine sızdırılmış başka sözcük vardır."""
    kalan = {fold(w) for w in eski}
    return all(_sayisal_sozcuk_mu(w) or fold(w) in kalan for w in yeni)


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
    return any(c.isdigit() for c in onceki_cikti)


_NOKTALAMA = set(".,:;'’%-+")


def _yalniz_noktalama_farki(x, y):
    """Rakam içeren iki sözcük yalnız noktalama/işaretle ayrışıyor mu? (``14:30'da`` → ``14.30'da``)"""
    sade = lambda w: ''.join(c for c in w if c not in _NOKTALAMA)
    return any(c.isdigit() for c in x) and any(c.isdigit() for c in y) and sade(x) == sade(y)


def _parcalar(a, b):
    """Hizalamayı ('esit'|'degis', i1, i2, eski, yeni) parçalarına çevirir. Fold'u eşit ama biçimi farklı olan
    rakamlı sözcük çiftleri (``14:30'da``/``14.30'da``, ``12``/``-12``, ``60'ı``/``%60'ı``) tek başına 'rakam'
    parçası olur; komşusu bir değişiklikse onunla tek bölgede birleştirilir."""
    fa, fb = [fold(w) for w in a], [fold(w) for w in b]
    bas = 0  # ortak baş/son sözcükler önce ayrılır: "yedi yüz gram yedi" → "700 g yedi" sondaki fiille eşlenmesin
    while bas < min(len(a), len(b)) and fa[bas] == fb[bas]:
        bas += 1
    son = 0
    while son < min(len(a), len(b)) - bas and fa[len(a) - 1 - son] == fb[len(b) - 1 - son]:
        son += 1
    ops = [('equal', 0, bas, 0, bas)] if bas else []
    ops += [(e, i1 + bas, i2 + bas, j1 + bas, j2 + bas) for e, i1, i2, j1, j2 in SequenceMatcher(
        None, fa[bas:len(a) - son], fb[bas:len(b) - son], autojunk=False).get_opcodes()]
    if son:
        ops.append(('equal', len(a) - son, len(a), len(b) - son, len(b)))
    parca = []
    for etiket, i1, i2, j1, j2 in ops:
        if etiket == 'equal':
            for k in range(i2 - i1):
                x, y = a[i1 + k], b[j1 + k]
                tur = 'rakam' if x != y and any(c.isdigit() for c in x) and any(c.isdigit() for c in y) else 'esit'
                parca.append([tur, i1 + k, i1 + k + 1, [x], [y], j1 + k])
        else:
            parca.append(['degis', i1, i2, a[i1:i2], b[j1:j2], j1])
    etkin = [p[0] == 'degis' for p in parca]
    for sira in (range(len(parca)), range(len(parca) - 1, -1, -1)):
        yon = 1 if sira[0] == 0 else -1
        for k in sira:
            if parca[k][0] == 'rakam' and 0 <= k - yon < len(parca) and etkin[k - yon]:
                etkin[k] = True
    sonuc = []
    for k, p in enumerate(parca):
        if etkin[k]:
            if sonuc and sonuc[-1][0] == 'degis':
                son = sonuc[-1]
                son[2] = p[2]; son[3] = son[3] + p[3]; son[4] = son[4] + p[4]
            else:
                sonuc.append(['degis', p[1], p[2], list(p[3]), list(p[4]), p[5]])
        else:
            sonuc.append(p)
    return sonuc


def koru(girdi, ham):
    """(metin, uyarılar). ``ham`` modelin ürettiği metin; yalnız sayı bölgelerindeki değişiklikler kabul edilir."""
    uyarilar = []
    a, b = girdi.split(), ham.split()
    if not b:
        return girdi, ['model boş çıktı üretti; girdi korundu']
    if not a:
        return girdi, []
    sonuc = []
    for tur, i1, i2, eski, yeni, j1 in _parcalar(a, b):
        if tur != 'degis':
            x, y = eski[0], yeni[0]
            if tur == 'rakam':
                sonuc.append(y if _yalniz_noktalama_farki(x, y) else x)
                continue
            # Özgün sözcük korunur; tek istisna: tarihte ay adının büyük harfi
            # (ekliyse "Kasım'da": gün sayısı bu çıktıda rakama çevrilmişse).
            ay = fold(x) in _AY_ADLARI and x != y and kucult(x) == kucult(y)
            if not ay and x != y and _ekli_ay_tarihi(a, b, i1, j1, x, y):
                ay = True
            sonuc.append(y if ay else x)
            continue
        if not eski:
            uyarilar.append(f'eklenen "{" ".join(yeni)}" reddedildi (girdide karşılığı yok)')
            continue
        if not yeni:
            uyarilar.append(f'silinen "{" ".join(eski)}" geri alındı')
            sonuc.extend(eski)
            continue
        girdi_ok = all(sayi_benzeri_mi(w, a[i1 + k - 1] if i1 + k > 0 else None, a[i1 + k + 1:i1 + k + 4])
                       for k, w in enumerate(eski))
        cikti_ok = _cikti_sayi_iceriyor(yeni) and _cikti_temiz_mi(eski, yeni)
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
            if (yol / 'adapter_config.json').exists():
                taban = PeftModel.from_pretrained(taban, yol, local_files_only=True)
            elif '/' in str(kontrol_noktasi):
                # Yerel klasör yolu ya da Hugging Face depo adı (ör. pandakingpunc/megazeka-sayi-byt5-tr-itn).
                taban = PeftModel.from_pretrained(taban, str(kontrol_noktasi))
            else:
                raise RuntimeError(f'Eğitilmiş model bulunamadı: {yol}. Önce training/train.py çalıştırın '
                                   'ya da --checkpoint pandakingpunc/megazeka-sayi-byt5-tr-itn verin.')
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
    ap.add_argument('--checkpoint', default='best',
                    help='models/checkpoints altındaki ad (best, latest, v1.1...), base ya da HF depo adı')
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
