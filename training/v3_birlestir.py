"""v2'nin donmuş yedeklerine D kaynağını ekler; ölçüm dosyaları açılmaz.

    python training/v3_birlestir.py --seed 3300 [--kuru]

Yedekler ilk yazmadan önce alınır. Çelişkiler bütün bölümlerde birlikte aranır;
dışlama, yeni karar, kaynaklar arası çelişki ve bölüm sızıntısı ayrı sayılır.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))

from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi.turkce import inflect, lower_tr  # noqa: E402
from v3_gercek import HARIC_YOLU, haric_yukle, ozet, yaz  # noqa: E402

VERI = KOK / "data"
SURE = r"(?:yaş|saat|gün|gece|hafta|ay|yıl|sene)\w*"
INSAN = r"(?:adam|kadın|ihtiyar|amca|teyze|dede|nine|insan|erkek|delikanlı|biri)\w*"
KUCUGUN_YAZISI = "|".join(S.BIRLER)
SIRA = "|".join(S.sira_oku(n) for n in range(1, 21))
LIK = "|".join(inflect(S.sayi_oku(n), "lik")[0] for n in range(10, 100, 10))


def oku(yol: Path) -> list[dict]:
    return [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]


def eski_karar_ihlali(r: dict) -> str | None:
    """Yeni kararlarla ters etiketleri tarar; belirsiz örnekleri yeniden etiketlemez."""
    g, h = lower_tr(r["girdi"]), lower_tr(r["hedef"])
    if g == h:
        # Bir buçuklu miktar aralığı artık sözcük kalamaz; metreli boy zaten v2'de doğrudur.
        if re.search(r"\bbir buçuk iki (?:saat|ay|gün|hafta|yıl|sene|kilo|kilogram|litre|metre)\b", g):
            return "bucuklu_aralik"
        if re.search(r"\bbir (?:elli|altmış|yetmiş|seksen|doksan)(?: (?:bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz))? boy\w*", g):
            return "birimsiz_boy"
        return None
    for m in re.finditer(rf"\b({KUCUGUN_YAZISI}) ({SURE})", g):
        n = S.BIRLER.index(m[1])
        # Bileşik süre, saat deyişi ve kesir/aralık bu kararın dışındadır.
        if r["kategori"] in {"bilesik", "saat", "saat_deyis", "aralik"}:
            continue
        if re.search(rf"\b{n} {re.escape(m[2])}\b", h):
            return "kucuk_sure_yas"
    if re.search(rf"\b(?:{LIK}) (?:bir )?{INSAN}", g) and re.search(rf"\d+'l[ıiuü]k (?:bir )?{INSAN}", h):
        return "yas_tahmini"
    unvan = r"(?:kaptan|subay|kâtip|katip|müdür|başkan|yardımcı)\w*"
    sifat = r"(?:büyük|küçük|uzun|kısa|uykusuz|soğuk|sıcak|zor|kolay|sessiz|güzel|eski|yeni)"
    if re.search(rf"\b(?:{SIRA}) (?:{unvan}|{sifat} [^\W\d_]+)", g) and re.search(rf"\d+\. (?:{unvan}|{sifat} [^\W\d_]+)", h):
        return "anlatim_unvan"
    # Eski etiket aralık yapmış ya da hiç çevirmemişse yeni yazıma aykırıdır.
    if re.search(r"\bbir buçuk iki (?:saat|ay|gün|hafta|yıl|sene|kilo|kilogram|litre|metre)\b", g):
        if "1,5-2" not in h:
            return "bucuklu_aralik"
    if re.search(r"\bbir (?:elli|altmış|yetmiş|seksen|doksan)(?: (?:bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz))? boy\w*", g):
        if not re.search(r"\b1,[5-9]\d boy", h):
            return "birimsiz_boy"
    return None


def birlestir(eski: dict, yeni: dict, dis: set[str], seed: int = 3300) -> tuple[dict, dict]:
    """Saf birleştirme; testleri ve deneme çalıştırmasını dosyalardan bağımsız kılar."""
    adaylar = []
    sayim = {b: Counter() for b in ("train", "validation", "test-v3")}
    for b in ("train", "validation"):
        for r in eski[b]:
            adaylar.append((b, "eski", dict(r)))
        for r in yeni[b]:
            adaylar.append((b, "d", {**r, "kaynak": "d"}))
    adaylar += [("test-v3", "d", {**r, "kaynak": "d"}) for r in yeni["test"]]
    # Dışlama/karar elemesinden önce toplanır: çelişkili girdinin iki etiketi de çıkar.
    hedefler = defaultdict(set)
    for _, _, r in adaylar:
        hedefler[r["girdi"]].add(r["hedef"])
    celiskiler = {g for g, hs in hedefler.items() if len(hs) > 1}
    temiz = {b: [] for b in sayim}
    gecen = []
    for b, k, r in adaylar:
        nedenler = []
        if ozet(r["girdi"]) in dis or ozet(r["hedef"]) in dis:
            nedenler.append("dislanan")
        if r["girdi"] in celiskiler:
            nedenler.append("celiskili")
        ihlal = eski_karar_ihlali(r) if k == "eski" else None
        if ihlal:
            nedenler.append("eski_karar")
            sayim[b]["karar_" + ihlal] += 1
        for neden in nedenler:
            sayim[b]["saptanan_" + neden] += 1
        if nedenler:
            # 'cikarilan_*' birbirini dışlar; 'saptanan_*' örtüşebilir.
            sayim[b]["cikarilan_" + nedenler[0]] += 1
        else:
            gecen.append((b, k, r))
    # Test > validation > train: D test cümlesi eski akışta varsa eğitimden çıkar.
    sahip_g, sahip_h = {}, {}
    for b in ("test-v3", "validation", "train"):
        for bolum, _, r in gecen:
            if bolum == b:
                sahip_g.setdefault(r["girdi"], b)
                sahip_h.setdefault(r["hedef"], b)
    gorulen = {b: set() for b in temiz}
    for b, _, r in gecen:
        g, h = r["girdi"], r["hedef"]
        if sahip_g[g] != b or sahip_h[h] != b:
            sayim[b]["cikarilan_bolum_cakismasi"] += 1
        elif (g, h) in gorulen[b]:
            sayim[b]["cikarilan_yinelenen"] += 1
        else:
            gorulen[b].add((g, h))
            temiz[b].append(r)
    rapor = {"seed": seed, "celiskili_girdi": len(celiskiler), "bolumler": {}}
    for b, satirlar in temiz.items():
        random.Random(f"{seed}-{b}").shuffle(satirlar)
        rapor["bolumler"][b] = {
            "satir": len(satirlar), "kaynak": dict(sorted(Counter(r.get("kaynak", "v2") for r in satirlar).items())),
            "kategori": dict(sorted(Counter(r["kategori"] for r in satirlar).items())),
            "negatif_payi": sum(r["girdi"] == r["hedef"] for r in satirlar) / max(1, len(satirlar)),
            "elemeler": dict(sorted(sayim[b].items())),
            "cikarilan_toplam": sum(v for k, v in sayim[b].items() if k.startswith("cikarilan_")),
        }
    return temiz, rapor


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=3300)
    ap.add_argument("--kuru", action="store_true", help="dosya ve yedek yazmadan hesapla")
    ap.add_argument("--data", type=Path, default=VERI)
    ap.add_argument("--haric", type=Path, default=HARIC_YOLU)
    a = ap.parse_args(argv)
    # Gerekli bütün dosyalar okunup doğrulanmadan ana akışa dokunulmaz.
    yeni = {b: oku(a.data / "v3" / f"d-{b}.jsonl") for b in ("train", "validation", "test")}
    d_rapor = a.data / "v3/d-rapor.json"
    if d_rapor.exists():
        esikler = json.loads(d_rapor.read_text(encoding="utf-8"))["esikler"]
        if not all(e["gecti"] for e in esikler.values()):
            raise ValueError("D kaynağının eşikleri geçmedi; ana eğitim akışı yazılmadı")
    dis = haric_yukle(a.haric)
    eski = {}
    for b in ("train", "validation"):
        yedek = a.data / f"{b}-v2.jsonl"
        eski[b] = oku(yedek if yedek.exists() else a.data / f"{b}.jsonl")
    sonuc, rapor = birlestir(eski, yeni, dis, a.seed)
    if not a.kuru:
        for b in ("train", "validation"):
            yedek = a.data / f"{b}-v2.jsonl"
            if not yedek.exists():
                shutil.copyfile(a.data / f"{b}.jsonl", yedek)
        for b, satirlar in sonuc.items():
            yaz(a.data / f"{b}.jsonl", satirlar)
        (a.data / "metadata-v3.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
