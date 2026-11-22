"""Gerçek 3 kümesinin elle yazılmış etiketleri ve kümeyi kuran betik.

    python evaluation/gercek3_etiket.py --aday <g3-aday.jsonl>

Adaylar `gercek_ornekle.sec` ile seçildi (tohum 20261122, kotalar 10/25/25). Dışlananlar: gercek.jsonl,
gercek2.jsonl ve eğitim/doğrulama/test dosyalarında (cv_duz biçimiyle) geçen her Common Voice cümlesi.
Etiketler v2.5 ve base adayının çıktılarına bakılmadan, SPEC.md, SPEC-v2.md ve SPEC-v3-kararlar.md'ye göre yazıldı
(2026-11-22). `hedef` None ise cümle değişmez. Üçüncü öğe şartnamenin açık bıraktığı durumlarda kabul edilen öteki yazımlardır.
"""
import argparse
import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

E = {
    1: ("kalip", None),
    2: ("aralik", "Senede 7-8 TL'lik mahsul verebilecek olan bir ağaç kökü yarım liraya müşteri bulamıyordu."),
    3: ("kalip", None), 4: ("kalip", None), 5: ("kalip", None), 6: ("kalip", None),
    7: ("atasozu", None), 8: ("kalip", None),
    9: ("kardinal", "Ama adam 50'sinden sonra rakıya vurdu."),
    10: ("atasozu", None),
    11: ("aralik", "Ayağını makineye kaptırmış; eline 40-50 bangonot sıkıştırmışlar, kapı dışarı etmişler."),
    12: ("kardinal", "156."),
    13: ("aralik", "Bir zamanlar herhangi bir arkadaşından 25-50 kuruş borç istemek gündelik işlerdendi."),
    14: ("para", "150 TL'yi avucunda sımsıkı tutarak doğumevine döndü."),
    15: ("para", "Fakat bu sefer hepsine birden 150 TL'den fazla veren çıkmadı."),
    16: ("kardinal", "Arkası olan arkadaşlar ofise, milli korunma kontrolörlüğüne yapışmışlar, gecede 150 papel eziyorlar."),
    17: ("para", "Ben Kemal'e sokuldum, bir 50 kuruş daha uzatarak:"),
    18: ("para", "Bütün ekinimi satsam da kışın aç otursak, gene 50 TL bile denkleştiremem…"),
    19: ("kalip", None),
    20: ("tarih", "Eylül 1930."),
    21: ("kardinal", "137"),
    22: ("kalip", None),
    23: ("para", "Galiba cebimde 35 kuruş kadar bir şey vardı."),
    24: ("kardinal", "Yaşı 35 sularında olabilirdi."),
    25: ("kardinal", "Bu sırada, onları tekrar ve 30 adım kadar ileride gördü."),
    26: ("para", "30 TL'yi nereden mi bulacakmışım?"),
    27: ("kardinal", "Burası benim 30 sene önce gördüğüm, içinde en güzel günlerimi geçirdiğim yer değildi."),
    28: ("aralik", "20-30 adım uzaktan, dişsiz ağzını alabildiğine açarak, bir şeyler bağırıp duruyordu."),
    29: ("kucuk_sayi", None, ["İndiğim handa buldum, 8 kağıt verip aldım."]),
    30: ("tarih", "1928.", ["1.928."]),
    31: ("aralik", "Hele Çirkince… Hele bu 7, 800 hanelik dağ köyü…",
         ["Hele Çirkince… Hele bu 700, 800 hanelik dağ köyü…", "Hele Çirkince… Hele bu 700-800 hanelik dağ köyü…",
          "Hele Çirkince… Hele bu 7-800 hanelik dağ köyü…"]),
    32: ("aralik", "Sıcakta 7-8 saat yol alıyorduk."),
    33: ("kardinal", "Yaşı daha 18 ya var, ya yoktu."),
    34: ("kucuk_sayi", None, ["8 aylık bir çırağın elinden gelebilecek en büyük hüneri gösterdi."]),
    35: ("kardinal", "En büyüğü 18 yaşında beş çocuğu ve bir de karısı vardı."),
    36: ("kardinal", "Ve 18 yaşındaki delikanlı, bundan evvel İzmir’e gidip gelenlerden akıl danışmaya gitti."),
    37: ("kardinal", "128."),
    38: ("atasozu", None), 39: ("atasozu", None), 40: ("atasozu", None),
    41: ("kardinal", "Yolda 40 defa arabayı durdurdu.", ["Yolda kırk defa arabayı durdurdu."]),
    42: ("tarih", "Kasım 1940."),
    43: ("tarih", "11 Şubat 1944."),
    44: ("atasozu", None),
    45: ("kardinal", "45 seneden beri beraber yaşadığı ilk karısı Hacer: \"İki döşek serelim, Kerim Ağa…\""),
    46: ("para", "Öteki doğruldu, inanmaz gözlerle yüzüme bakarak: \"Yedi gazete amuca, 42 kuruş eder!\" dedi."),
    47: ("para", "42 TL ile ev idare olmaz."),
    48: ("kardinal", "Hacer kadın, aradığını bulamadığına kızmışa benziyordu: \"40 sene kahrını çektim…\""),
    49: ("atasozu", None),
    50: ("saat", "Kolundaki saate baktı; 9'a geliyordu."),
    51: ("saat", "Hele sen 9'u 5 dakika geçir de, gör dünyanın kaç bucak olduğunu."),
    52: ("atasozu", None), 53: ("atasozu", None), 54: ("atasozu", None), 55: ("atasozu", None),
    56: ("atasozu", None), 57: ("atasozu", None),
    58: ("tarih", "Şubat 1928."),
    59: ("es_yazim", None, ["Karanlıkta oturup birer parça bazlama ile 3 gün evvelden kalmış birazcık yoğurdu yediler."]),
    60: ("kucuk_sayi", None),
    61: ("es_yazim", None),
    62: ("kardinal", "117."),
    63: ("kardinal", "17 yaşında bir kalbin yüklenemeyeceği ağırlıkları yüklenmiş gibi…"),
    64: ("kardinal", "25 senedir ekmek yediği dükkanın kapısını çekti gitti."),
    65: ("para", "Boyunlarına 7 TL'lik eşarp takan kayınbiraderler ise:"),
    66: ("aralik", "Öndekilerle aralarında, 6-7 adım bir mesafe vardı."),
    67: ("es_yazim", None),
    68: ("atasozu", None),
    69: ("kardinal", "Aynı manasız gülümsemelerle dolu olan 20 dakika bana bir saniye kadar kısa göründü."),
    70: ("aralik", "Uzun uzun, belki 15-20 dakika böyle kaldı."),
    71: ("sira", "Nihayet, 25. günü, onu kürküne sardım, koluna girerek merdivenlerden indirdim.",
         ["Nihayet, yirmi beşinci günü, onu kürküne sardım, koluna girerek merdivenlerden indirdim."]),
    72: ("kardinal", "24 yaşında olduğum halde başımdan hiçbir kadın macerası geçmemişti."),
    73: ("kardinal", "24 yaşma geldiğim halde hâlâ çocukluğumun saflığından kurtulamamıştım."),
    74: ("kardinal", "Haydi, al şu 25'i de, bu hesabı kapayalım…"),
    75: ("kardinal", "O, daha ne olduğunu anlamadan ben mavzeri kapınca 20 adım öteye fırlamıştım."),
    76: ("para", "Olmaz, 20 kuruş!"),
    77: ("kardinal", "Maria Puder, hastanede 25 gün kaldı."),
    78: ("kardinal", "Kamyon, içindeki 22 müşterisiyle beraber sokağa çıkıp biraz ilerledikten sonra durdu."),
    79: ("kucuk_sayi", None, ["Temiz iş 6 ayda çıkar."]),
    80: ("es_yazim", None),
    81: ("kucuk_sayi", None, ["6 senedir koynuna girersin!"]),
    82: ("es_yazim", None),
    83: ("kucuk_sayi", None, ["6 yaşındaki oğlunu oraya yolladı."]),
    84: ("es_yazim", None),
    85: ("para", "6 TL'yi bir denkleştirebilsem verir kurtulurdum ama, bu zamanda 6 TL'nin yolu nerde?"),
    86: ("es_yazim", None),
    87: ("aralik", "Melek yavaşça elindeki çantayı açtı, içinden 4-5 altın bilezikle bir çift küpe aldı."),
    88: ("kucuk_sayi", None, ["Ah birader, bir bilsen, okumaya başladı mı plak değiştirmeden 6 saat söyler…"]),
    89: ("es_yazim", None),
    90: ("kardinal", "3.000 gönüllü Arnavut; bu bir şaka değildi."),
    91: ("kardinal", "Mest etmişti 1.000 kazı.", ["Mest etmişti bin kazı."]),
    92: ("atasozu", None), 93: ("atasozu", None),
    94: ("kardinal", "3.000 kişinin son ferdi, son kurşunuyla efeyi yaralayabilmişti."),
    95: ("es_yazim", None),
    96: ("atasozu", None),
    97: ("es_yazim", None),
    98: ("kalip", None, ["2 günden beri sabahtan akşama kadar içiyor ve binbir türlü planlar kuruyordu."]),
    99: ("kalip", None), 100: ("kalip", None),
    101: ("aralik", "Bu şekilde sevdiklerim hayatla 3-4 kişiden ibarettir."),
    102: ("kucuk_sayi", None),
    103: ("kalip", None),
    104: ("kardinal", "Şöyle bir hesapladım. 14 sene olmuş."),
    105: ("kucuk_sayi", None, ["4 gün uğraştılar…"]),
    106: ("kalip", None),
    107: ("para", "400 TL'ye çocuğunu alırım kardeşim."),
    108: ("kalip", None),
    109: ("kucuk_sayi", None, ["3 hafta önce."]),
    110: ("aralik", "İsa'dan bâhis, 2-3 sene sonra."),
    111: ("kucuk_sayi", None, ["3 saat kadar gittiler."]),
    112: ("kucuk_sayi", None),
    113: ("kalip", None),
    114: ("sira", None, ["2 gecedir uykusuz, bu akşam üçüncü gece olacak…", "İki gecedir uykusuz, bu akşam 3. gece olacak…",
                        "2 gecedir uykusuz, bu akşam 3. gece olacak…"]),
    115: ("kucuk_sayi", None, ["Fakat 3 günden beri bunu da yapamıyordu."]),
    116: ("kucuk_sayi", None, ["3 gün önce."]),
    117: ("kalip", None),
    118: ("atasozu", None),
    119: ("kalip", None),
    120: ("para", "Hatta küçük satıcı artık \"arabalar 5 kuruşa\" diye bağırmayı bile unutmuştu."),
    121: ("kucuk_sayi", None),
    122: ("kucuk_sayi", None, ["Halbuki 5 dakika için bile ondan ayrılmayı kafası almıyordu."]),
    123: ("aralik", "5-10 gün bunu evde yatırdım."),
    124: ("aralik", "5-10 gün oturup dinlenirsin!"),
    125: ("kardinal", "Aradan 15 dakikaya yakın bir zaman geçtiği halde geri gelmedi."),
    126: ("aralik", "Herkes 5-10 adım geri çekildi."),
    127: ("aralik", "Burası, 5-10 hanelik küçük bir zeybek koyu idi."),
    128: ("atasozu", None),
    129: ("es_yazim", None), 130: ("es_yazim", None),
    131: ("olcu", "100 m kadar ötede, gölün kıyısında siyah ve bodur söğütler görünüyordu."),
    132: ("es_yazim", None), 133: ("es_yazim", None), 134: ("es_yazim", None), 135: ("es_yazim", None),
    136: ("kardinal", "Ve senden 100 kat akıllı ve usta adamlar anlattıkları halde, gene beni kandıramıyorlar.",
          ["Ve senden yüz kat akıllı ve usta adamlar anlattıkları halde, gene beni kandıramıyorlar."]),
    137: ("es_yazim", None), 138: ("es_yazim", None),
    139: ("kucuk_sayi", None, ["2 gün evvel çamaşırımı yıkadığı halde bana çamaşırım olup olmadığını sordu…"]),
    140: ("kalip", None),
    141: ("kucuk_sayi", None),
    142: ("kalip", None), 143: ("kalip", None), 144: ("kalip", None),
    145: ("kucuk_sayi", None), 146: ("kucuk_sayi", None),
    147: ("kalip", None), 148: ("kalip", None),
    149: ("zamir", None),
    150: ("kardinal", "Daha 10 adım öteden muharrir Hüseyin beyin sesi geldi:"),
    151: ("atasozu", None),
    152: ("kardinal", "10 gündür de rıhtımda bekliyor, bu sabah mavnaya yüklettim, nerdeyse gemiye yanaşmıştır!"),
    153: ("es_yazim", None),
    154: ("zamir", None),
    155: ("kardinal", "10 sene mi?"),
    156: ("zamir", None),
    157: ("kardinal", "10 gün kadar sonra uzun bir mektup aldım."),
    158: ("es_yazim", None),
    159: ("atasozu", None),
    160: ("kardinal", "Bizim dairede 10 kişi kadar varız…"),
    161: ("zamir", None),
    162: ("kardinal", "Tekrar hızlandı ve gelip geçenlere çarparak 10 adıma kadar yaklaştı."),
    163: ("zamir", None),
    164: ("es_yazim", None),
    165: ("zamir", None),
    166: ("para", "Biraz tereddütten sonra buna bir de 10 kuruşluk kattım, ona verdim."),
    167: ("kalip", None),
    168: ("para", "Bir 10 TL'lik gösterdi."),
    169: ("kardinal", "Evet, bekledim; hem yalnız sonbahara kadar değil, tam 10 sene bekledim."),
    170: ("sira", "Yolun açılışının 10. günü nafıanın fen memurlan vilayete bir rapor vermişler.",
          ["Yolun açılışının onuncu günü nafıanın fen memurlan vilayete bir rapor vermişler."]),
    171: ("es_yazim", None),
    172: ("zamir", None),
    173: ("kardinal", "Belki 10 dakika böyle kaldık."),
}
for _i in range(174, 199):
    E.setdefault(_i, ("kalip", None))
E[183] = ("atasozu", None)


def kur(aday_yolu):
    adaylar = [json.loads(s) for s in Path(aday_yolu).read_text(encoding="utf-8").splitlines() if s.strip()]
    assert len(adaylar) == len(E) and set(E) == set(range(1, len(adaylar) + 1))
    satirlar = []
    for i, r in enumerate(adaylar, 1):
        kat, hedef, *kabul = E[i]
        kabul = kabul[0] if kabul else []
        hedef = r["girdi"] if hedef is None else hedef
        assert hedef not in kabul, i
        o = {"girdi": r["girdi"], "hedef": hedef, "kategori": kat, "sablon": "gercek3-cv", "katman": r["katman"]}
        if kabul:
            o["kabul"] = kabul
        satirlar.append(o)
    return satirlar


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--aday", required=True)
    ap.add_argument("--cikti", default=str(KOK / "evaluation" / "gercek3.jsonl"))
    a = ap.parse_args()
    s = kur(a.aday)
    Path(a.cikti).write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in s), encoding="utf-8")
    print(f"{len(s)} satır, pozitif {sum(o['girdi'] != o['hedef'] for o in s)}, kabullü {sum('kabul' in o for o in s)}")
