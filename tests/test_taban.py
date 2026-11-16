"""Taban model seçimi (small/base) testleri; model veya ağ gerektirmez."""
import json
import sys
import types

from megazeka_sayi import depolama


def test_mimari_adi():
    assert depolama.mimari_adi() == 'ByT5-small + LoRA'
    assert depolama.mimari_adi('google/byt5-small') == 'ByT5-small + LoRA'
    assert depolama.mimari_adi('google/byt5-base') == 'ByT5-base + LoRA'


def test_kontrol_noktasi_tabani(tmp_path):
    assert depolama.kontrol_noktasi_tabani(tmp_path) == depolama.TEMEL_MODEL  # dosya yok → small
    (tmp_path / 'taban.json').write_text('{"taban": "google/byt5-base"}', encoding='utf-8')
    assert depolama.kontrol_noktasi_tabani(tmp_path) == 'google/byt5-base'
    (tmp_path / 'taban.json').write_text('bozuk', encoding='utf-8')
    assert depolama.kontrol_noktasi_tabani(tmp_path) == depolama.TEMEL_MODEL
    (tmp_path / 'taban.json').write_text(json.dumps({'taban': ''}), encoding='utf-8')
    assert depolama.kontrol_noktasi_tabani(tmp_path) == depolama.TEMEL_MODEL


def _sahte_transformers(monkeypatch, basarili):
    """``basarili``: (kaynak, yerel) çiftleri; öteki denemeler OSError verir. Denemeleri kaydeder."""
    denemeler = []

    def yukle(kaynak, local_files_only=False, **_):
        if (kaynak, local_files_only) not in basarili:
            raise OSError('yok')
        return kaynak

    def tokenizer_yukle(kaynak, local_files_only=False, **kw):
        denemeler.append((kaynak, local_files_only))  # her deneme önce belirteçle başlar
        return yukle(kaynak, local_files_only, **kw)

    sahte = types.ModuleType('transformers')
    sahte.AutoTokenizer = types.SimpleNamespace(from_pretrained=tokenizer_yukle)
    sahte.AutoModelForSeq2SeqLM = types.SimpleNamespace(from_pretrained=yukle)
    monkeypatch.setitem(sys.modules, 'transformers', sahte)
    return denemeler


def test_temel_model_yukle_small_sirasi(monkeypatch):
    monkeypatch.setattr(depolama, 'YEDEK_TEMEL', 'yerel/small')
    monkeypatch.setattr(depolama, 'YEDEK_TEMEL_BASE', 'yerel/base')
    d = _sahte_transformers(monkeypatch, {('yerel/small', True)})
    assert depolama.temel_model_yukle()[2] == 'yerel/small'
    assert d == [('google/byt5-small', True), ('yerel/small', True)]  # base yedeği small'a karışmaz


def test_temel_model_yukle_base_sirasi(monkeypatch):
    monkeypatch.setattr(depolama, 'YEDEK_TEMEL', 'yerel/small')
    monkeypatch.setattr(depolama, 'YEDEK_TEMEL_BASE', 'yerel/base')
    d = _sahte_transformers(monkeypatch, {('yerel/base', True)})
    assert depolama.temel_model_yukle(None, 'google/byt5-base')[2] == 'yerel/base'
    assert d == [('google/byt5-base', True), ('yerel/base', True)]


def test_temel_model_yukle_hub_son_care(monkeypatch):
    monkeypatch.setattr(depolama, 'YEDEK_TEMEL_BASE', '')
    d = _sahte_transformers(monkeypatch, {('google/byt5-base', False)})
    assert depolama.temel_model_yukle(None, 'google/byt5-base')[2] == 'google/byt5-base'
    assert d == [('google/byt5-base', True), ('google/byt5-base', False)]
