"""Megazeka-Sayı LoRA eğitimi (ByT5-small + LoRA, bf16). Megazeka eğitim betiğinden uyarlanmıştır.

Kullanım:
    python training/train.py --config configs/medium.json [--resume] [--steps N] [--data-dir DIR]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import argparse
import json
import os
import random
import time

from megazeka_sayi import depolama
from megazeka_sayi.depolama import ROOT

depolama.yapilandir()
import numpy as np
import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from rapidfuzz.distance import Levenshtein

RAPOR = ROOT / 'reports'


def json_yaz(yol, deger):
    gecici = yol.with_suffix('.tmp')
    gecici.write_text(json.dumps(deger, ensure_ascii=False, indent=2), encoding='utf-8')
    for _ in range(30):
        try:
            gecici.replace(yol)
            return
        except PermissionError:
            time.sleep(.05)  # Windows: okuyucu/antivirüs tutamağı kısa süre açık kalabilir
    print('Dosya meşgul; sonraki adımda yazılacak:', yol.name, flush=True)


def kontrol_noktasi_kaydet(model, optimizer, config, durum, ad):
    depolama.butce_kontrol(250_000_000, 'LoRA kontrol noktası: ' + ad)
    ust = ROOT / 'models/checkpoints'
    gecici, hedef = ust / ('temporary-' + ad), ust / ad
    if gecici.exists():
        depolama.guvenli_sil(gecici)
    gecici.mkdir(parents=True)
    model.save_pretrained(gecici, safe_serialization=True)
    json_yaz(gecici / 'training_config.json', config)
    json_yaz(gecici / 'state.json', durum)
    if optimizer is not None:
        torch.save({'optimizer': optimizer.state_dict(), 'random': random.getstate(),
                    'numpy': np.random.get_state(), 'torch': torch.get_rng_state(),
                    'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []},
                   gecici / 'resume.pt')
    if hedef.exists():
        depolama.guvenli_sil(hedef)
    gecici.replace(hedef)


def veri_hazirla(ad, max_bytes):
    satirlar = depolama.veri_oku(ad)
    uygun = [r for r in satirlar if len(r['girdi'].encode()) < max_bytes and len(r['hedef'].encode()) < max_bytes]
    return uygun, len(satirlar) - len(uygun)


def dogrula(model, tokenizer, ornekler, cihaz, max_bytes, grup=32):
    """Açgözlü üretimle tam eşleşme ve CER (doğrulama alt kümesinde)."""
    model.eval()
    model.config.use_cache = True
    sirali = sorted(ornekler, key=lambda r: len(r['girdi']))
    tam = hata = toplam = 0
    with torch.inference_mode():
        for i in range(0, len(sirali), grup):
            parca = sirali[i:i + grup]
            x = tokenizer([r['girdi'] for r in parca], return_tensors='pt', padding=True).to(cihaz)
            cikti = model.generate(**x, max_new_tokens=max_bytes + 8, do_sample=False, num_beams=1)
            for r, tahmin in zip(parca, tokenizer.batch_decode(cikti, skip_special_tokens=True)):
                tam += tahmin == r['hedef']
                hata += Levenshtein.distance(tahmin, r['hedef'])
                toplam += len(r['hedef'])
    model.config.use_cache = False
    model.train()
    return {'tam_eslesme': tam / max(1, len(sirali)), 'cer': hata / max(1, toplam)}


def ana():
    ap = argparse.ArgumentParser(description='Megazeka-Sayı LoRA eğitimi')
    ap.add_argument('--config', default='configs/medium.json')
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--steps', type=int)
    ap.add_argument('--data-dir', help='data/ yerine başka bir veri dizini (ör. duman testi)')
    args = ap.parse_args()
    if args.data_dir:
        os.environ[depolama.VERI_ORTAM] = str(Path(args.data_dir).resolve())
    yol = Path(args.config)
    config = json.loads((yol if yol.is_absolute() else ROOT / yol).read_text(encoding='utf-8'))
    if args.steps:
        config['steps'] = args.steps
    onceki = ROOT / 'models/checkpoints/latest/state.json'
    if args.resume and onceki.exists():
        if json.loads(onceki.read_text(encoding='utf-8'))['step'] >= config['steps']:
            print(f'Hedef {config["steps"]} adım zaten tamamlanmış. Devam için --steps değerini artırın.', flush=True)
            return
    RAPOR.mkdir(exist_ok=True)
    (ROOT / 'models/checkpoints').mkdir(parents=True, exist_ok=True)
    random.seed(config['seed']); np.random.seed(config['seed']); torch.manual_seed(config['seed'])
    cihaz = 'cuda' if torch.cuda.is_available() else 'cpu'
    if cihaz == 'cpu':
        config['batch_size'] = min(config['batch_size'], 2)
    dtype = torch.bfloat16 if cihaz == 'cuda' and torch.cuda.is_bf16_supported() else torch.float32
    tokenizer, model, kaynak = depolama.temel_model_yukle(dtype)
    print(f'Temel model: {kaynak} | hassasiyet {dtype}', flush=True)
    durum = {'step': 0, 'best_score': -1.0, 'bad_evaluations': 0, 'elapsed_seconds': 0, 'examples_processed': 0}
    devam_dizini = ROOT / 'models/checkpoints/latest'
    if args.resume:
        durum = json.loads((devam_dizini / 'state.json').read_text(encoding='utf-8'))
        model = PeftModel.from_pretrained(model, devam_dizini, is_trainable=True)
    else:
        model = get_peft_model(model, LoraConfig(task_type=TaskType.SEQ_2_SEQ_LM, r=config['rank'],
                               lora_alpha=config['rank'] * 2, lora_dropout=.05, target_modules='all-linear'))
    model.to(cihaz)
    model.config.use_cache = False
    parametreler = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(parametreler, lr=config['learning_rate'])
    if args.resume:
        kayit = torch.load(devam_dizini / 'resume.pt', map_location='cpu', weights_only=False)  # yalnız bu proje üretir
        optimizer.load_state_dict(kayit['optimizer'])
        random.setstate(kayit['random']); np.random.set_state(kayit['numpy']); torch.set_rng_state(kayit['torch'])
        if cihaz == 'cuda' and kayit['cuda']:
            torch.cuda.set_rng_state_all(kayit['cuda'])

    max_bytes = config['max_bytes']
    egitim, atilan_e = veri_hazirla('train', max_bytes)
    dogrulama, atilan_d = veri_hazirla('validation', max_bytes)
    alt_kume = random.Random(config['seed']).sample(dogrulama, min(config['eval_ornek'], len(dogrulama)))
    print(f'Veri: eğitim {len(egitim)} (atılan {atilan_e}), doğrulama {len(dogrulama)} (alt küme {len(alt_kume)}, atılan {atilan_d}) | '
          f'dizin {depolama.veri_dizini()}', flush=True)
    kodlu = [(tokenizer(r['girdi']).input_ids, tokenizer(r['hedef']).input_ids) for r in egitim]

    def toplu(satirlar):
        x = tokenizer.pad({'input_ids': [r[0] for r in satirlar]}, return_tensors='pt')
        y = tokenizer.pad({'input_ids': [r[1] for r in satirlar]}, return_tensors='pt')['input_ids']
        y[y == tokenizer.pad_token_id] = -100
        return {**{k: v.to(cihaz) for k, v in x.items()}, 'labels': y.to(cihaz)}

    bilgi = {'mimari': 'ByT5-small + LoRA', 'temel': kaynak, 'aygit': torch.cuda.get_device_name() if cihaz == 'cuda' else 'CPU',
             'hassasiyet': str(dtype), 'egitilebilir_parametre': sum(p.numel() for p in parametreler), 'config': config}
    json_yaz(RAPOR / 'model_info.json', bilgi)
    print(json.dumps(bilgi, ensure_ascii=False), flush=True)

    etkin = config['batch_size'] * config['gradient_accumulation']
    permutasyon, perm_donem = [], -1

    def indeksler(baslangic, adet):
        nonlocal permutasyon, perm_donem
        sonuc = []
        for k in range(baslangic, baslangic + adet):
            donem, i = divmod(k, len(egitim))
            if donem != perm_donem:
                permutasyon = list(range(len(egitim)))
                random.Random(config['seed'] + donem).shuffle(permutasyon)
                perm_donem = donem
            sonuc.append(permutasyon[i])
        return sonuc

    durdur = RAPOR / 'stop-training'
    durdur.unlink(missing_ok=True)
    if not args.resume:
        (RAPOR / 'history.jsonl').write_text('', encoding='utf-8')
    baslangic = time.perf_counter(); onceki_sure = durum['elapsed_seconds']
    adim_sureleri = []; kayiplar = []
    durum_kaydi = dict(durum)
    if cihaz == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    model.train()
    for adim in range(durum['step'] + 1, config['steps'] + 1):
        t0 = time.perf_counter()
        optimizer.zero_grad(set_to_none=True)
        ids = indeksler(durum['examples_processed'], etkin)
        toplam_kayip = 0.0
        for mikro in range(config['gradient_accumulation']):
            secilen = ids[mikro * config['batch_size']:(mikro + 1) * config['batch_size']]
            sonuc = model(**toplu([kodlu[i] for i in secilen]))
            if not torch.isfinite(sonuc.loss):
                raise RuntimeError('Sonlu olmayan eğitim kaybı; en son kontrol noktasından --resume ile devam edilebilir.')
            (sonuc.loss / config['gradient_accumulation']).backward()
            toplam_kayip += sonuc.loss.detach().float().item() / config['gradient_accumulation']
        torch.nn.utils.clip_grad_norm_(parametreler, 1.0)
        # Isınma + kosinüs azalma (lr_min_oran=1.0 → sabit). Adım sayısı artırılırsa devam tutarlı kalır.
        ilerleme = min(1.0, adim / max(1, config['steps']))
        alt = config.get('lr_min_oran', 1.0)
        lr = config['learning_rate'] * min(1.0, adim / max(1, config.get('warmup', 30))) * \
            (alt + (1 - alt) * .5 * (1 + float(np.cos(np.pi * ilerleme))))
        for grup in optimizer.param_groups:
            grup['lr'] = lr
        optimizer.step()
        kayiplar.append(toplam_kayip)
        durum.update(step=adim, examples_processed=durum['examples_processed'] + etkin,
                     elapsed_seconds=onceki_sure + time.perf_counter() - baslangic)
        if cihaz == 'cuda':
            torch.cuda.synchronize()
        adim_sureleri.append(time.perf_counter() - t0)
        if adim % 10 == 0:
            son = adim_sureleri[-100:]
            vram = f' | tepe VRAM {torch.cuda.max_memory_allocated() / 2**30:.2f} GB' if cihaz == 'cuda' else ''
            print(f'Adım {adim}/{config["steps"]} | kayıp {toplam_kayip:.4f} | lr {lr:.2e} | '
                  f'100 adım ≈ {sum(son) / len(son) * 100:.1f}s{vram} | geçen {durum["elapsed_seconds"]:.0f}s', flush=True)
        durum_kaydi = {**durum, 'epoch': durum['examples_processed'] / len(egitim), 'loss': toplam_kayip,
                       'learning_rate': lr, 'total_steps': config['steps'], 'running': True, 'pid': os.getpid()}
        json_yaz(RAPOR / 'training_status.json', durum_kaydi)
        dur = durdur.exists()
        if adim % config['eval_every'] == 0 or adim == config['steps'] or dur:
            olcum = dogrula(model, tokenizer, alt_kume, cihaz, max_bytes)
            puan = olcum['tam_eslesme'] - olcum['cer'] * 1e-3
            iyi = puan > durum['best_score']
            durum['bad_evaluations'] = 0 if iyi else durum['bad_evaluations'] + 1
            if iyi:
                durum.update(best_score=puan, best_step=adim, best_exact_match=olcum['tam_eslesme'], best_cer=olcum['cer'])
                kontrol_noktasi_kaydet(model, None, config, durum, 'best')
            kontrol_noktasi_kaydet(model, optimizer, config, durum, 'latest')
            gecmis = {**durum_kaydi, 'loss': sum(kayiplar) / len(kayiplar), 'metrics': olcum, 'storage': depolama.kullanim()}
            with (RAPOR / 'history.jsonl').open('a', encoding='utf-8') as akis:
                akis.write(json.dumps(gecmis, ensure_ascii=False) + '\n')
            print(f'DOĞRULAMA adım {adim} | tam eşleşme {olcum["tam_eslesme"]:.3f} | CER {olcum["cer"]:.4f} | '
                  f'en iyi adım {durum.get("best_step")} | sabır {durum["bad_evaluations"]}/{config["patience"]}', flush=True)
            kayiplar = []
            if durum['bad_evaluations'] >= config['patience'] or dur:
                print('Durdurma isteği alındı.' if dur else 'Erken durdurma.', flush=True)
                break
    durum_kaydi.update(durum, running=False)
    json_yaz(RAPOR / 'training_status.json', durum_kaydi)
    if cihaz == 'cuda':
        print(f'Tepe VRAM: {torch.cuda.max_memory_allocated() / 2**30:.2f} GB (ayrılan {torch.cuda.max_memory_reserved() / 2**30:.2f} GB)', flush=True)
    print('Eğitim tamamlandı.', flush=True)


if __name__ == '__main__':
    from filelock import FileLock, Timeout
    (ROOT / 'reports').mkdir(exist_ok=True)
    try:
        with FileLock(ROOT / 'reports/training.lock', timeout=0):
            ana()
    except Timeout:
        raise SystemExit('Bu proje için başka bir eğitim zaten çalışıyor.')
