"""Pre-registered text edits and anonymized independent visual feedback."""
from pathlib import Path
import ast
import json
import re
import shutil
import subprocess
import sys
import time
from pilot import ROOT,read,config,write_json,call,cpu_environment,current,guard
from model_evidence import compact_structure

EDITOR_INSTRUCTION='把场景中按共同规则标识的工作台/工作桌组合表面改为蓝色 RGBA=(0.02,0.08,0.8,1)，粗糙度0.45；包括其现有父子结构归属的部件。保持目标几何以及所有非目标对象的几何、材质、变换和依赖关系。'

def text_target(structure,scene_id):
    rule=config()['pilot']['text_edit_targets'][scene_id]
    aliases=set(rule['name_tokens'])
    def named(obj):
        normalized=re.sub(r'([a-z])([A-Z])',r'\1_\2',obj['name']).lower()
        return bool(set(re.findall(r'[a-z]+',normalized)) & aliases)
    objects=structure.get('objects',[])
    groups={o['name'] for o in objects if o['type']=='EMPTY' and o.get('parent') is not None and named(o)}
    meshes=[o['name'] for o in objects if o['type']=='MESH' and o.get('finite_nonempty_mesh') and (named(o) or groups.intersection(o.get('parent_chain',[])))]
    return {'object':'predeclared_workbench_assemblies','mesh_names':sorted(meshes),'group_names':sorted(groups),'expected':True,'identity_basis':'Fixed name-token/parent-chain approximation; not semantic ground truth','rule':rule,'missing_target_is_failure':True}

def edit(row):
    folder=Path(row['folder']);dest=folder/'text_edit';dest.mkdir(exist_ok=True)
    if (dest/'status.json').exists():return
    raw_structure=read(folder/'functional/scene_structure.json',{})
    target=text_target(raw_structure,row['scene_id']);write_json(dest/'target_mapping.json',target)
    raw_structure['target']=target
    structure=compact_structure(raw_structure)
    targets=structure.get('target',{}).get('mesh_names',[])
    if not targets:
        write_json(dest/'status.json',{'status':'failed','reason':'required_edit_target_missing'});return
    write_json(dest/'targets.json',targets)
    prompt='You are the frozen Blender Python editor. Do not use tools. Return one complete Python code block that edits the currently open project. bpy is available. Do not open files, access the network, call models, render or save; a fixed external runner handles those. One call, no repair. Instruction: '+EDITOR_INSTRUCTION+'\nTarget mesh names: '+json.dumps(targets)+'\nScene structure: '+json.dumps(structure,ensure_ascii=False)
    started=time.monotonic()
    try:
        response,session=call(prompt,config()['model'],dest/'editor_call',[folder/'final.png'],role='fixed_editor')
        import re
        blocks=re.findall(r'```python\s*\n(.*?)```',response,re.S)
        if not blocks:raise ValueError('No Python code block')
        code=blocks[-1];tree=ast.parse(code)
        for n in ast.walk(tree):
            if isinstance(n,(ast.Import,ast.ImportFrom)):
                names=[x.name.split('.')[0] for x in n.names] if isinstance(n,ast.Import) else [(n.module or '').split('.')[0]]
                if any(x not in ['bpy','math','mathutils'] for x in names):raise ValueError('Editor import outside allowed modules')
            if isinstance(n,ast.Name) and n.id in ['exec','eval','open','__import__']:raise ValueError('Editor forbidden operation')
            if isinstance(n,ast.Attribute) and n.attr in ['save_as_mainfile','render','open_mainfile']:raise ValueError('Editor may not render/save/open')
        (dest/'edit.py').write_text(code);shutil.copy2(folder/'final.png',dest/'before.png');guard('render')
        args=[config()['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python',str(ROOT/'text_edit_worker.py'),'--','--blend',str(folder/'scene.blend'),'--output',str(dest),'--settings',str(ROOT/'config.json'),'--targets',str(dest/'targets.json'),'--code',str(dest/'edit.py')]
        with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
            proc=subprocess.run(args,stdout=out,stderr=err,timeout=config()['blender']['timeout'],env=cpu_environment())
        status={'status':'complete' if proc.returncode==0 else 'failed','exit_code':proc.returncode,'instruction':EDITOR_INSTRUCTION,'seconds':time.monotonic()-started}
    except (ValueError,RuntimeError,OSError,subprocess.TimeoutExpired) as error:
        status={'status':'failed','error':str(error),'instruction':EDITOR_INSTRUCTION,'seconds':time.monotonic()-started}
    write_json(dest/'status.json',status)
    if (dest/'text_edit.json').exists():shutil.copy2(dest/'text_edit.json',folder/'functional/text_edit.json')


def judge(row,index):
    dest=ROOT/'judgments'/f'anon_{index:03d}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'judgment.json').exists():return
    folder=Path(row['folder'])
    if row['status']!='complete':
        write_json(dest/'judgment.json',{'status':'not_evaluated','reason':'no_valid_render'});return
    for src,name in [(folder/'reference.png','input.png'),(folder/'final.png','output.png')]:shutil.copy2(src,dest/name)
    prompt='Independent visual review. Image 1 is the reference; Image 2 is a reconstruction render. You have no method identity, proposal history or scores. Do not use tools. Report visible framing/scale, object omission/occlusion, spatial contact and material differences. Score visible similarity from 0 (none) to 4 (very close) and explain. Treat 3D depth/support interpretations as uncertain visual hypotheses; there is no 3D ground truth. Do not infer invisible geometry correctness. Return JSON with score, observations, uncertain_3d_hypotheses.'
    schema={'type':'object','additionalProperties':False,'properties':{'score':{'type':'integer','minimum':0,'maximum':4},'observations':{'type':'string'},'uncertain_3d_hypotheses':{'type':'string'}},'required':['score','observations','uncertain_3d_hypotheses']}
    try:
        response,session=call(prompt,config()['proposer'],dest/'judge_call',[dest/'input.png',dest/'output.png'],role='independent_judge',schema=schema)
        result={'status':'complete','judgment':json.loads(response),'supplement_only':True}
    except (RuntimeError,ValueError,OSError,subprocess.TimeoutExpired) as error:result={'status':'failed','error':str(error)}
    write_json(dest/'judgment.json',result)
    write_json(dest/'mapping_for_report.json',{k:row[k] for k in ['method','run_id','candidate_id','scene_id']})


def main():
    if read(ROOT/'state.json',{}).get('phase') not in ['main_complete','supplement_complete']:raise RuntimeError('Complete and freeze main comparison first')
    manifest=read(ROOT/'manifest.json');test=[s['scene_id'] for s in manifest if s['split']=='test']
    choices=read(ROOT/'selections.json',[])
    rows=[read(p) for p in (ROOT/'results').glob('*/*/*/test/*/record.json')]
    rows=[row for row in rows if any(row['method']==c['method'] and row['run_id']==c['run_id'] and row['candidate_id']==c['candidate_id'] for c in choices)]
    rows.sort(key=lambda r:(test.index(r['scene_id']),r['run_id'],['fixed_h0','sceneevolve_cli','generic_rsi','scene_rsi_pilot'].index(r['method'])))
    for row in rows:
        if row['scene_id'] in test[:2]:
            if row['status']=='complete':edit(row)
            else:
                dest=Path(row['folder'])/'text_edit';dest.mkdir(exist_ok=True);write_json(dest/'status.json',{'status':'failed','reason':'reconstruction_failed','editor_calls':0})
    for i,row in enumerate(rows,1):judge(row,i)
    write_json(ROOT/'ledger.json',current());write_json(ROOT/'state.json',{'phase':'supplement_complete','time':time.time()})

if __name__=='__main__':main()
