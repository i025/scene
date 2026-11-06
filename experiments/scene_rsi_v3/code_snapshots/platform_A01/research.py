"""Fixed research executor. M owns decisions/actions; evaluation and budgets stay outside."""
import ast, difflib, importlib.util, json, shutil, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from codex_wrapper import call
from data import write_json
from processes import cpu_environment,run_measured
from budget import guard

DECISION_SCHEMA={'type':'object','additionalProperties':False,'properties':{
    'decision':{'type':'string','enum':['action','propose','stop']},
    **{k:{'type':'string'} for k in ['scene_id','action_name','parameters_json','expectation','analysis','scope','new_action_source']},
    'changes':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{
        'target':{'type':'string','enum':['H','M']},'path':{'type':'string'},'content':{'type':'string'},'rationale':{'type':'string'}},
        'required':['target','path','content','rationale']}}},
    'required':['decision','scene_id','action_name','parameters_json','expectation','analysis','scope','new_action_source','changes']}

def sources(folder):
    return {str(p.relative_to(folder)):p.read_text() for p in sorted(folder.rglob('*'))
            if p.is_file() and p.suffix in ['.py','.txt','.md'] and '__pycache__' not in p.parts}

def load_meta(folder):
    sys.path.insert(0,str(folder))
    spec=importlib.util.spec_from_file_location('research_meta_'+str(time.time_ns()),folder/'meta.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def validate_source(text,kind,module_names=()):
    tree=ast.parse(text)
    allowed={'json','re','math','random','statistics','collections','itertools','pathlib','numpy','bpy','bpy_extras','mathutils','sceneact','regression'}|set(module_names)
    forbidden={'exec','eval','compile','open','__import__','getattr','setattr','delattr','globals','locals','breakpoint','input'}
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in n.names] if isinstance(n,ast.Import) else [(n.module or '').split('.')[0]]
            if any(x not in allowed for x in names):raise ValueError('Candidate import outside staged contract: '+str(names))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden:raise ValueError('Candidate execution outside contract')
        if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id in {'api','runtime'}:
            permitted={'ask','remaining','record_decision','create_action','execute_action'} if n.value.id=='api' else {'ask','execute','select','remaining','image'}
            if n.attr not in permitted:raise ValueError('Private fixed runtime access')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='read_text' and kind=='policy.py':
            value=ast.dump(n.func.value)
            valid={ast.dump(ast.parse(x,mode='eval').body) for x in ["Path(__file__).parent / 'system.txt'","Path(__file__).with_name('system.txt')"]}
            if value not in valid:raise ValueError('Only own system file can be read')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'open','read_bytes','write_text','write_bytes','unlink','glob','rglob','iterdir','mkdir','system','popen','connect','render','wm','libraries','load','save','import_scene','import_mesh','export_scene','export_mesh','save_as_mainfile','open_mainfile','read_factory_settings'}:raise ValueError('Candidate filesystem/process/render access outside contract')
        if isinstance(n,ast.Attribute) and n.attr=='read_text' and kind!='policy.py':raise ValueError('Candidate arbitrary filesystem read')
        if isinstance(n,ast.Attribute) and n.attr.startswith('__'):raise ValueError('Candidate introspection outside contract')
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and any(x in n.value for x in ['/home/','/srv/','commons_','bw_00','Final Test']):raise ValueError('Hardcoded private path or task identifier')
    required={'policy.py':'solve','meta.py':'research'}.get(kind)
    if required and not any(isinstance(n,ast.FunctionDef) and n.name==required for n in tree.body):raise ValueError('Missing '+required)

def change_kind(parent_h,parent_m,candidate_h,candidate_m):
    def program(folder,kind):
        return {name:text for name,text in sources(folder).items() if name.endswith('.py') or kind=='H' and name=='system.txt'}
    h=program(parent_h,'H')!=program(candidate_h,'H');m=program(parent_m,'M')!=program(candidate_m,'M')
    return 'H+M' if h and m else 'H-only' if h else 'M-only' if m else 'unchanged'

def m_change_executed(parent,candidate,loaded_helpers,executed_action_sources):
    before,after=sources(parent),sources(candidate)
    changed={name for name in set(before)|set(after) if name.endswith('.py') and before.get(name)!=after.get(name)}
    loaded={str(Path(path).relative_to(candidate)) for path in loaded_helpers}
    tested={name for name in changed if name.startswith('actions/') and after.get(name) in executed_action_sources}
    return {'changed_python_files':sorted(changed),'executed_changed_files':sorted(changed&({'meta.py'}|loaded|tested)),
            'effective_program_change':bool(changed&({'meta.py'}|loaded|tested))}

class ResearchAPI:
    def __init__(self,cfg,folder,h,m,scenes,images):
        self.cfg,self.folder,self.h,self.m,self.scenes,self.images=cfg,folder,h,m,scenes,images
        self.sessions=0;self.frames=0;self.started=time.monotonic();self.decisions=[];self.executed_actions=[]
        folder.mkdir(parents=True,exist_ok=True)
    def remaining(self):
        p=self.cfg['pilot']
        return {'sessions':p['research_sessions_per_round']-self.sessions,
                'diagnostic_frames':p['diagnostic_frames_per_round']-self.frames,
                'seconds':max(0,p['research_seconds_per_round']-(time.monotonic()-self.started))}
    def ask(self,packet):
        if self.remaining()['sessions']<=0 or self.remaining()['seconds']<=0:raise RuntimeError('M research budget exhausted')
        self.sessions+=1
        prompt=('You are the research decision component of the currently executing M strategy. '
                'The attached development references/renders correspond to the explicit packet order. '
                'Return an action decision, a shared H/M proposal with complete file contents, or stop. '
                'Set parameters_json.render=true only when a diagnostic render is needed; custom read-only actions do not render by default. Preserve original author-view aspect. No external tools or hidden model calls. M actions will actually execute in an isolated '
                'Blender scene and their measurements return to your executable M strategy before next '
                'decision. Selection returns aggregates only; Test is inaccessible. '
                'An action run(context) may import bpy/mathutils/math/numpy/json; its current scene is '
                'already loaded. Return JSON-serializable measurements; no file/process/network/render '
                'calls. name is a relative actions/*.py filename. To add reusable action provide its '
                'complete source and applicability. For a proposal target H or M, relative path, full '
                'content and reason. H keeps solve(task,runtime), M keeps research(context,api). '
                'Leave unused strings empty, parameters_json="{}", changes=[] when not proposing.\n'+json.dumps(packet,ensure_ascii=False))
        call_folder=self.folder/'calls'/f'{self.sessions:02d}'
        if (call_folder/'session.json').exists():
            previous=json.loads((call_folder/'session.json').read_text())
            if previous['status']!='completed' or not (call_folder/'response.txt').exists():raise RuntimeError('Existing interrupted/failed model call must not be silently resampled: '+str(call_folder))
            write_json(call_folder/'explicit_replay.json',{'reason':'Resume exact recorded decision; no new model call','time':time.time()})
            return json.loads((call_folder/'response.txt').read_text())
        text,_=call(prompt,self.cfg['proposer'],call_folder,self.images,
                    role='M',timeout=min(self.cfg['proposer']['timeout'],self.remaining()['seconds']),schema=DECISION_SCHEMA)
        return json.loads(text)
    def record_decision(self,decision):
        self.decisions.append(decision)
        write_json(self.folder/'decisions.json',self.decisions)
    def create_action(self,name,source,scope):
        path=Path(name)
        if path.parts[0]!='actions' or path.suffix!='.py' or '..' in path.parts:raise ValueError('Action path must be actions/*.py')
        validate_source(source,'action',[p.stem for p in self.m.rglob('*.py')])
        target=self.m/path;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_text()==source:return
        target.write_text(source)
        index_path=self.m/'actions_index.json'
        index=json.loads(index_path.read_text()) if index_path.exists() else {}
        previous=index.get(name,{'revision':0})
        index[name]={'creator_M':str(self.m),'revision':previous['revision']+1,'scope':scope,'status':'created_pending_reuse'}
        write_json(index_path,index)
        write_json(self.folder/f'created_action_{len(self.decisions):02d}.json',{'name':name,'scope':scope,'creator_M':str(self.m),'source':source,'status':'created_pending_reuse'})
    def execute_action(self,name,scene_id,parameters,expectation):
        scene=self.scenes[scene_id]
        folder=self.folder/'actions'/f'{len(self.executed_actions)+1:02d}';folder.mkdir(parents=True,exist_ok=True)
        if not scene['valid_blend']:
            result={'status':'unavailable','reason':'No valid blend. Diagnose saved execution trace instead.'}
            self.executed_actions.append(result)
            write_json(folder/'observation.json',result);return result
        saved=folder/'observation.json'
        if saved.exists():
            result=json.loads(saved.read_text());self.executed_actions.append(result)
            if result.get('render'):self.images.append(result['render'])
            return result
        action=self.m/name
        if not action.resolve().is_relative_to(self.m.resolve()) or not action.is_file():raise ValueError('Action outside current M')
        validate_source(action.read_text(),'action',[p.stem for p in self.m.rglob('*.py')])
        shutil.copy2(action,folder/'action.py')
        index_path=self.m/'actions_index.json'
        index=json.loads(index_path.read_text()) if index_path.exists() else {}
        provenance=index.get(name,{'creator_M':'unknown','revision':None})
        write_json(folder/'action_request.json',{'action_name':name,'M':str(self.m),'creator_M':provenance['creator_M'],'action_revision':provenance['revision'],'scene_id':scene_id,'parameters':parameters,'expectation':expectation,'source_snapshot':'action.py'})
        requested=[parameters[k] for k in ['object_id','support_id','group_id'] if parameters.get(k)]
        requested+=parameters.get('object_ids',[])
        if any(name not in scene['object_ids'] for name in requested):raise ValueError('Unknown requested object ID')
        ctx={'parameters':parameters,'scene_id':scene_id}
        write_json(folder/'context.json',ctx)
        render=parameters.get('render',name=='actions/intervene.py')
        if render and self.remaining()['diagnostic_frames']<=0:raise RuntimeError('M diagnostic frame cap reached')
        command=[self.cfg['blender']['executable'],'--background','--disable-autoexec','--threads',str(self.cfg['resources']['threads_per_blender']),'--python-exit-code','1','--python',str(ROOT/'action_worker.py'),'--','--blend',scene['blend_path'],'--action',str(action),'--context',str(folder/'context.json'),'--output',str(folder/'measurement.json')]
        if render:
            guard('render');self.frames+=1
            settings={**self.cfg['render'],'threads':self.cfg['resources']['threads_per_blender'],'width':scene['width'],'height':scene['height'],'samples':16,'device':'CPU'}
            write_json(folder/'settings.json',settings);command+=['--render-settings',str(folder/'settings.json')]
        with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
            process=run_measured(command,timeout=min(self.cfg['blender']['timeout'],self.remaining()['seconds']),measurement_path=folder/'process.json',memory_limit_bytes=self.cfg['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=cpu_environment(threads=self.cfg['resources']['threads_per_blender']))
        result={'status':'completed' if process['returncode']==0 else 'failed','measurement':json.loads((folder/'measurement.json').read_text()) if (folder/'measurement.json').exists() else None,'process':process,'render':str(folder/'final.png') if (folder/'final.png').exists() else None,'expectation':expectation,'action':name,'scene_id':scene_id,'M':str(self.m)}
        self.executed_actions.append(result);write_json(folder/'observation.json',result)
        if result['render']:
            result['render_attachment_index']=len(self.images)+1
            self.images.append(result['render'])
            write_json(folder/'observation.json',result)
        return result
