"""v3 akışına E kaynağını ekler (v3e): data/train.jsonl ve data/validation.jsonl yeniden yazılır.

    python training/v3e_birlestir.py [--kuru]

İlk çalıştırmada mevcut v3 akışı data/train-v3.jsonl ve data/validation-v3.jsonl olarak yedeklenir; sonraki
çalıştırmalar hep bu yedeklerden okur. E1 (elle etiketli gerçek cümleler) eğitimde E1_TEKRAR kez yer alır.
Bir E girdisi eski akışta başka hedefle geçiyorsa eski satır çıkarılır (E kararları yenidir) ve sayılır.
data/v3/haric-md5.txt özetiyle eşleşen her satır çıkarılır. Test dosyalarına dokunulmaz.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

from v3_gercek import HARIC_YOLU, haric_yukle, ozet, yaz  # noqa: E402

VERI = KOK / "data"
E1_TEKRAR = 2


def oku(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def birlestir(eski: dict, yeni: dict, dis: set[str], seed: int) -> tuple[dict, dict]:
    e_hedef = {}
    for b in ("train", "validation"):
        for r in yeni[b]:
            e_hedef[r["girdi"]] = r["hedef"]
    sonuc, rapor = {}, {"seed": seed, "e1_tekrar": E1_TEKRAR, "bolumler": {}}
    for b in ("train", "validation"):
        say = Counter()
        satirlar = []
        for r in eski[b]:
            if ozet(r["girdi"]) in dis or ozet(r["hedef"]) in dis:
                say["eski_dislanan"] += 1
            elif r["girdi"] in e_hedef and e_hedef[r["girdi"]] != r["hedef"]:
                say["eski_e_ile_celisen"] += 1
            elif r["girdi"] in e_hedef:
                say["eski_e_ile_ayni"] += 1  # E'den gelen kopya yeterli
            else:
                satirlar.append(r)
        for r in yeni[b]:
            r = {k: v for k, v in r.items() if k != "olgu"} | {"kaynak": "e", "olgu": r["olgu"]}
            n = E1_TEKRAR if (b == "train" and r["olgu"] == "E1") else 1
            satirlar += [r] * n
        random.Random(f"{seed}-{b}").shuffle(satirlar)
        sonuc[b] = satirlar
        rapor["bolumler"][b] = {
            "satir": len(satirlar),
            "kaynak": dict(sorted(Counter(r.get("kaynak", "v2") for r in satirlar).items())),
            "e_olgu": dict(sorted(Counter(r["olgu"] for r in satirlar if r.get("kaynak") == "e").items())),
            "negatif_payi": round(sum(r["girdi"] == r["hedef"] for r in satirlar) / len(satirlar), 4),
            "elemeler": dict(say),
        }
    return sonuc, rapor


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=3323)
    ap.add_argument("--kuru", action="store_true")
    a = ap.parse_args(argv)
    eski = {}
    for b in ("train", "validation"):
        yedek = VERI / f"{b}-v3.jsonl"
        eski[b] = oku(yedek if yedek.exists() else VERI / f"{b}.jsonl")
    yeni = {b: oku(VERI / "v3" / f"e-{b}.jsonl") for b in ("train", "validation")}
    sonuc, rapor = birlestir(eski, yeni, haric_yukle(HARIC_YOLU), a.seed)
    if not a.kuru:
        for b in ("train", "validation"):
            yedek = VERI / f"{b}-v3.jsonl"
            if not yedek.exists():
                shutil.copyfile(VERI / f"{b}.jsonl", yedek)
            yaz(VERI / f"{b}.jsonl", sonuc[b])
        (VERI / "metadata-v3e.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
