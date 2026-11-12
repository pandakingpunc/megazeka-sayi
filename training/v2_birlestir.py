"""v2 verisini birleştirir: v1.1 akışı (sabit dosya) + data/v2/{a,b,c}-* kaynakları.

    python training/v2_birlestir.py [--seed 2200] [--kuru]

- Eski akış `data/train-v1.1.jsonl` ve `data/validation-v1.1.jsonl` dosyalarından okunur (ilk çalıştırmada
  `train.jsonl` / `validation.jsonl` bu adlara kopyalanır); belirsiz telefon satırları elenir (SPEC-v2 §A2).
- Zorluk kümeleriyle (`evaluation/challenge*.jsonl`) aynı girdiye sahip eğitim/doğrulama satırları çıkarılır.
- Aynı girdiye farklı hedef veren satırlar (kaynaklar arası çelişki) iki taraftan da çıkarılır.
- Çıktı: `data/train.jsonl`, `data/validation.jsonl`, `data/test-v2.jsonl`, `data/metadata-v2.json`.
  `data/test.jsonl` (v1.1) ve `data/test-v1.jsonl` donmuş kalır.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

from v2_sayisal import telefon_satiri_belirsiz  # noqa: E402

VERI = KOK / "data"
KAYNAKLAR = ("a", "b", "c")
BAYT_SINIRI = 180


def oku(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def yaz(yol: Path, satirlar: list[dict]) -> None:
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        for r in satirlar:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2200)
    ap.add_argument("--kuru", action="store_true", help="yalnız say, dosya yazma")
    a = ap.parse_args(argv)

    for ad in ("train", "validation"):
        yedek = VERI / f"{ad}-v1.1.jsonl"
        if not yedek.exists():
            shutil.copyfile(VERI / f"{ad}.jsonl", yedek)

    zorluk = set()
    for yol in sorted((KOK / "evaluation").glob("challenge*.jsonl")):
        zorluk |= {r["girdi"] for r in oku(yol)}

    rapor: dict = {"seed": a.seed, "bolumler": {}}
    test_v2 = []
    for k in KAYNAKLAR:
        test_v2 += [{**r, "kaynak": k} for r in oku(VERI / "v2" / f"{k}-test.jsonl")]
    test_girdileri = {r["girdi"] for r in test_v2} | {r["girdi"] for r in oku(VERI / "test.jsonl")} \
        | {r["girdi"] for r in oku(VERI / "test-v1.jsonl")}

    for ad in ("train", "validation"):
        eski = oku(VERI / f"{ad}-v1.1.jsonl")
        sayim = Counter()
        satirlar = []
        for r in eski:
            if r["kategori"] in ("telefon", "karisik") and telefon_satiri_belirsiz(r["girdi"], r["hedef"]):
                sayim["eski_belirsiz_telefon"] += 1
                continue
            satirlar.append({**r, "kaynak": "v1.1"})
        sayim["eski"] = len(satirlar)
        for k in KAYNAKLAR:
            yeni = oku(VERI / "v2" / f"{k}-{ad}.jsonl")
            sayim[f"yeni_{k}"] = len(yeni)
            satirlar += [{**r, "kaynak": k} for r in yeni]

        hedefler = defaultdict(set)
        for r in satirlar:
            hedefler[r["girdi"]].add(r["hedef"])
        temiz, gorulen = [], set()
        for r in satirlar:
            g = r["girdi"]
            if g in zorluk:
                sayim["zorluk_cakismasi"] += 1
            elif len(hedefler[g]) > 1:
                sayim["celiskili_girdi"] += 1
            elif g in test_girdileri and r["kaynak"] != "v1.1":
                sayim["test_cakismasi"] += 1
            elif (g, r["hedef"]) in gorulen:
                sayim["yinelenen"] += 1
            elif max(len(g.encode("utf-8")), len(r["hedef"].encode("utf-8"))) > BAYT_SINIRI:
                sayim["uzun"] += 1
            else:
                gorulen.add((g, r["hedef"]))
                temiz.append(r)
        random.Random(f"{a.seed}-{ad}").shuffle(temiz)
        rapor["bolumler"][ad] = {
            "adet": len(temiz), "elemeler": dict(sayim),
            "kaynak": dict(Counter(r["kaynak"] for r in temiz)),
            "kategori": dict(sorted(Counter(r["kategori"] for r in temiz).items())),
            "negatif_payi": round(sum(r["girdi"] == r["hedef"] for r in temiz) / len(temiz), 4),
        }
        if not a.kuru:
            yaz(VERI / f"{ad}.jsonl", temiz)

    test_v2 = [r for r in test_v2 if r["girdi"] not in zorluk]
    rapor["bolumler"]["test-v2"] = {
        "adet": len(test_v2), "kaynak": dict(Counter(r["kaynak"] for r in test_v2)),
        "kategori": dict(sorted(Counter(r["kategori"] for r in test_v2).items())),
        "negatif_payi": round(sum(r["girdi"] == r["hedef"] for r in test_v2) / len(test_v2), 4),
    }
    if not a.kuru:
        yaz(VERI / "test-v2.jsonl", test_v2)
        (VERI / "metadata-v2.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
