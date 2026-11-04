"""Freeze the actual V2 protocol after mechanism and real-image acceptance."""
from pathlib import Path
import json,shutil,time,difflib
import pilot
ROOT=Path(__file__).resolve().parent

def main():
    if (ROOT/'protocol_frozen.json').exists():raise RuntimeError('Protocol already frozen; preserve it')
    acceptance=pilot.read(ROOT/'tests/mechanism_acceptance.json');smoke=pilot.read(ROOT/'tests/real_smoke.json')
    assert acceptance['first_seven_requirements_passed'] and smoke['passed']
    ledger=pilot.current();forecast=ledger['cli_sessions']+72*5+4+8+24
    if forecast>420:raise RuntimeError('Reduce and disclose scope before freezing; no formal submissions yet')
    cfg=pilot.config();cfg['pilot']['status']='frozen';cfg['pilot']['max_regression_tests_per_candidate']=6
    cfg['pilot']['budget_forecast']={'new_sessions_at_freeze':ledger['cli_sessions'],'remaining_main_reconstructions':72,'max_student_calls':360,'proposals':4,'editors':8,'judges':24,'total_upper_bound':forecast,'transient_auto_retries':0,'render_upper_bound':600}
    pilot.write_json(ROOT/'config.json',cfg);pilot.write_json(ROOT/'configs/frozen_config.json',cfg)
    snap=ROOT/'code_snapshots/v2_frozen';snap.mkdir()
    for name in ['pilot.py','strategies.py','inspect_blend.py','regression.py','model_evidence.py','smoke.py','resume.py','supplement.py','text_edit_worker.py']:
        shutil.copy2(ROOT/name,snap/name)
    shutil.copytree(ROOT/'backend',snap/'backend',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    diff=''
    for name in ['pilot.py','strategies.py','inspect_blend.py']:
        diff+=''.join(difflib.unified_diff((ROOT/'code_snapshots/v1_reference'/name).read_text().splitlines(True),(ROOT/name).read_text().splitlines(True),fromfile='V1/'+name,tofile='V2/'+name))
    (ROOT/'code_snapshots/v1_to_v2.diff').write_text(diff)
    text=f'''# Scene-RSI V2 冻结运行协议

冻结时间 UTC epoch：{time.time()}。本协议在 V2 机制与真实图像烟测后、正式 Development/Selection/Test 运行前写入；V1 历史不是预注册证据。烟测期间修复了脚本模块路径与夹具文件名，原失败日志保留；烟测不进入正式数据，也不继承烟测生成的后代。

## 实验与共同起点

仅运行 scene_rsi_v2 与内部 fixed_h0。2 次独立研发 r1/r2，K=2 个共享候选；每轮依序 r1/r2 交错。4 Development、4 Selection、6 Test，组别见 manifest。H0 为 V1 backend/harnesses/baseline 的 policy/system，非历史最佳后代。M0 为本轮修复的 initial_meta/scene_rsi_v2/meta.py。所有输出、预算与状态独立。

数据源本地 web_scenes 人工无人物筛选索引；本轮来源 ID 不在 V1 实际重建/回放/烟测中，按来源标题分组，物理独立性无法完全验证。历史联系表曝光和其他人工分析记录不足，exploratory，不宣称全新盲测。图像 EXIF/RGB 缩放最长边512。第三方来源与许可保留。

## 固定模型与执行

重建/编辑 sol=gpt-6.1-sol medium；提案/独立评审 astra=gpt-6-astra medium。请求模型与 CLI 实报分开，不能确认 actual_model 则 unknown。Codex CLI0.163.0，真实 --image 附件，fresh ephemeral，read-only，无 shell/web/工具/隐藏 subagent。不控制远端采样种子。适配器复制进仅含所需图像的临时工作区。只能修改候选 policy.py/system.txt/meta.py。M 程序不能改 evaluator、资源和预算；其输入以 JSON 深拷贝传入。

固定内层每场景最多5次 CLI、3次 Blender 执行、1200秒；单次模型600秒，提案2400秒。无自动服务重试；暂停与失败保留，恢复不删除事实。上限420 CLI、1500帧，包括烟测/提案/修复/评审/编辑。冻结前已有 {ledger['cli_sessions']} CLI，保守总上界 {forecast}；72次正式重建最多360，提案4，文字编辑8，评审24。实际少用不会为正结果扩容。未完成终测不因预算临时删去。

Cycles16 samples、seed42、512最长边、AgX look=None、exposure0/gamma1、关闭降噪/自适应采样；CPU/GPU质量相同。CPU单重任务2线程，数值指标CPU。授权池0–3每个子进程检查显存、利用率与活跃进程，最多1卡，忙则CPU。等待与运行不混同效率比较。

## 两阶段机制

M.plan_probes 得到显式剩余/已用探测数、菜单、全部真实对象ID与固定投影的最大128个Mesh数值明细、开发参考/渲染、指标、P与轨迹、功能事实、历史档案。M0 选择最差Q开发场景与最大非结构生成 Mesh，是覆盖启发式，不声称已知语义错误位置。对象尺度/隔离必须使用M给出的真实ID，相机可无对象。

每候选最多2个临时受控探测：焦距x1.1、指定对象几何中心尺度x1.1、隔离其他Mesh。记录固定项/变化项/实测视觉变化，不作为唯一因果识别。探测不覆盖原 .blend。真实探测与研发回归结果进入可执行 M.plan_patch，保存 stage1/stage2，再由一个 astra 会话修改共享H/M。提案自己不能申请隐藏额外探测或调用。

研发期回归每候选最多6次：提案前M选3次；候选后根据实际diff风险关键词 camera/material/parts 或 geometry，候选M再选最多3次；探测额度后阶段为0。固定菜单：hierarchy_parts、known_support、mesh_intersection、material_preservation、composite_move、camera_framing。全部实际执行结果回到M的第二阶段，候选后决策进入下一次档案。不改变最终验收菜单。生成M执行失败记录为失败，不能外层人工修复。

## H/M轨迹与选择

允许 H-only/M-only/H+M。M-only复用相同H测量，accepted_H=false，不算H改善，允许有效M实际控制后续研发。后代接口在真实上下文执行测试，保存源码/diff/使用源。AST变化不作能力证据。每条有效候选可作为下个探索父代；最终H只依据Selection保留，包含H0。K2使用有效C1的M；无法执行的M不能当作有效后代。没有后续使用则不称递归能力证据。

只向研发给Selection预定聚合，不给原始图像/逐场景标签。门槛：执行成功数和功能通过数不低于同runH0，端到端Q效用比当前最佳提高>0.01；否则保留最佳，平局H0/先前最佳。0.01沿用V1透明保留阈值，不是V2重复波动估计，也不代表统计显著性。所有run选择冻结 selection_freeze.json 后统一Test。Test不回流本轮研发。历史曝光使严格盲测无法证明。

## 固定最终评价与边界

Q沿用V1：(clip(SSIM,0,1)+1-clip(LPIPS,0,1)+(1+clip(DINO,-1,1))/2)/3；PSNR也实测。缺测原始字段null。失败独立 task_utility_v2=0，全预定分母；条件质量仅完成场景，配对差只用双方成功；服务故障单列，不直接解释成算法退化。功能逐项 required/applicable/measured_pass/gate_pass。必需未执行/失败不能通过；非必需失败保留但不阻止候选。

最终固定：Blender能打开、>=3有限非空Mesh/有效矩阵、局部材质目标成功且非目标保持、预先要求组合移动时部件关系保持；预先要求组合结构的任务必须有可测的发射部件声明且完整；没有声明为required但不可执行，不能记N/A通过。未声明自然图像参考对象完整性、支撑语义与真实几何准确性为unknown。支撑为声明关系的归一化AABB近似；三角Mesh BVH相交为表面交叉，不是语义不合理穿插，也不测完全包含。两者均作补充，不能临时变硬约束。机械操作不等于文字编辑。

文字编辑在固定前2个Test场景、双方/两个run同一编辑器同一指令一次无修复，目标按固定生成对象规则，不声称参考语义定位。所有终测有效输出独立匿名astra评审，仅补充、不参与H选择。H0被选时同一产物别名复用，记录alias，不冒充新的独立重建。

## 可视化与后续

Figure1纳入按manifest顺序的全部Test场景/两个run；失败空缺。诊断板选择路径排序首个正式候选，不按成功选。编辑板首个可用Test机械产物，文字编辑另列。统计展示所有点，不将视角计独立重复。仅2研发重复，不做普遍优势/显著性或单调元能力提升结论。未完成相同陌生H起点冻结M回放前，不展示MetaImp曲线。没有恰当新任务或预算时记录pending，不扩展多方法实验。
'''
    (ROOT/'protocol.md').write_text(text)
    pilot.write_json(ROOT/'protocol_frozen.json',{'time':time.time(),'mechanisms':'tests/mechanism_acceptance.json','smoke':'tests/real_smoke.json','budget_forecast':cfg['pilot']['budget_forecast'],'formal_results_exist':False})
    print(json.dumps(cfg['pilot']['budget_forecast']))

if __name__=='__main__':main()
