"""Fixed-data action reuse checks; no action code, model or Blender is executed."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve()
    sys.path[:0]=[str(root),str(root/'backend')]
    from research import action_reuse_evidence
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    base=args.output.resolve();base.mkdir(parents=True,exist_ok=False)
    parent=base/'parent';parent.mkdir()
    candidate=base/'fixture_program';(candidate/'actions').mkdir(parents=True)
    source='def run(context):\n    return {"measured": True}\n'
    (candidate/'actions/example.py').write_text(source)
    rows=[]
    for name,executions,expected in [
        ('one_scene',[('fixture_a','completed')],False),
        ('two_scenes',[('fixture_a','completed'),('fixture_b','completed')],True),
        ('second_failed',[('fixture_a','completed'),('fixture_b','failed')],False),
    ]:
        trace=base/name;trace.mkdir()
        for index,(scene_id,status) in enumerate(executions,1):
            folder=trace/str(index);folder.mkdir()
            (folder/'action.py').write_text(source)
            write(folder/'observation.json',{'action':'actions/example.py','scene_id':scene_id,'status':status})
        evidence=action_reuse_evidence(parent,candidate,list(trace.iterdir()),{'fixture_a','fixture_b'})
        assert len(evidence)==1 and evidence[0]['pass'] is expected
        rows.append({'test':name,'pass':True,'expected_M_action_eligible':expected,'evidence':evidence})
    shutil.copyfile(__file__,base/'test_driver.py')
    receipt={'status':'passed','fixture_only':True,'new_model_calls':0,'new_Blender_jobs':0,
             'action_execution_count':0,'formal_H_or_M_changed':False,'tests':rows}
    write(base/'tests.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
