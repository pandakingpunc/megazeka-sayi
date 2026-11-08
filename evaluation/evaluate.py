"""Değerlendirme: kopya / kural tabanı / model (korumasız ve korumalı) — test ve zorluk kümelerinde.

    python evaluation/evaluate.py [--checkpoint best] [--ad ADI] [--limit N] [--data-dir DIR]

Çıktı: reports/degerlendirme-<ad>.json ve .md (Türkçe tablolar + 25 hata örneği).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import argparse
import json
import os
import time

from megazeka_sayi import depolama
from megazeka_sayi.depolama import ROOT

depolama.yapilandir()
from megazeka_sayi.cikarim import SayiDonusturucu, koru
from megazeka_sayi.kural_tabani import donustur as kural
from megazeka_sayi.olcum import kategori_kirilimi, olc

CHALLENGE = ROOT / 'evaluation' / 'challenge.jsonl'
SISTEMLER = [('kopya', 'Girdiyi kopyala'), ('kural', 'Kural tabanlı (saf)'),
             ('model_korumasiz', 'Model (korumasız)'), ('model_korumali', 'Model + koruma')]
HATA_SAYISI = 25


def oku(yol, limit):
    satirlar = [json.loads(s) for s in Path(yol).read_text(encoding='utf-8').splitlines() if s.strip()]
    return satirlar[:limit] if limit else satirlar


def tahminler(satirlar, motor):
    """{sistem: [çıktı]}; motor yoksa yalnız kopya ve kural."""
    girdiler = [r['girdi'] for r in satirlar]
    sonuc = {'kopya': list(girdiler), 'kural': [kural(g) for g in girdiler]}
    uyarilar = [[] for _ in girdiler]
    if motor is not None:
        ham = motor.ham(girdiler)
        sonuc['model_korumasiz'] = ham
        korumali = [koru(g, h) for g, h in zip(girdiler, ham)]
        sonuc['model_korumali'] = [k[0] for k in korumali]
        uyarilar = [k[1] for k in korumali]
    return sonuc, uyarilar


def degerlendir(ad, satirlar, motor):
    sonuc, uyarilar = tahminler(satirlar, motor)
    olcumler, kirilim = {}, {}
    for sistem, cikti in sonuc.items():
        birlesik = [{**r, 'cikti': c} for r, c in zip(satirlar, cikti)]
        olcumler[sistem] = olc(birlesik)
        kirilim[sistem] = kategori_kirilimi(birlesik)
    hata_kaynagi = 'model_korumali' if motor is not None else 'kural'
    hatalar = [{'girdi': r['girdi'], 'hedef': r['hedef'], 'cikti': c, 'ham': (sonuc.get('model_korumasiz') or [None] * len(satirlar))[i],
                'kategori': r.get('kategori'), 'sablon': r.get('sablon'), 'uyari': uyarilar[i]}
               for i, (r, c) in enumerate(zip(satirlar, sonuc[hata_kaynagi])) if c != r['hedef']]
    return {'ad': ad, 'ornek': len(satirlar), 'hata_kaynagi': hata_kaynagi, 'olcumler': olcumler, 'kirilim': kirilim,
            'hata_sayisi': len(hatalar), 'hatalar': hatalar[:200],
            'koruma_geri_alma': sum(1 for u in uyarilar if u)}


def yuzde(x):
    return '—' if x is None else f'{100 * x:.1f}'


def tablo_olcum(rapor):
    s = ['| Sistem | Örnek | Tam eşleşme % | CER % | WER % | Sayı belirteci % | Yanlış dönüşüm % (negatif n) |',
         '|---|---:|---:|---:|---:|---:|---:|']
    for sistem, etiket in SISTEMLER:
        m = rapor['olcumler'].get(sistem)
        if m:
            s.append(f"| {etiket} | {m['ornek']} | {yuzde(m['tam_eslesme'])} | {yuzde(m['cer'])} | {yuzde(m['wer'])} | "
                     f"{yuzde(m['sayi_belirteci_dogrulugu'])} | {yuzde(m['yanlis_donusum_orani'])} ({m['negatif_ornek']}) |")
    return s


def tablo_kategori(rapor):
    sistemler = [(k, e) for k, e in SISTEMLER if k in rapor['kirilim']]
    kategoriler = sorted({k for s in rapor['kirilim'].values() for k in s})
    s = ['| Kategori | n | ' + ' | '.join(e + ' (tam %)' for _, e in sistemler) + ' |',
         '|---|---:|' + '---:|' * len(sistemler)]
    for k in kategoriler:
        n = next(v[k]['ornek'] for v in rapor['kirilim'].values() if k in v)
        s.append(f'| {k} | {n} | ' + ' | '.join(yuzde(rapor['kirilim'][sk][k]['tam_eslesme']) for sk, _ in sistemler) + ' |')
    return s


def markdown(raporlar, bilgi):
    s = [f"# Megazeka-Sayı değerlendirmesi — {bilgi['ad']}", '',
         f"Kontrol noktası: `{bilgi['kontrol_noktasi']}` · süre: {bilgi['saniye']:.0f} sn · "
         '“Yanlış dönüşüm” = girdi = hedef olan satırlarda çıktının değişmesi. '
         '“Sayı belirteci” = hedefteki rakamlı her belirtecin çıktıda birebir bulunması.', '']
    for r in raporlar:
        s += [f"## Küme: {r['ad']} ({r['ornek']} örnek)", ''] + tablo_olcum(r) + ['']
        if r.get('koruma_geri_alma') is not None and 'model_korumali' in r['olcumler']:
            s += [f"Koruma {r['koruma_geri_alma']} örnekte en az bir bölgeyi geri aldı.", '']
        s += ['### Kategori kırılımı', ''] + tablo_kategori(r) + ['']
        s += [f"### Hata örnekleri ({r['hata_kaynagi']}; toplam {r['hata_sayisi']} hata, ilk {min(HATA_SAYISI, r['hata_sayisi'])} gösterilir)", '']
        for h in r['hatalar'][:HATA_SAYISI]:
            s += ['```text', f"[{h['kategori']}/{h['sablon']}]", 'GİRDİ: ' + h['girdi'], 'ÇIKTI: ' + h['cikti']]
            if h['ham'] is not None and h['ham'] != h['cikti']:
                s.append('HAM  : ' + h['ham'])
            s += ['HEDEF: ' + h['hedef'], '```', '']
        if not r['hatalar']:
            s += ['Hata yok.', '']
    return '\n'.join(s)


def ana():
    ap = argparse.ArgumentParser(description='Megazeka-Sayı değerlendirmesi')
    ap.add_argument('--checkpoint', default='best', choices=['best', 'latest', 'base'])
    ap.add_argument('--ad', help='rapor adı (varsayılan: kontrol noktası)')
    ap.add_argument('--limit', type=int, help='yalnız hızlı denemeler için; varsayılan tam küme')
    ap.add_argument('--data-dir')
    ap.add_argument('--yalniz-taban', action='store_true', help='modeli yükleme; yalnız kopya ve kural')
    args = ap.parse_args()
    if args.data_dir:
        os.environ[depolama.VERI_ORTAM] = str(Path(args.data_dir).resolve())
    ad = args.ad or args.checkpoint
    baslangic = time.perf_counter()
    motor = None if args.yalniz_taban else SayiDonusturucu(args.checkpoint)
    kumeler = [('test', depolama.veri_dizini() / 'test.jsonl')]
    if CHALLENGE.exists():
        kumeler.append(('zorluk', CHALLENGE))
    raporlar = []
    for ku, yol in kumeler:
        satirlar = oku(yol, args.limit)
        print(f'{ku}: {len(satirlar)} örnek değerlendiriliyor...', flush=True)
        raporlar.append(degerlendir(ku, satirlar, motor))
    bilgi = {'ad': ad, 'kontrol_noktasi': 'yok (yalnız taban çizgileri)' if motor is None else args.checkpoint,
             'saniye': time.perf_counter() - baslangic, 'limit': args.limit}
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / f'reports/degerlendirme-{ad}.json').write_text(
        json.dumps({'bilgi': bilgi, 'kumeler': raporlar}, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / f'reports/degerlendirme-{ad}.md').write_text(markdown(raporlar, bilgi), encoding='utf-8')
    for r in raporlar:
        print(f"== {r['ad']} ==")
        print('\n'.join(tablo_olcum(r)))
    print(f"Rapor: reports/degerlendirme-{ad}.json / .md", flush=True)


if __name__ == '__main__':
    ana()
