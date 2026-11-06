"""A bounded process runs the actual M; no access to Selection/Test data is passed."""
import argparse,json,sys
from pathlib import Path
from research import ResearchAPI,load_meta
from pilot import cfg,exercise_meta_interface
from data import write_json
p=argparse.ArgumentParser();p.add_argument('mode',choices=['research','contract']);p.add_argument('--request',type=Path,required=True);a=p.parse_args()
r=json.loads(a.request.read_text());folder=Path(r['result_folder'])
if a.mode=='contract':
    result=exercise_meta_interface(Path(r['M_candidate']),r['context'])
    write_json(folder/'M_execution_contract.json',result)
else:
    api=ResearchAPI(cfg(),Path(r['trace_folder']),Path(r['H']),Path(r['M_candidate']),r['scenes'],r['images'])
    try:
        module=load_meta(Path(r['M_program']))
        write_json(folder/'M_program_execution.json',{'program':str(Path(r['M_program'])/'meta.py'),'status':'entered','candidate_type':'research_strategy_program'})
        result=module.research(r['context'],api)
        write_json(folder/'proposal.json',result)
        loaded=[str(Path(m.__file__).resolve()) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(Path(r['M_program']).resolve())]
        write_json(folder/'M_program_execution.json',{'program':str(Path(r['M_program'])/'meta.py'),'status':'completed','loaded_M_helpers':sorted(set(loaded))})
    finally:
        write_json(folder/'worker_summary.json',{'sessions':api.sessions,'frames':api.frames,'actions':api.executed_actions})
