"""Gerçek metin kümesinde ölçüm: evaluation/gercek.jsonl (Common Voice cümleleri, elle etiketli).

    python evaluation/gercek_olc.py [--checkpoint best] [--ad v2]

Her satırda `hedef` şartnameye göre birincil cevaptır; `kabul` varsa şartnamenin açık bırakmadığı
durumlarda eşit derecede savunulabilir öteki yazımlardır. İki sonuç verilir: katı (yalnız hedef) ve
esnek (hedef ya da kabul). Çıktı: reports/gercek-<ad>.json ve .md.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import argparse
import json
from collections import Counter, defaultdict

from megazeka_sayi import depolama
from megazeka_sayi.depolama import ROOT

depolama.yapilandir()
from megazeka_sayi.cikarim import SayiDonusturucu, koru
from megazeka_sayi.kural_tabani import donustur as kural

KUME = ROOT / 'evaluation' / 'gercek.jsonl'
SISTEMLER = [('kopya', 'Girdiyi kopyala'), ('kural', 'Kural tabanlı (saf)'),
             ('ham', 'Model (korumasız)'), ('korumali', 'Model + koruma')]


def ozet(satirlar, ciktilar):
    n = len(satirlar)
    kati = sum(c == r['hedef'] for r, c in zip(satirlar, ciktilar))
    esnek = sum(c == r['hedef'] or c in r.get('kabul', ()) for r, c in zip(satirlar, ciktilar))
    neg = [(r, c) for r, c in zip(satirlar, ciktilar) if r['girdi'] == r['hedef']]
    poz = [(r, c) for r, c in zip(satirlar, ciktilar) if r['girdi'] != r['hedef']]
    return {'ornek': n, 'kati': kati, 'esnek': esnek,
            'negatif': len(neg), 'yanlis_donusum': sum(c != r['girdi'] and c not in r.get('kabul', ()) for r, c in neg),
            'pozitif': len(poz), 'pozitif_dogru': sum(c == r['hedef'] or c in r.get('kabul', ()) for r, c in poz),
            'pozitif_dokunulmadi': sum(c == r['girdi'] and c not in r.get('kabul', ()) for r, c in poz)}


def ana():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', default='best')
    ap.add_argument('--ad', default='v2')
    a = ap.parse_args()
    satirlar = [json.loads(s) for s in KUME.read_text(encoding='utf-8').splitlines() if s.strip()]
    girdiler = [r['girdi'] for r in satirlar]
    motor = SayiDonusturucu(a.checkpoint)
    ham = motor.ham(girdiler)
    korunan = [koru(g, h) for g, h in zip(girdiler, ham)]
    cikti = {'kopya': girdiler, 'kural': [kural(g) for g in girdiler], 'ham': ham, 'korumali': [k[0] for k in korunan]}
    genel = {s: ozet(satirlar, c) for s, c in cikti.items()}
    kategori = defaultdict(dict)
    for kat in sorted({r['kategori'] for r in satirlar}):
        idx = [i for i, r in enumerate(satirlar) if r['kategori'] == kat]
        for s, c in cikti.items():
            kategori[kat][s] = ozet([satirlar[i] for i in idx], [c[i] for i in idx])
    hatalar = [{'no': i + 1, 'girdi': r['girdi'], 'hedef': r['hedef'], 'kabul': r.get('kabul', []), 'ham': ham[i],
                'korumali': cikti['korumali'][i], 'kural': cikti['kural'][i], 'kategori': r['kategori'], 'uyari': korunan[i][1]}
               for i, r in enumerate(satirlar)
               if any(c != r['hedef'] and c not in r.get('kabul', ()) for c in (ham[i], cikti['korumali'][i]))]
    rapor = {'ad': a.ad, 'kontrol_noktasi': a.checkpoint, 'genel': genel, 'kategori': kategori, 'hatalar': hatalar,
             'koruma_geri_alma': sum(1 for k in korunan if k[1])}
    (ROOT / f'reports/gercek-{a.ad}.json').write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding='utf-8')

    y = lambda a_, b: '—' if not b else f'{100 * a_ / b:.1f}'
    md = [f'# Gerçek metin ölçümü — {a.ad}', '',
          f'Küme: `evaluation/gercek.jsonl`, {len(satirlar)} Common Voice cümlesi (sayı kökü içerenler, köke göre katmanlı, '
          'elle etiketli). Katı = yalnız birincil hedef; esnek = hedef ya da kabul edilen öteki yazım.', '',
          '| Sistem | Katı % | Esnek % | Yanlış dönüşüm % (negatif n) | Pozitifte doğru % (n) | Pozitife hiç dokunmadı |',
          '|---|---:|---:|---:|---:|---:|']
    for s, e in SISTEMLER:
        g = genel[s]
        md.append(f"| {e} | {y(g['kati'], g['ornek'])} | {y(g['esnek'], g['ornek'])} | {y(g['yanlis_donusum'], g['negatif'])} ({g['negatif']}) | "
                  f"{y(g['pozitif_dogru'], g['pozitif'])} ({g['pozitif']}) | {g['pozitif_dokunulmadi']} |")
    md += ['', f"Koruma {rapor['koruma_geri_alma']} örnekte en az bir bölgeyi geri aldı.", '', '## Kategori kırılımı (esnek doğru / n)', '',
           '| Kategori | n | ' + ' | '.join(e for _, e in SISTEMLER) + ' |', '|---|---:|' + '---:|' * len(SISTEMLER)]
    for kat, v in kategori.items():
        md.append(f"| {kat} | {v['kopya']['ornek']} | " + ' | '.join(str(v[s]['esnek']) for s, _ in SISTEMLER) + ' |')
    md += ['', f'## Model hataları ({len(hatalar)}; ham ya da korumalı çıktı yanlış)', '']
    for h in hatalar:
        md += ['```text', f"[{h['no']} · {h['kategori']}]", 'GİRDİ: ' + h['girdi'], 'HAM  : ' + h['ham']]
        if h['korumali'] != h['ham']:
            md.append('KORU : ' + h['korumali'])
        md += ['HEDEF: ' + h['hedef'], '```', '']
    (ROOT / f'reports/gercek-{a.ad}.md').write_text('\n'.join(md), encoding='utf-8')
    print('\n'.join(md[4:4 + 2 + len(SISTEMLER)]))
    print(f'hata {len(hatalar)}; rapor reports/gercek-{a.ad}.md')


if __name__ == '__main__':
    ana()
