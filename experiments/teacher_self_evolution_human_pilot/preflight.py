"""Small deterministic contract tests. No remote model, rendering, or quality test."""
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from PIL import Image
import runner
from data import write_json

ROOT=Path(__file__).resolve().parent

def main():
    config=runner.read(ROOT/'config.json');plan=runner.read(ROOT/'plan.json')
    assert len(plan)==12 and len({p['task_id'] for p in plan})==12
    for p in plan:
        if p['round']==2:assert next(q['order'] for q in plan if q['task_id']==p['task_id'][:-1]+'1')<p['order']
    teacher=runner.load_teacher('M0')
    for f in runner.TEACHER_FUNCTIONS:assert isinstance(teacher[f]({'public_task':'room','previous':None}),str)
    assert runner.hint_error('普通指导',1200) is None
    assert runner.hint_error('甲'*1201,1200)=='over_length'
    assert runner.hint_error('import bpy',1200)=='code_path_or_encoded_payload'
    original=runner.ROOT
    test_results=[]
    class FakeRuntime:
        def __init__(self,task,config,folder):
            import time
            self.folder=folder;self.executions=0;self.calls=0;self.deadline=time.monotonic()+3600
        def save_usage(self):pass
        def remaining(self):return {'model_calls':2-self.calls,'executions':2-self.executions,'seconds':3000}
        def execute(self,code):
            self.executions+=1;f=self.folder/'steps'/f'{self.executions:03d}';f.mkdir(parents=True)
            (f/'build.py').write_text(code)
            ok=code!='FAIL';result={'ok':ok,'step':self.executions,'image':str(f/'final.png') if ok else None,'failure_type':None if ok else 'blender_build_error','error':None if ok else 'fixture','stderr':''}
            write_json(f/'result.json',result)
            if ok:write_json(self.folder/'selected.json',{'step':self.executions})
            return result
    for first,second,decision,expected in [('GOOD','FAIL','revise',1),('GOOD','','keep',1),('FAIL','GOOD','revise',2)]:
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'tasks/X_M0_R1').mkdir(parents=True)
            for name in ['student_prompt.txt','public_task.txt','sceneact_api.txt']:(root/name).write_text((ROOT/name).read_text())
            image=root/'reference.png';Image.new('RGB',(4,3)).save(image)
            calls=[]
            def fake_invoke(prompt,settings,base,images,role,response_schema,**kwargs):
                calls.append({'prompt':prompt,'images':images})
                return {'decision':'build' if len(calls)==1 else decision,'reason':'stub','observation':'stub','code':first if len(calls)==1 else second},{}
            item={'task_id':'X_M0_R1','scene':'X','teacher':'M0','round':1,'order':0}
            with patch.object(runner,'ROOT',root),patch.object(runner,'Runtime',FakeRuntime),patch.object(runner,'invoke',fake_invoke):
                runner.student(item,config,image,{'hint':'自然语言指导'})
            state=runner.read(root/'tasks/X_M0_R1/status.json')
            assert state['selected_step']==expected and state['main_student_calls']==2
            assert len(calls[0]['images'])==1
            assert len(calls[1]['images'])==(2 if first=='GOOD' else 1)
            assert state['restored_checkpoint']==(second=='FAIL')
            test_results.append({'first':first,'second':second,'decision':decision,'selected':expected,'passed':True})
    assert runner.ROOT==original
    write_json(ROOT/'preparation/preflight.json',{'passed':True,'model_calls':0,'blender_calls':0,'synthetic_fixture_only':True,'plan_unique':True,'R2_dependency':True,'teacher_interfaces':True,'hint_contract':True,'student_control_flow':test_results})
    print('Deterministic preflight passed; no model or Blender invocation.')

if __name__=='__main__':main()
