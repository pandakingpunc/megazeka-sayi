"""Megazeka-Sayı v2 · B kaynağı: tuzaklar (değişmemesi gereken cümleler) + karşıt pozitifler.

Kullanım:
    python training/v2_tuzak.py --out data/v2 --seed 2202 --train 10000 --validation 300 --test 400

Çıktı: b-train.jsonl, b-validation.jsonl, b-test.jsonl (satır sözleşmesi SPEC §5; `sablon` kimliği `v2b-...`).

Tasarım
- 10 olgu (SPEC-v2 §B) için elle yazılmış, yer tutuculu şablonlar (`OLGULAR`). Negatiflerde girdi == hedef.
- Karşıt pozitifler (%17): aynı yüzey sözcüğün sayı olduğu cümleler; hedef yalnız `varliklar.kur_*` ile kurulur,
  girdi `Varlik.sozlu`dan gelir.
- Her negatif cümle `denetle()` kural denetiminden geçer (SPEC §1.1 küçük sayı politikasına göre cümlede çevrilmesi
  gereken bir sayı bulunmamalı). İhlal eden satırlar atılır.
- Test dosyası, eğitim/doğrulamada hiç kullanılmayan şablonlarla üretilir (her olgudan ≥ %15).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "src"))

from megazeka_sayi import sayilar as S  # noqa: E402
from megazeka_sayi import varliklar as V  # noqa: E402
from megazeka_sayi.sablonlar import ACILISLAR, FILLERS as _F0, KAPANISLAR  # noqa: E402
from megazeka_sayi.turkce import EKLER, ek_uret, ilk_harfi_buyut, inflect, lower_tr  # noqa: E402

BAYT_SINIRI = 180
KARSIT_ORANI = 0.17
KISA_ORANI = 0.05            # kısa şablon havuzundan örnekleme payı (sarmalayıcı sonrası 2-5 sözcük payı ölçülür)
VOKATIF_OLGU = {"bin", "ikinciel", "yuz"}
VOKATIF_ORANI = 0.5
KISA_OLGU = {"bin": 0.54, "ikinciel": 0.58, "yuz": 0.48}
KISA_DIGER = {"deyim": 0.35}
SARMA_ACILIS = 0.40
SARMA_KAPANIS = 0.20
BUYUK_HARF_ORANI = 0.40
TEST_ORANI = 0.18


# ======================================================================================
# Dolgu listeleri (yer tutucular)
# ======================================================================================
def _ekli(liste, ek):
    return [x + "'" + ek_uret(x, ek) for x in liste]


_SEHIR = ["Ankara", "İstanbul", "İzmir", "Bursa", "Antalya", "Konya", "Adana", "Trabzon", "Samsun", "Eskişehir",
          "Gaziantep", "Kayseri", "Mersin", "Diyarbakır", "Erzurum", "Van", "Edirne", "Bolu", "Rize", "Muğla",
          "Denizli", "Sivas", "Malatya", "Tokat", "Ordu"]
_TAKIM = ["Galatasaray", "Fenerbahçe", "Trabzonspor", "Başakşehir", "Konyaspor", "Sivasspor", "Bursaspor",
          "Kayserispor", "Samsunspor", "Rizespor"]

F: dict[str, list[str]] = {}
for _ad in ("isim", "urun", "esya", "kisi", "nesne", "tasit_dat", "binek_dat", "yiyecek", "yiyecek_acc",
            "yiyecek_gen", "tabakli", "dilimli", "zaman_gecmis", "zaman_gelecek", "su_yeri", "alt_gen", "agac_gen",
            "kucuk_nesne", "kucuk_acc", "yer_loc", "sey_acc", "iyelikli", "ozellik", "mevsim_loc", "hayvan_acc",
            "ikinci_el_esya", "mekan", "malzeme", "beklenen", "olay", "kesir_nom", "kesir_acc", "kesir_bare",
            "kesir_dat", "ay_ek", "ay_abl", "ay_dat", "ay_gen", "ay_bare", "urun_gen"):
    F[_ad] = list(_F0[_ad])
F["sehir"] = list(_SEHIR)
F["takim"] = list(_TAKIM)
for _e, _ad in (("yonelme", "dat"), ("belirtme", "acc"), ("ilgi", "gen"), ("ayrilma", "abl"), ("vasita", "ins"),
                ("bulunma", "loc")):
    F["isim_" + _ad] = _ekli(F["isim"], _e)
    F["sehir_" + _ad] = _ekli(_SEHIR, _e)
F["ikinci_el_cogul"] = ["telefonlar", "arabalar", "bisikletler", "kameralar", "bilgisayarlar", "koltuklar",
                        "motosikletler", "buzdolapları", "tabletler", "kitaplar", "montlar", "halılar",
                        "fotoğraf makineleri", "oyun konsolları"]
F["ikinci_el_acc"] = ["arabayı", "telefonu", "bisikleti", "kamerayı", "bilgisayarı", "koltuğu", "motosikleti",
                      "buzdolabını", "tableti", "kitabı", "montu", "halıyı", "fotoğraf makinesini", "oyun konsolunu"]
F["tasit_dat"] += ["arabaya", "kamyona", "traktöre", "kayığa", "motora", "sandala"]
F["akraba"] = ["annem", "babam", "dedem", "ablam", "ağabeyim", "kardeşim", "teyzem", "amcam", "komşum", "kuzenim"]
F["meslek"] = ["öğretmen", "doktor", "usta", "şoför", "garson", "kasiyer", "mühendis", "avukat", "ressam", "berber"]
F["hayvan"] = ["köpek", "kedi", "at", "kuzu", "tavuk", "kuş", "eşek", "inek"]
F["yemek_yeri"] = ["lokantada", "kafede", "pastanede", "kantinde", "evde", "bahçede", "balkonda", "pikniğe giderken"]


# ======================================================================================
# Kural denetimi: negatif cümlede SPEC'e göre çevrilmesi gereken sayı olmamalı
# ======================================================================================
_KARD = {"sıfır": 0, "bir": 1, "iki": 2, "üç": 3, "dört": 4, "beş": 5, "altı": 6, "yedi": 7, "sekiz": 8,
         "dokuz": 9, "on": 10, "yirmi": 20, "otuz": 30, "kırk": 40, "elli": 50, "altmış": 60, "yetmiş": 70,
         "seksen": 80, "doksan": 90, "yüz": 100, "bin": 1000, "milyon": 10 ** 6, "milyar": 10 ** 9,
         "trilyon": 10 ** 12}


def _ek_bicimleri(kok: str, ek: str) -> set[str]:
    bicim = {kok + ek_uret(kok, ek)}
    bicim.add(inflect(kok, ek)[0])
    return bicim


KARD_FORM: dict[str, tuple[int, str]] = {}   # çekimli sayı sözcüğü -> (değer, ek)
SIRA_TEMEL: set[str] = set(S.SIRA_EKLI.values())
SIRA_FORM: set[str] = set()                   # çekimli sıra sayısı (ikincisi, birincilik ...)
for _k, _v in _KARD.items():
    for _e in EKLER:
        for _b in _ek_bicimleri(_k, _e):
            KARD_FORM.setdefault(_b, (_v, _e))
for _o in SIRA_TEMEL:
    for _e in EKLER:
        SIRA_FORM.update(_ek_bicimleri(_o, _e))
SIRA_FORM -= SIRA_TEMEL
for _b in list(KARD_FORM):
    if _b in _KARD:
        del KARD_FORM[_b]

BIRIM_ONEKLERI = ("kilo", "gram", "metre", "santim", "milim", "litre", "mililitre", "gigabayt", "megabayt",
                  "terabayt", "kilovat", "vat", "volt", "derece", "santigrat", "lira", "kuruş", "dolar", "avro",
                  "euro", "sterlin", "ton", "inç", "kalori", "hektar", "dönüm", "beygir", "piksel", "karat")
BIRIM_DISI = ("vatan", "vatandaş", "tonla", "tonlarca", "metreler", "kiloyu")  # kesin sayıyla birlikte gelmeyenler
AYLAR = ("ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım",
         "aralık")
SIRA_YUKLEM = {"oldu", "oldum", "olduk", "olmuş", "olunca", "olarak", "olmak", "olacak", "olmaktan", "olduğunu",
               "olmadı", "geldi", "geldim", "geldik", "gelen", "gelmiş", "gelince", "gelmek", "çıktı", "çıktım",
               "bitirdi", "bitirdim", "bitirdik", "tamamladı", "seçildi", "belirlendi", "kaldı", "kaldım", "ve",
               "ama", "mi", "mı", "mu", "mü", "de", "da", "ise", "bitti", "geldiğini", "gelmesi", "seçilmiş",
               "gelirse", "çıkmış", "olsun", "olsa", "olmayı", "olmasından", "gelmeyi", "gelmesini"}

SIRA_YUKLEM_ONEK = ("old", "olm", "olu", "olac", "olsa", "olsu", "gel", "çıkt", "çıkm", "bitir", "bitt", "seçil",
                    "kald")
_BIN_ONCE = {"hadi", "haydi", "sen", "siz", "ben", "biz", "de", "da", "atla", "önce", "sakın", "hemen", "çabuk",
             "artık", "o", "hepiniz", "hepimiz", "lütfen", "ve", "ama"} | {x.lower() for x in F["tasit_dat"]} | \
            {x.lower() for x in F["binek_dat"]}
_BIN_SONRA = {"de", "da", "hemen", "şu", "bu", "o", "ama", "bakalım", "artık", "lütfen", "çabuk", "hadi", "ve",
              "diye", "ki", "mi", "mı", "sonra", "yoksa", "şimdi", "şuraya", "yanıma", "içeri", "arkama", "hızlı",
              "öne", "arkaya", "gidelim", "ben", "sen"}
_YUZ_ONCE = {"hadi", "haydi", "sen", "siz", "ben", "biz", "de", "da", "biraz", "sakın", "hemen", "artık", "çabuk"}
_YUZ_SONRA = {"biraz", "bakalım", "de", "da", "hemen", "artık", "lütfen", "çabuk", "mi", "mı", "sen", "siz", "hadi"}
_KIRK_ONCE = {x.lower() for x in F["hayvan_acc"]} | {"saçını", "saçımı", "yünleri", "yünü", "tüyleri", "şunları",
                                                     "bunları"}
_KIRK_SONRA = {"şu", "bu", "hemen", "artık", "lütfen", "çabuk", "bakalım"}
SERBEST_CIPLAK = {"bin": (_BIN_ONCE, _BIN_SONRA), "yüz": (_YUZ_ONCE, _YUZ_SONRA), "kırk": (_KIRK_ONCE, _KIRK_SONRA)}

ONAYLI: list[tuple[str, ...]] = []   # onaylı kalıplar (deyim, özel ad ...); sondaki sözcük ön ek olarak eşleşir


def belirteclestir(metin: str) -> list[str]:
    t = lower_tr(metin)
    t = re.sub(r"['’]", "", t)
    return re.findall(r"[^\W\d_]+|§", t)


def _birim_mi(s: str) -> bool:
    return bool(s) and s.startswith(BIRIM_ONEKLERI) and not s.startswith(BIRIM_DISI)


def _sayi_sozcugu(s: str) -> bool:
    return s in _KARD or s in KARD_FORM


def denetle(metin: str) -> list[str]:
    """SPEC §1.1'e göre cümlede rakama çevrilmesi gereken sayı varsa ihlal listesi döndürür (boş = temiz).

    Kurallar (yalnız tam sayı sözcüğü ya da çekimi denetlenir; `onbaşı`, `ikiz`, `altında` gibi türevler sayı
    değildir):
    - ardışık sayı sözcükleri (aralık / bileşik sayı), `saat`/`yüzde`/`eksi` sonrası sayı, sayıdan sonra birim,
      para, ay adı, `buçuk` -> ihlal;
    - çıplak 10 ve üstü sayı sözcüğü ihlal (yalnız `bin`/`yüz`/`kırk` eş yazımlı kullanım bağlamında serbest);
    - sıra sayısı + ad ihlal (yüklem, `ikinci el` ve çekimli biçimler serbest);
    - `kadar` önündeki çekimli sayı (`ona kadar`) ihlal; kesirler (`üçte bir`) serbest.
    Onaylı kalıplar (`ONAYLI`) maskelenir.
    """
    tk = belirteclestir(metin)
    n = len(tk)
    maske = [False] * n
    for et in ONAYLI:
        uz = len(et)
        for i in range(n - uz + 1):
            if tk[i:i + uz - 1] == list(et[:-1]) and tk[i + uz - 1].startswith(et[-1]):
                for j in range(i, i + uz):
                    maske[j] = True
    ihlal: list[str] = []
    for i, t in enumerate(tk):
        if maske[i]:
            continue
        onc = tk[i - 1] if i else ""
        son = tk[i + 1] if i + 1 < n else ""
        if t in SIRA_TEMEL:
            if not (son == "" or son in SIRA_YUKLEM or son.startswith(SIRA_YUKLEM_ONEK)
                    or (t == "ikinci" and son.startswith("el"))):
                ihlal.append(f"sıra sayısı + ad: {t} {son}")
            continue
        if t in SIRA_FORM:
            continue
        if t in _KARD:
            v = _KARD[t]
            if _sayi_sozcugu(son):
                ihlal.append(f"ardışık sayı: {t} {son}")
            elif onc in ("saat", "yüzde", "eksi"):
                ihlal.append(f"bağlamlı sayı: {onc} {t}")
            elif _birim_mi(son) or son.startswith(AYLAR) or son.startswith("buçuk"):
                ihlal.append(f"birimli sayı: {t} {son}")
            elif v >= 10:
                izin = SERBEST_CIPLAK.get(t)
                if not (izin and (onc in izin[0] or son in izin[1])):
                    ihlal.append(f"çıplak büyük sayı: {onc} {t} {son}")
            continue
        if t in KARD_FORM:
            v, ek = KARD_FORM[t]
            if onc in ("saat", "yüzde", "eksi"):
                ihlal.append(f"bağlamlı sayı: {onc} {t}")
            elif son == "kadar" or _birim_mi(son) or son.startswith(AYLAR):
                ihlal.append(f"çekimli sayı + bağlam: {t} {son}")
            elif _sayi_sozcugu(son) and ek != "bulunma":
                ihlal.append(f"ardışık sayı: {t} {son}")
    return ihlal


# ======================================================================================
# Şablonlar
# ======================================================================================
# Satır biçimi: `[* ][etiket | ]şablon`. `*` = sarmalayıcısız kısa cümle. `etiket` = onaylı kalıp / deyim / ad
# (denetimde maskelenir, raporda "ayrı deyim" sayılır). Yer tutucular `{ad}`; karşıt pozitiflerde `{slot[:ek]}`.
BIN = """
* Hadi bin
* Haydi bin artık
* Sen de bin
* Atla bin
* Bin şu arabaya
* Bin hemen
* Binsene
* Binin lütfen
* Binelim mi
* Sakın binme
* Ben de bindim
* Hepimiz bindik
* Önce sen bin
* Bin de görelim
* Kim binmek ister?
* Çocuklar biniyor
* Neden binmedin?
* Bindi mi
* Siz binmediniz mi
* {tasit_dat} bin
* {tasit_dat} bin hemen
* {tasit_dat} bin de gel
* {tasit_dat} bin ama çabuk ol
* {tasit_dat} binelim
* {tasit_dat} bindik
* {tasit_dat} bindim
* {tasit_dat} binecek miyiz
* {tasit_dat} binmem
* {tasit_dat} binerek gidelim
* {tasit_dat} bineceğiz
* {isim} {tasit_dat} bindi
* {isim}, hadi bin
* {isim} hemen bindi
* {isim} biniyor mu
* Ata bin
* {binek_dat} bin bakalım
* {binek_dat} binme
{zaman_gecmis} {tasit_dat} bindim ve doğru eve geldim
{isim} acele edip {tasit_dat} bindi
Yağmur başlayınca hepimiz {tasit_dat} bindik
Biletini aldıktan sonra {tasit_dat} bin
Çocuklar sırayla {tasit_dat} biniyor
{tasit_dat} bineceğimiz için erkenden kalktık
Her sabah {tasit_dat} binip işe gidiyorum
{isim} {tasit_dat} binmeyi pek sevmez
{tasit_dat} binmeden önce biletini göster
{yer_loc} bekleyip {tasit_dat} bindik
Yolcular {tasit_dat} binerken itişip kakışmasın
Kapı açılınca herkes {tasit_dat} binmeye çalıştı
Yaşlı amcayı {tasit_dat} bindirdik
Küçük kız annesiyle {tasit_dat} biniyordu
{isim_ins} birlikte {tasit_dat} binerek {sehir} şehrine gittik
{isim} yarın {tasit_dat} binip bize gelecek
Ben {tasit_dat} binerim, sen yürüyerek gel
Sen {tasit_dat} binersin, ben arkadan gelirim
Biz {tasit_dat} biner, siz arabayla gelirsiniz
Yolcuların çoğu {tasit_dat} binmişti bile
{isim} yorgun olduğu için {tasit_dat} binmek istedi
Şoför kapıyı açtı, biz de {tasit_dat} bindik
Biz {tasit_dat} biniyoruz, siz nerede bekliyorsunuz
Sen de {tasit_dat} biniyorsun, değil mi
{zaman_gecmis} {isim_ins} {tasit_dat} bindik
Çocuklar her gün {tasit_dat} biniyorlar
{isim} {tasit_dat} bindiğinde herkes ayağa kalktı
{tasit_dat} bindiğimiz gün hava çok güzeldi
{tasit_dat} binen yolcular biletlerini göstersin
Biraz erken çıksaydın {tasit_dat} binebilirdin
{isim} yetişemeyince {tasit_dat} binemedi
Ben o gün {tasit_dat} binemedim, çok üzüldüm
{isim} {tasit_dat} binmişti, biz de arkasından bindik
Yolcular {tasit_dat} binmiyor, çünkü bekleme salonu sıcak
Çocuk {tasit_dat} binmedi, annesine sarıldı
Seneye {tasit_dat} binmeyeceğim, yürümeyi tercih ederim
{isim} {tasit_dat} binmesin, sağlığı elvermiyor
{tasit_dat} binsek mi yoksa yürüsek mi
{tasit_dat} binseydi daha erken gelirdi
Yorgunsan {tasit_dat} binebilirsin
Burada {tasit_dat} binilir, öbür kapıdan inilir
Binişte kalabalık olur, erken gel
Hostes yolcuları {tasit_dat} bindirdi
Rehber turistleri {tasit_dat} bindirmek için kapıda bekledi
{isim} {binek_dat} binmeyi küçük yaşta öğrendi
Çocuklar sırayla {binek_dat} bindi
Ben {binek_dat} binince korktum
{zaman_gecmis} {binek_dat} bindik, çok eğlendik
Hadi {binek_dat} bin de gösteriş yap
{isim} {binek_dat} binip köye gitti
{binek_dat} binerken dikkatli ol
Turistler {binek_dat} binmek için sıraya girdi
Küçük çocuk ilk kez {binek_dat} bindi
Yarın sabah {binek_dat} bineceğiz
* Bin hadi gidiyoruz
* Bin hadi
* Bin artık geç kalıyoruz
* Bin şuraya
* Bin yanıma
* Motora bin arkama
* Arabaya bin yanıma
* Bin içeri
* Bin de gidelim
* Bin bakalım
* Bin şimdi
* Bin yoksa kalırsın
* Hemen bin
* Çabuk bin
* Lütfen bin
* Sen bin ben iterim
* Önce ben bineyim
* Ben bineyim
* Sen binme
* Kim bindi
* Kim biner
* Biner misin
* Binmez miyiz
* Binmedim
* Bindiniz mi
* Binecek misin
* Binelim hadi
* Binsek mi
* Binmeyelim
* Binmeyin
* Binmesin
* Binsin
* Binsinler
* Binme sakın
* Bindirelim onu
* Binmek lazım
* Binmem lazım
* Binmek zorundayız
* Binmek istemiyorum
* Binmek ister misin
* Binerim ama
* Binmeden bekle
* Bindikten sonra ara
* {tasit_dat} bin yoksa kalırsın
* {tasit_dat} binin çocuklar
* {tasit_dat} binsene
* {tasit_dat} binmeyelim
* {tasit_dat} biner misin
* {tasit_dat} bindi mi
* {tasit_dat} bindiler
* {tasit_dat} binmedi
* {isim} binsin
* Sen {tasit_dat} bin
* Hadi {tasit_dat} bin
* Hemen {tasit_dat} bin
* {tasit_dat} bin şimdi
* {tasit_dat} bin lütfen
* {tasit_dat} bin çabuk
* Kim {tasit_dat} bindi
* {isim} nerede bindi
* {binek_dat} binmem
* {binek_dat} binelim
* {isim_ins} {tasit_dat} bindik
"""

IKINCIEL = """
* İkinci el telefonlar
* İkinci el {ikinci_el_cogul}
* {ikinci_el_esya} ikinci el
* Bu {ikinci_el_esya} ikinci el
* İkinci elden aldım
* İkinci elden {ikinci_el_esya}
* İkinci ele düştü
* Hepsi ikinci el
* İkinci el mi
* İkinci el satıyorum
* İkinci el pazarı
* Sadece ikinci el
* Ucuz, ikinci el
* Bu araba ikinci el
* {isim} ikinci el aldı
* Ben ikinci elden aldım
* Yeni değil ikinci el
* İkinci el {ikinci_el_esya} arıyorum
* İkinci el kitap satılır
* İkinci elden alalım
* {ikinci_el_esya} ikinci elden
* {isim} ikinci ele düşen {ikinci_el_esya}
* Bu ikinci el mi
{isim} geçen yıl ikinci el bir {ikinci_el_esya} aldı
Bütçemiz kısıtlı olduğu için ikinci el {ikinci_el_esya} bakıyoruz
Bu {ikinci_el_esya} ikinci elden alınmış ama sapasağlam
İkinci el {ikinci_el_esya} fiyatları son aylarda çok arttı
{sehir} çarşısında ikinci el {ikinci_el_esya} satan bir dükkân var
Ben hep ikinci elden alışveriş yapıyorum
{isim} eşyaların çoğunu ikinci elden topladı
Kardeşim ikinci el bir {ikinci_el_esya} alıp tamir etti
İkinci el piyasasında {ikinci_el_esya} bulmak zor
Eski {ikinci_el_esya} ikinci ele düşünce değeri yarıya indi
Mahallede ikinci el eşya alım satımı yapan bir amca var
İkinci el {ikinci_el_esya} alırken faturasını sormayı unutma
{isim} ikinci el {ikinci_el_esya} satmak için ilan verdi
Kitabı ikinci elden bulduk, kapağı biraz yıpranmış
İkinci el kıyafet pazarı her hafta sonu kurulur
Bu mağaza hem yeni hem ikinci el {ikinci_el_esya} satıyor
{isim_ins} ikinci el {ikinci_el_esya} bakmaya gittik
Kullanılmış olsa da ikinci el bir {ikinci_el_esya} işimizi görür
Dükkânın tabelasında ikinci el yazıyordu
Annem ikinci el eşya alıp satan bir mağazada çalışıyor
İkinci el {ikinci_el_cogul} her geçen gün daha çok ilgi görüyor
Öğrenciler ikinci el kitaplardan yararlanıyor
Sahaf ikinci elden aldığı kitapları rafa dizdi
Bu {ikinci_el_esya} ikinci el olduğu için garanti kapsamında değil
Müşteri ikinci el {ikinci_el_esya} için pazarlık yaptı
İlandaki {ikinci_el_esya} ikinci el ama çok iyi durumda
Ev eşyalarının çoğu ikinci elden
{isim} yeni bir {ikinci_el_esya} yerine ikinci el bir tane aldı
Önceki sahibi satınca bu {ikinci_el_esya} ikinci ele düşmüş
* İkinci el olur
* İkinci el olsun
* İkinci el değil
* Hep ikinci el
* Hepsi ikinci elden
* İkinci el alma
* İkinci el almayalım
* İkinci el aldık
* İkinci el bakıyorum
* İkinci el arıyoruz
* İkinci el satarız
* İkinci elden satıyoruz
* İkinci el fiyatı
* İkinci el ilanı
* İkinci el çarşısı
* İkinci el dükkânı
* Yeni mi ikinci el mi
* İkinci el {ikinci_el_esya} fiyatları
* {ikinci_el_cogul} ikinci el
* Bu {ikinci_el_esya} ikinci elden
* {isim} ikinci el sattı
* {isim} ikinci elden aldı
* İkinci ele geçti
* {ikinci_el_esya} ikinci ele düştü
* İkinci el olmaz
* İkinci el kullanır mısın
* İkinci el sever misin
* Bunu ikinci elden buldum
* Onu ikinci elden aldım
* {ikinci_el_acc} ikinci elden aldık
* {ikinci_el_acc} ikinci elden aldım
* {ikinci_el_acc} ikinci elden satın aldı
* İkinci elden {ikinci_el_acc} aldık
* Bu {ikinci_el_esya} ikinci el mi
* {ikinci_el_esya} ikinci el mi
* {isim} ikinci el mi aldı
* Arabayı ikinci elden aldık
* Telefonu ikinci elden aldım
* Motoru ikinci elden aldık
"""

YUZ = """
* Bu yüzden gelmedi
* O yüzden aradım
* Bu yüzden mi
* Senin yüzünden
* {isim_gen} yüzünden oldu
* Yüzüme bakma
* Yüzünü yıka
* yüz yüze | Yüz yüze konuşalım
* Hadi yüz biraz
* Denizde yüzelim
* {su_yeri} yüzdük
* {isim} {su_yeri} yüzüyor
* Yüzmeye gidelim
* Ben yüzemem
* Yüzleşmek zorundayız
* Yüzsüz biri
* Güler yüzlü bir garson
* {isim} yüzünü gizledi
* Yüzü kızardı
* Yüzmeyi biliyor musun
* Yüzücüler geldi
* Havuzda yüzdüm
* Sen de yüz bakalım
* Çocuklar yüzmeye gitti
* Biraz da sen yüz
* Yüzünde bir gülümseme var
* {isim} yüzüne baktı
* Yüzdük yüzdük yorulduk
* Yüzer misin benimle
* Yüzümü yıkadım
* O yüzden gitmedim
Yol kapalıydı, bu yüzden toplantıya geç kaldık
Yağmur yağıyordu, o yüzden pikniği iptal ettik
Hazırlanmadığı için sınavdan düşük aldı, bu yüzden üzgün
{isim_gen} yüzünden hepimiz yağmurda kaldık
Senin yüzünden son otobüsü kaçırdık
Çocuk utancından yüzünü ellerinin arasına gizledi
Sabah yüzümü yıkayıp kahvaltı hazırladım
Aynanın karşısında yüzüme krem sürdüm
Yüzüne bakınca bir sorun olduğunu anladım
{isim} bana gerçekleri yüzüme karşı söyledi
Ağladığı için yüzü şişmişti
Annemin yüzü güldü
{isim} komşusunun yüzüne bile bakmadı
Yaz tatilinde her gün {su_yeri} yüzdük
{zaman_gecmis} {su_yeri} uzun uzun yüzdük
{isim} her sabah {su_yeri} yüzer
Yarın sabah {su_yeri} yüzmeye gidiyoruz
Çocuklar yüzmeyi dedelerinden öğrendi
Yüzme bilmeyenler kıyıdan uzaklaşmasın
Yüzmek en sevdiğim spor
yüz yüze | {isim} yıllar sonra eski dostuyla yüz yüze geldi
Yaptığı hatayla sonunda yüzleşti
{isim} yüzsüzlüğüyle herkesi şaşırttı
Güler yüzlü satıcı bize çay ikram etti
Yüzünü asan müşteriye bile tatlı dille cevap verdi
Bu yüzden kimseye haber vermedik
Dalgalara rağmen {isim_ins} birlikte yüzdük
Kız kardeşim yüzmeyi öğrenince çok sevindi
{isim} yarışmada yüzdü, ben kıyıdan izledim
{isim} yüzünü buruşturdu
Soğuk su yüzüme çarpınca uyandım
yüz yüze | Yüz yüze gelmekten kaçınıyorlar
Hadi yüz de {su_yeri} serinleyelim
* Bu yüzden geç kaldım
* Bu yüzden gelmedim
* Bu yüzden değil
* O yüzden gitmedim
* Onun yüzünden geç kaldık
* Benim yüzümden oldu
* Trafik yüzünden geç kaldım
* Yağmur yüzünden gelmedi
* Hava yüzünden iptal oldu
* Yüzüne bak
* Yüzüme bak
* Yüzünü göster
* Yüzü kırmızı
* Yüzü güldü
* Yüzü düştü
* Yüzünü ekşitti
* yüz yüze | Yüz yüze geldik
* yüz yüze | Yüz yüze görüştük
* Yüzmeyi seviyorum
* Yüzmek ister misin
* Yüzdün mü
* Yüzüyorlar
* {su_yeri} yüzelim
* Yüz hadi
* Sen de yüz
* {su_yeri} yüzdüm
* {isim} yüzdü
* Çocuklar yüzüyor
* Yüzme havuzu
* Yüzme dersi
* Yüzme bilmem
* Yüzleşelim
* Yüzleşti mi
* Yüzsüz herif
* Güler yüzlü biri
* Yüzünde ne var
* {isim_gen} yüzünden geç kaldık
* Bu yüzden {isim} gelmedi
* {isim} yüzmeye gitti
"""

SIRA = """
* Üçüncü oldu
* Birinci geldi
* {isim} ikinci geldi
* {isim} üçüncü oldu
* Ben dördüncü oldum
* Birincisi {isim}
* İkincisi daha güzel
* Üçüncüsü daha iyi
* Sonuncu geldi
* Sonuncusu bozuk
* Birincilik {isim_dat} gitti
* Kim birinci oldu?
* {takim} üçüncü bitirdi
* Beşinci geldim
* Altıncı oldu
* Yedinci oldum
* Onuncu oldu
* {takim} dördüncü oldu
* Ben birinci geldim
* Birincisini seç
* İkincisi {isim} oldu
* Sonuncu olmak istemem
* Birinci oldun
* {takim} birinci olacak
{isim} koşuda üçüncü oldu ve madalya aldı
Yarışta birinci gelen kişi ödülü alacak
Sınavda sınıf ikincisi oldum
Okul birinciliğini {isim} kazandı
Final maçında {takim} ikinci oldu
Kardeşlerin ikincisi doktor oldu
Bu çiçeklerin üçüncüsünü sana verdim
Yarışmada dördüncü gelince çok üzüldü
Ödül töreninde adı birinci olarak okundu
Üçüncü oldum ama gurur duyuyorum
Dün akşam sınıfta birinci seçildi
{isim} şampiyonada ikinci olmuş
Çocuk satranç turnuvasında üçüncü olunca sevindik
Sonuncu gelmek bile {isim} için büyük başarıydı
Sonuncu olmaktan korkma
Kapıdan giren ilk kişi {isim}, sonuncusu ben oldum
Elimdeki kitapların birincisini okudum, ikincisini daha açmadım
Birinciliği kaptırmak istemedi
Birincilik ödülü {isim_dat} verildi
Maraton bitince {isim} altıncı olduğunu öğrendi
{takim} lig tablosunda beşinci olarak sezonu kapattı
Kayıkçılar yarışında {isim} yedinci geldi
Üçüncüsünü de alırsan bu iş tamam
Küçük kızımız resim yarışmasında birinci oldu
Birinci geldiğini duyunca sevinçten ağladı
{isim} ikinci gelmeyi hiç kabul etmezdi
Bu yarışta dokuzuncu oldum ama pes etmedim
Takımın ikincisi sahada çok iyiydi
"""

ONALTI = """
* Ona söyle
* Onu gördüm
* Onun fikri farklı
* Onlar geldi
* Onlara sordum
* Ondan haber yok
* Onunla konuştum
* Onları unutma
* Onca zahmet
* Onu da çağır
* Ona bak
* Ona ne oldu?
* {isim} onu aradı
* Onlar nerede?
* Onlarla gideriz
* Ondan başka kimse yok
* Onda bir şey yok
* Masanın altında
* Altını çiz
* Altından geç
* Yatağın altına bak
* {alt_gen} altında {kucuk_nesne}
* Altı çizili
* Köprünün altından geçtik
* {alt_gen} altına koy
* Altına bak
* {alt_gen} altını süpür
* Bunun altında ne yatıyor?
* Yemeğini yedi
* Hepsini yedi
* {isim} {yiyecek_acc} yedi
* Ne yedin?
* Ne yedik ne içtik
* {yiyecek_acc} yedim
* Sen de yedin mi
* Çocuklar yediler
* Yedik içtik
* Biz yedik
* Dün {yiyecek_acc} yedik
* Koyunları kırk
* Kuzuları kırktı
* Çoban yünleri kırkıyor
* Saçımı kırktırdım
* Kırkım zamanı geldi
* Yünleri kırkmışlar
* Berber saçını kırktı
* dokuz doğur | Dokuz doğurttu bize
Onu {zaman_gecmis} {yer_loc} gördüm
Onun {iyelikli} çok güzelmiş
Ona {sey_acc} verdim
Onlara haberi ben verdim
{isim} onu ve beni aradı
Onlarla {zaman_gecmis} {yer_loc} buluştum
Ondan {zaman_gecmis} haber aldım
Onlar {zaman_gelecek} {sehir} yolculuğuna çıkacak
Onca zahmete rağmen {isim} vazgeçmedi
Onunla {yer_loc} konuştum
Onlardan hiçbiri gelmedi
Onları {yer_loc} bekledim
Onun gibi güvenilir bir arkadaş bulmak zor
{isim_ins} onun hakkında konuştuk
{alt_gen} altına eğilip {kucuk_acc} aradı
Kedi {alt_gen} altından çıkıp bahçeye koştu
Çocuk {alt_gen} altına saklanıp bizi güldürdü
Bu kararın altında yatan sebebi anlamadım
{isim} raporun altına imzasını attı
Önemli cümlelerin altını kırmızı kalemle çizdim
{alt_gen} altına bakmayı unutma
Köprünün altından geçen dereyi izledik
{isim} yükün altında ezilmemek için yardım istedi
Kahvaltıda ne yediniz diye sordu
{isim} {zaman_gecmis} {yiyecek_acc} yedi ve uyudu
Biz de {yiyecek_acc} yedik
Çocuklar {yiyecek_acc} yedikten sonra uyudu
{yemek_yeri} hep birlikte {yiyecek} yedik
Ben {zaman_gecmis} {yiyecek_acc} yedim ama doymadım
Siz {yiyecek_acc} yediniz mi
Açıkta kalan {yiyecek_acc} kediler yedi
Çoban {mevsim_loc} {hayvan_acc} kırkar
{isim} dün {hayvan_acc} kırktı
Köylüler {hayvan_acc} kırkmak için toplandı
Kırkılan yünler avluda kurumaya bırakıldı
Berber müşterinin sakalını kırkıp ensesini düzeltti
Her yıl bu zamanlarda koyunlar kırkılır
{isim} yarın {hayvan_acc} kırkacak
dokuz doğur | Bekleye bekleye dokuz doğurduk
dokuz doğur | {isim} beni bekletip dokuz doğurttu
Onu aradığımda telefonu kapalıydı
Onunla {zaman_gecmis} {yer_loc} karşılaştım
Ona doğum günü hediyesi almak istiyorum
Onların evi {sehir} yakınlarında
Ondan hiçbir şey saklamadım
Onlara kapıyı kimin açtığını bilmiyorum
Onu bu işe kimin soktuğunu merak ediyorum
Ona güvenmek bazen zor oluyor
Onun adını duyunca herkes sustu
Onlardan biri {zaman_gecmis} bize uğradı
Ona kızmak yerine konuşmayı denedim
Onları {sehir} otobüsünde gördüm
Onunla yarın konuşacağım
Onun için bir sürpriz hazırladık
Ondan sonra kimse sesini duymadı
Onlar da bizimle gelmek istiyor
Onca yolu yürüyüp geldik
Ona rağmen yola devam ettik
Onu kimse tanımıyordu
Onlarla {yer_loc} kahve içtik
Çay bardağının altına peçete koydum
{isim} dolabın altındaki kutuyu çıkardı
Kitabın altı çizilmiş cümleleri tekrar okudum
Yağmur başlayınca ağacın altına sığındık
Halının altında kalan parayı {isim} buldu
Merdivenin altından garip bir ses geliyordu
Sandalyenin altına düşen {kucuk_nesne} bulunamadı
Bu iddianın altını dolduracak delil yok
Köprünün altında balık tutanlar vardı
Tablonun altına küçük bir not yapıştırdım
Arabanın altına bakıp yağ kaçırıp kaçırmadığını kontrol etti
Masanın altı yine kırıntı dolu
Kahvaltıda peynir ve zeytin yedik
{isim} acıkınca dolaptaki {yiyecek_acc} yedi
Akşam yemeğinde {yiyecek} yediler
Ne yediğini sorunca hiçbir şey demedi
Yedikçe şişmanladığını düşünüyordu
Dün gece {yiyecek_acc} kim yedi
Hepimiz aynı tabaktan yedik
Çocuklar elma yedikten sonra oyuna döndü
{isim} {yiyecek_acc} yediğine pişman oldu
Misafirlere {yiyecek} yedirdik
Yün kırkma makinesi bozulunca iş yarım kaldı
Bu ay {isim} saçını kırktıracak
Kırkılan koyunlar serin yerde dinlendi
dokuz doğur | Doktor bizi bekletip dokuz doğurttu
dokuz doğur | Sıra bir türlü gelmeyince dokuz doğurduk
"""

DEYIM = """
dört dörtlük | * Dört dörtlük bir sunum
dört dörtlük | {isim} sınavdan dört dörtlük geçti
dört dörtlük | Dört dörtlük bir takım olduk
iki arada bir derede | * İki arada bir derede kaldım
iki arada bir derede | {isim} iki arada bir derede kalınca ne yapacağını bilemedi
kırk yılın başı | * Kırk yılın başı geldin
kırk yılın başı | Kırk yılın başı bize uğradın, hoş geldin
kırk yılın başı | {isim} kırk yılın başı bir iyilik yaptı
kırk fırın ekmek | * Kırk fırın ekmek yemiş biri
kırk fırın ekmek | {isim} kırk fırın ekmek yemiş, bu işleri bilir
yedi kat yabancı | * Yedi kat yabancı gibi baktı
yedi kat yabancı | {isim} bize yedi kat yabancı davrandı
bir taşla iki kuş | * Bir taşla iki kuş vurduk
bir taşla iki kuş | Bu işle bir taşla iki kuş vurmuş olacağız
iki ayağını bir pabuca | * İki ayağını bir pabuca soktu
iki ayağını bir pabuca | {isim} herkesin iki ayağını bir pabuca sokacak
dokuz köyden kovulur | * Dokuz köyden kovulur bu adam
dokuz köyden kovulur | Böyle giderse dokuz köyden kovulur
bin pişman | * Bin pişman oldum
bin pişman | {isim} yaptığına bin pişman
bin pişman | Dönüp bakınca bin pişman oluyorsun
bin bir türlü | * Bin bir türlü derdi var
bin bir türlü | {isim} bin bir türlü bahane buldu
yüz bul | * Yüz bulunca şımardı
yüz bul | {isim} yüz bulunca haddini aştı
yüz bul | Fazla ilgi gösterirsen yüz bulur
beş para etmez | * Beş para etmez bu iş
beş para etmez | Bu kadar özensiz iş beş para etmez
beş para etmez | {isim} beş para etmez biri çıktı
üç aşağı beş yukarı | * Üç aşağı beş yukarı aynı
üç aşağı beş yukarı | Fiyatlar üç aşağı beş yukarı bu civarda
üç aşağı beş yukarı | {isim} işi üç aşağı beş yukarı bitirdi
iki gözüm | * Gel iki gözüm
iki gözüm | {isim}, iki gözüm, nereye böyle?
bir elin nesi var iki elin sesi var | * Bir elin nesi var iki elin sesi var
bir elin nesi var iki elin sesi var | Hadi hep beraber çalışalım, bir elin nesi var iki elin sesi var
iki dirhem bir çekirdek | * İki dirhem bir çekirdek giyindi
iki dirhem bir çekirdek | {isim} düğüne iki dirhem bir çekirdek gitmiş
dokuz canlı | * Kedi dokuz canlıdır
dokuz canlı | Bizim kedi gerçekten dokuz canlı çıktı
yedi düvel | * Yedi düvel birleşse de olmaz
yedi düvel | Yedi düvele karşı direndiler
kırk yıllık dost | * Kırk yıllık dostum
kırk yıllık dost | {isim} kırk yıllık dostumdur
on parmağında on marifet | * On parmağında on marifet var
on parmağında on marifet | {isim} gerçekten on parmağında on marifet biri
sıfırı tüket | * Sıfırı tüketti
sıfırı tüket | Para bitti, sıfırı tükettik
sıfırdan başla | * Sıfırdan başladı
sıfırdan başla | {isim} her şeye sıfırdan başladı
sıfır araba | * Sıfır araba aldık
sıfır araba | Sıfır araba almak için kredi çekti
bire bir | * Bire bir aynı
bire bir | Bu kopya orijinaliyle bire bir aynı
birebir | * Birebir görüşme yaptık
birebir | Birebir aynı olmasa da benziyor
bir an önce | * Bir an önce gel
bir an önce | {isim} bir an önce eve dönmek istiyor
bir daha | * Bir daha yapma
bir daha | Bir daha {yer_loc} görüşmeyiz
tek bir | * Tek bir kelime etmedi
tek bir | Tek bir {kucuk_nesne} bile kalmamış
bir de | * Bir de {urun} alalım
bir de | {isim} bir de {urun} istedi
birdenbire | * Birdenbire yağmur bastırdı
birdenbire | {isim} birdenbire ağlamaya başladı
kırk dereden su getir | * Kırk dereden su getirdi
kırk dereden su getir | {isim} kırk dereden su getirip bahane buldu
yedi iklim dört bucak | * Yedi iklim dört bucak gezdi
yedi iklim dört bucak | {isim} yedi iklim dört bucak dolaştı
iki cami arasında | * İki cami arasında kaldı
iki cami arasında | {isim} iki cami arasında beynamaz kaldı
bir ayağı çukurda | * Bir ayağı çukurda
bir ayağı çukurda | Hasta yatağında bir ayağı çukurda yaşıyor
bir yastıkta koca | * Bir yastıkta kocayın
bir yastıkta koca | Gençler, bir yastıkta kocayın
bir kulağından girip öbüründen çık | * Bir kulağından girip öbüründen çıkıyor
bir kulağından girip öbüründen çık | Söylediklerim bir kulağından girip öbüründen çıkıyor
bir çırpıda | * Bir çırpıda bitirdi
bir çırpıda | {isim} {yiyecek_acc} bir çırpıda yedi
bir el at | * Bir el at şuna
bir el at | Şu masaya bir el atar mısın
beş parasız | * Beş parasız kaldık
beş parasız | {isim} ay sonunda beş parasız kaldı
üç günlük dünya | * Üç günlük dünya
üç günlük dünya | Üç günlük dünyada kimseyi kırmamalı
üç kâğıtçı | * Üç kâğıtçıya dikkat et
üç kâğıtçı | Pazarda üç kâğıtçı oynayan biri yakalandı
dört elle sarıl | * Dört elle sarıldı
dört elle sarıl | {isim} işine dört elle sarılıyor
dört bir yan | * Dört bir yan sessizdi
dört bir yan | {isim} dört bir yanına baktı
dört nala | * Dört nala koştu
dört nala | Atlar dört nala geldi
dört duvar arasında | * Dört duvar arasında kaldı
dört duvar arasında | {isim} dört duvar arasında yaşıyor
dört gözle bekle | * Dört gözle bekliyoruz
dört gözle bekle | {isim} mektubu dört gözle bekledi
dört mevsim | * Dört mevsim yeşil
dört mevsim | Bu bahçe dört mevsim çiçek açar
altı üstü | * Altı üstü bir {urun}
altı üstü | Altı üstü bir kahve için bu kadar tartıştık
yedisinden yetmişine | * Yedisinden yetmişine herkes geldi
yedisinden yetmişine | Yedisinden yetmişine herkes bu şarkıyı bilir
yüz göz ol | * Yüz göz oldu
yüz göz ol | Çocukların başında yüz göz olduk
yüz ver | * Yüz verme ona
yüz ver | Çocuğa fazla yüz verince hep istedi
yüz çevir | * Yüz çevirdi bana
yüz çevir | Zor günde yüz çeviren dost olmaz
yüz karası | * Yüz karası olma
yüz karası | Aileye yüz karası olmaktan korkuyordu
yüz akı | * Yüz akıyla çıktı
yüz akı | Sınavdan yüz akıyla geçtik
bin bir çeşit | * Bin bir çeşit yemek vardı
bin bir çeşit | Sofrada bin bir çeşit {yiyecek} vardı
iki eli kanda | * İki eli kanda olsa gelir
iki eli kanda | Hasta olsa da iki eli kanda olsa işini bırakmaz
iki gözü iki çeşme | * İki gözü iki çeşme ağladı
iki gözü iki çeşme | {isim} iki gözü iki çeşme ağlıyordu
iki cihan | * İki cihan saadeti
iki cihan | Sana iki cihan saadeti diliyorum
iki elim yakanda | * İki elim yakanda
iki elim yakanda | Bir daha yaparsan iki elim yakanda olur
iki lafın belini | * İki lafın belini kırdı
iki lafın belini | Toplantıda iki lafın belini kırmak için oturduk
iki yakası bir araya gel | * İki yakası bir araya gelmiyor
iki yakası bir araya gel | Bu maaşla iki yakası bir araya gelmez
iki büklüm | * İki büklüm oldu
iki büklüm | {isim} yükün altında iki büklüm yürüyordu
bir bakmışsın | * Bir bakmışsın akşam olmuş
bir bakmışsın | Oyalanırsan bir bakmışsın gün bitmiş
bir hayli | * Bir hayli yoruldum
bir hayli | {isim} bir hayli sevindi
bir nebze | * Bir nebze rahatladım
bir nebze | {isim} bir nebze sakinleşti
bir yana | * Bir yana bırak
bir yana | Şakayı bir yana bırakıp çalışalım
bir hamlede | * Bir hamlede kazandı
bir hamlede | {isim} rakibini bir hamlede yendi
bir anda | * Bir anda karardı
bir anda | {zaman_gecmis} bir anda yağmur bastırdı
bir bakıma | * Bir bakıma haklısın
bir bakıma | Bir bakıma {isim} haklıydı
bir arada | * Hep bir arada
bir arada | Bütün aile bir arada yaşıyor
bir tek | * Bir tek sen yoktun
bir tek | Bir tek {isim} bunu bilmiyordu
birçok | * Birçok {kisi} geldi
birçok | {isim} birçok {urun} aldı
yedi cihan | * Yedi cihana duyurdu
yedi cihan | Adı yedi cihana yayıldı
yedi sülale | * Yedi sülaleni sayarım
yedi sülale | {isim} yedi sülalesini sayıp döktü
yedi mahalle | * Yedi mahalle duydu
yedi mahalle | Kavganın sesini yedi mahalle duydu
bir ağızdan | * Bir ağızdan söylediler
bir ağızdan | Çocuklar bir ağızdan şarkı söyledi
bir kere | * Bir kere de sen dene
bir kere | {isim} bir kere bile gelmedi
bir tanem | * Bir tanem
bir tanem | Gel buraya bir tanem
bir dahaki | * Bir dahaki sefere
bir dahaki | Bir dahaki sefere erken gel
bir ara | * Bir ara uğra
bir ara | Bir ara {isim} ile görüşelim
bir zahmet | * Bir zahmet kapıyı kapat
bir zahmet | Bir zahmet {isim} geldi mi bak
bir sonraki | * Bir sonraki durak
bir sonraki | Bir sonraki toplantıda konuşuruz
bir gün | * Bir gün gelecek
bir gün | Bir gün {isim} bana {yer_loc} rastladı
bir şey | * Bir şey söyle
bir şey | {isim} bir şey söyleyecekti ama vazgeçti
bir sürü | * Bir sürü {urun} aldık
bir sürü | Masada bir sürü {yiyecek} vardı
bir türlü | * Bir türlü olmadı
bir türlü | Bir türlü {urun} bulamadım
bir iki derken | * Bir iki derken akşam oldu
bir iki derken | Bir iki derken yıl bitti
bir bir say | * Bir bir saydı
bir bir say | {isim} parmaklarıyla bir bir saydı
birbirine | * Birbirine sarıldılar
birbirine | Çocuklar birbirine ışık tuttu
dört başı mamur | * Dört başı mamur bir proje
dört başı mamur | {isim} dört başı mamur bir ev yaptırdı
bir kalemde | * Bir kalemde sildi
bir kalemde | Borçları bir kalemde sildiler
bir solukta | * Bir solukta içti
bir solukta | {isim} kitabı bir solukta okudu
bir çuval inciri berbat et | * Bir çuval inciri berbat etti
bir çuval inciri berbat et | Aceleci davranıp bir çuval inciri berbat ettik
bir fiske | * Bir fiske vursan düşer
bir fiske | Bu eski masa bir fiske vurulsa yıkılır
bir lokma | * Bir lokma ekmek
bir lokma | Evde bir lokma ekmek kalmamış
bir avuç | * Bir avuç {urun}
bir avuç | {isim} cebine bir avuç {urun} doldurdu
bir zamanlar | * Bir zamanlar burada ev vardı
bir zamanlar | Bir zamanlar {isim} burada otururdu
bir ihtimal | * Bir ihtimal daha var
bir ihtimal | Bir ihtimal {isim} haklı çıkabilir
bin dereden su getir | * Bin dereden su getirdi
bin dereden su getir | {isim} bin dereden su getirip yine de ikna olmadı
bir çift söz | * Bir çift söz edeyim
bir çift söz | Gelmişken {isim_ins} bir çift söz edelim
bir tutam | * Bir tutam tuz
bir tutam | Yemeğe bir tutam tuz attım
bir dilim | * Bir dilim {dilimli}
bir dilim | {isim} bir dilim {dilimli} istedi
bir kez daha | * Bir kez daha dene
bir kez daha | Bir kez daha {yer_loc} buluşalım
bir eli yağda bir eli balda | * Bir eli yağda bir eli balda
bir eli yağda bir eli balda | {isim} bir eli yağda bir eli balda yaşıyor
bir ayak üstünde | * Bir ayak üstünde bekledik
bir ayak üstünde | Kapıda bir ayak üstünde bekleyip döndük
beş vakit | * Beş vakit namaz kıldı
beş vakit | Dedem beş vakit namazını aksatmaz
yedi canlı | * Yedi canlı kedi
yedi canlı | Bizim kedi yedi canlı çıktı
"""

OZELAD = """
dokuz eylül üniversitesi | * Dokuz Eylül Üniversitesi
dokuz eylül üniversitesi | {isim} Dokuz Eylül Üniversitesi'ni kazandı
dokuz eylül üniversitesi | Kardeşim Dokuz Eylül Üniversitesi'nde okuyor
ondokuz mayıs üniversitesi | * Ondokuz Mayıs Üniversitesi
ondokuz mayıs üniversitesi | {isim} Ondokuz Mayıs Üniversitesi'nden mezun oldu
ondokuz mayıs üniversitesi | Ondokuz Mayıs Üniversitesi'nin yemekhanesi çok temiz
yüzüncü yıl üniversitesi | * Yüzüncü Yıl Üniversitesi
yüzüncü yıl üniversitesi | {isim} Yüzüncü Yıl Üniversitesi'nde asistan oldu
yüzüncü yıl üniversitesi | Van'daki Yüzüncü Yıl Üniversitesi geniş bir kampüse sahip
beşiktaş | * Beşiktaş maçı
beşiktaş | {zaman_gelecek} Beşiktaş'ta toplanıyoruz
beşiktaş | {isim} Beşiktaş'ın taraftarı
beşiktaş | Beşiktaş iskelesinden vapura bindik
yedikule | * Yedikule Hisarı
yedikule | Yedikule'de yürüyüş yaptık
yedikule | {isim} Yedikule'den eve döndü
üçkuyular | * Üçkuyular
üçkuyular | {isim} Üçkuyular'da oturuyor
üçkuyular | Üçkuyular'dan vapura bindik
dörtyol | * Dörtyol ilçesi
dörtyol | {isim} Dörtyol'dan geldi
dörtyol | Dörtyol'da portakal bahçeleri var
kırklareli | * Kırklareli'ne gidiyoruz
kırklareli | Kırklareli'nin peyniri meşhurdur
kırklareli | {isim} Kırklareli'nde doğdu
binali | * Binali geldi
binali | {isim_ins} Binali de toplantıdaydı
binali | Binali'nin babası bizi aradı
altınordu | * Altınordu maçı
altınordu | Altınordu'nun taraftarları stada geldi
altınordu | {zaman_gelecek} Altınordu ile oynayacağız
yedi cüceler | * Yedi Cüceler masalı
yedi cüceler | Çocuklar Pamuk Prenses ve Yedi Cüceler'i izledi
yedi cüceler | Yedi Cüceler'in evi ormanın içindeydi
üç silahşörler | * Üç Silahşörler romanı
üç silahşörler | {isim} Üç Silahşörler'i bir çırpıda okudu
üç silahşörler | Üç Silahşörler filmini yeniden izledik
kırk haramiler | * Ali Baba ve Kırk Haramiler
kırk haramiler | Çocuklara Ali Baba ve Kırk Haramiler masalını okudum
kırk haramiler | Kırk Haramiler mağarayı kendilerine sığınak yapmış
binbir gece masalları | * Binbir Gece Masalları
binbir gece masalları | {isim} Binbir Gece Masalları'nı okuyor
binbir gece masalları | Binbir Gece Masalları'ndaki hikâyeler beni büyüledi
beş hececiler | * Beş Hececiler
beş hececiler | Edebiyat dersinde Beş Hececiler'i işledik
beş hececiler | Beş Hececiler'in şiirleri ezberlendi
yediler | * Yediler toplandı
yediler | Yediler grubunun toplantısı yarın
kırklar dağı | * Kırklar Dağı
kırklar dağı | Kırklar Dağı'na tırmandık
kırklar dağı | {isim} Kırklar Dağı'nın eteğinde yaşıyor
bingöl | * Bingöl'e gidiyoruz
bingöl | Bingöl'ün balı çok meşhurdur
binbirdirek | * Binbirdirek Sarnıcı
binbirdirek | Binbirdirek Sarnıcı'nı gezdik
kırkpınar | * Kırkpınar güreşleri
kırkpınar | Kırkpınar'da yağlı güreş izledik
beşparmak dağları | * Beşparmak Dağları
beşparmak dağları | Beşparmak Dağları'nda yürüyüş yaptık
yedigöller | * Yedigöller Milli Parkı
yedigöller | Yedigöller'e kamp yapmaya gittik
yedi uyurlar | * Yedi Uyurlar efsanesi
yedi uyurlar | Yedi Uyurlar mağarası turistlerle doldu
yedi bela hüsnü | * Yedi Bela Hüsnü filmi
yedi bela hüsnü | {isim} Yedi Bela Hüsnü'yü kaç kez izledi
yüzyıllık yalnızlık | * Yüzyıllık Yalnızlık romanı
yüzyıllık yalnızlık | {isim} Yüzyıllık Yalnızlık'ı yeniden okudu
onikişubat | * Onikişubat ilçesi
onikişubat | Onikişubat'ta yeni bir kafe açıldı
ondokuzmayıs | * Ondokuzmayıs ilçesi
ondokuzmayıs | Ondokuzmayıs'a yaz tatilinde gideriz
beşikdüzü | * Beşikdüzü
beşikdüzü | Beşikdüzü'nde fındık toplanır
yedi tepe | * Yedi Tepe
yedi tepe | İstanbul'a Yedi Tepe'nin şehri derler
oniki ada | * Oniki Ada
oniki ada | Oniki Ada'ya feribotla gidilir
kırkağaç | * Kırkağaç'ta pazar kuruldu
kırkağaç | {isim} Kırkağaç'tan geliyor
altındağ | * Altındağ'da oturuyoruz
altındağ | Altındağ'daki okul yenilendi
"""

SOZCUK = """
* Onbaşı emri verdi
* Yeni gelen onbaşı çok disiplinliydi
{isim} terhis olmadan önce onbaşı oldu
* Yüzbaşı birliğe talimat verdi
Yüzbaşı {zaman_gelecek} geliyor
* Binbaşı sabah toplantısına katıldı
Binbaşı {zaman_gecmis} kışlayı denetledi
* Duvarda koca bir kırkayak gördüm
Kırkayak yavaşça taşın altına girdi
* Tahtaya bir üçgen çizdi
Üçgenin kenarlarını birlikte ölçtük
* Dörtgenin açıları toplandı
Defterine bir dörtgen çizdi
* Beşgen biçimli bir oda
Beşgen masaya sığmadık
* Arıların peteği altıgendir
Altıgen biçiminde bir masa aldık
* Sekizgen tabela asıldı
{isim} sekizgen şeklinde bir masa seçti
* İkiz kardeşler aynı okula gitti
{isim} ikiz bebeklerine isim aradı
* Üçüz bebekler doğdu
Komşunun üçüz çocukları var
* At dörtnala koştu
Dörtnala gelen atlıyı herkes izledi
* Yediveren gülü bahçeyi sardı
Duvarın dibinde yediveren gülleri açtı
* Bu bir ikilem
{isim} büyük bir ikilemde kaldı
* İkili görüşme yapıldı
İkili ilişkiler yeniden gelişiyor
* Üçlü koltuğa oturduk
Üçlü çekim yapılacak
* Beşli takım kuruldu
Beşli çete mahalleyi korkuttu
* Onluk bozuk para
Cebimde onluk kalmadı
* Yüzlük banknot bozdurdum
Cüzdanda yüzlük kalmadı
* Binlik banknot
Binlik bozdurmak zor oldu
* İkişer ikişer sıraya girin
Çocuklara ikişer {kucuk_nesne} dağıttı
* Üçer üçer saydı
Her kişiye üçer dilim {dilimli} verdi
* Beşer beşer ayrıldılar
Takımlar beşer kişiden kuruldu
* Onar onar dizdi
Her sınıfa onar kitap bağışladı
* İkimiz de geç kaldık
İkimiz de {sehir} şehrinde doğduk
* Üçümüz yola çıktık
Üçümüz de {yer_loc} buluşuruz
beşi birden | * Beşi birden içeri girdi
beşi birden | Çocuklar beşi birden koşarak geldi
* Onlarca {kisi} toplandı
Onlarca {kisi} {yer_loc} bekliyordu
* Yüzlerce {kisi} yürüdü
Yüzlerce {kisi} {sehir} sokaklarını doldurdu
* Binlerce {kisi} izledi
Binlerce {kisi} {sehir} meydanında toplandı
* Milyonlarca {kisi} bu haberi duydu
Milyonlarca insan ekran başındaydı
* Birkaç {kisi} geldi
{isim} birkaç {urun} aldı
* Birlikte gidelim
{isim_ins} birlikte {sehir} yoluna çıktık
* Biraz bekle
Biraz sonra {isim} gelir
* Birbirimizi iyi tanırız
Birbirinize sabırlı olun
* Dörtlük okudu
Şiirin son dörtlüğünü ezberledi
* Altılı takım aldık
Altılı masa kurduk
* İkiyüzlü biri
{isim} ikiyüzlülükten nefret eder
* Yüzük parmağında parlıyordu
{isim} yüzüğünü {yer_loc} unutmuş
* Yüzey çok pürüzlüydü
Yüzeysel bir bakışla hiçbir şey anlaşılmaz
* Binici atından düştü
Genç binici yarışı kazandı
* Binanın girişinde bir kedi vardı
Yeni bina {sehir} merkezinde yükseliyor
* Altın bilezik taktı
Altın fiyatları yine arttı
* Onay bekliyoruz
Belge dün onaylandı
* Köprünün onarımı sürüyor
Yolun onarımı {zaman_gelecek} başlıyor
* Bebeği beşiğe yatırdık
Beşik kertme ağacından yapılmış
* İkindi vakti çay içtik
İkindi ezanı okunurken çıktık
* Birey olarak özgürsün
Bireysel emeklilik hakkında bilgi aldım
"""

BIRIM = """
* Tonlarca yük taşıdılar
* Metrelerce kumaş aldı
* Kalorisi düşük
* İnç inç ölçtü
* Dakikalarca bekledim
* Saniyesinde bitti
* Liranın değeri düştü
* {ay_ek} geliriz
* Kilo verdim
* Kilo almak istemiyor
* Litresi kaç para?
* Gram gram biriktirdi
* Hektarlarca arazi
* Dönümlerce bahçe
* Saatlerce yürüdük
* Günlerce yağdı
* Haftalarca sürdü
* Aylarca bekledik
* Yıllarca çalıştı
* Kuruşu kuruşuna
* Dolara güven
* Avro düştü
* Sterlin yükseldi
* Metreyi getir
* Derecesi yüksek
* Pikseli bozuk
* Karat hesabı yaptı
* Beygir gücü yüksek
* {ay_ek} döneriz
* {ay_abl} beri yok
* {ay_gen} sonunda
* Kasımda başlıyoruz
* Saat kaç oldu?
* Saati söyle
{ay_ek} tatile çıkacağız
{isim} {ay_ek} yeni işine başlayacak
{ay_abl} beri {isim} bize uğramadı
{ay_dat} kadar sabret
{ay_gen} sonunda kira artacak
{ay_gen} ilk haftasında yağmur bekleniyor
Geçen {ay_bare} ayında çok yağmur yağdı
Her {ay_bare} ayında bu festival yapılır
{ay_bare} ayı bu yıl çok yoğun geçti
Liranın değeri son aylarda sürekli düşüyor
Dolara olan talep birden arttı
Avro ve sterlin hakkında {isim} hiçbir şey bilmiyor
{isim} her kuruşunu biriktirdi
Kilo vermek istiyorsan şekeri azalt
{isim} geçen yıl çok kilo aldı
Terzi metreyi boynuma doladı
Kumaşın metresi kaç lira diye sordum
Zeytinyağının litresi bu ay çok arttı
Fırının derecesini ayarla
Termometredeki dereceyi okudum
Milimetre hassasiyetinde ölçüm yapıldı
Tonlarca çöp {sehir} sokaklarından toplandı
Kalorisi yüksek yiyeceklerden uzak durmalısın
Bu telefonun pikseli çok yüksek
Araçların beygir gücü hakkında konuştuk
Hektarlarca arazi {sehir} yakınlarında satılıkmış
Dakikalarca {yer_loc} bekledik
Saatlerce uğraştı ama başaramadı
Haftalarca süren hazırlık sonunda bitti
Saniyesinde cevap veren bir sistem istiyoruz
Yıllarca aynı yolu yürüdü
Dönümlerce bahçeyi {isim} tek başına suladı
Günlerce süren yağmur sonunda dindi
Yüzde kaç oranında indirim var?
Aylarca beklediğimiz haber sonunda geldi
Dolar ne kadar oldu diye merak ettim
Avronun değeri bu hafta arttı
Gramı kaç lira olduğunu sordu
Altın gramı bugün yükseldi
Sterlinin değeri {zaman_gecmis} değişti
Kilosu pahalı ama tadı güzel
{isim} litrelerce su taşıdı
Kilometrelerce yürüyüp köye ulaştık
"""

KESIR = """
* Yarım saat bekledim
* Yarım yamalak biliyor
* Çeyrek altın aldı
* Çeyrek final maçı
* {kesir_nom}
* Yarım kalmış
* Yarım porsiyon
* Yarım ekmek
* Yarım kilo {urun}
* Çeyrek kilo {urun}
* {isim} yarım bıraktı
* Yarısı yenmiş
* Çeyreği boş
* Yarım gün çalıştı
* Yarım elma yedi
* Yarısını sen al
* Çeyrek saat sürdü
* Yarım kaldı
* Yarısı bana
* İkide bir arıyor
* {kesir_bare} kadar
Yarım saat sonra {isim} gelir
Toplantıyı yarım bırakıp çıktı
Kitabı yarım okudum, kalanını yarın bitiririm
{isim} yarım yamalak İngilizce konuşuyor
Çeyrek altını bileziğe çevirttik
Çeyrek final maçını {zaman_gelecek} oynayacaklar
Sınıfın {kesir_nom} bugün gelmedi
Nüfusun {kesir_nom} gençlerden oluşuyor
{isim} {yiyecek_gen} {kesir_acc} yedi
{isim} {yiyecek_gen} yarısını yedi
{isim} maaşının {kesir_acc} kiraya veriyor
Kitabın {kesir_acc} okudum
Tarlanın {kesir_nom} henüz ekilmedi
Havuzun {kesir_bare} kadarı doldu
Yolun {kesir_bare} kadarını yürüdük
Hastaların {kesir_nom} taburcu edildi
Kazancın {kesir_dat} razıyım
Maaşımın yarısı kiraya gidiyor
Salonun çeyreği boş kaldı
{isim} bakkaldan yarım kilo {urun} aldı
Yarım kalan işi {isim} bitirdi
Yarım gün izin alıp {sehir} yolculuğuna çıktık
{isim} ikide bir saatine bakıyor
Çocuk ikide bir {urun} istiyor
Yarım ağızla özür dilemekten kaçındı
Pastanın yarısı çoktan bitmişti
{isim} çeyrek kilo {urun} istedi
Sınıfın yarısı kantine indi
Ormanın {kesir_nom} yandı
Okulun {kesir_nom} yeni öğrencilerden oluşuyor
Yarım porsiyon {yiyecek} söyledik
* Saat buçuğu vuruyor
* Buçuklarda gelirim
* Buçuğu vurdu
* Buçuklu saatler uygun
Buçuklu saatlerde seferler var
Servis buçuklu saatlerde kalkıyor
Duvardaki saat buçuğu vurdu
Tam saatlerde ve buçuklarda zil çalıyor
Çan her buçukta çalar
Saat buçuğu vurunca {isim} uyandı
"""

OLGULAR = [
    ("bin", "negatif_es", BIN),
    ("ikinciel", "negatif_kalip", IKINCIEL),
    ("yuz", "negatif_es", YUZ),
    ("sira", "negatif_kalip", SIRA),
    ("onalti", "negatif_es", ONALTI),
    ("deyim", "negatif_kalip", DEYIM),
    ("ozelad", "negatif_kalip", OZELAD),
    ("sozcuk", "negatif_kalip", SOZCUK),
    ("birim", "negatif_kalip", BIRIM),
    ("kesir", "negatif_kalip", KESIR),
]


# ======================================================================================
# Karşıt pozitif slotları: yalnız `varliklar.kur_*` ile kurulur
# ======================================================================================
def _sec(deger):
    return lambda r: r.choice(deger)


def _para(degerler):
    return lambda r, ek: V.kur_para(lira=r.choice(degerler), ek=ek)


def _kard(degerler):
    return lambda r, ek: V.kur_kardinal(r.choice(degerler), ek=ek)


def _olcu(degerler, birimler):
    return lambda r, ek: V.kur_olcu(r.choice(degerler), "", r.choice(birimler), r.randrange(2), ek=ek)


def _yuzde(degerler):
    return lambda r, ek: V.kur_yuzde(r.choice(degerler), ek=ek)


def _saat(degerler):
    return lambda r, ek: V.kur_saat(r.choice(degerler), 0, False, "tam", ek)


def _sira(degerler):
    return lambda r, ek: V.kur_sira(r.choice(degerler))


def _bucuk_olcu(r, ek):
    return V.kur_olcu(r.randint(1, 9), "5", r.choice(["kg", "L", "m", "km"]), r.randrange(2), True, False, ek)


def _bucuk_say(r, ek):
    return V.kur_ondalik(r.randint(1, 9), "5", True, False, ek)


def _bucuk_saat(r, ek):
    return V.kur_saat(r.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]), 30, True, "dk", ek)


KS = {
    "bin_tl": _para([1000, 1000, 1000, 1250, 1500, 1800, 1100, 1200]),
    "bin_say": _kard([1000, 1000, 1200, 1500, 1800, 1100, 1250]),
    "bin_olcu": _olcu([1000, 1000, 1200, 1500], ["m", "km", "g", "mL", "mm"]),
    "bin_m": _olcu([1000, 1000, 1200, 1500], ["m"]),
    "yuz_yol": _olcu([100, 100, 150, 120, 125, 175], ["m", "km"]),
    "on_yol": _olcu([10, 10, 12, 15, 14], ["km", "m"]),
    "yedi_yol": _olcu([7], ["km", "m"]),
    "alti_kg": _olcu([6], ["kg"]),
    "dokuz_kg": _olcu([9], ["kg"]),
    "iki_kg": _olcu([2], ["kg"]),
    "kirk_kg": _olcu([40, 45], ["kg"]),
    "yuz_tl": _para([100, 100, 100, 120, 125, 150, 175, 180]),
    "yuz_say": _kard([100, 100, 120, 150, 180, 110]),
    "yuz_m": _olcu([100, 100, 150, 120, 175], ["m"]),
    "yuz_olcu": _olcu([100, 100, 150, 120, 125], ["m", "km", "cm", "g", "mL", "L"]),
    "yuz_yuzde": _yuzde([100]),
    "on_say": _kard([10, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),
    "on_tl": _para([10, 10, 11, 12, 15, 18, 19]),
    "on_olcu": _olcu([10, 10, 12, 15, 14], ["kg", "m", "cm", "L", "km", "g"]),
    "on_yuzde": _yuzde([10, 10, 12, 15, 18]),
    "on_saat": _saat([10, 10, 11, 12]),
    "alti_tl": _para([6]),
    "alti_yuz_tl": _para([600, 650, 625, 675, 640]),
    "alti_olcu": _olcu([6], ["kg", "m", "L", "km", "cm"]),
    "alti_bin": _kard([6000, 6500, 6200, 6800]),
    "alti_yuzde": _yuzde([6]),
    "alti_saat": _saat([6]),
    "yedi_tl": _para([7]),
    "yedi_yuz_tl": _para([700, 750, 725]),
    "yedi_yuz_g": _olcu([700, 750, 725], ["g"]),
    "yedi_olcu": _olcu([7], ["kg", "m", "L", "km", "cm"]),
    "yedi_yuzde": _yuzde([7]),
    "yedi_saat": _saat([7]),
    "kirk_say": _kard([40, 40, 41, 42, 45, 48]),
    "kirk_tl": _para([40, 40, 45, 48]),
    "kirk_olcu": _olcu([40, 45], ["cm", "m", "kg", "L"]),
    "kirk_yuzde": _yuzde([40]),
    "dokuz_olcu": _olcu([9], ["kg", "m", "L", "km", "cm"]),
    "dokuz_yuz_tl": _para([900, 950, 925]),
    "dokuz_saat": _saat([9]),
    "iki_olcu": _olcu([2], ["kg", "m", "L", "km", "cm"]),
    "sira_1": _sira([1]), "sira_2": _sira([2]), "sira_3": _sira([3]), "sira_4": _sira([4]), "sira_5": _sira([5]),
    "sira_k": _sira([2, 3, 4, 5, 6, 7, 8, 9]),
    "sira_b": _sira([10, 11, 12, 15, 20]),
    "buc_olcu": _bucuk_olcu,
    "buc_kg": lambda r, ek: V.kur_olcu(r.randint(1, 9), "5", "kg", r.randrange(2), True, False, ek),
    "buc_say": _bucuk_say,
    "buc_saat": _bucuk_saat,
}

KARSIT = """
{bin_tl} ver
{bin_tl} yeter
Taksiciye {bin_tl} verdim
{isim} {bin_tl} ödeyip taksiye bindi
{bin_tl:yonelme} satılıyor
{bin_tl:ayrilma} başlıyor
Bu {esya} {bin_tl:bulunma} duruyor
{bin_say} kişi geldi
{bin_say} kişi bu yüzden vazgeçti
{bin_m} yürüdük
{bin_m:lik} yol
{isim} {bin_m:ayrilma} fazla yürüdü
{yuz_m} yüzdü
{yuz_m} yüzdük
Havuzda {yuz_m} yüzdüm
{isim} {su_yeri} {yuz_m} yüzdü
{yuz_tl} ver
{yuz_tl} yüzünden kavga ettiler
{yuz_tl:yonelme} kadar öderim
{yuz_say} kişi denizde yüzdü
{yuz_say} kişi bu yüzden sıraya girdi
{yuz_yuzde} eminim
{yuz_yuzde} doğru değil
{yuz_olcu:lik} bir parça
{on_say} kişi ona baktı
{on_say} kişi onu aradı
{on_tl} verip ona çay ısmarladı
{on_yuzde} indirimi ona verdiler
Saat {on_saat:bulunma} ona haber verelim
Saat {on_saat:bulunma} {tasit_dat} bineceğiz
{on_yol} yol var, onunla gideriz
{alti_yuz_tl:ilgi} altında bir şey bulamadık
{alti_tl:ilgi} altında bir fiyat arıyorum
{isim} masanın altında {alti_tl} buldu
{alti_kg} {urun} yedik
{alti_bin} {kisi} bu yüzden yola çıktı
Saat {alti_saat:bulunma} masanın altında buluşalım
{alti_yuzde} indirim yapıldı, altını çizdim
{isim} {yedi_yuz_g} {urun} yedi
{isim} {yedi_tl} verip {yiyecek_acc} yedi
{yedi_yuz_tl} verip {yiyecek_acc} yedik
{yedi_yuz_g} yedi
{yedi_yol} yol yürüyüp {yiyecek_acc} yedik
Saat {yedi_saat:bulunma} {yiyecek_acc} yedik
Faiz {yedi_yuzde} oldu, biz de {yiyecek_acc} yedik
{kirk_say} koyunu kırktılar
{isim} {kirk_say} koyunu kırktı
{kirk_say} kişi yemeği yedi
{kirk_tl} verip koyunları kırktırdı
{kirk_kg} yünü kırktı
{kirk_yuzde} indirimle {urun} yedik
{dokuz_kg} {urun} yedi
{dokuz_yuz_tl:ilgi} altına düştü
Saat {dokuz_saat:bulunma} {tasit_dat} bindik
{iki_kg} {urun} aldım
{sira_2} katta oturuyor
{sira_3} sınıfa gidiyor
{sira_1} kata çıkın
{sira_k} yüzyılda yaşamış bir şair
{sira_k} sınıf öğrencisi yüzmeyi biliyor
{isim} {sira_k} kattaki odaya taşındı
Sözleşmenin {sira_k} maddesi bu yüzden değişti
{sira_4} sokakta oturuyoruz
{sira_b} kata çıkan çocuk
{sira_5} cadde üzerindeki dükkân
{isim} {sira_k} bölümü bitirdi
Yarışta {yuz_m} yüzen {isim} birinci geldi
{isim} {bin_tl} verip ikinci el {ikinci_el_esya} aldı
{yuz_tl} verip ikinci el bir {ikinci_el_esya} aldı
{on_say} kişi ikinci el {ikinci_el_esya} baktı
{buc_kg} {urun} aldım
Saat {buc_saat:bulunma} buluşalım
{buc_say} {sure_birim_k} yüzdük
{yuz_say} kişi {su_yeri} yüzdü
{bin_tl} verip {tasit_dat} bindi
{on_say} kişi {tasit_dat} bindi
{kirk_say} {kisi} {tasit_dat} bindi
{yuz_yol} yürüdük, sonra {tasit_dat} bindik
{yuz_say} {kisi} {yer_loc} bekliyordu
{bin_say} {kisi} {sehir} yolunda yürüdü
{bin_tl} kaldı
{bin_tl} eder
{bin_tl} yok
{yuz_tl} eder
{yuz_tl} yeter
{yuz_m} kaldı
{yuz_m} daha
{yuz_say} kişi var
{bin_say} kişi var
{on_say} kişi bindi
{on_tl} yeter
{alti_tl} ver
{yedi_tl} ver
{kirk_tl} ver
{dokuz_yuz_tl} eder
{sira_2} kat burası
{sira_k} kat burası
{sira_k} sınıf burası
{sira_1} kat
{sira_3} kat solda
{yuz_yuzde} haklısın
{on_yuzde} indirim
{bin_m} kaldı
{yuz_olcu} yeter
{on_say} {kisi} geldi
{kirk_say} {kisi} geldi
{yuz_tl:yonelme} aldım
{yuz_tl:yonelme} verdim
{sira_2} katta
{sira_3} sınıfta
"""
F["sure_birim_k"] = ["saat", "gün", "hafta"]


# ======================================================================================
# Şablon kayıtları
# ======================================================================================
SLOT = re.compile(r"\{(\w+)(?::(\w+))?\}")


class Sablon:
    __slots__ = ("id", "olgu", "kategori", "metin", "kisa", "etiket", "parcalar", "karsit", "ilk_dolgu")

    def __init__(self, id_, olgu, kategori, metin, kisa, etiket):
        self.id, self.olgu, self.kategori, self.metin, self.kisa, self.etiket = id_, olgu, kategori, metin, kisa, etiket
        self.karsit = olgu == "karsit"
        self.parcalar = []
        son = 0
        for m in SLOT.finditer(metin):
            if m.start() > son:
                self.parcalar.append(("m", metin[son:m.start()], None))
            self.parcalar.append(("s", m.group(1), m.group(2)))
            son = m.end()
        if son < len(metin):
            self.parcalar.append(("m", metin[son:], None))
        for p in self.parcalar:
            if p[0] == "s":
                assert p[1] in F or p[1] in KS, (id_, p[1])
                if p[2]:
                    assert p[2] in EKLER, (id_, p[2])
        self.ilk_dolgu = self.parcalar[0][1] if self.parcalar and self.parcalar[0][0] == "s" else None


def _ayristir(olgu, kategori, metin):
    sonuc = []
    for ham in metin.strip().splitlines():
        s = ham.strip()
        if not s:
            continue
        kisa = False
        if s.startswith("* "):
            kisa, s = True, s[2:]
        etiket = None
        if " | " in s:
            etiket, s = s.split(" | ", 1)
            if s.startswith("* "):
                kisa, s = True, s[2:]
        no = len(sonuc) + 1
        sonuc.append(Sablon(f"v2b-{olgu}-{no:03d}", olgu, kategori, s, kisa, etiket))
    return sonuc


def _karsit_ayristir():
    sonuc = []
    for ham in KARSIT.strip().splitlines():
        s = ham.strip()
        if s:
            sonuc.append(Sablon(f"v2b-karsit-{len(sonuc) + 1:03d}", "karsit", None, s, True, None))
    return sonuc


SABLONLAR: dict[str, list[Sablon]] = {o: _ayristir(o, k, m) for o, k, m in OLGULAR}
SABLONLAR["karsit"] = _karsit_ayristir()
TUM_SABLONLAR = [s for lst in SABLONLAR.values() for s in lst]
SABLON_ID = {s.id: s for s in TUM_SABLONLAR}
for _s in TUM_SABLONLAR:
    if _s.etiket:
        ONAYLI.append(tuple(belirteclestir(_s.etiket)))
ONAYLI = sorted(set(ONAYLI))


def ayir_test_sablonlari() -> set[str]:
    """Her olgudan (karşıt dahil) şablonların ≥ %15'i (burada ceil(%18)) teste ayrılır; seçim tohumdan bağımsızdır."""
    rng = random.Random("megazeka-sayi-v2b-bolunme")
    secili: set[str] = set()
    for olgu in sorted(SABLONLAR):
        idler = [s.id for s in SABLONLAR[olgu]]
        secili.update(rng.sample(idler, max(2, math.ceil(TEST_ORANI * len(idler)))))
    return secili


TEST_SABLONLARI = ayir_test_sablonlari()


# ======================================================================================
# Cümle üretimi
# ======================================================================================
SORU_EKLERI = {"mi", "mı", "mu", "mü", "misin", "mısın", "musun", "müsün", "miyiz", "mıyız", "muyuz", "müyüz",
               "miyim", "mıyım", "miyiz"}
_NOKTALAMA = str.maketrans("", "", ".,!?;:\"…'’“”()")
_COK_BOSLUK = re.compile(r" {2,}")


def _temiz(t: str) -> str:
    return t.translate(_NOKTALAMA)


def render(sb: Sablon, rng: random.Random, buyuk: bool, sarmala: bool = True):
    """(girdi, hedef, kategoriler, tasiyici) döndürür. `tasiyici`: varlık yerlerine § konmuş metin."""
    parcalar = []        # (tur, girdi_metni, hedef_metni, tasiyici_metni)
    kullanilan: dict[str, set] = {}
    kats = []
    for tur, ad, ek in sb.parcalar:
        if tur == "m":
            t = ad
            if not buyuk:
                t = _temiz(lower_tr(t))
            parcalar.append(["m", t, t, t])
        elif ad in F:
            havuz = [x for x in F[ad] if x not in kullanilan.setdefault(ad, set())]
            s = rng.choice(havuz)
            kullanilan[ad].add(s)
            if not buyuk:
                s = _temiz(lower_tr(s))
            parcalar.append(["d" + ("z" if ad.startswith("zaman_") else ""), s, s, s])
        else:
            v = KS[ad](rng, ek)
            kats.append(v.kategori)
            parcalar.append(["v", v.sozlu if buyuk else lower_tr(v.sozlu), v.yazili, "§"])
    if sarmala and sb.kisa and not sb.karsit and sb.olgu in VOKATIF_OLGU and rng.random() < VOKATIF_ORANI             and sum(len(p[1].split()) for p in parcalar) <= 4 and not sb.metin.rstrip().endswith(("?", "!")):
        # hitap (vokatif): açılış/kapanış eki değil, kısa cümleye çeşitlilik katar (en çok 5 sözcük)
        havuz = [x for x in F["isim"] if x not in kullanilan.get("isim", set())]
        ad_ = rng.choice(havuz)
        ad_ = ad_ if buyuk else _temiz(lower_tr(ad_))
        ilk = parcalar[0]
        if ilk[0] == "m" and rng.random() < 0.5:
            if buyuk:
                for j in (1, 2, 3):
                    ilk[j] = lower_tr(ilk[j][:1]) + ilk[j][1:]
            sep = ", " if buyuk else " "
            parcalar.insert(0, ["m", ad_ + sep, ad_ + sep, ad_ + sep])
        else:
            sep = ", " if buyuk else " "
            parcalar.append(["m", sep + ad_, sep + ad_, sep + ad_])
    if sarmala and not sb.karsit and not (sb.kisa and sb.olgu in KISA_OLGU):
        ilk = parcalar[0]
        ilk_serbest = (ilk[0] == "m" and sb.olgu != "ozelad") or ilk[0] == "dz"
        if ilk_serbest and rng.random() < SARMA_ACILIS:
            a = rng.choice(ACILISLAR)
            for j in (1, 2, 3):
                ilk[j] = lower_tr(ilk[j][:1]) + ilk[j][1:]
            a = a if buyuk else _temiz(lower_tr(a))
            parcalar.insert(0, ["m", a + ("," if buyuk else "") + " ", a + ("," if buyuk else "") + " ",
                                a + ", "])
        if rng.random() < SARMA_KAPANIS and not sb.metin.rstrip().endswith(("?", "!")):
            c = rng.choice(KAPANISLAR)
            ek_metin = (", " if buyuk else " ") + c + ("?" if buyuk and c.endswith(" mi") else "")
            parcalar.append(["m", ek_metin, ek_metin, ek_metin])
    g = "".join(p[1] for p in parcalar)
    h = "".join(p[2] for p in parcalar)
    ta = "".join(p[3] for p in parcalar)
    if buyuk:
        if g[-1] not in ".?!":
            son = (belirteclestir(g) or [""])[-1]
            nokta = "?" if son in SORU_EKLERI else "."
            g += nokta
            h += nokta
        g, h = ilk_harfi_buyut(g), ilk_harfi_buyut(h)
    g = _COK_BOSLUK.sub(" ", g).strip()
    h = _COK_BOSLUK.sub(" ", h).strip()
    return g, h, kats, ta


def _kisa_siniflandir():
    """Gerçekleşen uzunluğu ≤ 5 sözcük olan negatif şablonlar `kisa` sayılır (sarmalayıcı almaz, kısa havuzda örneklenir)."""
    rng = random.Random("v2b-kisa-sinif")
    for sb in TUM_SABLONLAR:
        if sb.karsit or sb.kisa:
            continue
        olc = sorted(sozcuk_sayisi(render(sb, rng, False, sarmala=False)[0]) for _ in range(9))
        if olc[4] <= 5:
            sb.kisa = True


def sozcuk_sayisi(t: str) -> int:
    return len(t.split())


def kategori_karsit(kats):
    k = set(kats)
    return next(iter(k)) if len(k) == 1 else "karisik"


def tum_cumleler(tekrar: int = 150, seed: int = 7):
    """Her şablondan bol örnek (bölünmeden bağımsız); örnek cümle üretilebilirlik testleri için."""
    rng = random.Random(seed)
    for sb in TUM_SABLONLAR:
        for i in range(tekrar):
            yield sb, render(sb, rng, buyuk=(i % 2 == 0), sarmala=False)


# ======================================================================================
# Bölüm üretimi
# ======================================================================================
_kisa_siniflandir()


class Uretici:
    def __init__(self, seed: int, yasak: set[tuple[str, str]], yasak_hedef: set[str]):
        self.seed = seed
        self.gorulen = yasak
        self.hedefler = yasak_hedef
        self.atilan = Counter()

    def bolum(self, ad: str, n: int) -> list[dict]:
        test = ad == "test"
        rng = random.Random(f"{self.seed}-v2b-{ad}")
        n_karsit = round(KARSIT_ORANI * n)
        n_neg = n - n_karsit
        olgular = [o for o, _, _ in OLGULAR]
        kota = {o: n_neg // len(olgular) for o in olgular}
        ek = olgular[:]
        rng.shuffle(ek)
        for o in ek[: n_neg - sum(kota.values())]:
            kota[o] += 1
        kota["karsit"] = n_karsit
        satirlar: list[dict] = []
        ilk_sayac: Counter = Counter()
        ilk_sinir = int(0.05 * n) + 1
        tavan = max(3, int(0.03 * n)) if n < 2000 else int(0.009 * n)
        for olgu in olgular + ["karsit"]:
            adaylar = [s for s in SABLONLAR[olgu] if (s.id in TEST_SABLONLARI) == test]
            satirlar += self._olgu(olgu, adaylar, kota[olgu], rng, tavan, ilk_sayac, ilk_sinir, n)
        rng.shuffle(satirlar)
        return satirlar

    def _olgu(self, olgu, adaylar, kota, rng, tavan, ilk_sayac, ilk_sinir, n):
        durum = {s.id: [0, 0] for s in adaylar}     # [satır, ardışık başarısızlık]
        kisa = [s for s in adaylar if s.kisa]
        uzun = [s for s in adaylar if not s.kisa]
        p_kisa = 1.0 if olgu == "karsit" else KISA_OLGU.get(olgu, KISA_DIGER.get(olgu, KISA_ORANI))
        if olgu == "onalti":
            tavan = min(tavan, max(3, int(0.028 * kota)))
        satirlar = []
        while len(satirlar) < kota:
            musait_k = [s for s in kisa if durum[s.id][0] < tavan and durum[s.id][1] < 25]
            musait_u = [s for s in uzun if durum[s.id][0] < tavan and durum[s.id][1] < 25]
            if not musait_k and not musait_u:
                raise RuntimeError(f"{olgu}: şablon kapasitesi yetersiz ({len(satirlar)}/{kota}, bölüm n={n})")
            if musait_k and (not musait_u or rng.random() < p_kisa):
                sb = rng.choice(musait_k)
            else:
                sb = rng.choice(musait_u)
            buyuk = rng.random() < BUYUK_HARF_ORANI
            g, h, kats, ta = render(sb, rng, buyuk)
            satir = self._dogrula(sb, g, h, kats, ta, ilk_sayac, ilk_sinir)
            if satir is None:
                durum[sb.id][1] += 1
                continue
            durum[sb.id][1] = 0
            durum[sb.id][0] += 1
            self.gorulen.add((g, h))
            self.hedefler.add(h)
            ilk_sayac[belirteclestir(g)[0]] += 1
            satirlar.append(satir)
        return satirlar

    def _dogrula(self, sb, g, h, kats, ta, ilk_sayac, ilk_sinir):
        if len(g.encode("utf-8")) > BAYT_SINIRI or len(h.encode("utf-8")) > BAYT_SINIRI:
            self.atilan["bayt"] += 1
            return None
        if (g, h) in self.gorulen or h in self.hedefler:
            return None
        ilk = (belirteclestir(g) or [""])[0]
        if ilk_sayac[ilk] >= ilk_sinir:
            self.atilan["ilk_sozcuk"] += 1
            return None
        if sb.karsit:
            if g == h or not re.search(r"\d", h):
                self.atilan["karsit_bicim"] += 1
                return None
            if denetle(ta):
                self.atilan["karsit_tasiyici"] += 1
                return None
            return {"girdi": g, "hedef": h, "kategori": kategori_karsit(kats), "sablon": sb.id}
        if g != h or re.search(r"[\d%]", g):
            self.atilan["negatif_bicim"] += 1
            return None
        ihlal = denetle(g)
        if ihlal:
            self.atilan["denetim:" + sb.id] += 1
            return None
        return {"girdi": g, "hedef": h, "kategori": sb.kategori, "sablon": sb.id}


def uret_hepsi(seed: int, train: int, validation: int, test: int):
    gorulen: set = set()
    hedefler: set = set()
    u = Uretici(seed, gorulen, hedefler)
    sonuc = {}
    for ad, n in (("test", test), ("validation", validation), ("train", train)):   # test önce: sızıntıyı önler
        sonuc[ad] = u.bolum(ad, n)
    return sonuc, u.atilan


# ======================================================================================
# Ölçümler
# ======================================================================================
def olgu_of(sablon_id: str) -> str:
    return sablon_id.split("-")[1]


def olcumler(satirlar: list[dict]) -> dict:
    n = len(satirlar)
    sablon_say = Counter(r["sablon"] for r in satirlar)
    ilk = Counter((belirteclestir(r["girdi"]) or [""])[0] for r in satirlar)
    kisa = sum(1 for r in satirlar if 2 <= sozcuk_sayisi(r["girdi"]) <= 5)
    olgu_say = Counter(olgu_of(r["sablon"]) for r in satirlar)
    olgu_sablon = {o: len({r["sablon"] for r in satirlar if olgu_of(r["sablon"]) == o}) for o in olgu_say}
    deyimler = {SABLON_ID[r["sablon"]].etiket for r in satirlar if olgu_of(r["sablon"]) == "deyim"}
    bin_cekim = set()
    for r in satirlar:
        if olgu_of(r["sablon"]) == "bin":
            bin_cekim.update(t for t in belirteclestir(r["girdi"]) if t.startswith("bin"))
    return {
        "satir": n,
        "sablon_sayisi": len(sablon_say),
        "en_buyuk_sablon_payi": max(sablon_say.values()) / n,
        "en_buyuk_sablon": sablon_say.most_common(1)[0][0],
        "en_buyuk_ilk_sozcuk_payi": ilk.most_common(1)[0][1] / n,
        "en_buyuk_ilk_sozcuk": ilk.most_common(1)[0][0],
        "kisa_2_5_payi": kisa / n,
        "olgu_satir": dict(olgu_say),
        "olgu_sablon": olgu_sablon,
        "ayri_deyim": len({d for d in deyimler if d}),
        "bin_cekim_sayisi": len(bin_cekim),
        "karsit_payi": olgu_say.get("karsit", 0) / n,
        "olgu_kisa_pay": {o: sum(1 for r in satirlar if olgu_of(r["sablon"]) == o and SABLON_ID[r["sablon"]].kisa
                                 and 2 <= sozcuk_sayisi(r["girdi"]) <= 5) / olgu_say[o] for o in olgu_say},
        "olgu_kisa_sablon": {o: len({r["sablon"] for r in satirlar if olgu_of(r["sablon"]) == o
                                     and SABLON_ID[r["sablon"]].kisa}) for o in olgu_say},
        "onalti_en_buyuk_sablon_payi": max(c for k, c in sablon_say.items() if olgu_of(k) == "onalti")
        / olgu_say["onalti"],
    }


def yaz(out: Path, sonuc: dict):
    out.mkdir(parents=True, exist_ok=True)
    for ad, satirlar in sonuc.items():
        with open(out / f"b-{ad}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in satirlar:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v2")
    ap.add_argument("--seed", type=int, default=2202)
    ap.add_argument("--train", type=int, default=10000)
    ap.add_argument("--validation", type=int, default=300)
    ap.add_argument("--test", type=int, default=400)
    a = ap.parse_args(argv)
    sonuc, atilan = uret_hepsi(a.seed, a.train, a.validation, a.test)
    yaz(Path(a.out), sonuc)
    rapor = {ad: {"satir": len(s)} for ad, s in sonuc.items()}
    rapor["train_olcum"] = olcumler(sonuc["train"])
    rapor["atilan"] = dict(atilan.most_common(15))
    print(json.dumps(rapor, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
