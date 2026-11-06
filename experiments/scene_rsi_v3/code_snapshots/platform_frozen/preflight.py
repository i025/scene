"""V3 preflight: preserved deterministic tests, real image/model/build checks."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json
from runtime import Runtime
from PIL import Image,ImageOps

def execute_model_code(model):
    source=ROOT/'preparation/model_selection'/model/'host_attempt'
    output=source/'execution';output.mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'config.json').read_text())
    old=json.loads((ROOT.parent/'scene_rsi_v2_4/manifest.json').read_text())
    with Image.open(old[0]['source']['image_path']) as im:
        im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((512,512));im.save(output/'reference.png')
    task={'image':str(output/'reference.png'),'width':im.width,'height':im.height}
    rt=Runtime(task,cfg,output)
    result=rt.execute((source/'build.py').read_text())
    write_json(source/'execution_status.json',result)
    print(json.dumps({'model':model,'ok':result['ok'],'error':result['error']}),flush=True)
    return result['ok']

def contracts():
    from research import load_meta,change_kind,validate_source
    import shutil,tempfile
    from regression import gate
    tests=[]
    for required in [True,False]:
        for applicable in [True,False]:
            for measured in [True,False,None]:
                result=gate(required,applicable,measured)
                assert result['gate_pass']==(not required or applicable and measured is True)
    tests.append({'test':'required_applicable_measured_gate','passed':True,'cases':12})
    class Stub:
        def __init__(self,measure):self.n=0;self.measure=measure;self.observed=[];self.packets=[]
        def remaining(self):return {'sessions':4-self.n,'diagnostic_frames':16,'seconds':100}
        def ask(self,packet):
            self.n+=1
            self.observed.append(packet['observations']);self.packets.append(packet)
            if self.n==1:return {'decision':'action','new_action_source':'','action_name':'actions/inspect_scene.py','scene_id':'devA','parameters_json':'{}','expectation':'Inspect target','changes':[]}
            if packet['observations'][-1]['observation']['distinct']=='ambiguous' and self.n==2:return {'decision':'action','new_action_source':'','action_name':'actions/intervene.py','scene_id':'devB','parameters_json':'{}','expectation':'Distinguish alternative','changes':[]}
            return {'decision':'stop','analysis':'resolved' if self.measure=='resolved' else 'insufficient','changes':[]}
        def record_decision(self,d):pass
        def execute_action(self,*a):return {'status':'completed','distinct':self.measure}
    meta=load_meta(ROOT/'initial_m')
    a,b=Stub('resolved'),Stub('ambiguous');meta.research({},a);meta.research({},b)
    assert a.n==2 and b.n==3 and a.observed[1][0]['observation']['distinct']=='resolved'
    tests.append({'test':'M_observes_action_then_adapts','passed':True,'decision_calls':[a.n,b.n]})
    with tempfile.TemporaryDirectory(dir=ROOT/'preparation') as tmp:
        tmp=Path(tmp);h=tmp/'h';m=tmp/'m';hc=tmp/'hc';mc=tmp/'mc'
        shutil.copytree(ROOT/'fixed_h/historical_r1_C2_start',h);shutil.copytree(ROOT/'initial_m',m)
        shutil.copytree(h,hc);shutil.copytree(m,mc)
        assert change_kind(h,m,hc,mc)=='unchanged'
        text=(mc/'meta.py').read_text().replace("observations = []","observations = []; context = {**context, 'deterministic_stub_descendant': True}")
        (mc/'meta.py').write_text(text)
        assert change_kind(h,m,hc,mc)=='M-only'
        mod=load_meta(mc);stub=Stub('resolved');mod.research({},stub);assert stub.packets[0]['deterministic_stub_descendant']
    tests.append({'test':'M_only_loaded_H_unchanged_and_identical_not_descendant','passed':True,'interpretation':'deterministic fixture, not automatic research descendant'})
    validate_source((ROOT/'initial_m/actions/inspect_scene.py').read_text(),'action')
    tests.append({'test':'open_action_interface_source','passed':True})
    write_json(ROOT/'preparation/contract_tests.json',{'status':'passed','tests':tests})
    print(json.dumps(tests),flush=True)
def final_checks():
    contracts()
    from pilot import validate_candidate,cfg
    from research import ResearchAPI
    c=cfg();validate_candidate(ROOT/'fixed_h/historical_r1_C2_start',ROOT/'initial_m')
    calibration=json.loads((ROOT/'preparation/bw_calibration/calibration.json').read_text())
    assert calibration['completed']==20 and calibration['eval_failed']==0
    smoke=json.loads((ROOT/'preparation/open_m_smoke/attempt_02/worker_summary.json').read_text())
    assert len(smoke['actions'])==2 and all(a['status']=='completed' for a in smoke['actions'])
    assert len({a['scene_id'] for a in smoke['actions']})==2
    assert len({a['action'] for a in smoke['actions']})==1
    folder=ROOT/'preparation/final_contract_checks/attempt_02'
    scene=ROOT/'preparation/model_selection/gpt-6.1-terra/host_attempt/execution'
    facts=json.loads((ROOT/'preparation/bw_calibration/evidence/development_photo/scene_facts.json').read_text())
    with Image.open(scene/'final.png') as im:width,height=im.size
    scenes={'goa':{'valid_blend':True,'blend_path':str(scene/'scene.blend'),'object_ids':[o['object_id'] for o in facts['objects']],'width':width,'height':height}}
    api=ResearchAPI(c,folder,ROOT/'fixed_h/historical_r1_C2_start',ROOT/'initial_m',scenes,[])
    result=api.execute_action('actions/intervene.py','goa',{'operation':'camera_focal','factor':1.001,'render':True},'Known 0.1% focal intervention; preserve original image aspect. Platform test, no diagnosis claim.')
    assert result['status']=='completed'
    with Image.open(result['render']) as im:assert im.size==(width,height)
    native=api.execute_action('actions/ray_depth_mask.py','goa',{'size':8,'render':False},'Native ray/object data executes without a renderer request.')
    assert native['status']=='completed' and native['measurement']['width']==8
    fixture=ROOT/'preparation/functional_fixtures/correct'
    facts=json.loads((ROOT/'preparation/bw_calibration/evidence/correct/scene_facts.json').read_text())
    scenes['fixture']={'valid_blend':True,'blend_path':str(fixture/'scene.blend'),'object_ids':[o['object_id'] for o in facts['objects']],'width':256,'height':256}
    explicit=api.execute_action('actions/regression.py','fixture',{'test':'material_preservation','object_id':'Z_target_part','render':False},'Target must be explicit Z, not alphabetically first A.')
    assert explicit['status']=='completed' and explicit['measurement']['measured_pass'] and explicit['measurement']['target']==['Z_target_part']
    from pilot import decide_h
    parent={'S_BW':50,'eligible':False,'completed':4,'evaluation_completed':4}
    rejected={'S_BW':90,'eligible':False,'completed':4,'evaluation_completed':4}
    assert decide_h(rejected,parent,2.5)[0] is False
    good={'S_BW':60,'eligible':True,'completed':4,'evaluation_completed':4}
    assert decide_h(good,parent,2.5)[0] is True
    service={'S_BW':50,'eligible':False,'completed':4,'evaluation_completed':3}
    assert decide_h(good,service,2.5)[0] is False
    stable={'S_BW':59,'eligible':True,'completed':4,'evaluation_completed':4}
    assert decide_h(good,stable,2.5)[0] is False
    write_json(folder/'final_acceptance.json',{'status':'passed','formal_started':False,'tests':['CPU propagation and measured resources','real Terra image and executable blend','M observation-controlled next decision','real Astra-created action two-scene reuse','M-only execution and unchanged discrimination','BW formula eight dimensions and actual structural route','20 repeated judge calibrations; no missing scores','known geometry/edit bad fixtures detected','H/M staged context excludes test directory and labels','original author aspect preserved in real diagnostic render','native ray depth/mask measurement executes','Explicit regression edit target Z is used','Absolute Selection eligibility and evaluator failure distinction'],'promotion_delta':calibration['promotion_delta_recommendation'],'limitations':['CLI exact model requests and observed routing unknown','No strict unseen-scene independence','No human quality verification','Some intermediate preparation source variants were not separately snapshotted']})
    print('Final V3 platform acceptance passed; formal rounds remain unstarted.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['contracts','model-build','final']);p.add_argument('--model',default='gpt-6.1-terra');a=p.parse_args()
    if a.command=='contracts':contracts()
    elif a.command=='final':final_checks()
    else:raise SystemExit(0 if execute_model_code(a.model) else 1)
