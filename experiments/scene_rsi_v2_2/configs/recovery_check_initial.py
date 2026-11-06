"""One bounded service check; not a reconstruction retry or algorithm result."""
from pathlib import Path
import time
import pilot

root=Path(__file__).resolve().parent
dest=root/'configs/service_recovery_once'
if dest.exists():raise RuntimeError('One recovery attempt already exists; no repeated automatic retry')
dest.mkdir()
pause=root/'service_pause.json'
pause.rename(dest/'original_service_pause.json')
image=root/'results/smoke/fixed_h/r1_C2/smoke/old_dev_excluded_smoke/reference.png'
try:
    answer,session=pilot.call('Describe the attached image in one short sentence. Do not use tools.',pilot.config()['proposer'],dest/'call',[image],role='one_bounded_service_recovery_check',timeout=90)
except (RuntimeError,TimeoutError) as error:
    pilot.write_json(dest/'result.json',{'status':'failed','error':str(error),'time':time.time()})
    raise
else:
    pilot.write_json(dest/'result.json',{'status':'completed','answer':answer,'time':time.time(),'resampled_A_tasks':0})
