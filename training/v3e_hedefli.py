"""v3 E kaynağı: ByT5-base adayının gerçek metindeki hatalarına yönelik hedefli veri (2026-11-22).

    python training/v3e_hedefli.py --out data/v3

E1 · elle etiketlenmiş gerçek Common Voice cümleleri (training/v3e_gercek_etiket.py)
E2 · yaş ve 10 üstü sayı + ad: `kırk yaşında` → `40 yaşında`, `kırkını geçmiş` → `40'ını geçmiş`,
     `iki milyon esir` → `2 milyon esir`; karşıt: 0–9 yaş yazıyla kalır
E3 · yan yana yaklaşık aralık: `beş on adım` → `5-10 adım`, `üç dört kişi` → `3-4 kişi`; karşıt: `bir iki gün`
E4 · sıra sayısı zinciri (`on ikinci maddenin birinci fıkrası` → `12. maddenin 1. fıkrası`) ve sayma dizileri (değişmez)
E5 · eğitimde olmayan sayı sözcüklü deyim ve atasözleri (değişmez)

Ölçüm kümeleri okunmaz; yalnız data/v3/haric-md5.txt özetleriyle ve gerçek kümelerle 3-sözcük örtüşmesine karşı
denetlenir (E5 sözleri ve E1 adayları için). Çıktı: data/v3/e-{train,validation}.jsonl, data/v3/e-rapor.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "training"))
sys.path.insert(0, str(KOK / "evaluation"))

from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi.turkce import ae, iiuu, ilk_harfi_buyut, lower_tr, son_unlu  # noqa: E402
from gercek_ornekle import kokler  # noqa: E402
from uret import cv_duz  # noqa: E402
from v3_gercek import CV_YOLU, HARIC_YOLU, ek_parcasi, guvenli_sozcuk, haric_yukle, ozet, para  # noqa: E402
from v3e_gercek_etiket import etiketle  # noqa: E402

BAYT = 180
NOKTALAMA = re.compile(r"[^\w\s{}]|_")


# ---------------------------------------------------------------- ortak
def oku(n: int) -> str:
    return S.sayi_oku(n)


def yaz(n: int) -> str:
    return S.yaz_sayi(n)


def iyelik(n: int, hal: str) -> tuple[str, str]:
    """3. tekil iyelik + hâl: kırkını → 40'ını, ellisinden → 50'sinden, otuzunda → 30'unda."""
    soz = oku(n)
    son = soz.split()[-1]
    p = ek_parcasi(son, "si")
    u = son_unlu(p)
    ek = p + {"": "", "ni": "n" + iiuu(u), "nde": "nd" + ae(u), "nden": "nd" + ae(u) + "n",
              "ne": "n" + ae(u)}[hal]
    return yaz(n) + "'" + ek, soz + ek


def duzlestir(metin: str) -> str:
    return re.sub(r"\s+", " ", NOKTALAMA.sub("", lower_tr(metin))).strip()


def bas_harf(t: str) -> str:
    return ilk_harfi_buyut(t) if t and t[0].isalpha() else t


def satir(girdi: str, hedef: str, kategori: str, sablon: str) -> dict:
    return {"girdi": girdi, "hedef": hedef, "kategori": kategori, "sablon": sablon}


def iki_bicim(metin: str, degerler: dict[str, tuple[str, str]], kategori: str, sablon: str) -> list[dict]:
    """Noktalı (büyük harfle başlar) ve düz (küçük harf, noktalamasız) biçim; değerler (yazılı, sözlü)."""
    out = []
    for duz in (False, True):
        m = duzlestir(metin) if duz else metin
        g = m.format(**{k: v[1] for k, v in degerler.items()})
        h = m.format(**{k: v[0] for k, v in degerler.items()})
        if not duz:
            g, h = bas_harf(g), bas_harf(h)
        if max(len(g.encode()), len(h.encode())) <= BAYT:
            out.append(satir(g, h, kategori if g != h else "negatif_kalip", sablon))
    return out


# ---------------------------------------------------------------- E1
def e1_adaylar(cv_yolu: Path = CV_YOLU) -> list[str]:
    """v3e_gercek_etiket'teki 466 adayın seçimi (eğitim ve ölçüm kümelerinde geçmeyen gerçek cümleler)."""
    egitim = set()
    # train/validation: E eklenmeden önceki v3 akışı (birleştirme sonrası yedeği train-v3.jsonl'dir).
    yollar = [KOK / "data" / (f"{b}-v3.jsonl" if (KOK / "data" / f"{b}-v3.jsonl").exists() else f"{b}.jsonl")
              for b in ("train", "validation")]
    yollar += [KOK / "data" / f for f in ("test-v3.jsonl", "test.jsonl", "test-v1.jsonl", "test-v2.jsonl")]
    for yol in yollar:
        for s in yol.read_text(encoding="utf-8").splitlines():
            r = json.loads(s)
            egitim.add(cv_duz(r["girdi"]))
            egitim.add(cv_duz(r["hedef"]))
    olcum = set()
    for f in ("gercek.jsonl", "gercek2.jsonl", "gercek3.jsonl"):
        for s in (KOK / "evaluation" / f).read_text(encoding="utf-8").splitlines():
            olcum.add(cv_duz(json.loads(s)["girdi"]))
    BUYUK = ("on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan", "yüz", "bin", "milyon",
             "milyar", "buçuk")
    KUCUK = ("iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
    ON_EK = ("onu", "ona", "onl", "ond", "onc", "ons", "yüzü", "yüzün", "yüze", "bina", "bini", "bine", "binm", "bind")
    sec = []
    for c in sorted(set(x.strip() for x in cv_yolu.read_text(encoding="utf-8").splitlines())):
        if re.search(r"\d", c) or len(c.encode()) > 178 or len(c.split()) < 2:
            continue
        d = cv_duz(c)
        if d in egitim or d in olcum:
            continue
        lw = lower_tr(c)
        riskli = [w for w in re.findall(r"[^\W\d_]+", lw) if kokler(w) and not guvenli_sozcuk(w)]
        if not riskli:
            continue
        buyuk = any(w == b or (w.startswith(b) and not w.startswith(ON_EK)) for w in riskli for b in BUYUK)
        yas = re.search(r"\b(?:" + "|".join(KUCUK + BUYUK) + r")\w* yaş", lw)
        yan = re.search(r"\b(?:" + "|".join(KUCUK + ("on",)) + r") (?:" + "|".join(KUCUK[1:] + ("on",)) + r")\b", lw)
        if buyuk or yas or yan:
            sec.append(c)
    return sec


def e1(cv_yolu: Path = CV_YOLU) -> list[dict]:
    from v3e_gercek_etiket import L, DUSUR
    adaylar = e1_adaylar(cv_yolu)
    ciftler = etiketle(adaylar)
    out = []
    no_map = [i for i in range(1, len(adaylar) + 1) if i not in DUSUR]
    for no, (g, h) in zip(no_map, ciftler):
        kat = "negatif_dogal" if g == h else ("aralik" if re.search(r"\d-\d", h) else
                                               "para" if re.search(r"TL|kuruş", h) and re.search(r"\d", h) else "kardinal")
        sid = f"v3e-e1-{no:03d}"
        out.append(satir(g, h, kat, sid))
        # Düz biçim: girdi cv_duz; hedefte aynı değişiklikler küçük harfli girdiye uygulanır.
        gd, hd = cv_duz(g), cv_duz(g)
        tamam = True
        for eski, yeni in L.get(no, ()):
            e = cv_duz(eski)
            y = re.sub(r"[.!?…]+$", "", yeni)
            if hd.count(e) != 1:
                tamam = False
                break
            hd = hd.replace(e, y)
        if tamam and gd:
            out.append(satir(gd, hd, kat, sid))
    return out


# ---------------------------------------------------------------- E2
YAS_SABLON = (
    "{v} yaşında bir adam kapıyı çaldı.", "Babam {v} yaşında emekli oldu.", "Ben {v} yaşındayım, bunları bilirim.",
    "Kız henüz {v} yaşındaydı.",
    "Dedem {v} yaşına girdi ama hâlâ bağa gidiyor.", "Annem {v} yaşından sonra okumayı öğrendi.",
    "{v} yaşlarında bir çoban bize yolu gösterdi.",
    "Adam {v} yaşını geçmişti, saçları ağarmıştı.", "Oğlu {v} yaşında askere gitti.",
    "{v} yaşındaki ihtiyar, bastonuna dayanarak kalktı.", "Ben de {v} yaşındayken aynı hatayı yapmıştım.",
    "Komşumuz {v} yaşında ölmüş.",
    "Kadın {v} yaşlarında gösteriyordu.", "Daha {v} yaşında bir delikanlıydı.",
    "{v} yaşına kadar hiç şehir görmemişti.", "Kocası ondan {v} yaş büyüktü.", "Aramızda {v} yaş fark var.",
    "Bu ağaç {v} yaşında, dedem dikmiş.", "Hacı Ömer {v} yaşında hâlâ dimdikti.",
    "Ben {v} yaşında adamım, bana akıl verme!", "{v} yaşına bastı, bir türlü evlenmedi.",
    "Öğretmen {v} yaşlarında, gözlüklü bir adamdı.", "Mahkemede {v} yaşında olduğunu söyledi.",
    "Bu sene {v} yaşına giriyorum.", "{v} yaşından beri bu dükkânda çalışıyor.",
    "Hastaneye {v} yaşında bir çocuk getirdiler.", "Yanında {v} yaşlarında bir oğlan vardı.",
    "Öldüğünde {v} yaşındaydı.", "Sen {v} yaşına gelmişsin, hâlâ çocuk gibisin.",
    "Nüfus kâğıdına göre {v} yaşındaymış.", "{v} yaşında bir kadın için fazla dinçti.",
    "Benim gibi {v} yaşındaki bir adamı kim işe alır?",
    "Rahmetli {v} yaşına kadar yaşadı.", "Kendisi {v} yaşlarında, kır saçlı bir zattı.",
    "Ağabeyim {v} yaşındayken köyden ayrıldı.", "O vakit daha {v} yaşımdaydım.",
    "Babası {v} yaşında olduğu halde tarlaya iniyordu.", "Hepimiz {v} yaşın üstündeydik.",
)
YAS_IYELIK = (
    ("Adam {v} geçmiş, hâlâ bekârdı.", "ni"), ("Kendisi {v} çoktan aşmıştı.", "ni"),
    ("Sen {v} geçmiş adamsın, utan!", "ni"), ("Doktor {v} geçmiş hastalara bu ilacı vermiyor.", "ni"),
    ("{v} sonra sigarayı bıraktı.", "nden"), ("Teyzem {v} sonra bahçeyle uğraşmaya başladı.", "nden"),
    ("{v} sonra insanın aklı başına gelir.", "nden"), ("Annem {v} sonra okumaya başladı.", "nden"),
    ("Babam {v} bu evi yaptırdı.", "nde"), ("Şimdi sağ olsa {v} olacaktı.", "nde"),
    ("Kadın {v} gösteriyordu.", "nde"), ("Ben {v} köyü terk ettim.", "nde"),
    ("Annem {v} gelmeden saçları ağarmıştı.", "ne"), ("{v} girmeden evlenmek istiyordu.", "ne"),
    ("Daha {v} basmadan bütün işleri öğrenmişti.", "ne"), ("Bu adam bugün tam {v} girdi.", "ne"),
)
SAYI_AD = (
    "{v} gün sonra köye döndü.", "Bu {v} sene içinde çok şey değişti.",
    "Toplantıya {v} kişi gelmişti.", "Kapıyı {v} kere çaldı.",
    "Bu iş {v} günde biter.", "{v} gündür yağmur yağıyor.", "Fabrikada ayın {v} gününde maaş verilirdi.",
    "{v} senedir bu evde oturuyoruz.", "Aradan {v} yıl geçti.",
    "Köyde {v} hane kalmıştı.", "Sınıfta {v} öğrenci vardı.", "Masada {v} tabak duruyordu.",
    "{v} dakika sonra tren kalktı.", "Tam {v} saat yol yürüdük.",
    "Ceza olarak {v} sene yemişti.", "{v} sene evvel buradan geçmiştim.",
)
BUYUK_AD = (
    "Şehirde {v} insan yaşıyor.", "Savaşta {v} asker ölmüş.",
    "Memlekette {v} köylü toprak bekliyor.", "Ülkenin nüfusu {v} kişiyi geçti.", "{v} kişi bu haberi okudu.",
)


def yas_degeri(rng: random.Random) -> int:
    r = rng.random()
    if r < 0.2:
        return rng.randint(2, 9)
    if r < 0.6:
        return rng.choice((10, 20, 30, 40, 50, 60, 70, 80, 90))
    if r < 0.97:
        return rng.randint(11, 99)
    return rng.randint(100, 110)


def e2(seed: int) -> list[dict]:
    rng = random.Random(f"{seed}-E2")
    out = []
    for i, m in enumerate(YAS_SABLON):
        for _ in range(36):
            n = yas_degeri(rng)
            v = (oku(n), oku(n)) if n < 10 else (yaz(n), oku(n))
            out += iki_bicim(m, {"v": v}, "kardinal", f"v3e-e2-yas-{i:02d}")
    for i, (m, hal) in enumerate(YAS_IYELIK):
        for _ in range(45):
            n = rng.choice((20, 30, 40, 40, 50, 50, 60, 60, 70, 80)) if rng.random() < 0.7 else rng.randint(15, 89)
            out += iki_bicim(m, {"v": iyelik(n, hal)}, "kardinal", f"v3e-e2-iyelik-{i:02d}")
    for i, m in enumerate(SAYI_AD):
        for _ in range(16):
            n = rng.choice((10, 10, 10, 12, 15, 20, 25, 30, 40, 50)) if rng.random() < 0.7 else rng.randint(11, 99)
            out += iki_bicim(m, {"v": (yaz(n), oku(n))}, "kardinal", f"v3e-e2-ad-{i:02d}")
    for i, m in enumerate(BUYUK_AD):
        for _ in range(25):
            n = rng.randint(2, 9) if rng.random() < 0.6 else rng.randint(10, 90)
            b = rng.choice(("milyon", "milyon", "bin")) if n < 10 else "milyon"
            v = (f"{n} {b}", f"{oku(n)} {b}") if b == "milyon" else (yaz(n * 1000), oku(n * 1000))
            out += iki_bicim(m, {"v": v}, "buyuk", f"v3e-e2-buyuk-{i:02d}")
    return out


# ---------------------------------------------------------------- E3
ARALIK_AD = (
    "{v} adım ileride bir çeşme vardı.", "{v} adım yürüdükten sonra durdu.",
    "{v} adım arkasından yürüyordum.", "Çocuklar {v} adım geride kaldı.",
    "Bu işten ancak {v} kuruş kazanırdı.", "Kesesinde {v} kuruş kalmıştı.", "Dilenciye {v} kuruş verdi.",
    "{v} günde iyileşirsin.", "Doktor {v} gün yatmasını söyledi.",
    "Kapıda {v} kişi bekliyordu.", "Kahvede {v} kişi oturmuş, domino oynuyordu.",
    "{v} sene sonra köye döndü.", "{v} sene evvel buradaydık.",
    "{v} dakika sonra tren geldi.", "Her merdivende {v} dakika dinlendi.", "Dağın eteğinde {v} ev vardı.",
    "Masada {v} tane elma vardı.", "{v} tanesi dışarıda dolaşıyordu.", "Bugün {v} kere öksürdü.",
    "Kadını {v} saat bekletti.", "Yol {v} saat sürer.", "Tepeden {v} süvari göründü.",
    "{v} çocuk sokakta top oynuyordu.", "{v} aylık bir çalışmanın sonunda bitti.",
    "{v} haftada bir bize uğrardı.", "{v} kelimelik cümlelerle konuşuyordu.", "Bahçede {v} ağaç vardı.",
    "Başucunda {v} sinek vızıldıyordu.", "{v} parça eşyası vardı, onları da sattı.",
    "Kasabadan {v} kutu ilaç aldım.", "Elinde avucunda {v} altın kalmıştı.", "{v} yerde kalabalık toplanmıştı.",
)
ARALIK_PARA = (
    ("Ona {v} verdim.", None), ("{v} kazanıp borcunu ödeyecek.", None), ("Elime {v} sıkıştırdı.", None),
    ("Bunu {v} satarım.", "yonelme"), ("Bu çoraplar {v} satılıyor.", "yonelme"),
    ("{v} bir senet imzaladı.", "lik"), ("Cebinden {v} çıkardı.", "lik"),
)
CIFTLER = ((2, 3), (2, 3), (3, 4), (3, 4), (4, 5), (4, 5), (5, 6), (5, 6), (6, 7), (7, 8), (7, 8), (8, 9),
           (8, 10), (5, 10), (5, 10), (5, 10), (5, 10), (3, 5), (10, 12), (10, 15), (15, 20), (15, 20), (20, 25),
           (20, 30), (25, 30), (30, 40), (40, 50), (40, 50), (50, 60), (60, 70), (70, 80))


def e3(seed: int) -> list[dict]:
    rng = random.Random(f"{seed}-E3")
    out = []
    for i, m in enumerate(ARALIK_AD):
        for _ in range(38):
            if rng.random() < 0.08:
                v = ("bir iki", "bir iki")  # içinde bir geçen aralık sözcük kalır
            else:
                a, b = rng.choice(CIFTLER)
                if (a, b) == (3, 5) and "kuruş" in m:
                    a, b = 5, 10  # 'üç beş kuruş' D2'de deyim
                v = (f"{a}-{b}", f"{oku(a)} {oku(b)}")
            out += iki_bicim(m, {"v": v}, "aralik", f"v3e-e3-ad-{i:02d}")
    for i, (m, ek) in enumerate(ARALIK_PARA):
        for _ in range(40):
            a, b = rng.choice(CIFTLER)
            p = para(b, ek)
            v = (f"{a}-" + p.yazili, oku(a) + " " + p.sozlu)
            out += iki_bicim(m, {"v": v}, "aralik", f"v3e-e3-para-{i:02d}")
    return out


# ---------------------------------------------------------------- E4
SIRA_SABLON = (
    "Kanunun {a} maddesi bunu açıkça yasaklar.",
    "Yönetmeliğin {a} maddesinin {b} bendine bakın.", "{a} bölümün {b} paragrafını tekrar oku.",
    "Sözleşmenin {a} maddesine göre kira artmaz.", "{a} sayfanın {b} satırında bir hata var.",
    "Raporun {a} bölümünde ayrıntılar yazıyor.", "{a} maddenin {b} fıkrası değiştirildi.",
)
SAYMA = ("bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on")
SAYMA_TASIYICI = ("{s}.", "Çocuk parmaklarıyla saydı: {s}.", "Yüksek sesle saymaya başladı: {s}…",
                  "Öğretmen tahtaya yazdı: {s}.", '"{s}" diye sayarken uykuya daldı.', "{s}, haydi çık!")


def e4(seed: int) -> list[dict]:
    rng = random.Random(f"{seed}-E4")
    out = []
    for i, m in enumerate(SIRA_SABLON):
        for _ in range(40):
            a = rng.choice((1, 2, 3, 4, 5, 10, 11, 12, 13, 15, 20, 21, 25, 30, 42)) if rng.random() < 0.7 else rng.randint(1, 60)
            b = rng.randint(1, 9)
            out += iki_bicim(m, {"a": (f"{a}.", S.sira_oku(a)), "b": (f"{b}.", S.sira_oku(b))}, "sira",
                             f"v3e-e4-sira-{i:02d}")
    for i, m in enumerate(SAYMA_TASIYICI):
        for son in range(3, 11):
            dizi = list(SAYMA[:son])
            for ters in (False, True):
                s = ", ".join(reversed(dizi) if ters else dizi)
                out += iki_bicim(m, {"s": (s, s)}, "negatif_kalip", f"v3e-e4-sayma-{i:02d}")
    return out


# ---------------------------------------------------------------- E5
# Kendi bilgimizle seçilen, D2 listesinde olmayan sözler; her biri birkaç doğal cümlede (girdi = hedef).
SOZ_CUMLELERI = {
    "kirk-katir": ("Kırk katır mı, kırk satır mı?", "Bana kırk katır mı kırk satır mı diye sordular.",
                   "Seçim kırk katır mı kırk satır mı, ikisi de kötü."),
    "kirk-yillik-kani": ("Kırk yıllık Kâni olur mu Yani?", "Ne demişler: kırk yıllık Kâni olur mu Yani.",
                         "O adam değişmez, kırk yıllık Kâni olur mu Yani."),
    "kirk-bir-masallah": ("Kırk bir kere maşallah!", "Çocuğa kırk bir kere maşallah dedi.",
                          "Maşallah, kırk bir kere maşallah, ne güzel büyümüş."),
    "dokuz-ayin": ("Dokuz ayın çarşambası bir araya gelmiş.", "Bugün dokuz ayın çarşambası bir araya geldi.",
                   "Ne şanssızlık, dokuz ayın çarşambası bir araya gelmiş sanki."),
    "yedi-kocali": ("Yedi kocalı Hürmüz gibi konuşma!", "Onun hali yedi kocalı Hürmüz'e döndü.",
                    "Mahallede ona yedi kocalı Hürmüz diyorlar."),
    "kirk-yamali": ("Elinde kırk yamalı bir bohça vardı.", "Ceketi kırk yerinden yamalıydı.",
                    "Bu kırk yamalı bohça gibi plan işe yaramaz."),
    "kirkikindi": ("Bu kırk ikindi yağmuru bir türlü dinmiyor.", "Kırk ikindi yağmurları başladı.",
                   "Mayısta kırk ikindi yağmuru yağar dedi annem."),
    "on-ikiden": ("Tam on ikiden vurdu.", "Söylediği söz on ikiden vurdu.", "Hakem sonunda on ikiden vurdu."),
    "yetmis-iki-bucuk": ("Burada yetmiş iki buçuk millet var.", "Yetmiş iki buçuk millet aynı otobüse binmiş.",
                         "Çarşıda yetmiş iki buçuk milletten insan gördüm."),
    "bin-isit": ("Bin işit, bir söyle.", "Dedem hep bin işit bir söyle derdi.",
                 "Ne demişler, bin işit bir söyle."),
    "bin-isitmek-gormek": ("Bin işitmek, bir görmek gibi olmaz.", "Bin işitmek bir görmek gibi olmaz, git kendin bak."),
    "yuz-liran": ("Yüz liran olmasın, yüz arkadaşın olsun.", "Annem hep yüz liran olmasın yüz arkadaşın olsun derdi.",
                  "Ne demişler: yüz liran olacağına yüz arkadaşın olsun."),
    "yedigin-ictigin": ("Yediğin içtiğin senin olsun, gördüğünü söyleme.",
                        "Ona yediğin içtiğin senin olsun dedim, sustu."),
    "kirk-takla": ("Patronun karşısında kırk takla atıyor.", "Bir iş için kırk takla atmaya gerek yok.",
                   "Kırk takla atsan da seni beğenmez."),
    "dokuz-babali": ("Ona dokuz babalı derler.", "Dokuz babalı bir adamla uğraşmaya değmez."),
    "yedi-tepeli": ("Yedi tepeli şehre ilk defa geldim.", "Yedi tepeli İstanbul kar altındaydı."),
    "kirk-kilikli": ("O kırk kılıklı adama güvenilmez.", "Kırk kılıklı biri gibi her gün başka türlü konuşuyor."),
    "bin-kere-sukur": ("Bin kere şükür, kimseye muhtaç değiliz.", "Bin kere şükür ki zamanında yetiştik."),
    "binbir-emek": ("Bu evi bin bir emekle yaptık.", "Bin bir emekle büyüttüğü çocuk gitti."),
    "bin-parca": ("Kalbi bin parça oldu.", "Vazo yere düşüp bin parça oldu."),
    "yuz-akiyla": ("Bu işten yüz akıyla çıktık.", "İnşallah yüz akıyla çıkarız."),
    "yuz-kizartici": ("Bu yüz kızartıcı bir suçtur.", "Yüz kızartıcı bir iş yapmadım ki."),
    "ikinci-bahar": ("Emekli olunca ikinci baharını yaşamaya başladı.", "Annem ikinci baharını yaşıyor gibi."),
    "birinci-elden": ("Bu haberi birinci elden duydum.", "Birinci elden bilgi almak lazım."),
    "on-numara": ("Bu adam on numara beş yıldız.", "Yemekler on numaraydı.", "Senin fikrin on numara."),
    "yuz-numara": ("Yüz numara nerede acaba?", "Lokantanın yüz numarası arka tarafta."),
    "kirk-yil-dusunse": ("Kırk yıl düşünse aklına gelmez.", "Bunu kırk yıl düşünsem aklıma gelmezdi."),
    "besi-bir-yerde": ("Gelinin boynuna beşi bir yerde taktılar.", "Düğünde beşi bir yerde altın verdiler."),
    "uc-kagit": ("Bizi üç kağıda getirdi.", "Bu adam üç kağıtçının biri.", "Üç kağıda gelmem ben."),
}
SOZ_TASIYICI = ("{s}", "{s} Dedem böyle derdi.", '"{s}" dedi, güldü.', "Ne demişler, {s}")


def ngramlar(t: str, n: int = 3) -> set[tuple[str, ...]]:
    w = duzlestir(t).split()
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def olcum_ngramlari() -> set[tuple[str, ...]]:
    g = set()
    for f in ("gercek.jsonl", "gercek2.jsonl", "gercek3.jsonl"):
        for s in (KOK / "evaluation" / f).read_text(encoding="utf-8").splitlines():
            g |= ngramlar(json.loads(s)["girdi"])
    return g


def e5() -> tuple[list[dict], list[str]]:
    yasak = olcum_ngramlari()
    out, atilan = [], []
    for k, cumleler in SOZ_CUMLELERI.items():
        for j, c in enumerate(cumleler):
            if ngramlar(c) & yasak:
                atilan.append(c)
                continue
            tasiyicilar = SOZ_TASIYICI if j == 0 else ("{s}",)
            for t in tasiyicilar:
                out += iki_bicim(t.replace("{s}", c), {}, "negatif_kalip", f"v3e-e5-{k}")
    return out, atilan


# ---------------------------------------------------------------- toplama
def bolum(sablon: str) -> str:
    return "validation" if int(hashlib.md5(sablon.encode()).hexdigest(), 16) % 100 < 7 else "train"


def uret(seed: int = 3322, cv_yolu: Path = CV_YOLU) -> tuple[dict, dict]:
    dis = haric_yukle(HARIC_YOLU)
    e5_satir, e5_atilan = e5()
    kaynaklar = {"E1": e1(cv_yolu), "E2": e2(seed), "E3": e3(seed), "E4": e4(seed), "E5": e5_satir}
    sonuc = {"train": [], "validation": []}
    sayim = Counter()
    for olgu, satirlar in kaynaklar.items():
        gorulen = set()
        for r in satirlar:
            if ozet(r["girdi"]) in dis or ozet(r["hedef"]) in dis:
                sayim["haric"] += 1
                continue
            if (r["girdi"], r["hedef"]) in gorulen:
                sayim["yinelenen"] += 1
                continue
            gorulen.add((r["girdi"], r["hedef"]))
            r["olgu"] = olgu
            sonuc[bolum(r["sablon"])].append(r)
    # Bir girdiye iki hedef verilmesin (ör. aynı aralık iki şablonda).
    for b, satirlar in sonuc.items():
        hedefler = {}
        for r in satirlar:
            hedefler.setdefault(r["girdi"], set()).add(r["hedef"])
        celisik = {g for g, hs in hedefler.items() if len(hs) > 1}
        sayim[f"celiskili_{b}"] = len(celisik)
        sonuc[b] = [r for r in satirlar if r["girdi"] not in celisik]
        random.Random(f"{seed}-{b}").shuffle(sonuc[b])
    rapor = {"seed": seed, "elemeler": dict(sayim), "e5_olcumle_ortusen_atilan": e5_atilan, "bolumler": {}}
    for b, satirlar in sonuc.items():
        rapor["bolumler"][b] = {
            "satir": len(satirlar),
            "olgu": dict(sorted(Counter(r["olgu"] for r in satirlar).items())),
            "kategori": dict(sorted(Counter(r["kategori"] for r in satirlar).items())),
            "negatif_payi": round(sum(r["girdi"] == r["hedef"] for r in satirlar) / max(1, len(satirlar)), 3),
            "sablon": len({r["sablon"] for r in satirlar}),
        }
    return sonuc, rapor


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=3322)
    ap.add_argument("--out", type=Path, default=KOK / "data" / "v3")
    ap.add_argument("--cv", type=Path, default=CV_YOLU)
    a = ap.parse_args(argv)
    sonuc, rapor = uret(a.seed, a.cv)
    a.out.mkdir(parents=True, exist_ok=True)
    for b, satirlar in sonuc.items():
        (a.out / f"e-{b}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in satirlar),
                                            encoding="utf-8")
    (a.out / "e-rapor.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
