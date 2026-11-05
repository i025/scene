"""Same shared helper source, images and repair-call cap for both diagnostic strategies."""
from pathlib import Path
import sys,json,ast,difflib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot
SOURCE=ROOT/'tests/fixture_h0.py'
for method in ['fixed_heuristic','scene_rsi_v2_1']:
    dest=ROOT/'tests/diagnosis'/('repair_'+method);dest.mkdir(exist_ok=True)
    if (dest/'candidate.py').exists():continue
    evidence=[];images=[]
    for case in sorted((ROOT/'tests/diagnosis').glob('case*')):
        evidence.append({'scene':case.name,'stage1':pilot.read(case/method/'stage1.json'),'stage2':pilot.read(case/method/'stage2.json')})
        images.extend([str(case/'reference.png'),str(case/'final.png')])
    prompt='Repair the following SHARED fixture transformation helper program using the attached reference/output pairs and executable M decisions. This is an auxiliary controlled test, not reconstruction H0. Preserve API: frame(camera,nominal_lens) sets requested focal length; size(group,nominal_scale) sets requested scale; show(objects,visible) sets render visibility; support(object,contact_z) places local Z at the computed contact; local_material(object,rgba) must change only the target material appearance, preserving unrelated object geometry and material values even with shared mesh/material data. Output complete code only in JSON {code,reason}. Standard bpy/mathutils allowed; no files/tools/network. Do not encode case IDs or object names. The candidate will also execute on unseen nominal values, reordered object names and different sharing.\n'+SOURCE.read_text()+'\n'+json.dumps(evidence)
    schema={'type':'object','additionalProperties':False,'properties':{'code':{'type':'string'},'reason':{'type':'string'}},'required':['code','reason']}
    text,session=pilot.call(prompt,pilot.config()['proposer'],dest/'proposal_call',images,role='controlled_shared_fixture_repair',schema=schema)
    result=json.loads(text);tree=ast.parse(result['code'])
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            modules=[a.name.split('.')[0] for a in n.names] if isinstance(n,ast.Import) else [n.module]
            if any(m not in ['bpy','math','mathutils'] for m in modules):raise ValueError('Fixture candidate import outside contract')
        if isinstance(n,ast.Name) and n.id in ['open','exec','eval','__import__']:raise ValueError('Fixture candidate external access')
    (dest/'candidate.py').write_text(result['code']);pilot.write_json(dest/'rationale.json',result)
    (dest/'changes.diff').write_text(''.join(difflib.unified_diff(SOURCE.read_text().splitlines(True),result['code'].splitlines(True),fromfile='fixture_H0.py',tofile='fixture_H1.py')))
print('TWO_FIXTURE_REPAIR_PROPOSALS_SAVED')
