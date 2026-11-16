"""Gidiş-dönüş (değer) denetimi: model çıktısındaki rakamlar girdideki sayı sözcüklerinden türetilebilir mi?

``koru`` bir değiştirme bölgesini (eski = girdi sözcükleri, yeni = çıktı sözcükleri) kabul etmeden önce
``deger_tutuyor_mu(eski, yeni)`` sorar. Yöntem:

  * Girdi bölgesindeki sayı sözcükleri "atom" dizisine çevrilir: sayı kökleri (eklenmiş ve bitişik yazılmış
    biçimleriyle: ``onbeşinci`` → on, beş), ``buçuk`` ve rakamlı sözcükler (rakam dizisi olduğu gibi atomdur).
    Sayı olmayan sözcükler (lira, kuruş, birim, yüzde, virgül, ay adı ...) atom üretmez; yalnız grup sınırı olmaz,
    ``kuruş`` gibi bağlam ipuçları atoma işlenir.
  * Çıktı bölgesindeki bütün rakamlar (``[0-9]``; ``m²``'deki üs sayılmaz) uç uca eklenip tek bir rakam dizisi olur.
  * Atom dizisi her yolla ardışık gruplara bölünür; her grup kardinal sayı olarak okunur (``yetmiş sekiz milyon on bin``
    → 78010000) ve ondalık yazımı üretilir. Rakam dizisi bu gruplar uç uca eklenerek elde edilebiliyorsa değer tutar.
    Bu bir kümeyi üretmek yerine (DP) "p. rakama kadar eşleşti mi" tablosuyla yapılır; uzun telefon dizileri patlamaz.
  * Atomun hiçbiri düşürülemez (``iki buçuk üç`` → ``2,5`` tutmaz: ``3`` kayıp). Tek istisna, çıktıda sözcük olarak
    kalan çarpan (``iki buçuk milyon`` → ``2,5 milyon``) ve ``buçuk``: rakam üretmeyebilir.
  * Meşru biçimler: kuruş iki haneye tamamlanır (``beş lira beş kuruş`` → ``5,05``); çıktıda saat deseni
    (``14.05``) varsa tek haneli dakika ``0`` ile tamamlanabilir; ``buçuk`` saatte ``30``, başka yerde ``5``;
    ``sıfır virgül sıfır beş`` rakam rakam okunur (``005``); telefon/kod gruplu ve rakam rakam karışık olabilir.

Bilinçli boşluk: zeminde yalnız rakam dizisi karşılaştırılır (ondalık ayracı/binlik noktası/``TL`` yeri bakılmaz);
tek haneli dakikada ``0`` tamamlaması saat deseni varsa isteğe bağlıdır (``14.5`` ile ``14.05`` ayrılamaz).
"""
from __future__ import annotations

import itertools
import re
from typing import NamedTuple

_KATLA = str.maketrans('çğıöşüâîû', 'cgiosuaiu')
_BUYUK_I = str.maketrans({'I': 'ı', 'İ': 'i'})


def _katla(sozcuk):
    """Büyük/küçük harf, aksan ve noktalamadan bağımsız anahtar (``cikarim.fold`` ile aynı)."""
    return ''.join(c for c in sozcuk.translate(_BUYUK_I).lower().translate(_KATLA) if c.isalnum())


# Katlanmış sayı kökleri: tür b=birler, o=onlar, y=yüz, m=çarpan (bin, milyon ...).
_KOKLER = {
    'sifir': ('b', 0), 'bir': ('b', 1), 'iki': ('b', 2), 'uc': ('b', 3), 'dort': ('b', 4), 'dord': ('b', 4),
    'bes': ('b', 5), 'alti': ('b', 6), 'yedi': ('b', 7), 'sekiz': ('b', 8), 'dokuz': ('b', 9),
    'on': ('o', 10), 'yirmi': ('o', 20), 'otuz': ('o', 30), 'kirk': ('o', 40), 'elli': ('o', 50),
    'altmis': ('o', 60), 'yetmis': ('o', 70), 'seksen': ('o', 80), 'doksan': ('o', 90),
    'yuz': ('y', 100), 'bin': ('m', 10 ** 3), 'milyon': ('m', 10 ** 6), 'milyar': ('m', 10 ** 9),
    'trilyon': ('m', 10 ** 12),
}
_KOK_SIRALI = sorted(_KOKLER, key=len, reverse=True)
# Çıktıda sözcük olarak kalabilen çarpanlar (``2,5 milyon``): bu atomlar rakam üretmeyebilir.
_KALAN_CARPAN = ('milyon', 'milyar', 'trilyon')
_ENFAZLA_YUZDE = 4  # bir bölgede yorumu denenen en çok ``yüzde`` sözcüğü
_ENFAZLA_GRUP = 16  # tek grubun en çok atom sayısı (``yüz yirmi üç milyon ... dokuz yüz`` ≈ 13 atom)

_RAKAM = re.compile(r'[0-9]+')
_SAAT_DESENI = re.compile(r'[0-9]{1,2}[.:]0[0-9](?![0-9])')
_SAAT_OTUZ = re.compile(r'[0-9]{1,2}[.:]30(?![0-9])')
_TEK_HANELI_DAKIKA = re.compile(r'[0-9]{1,2}[.:][0-9](?![0-9])')


class _Atom(NamedTuple):
    tur: str           # b, o, y, m (sayı kökleri) | l (rakamlı sözcük) | k (buçuk)
    deger: int | None  # kökün değeri; rakamlı sözcükte yalnız-rakam ise sayı değeri, değilse None
    ad: str            # katlanmış kök (çarpan/buçuk için) ya da boş
    lit: str           # rakamlı sözcüğün rakamları (tür l)
    kurus: int         # 2: arkasından bölge içinde kuruş geliyor, 1: bölge dışında kuruş geliyor, 0: yok
    ayri: bool = False  # önündeki sayı atomuyla arasında sayı olmayan sözcük var (virgül, lira ...): aynı grupta olamazlar
    ekli: bool = False  # sözcük ek aldı (``dokuzdan``, ``yüzde`` = yüz + de): sayı burada biter
    onluk: bool = False  # ``doksanlarda``: onlar kökü + çoğul eki (çıktıda ``1990'larda``: yüzyıl öneki eklenebilir)


def _kok_ayir(f, _onbellek={}):
    """``f`` katlanmış sözcüğün başındaki art arda sayı köklerinin en uzun kapsayan dizilimi (kalan = ek)."""
    if f in _onbellek:
        return _onbellek[f]
    en_iyi = (0, ())
    for k in _KOK_SIRALI:
        if f.startswith(k):
            kalan = _kok_ayir(f[len(k):])
            aday = (len(k) + kalan[0], (k,) + kalan[1])
            if aday[0] > en_iyi[0]:
                en_iyi = aday
    _onbellek[f] = en_iyi
    return en_iyi


_SAAT_LIT = re.compile(r'^[^0-9]*0[0-9][:.][0-9]{2}(?![0-9])')


def _kelime_atomlari(w, yuz_ek=False):
    """``yuz_ek``: ``yüzde`` sözcüğü yüz + bulunma eki (``dört yüzde`` → ``400'de``); değilse yüzde (%) sözcüğü."""
    rak = _RAKAM.findall(w)
    if rak:
        cek = re.sub(r'^[^0-9]+|[^0-9]+$', '', re.split("['’]", w)[0])
        deger = int(cek) if re.fullmatch('[0-9]+', cek) else None
        lit = ''.join(rak)
        # saatte baştaki sıfır düşer: 02:15 → 2.15 (SPEC §1)
        return [_Atom('l', deger, 'saat0' if _SAAT_LIT.match(w) else '', lit, 0)]
    f = _katla(w)
    if f.startswith(('bucuk', 'bucug')):
        return [_Atom('k', None, 'bucuk', '', 0)]
    if f == 'yuzde' and not yuz_ek:  # yüzde (%); yüz + de ise ``yuz_ek``
        return []
    kapsanan, kokler = _kok_ayir(f)
    atomlar = [_Atom(_KOKLER[k][0], _KOKLER[k][1], k, '', 0) for k in kokler]
    if atomlar and atomlar[-1].tur == 'o' and f[kapsanan:].startswith(('lar', 'ler')):
        atomlar[-1] = atomlar[-1]._replace(onluk=True)
    if atomlar and kapsanan < len(f):  # ekli sözcük sayıyı bitirir: sonraki sayı onunla aynı grupta olamaz
        atomlar[-1] = atomlar[-1]._replace(ekli=True)
    return atomlar


def _atomlar(eski, sonraki, yuz_ek=()):
    """Girdi bölgesinin atomları. ``yuz_ek``: belirsiz ``yüzde`` sözcüklerinin (sırayla) yüz + ek sayılıp sayılmayacağı."""
    atomlar, belirsiz, ayri = [], 0, False
    for k, w in enumerate(eski):
        ek = False
        if _katla(w) == 'yuzde':
            ek = belirsiz < len(yuz_ek) and yuz_ek[belirsiz]
            belirsiz += 1
        yeni = _kelime_atomlari(w, ek)
        if not yeni:
            ayri = True
            continue
        yeni[0] = yeni[0]._replace(ayri=(ayri or (bool(atomlar) and atomlar[-1].ekli)) and bool(atomlar))
        ayri = False
        if k + 1 < len(eski):
            sira, nxt = 2, eski[k + 1]
        else:
            sira, nxt = 1, sonraki
        if nxt is not None and _katla(nxt).startswith('kurus'):
            yeni[-1] = yeni[-1]._replace(kurus=sira)
        atomlar.extend(yeni)
    return atomlar


def _parca(atomlar):
    """1000'den küçük kısım: [birler yüz] [onlar] [birler] ya da tek rakamlı sözcük (< 1000)."""
    n = len(atomlar)
    if n == 0:
        return None
    if n == 1 and atomlar[0].tur == 'l':
        d = atomlar[0].deger
        return d if d is not None and d < 1000 else None
    i, v = 0, 0
    if n >= 2 and atomlar[0].tur == 'b' and atomlar[0].deger >= 1 and atomlar[1].tur == 'y':
        v, i = atomlar[0].deger * 100, 2
    elif atomlar[0].tur == 'y':
        v, i = 100, 1
    if i < n and atomlar[i].tur == 'o':
        v += atomlar[i].deger
        i += 1
    if i < n and atomlar[i].tur == 'b' and atomlar[i].deger >= 1:
        v += atomlar[i].deger
        i += 1
    return v if i == n else None


def _kardinal(atomlar):
    """Atom dizisinin kardinal değeri (``yetmiş sekiz milyon on bin`` → 78010000); geçersizse None."""
    toplam, son, cur = 0, None, []
    for a in atomlar:
        if a.tur == 'm':
            c = _parca(cur) if cur else 1  # "bin", "milyon" yalın = 1 çarpan
            if c is None or c < 1 or (son is not None and a.deger >= son):
                return None
            toplam += c * a.deger
            son, cur = a.deger, []
        elif a.tur in 'byol':
            cur.append(a)
        else:
            return None
    if cur:
        c = _parca(cur)
        if c is None:
            return None
        toplam += c
    return toplam if atomlar else None


def deger_tutuyor_mu(eski, yeni, onceki=None, sonraki=None):
    """``yeni`` (çıktı sözcükleri) içindeki rakamların hepsi ``eski`` (girdi sözcükleri) sayı sözcüklerinden türetilebilir mi?

    ``onceki``/``sonraki``: girdide bölgenin hemen öncesindeki/sonrasındaki sözcük (``saat`` bağlamı, bölge dışı ``kuruş``).
    ``yüzde`` sözcüğü hem yüzde (%) hem yüz + ``-de`` eki olabilir: her yorum denenir, biri tutarsa yeter."""
    belirsiz = sum(1 for w in eski if _katla(w) == 'yuzde')
    for secim in itertools.product((False, True), repeat=min(belirsiz, _ENFAZLA_YUZDE)):
        if _deger_tutuyor_mu(eski, yeni, onceki, sonraki, secim):
            return True
    return False


def _deger_tutuyor_mu(eski, yeni, onceki, sonraki, yuz_ek):
    atomlar = _atomlar(eski, sonraki, yuz_ek)
    cikti = ' '.join(yeni)
    hedef = ''.join(_RAKAM.findall(cikti))
    m = len(atomlar)
    if m == 0:
        return hedef == ''
    cikti_f = [_katla(w) for w in yeni]
    saat_bagi = _katla(onceki or '') == 'saat' or bool(_SAAT_OTUZ.search(cikti))
    saat_dakika = bool(_SAAT_DESENI.search(cikti))
    if _katla(onceki or '') == 'saat' and _TEK_HANELI_DAKIKA.match(cikti):
        return False  # "saat 14.5" yazılmaz: dakika iki hane (SPEC §1)
    kurus_kalan = any(w.startswith('kurus') for w in cikti_f)

    def bos_olabilir(a):
        if a.tur == 'k':
            return any(w.startswith('bucu') for w in cikti_f)
        return a.tur == 'm' and a.ad in _KALAN_CARPAN and any(w.startswith(a.ad) for w in cikti_f)

    # Çıktı rakam dizisinde p. rakamın hemen önünde başka bir rakam varsa (ayraçsız bitişik) sınır "içeride"dir.
    # ``zayif``: önünde rakam, binlik noktası ya da ondalık virgülü var (``369.1004`` bir ayraç sayılmaz).
    bitisik, zayif, onceki_rakam, onceki_c = [], [], False, ''
    for c in cikti:
        if '0' <= c <= '9':
            bitisik.append(onceki_rakam)
            zayif.append(onceki_rakam or onceki_c in '.,')
        onceki_rakam, onceki_c = '0' <= c <= '9', c
    n = len(hedef)

    def tek_rakam(a):
        return (a.tur == 'b') or (a.tur == 'l' and len(a.lit) == 1)

    onbellek = {}

    def grup(i, j):
        """atomlar[i:j] grubunun üretebileceği rakam dizileri."""
        anahtar = (i, j)
        if anahtar in onbellek:
            return onbellek[anahtar]
        g = atomlar[i:j]
        sonuc = set()
        if any(a.ayri for a in g[1:]):
            pass  # sayı olmayan sözcük grubu böler
        elif len(g) == 1:
            a = g[0]
            if a.tur == 'l':
                sonuc.add(a.lit)
                if a.ad == 'saat0':
                    sonuc.add(a.lit[1:])
                tek = a.lit if len(a.lit) == 1 and a.lit != '0' else ''
            elif a.tur == 'k':
                sonuc.add('5')
                if saat_bagi:
                    sonuc.add('30')
                tek = ''
            else:
                sonuc.add(str(a.deger))
                if a.onluk:  # doksanlar → 1990'lar
                    sonuc.update(onek + str(a.deger) for onek in ('18', '19', '20'))
                tek = str(a.deger) if a.tur == 'b' and a.deger >= 1 else ''
            if tek:
                if a.kurus == 2 and not kurus_kalan:
                    sonuc = {'0' + tek}  # 5,05 TL: bölgede tüketilen kuruş iki hane
                elif i > 0 and saat_dakika:
                    sonuc.add('0' + tek)  # 14.05: tek haneli dakika
        else:
            if g[-2].tur == 'k' and g[-1].tur == 'm' and len(g) > 2:  # iki buçuk milyon = 2.500.000
                kat = _kardinal(g[:-2])
                if kat is not None:
                    sonuc.add(str(kat * g[-1].deger + g[-1].deger // 2))
            elif all(a.tur != 'k' for a in g):
                d = _kardinal(g)
                if d is not None:
                    sonuc.add(str(d))
        onbellek[anahtar] = sonuc
        return sonuc

    def katsayi_ayrildi(i):
        """atomlar[i] bir grubu başlatırsa, hemen öncesindeki atomun katsayısını (beş | yüz, yirmi beş | bin) ondan ayırır mı?"""
        if i == 0 or atomlar[i].ayri:
            return False
        onceki, a = atomlar[i - 1], atomlar[i]
        return (a.tur == 'y' and onceki.tur == 'b') or (a.tur == 'm' and onceki.tur in 'byol')

    # durum: (p, son grup tek rakam mı); None = henüz grup yok
    ulasilan = [set() for _ in range(m + 1)]
    ulasilan[0].add((0, None))
    for i in range(m):
        for p, tek in ulasilan[i]:
            if bos_olabilir(atomlar[i]):
                ulasilan[i + 1].add((p, tek))
            if tek is not None and 0 < p < n and ((bitisik[p] and not tek) or (zayif[p] and katsayi_ayrildi(i))):
                # Çıktıda ayraçsız bitişik rakamlar arasında grup sınırı yalnız solu tek rakam olan gruplarda geçerli
                # (0532, kod); katsayıyı çarpanından ayıran sınır ayraç yoksa (ya da yalnız binlik noktası/ondalık
                # virgülü varsa) geçersiz: "beş yüz on" → 5110, "üç bin yedi" → 3.1007 olmaz.
                continue
            for j in range(i + 1, min(m, i + _ENFAZLA_GRUP) + 1):
                for s in grup(i, j):
                    if hedef.startswith(s, p):
                        ulasilan[j].add((p + len(s), j - i == 1 and tek_rakam(atomlar[i])))
    return any(p == n for p, _ in ulasilan[m])
