"""Gerçek metin kümesi için aday cümleleri seçer (etiketsiz).

    python evaluation/gercek_ornekle.py --cv <common_voice_tr.txt> [--cikti evaluation/gercek-aday.jsonl]

Kaynak: Common Voice Türkçe cümle derlemi (CC0). Eğitimdeki doğal negatifler aynı derlemden gelir ama
yalnız sayı kökü İÇERMEYEN cümlelerden (training/uret.py: cv_yukle); burada tam tersine yalnız sayı kökü
içerenler alınır, yani eğitimle çakışma yoktur.

Katmanlama: `bir` ve `on` derlemde çok baskın olduğu için ayrı ve küçük kotayla alınır; öteki her kök
için en çok KOK_KOTASI cümle seçilir, böylece seyrek kökler (milyon, buçuk, sıfır) de temsil edilir.
Seçim sabit tohumludur. Etiketler elle yazılır: evaluation/gercek.jsonl.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
from megazeka_sayi.turkce import lower_tr  # noqa: E402

KOKLER = ("sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz",
          "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan", "yüz", "bin", "milyon", "milyar", "trilyon",
          "yarım", "buçuk", "çeyrek", "eksi")
BAYT_SINIRI = 178
KOK_KOTASI = 10
BIR_KOTASI = 30
ON_KOTASI = 30
TOHUM = 20261116


def kokler(cumle):
    jetonlar = re.findall(r"[^\W\d_]+", lower_tr(cumle))
    return {k for j in jetonlar for k in KOKLER if j.startswith(k)}


def sec(cumleler, tohum=TOHUM, haric=(), kok_kotasi=KOK_KOTASI, on_kotasi=ON_KOTASI, bir_kotasi=BIR_KOTASI):
    rng = random.Random(tohum)
    haric = set(haric)
    havuz = []
    for t in sorted(set(c.strip() for c in cumleler)):
        if t in haric or len(t.encode("utf-8")) > BAYT_SINIRI or len(t.split()) < 3 or re.search(r"\d", t):
            continue
        ks = kokler(t)
        if ks:
            havuz.append((t, ks))
    rng.shuffle(havuz)
    secilen, gorulen = [], set()

    def al(kosul, kota, katman):
        n = 0
        for t, ks in havuz:
            if n >= kota:
                break
            if t not in gorulen and kosul(ks):
                gorulen.add(t)
                secilen.append({"girdi": t, "katman": katman})
                n += 1

    sayim = {k: sum(1 for _, ks in havuz if k in ks) for k in KOKLER}
    # seyrek kökten sık köke: seyrek olanlar başka katmana kapılmasın
    for k in sorted((k for k in KOKLER if k not in ("bir", "on") and sayim[k]), key=lambda k: (sayim[k], k)):
        al(lambda ks, k=k: k in ks, kok_kotasi, k)
    al(lambda ks: ks == {"on"} or ks == {"on", "bir"}, on_kotasi, "on")
    al(lambda ks: ks == {"bir"}, bir_kotasi, "bir")
    return secilen, len(havuz)


def ana():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", required=True)
    ap.add_argument("--cikti", default=str(KOK / "evaluation" / "gercek-aday.jsonl"))
    ap.add_argument("--tohum", type=int, default=TOHUM)
    ap.add_argument("--haric", nargs="*", default=[], help="girdileri dışlanacak .jsonl dosyaları (önceki kümeler)")
    ap.add_argument("--kotalar", type=int, nargs=3, default=[KOK_KOTASI, ON_KOTASI, BIR_KOTASI], metavar=("KOK", "ON", "BIR"))
    a = ap.parse_args()
    haric = [json.loads(s)["girdi"] for y in a.haric for s in Path(y).read_text(encoding="utf-8").splitlines() if s.strip()]
    secilen, havuz = sec(Path(a.cv).read_text(encoding="utf-8").splitlines(), a.tohum, haric, *a.kotalar)
    Path(a.cikti).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in secilen), encoding="utf-8")
    print(f"havuz {havuz}, seçilen {len(secilen)} -> {a.cikti}")


if __name__ == "__main__":
    ana()
