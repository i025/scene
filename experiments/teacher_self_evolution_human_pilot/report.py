"""Offline human review of actual artifacts; never imports any evaluator/model."""
import csv
import difflib
import html
import json
from pathlib import Path
import sys
from collections import Counter
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json
from budget import current


def read(path):return json.loads(path.read_text())
def esc(text):return html.escape(str(text))


def csv_write(path, rows, fields):
    with path.open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for row in rows:writer.writerow({key:'null' if row.get(key) is None else row[key] for key in fields})


def generate():
    plan=read(ROOT/'plan.json');manifest=read(ROOT/'manifest.json');mapping=read(ROOT/'display_mapping.json')
    reports=ROOT/'reports';reports.mkdir(exist_ok=True);metrics=ROOT/'metrics';metrics.mkdir(exist_ok=True)
    rows=[]
    for item in plan:
        folder=ROOT/'tasks'/item['task_id'];path=folder/'status.json'
        row=read(path) if path.exists() else {**item,'status':'not_started','student_started':False}
        sessions=[read(p) for p in folder.glob('**/session.json')]
        row={**row,'cli_sessions':len(sessions),'known_input_tokens':sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'),int)),
             'known_output_tokens':sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'),int)),
             'unknown_usage_sessions':sum(s.get('input_tokens') is None for s in sessions),
             'reviewed_intermediate_render':bool(row.get('render_attached_for_student_review',[])) if row['status'] in {'completed','failed'} else None}
        rows.append(row)
    fields=['task_id','scene','teacher','round','status','student_started','selected_step','build_attempts',
            'main_student_calls','restored_checkpoint','final_seen_by_student','failure_reason','internal_failure',
            'seconds','cli_sessions','known_input_tokens','known_output_tokens','unknown_usage_sessions','reviewed_intermediate_render']
    csv_write(metrics/'tasks.csv',rows,fields);write_json(metrics/'tasks.json',rows)
    chains=[]
    for item in plan:
        folder=ROOT/'tasks'/item['task_id'];guidance=folder/'guidance.json'
        if not guidance.exists():continue
        g=read(guidance);previous=ROOT/'tasks'/f"{item['scene']}_{item['teacher']}_R1"/'guidance.json'
        difference=''
        if item['round']==2 and previous.exists():
            difference=''.join(difflib.unified_diff(read(previous)['hint'].splitlines(True),g['hint'].splitlines(True),fromfile='R1 language hint',tofile='R2 language hint'))
        context=read(folder/'teacher_context.json')
        chains.append({'task_id':item['task_id'],'teacher':item['teacher'],'function':g['function'],
                       'hint_characters':g['characters'],'previous_render_attachment':context['result_attachment'],
                       'observations':g['observations'],'correction_record':g['correction_record'],
                       'change_reason':g['change_reason'],'hint_diff':difference})
    write_json(metrics/'guidance_chains.json',chains)
    csv_write(metrics/'guidance_chains.csv',chains,['task_id','teacher','function','hint_characters','previous_render_attachment','observations','correction_record','change_reason','hint_diff'])
    sessions=[]
    for base in [ROOT/'tasks',ROOT/'self_modification']:
        for path in base.glob('**/session.json'):
            s=read(path);sessions.append({**s,'path':str(path.relative_to(ROOT)),
                'image_attachments':len(s['original_images_for_audit']),**s['observable_tool_counts']})
    csv_write(metrics/'cli_calls.csv',sessions,['path','role','requested_model','observed_model','reasoning_effort','status','seconds',
              'input_tokens','output_tokens','cached_input_tokens','observable_cli_turns','tool_calls',
              'image_attachments','command_execution','file_change','image_view','collab_tool_call',
              'observable_model_requests_lower_bound','exact_model_requests','cost_usd'])
    costs=[]
    for role in sorted({s['role'] for s in sessions}):
        selected=[s for s in sessions if s['role']==role]
        costs.append({'role':role,'sessions':len(selected),'completed':sum(s['status']=='completed' for s in selected),
                      'seconds_sum':sum(s.get('seconds',0) for s in selected),
                      'known_input_tokens':sum(s['input_tokens'] for s in selected if isinstance(s.get('input_tokens'),int)),
                      'known_output_tokens':sum(s['output_tokens'] for s in selected if isinstance(s.get('output_tokens'),int)),
                      'usage_unknown':sum(s.get('input_tokens') is None for s in selected),
                      'exact_model_requests':None,'cost_usd':None})
    csv_write(metrics/'cost_by_role.csv',costs,['role','sessions','completed','seconds_sum','known_input_tokens','known_output_tokens','usage_unknown','exact_model_requests','cost_usd'])
    timing=[]
    for base in [ROOT/'tasks',ROOT/'self_modification']:
        for p in base.glob('**/*process.json'):
            x=read(p);timing.append({**x,'path':str(p.relative_to(ROOT))})
    csv_write(metrics/'timing.csv',timing,['path','status','seconds','cpu_user_seconds','cpu_system_seconds',
                   'peak_individual_rss_kib','sampled_peak_tree_rss_kib_lower_bound','timed_out'])
    stage_costs=[]
    for stage in ('student_cli','teacher_cli','self_modification_cli','blender_build','blender_render'):
        selected=[]
        for x in timing:
            path=x['path']
            actual=('blender_build' if path.endswith('/build_process.json') else
                    'blender_render' if path.endswith('/render_process.json') else
                    'self_modification_cli' if path.startswith('self_modification/') else
                    'teacher_cli' if '/teacher_calls/' in path else 'student_cli')
            if actual==stage:selected.append(x)
        stage_costs.append({'stage':stage,'processes':len(selected),
             'wall_seconds_sum':sum(x['seconds'] for x in selected if 'seconds' in x),
             'cpu_user_seconds_sum':sum(x['cpu_user_seconds'] for x in selected if x.get('cpu_user_seconds') is not None),
             'cpu_system_seconds_sum':sum(x['cpu_system_seconds'] for x in selected if x.get('cpu_system_seconds') is not None),
             'cpu_measurement_count':sum(x.get('cpu_user_seconds') is not None for x in selected),
             'peak_individual_rss_kib':max((x['peak_individual_rss_kib'] for x in selected if x.get('peak_individual_rss_kib') is not None),default=None)})
    csv_write(metrics/'cost_by_stage.csv',stage_costs,['stage','processes','wall_seconds_sum','cpu_user_seconds_sum',
              'cpu_system_seconds_sum','cpu_measurement_count','peak_individual_rss_kib'])
    builds=[]
    for p in sorted((ROOT/'tasks').glob('*/steps/*/result.json')):
        result=read(p);lines=[line for line in result['stderr'].splitlines() if line.strip()]
        builds.append({'task_id':p.parents[2].name,'step':result['step'],'ok':result['ok'],
                       'failure_type':result['failure_type'],'seconds':result['seconds'],
                       'exception_summary':lines[-1] if lines and not result['ok'] else None,
                       'raw_record':str(p.relative_to(ROOT))})
    csv_write(metrics/'build_attempts.csv',builds,['task_id','step','ok','failure_type','seconds','exception_summary','raw_record'])
    summary={'planned':12,'started':sum(r['student_started'] for r in rows),'delivered':sum(r['status']=='completed' for r in rows),
             'statuses':dict(Counter(r['status'] for r in rows)),
             'build_attempts':sum(r.get('build_attempts',0) for r in rows),'budget':current(),
             'automatic_quality_evaluation':False,'human_quality_verdict':None,
             'student_reviewed_render_tasks':sum(r['reviewed_intermediate_render'] is True for r in rows),
             'internal_build_failures':sum(not read(p)['ok'] for p in (ROOT/'tasks').glob('*/steps/*/result.json'))}
    write_json(metrics/'summary.json',summary)
    by_id={r['task_id']:r for r in rows}
    figures=ROOT/'figures';figures.mkdir(exist_ok=True)
    for split,columns in [('development',3),('comparison',5)]:
        sources=[s for s in manifest if s['split']==split]
        sheet=Image.new('RGB',(columns*420,len(sources)*360),'#f4f5f7');draw=ImageDraw.Draw(sheet)
        for row_index,s in enumerate(sources):
            sid=s['id'];panels=[(ROOT/s['image_path'],sid+' Reference','original')]
            aliases={'M0':'M0'} if split=='development' else mapping[sid]
            for alias,teacher in aliases.items():
                for n in (1,2):
                    tid=f'{sid}_{teacher}_R{n}';record=by_id[tid]
                    panels.append((ROOT/'tasks'/tid/'final.png',f'{sid} {alias} R{n}',record['status']))
            for col,(path,label,status) in enumerate(panels):
                x=col*420;y=row_index*360;draw.text((x+12,y+9),label+' | '+status,fill='#202a35')
                if path.exists():
                    with Image.open(path) as source_image:im=ImageOps.contain(source_image.convert('RGB'),(404,310))
                    sheet.paste(im,(x+(420-im.width)//2,y+35+(310-im.height)//2))
                else:draw.text((x+20,y+130),'No delivered render: '+status,fill='#803030')
        sheet.save(figures/f'{split}_contact.png')

    def picture(path,label,reference=None):
        link='../'+str(path.relative_to(ROOT))
        attrs=f' data-render="{esc(link)}" data-reference="{esc(reference)}"' if reference else ''
        return f'<figure><figcaption>{esc(label)}</figcaption><a href="{esc(link)}" target="_blank"><img src="{esc(link)}"{attrs} alt="{esc(label)}" loading="lazy"></a></figure>'

    def task_card(sid,version,n,label):
        tid=f'{sid}_{version}_R{n}';row=by_id[tid];folder=ROOT/'tasks'/tid
        reference='../sources/'+sid+'.jpg'
        if row['status']=='completed':media=picture(folder/'final.png',label,reference)
        else:media=f'<figure><figcaption>{esc(label)}</figcaption><div class="missing">{esc(row["status"])}<p>{esc(row.get("failure_reason") or "尚无交付")}</p></div></figure>'
        media+=f'<div class="identity" hidden>{esc(tid)} · {esc(version)}</div>'
        if row['status']=='completed':
            media+='<p>学生内部看图：'+('有实际渲染附件' if row['reviewed_intermediate_render'] else '无；首建错误修复后交付，无第三次调用')+'</p>'
        detail=[]
        for name,title in [('guidance.json','实际交付 Hint / 观察 / 更新原因'),('guidance_draft.json','原始指导草稿'),('teacher_context.json','教师允许看到的本题上下文'),('status.json','执行事实')]:
            p=folder/name
            if p.exists():detail.append(f'<h4>{title}</h4><pre>{esc(p.read_text())}</pre>')
        for p in sorted((folder/'steps').glob('*/result.json')):
            step=p.parent;detail.append(f'<h4>内部构建 {esc(step.name)}</h4>')
            if (step/'final.png').exists():detail.append(picture(step/'final.png','内部 checkpoint '+step.name))
            detail.append(f'<a href="../{esc(str((step/"build.py").relative_to(ROOT)))}">实际场景程序</a><pre>{esc(p.read_text())}</pre>')
        for p in sorted(folder.glob('**/session.json')):
            session=read(p);relative=str(p.parent.relative_to(ROOT))
            detail.append(f'<p>{esc(session["role"])} · {esc(session["status"])} · {esc(session.get("seconds"))}秒 · 请求模型 {esc(session["requested_model"])} / 观测路由 {esc(session.get("observed_model","unknown"))}</p>'
                          f'<a href="../{esc(relative)}/prompt.txt">完整提示</a> · <a href="../{esc(relative)}/response.txt">最终回复</a> · <a href="../{esc(relative)}/session.json">usage及可观察事件计数</a>')
        return '<article>'+media+'<details><summary>展开指导、内部版本与执行记录（包含身份）</summary>'+''.join(detail)+'</details></article>'

    sections=[]
    for source in manifest:
        sid=source['id'];ref=ROOT/source['image_path']
        cards=picture(ref,'参考原图 '+sid)
        if source['split']=='development':
            cards+=''.join(task_card(sid,'M0',n,f'M0 第{n}轮从零重建') for n in (1,2))
        else:
            for alias in ('A','B'):
                cards+=''.join(task_card(sid,mapping[sid][alias],n,f'{alias} 第{n}轮从零重建') for n in (1,2))
        controls='<button onclick="toggleImages(this,true)">本组同步看原图</button> <button onclick="toggleImages(this,false)">恢复各自渲染</button>'
        opinion=''
        if source['split']=='comparison':
            opinion=f'<label>可选人工意见：<select data-scene="{sid}"><option value="">尚未判断</option><option>A更好</option><option>B更好</option><option>差不多</option><option>无法判断</option></select></label><textarea data-scene="{sid}" placeholder="可选备注；仅保存在本页，点击导出保存"></textarea>'
        sections.append(f'<section><h2>{sid} · {"开发" if source["split"]=="development" else "冻结后比较"}</h2>{controls}<div class="grid">{cards}</div>{opinion}<details><summary>原图来源与历史暴露</summary><pre>{esc(json.dumps(source,ensure_ascii=False,indent=2))}</pre><a href="{esc(source["source_page"])}">原始来源</a> · <a href="{esc(source["license_url"])}">{esc(source["license"])}</a></details></section>')
    diff=ROOT/'self_modification/M0_to_M1.diff'
    changes=diff.read_text() if diff.exists() else '尚未产生 M1。'
    table='<tr>'+''.join(f'<th>{esc(f)}</th>' for f in fields[:10])+'</tr>'
    for row in rows:table+='<tr>'+''.join(f'<td>{esc(row.get(f,"—"))}</td>' for f in fields[:10])+'</tr>'
    document='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>教师自修改：人工看图</title>
<style>body{font:16px/1.55 system-ui,sans-serif;background:#f4f5f7;color:#202a35;max-width:1800px;margin:24px auto;padding:0 20px}section{background:white;margin:24px 0;padding:20px;border-radius:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;align-items:start}figure{margin:0}img{width:100%;height:300px;object-fit:contain;background:#eee}figcaption{min-height:30px;font-weight:600}.missing{height:300px;background:#eee;display:grid;place-content:center;padding:8px;overflow:auto}button,select{padding:8px 12px;margin:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;background:#f2f3f5;padding:12px;max-height:500px;overflow:auto}textarea{display:block;width:95%;min-height:70px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #ddd;padding:6px}details{margin-top:10px}.scroll{overflow:auto}a{color:#235eb2}.identity{color:#555}</style>
<h1>一次教师自修改 · 人工看图</h1><p>同一固定学生，从零重建；A/B 身份在运行前确定。这里没有自动质量分数或预设赢家。点击图片可打开原尺寸；展开区保留内部版本及真实错误。</p>
<button onclick="document.querySelectorAll('.identity').forEach(e=>e.hidden=!e.hidden)">显示／隐藏教师版本</button><button onclick="exportOpinions()">导出本地人工意见 JSON</button>'''
    document+=''.join(sections)
    document+=f'<section><h2>技术完成情况</h2><p>预定12项 · 已启动{summary["started"]} · 已交付{summary["delivered"]} · 内部构建{summary["build_attempts"]}次。交付不等于质量合格。</p><details><summary>展开逐任务技术状态（包含教师身份）</summary><div class="scroll"><table>{table}</table></div></details><h3>调用与成本</h3><pre>{esc(json.dumps(summary["budget"],ensure_ascii=False,indent=2))}</pre><a href="../metrics/tasks.csv">逐项CSV</a> · <a href="../metrics/cli_calls.csv">CLI记录CSV</a> · <a href="../metrics/timing.csv">阶段耗时CSV</a><details><summary>M0 → M1 真实源码 diff</summary><pre>{esc(changes)}</pre></details></section>'
    document+='''<script>
function toggleImages(button,reference){button.closest('section').querySelectorAll('img[data-render]').forEach(img=>{img.src=reference?img.dataset.reference:img.dataset.render;img.parentNode.href=img.src})}
function exportOpinions(){let opinions=[];document.querySelectorAll('select[data-scene]').forEach(e=>opinions.push({scene:e.dataset.scene,opinion:e.value||null,note:document.querySelector('textarea[data-scene="'+e.dataset.scene+'"]').value}));let data={recorded_at:new Date().toISOString(),human_entered:true,automatic_score:null,opinions};let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='human_opinions.json';a.click();URL.revokeObjectURL(a.href)}
</script></html>'''
    (reports/'index.html').write_text(document)
    md=['# 教师一次自修改：人工判断先导实验','',f'预定 12 项；已启动 {summary["started"]} 项；技术交付 {summary["delivered"]} 项。内部构建 {summary["build_attempts"]} 次。',
        '', '学生 S 固定：gpt-6.1-terra / medium；教师及自修改：gpt-6-astra / medium。全部通过现有 Codex CLI。',
        '四个来源、两题开发、两题比较、单条教师演化轨迹。历史暴露见 manifest；本次隔离不代表从未见过的盲测。',
        '关闭 BW、VLM judge、Q、SSIM、LPIPS、DINO。没有自动质量接受或晋升。M1 可执行不等于更强，质量等待用户看图判断。',
        f'学生实际收到本任务中间渲染的任务数：{summary["student_reviewed_render_tasks"]}。内部构建失败数：{summary["internal_build_failures"]}；失败程序与日志保留。首建失败时第二次调用用于错误修复，不能声称学生已经看过修复后final；不额外补第三次调用。',
        '', '|任务|状态|选择构建|内部构建|','|---|---|---|---|']
    md += [f'|{r["task_id"]}|{r["status"]}|{r.get("selected_step")}|{r.get("build_attempts") }|' for r in rows]
    md += ['', '完整原图、渲染、Hint、内部 checkpoint 与源码 diff：[离线HTML](index.html)。',
           '全部真实联系表：[开发](../figures/development_contact.png) · [匿名比较](../figures/comparison_contact.png)。',
           '联系表来自 plan.json、display_mapping.json、metrics/tasks.json 与原始PNG；重画脚本 report.py，按冻结顺序展示全部四题，没有按质量筛选。',
           '阶段耗时与进程CPU：[cost_by_stage.csv](../metrics/cost_by_stage.csv)；模型等待无法拆为纯推理时间，底层请求数未知。',
           '', '成本（usage 缺失不作零，底层模型请求数及货币费用未知）：','```json',json.dumps(summary['budget'],indent=2),'```']
    (reports/'REPORT_ZH.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=='__main__':generate()
