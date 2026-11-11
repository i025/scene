"""Pure audit of actual report functions; no report, model, or Blender execution."""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import re
import statistics


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    fixture = args.output / 'fixture'
    tree = ast.parse(args.source.read_text())
    functions = {node.name:node for node in tree.body if isinstance(node, ast.FunctionDef)}
    wanted = ['read', 'relative', 'mean', 'evaluator_failure', 'evaluator_revision',
              'get_scenes', 'group_statistics', 'test_repeat_policy']
    namespace = {'ROOT':fixture, 'json':json, 'Path':Path, 'Counter':Counter,
                 'statistics':statistics, 're':re,
                 'TERMINAL':{'completed', 'failed', 'timeout', 'invalid', 'selected', 'rejected', 'unchanged'}}
    exec(compile(ast.Module(body=[functions[name] for name in wanted], type_ignores=[]),
                 str(args.source), 'exec'), namespace)
    current = 'authored_native_project_facts_A03_lighting'
    previous = 'authored_native_project_facts_A02'
    delivery = 'original_delivery_metadata_A02'
    config = {'evaluation':{'native_evidence_version':current},
              'pilot':{'final_test':{'primary_repeats':1}}}
    write(fixture/'config.json', config)
    write(fixture/'configs/selection_repeats.json', {'Hstart':{'s1':2,'s2':1,'s3':1}})
    def row(scene_id, repeat, native, score):
        folder = fixture/f'results/Hstart/selection/{scene_id}/{repeat}'
        data = {'scene_id':scene_id,'split':'selection','H_version':'Hstart','M_version':'M0',
                'repeat':repeat,'status':'completed','valid':True,'folder':str(folder),
                'metrics':{'overall':0.4},'functional':{'functional_pass':True,'checks':{}},
                'bw':{'native_evidence_version':native,'delivery_evidence_version':delivery,
                      'evaluation_status':'completed','S_BW':score,'S_rubric':score,
                      'S_dimension':score,'dimension_scores':[],'rubric_scores':[]}}
        write(folder/'record.json', data)
        return folder, data
    old_folder, old = row('s1',1,previous,20)
    row('s1',2,current,60)
    s2_folder, s2 = row('s2',1,current,70)
    row('s3',1,current,80)
    manifest = [{'scene_id':f's{i}','split':'selection'} for i in range(1,4)]
    manifest += [{'scene_id':f't{i}','split':'test'} for i in range(6)]
    state = {'H_start':'Hstart','H_best':'Hbest','final_selection_frozen':False}
    policy = namespace['test_repeat_policy'](config)
    raw = namespace['get_scenes']()
    primary = [record for record in raw if record['primary_analysis']]
    groups = namespace['group_statistics'](primary,manifest,state,policy)
    assert len(raw)==4 and len(primary)==3
    assert groups[0]['all_scheduled']==3 and groups[0]['execution_success']==3
    assert groups[0]['execution_success_rate_all_scheduled']==1.0
    assert groups[0]['BW_conditional_mean']==70
    retained_old = next(record for record in raw if record['scene_id']=='s1' and record['repeat']==1)
    assert retained_old['BW'] is None and retained_old['record_raw_BW']==20
    assert retained_old['evaluation_status']=='pending_current_evaluation'
    first = {'raw_rows':len(raw),'primary_rows':len(primary),'group':groups[0],
             'old_raw_BW':retained_old['record_raw_BW'],'old_effective_BW':retained_old['BW']}
    s2['bw']['native_evidence_version'] = previous
    write(s2_folder/'record.json',s2)
    rows = namespace['get_scenes']()
    current_s2 = next(record for record in rows if record['scene_id']=='s2')
    assert current_s2['primary_analysis'] and current_s2['BW'] is None and current_s2['record_raw_BW']==70
    mixed = namespace['group_statistics']([record for record in rows if record['primary_analysis']],manifest,state,policy)[0]
    assert mixed['BW_measured']==2 and mixed['evaluation_coverage']==2/3
    assert mixed['execution_success_rate_all_scheduled']==1
    # Execute the actual report assignments, not the file-producing report function.
    report = functions['report']
    pending_targets = {'test_records','test_sources','expected_test','test_finished','test_status'}
    assignments = [node for node in report.body if isinstance(node,ast.Assign)
                   and any(isinstance(target,ast.Name) and target.id in pending_targets for target in node.targets)]
    pending_namespace = {**namespace,'scenes':rows,'manifest':manifest,'state':state,'test_policy':policy}
    exec(compile(ast.Module(body=assignments,type_ignores=[]),str(args.source),'exec'),pending_namespace)
    summary_dict = next(node.value for node in report.body if isinstance(node,ast.Assign)
                        and any(isinstance(target,ast.Name) and target.id=='summary' for target in node.targets))
    rate = next(value for key,value in zip(summary_dict.keys,summary_dict.values)
                if isinstance(key,ast.Constant) and key.value=='test_execution_success_rate_all_scheduled')
    pending_rate = eval(compile(ast.Expression(body=rate),str(args.source),'eval'),pending_namespace)
    assert pending_namespace['test_status']=='pending' and pending_namespace['test_finished']==0 and pending_rate is None
    pending_namespace['state']={**state,'final_selection_frozen':True}
    exec(compile(ast.Module(body=assignments,type_ignores=[]),str(args.source),'exec'),pending_namespace)
    frozen_pending_rate=eval(compile(ast.Expression(body=rate),str(args.source),'eval'),pending_namespace)
    assert pending_namespace['expected_test']==12 and frozen_pending_rate is None
    # Test delivery protocol mismatch against both actual readers.
    s2['bw']['native_evidence_version']=current
    s2['bw']['delivery_evidence_version']='obsolete_delivery'
    write(s2_folder/'record_before_A02_evaluator.json',old)
    write(s2_folder/'record.json',s2)
    mismatched=next(record for record in namespace['get_scenes']() if record['scene_id']=='s2')
    revision=namespace['evaluator_revision'](s2_folder/'record.json')
    delivery_mismatch={'get_scenes_effective_BW':mismatched['BW'],
                       'evaluator_revision_new_BW':revision['new_BW'],
                       'inconsistent_protocol_gate':mismatched['BW'] is not None and revision['new_BW'] is None}
    # A plotting stub records plotted coordinates; it does not import Matplotlib.
    class PlotStub:
        def __init__(self): self.lines=[]
        def plot(self,x,y,*args,**kwargs): self.lines.append({'x':x,'y':y})
        def __getattr__(self,name): return lambda *args,**kwargs: None
    plot=PlotStub()
    write(fixture/'round0.json',{'H':'Hstart','selection':{'S_BW':27.585227272727273}})
    plot_namespace={**namespace,'plt':plot,'figure':lambda *args,**kwargs:None}
    exec(compile(ast.Module(body=[functions['plot_evolution']],type_ignores=[]),str(args.source),'exec'),plot_namespace)
    plot_namespace['plot_evolution']([])
    assert plot.lines[0]['y']==[27.585227272727273]
    results={'status':'pure_checks_completed_with_findings','checks_passed':[
        'three_primary_plus_one_superseded_retained_raw','primary_success_rate_3_of_3_not_4_of_3',
        'A02_score_excluded_under_A03_with_raw_value_retained','old_native_primary_row_is_pending_not_measured',
        'Test_not_started_status_pending_and_rate_null','Test_frozen_but_not_started_rate_null'],
        'three_plus_one':first,'mixed_protocol_primary_group':mixed,
        'pending_Test':{'status':pending_namespace['test_status'],'finished':pending_namespace['test_finished'],
                        'expected_if_frozen':pending_namespace['expected_test'],'rate':frozen_pending_rate},
        'findings':{'delivery_gate_mismatch':delivery_mismatch,
                    'plot_evolution_unversioned_round0_score_is_still_plotted':plot.lines},
        'model_calls':0,'Blender_jobs':0,'main_report_executed':False,'source_modified':False}
    write(args.output/'results.json',results)
    print(json.dumps(results,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
