"""Build an offline report from measured pilot records; never runs experiments."""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

METHODS = ("fixed_h0", "sceneevolve_cli", "generic_rsi", "scene_rsi_pilot")
METRICS = ("overall", "ssim", "lpips", "dino", "psnr")
COMPLETE = {"complete", "completed", "success", "succeeded"}
PENDING = {"pending", "scheduled", "running", "waiting", "waiting_resource"}


def read(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text()) if path.exists() else default


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def average(values: list[Any]) -> float | None:
    measured = [float(v) for v in values if number(v)]
    return sum(measured) / len(measured) if measured else None


def display(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        return f"{value:.5g}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: display(row.get(key)) for key in fields})


def manifest_rows(manifest: Any) -> list[dict]:
    """Accept either a flat scene list or explicit split lists."""
    if isinstance(manifest, list):
        return [dict(row) if isinstance(row, dict) else {"scene_id": row} for row in manifest]
    if not isinstance(manifest, dict):
        return []
    if isinstance(manifest.get("scenes"), list):
        return manifest_rows(manifest["scenes"])
    if isinstance(manifest.get("tasks"), list):
        return manifest_rows(manifest["tasks"])
    splits = manifest.get("splits", manifest)
    rows = []
    for split, values in splits.items():
        if split in ("smoke", "dev", "development", "selection", "test", "held_out_test") and isinstance(values, list):
            rows.extend({**row, "split": row.get("split", split)} for row in manifest_rows(values))
    return rows


def scene_id(row: dict) -> str:
    return str(row.get("scene_id", row.get("id", row.get("task_id", "unknown"))))


def collect(root: Path) -> list[dict]:
    paths = sorted((root / "smoke").glob("*/record.json"))
    paths += sorted((root / "results").glob("*/*/*/*/*/record.json"))
    rows = []
    for path in paths:
        row = read(path)
        row["scene_id"] = scene_id(row)
        row.setdefault("metrics", {})
        row.setdefault("usage", {})
        row["record_path"] = str(path.relative_to(root))
        row["directory"] = str(path.parent.relative_to(root))
        rows.append(row)
    return rows


def functional_rows(root: Path, rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        directory = root / row["directory"] / "functional"
        checks = read(directory / 'summary.json', row.get('functional', {})) or {}
        for key in ('structure_pass', 'material_pass', 'composite_pass'):
            if isinstance(checks.get(key), bool):
                result.append({**{k: row.get(k) for k in ('method','run_id','scene_id','split','candidate_id')},
                               'check': key, 'applicable': True, 'passed': checks[key],
                               'status': 'no_valid_artifact' if row.get('status') not in COMPLETE else 'artifact_available', 'source': str((directory/'summary.json').relative_to(root)) if (directory/'summary.json').exists() else row['record_path'],
                               'detail': 'Endpoint requirement: missing/uncompleted checks do not pass. A failed reconstruction is not a measured mesh defect. Full mechanical/process records distinguish measured checks from unavailable outputs; not 3D ground truth.'})
        for name in ("text_edit.json", "text_editor.json"):
            path = directory / name
            payload = read(path)
            if not isinstance(payload, (dict, list)):
                continue
            pending = [(name.removesuffix(".json"), payload)]
            while pending:
                key, value = pending.pop(0)
                if isinstance(value, list):
                    pending.extend((f"{key}/{i}", item) for i, item in enumerate(value))
                elif isinstance(value, dict):
                    passed = value.get("passed", value.get("pass"))
                    applicable = value.get("applicable")
                    if isinstance(passed, bool) or applicable is False:
                        result.append({**{k: row.get(k) for k in ("method", "run_id", "scene_id", "split", "candidate_id")},
                                       "check": key, "applicable": applicable if isinstance(applicable, bool) else None,
                                       "passed": passed if isinstance(passed, bool) else None,
                                       "status": value.get("status"), "source": str(path.relative_to(root)),
                                       "detail": value})
                    else:
                        pending.extend((f"{key}/{child}", item) for child, item in value.items()
                                       if isinstance(item, (dict, list)))
    return result


def summarize(rows: list[dict], functionals: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key) for key in ("run_id", "method", "candidate_id", "split"))].append(row)
    summaries = []
    for keys, group in groups.items():
        statuses = Counter(row.get("status", "unknown") for row in group)
        completed = sum(row.get("status") in COMPLETE for row in group)
        valid = sum(row.get("metrics", {}).get("valid") is True for row in group)
        summary = dict(zip(("run_id", "method", "candidate_id", "split"), keys))
        summary.update(recorded_scheduled=len(group), completed=completed,
                       failed=sum(n for status, n in statuses.items() if status not in COMPLETE | PENDING),
                       pending=sum(n for status, n in statuses.items() if status in PENDING),
                       success_numerator=valid, success_denominator=len(group),
                       end_to_end_success_rate=valid / len(group), statuses=dict(statuses),
                       quality_condition="metrics.valid is true; missing numeric measurements excluded",
                       conditional_quality={key: average([r["metrics"].get(key) for r in group if r["metrics"].get("valid") is True]) for key in METRICS},
                       metric_sample_counts={key: sum(r["metrics"].get("valid") is True and number(r["metrics"].get(key)) for r in group) for key in METRICS})
        checks = [f for f in functionals if tuple(f.get(k) for k in ("run_id", "method", "candidate_id", "split")) == keys]
        applicable = [f for f in checks if f["applicable"] is not False and f["passed"] is not None]
        summary["functional"] = {"passed": sum(f["passed"] is True for f in applicable),
                                 "required_applicable_checks": len(applicable),
                                 "not_applicable": sum(f["applicable"] is False for f in checks),
                                 "unknown_applicability": sum(f["applicable"] is None for f in checks),
                                 "unit": "individual endpoint requirements, including unavailable artifacts as non-passes; not independent scenes or measured mesh-defect counts"}
        summaries.append(summary)
    return summaries


def cost_rows(rows: list[dict]) -> list[dict]:
    result, totals = [], defaultdict(lambda: {"tokens": 0, "sessions": 0, "seconds": 0, "unknown_tokens": 0})
    for index, row in enumerate(rows, 1):
        usage = row.get("usage") or {}
        token = usage.get("total_tokens")
        if not number(token) and number(usage.get("input_tokens")) and number(usage.get("output_tokens")):
            token = usage["input_tokens"] + usage["output_tokens"]
        sessions = usage.get("cli_sessions", usage.get("calls"))
        seconds = row.get("seconds")
        key = (row.get("run_id"), row.get("method"))
        total = totals[key]
        total["tokens"] += token if number(token) else 0
        total["sessions"] += sessions if number(sessions) else 0
        total["seconds"] += seconds if number(seconds) else 0
        total["unknown_tokens"] += not number(token)
        result.append({**{k: row.get(k) for k in ("run_id", "method", "scene_id", "split", "candidate_id", "status")},
                       "record_order": index, "cli_sessions": sessions if number(sessions) else None,
                       "tokens": token if number(token) else None, "seconds": seconds,
                       "execution_attempts": usage.get("executions"),
                       "render_frames": usage.get("render_frames"),
                       "observable_model_turns": usage.get("observable_model_turns"),
                       "tool_calls": usage.get("tool_calls"),
                       "cumulative_known_tokens_lower_bound": total["tokens"],
                       "cumulative_unknown_token_records": total["unknown_tokens"],
                       "cumulative_observed_cli_sessions": total["sessions"],
                       "cumulative_record_seconds": total["seconds"]})
    return result


def plots(out: Path, rows: list[dict], costs: list[dict], funcs: list[dict], primary: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    formal = [r for r in rows if r.get("split") != "smoke"]
    shown = formal if formal else rows
    scope = "Formal records" if formal else "SMOKE ONLY - not a formal comparison"
    quality = [{**{k: r.get(k) for k in ("run_id", "method", "candidate_id", "scene_id", "split", "status")},
                "primary_metric": primary, "value": r["metrics"].get(primary),
                "valid": r["metrics"].get("valid"), "source": r["record_path"]} for r in shown]
    write_csv(out / "quality.csv", quality, ["run_id", "method", "candidate_id", "scene_id", "split", "status", "primary_metric", "value", "valid", "source"])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    measured = [r for r in quality if number(r["value"])]
    if measured:
        for method in dict.fromkeys(r["method"] for r in measured):
            points = [(i, r) for i, r in enumerate(quality) if r["method"] == method and number(r["value"])]
            ax.scatter([i for i, _ in points], [r["value"] for _, r in points], label=method, s=24)
        ax.legend(fontsize=8)
        ax.set_xlabel("Record order (see quality.csv; views are not samples)")
        ax.set_ylabel(primary)
    else:
        ax.text(.5, .5, "No measured visual metrics; pending", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(scope)
    fig.tight_layout(); fig.savefig(out / "quality.png", dpi=150); plt.close(fig)

    write_csv(out / "cost.csv", costs, ["record_order", "run_id", "method", "candidate_id", "scene_id", "split", "status", "cli_sessions", "tokens", "seconds", "execution_attempts", "render_frames", "observable_model_turns", "tool_calls", "cumulative_known_tokens_lower_bound", "cumulative_unknown_token_records", "cumulative_observed_cli_sessions", "cumulative_record_seconds"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    if costs:
        groups = defaultdict(list)
        for row in costs:
            groups[(row["run_id"], row["method"])].append(row)
        for key, values in groups.items():
            label = "/".join(map(str, key))
            for ax, column in zip(axes, ("cumulative_known_tokens_lower_bound", "cumulative_observed_cli_sessions")):
                ax.plot([v["record_order"] for v in values], [v[column] for v in values], ".-", label=label)
        axes[0].legend(fontsize=7)
    else:
        for ax in axes:
            ax.text(.5, .5, "No measured cost records", ha="center", transform=ax.transAxes)
    axes[0].set_ylabel("Known tokens lower bound (unknowns excluded)")
    axes[1].set_ylabel("Known CLI sessions lower bound (unknowns excluded)")
    for ax in axes:
        ax.set_xlabel("Record order; not wall-clock scheduling order")
    fig.suptitle("Reconstruction records only; full experiment budget is ledger.json")
    fig.tight_layout(); fig.savefig(out / "cost.png", dpi=150); plt.close(fig)

    write_csv(out / "functional.csv", funcs, ["run_id", "method", "candidate_id", "scene_id", "split", "check", "applicable", "passed", "status", "source", "detail"])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    counts = defaultdict(lambda: [0, 0])
    for row in funcs:
        if row["applicable"] is not False and row["passed"] is not None:
            key = f"{row['run_id']}/{row['method']}"
            counts[key][0] += row["passed"] is True
            counts[key][1] += 1
    if counts:
        keys = list(counts)
        ax.bar(range(len(keys)), [counts[k][0] / counts[k][1] for k in keys])
        ax.set_xticks(range(len(keys)), keys, rotation=20, ha="right", fontsize=8)
        for i, key in enumerate(keys):
            ax.text(i, counts[key][0] / counts[key][1], f"{counts[key][0]}/{counts[key][1]}", ha="center", va="bottom")
        ax.set_ylim(0, 1.15)
        ax.set_ylabel("Passed / applicable requirements (missing output is non-pass)")
    else:
        ax.text(.5, .5, "Functional checks not measured / schema has no pass evidence", ha="center", transform=ax.transAxes)
    ax.set_title("Functional requirements; raw records distinguish failed checks from missing outputs")
    fig.tight_layout(); fig.savefig(out / "functional.png", dpi=150); plt.close(fig)


def contact_sheets(root: Path, out: Path, rows: list[dict], manifest: list[dict], choices: list[dict]) -> list[str]:
    """Deterministic contact sheets assembled only from this run's recorded PNG files."""
    from PIL import Image, ImageDraw, ImageOps
    names=[]
    def save(name,headers,grid):
        width,height=260,235
        canvas=Image.new('RGB',(width*len(headers),height*len(grid)+30),'#edf1f4');draw=ImageDraw.Draw(canvas)
        for col,header in enumerate(headers):draw.text((col*width+7,8),header,fill='#18394e')
        sources=[]
        for rid,line in enumerate(grid):
            for col,(path,label) in enumerate(line):
                x,y=col*width,rid*height+30
                draw.multiline_text((x+6,y+3),label,fill='black',spacing=3)
                if path and path.exists():
                    with Image.open(path) as im:im=ImageOps.contain(im.convert('RGB'),(width-12,height-53));canvas.paste(im,(x+(width-im.width)//2,y+48+(height-53-im.height)//2))
                    sources.append({'row':rid,'column':col,'path':str(path.relative_to(root)),'label':label})
                else:
                    draw.rectangle((x+6,y+48,x+width-6,y+height-5),fill='#fff2d6');draw.text((x+18,y+100),'No valid artifact / pending',fill='#704f10')
                    sources.append({'row':rid,'column':col,'path':None,'label':label})
        canvas.save(out/f'{name}.png');save_json(out/f'{name}.json',{'headers':headers,'cells':sources,'independent_unit':'scene, not image/view'});names.append(name)
    development=[s for s in manifest if s.get('split')=='development']
    grid=[]
    for scene in development:
        records=[r for r in rows if r['method']=='fixed_h0' and r['split']=='development' and r['scene_id']==scene['scene_id']]
        if not records:continue
        reference=root/records[0]['directory']/'reference.png'
        cells=[(reference,scene['scene_id']+'\nDevelopment only')]
        for run in ('r1','r2'):
            row=next((r for r in records if r['run_id']==run),None)
            cells.append((root/row['directory']/'final.png' if row and row['status'] in COMPLETE else None, f"{run}: {row['status']}\nQ={display(row['metrics']['overall'])}" if row else run+': pending'))
        grid.append(cells)
    if grid:save('h0_development_repeats',['Reference','Same H0 / r1','Same H0 / r2'],grid)
    tests=[s for s in manifest if s.get('split')=='test']
    for run in ('r1','r2'):
        selected=[r for r in rows if r['run_id']==run and r['split']=='test' and any(c['run_id']==run and c['method']==r['method'] and c['candidate_id']==r['candidate_id'] for c in choices)]
        if not selected:continue
        grid=[]
        for scene in tests:
            records=[r for r in selected if r['scene_id']==scene['scene_id']]
            reference=root/records[0]['directory']/'reference.png' if records else None
            cells=[(reference,scene['scene_id']+'\n'+run)]
            for method in METHODS:
                row=next((r for r in records if r['method']==method),None)
                cells.append((root/row['directory']/'final.png' if row and row['status'] in COMPLETE else None, f"{row['candidate_id']} / {row['status']}\nQ={display(row['metrics']['overall'])}" if row else 'pending'))
            grid.append(cells)
        save('comparison_'+run,['Reference',*METHODS],grid)
        first=[r for r in selected if r['scene_id']==tests[0]['scene_id']]
        if first:
            grid=[]
            for method in METHODS:
                row=next((r for r in first if r['method']==method),None)
                if row is None:
                    grid.append([(None,method+' / pending'),(None,'Side / pending'),(None,'Top / pending')]);continue
                folder=root/row['directory']
                grid.append([(folder/'final.png',method+'\nInput view'),(folder/'views/view_side60.png',row['scene_id']+'\nSide +60deg'),(folder/'views/view_top.png',run+'\nTop')])
            save('multiview_'+run,['Input view','Fixed side','Fixed top'],grid)
        for scene in tests[:2]:
            edited=[r for r in selected if r['scene_id']==scene['scene_id'] and (root/r['directory']/'text_edit/status.json').exists()]
            if not edited:continue
            grid=[]
            for row in edited:
                folder=root/row['directory']/'text_edit';check=read(folder/'text_edit.json',{})
                grid.append([(folder/'before.png',row['method']+'\n'+scene['scene_id']),(folder/'after.png','Text instruction: blue material\n'+run+'; one call / no repairs')])
            save('text_edit_'+run+'_'+scene['scene_id'],['Before text editor','After text editor'],grid)
    for candidate in sorted((root/'candidates').glob('r[12]/*/C*')):
        observations=read(candidate/'diagnostic_observations.json',{})
        probes=observations.get('probes',[])
        if not probes:continue
        proposal=read(candidate/'proposal_result.json',{})
        parent_source=proposal.get('parent_source')
        parent_version=str(Path(parent_source).relative_to(root)) if parent_source else None
        run,method,cid=candidate.relative_to(root).parts[1:]
        grid=[]
        for index,probe in enumerate(probes,1):
            sid=probe['scene_id'];kind=probe['probe']
            parent=next((r for r in rows if r['run_id']==run and r['split']=='development' and r['scene_id']==sid and r.get('H_version')==parent_version),None)
            result=next((r for r in rows if r['run_id']==run and r['method']==method and r['candidate_id']==cid and r['split']=='development' and r['scene_id']==sid),None)
            parent_dir=root/parent['directory'] if parent else None
            result_dir=root/result['directory'] if result else None
            grid.append([(parent_dir/'reference.png' if parent_dir else None,sid+'\n'+run+' / '+cid),
                         (parent_dir/'final.png' if parent_dir else None,'Parent / Q='+display(probe.get('baseline_visual_metrics',{}).get('overall'))+'\nControlled probe source'),
                         (candidate/'probes'/f'{index}_{kind}'/f'probe_{kind}.png',kind+' / Q='+display(probe.get('visual_metrics',{}).get('overall'))+'\n'+str(probe.get('result',{}).get('status','unknown'))),
                         (result_dir/'final.png' if result_dir else None,method+'\n'+(result['status']+' / Q='+display(result['metrics']['overall']) if result else 'Candidate evaluation pending'))])
        name='diagnostic_'+run+'_'+method+'_'+cid
        save(name,['Reference','Parent H output','Actual intervention','Shared candidate on same dev'],grid)
        sources=read(out/f'{name}.json')
        sources.update(observations_source=str((candidate/'diagnostic_observations.json').relative_to(root)),proposal_source=str((candidate/'proposal_result.json').relative_to(root)),shared_diff=str((candidate/'changes.diff').relative_to(root)) if (candidate/'changes.diff').exists() else None,rejected_not_executed_diff=str((candidate/'rejected_proposal/changes.diff').relative_to(root)) if (candidate/'rejected_proposal/changes.diff').exists() else None,diagnosis=proposal.get('diagnosis'),rationale=proposal.get('rationale'),interpretation='Intervention sensitivity and later shared-code outcome are shown separately. This is not proof that the probe caused a gain; other development cases and terminal results remain necessary.')
        save_json(out/f'{name}.json',sources)
    return names


def generate(root: str | Path) -> dict:
    root = Path(root).resolve()
    out = root / "reports"
    out.mkdir(parents=True, exist_ok=True)
    # Archive rejected source for review only. Never replace executable H/M files.
    import difflib
    for result_path in sorted((root/'candidates').glob('*/*/*/proposal_result.json')):
        candidate=result_path.parent
        if read(result_path,{}).get('status')!='proposal_failed':continue
        response=next((candidate/name/'response.txt' for name in ('proposal_call_2','proposal_call') if (candidate/name/'response.txt').exists()),None)
        if response is None:continue
        try:
            proposal=json.loads(response.read_text())
        except json.JSONDecodeError:
            continue  # The full malformed response remains in its original CLI log.
        rejected=candidate/'rejected_proposal';rejected.mkdir(exist_ok=True)
        differences=[]
        for item in proposal.get('files',[]):
            name=item.get('path')
            if name not in ('policy.py','system.txt','meta.py') or not isinstance(item.get('content'),str):continue
            (rejected/name).write_text(item['content'])
            differences.extend(difflib.unified_diff((candidate/name).read_text().splitlines(True),item['content'].splitlines(True),fromfile='parent/'+name,tofile='rejected_not_executed/'+name))
        (rejected/'changes.diff').write_text(''.join(differences))
        save_json(rejected/'status.json',{'status':'rejected_not_executed','source_response':str(response.relative_to(root)),'original_error':read(result_path).get('error'),'purpose':'Post-hoc archival only; no H/M replacement or experimental repair'})
    config = read(root / "config.json", {})
    manifest = read(root / "manifest.json", {})
    ledger = read(root / "ledger.json")
    archive = read(root / "archive.json")
    selections = read(root / "selections.json")
    rows = collect(root)
    selection_frozen=(root/'selection_freeze.json').exists()
    visible_rows=rows if selection_frozen else [r for r in rows if r.get('split') not in ('selection','test')]
    funcs = functional_rows(root, rows)
    summaries = summarize(rows, funcs)
    costs = cost_rows(rows)
    primary = config.get("pilot", {}).get("primary_metric", config.get("metrics", {}).get("primary", "overall"))
    if primary not in METRICS:
        primary = "overall"
    analysis = read(root / "reports/analysis.json")
    stages = {name: read(root / f'{source}_status.json', {'status':'pending'}) for name,source in (('ablation','extras'),('replay','replay'),('external','external'))}
    summary = {"paired_analysis": analysis, "report_kind": "measured_records_only", "primary_metric": primary,
               "formal_records": sum(r.get("split") != "smoke" for r in rows),
               "smoke_records": sum(r.get("split") == "smoke" for r in rows),
               "record_count": len(rows), "completed": sum(r.get("status") in COMPLETE for r in rows),
               "physical_completed_reconstructions":sum(r.get('status') in COMPLETE and not r.get('reuse_of') for r in rows),
               "reused_outcomes":sum(bool(r.get('reuse_of')) for r in rows),
               "status_counts": dict(Counter(r.get("status", "unknown") for r in rows)),
               "all_scheduled": ledger.get("all_scheduled") if isinstance(ledger, dict) else None,
               "all_scheduled_note": "Only explicit ledger all_scheduled is reported; missing scheduled records are not inferred as completed.",
               "groups": summaries, "ledger": ledger, "selections": selections,
               "archive": archive, "additional_stages":stages, "data_exposure": config.get("pilot", {}).get("data_exposure", "unknown"),
               "limitations": ["没有三维真值，未估计真实三维恢复精度；多视角仅供结构检查。",
                               "缺失指标保持 null；质量均值仅在 valid 且有数值的记录上计算。",
                               "功能图的单位是检查项，不能当独立场景样本；遗漏检查不算通过。",
                               "重建成本图不包括未记录在 scene record 中的提案、评审、诊断和重试；总预算以 ledger 为准。",
                               "前段使用CPU；用户随后授权空闲GPU，后续Blender按逐次占用检查仅使用GPU 0的UUID，忙时继续CPU，质量设置不变。混合设备耗时不能解释为算法效率差异；1200秒期限也可能带来不同执行机会，属于本轮限制。CLI内部服务排队不可观测，service_queue_seconds为null，CLI耗时与重建总耗时互有包含。",
                               "图像已在历史联系表/人物审阅中暴露，本轮是 exploratory。",
                               "主对照仅两次独立研发重复；展示全部点与配对差异，不作普遍优势或元能力单调提高的结论。",
                               "CLI只记录请求模型，未独立返回可验证的实际路由；远端模型采样种子不可控，本地seed仅控制数据/程序/渲染。",
                               "机械操作仅检验可操作性；文本编辑只有真实独立编辑器执行证据才报告。",
                               "机械编辑目标按固定名称/层级规则选取，实测可能选中Architecture等建筑组合；文本测试另按预定工作台类别匹配。名称匹配不等于语义真值，不能据此证明应有对象完整。",
                               "机制A提供固定目标的焦距、尺度与隔离探测；尚无自动代码到语义对象定位器，未知映射不作归因。",
                               "机制B实际执行共同的完整三项检查菜单，Ours使用回归证据和提示优先级；按修改模块自动选择回归子集尚未实现。",
                               "共同候选导入白名单未完整列入提案提示；实测Ours(r1/C1)的meta.py与Generic(r2/C1)的policy.py因使用ast被拒绝，属于共同接口适配局限，不能解释为对应研究机制无效。保留原始失败，不对单组人工修补或放宽规则。",
                               "有效改进、配对数和元回放无完整证据时不推断，不预绘提升曲线。"]}
    save_json(out / "summary.json", summary)
    attempts=[]
    for row in visible_rows:
        directory=root/row['directory']
        timing={}
        trajectory=directory/'trajectory.jsonl'
        if trajectory.exists():
            for line in trajectory.read_text().splitlines():
                event=json.loads(line)
                if event['event'] in ('execute','execution_result'):timing.setdefault(event['step'],{})[event['event']]=event['time']
        for path in sorted(directory.glob('steps/*/result.json')):
            result=read(path);clock=timing.get(result['step'],{})
            attempts.append({**{k:row[k] for k in ('method','run_id','candidate_id','scene_id','split')},'step':result['step'],'execution_success':result['ok'],'error':result['error'],'seconds':clock['execution_result']-clock['execute'] if all(k in clock for k in ('execute','execution_result')) else None,'render_written':(path.parent/'final.png').exists(),'blend_written':(path.parent/'scene.blend').exists(),'source':str(path.relative_to(root))})
    write_csv(out/'execution_attempts.csv',attempts,['method','run_id','candidate_id','scene_id','split','step','execution_success','error','seconds','render_written','blend_written','source'])
    geometry=[]
    for row in visible_rows:
        path=root/row['directory']/'functional/scene_structure.json'
        structure=read(path,{})
        relation=structure.get('approximate_relations',{})
        geometry.append({**{k:row.get(k) for k in ('method','run_id','candidate_id','scene_id','split','status')},'blend_opened':structure.get('blend_opened'),'mesh_count':structure.get('mesh_count'),'finite_nonempty_mesh_count':structure.get('finite_nonempty_mesh_count'),'approximate_support_candidate_count':len(relation['approximate_support_candidates']) if 'approximate_support_candidates' in relation else None,'approximate_overlap_candidate_count':len(relation['approximate_overlap_candidates']) if 'approximate_overlap_candidates' in relation else None,'true_mesh_collision_pass':None,'true_3d_accuracy':None,'source':str(path.relative_to(root)) if path.exists() else None})
    write_csv(out/'geometry_relations.csv',geometry,list(geometry[0]) if geometry else [])
    edit_scenes=[s['scene_id'] for s in manifest_rows(manifest) if s.get('split')=='test'][:2]
    edits=[]
    for choice in selections or []:
        for sid in edit_scenes:
            row=next((r for r in rows if all(r[k]==choice[k] for k in ('method','run_id','candidate_id')) and r['split']=='test' and r['scene_id']==sid),None)
            directory=root/row['directory']/'text_edit' if row else None
            status=read(directory/'status.json',{}) if directory else {}
            measured=read(directory/'text_edit.json',{}) if directory else {}
            edits.append({**{k:choice[k] for k in ('method','run_id','candidate_id')},'scene_id':sid,'status':status.get('status','pending'),'instruction':status.get('instruction'),'passed':measured.get('passed',False if status.get('status')=='failed' else None),'target_success':measured.get('target_success'),'target_geometry_preserved':measured.get('target_geometry_preserved'),'non_target_preserved':measured.get('non_target_preservation',{}).get('pass'),'source':str((directory/'status.json').relative_to(root)) if directory else None})
    write_csv(out/'text_edit.csv',edits,['method','run_id','candidate_id','scene_id','status','instruction','passed','target_success','target_geometry_preserved','non_target_preserved','source'])
    judgments=[]
    for path in sorted((root/'judgments').glob('*/judgment.json')):
        value=read(path);mapping=read(path.parent/'mapping_for_report.json',{})
        judgments.append({**mapping,'status':value['status'],**value.get('judgment',{}),'source':str(path.relative_to(root))})
    write_csv(out/'independent_judgments.csv',judgments,['method','run_id','candidate_id','scene_id','status','score','observations','uncertain_3d_hypotheses','source'])
    flat = []
    for row in visible_rows:
        directory=root/row['directory']
        extra_frames=sum(read(p,{}).get('renders_completed',0) for p in directory.glob('*/render_ledger.json') if not p.is_symlink())
        frame_count=len(list(directory.glob('steps/*/final.png')))+extra_frames
        choice=next((c for c in (selections or []) if c['method']==row['method'] and c['run_id']==row['run_id']),None)
        item = {**{k: row.get(k) for k in ("method", "run_id", "scene_id", "split", "candidate_id", "parent_id", "H_version", "M_version", "model_roles", "status", "failure_type", "device", "device_mapping", "render_device_history", "functional_device_mapping", "seconds", "resource_wait_seconds", "service_queue_seconds", "usage", "record_path", "reuse_of")}, **row["metrics"], 'selected_for_run': row['candidate_id']==choice['candidate_id'] if choice else None, 'actual_render_frames':frame_count}
        flat.append(item)
    write_csv(out / "scenes.csv", flat, ["method", "run_id", "scene_id", "split", "candidate_id", "parent_id", "H_version", "M_version", "model_roles", "status", "failure_type", "valid", *METRICS, "selected_for_run", "actual_render_frames", "device", "device_mapping", "render_device_history", "functional_device_mapping", "seconds", "resource_wait_seconds", "service_queue_seconds", "usage", "reuse_of", "record_path"])
    visible_funcs=funcs if selection_frozen else [f for f in funcs if f.get('split') not in ('selection','test')]
    plots(out, visible_rows, costs, visible_funcs, primary)
    sheets=contact_sheets(root,out,rows,manifest_rows(manifest),selections or [])

    def link(path: Path, title: str | None = None) -> str:
        target = os.path.relpath(path, out)
        return f'<a href="{html.escape(target, quote=True)}">{html.escape(title or path.name)}</a>'

    def media(path: Path, title: str) -> str:
        if not path.exists():
            return '<div class="missing">pending / 无对应产物</div>'
        target = html.escape(os.path.relpath(path, out), quote=True)
        return f'<a href="{target}"><img loading="lazy" src="{target}" alt="{html.escape(title)}"></a>'

    def row_card(row: dict) -> str:
        directory = root / row["directory"]
        label = f"{row.get('candidate_id')} · {row.get('status')} · {primary}={display(row['metrics'].get(primary))}"
        if row.get('split')=='test':
            choice=next((c for c in (selections or []) if c['run_id']==row['run_id'] and c['method']==row['method']),None)
            if choice:label += ' · 主对照冻结选择' if choice['candidate_id']==row['candidate_id'] else ' · 额外阶段参考，非主对照所选系统'
        assets = " · ".join(link(directory / name) for name in ("record.json", "scene.blend", "build.py") if (directory / name).exists())
        return f'<div class="card"><p>{html.escape(label)}</p>{media(directory / "final.png", label)}<p>{assets}</p></div>'

    panels = ["<h1>scene_rsi_pilot：真实产物实验报告</h1>",
              f"<p>正式记录 {summary['formal_records']}；smoke 记录 {summary['smoke_records']}；完成记录 {summary['completed']}。缺失显示 pending/null。所有 smoke 排除正式对照。</p>",
              "<p>" + " · ".join(link(out / name) for name in ("report.md", "scenes.csv", "summary.json", "quality.csv", "cost.csv", "functional.csv", "geometry_relations.csv", "text_edit.csv", "independent_judgments.csv", "main_scheduled.csv", "calls.csv", "execution_attempts.csv", "method_total_cost.csv")) + "</p>",
              "<p>冻结配置与档案：" + " · ".join(link(root / name) for name in ("config.json", "manifest.json", "protocol.md", "ledger.json", "archive.json", "selections.json") if (root / name).exists()) + "</p>"]
    panels.append('<p>研究层次：P为单场景程序，H为跨图像共享重建流程，M为产生H/M修改的可执行策略。共同起点为本地SceneEvolve初始H0；CLI外层循环不计为H。生成与固定编辑器请求gpt-6.1-sol/medium；提案与独立匿名评审请求gpt-6-astra/medium。CLI实际路由未知，usage以原始返回为准。</p>')
    if not selection_frozen:panels.append('<p class="missing">中期报告：Selection/Test 的逐图指标、图像和结构细节在统一选择冻结后再展示；当前仅汇总登记状态。主对照尚未完成。</p>')
    gpu_checks=[]
    for folder in sorted((root/'smoke').glob('gpu_*_check')):
        execution=read(folder/'render_ledger.json',{})
        mapping=read(folder/'actual_device.json',{})
        comparison=read(folder/'comparison.json',{})
        gpu_checks.append({'check':folder.name,'exit_code':execution.get('exit_code'),'frames':execution.get('renders_completed'),'seconds':execution.get('seconds'),'backend':mapping.get('backend'),'gpu_uuid':mapping.get('gpu_uuid'),'mean_absolute_RGB_difference_0_1':comparison.get('mean_absolute_RGB_difference_0_1')})
        panels.append('<details><summary>GPU smoke：'+html.escape(folder.name)+'</summary><pre>'+html.escape(json.dumps(gpu_checks[-1],ensure_ascii=False,indent=2))+'</pre>'+media(folder/'final.png','实际 GPU smoke 输出')+link(folder/'stderr.log','原始错误日志')+'</details>')
    write_csv(out/'gpu_checks.csv',gpu_checks,['check','exit_code','frames','seconds','backend','gpu_uuid','mean_absolute_RGB_difference_0_1'])
    if gpu_checks:panels.append('<p>设备检查排除正式对照，失败也计入渲染预算。'+link(root/'gpu_adaptation.md','设备适配记录')+' · '+link(out/'gpu_checks.csv','GPU smoke 源数据')+'</p>')
    if not summary["formal_records"]:
        panels.append('<p class="missing">主对照尚未产生正式记录；下面图表仅为已完成 smoke 或未运行状态，不构成方法比较。</p>')
    for name, title in (("quality", "视觉质量：全部实测点"), ("cost", "重建记录累计成本"), ("functional", "已测功能检查"), ("effective_improvement", "冻结选择后的配对终测收益")):
        panels.append(f"<h2>{title}</h2>" + media(out / f"{name}.png", title) + link(out / f"{name}.csv", "图的源数据"))
    for name,title in (('rd_cost_gain','全部研发调用成本与 Selection 收益'),('terminal_quality','所选系统终测：全部场景点，两个研发重复'),('terminal_functional','所选系统终测功能通过率：失败保留分母'),('complete_improvement_rate','完整有效改进率：保留两次重复分母')):
        if (out/f'{name}.png').exists():
            panels.append(f'<h2>{title}</h2>'+media(out/f'{name}.png',title)+link(out/f'{name}.csv','图的源数据'))
    if sheets:
        panels.append('<h2>可下载联系表</h2><p>按冻结的 Test 场景顺序，空白表示没有对应产物。文本编辑与机械操作分开展示。</p>')
        for name in sheets:
            panels.append('<h3>'+html.escape(name)+'</h3>'+media(out/f'{name}.png',name)+link(out/f'{name}.json','图片来源记录'))

    panels.append("<h2>逐场景联系表</h2><p>按 manifest 顺序；每个重复分别展示，候选分别保留，未运行格留空。历史结果不混入本轮。</p>")
    scenes = manifest_rows(manifest)
    if scenes:
        smoke_ids = {scene_id(s) for s in scenes if s.get("split") == "smoke"}
        scenes = [{"split": "smoke", "scene_id": r["scene_id"]} for r in rows
                  if r.get("split") == "smoke" and r["scene_id"] not in smoke_ids] + scenes
    if not scenes:
        seen = set()
        for row in rows:
            key = (row.get("split"), row["scene_id"])
            if key not in seen:
                scenes.append({"split": key[0], "scene_id": key[1]}); seen.add(key)
    run_ids = list(dict.fromkeys(r.get("run_id", "unknown") for r in rows))
    if not run_ids:
        run_ids = ["pending"]
    for run_id in [r for r in run_ids if r in ('smoke','r1','r2')]:
        panels.append(f"<h3>run_id: {html.escape(str(run_id))}</h3><table><thead><tr><th>参考 / 场景</th>" + "".join(f"<th>{method}</th>" for method in METHODS) + "</tr></thead><tbody>")
        for scene in scenes:
            sid, split = scene_id(scene), scene.get("split")
            if split not in ('smoke','development','selection','test'):
                continue
            if run_id == "smoke" and split != "smoke":
                continue
            if run_id != "smoke" and split == "smoke":
                continue
            matches = [r for r in visible_rows if r.get("run_id") == run_id and r["scene_id"] == sid and (not split or r.get("split") == split)]
            reference = next((root / r["directory"] / "reference.png" for r in matches if (root / r["directory"] / "reference.png").exists()), None)
            reference_html = media(reference, sid) if reference is not None else '<div class="missing">pending</div>'
            panels.append(f"<tr><td><p>{html.escape(sid)} · {html.escape(str(split))}</p>{reference_html}</td>")
            for method in METHODS:
                matching = [r for r in matches if r.get("method") == method]
                panels.append("<td>" + ("".join(row_card(r) for r in matching) or '<div class="missing">pending / 未运行</div>') + "</td>")
            panels.append("</tr>")
        panels.append("</tbody></table>")

    extra_rows=[r for r in rows if r.get('method') not in METHODS or r.get('run_id') not in ('smoke','r1','r2')]
    panels.append('<h2>消融、冻结元代理回放与外部任务</h2><p>只展示实际运行记录；主对照 Test 的再次使用不是新的盲测。BlenderWorld 为 adapted evaluation，不是官方榜单分数。</p>')
    for name,status in stages.items():
        panels.append('<details><summary>'+html.escape(name+': '+str(status.get('status')))+ '</summary><pre>'+html.escape(json.dumps(status,ensure_ascii=False,indent=2))+'</pre></details>')
    additional=analysis.get('additional_stage_analysis',{}) if analysis else {}
    for key,name,title in [('ablation','ablation_terminal','独立生成消融：相对匹配 Ours 的逐场景差异'),('replay','frozen_meta_replay','冻结元策略：相同陌生 H 起点上的全部实测收益')]:
        if additional.get(key):
            panels.append('<h3>'+title+'</h3>'+media(out/f'{name}.png',title)+link(out/f'{name}.csv','图的源数据'))
    if additional.get('external'):
        panels.append('<p>'+link(out/'blenderworld_adapted.csv','BlenderWorld adapted evaluation 数据；非官方榜单分数')+'</p>')
    for row in extra_rows:
        label=' / '.join(str(row.get(k)) for k in ('run_id','method','candidate_id','split','scene_id'))
        panels.append('<h3>'+html.escape(label)+'</h3>'+row_card(row))

    panels.append("<h2>多视角、结构与编辑证据</h2><p>侧视/俯视没有真实新视角参考，不能证明不可见部分恢复正确。.blend 文件存在不等于已经验证可打开；可打开检查以 functional 原始记录为准。</p>")
    evidence_count = 0
    for row in visible_rows:
        directory = root / row["directory"]
        images = sorted((directory / "views").glob("*.png")) + sorted((directory / "functional").glob("*.png")) + sorted((directory / "text_edit").glob("*.png"))
        records = sorted((directory / "functional").glob("*.json")) + sorted((directory / "text_edit").glob("status.json"))
        if images or records:
            evidence_count += 1
            label = " / ".join(str(row.get(k)) for k in ("run_id", "method", "candidate_id", "split", "scene_id"))
            panels.append(f"<h3>{html.escape(label)}</h3><div class='media-grid'>" + "".join(f"<figure>{media(path, path.name)}<figcaption>{html.escape(path.name)}</figcaption></figure>" for path in images) + "</div>")
            for path in records:
                payload=read(path)
                if path.name=='scene_structure.json':
                    from model_evidence import compact_structure
                    payload=compact_structure(payload)
                preview=json.dumps(payload,ensure_ascii=False,indent=2)
                if len(preview)>40000:preview=preview[:40000]+'\n[HTML preview truncated; linked JSON retains the complete record]'
                panels.append(f"<details><summary>{link(path)}</summary><pre>{html.escape(preview)}</pre></details>")
    if not evidence_count:
        panels.append('<p class="missing">多视角和编辑检查尚无可展示的真实产物。</p>')
    panels.append("<h2>诊断与候选档案</h2><p>仅展示已保存的真实档案；没有可靠探测观测或程序 diff 时，不作因果归因。</p>")
    for candidate in sorted((root / "candidates").glob("*/*/*")):
        observations = read(candidate / "diagnostic_observations.json")
        if observations is None:
            continue
        panels.append("<h3>" + html.escape(str(candidate.relative_to(root))) + "</h3>")
        images = sorted((candidate / "probes").glob("*/probe_*.png"))
        panels.append("<div class='media-grid'>" + "".join(media(path, path.name) for path in images) + "</div>")
        panels.append("<details><summary>实际探测与诊断记录</summary><pre>" + html.escape(json.dumps(observations, ensure_ascii=False, indent=2)) + "</pre></details>")
        diff = candidate / "changes.diff"
        if diff.exists():
            panels.append("<details><summary>" + link(diff, "实际共享H/M差异") + "</summary><pre>" + html.escape(diff.read_text()) + "</pre></details>")
        rejected = candidate / "rejected_proposal/changes.diff"
        if rejected.exists():
            panels.append("<details><summary>" + link(rejected, "被拒绝的拟议差异：未执行，不是有效后代") + "</summary><pre>" + html.escape(rejected.read_text()) + "</pre></details>")
        proposal = read(candidate / "proposal_result.json")
        if proposal:
            panels.append("<p>" + html.escape(str(proposal.get("rationale", proposal.get("error", "unknown")))) + "</p>")
    panels.append("<details><summary>有效配对与完整改进率原始数据</summary><pre>" + html.escape(json.dumps(analysis, ensure_ascii=False, indent=2)) + "</pre></details>")
    for title, payload in (("候选档案", archive), ("Selection 决定", selections), ("预算账本", ledger)):
        panels.append(f"<details><summary>{title}</summary><pre>{html.escape(json.dumps(payload, ensure_ascii=False, indent=2))}</pre></details>")
    panels.append("<h2>局限与未完成</h2><ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in summary["limitations"]) + "</ul>")
    css = "body{font:15px system-ui,sans-serif;margin:24px;color:#20252b;background:#f5f7fa}h1,h2{color:#18394e}a{color:#145e9a}img{max-width:100%;height:auto;background:#eee}body>img{max-width:1100px}table{border-collapse:collapse;width:100%;table-layout:fixed}td,th{border:1px solid #ccd3d9;padding:8px;vertical-align:top;overflow-wrap:anywhere}th{background:#dfe8ee}.missing{padding:16px;background:#fff2d6;color:#704f10}.card{padding:5px;border-bottom:1px solid #cbd5dc}.media-grid{display:flex;flex-wrap:wrap;gap:8px}.media-grid figure{width:30%;min-width:220px;margin:4px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;padding:12px}details{margin:12px 0}"
    (out / "index.html").write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>scene_rsi_pilot</title><style>' + css + "</style><body>" + "\n".join(panels) + "</body></html>")
    lines = ["# scene_rsi_pilot 中文实验报告", "", "本报告只汇总本轮已保存的 record.json；历史结果不作为同条件结果。", "",
             f"正式记录：{summary['formal_records']}；smoke：{summary['smoke_records']}；完成：{summary['completed']}；状态：{display(summary['status_counts'])}。",
             f"明确登记的 all_scheduled：{display(summary['all_scheduled'])}；没有登记的总计划数保持 null，不能用完成数冒充计划分母。", "",
             "[本地可视化](index.html) · [逐场景 CSV](scenes.csv) · [汇总与完整账本](summary.json)", "",
             "研究对象分为单场景程序P、跨图像共享流程H、以及可执行改进策略M。四组共同从本地SceneEvolve初始H0出发；Codex CLI的外层agent循环不是被研究的H。生成/固定编辑器请求gpt-6.1-sol，提案/独立匿名评审请求gpt-6-astra，均为medium。CLI未独立返回实际模型路由，不能用模型自报身份验证。", "",
             "正式规模为2个Development、2个Selection、4个Test，两次独立研发、每次最多K=2共享候选。原4/4/8规模按最多5次内层调用估计已超过600会话上限，因此在正式结果产生前统一缩小。选择保留H0，先满足执行/功能不退化，再要求Selection端到端Q提升超过0.01；该实用阈值不是统计显著性界限。", "",
             "## 真实测量", "", "|重复|方法|候选|划分|记录分母|完成|失败|端到端成功|条件主指标均值|指标有效样本|", "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for item in summaries:
        cells = [item[k] for k in ("run_id", "method", "candidate_id", "split", "recorded_scheduled", "completed", "failed")]
        cells += [f"{item['success_numerator']}/{item['success_denominator']}", item["conditional_quality"][primary], item["metric_sample_counts"][primary]]
        lines.append("|" + "|".join(display(v) for v in cells) + "|")
    if not summaries:
        lines.append("\n暂无任何测量记录。")
    if not summary["formal_records"]:
        lines.append("\n主对照尚未运行完成；smoke 图不能解释为方法胜负。")
    lines += ["", f"主视觉指标字段：`{primary}`。缺失值不填零；失败保留在端到端分母中，条件质量另列。", "",
              "![视觉质量](quality.png)", "[源数据](quality.csv)", "", "![累计成本](cost.png)", "[源数据](cost.csv)", "", "![功能检查](functional.png)", "[源数据](functional.csv)", "",
              "## 选择、有效改进与元回放", "", "选择结果与原始候选档案原样保存在 summary.json；报告不根据 Test 重新选择。完整有效改进和有效配对数需要已冻结选择及对应 H0/候选功能和终测记录；当前脚本不从单个视觉分数推断。没有元回放实测数据时不绘跨代收益曲线。", "",
              "## 资源与复用", "", f"资源策略：{display(config.get('resources'))}；渲染配置：{display(config.get('render'))}；CPU 配置：{display(config.get('pilot', {}).get('cpu_threads'))}。实际逐记录设备保存在 scenes.csv，等待与执行成本以原账本字段为准。", "",
              "复用配置完整保存在 [config.json](../config.json)；数据来源保存在 [manifest.json](../manifest.json)。旧 scenespec M0–M3 为已知米尺度布局策略，不直接证明图像重建或本轮元策略改进。", "",
              "## 局限与待运行", ""]
    if analysis:
        lines += ['', '## 主对照配对结果', '', '|方法|重复|有效配对/计划|条件Q差|功能通过数差|完整有效改进|', '|---|---|---:|---:|---:|---|']
        for item in analysis.get('complete_valid_improvement',[]):
            values=[item['method'],item['run_id'],f"{item['valid_pairs']}/{item['all_scheduled_pairs']}",item['conditional_gain'],item['functional_pass_count_difference'],item['complete_valid_improvement']]
            lines.append('|'+ '|'.join(display(v) for v in values)+'|')
        lines += ['', '元策略执行证据：`'+display(analysis.get('method_realization'))+'`。源码发生变化和后代实际用于后续提案仍不证明元能力提高。', '', '![研发成本与收益](rd_cost_gain.png)', '[源数据](rd_cost_gain.csv)', '', '![完整有效改进率](complete_improvement_rate.png)', '[源数据](complete_improvement_rate.csv)']
    lines += ['', '## 额外阶段实际状态', '']
    for name,status in stages.items():
        source='extras' if name=='ablation' else name
        lines.append('- '+name+': '+display(status.get('status'))+'；[原始状态](../'+source+'_status.json)。')
    if additional.get('ablation'):
        lines += ['', '消融各条件均独立生成候选。下表只计真实终测配对；本阶段再次使用主实验 Test，不构成新的盲测。', '', '|方法|重复|场景|Q|相对H0差|相对匹配Ours差|功能通过|', '|---|---|---|---:|---:|---:|---|']
        for point in additional['ablation']:
            lines.append('|'+ '|'.join(display(point[k]) for k in ('method','run_id','scene_id','Q','paired_gain_H0','paired_difference_reference','functional_pass'))+'|')
        lines += ['', '![独立生成消融](ablation_terminal.png)', '[源数据](ablation_terminal.csv)']
    if additional.get('replay'):
        lines += ['', '冻结回放比较 M_initial 与 M_descendant 从同一 H_start 研发后的收益；历史图像筛选暴露仍使其属于探索性实验。有限起点和重复不能支持普遍或单调元能力提升。', '', '|M|起点|提案重复|场景|候选|相同H_start上的Q增益|功能不退化|CLI会话（不含共享起点）|', '|---|---|---:|---|---|---:|---|---:|']
        for point in additional['replay']:
            lines.append('|'+ '|'.join(display(point[k]) for k in ('method','start_id','proposal_repeat','scene_id','candidate_id','gain_over_same_H_start','functional_non_degradation','actual_cli_sessions_excluding_shared_H_start'))+'|')
        lines += ['', '![冻结元策略回放](frozen_meta_replay.png)', '[源数据](frozen_meta_replay.csv)']
        lines += ['', '|起点|提案重复|有效配对|后代减初始M的收益差|功能通过差|', '|---|---:|---|---:|---:|']
        for point in additional.get('replay_paired',[]):
            lines.append('|'+ '|'.join(display(point[k]) for k in ('start_id','proposal_repeat','paired_valid','descendant_minus_initial_gain','descendant_minus_initial_functional_pass'))+'|')
        lines += ['', '[元回放配对差异源数据](frozen_meta_paired.csv)']
    if additional.get('external'):
        lines += ['', 'BlenderWorld 使用直接读取 .blend、三视角和独立 Codex CLI 评审，保留 rubric 含义但改变评测入口与评审后端。以下是 adapted evaluation，非官方分数。', '', '|方法|场景|重建状态|Q|功能通过|适配评分/100|', '|---|---|---|---:|---|---:|']
        for point in additional['external']:
            lines.append('|'+ '|'.join(display(point[k]) for k in ('method','scene_id','reconstruction_status','Q','functional_pass','adapted_score_0_100'))+'|')
        lines += ['', '[BlenderWorld 适配评测源数据](blenderworld_adapted.csv)']
    lines += ['', '## 局限', '']
    lines += ["- " + item for item in summary["limitations"]]
    lines += ["", "## 重建报告", "", "```bash", f"bash '{root / 'run.sh'}' report", "```", "", "此命令使用已验证的本地Python环境，只重建数据表、图和报告，不启动模型、Blender 或补跑实验；实验续跑入口由 runner README 给出。", ""]
    (out / "report.md").write_text("\n".join(lines))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = generate(args.root)
    print(json.dumps({"report": str(args.root.resolve() / "reports/index.html"), "records": result["record_count"], "formal_records": result["formal_records"]}, ensure_ascii=False))
