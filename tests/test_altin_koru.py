"""Altın çiftlerde koruma ve bozma testi (model gerektirmez).

* Altın: ``data/{test,test-v1,test-v2,validation}.jsonl`` içindeki her satırda ``koru(girdi, hedef) == hedef`` olmalı.
  Değer denetimi tek bir altın satırı bile geri almamalı; denetimden önce de geri alınan 5 satır (hepsi ``on-`` zamiri
  eş yazımı, aşağıda) bilinen istisnadır.
* Bozma: girdi ≠ hedef satırlarda hedefin rakamları (değiştir/sil/ekle/takas, sabit tohum) bozulduğunda ``koru`` bozuk
  çıktıyı aynen geçirmemeli. Silinen/eklenen sıfırlar bazen başka bir meşru okumaya denk gelir; %100 şart değildir.
"""
import json
import random
from pathlib import Path

import pytest

from megazeka_sayi.cikarim import koru

VERI = Path(__file__).resolve().parent.parent / 'data'
DOSYALAR = ['test.jsonl', 'test-v1.jsonl', 'test-v2.jsonl', 'validation.jsonl']
RAKAMLAR = '0123456789'

# Değer denetiminden ÖNCE de geri alınan satırlar: ``onda/onu/ondan`` eş yazımı (bağlam yok) -- etiket tartışmalı
# (``xbox onu aldım`` → ``xbox 10'u aldım``, ``ondan önce`` → ``10'dan önce``); eş yazım korumasını gevşetmemek için bırakıldı.
BILINEN_GERI_ALINAN = {
    'Hesaplama onda tıkandı.',
    'şifreye onu ekle',
    'ben de xbox onu aldım',
    'Evden işe altı yüz seksen beş kilometre yol var, her gün ondan önce çıkıyorum.',
    'tablo ondan itibaren tekrar ediyor',
}


def _satirlar():
    sonuc = []
    for dosya in DOSYALAR:
        with open(VERI / dosya, encoding='utf-8') as f:
            sonuc += [(dosya, json.loads(l)) for l in f if l.strip()]
    return sonuc


@pytest.fixture(scope='module')
def altin():
    return _satirlar()


def test_dort_dosya_da_okundu(altin):
    assert {d for d, _ in altin} == set(DOSYALAR)
    assert len(altin) == 8492


def test_altin_satirlarda_yeni_geri_alma_yok(altin):
    gecen, basarisiz = 0, []
    for dosya, r in altin:
        metin, uyari = koru(r['girdi'], r['hedef'])
        if metin == r['hedef']:
            gecen += 1
        else:
            basarisiz.append((dosya, r['girdi'], r['hedef'], metin, uyari))
    deger_geri_alinan = [b for b in basarisiz if any('sayı değeri tutmuyor' in u for u in b[4])]
    assert not deger_geri_alinan, f'değer denetimi altın satırı geri aldı: {deger_geri_alinan[:5]}'
    yeni = [b for b in basarisiz if b[1] not in BILINEN_GERI_ALINAN]
    assert not yeni, f'yeni geri alınan altın satırlar: {yeni[:5]}'
    assert gecen >= 8487


def test_bozulan_rakamlar_yakalanir(altin):
    rng = random.Random(20260101)
    # her 3. satır (dört dosyadan da, yaklaşık 1800 satır × 4 bozma); koru'dan geçen altın satırlar
    secilen = [r for i, (_, r) in enumerate(altin)
               if i % 3 == 0 and r['girdi'] != r['hedef'] and any(c in RAKAMLAR for c in r['hedef'])
               and koru(r['girdi'], r['hedef'])[0] == r['hedef']]
    assert len(secilen) > 1000

    def boz(h, tur):
        yer = [i for i, c in enumerate(h) if c in RAKAMLAR]
        if tur == 'degistir':
            i = rng.choice(yer)
            return h[:i] + rng.choice([d for d in RAKAMLAR if d != h[i]]) + h[i + 1:]
        if tur == 'sil':
            i = rng.choice(yer)
            return h[:i] + h[i + 1:]
        if tur == 'ekle':
            j = rng.choice(yer) + rng.choice([0, 1])
            return h[:j] + rng.choice(RAKAMLAR) + h[j:]
        cift = [(i, j) for i in yer for j in yer if i < j and h[i] != h[j]]
        if not cift:
            return None
        i, j = rng.choice(cift)
        l = list(h)
        l[i], l[j] = l[j], l[i]
        return ''.join(l)

    sayac, yakalanan = {}, {}
    for r in secilen:
        for tur in ('degistir', 'sil', 'ekle', 'takas'):
            bozuk = boz(r['hedef'], tur)
            if bozuk is None or bozuk == r['hedef']:
                continue
            sayac[tur] = sayac.get(tur, 0) + 1
            if koru(r['girdi'], bozuk)[0] != bozuk:
                yakalanan[tur] = yakalanan.get(tur, 0) + 1
    for tur, esik in (('degistir', 0.995), ('takas', 0.995), ('sil', 0.98), ('ekle', 0.98)):
        oran = yakalanan.get(tur, 0) / sayac[tur]
        assert oran >= esik, f'{tur}: {oran:.4f} (< {esik})'
