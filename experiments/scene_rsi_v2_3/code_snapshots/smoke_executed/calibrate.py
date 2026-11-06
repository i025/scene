"""Deterministic pre-freeze calibration; no language-model calls."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fixtures import *

source=(ROOT/'fixtures/reference_renderer_evaluator_only.py').read_text()
folder=ROOT/'calibration';folder.mkdir(exist_ok=True)
rows=[]
for variant in [0,1]:
    spec=config(variant,False);good=build(load(ROOT/'fixtures/reference_renderer_evaluator_only.py'),spec)
    reference=signature(good);checks=compare(reference,reference)
    assert all(checks.values()),('legal scene rejected',variant,checks)
    rows.append({'name':'legal_'+str(variant),'expected':'pass','checks':checks,'passed':all(checks.values())})
for i in range(10):
    broken,module,_,_=inject(i,source);path=folder/f'broken_{i}.py';path.write_text(broken)
    spec=config(i%2,False)
    good=build(load(ROOT/'fixtures/reference_renderer_evaluator_only.py'),spec);ref=signature(good)
    state=build(load(path),spec);checks=compare(signature(state),ref)
    assert not all(checks.values()),('Injected error undetected',i,checks)
    rows.append({'name':'injected_'+str(i),'module':module,'expected':'fail','checks':checks,'detected':not all(checks.values())})
write(folder/'calibration.json',{'no_model_calls':True,'rows':rows,'passed':True,'meaning':'Known controlled compiler/edit defects distinguished from two legal scene templates; not natural geometry truth.'})
print('Calibration passed:',len(rows))
