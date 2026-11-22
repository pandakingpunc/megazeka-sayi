import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))
sys.path.insert(0, str(KOK / "evaluation"))

import v3e_hedefli as E  # noqa: E402


def test_iyelik_ekleri():
    assert E.iyelik(40, "ni") == ("40'ını", "kırkını")
    assert E.iyelik(50, "nden") == ("50'sinden", "ellisinden")
    assert E.iyelik(30, "nde") == ("30'unda", "otuzunda")
    assert E.iyelik(60, "ne") == ("60'ına", "altmışına")
    assert E.iyelik(45, "ni") == ("45'ini", "kırk beşini")


def test_kucuk_yas_yaziyla_kalir():
    satirlar = E.e2(3322)
    kucuk = [r for r in satirlar if r["sablon"].startswith("v3e-e2-yas") and r["girdi"] == r["hedef"]]
    assert kucuk and all(not any(c.isdigit() for c in r["hedef"]) for r in kucuk)


def test_aralik_bicimi():
    for r in E.e3(3322):
        if r["girdi"] != r["hedef"]:
            assert any(f"{a}-{b}" in r["hedef"] for a, b in E.CIFTLER)
        assert "üç beş kuruş" not in r["girdi"].lower() or r["girdi"] == r["hedef"]


def test_olcum_kumeleriyle_ortusme_yok():
    yasak = E.olcum_ngramlari()
    for cumleler in E.SOZ_CUMLELERI.values():
        for c in cumleler:
            assert not (E.ngramlar(c) & yasak), c


def test_uretilen_veri_dislama_listesinde_yok():
    from v3_gercek import HARIC_YOLU, haric_yukle, ozet
    dis = haric_yukle(HARIC_YOLU)
    for b in ("train", "validation"):
        yol = KOK / "data" / "v3" / f"e-{b}.jsonl"
        if not yol.exists():
            continue
        for s in yol.read_text(encoding="utf-8").splitlines():
            r = json.loads(s)
            assert ozet(r["girdi"]) not in dis and ozet(r["hedef"]) not in dis


def test_koruma_onluk_iyelik_n():
    from megazeka_sayi.cikarim import koru, sayi_benzeri_mi
    for w in ("ellisinden", "kırkını", "otuzunda", "altmışına", "yirmisine", "doksanını"):
        assert sayi_benzeri_mi(w), w
    for w in ("ikisini", "birini", "onunla"):
        assert not sayi_benzeri_mi(w), w
    assert koru("Ama adam ellisinden sonra rakıya vurdu.", "Ama adam 50'sinden sonra rakıya vurdu.")[0] == \
        "Ama adam 50'sinden sonra rakıya vurdu."
    assert koru("Her ikisini de gördüm.", "Her 2'sini de gördüm.")[0] == "Her ikisini de gördüm."
