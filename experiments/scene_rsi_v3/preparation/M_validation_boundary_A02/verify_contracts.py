"""Pure A02 contract checks, no model or Blender subprocess."""
import argparse,json,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args();root=a.root.resolve();sys.path[:0]=[str(root),str(root/'backend')]
import pilot,research
from check_data_split import check_split
from data import write_json
checks=[]
assert check_split(root/'manifest.json')['split_counts']['selection']==3;checks.append('fixed source split3Selection,6Test,12dev plus2replay/1unused')
n=3;good={'S_BW':60,'eligible':True,'completed':n,'evaluation_completed':n};bad={'S_BW':99,'eligible':False,'completed':n,'evaluation_completed':n};parent={'S_BW':50,'eligible':False,'completed':n,'evaluation_completed':n}
assert not pilot.decide_h(bad,parent,2.5)[0];assert pilot.decide_h(good,parent,2.5)[0]
service={**parent,'evaluation_completed':n-1};assert not pilot.decide_h(good,service,2.5)[0];checks.append('absolute eligibility independent of failedHstart; missingjudge not recovery')
with tempfile.TemporaryDirectory() as raw:
 temp=Path(raw);old=pilot.ROOT;pilot.ROOT=temp
 write_json(temp/'config.json',{'pilot':{'boundary_case_limit':2,'selection_size':3}})
 assert pilot.request_boundary_case('C01');assert pilot.request_boundary_case('C02');assert pilot.request_boundary_case('C01');assert not pilot.request_boundary_case('C03')
 assert len(json.loads((temp/'selection_boundary_cases.json').read_text()))==2
 pilot.ROOT=old
 checks.append('boundaryallowance two fullpairedcases; resume doesnotreserveagain; no partialthird')
 api=research.ResearchAPI(pilot.cfg(),temp/'trace',temp/'H',temp/'M',{},[])
 try:api.ask({'evidence':'x'*480001})
 except RuntimeError as error:assert 'input-size budget exhausted' in str(error)
 else:raise AssertionError('oversizeMpacketwas submitted')
 assert api.sessions==0 and not list(temp.rglob('request.json'));checks.append('oversizeMprompt stoppedbeforeCLI,notchargedasactualsession')
records=[json.loads((root/'results/historical_r1_C2_start/development'/s['scene_id']/'1/record.json').read_text()) for s in pilot.manifest('development')];panels=[]
for start in range(0,12,3):
 packet,scenes,images=pilot.context_for(records[start:start+3],pilot.H_START,root/'initial_m',1)
 size=len(json.dumps(packet,ensure_ascii=False).encode());assert size<=420000 and len(images)==6
 for entry,record in zip(packet['development'],records[start:start+3]):
  assert [row[0] for row in entry['object_inventory_all']]==[o['name'] for o in record['functional']['structure']['objects']]
  assert entry['BW_preview']['S_BW'] is None
 panels.append({'start':start,'bytes':size,'image_attachments':len(images),'projection':packet['common_evidence_projection']})
checks.append('all four actual three-source panels fit; allobjectIDs retained; historicalBWnotfedtoM')
write_json(Path(__file__).with_name('contracts_A02.json'),{'status':'passed','checks':checks,'panels':panels,'new_CLI':0,'new_Blender':0,'fixture_only':True})
print(json.dumps(checks))
