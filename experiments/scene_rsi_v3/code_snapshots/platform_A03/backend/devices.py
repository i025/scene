"""One explicitly authorized idle GPU per Blender child; CPU when busy."""
import json
import os
from pathlib import Path
import subprocess
import time
from processes import cpu_environment


def render_settings(config, folder):
    settings = dict(config['render'])
    policy = config.get('resources', {})
    selection = {'time': time.time(), 'device': 'CPU', 'reason': 'CPU policy',
                 'gpu_uuid': None, 'gpu_index': None, 'gpu_bus_id': None}
    if policy.get('policy') == 'cpu_if_busy' and policy.get('user_authorized_idle_gpu'):
        if any(os.environ.get(k) for k in ('SLURM_JOB_ID', 'PBS_JOBID', 'LSB_JOBID')):
            selection['reason'] = 'Scheduler context changed; no new GPU allocation verified'
        else:
            try:
                inventory = subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid,pci.bus_id,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True, timeout=10)
                processes = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader,nounits'], text=True, timeout=10)
                occupied = {line.split(',')[0].strip() for line in processes.splitlines() if line.strip()}
                observations = []
                for line in inventory.splitlines():
                    index, uuid, bus, memory, utilization = [x.strip() for x in line.split(',')]
                    if uuid not in policy['gpu_allowlist']:
                        continue
                    observations.append({'index': int(index), 'uuid': uuid, 'pci_bus_id': bus,
                                         'memory_used_mib': memory, 'utilization_percent': utilization,
                                         'active_compute_process': uuid in occupied})
                    if selection['device'] == 'CPU' and uuid not in occupied and memory.isdigit() and utilization.isdigit() and int(memory) <= 16 and int(utilization) == 0:
                        selection.update(device='GPU', reason='Authorized device idle at launch',
                                         gpu_uuid=uuid, gpu_index=int(index), gpu_bus_id=bus)
                selection['observations'] = observations
                if selection['device'] == 'CPU':
                    selection['reason'] = 'Authorized GPU pool busy or utilization unavailable; continue CPU'
            except (OSError, subprocess.SubprocessError) as error:
                selection.update(reason='GPU status query failed; continue CPU', error=repr(error))
    settings.update({k: selection[k] for k in ('device', 'gpu_uuid', 'gpu_index', 'gpu_bus_id')})
    settings['gpu_backend'] = policy.get('gpu_backend', 'CUDA')
    settings['gpu_kernel_root'] = policy.get('gpu_kernel_root')
    settings['actual_device_path'] = str(Path(folder) / 'actual_device.json')
    (Path(folder) / 'device_selection.json').write_text(json.dumps(selection, indent=2))
    settings['threads'] = config['resources']['threads_per_blender']
    return settings, cpu_environment(threads=config['resources']['threads_per_blender'],
                                     cuda_visible=selection['gpu_uuid'] or '')


def inspection_config(config, folder):
    settings, environment = render_settings(config, folder)
    path = Path(folder) / 'runtime_config.json'
    path.write_text(json.dumps({**config, 'render': settings}, indent=2))
    return path, environment


def configure_cycles(scene, settings, output=None):
    import bpy
    actual = {'device': 'CPU', 'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES', ''),
              'gpu_uuid': None, 'gpu_index': None, 'enabled_cycles_devices': []}
    use_gpu = settings.get('device') == 'GPU'
    if use_gpu:
        # Scene construction may take minutes after launch. Recheck before GPU work.
        try:
            rows = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader,nounits'], text=True, timeout=10)
            pids = [int(row.split(',')[1].strip()) for row in rows.splitlines()
                    if row.split(',')[0].strip() == settings['gpu_uuid']]
            usage = subprocess.check_output(['nvidia-smi', '--id='+settings['gpu_uuid'], '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True, timeout=10)
            memory, utilization = [int(value.strip()) for value in usage.strip().split(',')]
            own_context = os.getpid() in pids
            other_pids = [pid for pid in pids if pid != os.getpid()]
            use_gpu = not other_pids and (own_context or (memory <= 16 and utilization == 0))
            actual['gpu_idle_recheck'] = {'time': time.time(), 'requested_uuid': settings['gpu_uuid'],
                                         'other_compute_pids': other_pids, 'own_context': own_context,
                                         'memory_used_mib': memory, 'utilization_percent': utilization}
            if not use_gpu:
                actual['cpu_fallback_reason'] = 'Authorized GPU became busy during scene construction'
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            use_gpu = False
            actual['cpu_fallback_reason'] = 'Pre-render GPU query failed: '+repr(error)
    if use_gpu:
        if os.environ.get('CUDA_VISIBLE_DEVICES') != settings['gpu_uuid']:
            raise RuntimeError('Blender CUDA visibility differs from authorized device UUID')
        if settings.get('gpu_kernel_root'):
            import _cycles
            kernel_root = Path(settings['gpu_kernel_root'])
            _cycles.init(str(kernel_root), str(kernel_root / 'cache'), bpy.app.background)
            actual['kernel_root'] = str(kernel_root)
        preferences = bpy.context.preferences.addons['cycles'].preferences
        backend = settings.get('gpu_backend', 'CUDA')
        preferences.compute_device_type = backend
        preferences.refresh_devices()
        available = [d for d in preferences.devices if d.type == backend]
        if len(available) != 1:
            raise RuntimeError('Expected exactly one UUID-isolated GPU device')
        parts = settings['gpu_bus_id'].lower().split(':')
        bus = '0000:' + parts[-2] + ':' + parts[-1].split('.')[0]
        if bus not in available[0].id.lower():
            raise RuntimeError('Cycles PCI device differs from observed authorized GPU')
        for device in preferences.devices:
            device.use = device == available[0]
        scene.cycles.device = 'GPU'
        actual.update(device='GPU', gpu_uuid=settings['gpu_uuid'], gpu_index=settings['gpu_index'],
                      gpu_bus_id=settings['gpu_bus_id'], backend=backend,
                      enabled_cycles_devices=[{'name': available[0].name, 'id': available[0].id, 'type': available[0].type}])
    else:
        scene.cycles.device = 'CPU'
    path = output or settings.get('actual_device_path')
    if path:
        Path(path).write_text(json.dumps(actual, indent=2))
    return actual
