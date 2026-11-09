"""Megazeka-Sayı sentetik veri üreteci.

Kullanım: python training/uret.py --train 70000 --validation 2000 --test 2000 --seed 1234 --out data/
Önce yazılı biçim (hedef) kurulur, sonra deterministik olarak sözlü biçime (girdi) çevrilir.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))

from megazeka_sayi import sablonlar as B  # noqa: E402
from megazeka_sayi.turkce import lower_tr  # noqa: E402

# Doğal negatifler: Megazeka verisindeki Common Voice (CC0) hedefleri. MEGAZEKA_CV ya da --cv ile verilir;
# dosya yoksa bu kota negatif_kalip'e geçer.
CV_YOLU = Path(os.environ.get("MEGAZEKA_CV", str(KOK.parent / "proje" / "megazeka" / "data" / "processed" / "train.jsonl.gz")))
BAYT_SINIRI = 180

# Kategori ağırlıkları (yüzde); pozitif ~60, negatif ~40 (v1.1: ek çeşitliliği ve yer tutuculu negatifler için yeniden dengelendi).
AGIRLIKLAR = {
    "para": 8, "yuzde": 5.5, "olcu": 8, "saat": 6.5, "tarih": 6, "sira": 3.5, "telefon": 3, "kod": 2.5,
    "skor": 2.5, "aralik": 3, "ondalik": 8, "kardinal": 11, "buyuk": 2.5, "eksi": 1.5, "karisik": 3,
    "negatif_es": 14.5, "negatif_kalip": 17.5, "negatif_yazili": 8, "negatif_dogal": 9,
}
YAZILI_KAYNAK = B.POZITIF_KATEGORILER

SAYI_KOKLERI = ("sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz",
                "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan", "yüz", "bin", "milyon", "milyar", "trilyon",
                "yarım", "buçuk", "çeyrek", "eksi")


def paylastir(toplam: int) -> dict[str, int]:
    """En büyük kalan yöntemiyle kategori sayıları."""
    t = sum(AGIRLIKLAR.values())
    ham = {k: toplam * w / t for k, w in AGIRLIKLAR.items()}
    sayi = {k: int(v) for k, v in ham.items()}
    kalan = toplam - sum(sayi.values())
    for k in sorted(ham, key=lambda k: (-(ham[k] - sayi[k]), k))[:kalan]:
        sayi[k] += 1
    return sayi


def cv_yukle(yol: Path) -> dict[str, list[str]]:
    """Sayı sözcüğü/rakamı içermeyen Common Voice cümleleri; böl: test/validation/train."""
    havuz = {"train": [], "validation": [], "test": []}
    if not yol.exists():
        return havuz
    gorulen = set()
    with gzip.open(yol, "rt", encoding="utf-8") as f:
        for satir in f:
            r = json.loads(satir)
            if not str(r.get("source", "")).startswith("Common Voice"):
                continue
            t = r["target"].strip()
            if t in gorulen or len(t.encode("utf-8")) > BAYT_SINIRI - 2 or len(t.split()) < 3:
                continue
            gorulen.add(t)
            if re.search(r"\d|[%&@#/+=*<>°²]", t):
                continue
            jetonlar = re.findall(r"[^\W\d_]+", lower_tr(t))
            if any(j.startswith(SAYI_KOKLERI) for j in jetonlar):
                continue
            kova = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16) % 100
            havuz["test" if kova < 6 else "validation" if kova < 12 else "train"].append(t)
    for k in havuz:
        havuz[k].sort()
    return havuz


def cv_duz(t: str) -> str:
    t = lower_tr(t)
    t = re.sub(r"[^\w\s]|_", "", t)
    return re.sub(r"\s+", " ", t).strip()


class Uretici:
    def __init__(self, bolum: str, seed, politika: str, cv: list[str], yasak_hedefler: set[str]):
        self.bolum = bolum
        self.test = bolum == "test"
        self.rng = random.Random(f"{seed}-{bolum}")
        self.politika = politika
        self.cv = list(cv)
        self.rng.shuffle(self.cv)
        self.cv_i = 0
        self.gorulen: set[tuple[str, str]] = set()
        self.hedefler: set[str] = set()
        self.yasak = yasak_hedefler

    def _sec(self, kat):
        return self.rng.choice(B.sablonlar(kat, self.test))

    def _dogal(self):
        if not self.cv:
            return None
        t = self.cv[self.cv_i % len(self.cv)]
        self.cv_i += 1
        if self.rng.random() < 0.6:
            t = cv_duz(t)
        return t, t, "dogal-cv"

    def _tek(self, kat):
        rng = self.rng
        buyuk = rng.random() < 0.4
        if kat == "negatif_dogal":
            return self._dogal()
        if kat == "negatif_yazili":
            kaynak = rng.choices(YAZILI_KAYNAK, [AGIRLIKLAR[k] for k in YAZILI_KAYNAK])[0]
            sid, metin = self._sec(kaynak)
            g, h, kalir, n, _ = B.cumle_uret(metin, rng, buyuk, self.politika, yazili_mod=True)
            if n == 0 or (kalir and kaynak == "kardinal"):
                return None
            return g, h, "yazili:" + sid
        sid, metin = self._sec(kat)
        g, h, kalir, n, kats = B.cumle_uret(metin, rng, buyuk, self.politika,
                                           sarmalayici=kat in ("negatif_es", "negatif_kalip"))
        if kat.startswith("negatif"):
            if g != h:
                raise AssertionError((sid, g, h))
        elif g == h and not (kat == "kardinal" and kalir):
            raise AssertionError((sid, g, h))
        return g, h, sid

    def uret(self, kat: str, adet: int):
        satirlar = []
        deneme = 0
        while len(satirlar) < adet:
            deneme += 1
            if deneme > adet * 400 + 2000:
                raise RuntimeError(f"{self.bolum}/{kat}: yeterince benzersiz örnek üretilemedi ({len(satirlar)}/{adet})")
            s = self._tek(kat)
            if s is None:
                continue
            g, h, sid = s
            if len(g.encode("utf-8")) > BAYT_SINIRI or len(h.encode("utf-8")) > BAYT_SINIRI:
                continue
            if (g, h) in self.gorulen or h in self.yasak:
                continue
            self.gorulen.add((g, h))
            self.hedefler.add(h)
            satirlar.append({"girdi": g, "hedef": h, "kategori": kat, "sablon": sid})
        return satirlar


def uret_bolumler(train, validation, test, seed, politika, cv):
    B.KUCUK_SAYI_POLITIKASI = politika
    istek = {"test": test, "validation": validation, "train": train}
    sonuc, yasak = {}, set()
    for bolum in ("test", "validation", "train"):  # test önce: sızıntıyı önler
        u = Uretici(bolum, seed, politika, cv.get(bolum, []), set(yasak))
        satirlar = []
        sayilar = paylastir(istek[bolum])
        if not u.cv:  # Common Voice yoksa doğal negatifler kalıp negatiflerine kaydırılır
            sayilar["negatif_kalip"] += sayilar.pop("negatif_dogal")
        for kat, adet in sayilar.items():
            satirlar += u.uret(kat, adet)
        u.rng.shuffle(satirlar)
        sonuc[bolum] = satirlar
        yasak |= u.hedefler
    return sonuc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=int, default=70000)
    ap.add_argument("--validation", type=int, default=2000)
    ap.add_argument("--test", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--politika", choices=["yaziyla", "rakamla"], default="yaziyla")
    ap.add_argument("--out", default="data/")
    ap.add_argument("--cv", default=str(CV_YOLU))
    a = ap.parse_args(argv)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cv = cv_yukle(Path(a.cv))
    sonuc = uret_bolumler(a.train, a.validation, a.test, a.seed, a.politika, cv)
    sayim = {}
    for bolum, satirlar in sonuc.items():
        with open(out / f"{bolum}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in satirlar:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        sayim[bolum] = dict(sorted(Counter(r["kategori"] for r in satirlar).items()))
    meta = {
        "seed": a.seed, "politika": a.politika, "adet": {k: len(v) for k, v in sonuc.items()},
        "kategori_sayilari": sayim,
        "test_sablonlari": sorted(B.TEST_SABLONLARI),
        "yazili_test_sablonlari": sorted("yazili:" + i for i in B.TEST_SABLONLARI),
        "cv_havuz": {k: len(v) for k, v in cv.items()},
        "bayt_siniri": BAYT_SINIRI,
    }
    (out / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"adet": meta["adet"], "cv_havuz": meta["cv_havuz"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
