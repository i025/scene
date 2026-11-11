"""Offline M07 source/trace review; no model, Blender or new experiment."""
import csv
import json
import os
from pathlib import Path
import textwrap

for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS']:
    os.environ[key] = '1'
os.environ['MPLCONFIGDIR'] = '/tmp/scene_rsi_v3_matplotlib'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def source_files(folder):
    return {str(p.relative_to(folder)): p.read_text() for p in folder.rglob('*')
            if p.is_file() and p.suffix in {'.py', '.json'}}


def material_rows(measured):
    rows = []
    for obj in measured['objects']:
        if 'status' in obj:
            rows.append({'object_id': obj['object_id'], 'status': obj['status']})
            continue
        for material in obj['materials']:
            rows.append({'object_id': obj['object_id'], 'mesh_count': obj['mesh_count'],
                         'material': material['name'], 'material_mesh_users_in_group': material['mesh_count'],
                         'shader_nodes': material['shader_nodes']})
    return rows


def report():
    initial = ROOT / 'initial_m'
    descendant = ROOT / 'candidates/C07/M'
    before, after = source_files(initial), source_files(descendant)
    changed = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
    source = (descendant / 'actions/appearance_audit.py').read_text()
    rounds = {t: read(ROOT / 'rounds' / f'{t:02d}/record.json') for t in [7, 8, 9]}
    round10 = read(ROOT / 'rounds/10/record.json')
    actions = []
    rows = []
    for t in [7, 8, 9]:
        decisions = read(ROOT / 'meta_traces' / f'round{t:02d}/decisions.json')
        for index, folder in enumerate(sorted((ROOT / 'meta_traces' / f'round{t:02d}/actions').iterdir())):
            request = read(folder / 'action_request.json')
            measurement = read(folder / 'measurement.json')
            observation = read(folder / 'observation.json')
            process = read(folder / 'process.json')
            scene_id = request['scene_id']
            image_folder = ROOT / 'results' / rounds[t]['H_parent'] / 'development' / scene_id / '1'
            item = {'round': t, 'action_number': index + 1, 'M_entry_used': rounds[t]['M_program_used'],
                    'request': request, 'measurement': measurement,
                    'next_decision_after_observation': decisions[index + 1],
                    'source_matches_M07': (folder / 'action.py').read_text() == source,
                    'observation_status': observation['status'], 'process_seconds': process['seconds'],
                    'new_diagnostic_renders': 0, 'raw_folder': str(folder.relative_to(ROOT)),
                    'reference': str((image_folder / 'reference.png').relative_to(ROOT)),
                    'current_render': str((image_folder / 'final.png').relative_to(ROOT))}
            actions.append(item)
            rows.append({'round': t, 'action_number': index + 1, 'scene_id': scene_id,
                         'M_parent': rounds[t]['M_parent'], 'object_ids': request['parameters']['object_ids'],
                         'expectation': request['expectation'], 'status': observation['status'],
                         'source_matches_M07': item['source_matches_M07'], 'new_diagnostic_renders': 0,
                         'seconds': process['seconds'], 'next_decision': decisions[index + 1]['decision'],
                         'next_analysis': decisions[index + 1]['analysis'], 'raw_folder': item['raw_folder']})
    audit = {'scope': 'Offline source and saved trace review; not a frozen meta-capability replay',
             'changed_files': changed, 'entrypoint_identical': before['meta.py'] == after['meta.py'],
             'new_action_lines': len(source.splitlines()),
             'change_class': 'Astra-authored reusable read-only action plus action-index registration; planning entry and its prompt unchanged',
             'index_registration': read(descendant / 'actions_index.json')['actions/appearance_audit.py'],
             'source_diff': 'candidates/C07/M.diff', 'action_count': len(actions),
             'subsequent_M07_action_count': sum(a['round'] > 7 for a in actions),
             'actions': actions, 'rounds': rounds,
             'H08_diff': 'candidates/C08/H.diff',
             'H08_validation_delta': rounds[8]['selection']['S_BW'] - read(ROOT / 'rounds/04/record.json')['selection']['S_BW'],
             'H09_new_source_candidate': rounds[9]['new_source_candidate'],
             'round10': round10, 'best_H_created_before_M07': True,
             'retained_H_updates_after_M07': sum(read(ROOT / 'rounds' / f'{t:02d}/record.json')['H_accepted'] for t in [8, 9, 10]),
             'causal_action_benefit_established': False, 'meta_capability_improvement_established': False,
             'limitations': ['No action intervention or diagnostic render was requested',
                            'Shader socket defaults are not evaluated shading; linked inputs may override them',
                            'No controlled counterfactual M000 comparison or completed frozen replay',
                            'Action-index status created_pending_reuse is catalog metadata, not execution evidence; traces establish actual reuse']}
    metrics = ROOT / 'metrics';metrics.mkdir(exist_ok=True)
    (metrics / 'M07_review.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    with (metrics / 'M07_action_review.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]));writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                         for k, v in row.items()} for row in rows)
    # Every actual appearance audit, ordered chronologically; no score-based selection.
    fig, axes = plt.subplots(len(actions), 4, figsize=(18, 3.7 * len(actions)))
    for axes_row, action in zip(axes, actions):
        for axis in axes_row:axis.axis('off')
        for axis, key, title in [(axes_row[0], 'reference', 'Development reference'),
                                 (axes_row[1], 'current_render', 'Actual H04 author view')]:
            with Image.open(ROOT / action[key]) as image:axis.imshow(image.convert('RGB'))
            axis.set_title(f"R{action['round']} A{action['action_number']}: {title}", fontsize=9)
        measurements = material_rows(action['measurement'])
        excerpts = []
        for material in measurements[:3]:
            excerpt = {'object': material['object_id']}
            if 'shader_nodes' in material:
                excerpt['material'] = material['material']
                excerpt['inputs'] = [{key: ('linked' if value['linked'] else
                                           round(value['value'], 3) if isinstance(value['value'], (int, float))
                                           else [round(v, 3) for v in value['value']])
                                     for key, value in node['inputs'].items()
                                     if key in ['Roughness', 'Metallic', 'Emission Strength', 'Base Color']}
                                    for node in material['shader_nodes']]
            else:excerpt['status'] = material['status']
            excerpts.append(excerpt)
        facts = ('TARGETS: ' + ', '.join(action['request']['parameters']['object_ids'])
                 + '\nACTUAL VALUES (excerpt): ' + json.dumps(excerpts, ensure_ascii=True)
                 + f"\nLIGHTS: {len(action['measurement']['lights'])}; WORLD: "
                 + str([round(world['strength'], 3) for world in action['measurement']['world_backgrounds']])
                 + '\nRead-only; no intervention render. Linked defaults are not evaluated shading.')
        axes_row[2].text(0, 1, '\n'.join(textwrap.wrap(facts, 48))[:1400], va='top', fontsize=8)
        next_decision = action['next_decision_after_observation']
        outcome = ('M07 action retained; H unchanged' if action['round'] == 7 else
                   'H08 rejected: BW 37.895 -> 36.437' if action['round'] == 8 else
                   'Stop; unchanged H/M; no new H candidate')
        detail = ('EXPECTED: ' + action['request']['expectation'][:250] + '\nNEXT: '
                  + next_decision['decision'] + '\n' + next_decision['analysis'][:550]
                  + '\nROUND OUTCOME: ' + outcome
                  + '\nTrace source: ' + action['raw_folder'])
        axes_row[3].text(0, 1, '\n'.join(textwrap.wrap(detail, 48)), va='top', fontsize=8)
    fig.suptitle('All six saved appearance audits: new action in round 7, M07 reuse in rounds 8 and 9', fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .985))
    (ROOT / 'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT / 'figures/M07_action_evidence.png', dpi=125);plt.close(fig)
    text = f'''# M07 源码与执行轨迹审查

本报告只读取本轮已有源码、diff、真实动作输入输出和验证记录；没有调用模型或 Blender。审查覆盖全部六次 appearance_audit 执行，按第7、8、9轮时间顺序展示，不按效果挑选案例。

M07 与 M000 的 `meta.py` 完全相同；初始策略提示也未改变。真实差异是新增39行的 `actions/appearance_audit.py`，并在 `actions_index.json` 注册动作。它是研究动作库扩展，不是规划入口改写或普通代码整理。Astra在第7轮提出并保留了此M-only后代，共享H仍为H04。索引里残留的 `created_pending_reuse` 是目录元数据，不能当作实际执行结论；以下调用轨迹才是执行证据。

动作接收明确的 `object_ids`，检查这些对象及其Mesh后代的材质槽、Principled/Emission节点默认值与linked标志、材质在组内的使用次数，同时读取真实灯光、World背景、色彩管理、曝光和gamma。对象不存在时写missing。它不改几何、相机、材质或灯光，不渲染，不求解链接节点网络，也不测量像素亮度、可见性或唯一原因。

## 第7轮：动作创建与两场景复用

仓库 left_rack/left_goods/skylight 与教室 desk_0_1/stage/foreground_blue 的两次真实执行，观察到部分暗色材质仍完整、零发光，因而未把渲染发白直接归因于未赋材质。随后提交仅保留动作的M-only变更；这证明动作能够复用，不证明质量改进。

## 第8轮：动作 → 共享H补丁 → 负验证结果

问题：厨房画面缺乏预期的玻璃/金属区分，但也存在照明、方向与几何解释。M07指定 cooktop/kitchen/upper_cabinets；实际节点中选定材质保留约0.65 roughness、0 metallic。下一步并非认定唯一原因，而是在餐厅 table_04/chair_00/pendant_00/rear_glazing 上作第二次只读检查，观察到多种表面仍为默认响应，同时部分玻璃已显式发光。

随后M提出H08：在 `policy.py` 增加MATERIAL_GUIDANCE，要求实现图像支持的材质差异、检查共享材质用户、必要时复制材质，并打印最终Shader值。它改变了跨图重建提示和实现检查指导，没有直接替场景设置一组统一材质参数；代码执行入口与迭代预算不变。

独立Selection三图的H08 BW均值为 {rounds[8]['selection']['S_BW']:.6f}，父H04为 {read(ROOT / 'rounds/04/record.json')['selection']['S_BW']:.6f}，差值 {audit['H08_validation_delta']:+.6f}，未达到冻结的+2分晋升门槛，故拒绝。三图执行/必要功能资格通过不等于视觉收益。这条链说明观测与后续补丁一致，不能证明动作因果有效；本例没有产生更好的H。

## 第9轮：观测反驳假设，停止研发

M07指定教室 left_green_panel/right_green_panel/blue_lower_wall/wooden_top/wall_hook。实际测量确认两个面板分配不同的程序材质，Base Color是linked，反驳了该次记录中的错配材质猜测；默认颜色不能当成最终纹理颜色。后续转向宿舍 diffuser_0/shade_0/floor/lower/door_0，确认灯罩扩散面Emission Strength为0而场景另有Area灯。

M最终认为这些信息仍无法区分遮挡、位置与照明效应，不支持跨图统一修改，选择stop。第9轮是unchanged，没有生成新的H候选，没有Selection拒绝或通过事件，不应包装为“又一次修复成功”。

## 能证明与不能证明的内容

能证明：新动作源码真实保存；第7轮两场景执行后被保留；第8、9轮又实际执行四次，执行副本与M07源码一致；真实观测进入后续M决策。共六次只读检查，额外诊断渲染为0。

不能证明：M07比M000更强、主动干预的因果收益、一般递归能力提升。没有同一陌生H起点和相同档案下的已完成冻结回放。H08验证下降，H09未改动；动作被调用、动作数增长和M路径出现在父版本中均不足以证明能力增强。

最终保留的H04在第4轮已产生，早于第7轮M07诞生，因此H04的终测收益不能归因于M07。第10轮仍以M07为父版本，但没有执行新增appearance动作；它的H10候选Selection BW为 {round10['selection']['S_BW']:.6f}，也被拒绝。M07出现后的第8–10轮没有任何H更新被保留。这是本条轨迹的负结果，不能据此证明M07普遍弱于M000。

![全部真实动作证据](../figures/M07_action_evidence.png)

原始数据：[完整审查JSON](../metrics/M07_review.json)、[逐动作CSV](../metrics/M07_action_review.csv)。源码与轨迹：`initial_m/`、`candidates/C07/M.diff`、`candidates/C07/M/`、`meta_traces/round07..09/actions/`、`candidates/C08/H.diff`、`candidates/C08/proposal.json`、`candidates/C09/proposal.json`、`rounds/07..09/record.json`。

图中只有已有开发参考/真实重建和原生测量文字，没有新生成的干预图或因果示意图。离线重跑：`python audit_m07.py`。
'''
    (ROOT / 'reports/M07_REVIEW_ZH.md').write_text(text)
    print(json.dumps({'status': 'completed', 'changed_files': changed, 'actions': len(actions),
                      'new_model_calls': 0, 'new_Blender_jobs': 0}))


if __name__ == '__main__':
    report()
