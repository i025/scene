"""Read-only provenance/permissions checks, not reconstruction quality evaluation."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import runner
from data import write_json


def main():
    fixed=runner.read(ROOT/'FROZEN.json');plan=runner.read(ROOT/'plan.json');manifest={x['id']:x for x in runner.read(ROOT/'manifest.json')}
    changed=[p for p in fixed['fixed_files'] if (ROOT/p).read_bytes()!=(ROOT/'code_snapshots/preformal'/p).read_bytes()]
    checks=[]
    for item in plan:
        folder=ROOT/'tasks'/item['task_id'];state=runner.read(folder/'status.json')
        if not state['student_started']:
            checks.append({'task_id':item['task_id'],'started':False});continue
        source=ROOT/manifest[item['scene']]['image_path'];guidance=runner.read(folder/'guidance.json');inputs=runner.read(folder/'student_input.json');context=runner.read(folder/'teacher_context.json')
        teacher=runner.load_teacher(item['teacher']);name='initial_hint' if item['round']==1 else 'update_hint'
        expected=teacher[name](context)
        prompts=list((folder/'teacher_calls/guidance').glob('*/prompt.txt'))
        initial=list((folder/'student_calls/001').glob('*/request.json'))
        initial_inputs=[runner.read(p) for p in initial]
        second=list((folder/'student_calls/002').glob('*/request.json'))
        own_images=True
        for p in second:
            req=runner.read(p)
            own_images &= all(Path(x)==source or Path(x).is_relative_to(folder) for x in req['original_images_for_audit'])
        call_records=[runner.read(p) for p in folder.glob('**/session.json')]
        checks.append({'task_id':item['task_id'],'started':True,
                       'teacher_program_used':bool(prompts) and all(p.read_text()==expected for p in prompts),
                       'S_received_only_final_hint':inputs['hint']==guidance['hint'] and not inputs['previous_reconstruction_artifacts'],
                       'first_call_only_original':bool(initial_inputs) and all(q['original_images_for_audit']==[str(source)] for q in initial_inputs),
                       'second_call_only_own_artifacts':own_images,'fresh_sessions':all(s['fresh_session'] for s in call_records),
                       'no_visible_internal_tools':all(s['tool_calls']==0 for s in call_records),
                       'hint_within_contract':runner.hint_error(guidance['hint'],1200) is None,
                       'within_two_builds':state['build_attempts']<=2,
                       'teacher_initial_memory_empty':context['previous'] is None if item['round']==1 else None,
                       'student_render_review':bool(state['render_attached_for_student_review'])})
    requests=[runner.read(p) for p in (ROOT/'self_modification').glob('**/request.json')]
    no_comparison_images_in_development=all('/sources/E' not in path and '/tasks/E' not in path for q in requests for path in q['original_images_for_audit'])
    output={'scope':'Technical provenance only; no automatic quality evaluation','frozen_files_changed':changed,
            'M1_matches_frozen':(ROOT/'teachers/M1/teacher.py').read_text()==(ROOT/'self_modification/frozen_M1.py').read_text(),
            'self_modification_calls':len(requests),'no_comparison_images_in_self_modification':no_comparison_images_in_development,'tasks':checks}
    write_json(ROOT/'metrics/provenance_audit.json',output)
    keys=['teacher_program_used','S_received_only_final_hint','first_call_only_original','second_call_only_own_artifacts','fresh_sessions','no_visible_internal_tools','hint_within_contract','within_two_builds']
    assert not changed and output['M1_matches_frozen'] and no_comparison_images_in_development
    assert all(all(x[k] for k in keys) for x in checks if x['started'])
    print(json.dumps({'provenance_passed':True,'started_tasks':sum(x['started'] for x in checks),'no_quality_check':True}))

if __name__=='__main__':main()
