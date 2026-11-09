"""Küçük depolama yardımcıları: proje kökü, veri dizini, temel model yükleme, güvenli silme.

Depolama en aza indirilir: yalnızca ``models/checkpoints/best`` ve ``latest`` tutulur.
Temel model (ByT5-small) bu projeye kopyalanmaz; Hugging Face önbelleğinden (veya kardeş proje
Megazeka'nın ``models/base`` klasöründen) salt-okunur yüklenir.
"""
from pathlib import Path
import json
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
TEMEL_MODEL = 'google/byt5-small'
# İsteğe bağlı yerel kopya (ör. kardeş proje Megazeka'nın models/base klasörü).
YEDEK_TEMEL = os.environ.get('MEGAZEKA_SAYI_TEMEL', '')
VERI_ORTAM = 'MEGAZEKA_SAYI_VERI'
KONTROL_NOKTALARI = ROOT / 'models' / 'checkpoints'


def yapilandir():
    """UTF-8 çıktı ve belirteç ayarları. Hugging Face önbelleğini başka yere taşımaz."""
    os.environ['PYTHONUTF8'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    for akis in (sys.stdout, sys.stderr):
        if akis is not None and hasattr(akis, 'reconfigure'):
            akis.reconfigure(encoding='utf-8', errors='replace')


def veri_dizini():
    """``--data-dir``/ortam değişkeni ile değiştirilebilir; varsayılan ``<kök>/data``."""
    return Path(os.environ.get(VERI_ORTAM) or ROOT / 'data')


def veri_oku(ad, dizin=None):
    """``<dizin>/<ad>.jsonl`` satırlarını sözlük listesi olarak döndürür (yoksa FileNotFoundError)."""
    yol = Path(dizin or veri_dizini()) / f'{ad}.jsonl'
    with yol.open(encoding='utf-8') as akis:
        return [json.loads(satir) for satir in akis if satir.strip()]


def boyut(yol):
    yol = Path(yol)
    if not yol.exists():
        return 0
    if yol.is_file():
        return yol.stat().st_size
    return sum(p.stat().st_size for p in yol.rglob('*') if p.is_file())


def kullanim():
    return {'kontrol_noktalari_mb': round(boyut(KONTROL_NOKTALARI) / 1e6, 1),
            'veri_mb': round(boyut(veri_dizini()) / 1e6, 1),
            'raporlar_mb': round(boyut(ROOT / 'reports') / 1e6, 1)}


def butce_kontrol(ek_bayt, islem, sinir=2_000_000_000):
    """Kontrol noktası yazmadan önce diskte yer olduğunu doğrular."""
    if shutil.disk_usage(ROOT).free < ek_bayt + sinir // 4:
        raise RuntimeError(f'Depolama yetersiz: {islem} başlatılmadı.')
    if boyut(KONTROL_NOKTALARI) + ek_bayt > sinir:
        raise RuntimeError(f'Depolama sınırı ({sinir // 10**6} MB) aşılırdı: {islem} başlatılmadı.')


def guvenli_sil(yol):
    """Yalnızca ``models/checkpoints`` altındaki yolları siler."""
    yol = Path(yol).resolve()
    izinli = KONTROL_NOKTALARI.resolve()
    if yol == izinli or not yol.is_relative_to(izinli):
        raise ValueError('Silme yolu models/checkpoints dışında.')
    if yol.is_dir():
        shutil.rmtree(yol)
    elif yol.exists():
        yol.unlink()


def temel_model_yukle(dtype=None):
    """(tokenizer, model, kaynak) döndürür. Hiçbir şey indirmez (local_files_only)."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    hatalar = []
    # Önce yalnız yerel (önbellek / MEGAZEKA_SAYI_TEMEL); bulunamazsa ilk çalıştırmada Hub'dan bir kez indirir (~1,2 GB).
    denemeler = [(k, True) for k in (TEMEL_MODEL, YEDEK_TEMEL) if k] + [(TEMEL_MODEL, False)]
    for kaynak, yerel in denemeler:
        try:
            tok = AutoTokenizer.from_pretrained(kaynak, local_files_only=yerel)
            model = AutoModelForSeq2SeqLM.from_pretrained(kaynak, local_files_only=yerel, dtype=dtype)
            return tok, model, kaynak
        except Exception as hata:  # önbellek eksik/bölünmüş olabilir; sıradaki kaynağı dene
            hatalar.append(f'{kaynak}: {type(hata).__name__}: {str(hata)[:120]}')
    raise RuntimeError('Temel model yüklenemedi:\n' + '\n'.join(hatalar))


if __name__ == '__main__':
    yapilandir()
    print(json.dumps(kullanim(), ensure_ascii=False, indent=2))
