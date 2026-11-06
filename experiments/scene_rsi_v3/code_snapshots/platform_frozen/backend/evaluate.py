import argparse
import time
import resource
from functools import lru_cache
import json
import subprocess
import time
from pathlib import Path
import numpy as np
from PIL import Image
from data import ROOT, load_config, write_json
from processes import cpu_environment, run_measured


def quality(ssim, lpips, dino):
    values = np.array([ssim, lpips, dino], dtype=float)
    if not np.isfinite(values).all(): raise ValueError('Non-finite metric')
    return float((np.clip(ssim, 0, 1) + 1 - np.clip(lpips, 0, 1) +
                  (1 + np.clip(dino, -1, 1)) / 2) / 3)


def zero(reason):
    return {'valid': False, 'ssim': None, 'lpips': None, 'dino': None,
            'psnr': None, 'overall': None, 'error': reason}


@lru_cache(maxsize=2)
def metric_models(device, dino_model, lpips_net, lpips_model_path=None, alexnet_weights=None):
    import lpips
    import torch
    if alexnet_weights:
        weights = Path(alexnet_weights).resolve()
        if not weights.is_file():
            raise FileNotFoundError(weights)
        hub = ROOT.parents[2] / 'work' / 'metric-torch-hub'
        checkpoint = hub / 'checkpoints' / 'alexnet-owt-7be5be79.pth'
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        if not checkpoint.exists():
            checkpoint.symlink_to(weights)
        torch.hub.set_dir(str(hub))
    from transformers import AutoImageProcessor, AutoModel
    perceptual = lpips.LPIPS(net=lpips_net, model_path=lpips_model_path).eval().to(device)
    processor = AutoImageProcessor.from_pretrained(dino_model, local_files_only=True)
    encoder = AutoModel.from_pretrained(dino_model, local_files_only=True).eval().to(device)
    return perceptual, processor, encoder


def validate_blend(blend, output_dir, config):
    report = output_dir / 'validated.json'
    report.unlink(missing_ok=True)
    command = [config['blender']['executable'], '--background', '-noaudio', '--factory-startup',
               '--disable-autoexec', '--threads', str(config['resources']['threads_per_blender']), '--python-exit-code', '1', '--python', str(ROOT / 'render.py'),
               '--', '--scene', str(blend), '--output-dir', str(output_dir), '--validate-only']
    with (output_dir / 'validation.log').open('w') as log:
        measured = run_measured(command, stdout=log, stderr=subprocess.STDOUT,
                                timeout=config['blender']['build_timeout'],
                                measurement_path=output_dir / 'validation_process.json',
                                memory_limit_bytes=int(config['resources']['memory_limit_gb'] * 1024 ** 3),
                                env=cpu_environment(threads=config['resources']['threads_per_blender']))
    return measured['returncode'] == 0 and not measured['timed_out'] and report.exists()


def score(reference, output_dir, config):
    output_dir = Path(output_dir)
    try:
        blend, png = output_dir / 'scene.blend', output_dir / 'final.png'
        if not blend.is_file() or not png.is_file():
            return zero('Missing scene.blend or final.png')
        with blend.open('rb') as stream:
            header = stream.read(7)
            if not (header == b'BLENDER' or header.startswith(b'\x28\xb5\x2f\xfd') or header.startswith(b'\x1f\x8b')):
                return zero('Invalid Blender project header')
        with Image.open(reference) as image:
            ref = image.convert('RGB')
            ref.load()
        with Image.open(png) as image:
            pred = image.convert('RGB')
            pred.load()
        if ref.size != pred.size: return zero('Rendered dimensions differ from input')
    except (OSError, ValueError) as error:
        return zero(str(error))
    if not validate_blend(blend, output_dir, config):
        return zero('Blender project cannot be loaded or lacks geometry/camera')
    # Missing weights/dependencies or device failures are infrastructure errors;
    # let them propagate so they cannot silently select a harness on false scores.
    import torch
    torch.set_num_threads(config['resources']['threads_per_metric'])
    from skimage.metrics import structural_similarity
    device = config['metrics']['device']
    started = time.monotonic()
    cache_hits = metric_models.cache_info().hits
    timing_path=output_dir/'metric_timing.jsonl'
    started_load=time.monotonic();prior_hits=metric_models.cache_info().hits
    perceptual, processor, encoder = metric_models(device, config['metrics']['dino_model'], config['metrics']['lpips_net'],
                                                   config['metrics'].get('lpips_model_path'), config['metrics'].get('alexnet_weights'))
    with timing_path.open('a') as stream:stream.write(json.dumps({'stage':'metric_model_load','time':time.time(),'seconds':time.monotonic()-started_load,'cache_hit':metric_models.cache_info().hits>prior_hits})+'\n')
    compute_started=time.monotonic();cpu_started=resource.getrusage(resource.RUSAGE_SELF)
    load_seconds = time.monotonic() - started
    cache_hit = metric_models.cache_info().hits > cache_hits
    started = time.monotonic()
    a, b = np.asarray(ref), np.asarray(pred)
    small = min(a.shape[:2])
    if small < 3: return zero('Image too small for SSIM')
    win = min(7, small if small % 2 else small - 1)
    ssim = float(structural_similarity(a, b, channel_axis=2, data_range=255, win_size=win))
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    # null represents +infinity in JSON for identical images.
    psnr = float(10 * np.log10(255 ** 2 / mse)) if mse else None
    def tensor(image):
        return torch.from_numpy(np.asarray(image).copy()).permute(2, 0, 1).unsqueeze(0).float().to(device) / 127.5 - 1
    with torch.inference_mode():
        ta, tb = tensor(ref), tensor(pred)
        if min(ta.shape[-2:]) < 64:
            ta = torch.nn.functional.interpolate(ta, size=(64,64), mode='bilinear', align_corners=False)
            tb = torch.nn.functional.interpolate(tb, size=(64,64), mode='bilinear', align_corners=False)
        distance = float(perceptual(ta, tb).item())
        inputs = processor(images=[ref, pred], return_tensors='pt').to(device)
        features = encoder(**inputs).last_hidden_state[:, 0]
        similarity = float(torch.nn.functional.cosine_similarity(features[:1], features[1:]).item())
    cpu_finished=resource.getrusage(resource.RUSAGE_SELF)
    with timing_path.open('a') as stream:stream.write(json.dumps({'stage':'metric_compute','time':time.time(),'seconds':time.monotonic()-compute_started,'cpu_user_seconds':cpu_finished.ru_utime-cpu_started.ru_utime,'cpu_system_seconds':cpu_finished.ru_stime-cpu_started.ru_stime,'peak_parent_rss_kib':cpu_finished.ru_maxrss,'scope':'numeric metric process itself; Blender/CLI tree separately measured'})+'\n')
    return {'valid': True, 'ssim': ssim, 'lpips': distance, 'dino': similarity,
            'psnr': psnr, 'overall': quality(ssim, distance, similarity),
            'metric_timing': {'model_load_seconds': load_seconds, 'compute_seconds': time.monotonic() - started,
                              'model_cache_hit': cache_hit,
                              'threads': config['resources']['threads_per_metric']}}


def aggregate(results):
    if not results:
        raise ValueError('Cannot aggregate empty results')
    completed = [row for row in results if row['valid'] and row['overall'] is not None]
    def mean_metric(key):
        measured = [row[key] for row in completed if row[key] is not None]
        return sum(measured) / len(measured) if measured else None
    return {'overall': mean_metric('overall'),
            'valid_rate': len(completed) / len(results),
            'all_scheduled': len(results), 'completed_valid': len(completed),
            'e2e_utility': sum(row['overall'] for row in completed) / len(results),
            **{key: mean_metric(key) for key in ('ssim', 'lpips', 'dino')}}


def check_models(reference, config):
    import torch
    torch.set_num_threads(config['resources']['threads_per_metric'])
    device = config['metrics']['device']
    perceptual, processor, encoder = metric_models(device, config['metrics']['dino_model'], config['metrics']['lpips_net'],
                                                 config['metrics'].get('lpips_model_path'), config['metrics'].get('alexnet_weights'))
    with Image.open(reference) as image:
        image = image.convert('RGB')
        image.thumbnail((256, 256))
        if min(image.size) < 64:
            image = image.resize((64, 64))
        tensor = torch.from_numpy(np.asarray(image).copy()).permute(2, 0, 1).unsqueeze(0).float().to(device) / 127.5 - 1
        with torch.inference_mode():
            distance = float(perceptual(tensor, tensor).item())
            features = encoder(**processor(images=[image], return_tensors='pt').to(device)).last_hidden_state[:, 0]
    return {'status': 'passed', 'device': device, 'lpips_self_distance': distance,
            'dino_feature_shape': list(features.shape), 'dino_finite': bool(torch.isfinite(features).all()),
            'reference': str(reference), 'formal_experiment_score': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--image', required=True)
    parser.add_argument('--check-models', action='store_true')
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    if args.check_models:
        write_json(args.output_dir / 'model_load_test.json', check_models(args.image, load_config(args.config)))
    else:
        write_json(args.output_dir / 'image_metrics.json', score(args.image, args.output_dir, load_config(args.config)))
