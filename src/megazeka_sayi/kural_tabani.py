"""Saf kural tabanlı ITN taban çizgisi: bağlama BAKMADAN her sayı sözcüğü dizisini rakama çevirir.

Bilerek saftır: "yemeğini yedi" -> "yemeğini 7", "masanın altında" yerine "altı" geçen her yer, "onu" -> "10'u" gibi
hatalar BEKLENEN davranıştır (eş yazımlılar için model değerlidir). Kapsam: tam sayılar, ekli son sözcük
(kesme işaretiyle, basit ünlü uyumu), virgül/buçuk ondalıkları, yüzde -> %, eksi, lira/kuruş -> TL, temel birimler,
sıra sayıları (21.). Saat, tarih, telefon, skor, aralık gibi bağlamlı biçimler YOKTUR.

Kullanım: ``python -m megazeka_sayi.kural_tabani "yüzde on iki buçuk indirim"``
"""
import re
from .cikarim import fold, _EK

_SAYILAR = {'sifir': 0, 'bir': 1, 'iki': 2, 'uc': 3, 'dort': 4, 'dord': 4, 'bes': 5, 'alti': 6, 'yedi': 7, 'sekiz': 8,
            'dokuz': 9, 'on': 10, 'yirmi': 20, 'otuz': 30, 'kirk': 40, 'elli': 50, 'altmis': 60, 'yetmis': 70,
            'seksen': 80, 'doksan': 90, 'yuz': 100, 'bin': 1000, 'milyon': 10**6, 'milyar': 10**9, 'trilyon': 10**12}
# katlanmış kök -> (kısaltma, ince ünlülü okunuş mu?)  (ek uyumu kısaltmanın okunuşuna göre)
_BIRIMLER = {'kilogram': ('kg', 0), 'kilo': ('kg', 0), 'gram': ('g', 0), 'kilometre': ('km', 1), 'metre': ('m', 1),
             'santimetre': ('cm', 1), 'santim': ('cm', 1), 'milimetre': ('mm', 1), 'litre': ('L', 1),
             'mililitre': ('mL', 1), 'metrekare': ('m²', 1), 'gigabayt': ('GB', 0), 'megabayt': ('MB', 0),
             'terabayt': ('TB', 0), 'kilovat': ('kW', 0), 'vat': ('W', 0), 'volt': ('V', 0)}
_ORDINAL = ('inci', 'nci', 'uncu', 'ncu')
_NOKTA = re.compile(r'^(\W*)(.*?)(\W*)$', re.UNICODE)


def _kok_ek(f, kokler):
    """Katlanmış ``f`` = kök + ek ise (kök, ek_uzunluğu) döndürür (en uzun kök önce)."""
    for kok in sorted(kokler, key=len, reverse=True):
        if f == kok or (f.startswith(kok) and _EK.match(f[len(kok):])):
            return kok, len(f) - len(kok)
    return None


def _belirtec(sozcuk):
    on, cekirdek, son = _NOKTA.match(sozcuk).groups()
    f = fold(cekirdek)
    sayi = None
    if f != 'yuzde':  # "yüzde" yüz+de değil, yüzde işaretidir
        bulunan = _kok_ek(f, _SAYILAR)
        if bulunan:
            ek = cekirdek[len(cekirdek) - bulunan[1]:] if bulunan[1] else ''
            sayi = (_SAYILAR[bulunan[0]], ek, fold(ek) in _ORDINAL)
    return {'orj': sozcuk, 'on': on, 'son': son, 'cek': cekirdek, 'f': f, 'sayi': sayi}


def _ek_kismi(t, kokler):
    """Belirtecin kök sonrası (özgün yazımlı) ek kısmı."""
    n = _kok_ek(t['f'], kokler)[1]
    return t['cek'][len(t['cek']) - n:] if n else ''


def _tur(v):
    return 'sifir' if v == 0 else 'birim' if v < 10 else 'onluk' if v < 100 else 'yuz' if v == 100 else 'carpan'


def _devam(onceki, t, cur, v, son_carpan):
    if t == 'sifir':
        return False
    if onceki == 'birim':
        return t in ('yuz', 'carpan') and cur < 10
    return {'onluk': t in ('birim', 'carpan'), 'yuz': t in ('birim', 'onluk', 'carpan'),
            'carpan': t in ('birim', 'onluk', 'yuz') or (t == 'carpan' and v < son_carpan)}.get(onceki, False)


def _oku(tok, i):
    """tok[i:] başında en uzun tam sayı: (değer, bitiş, ek, sıra mı) ya da None."""
    toplam = cur = 0
    onceki, son_carpan, j, ek, sira = None, 0, i, '', False
    while j < len(tok) and tok[j]['sayi'] is not None:
        v, e, sr = tok[j]['sayi']
        t = _tur(v)
        if onceki is not None and not _devam(onceki, t, cur, v, son_carpan):
            break
        if t == 'yuz':
            cur = (cur or 1) * 100
        elif t == 'carpan':
            toplam, cur, son_carpan = toplam + (cur or 1) * v, 0, v
        else:
            cur += v
        onceki, j = t, j + 1
        if e:
            ek, sira = e, sr
            break
    return None if j == i else (toplam + cur, j, ek, sira)


def _sayi(tok, j):
    """Tam sayı + isteğe bağlı ondalık (virgül ... / buçuk). dict ya da None."""
    ilk = _oku(tok, j)
    if ilk is None:
        return None
    tam, bitis, ek, sira = ilk
    kesir = None
    if not ek and bitis < len(tok):
        f = tok[bitis]['f']
        if f == 'virgul':
            k, sifir = bitis + 1, 0
            while k < len(tok) and tok[k]['sayi'] and tok[k]['sayi'][0] == 0 and not tok[k]['sayi'][1]:
                k, sifir = k + 1, sifir + 1
            sag = _oku(tok, k)
            if sag:
                kesir, bitis, ek = '0' * sifir + str(sag[0]), sag[1], sag[2]
        elif re.match(r'^bucu[kg]', f) and _EK.match(f[5:] or 'a'):
            kesir, ek, bitis = '5', tok[bitis]['cek'][5:], bitis + 1
    return {'tam': tam, 'kesir': kesir, 'bitis': bitis, 'ek': ek, 'sira': sira and kesir is None}


def _bicim(tam, kesir):
    return f'{tam:,}'.replace(',', '.') + (',' + kesir if kesir else '')


def _ek_yaz(ek, ince=False):
    if not ek:
        return ''
    return "'" + (ek.translate(str.maketrans('aıuo', 'eiüö')) if ince else ek)


def _birim(tok, j):
    """(kısaltma, ince, ek, bitiş) ya da None. 'derece santigrat' -> °C; yalnız 'derece' sözcük kalır."""
    if j >= len(tok):
        return None
    if tok[j]['f'] == 'derece' and j + 1 < len(tok):
        b = _kok_ek(tok[j + 1]['f'], ['santigrat'])
        if b:
            return '°C', 0, tok[j + 1]['cek'][len(tok[j + 1]['cek']) - b[1]:] if b[1] else '', j + 2
    b = _kok_ek(tok[j]['f'], _BIRIMLER)
    if b:
        ek = tok[j]['cek'][len(tok[j]['cek']) - b[1]:] if b[1] else ''
        return _BIRIMLER[b[0]][0], _BIRIMLER[b[0]][1], ek, j + 1
    return None


def _para(tok, j):
    """'lira' / 'türk lirası' belirteci: (ek, bitiş) ya da None."""
    if j < len(tok) and tok[j]['f'] == 'turk':
        j += 1
    if j < len(tok):
        b = _kok_ek(tok[j]['f'], ['lira', 'lirasi'])
        if b:
            return (tok[j]['cek'][len(tok[j]['cek']) - b[1]:] if b[1] else ''), j + 1
    return None


def donustur(metin):
    """Girdi metindeki her sayı sözcüğü dizisini bağlama bakmadan rakama çevirir."""
    tok = [_belirtec(w) for w in metin.split()]
    cikti, i = [], 0
    while i < len(tok):
        yuzde, eksi = tok[i]['f'] == 'yuzde', tok[i]['f'] == 'eksi'
        r = _sayi(tok, i + 1 if (yuzde or eksi) else i)
        if r is None:
            cikti.append(tok[i]['orj']); i += 1
            continue
        yazi, ek, bitis, ince = _bicim(r['tam'], r['kesir']), r['ek'], r['bitis'], False
        if r['sira'] and not (yuzde or eksi):
            yazi, ek = yazi + '.', ''
        elif yuzde:
            yazi = '%' + yazi
        elif eksi:
            yazi = '-' + yazi
        if not ek and not yuzde and not r['sira']:
            para = _para(tok, bitis)
            birim = _birim(tok, bitis)
            if para:
                yazi, ek, bitis, ince = yazi + ' TL', para[0], para[1], True
                kurus = _sayi(tok, bitis)
                if not ek and kurus and kurus['bitis'] < len(tok) and not kurus['ek'] and r['kesir'] is None                         and 0 <= kurus['tam'] < 100 and _kok_ek(tok[kurus['bitis']]['f'], ['kurus']):
                    yazi = _bicim(r['tam'], '%02d' % kurus['tam']) + ' TL'
                    ek, bitis = _ek_kismi(tok[kurus['bitis']], ['kurus']), kurus['bitis'] + 1
            elif birim:
                yazi, ek, bitis, ince = f'{yazi} {birim[0]}', birim[2], birim[3], bool(birim[1])
            elif bitis < len(tok) and _kok_ek(tok[bitis]['f'], ['kurus']):
                yazi, ek, bitis = yazi + ' kuruş', _ek_kismi(tok[bitis], ['kurus']), bitis + 1
        cikti.append(tok[i]['on'] + yazi + _ek_yaz(ek, ince) + tok[bitis - 1]['son'])
        i = bitis
    return ' '.join(cikti)


if __name__ == '__main__':
    import sys
    for satir in (sys.argv[1:] or [s.rstrip('\n') for s in sys.stdin]):
        print(donustur(satir))
