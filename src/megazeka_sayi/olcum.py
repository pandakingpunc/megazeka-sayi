"""Ölçütler: tam eşleşme, CER, WER, sayı belirteci doğruluğu, yanlış dönüşüm oranı, kategori kırılımı.

Satır biçimi: ``{"girdi", "hedef", "cikti", "kategori"?}``.
"""
from collections import Counter, defaultdict
from rapidfuzz.distance import Levenshtein

_KENAR = ',;:!?"“”()'


def sayi_belirtecleri(metin):
    """Boşlukla ayrılmış belirteçlerden rakam içerenler (kenardaki , ; : ! ? " ( ) atılır; nokta ve % korunur)."""
    belirtecler = (t.strip(_KENAR) for t in metin.split())
    return [t for t in belirtecler if any(c.isdigit() for c in t)]


def sayi_belirteci_dogrulugu(satirlar):
    """Hedefteki rakam içeren her belirtecin çıktıda birebir bulunma oranı (çoklu küme, mikro ortalama).
    Hedefte sayısal belirteç yoksa None."""
    toplam = bulunan = 0
    for r in satirlar:
        hedef = Counter(sayi_belirtecleri(r['hedef']))
        if not hedef:
            continue
        cikti = Counter(sayi_belirtecleri(r['cikti']))
        toplam += sum(hedef.values())
        bulunan += sum((hedef & cikti).values())
    return bulunan / toplam if toplam else None


def olc(satirlar):
    """Tek bir satır kümesi için ölçütler."""
    n = len(satirlar)
    karakter = sozcuk = hata_k = hata_s = tam = negatif = yanlis = 0
    for r in satirlar:
        cikti, hedef = r['cikti'], r['hedef']
        karakter += len(hedef)
        sozcuk += len(hedef.split())
        hata_k += Levenshtein.distance(cikti, hedef)
        hata_s += Levenshtein.distance(cikti.split(), hedef.split())
        tam += cikti == hedef
        if r['girdi'] == hedef:
            negatif += 1
            yanlis += cikti != r['girdi']
    return {'ornek': n,
            'tam_eslesme': tam / n if n else None,
            'cer': hata_k / max(1, karakter),
            'wer': hata_s / max(1, sozcuk),
            'sayi_belirteci_dogrulugu': sayi_belirteci_dogrulugu(satirlar),
            'negatif_ornek': negatif,
            'yanlis_donusum_orani': yanlis / negatif if negatif else None}


def kategori_kirilimi(satirlar):
    """{kategori: olc(...)}; ``kategori`` alanı olmayan satırlar 'bilinmiyor' altında toplanır."""
    gruplar = defaultdict(list)
    for r in satirlar:
        gruplar[r.get('kategori') or 'bilinmiyor'].append(r)
    return {k: olc(v) for k, v in sorted(gruplar.items())}
