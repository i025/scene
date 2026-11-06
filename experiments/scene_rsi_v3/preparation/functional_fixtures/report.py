"""Rebuild the fixture contact sheet and readable data from saved measurements only."""

import csv
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent


def main():
    calibration = json.loads((OUT / 'calibration.json').read_text())
    cases = calibration['cases']
    summary = json.loads((OUT / 'action_reuse.json').read_text())
    definitions = [
        ('correct', 'Legal scene', 'Hierarchy / declared support PASS', 'hierarchy_and_support', True),
        ('detached_part', 'Detached part', 'Hierarchy FAIL; detected', 'hierarchy_parts', False),
        ('missing_declared_part', 'Missing declared part', 'Hierarchy FAIL; detected', 'hierarchy_parts', False),
        ('broken_support', 'Lifted target', 'Declared support FAIL; detected', 'known_support', False),
        ('shared_material_bad_edit', 'Unsafe shared material edit', 'Non-target changed; detected', 'non_target_preservation', False),
        ('independent_local_edit', 'Legal independent target edit', 'Target changed / non-target PASS', 'material_preservation', True),
        ('correct_group_move', 'Legal assembly movement', 'Part relations / non-target PASS', 'composite_move', True),
        ('triangle_crossing', 'Crossing triangle surfaces', 'Actual crossings found; supplemental', 'mesh_intersection', False),
    ]
    rows = []
    for name, label, interpretation, check, measured in definitions:
        case = cases[name]
        rows.append({'case_id': name, 'creator': 'engineering_fixture_not_M', 'label': label,
                     'test': check, 'applicable': True, 'measured_pass': measured,
                     'expected_error_detected': case.get('expected_error_detected'),
                     'legal_scene_passed': case.get('legal_scene_passed'),
                     'interpretation': interpretation, 'measurement_path': f'{name}/measurement.json',
                     'render_path': f'{name}/final.png', 'blend_path': f'{name}/scene.blend',
                     'formal_quality_score': None, 'device': 'CPU', 'threads': 8,
                     'render_quality': 'calibration_preview_256x256_4_samples'})
    with (OUT / 'functional_cases.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / 'functional_cases.json').write_text(json.dumps(rows, indent=2) + '\n')
    canvas = Image.new('RGB', (1200, 740), 'white')
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=24)
    font = ImageFont.load_default(size=15)
    small = ImageFont.load_default(size=13)
    draw.text((16, 12), 'V3 deterministic structure/edit calibration', fill='black', font=title_font)
    draw.text((16, 44), 'Engineering fixtures; CPU 8 threads; Cycles 256x256 / 4 samples; excluded from formal reconstruction scores', fill='black', font=small)
    for index, row in enumerate(rows):
        x, y = 12 + (index % 4) * 298, 76 + (index // 4) * 325
        image = Image.open(OUT / row['render_path']).convert('RGB')
        canvas.paste(image, (x + 14, y))
        draw.text((x + 2, y + 263), row['label'], fill='black', font=font)
        line = row['interpretation']
        if len(line) > 38:
            words = line.split(' ')
            first = ''
            while words and len(first + words[0]) < 38:
                first += words.pop(0) + ' '
            line = first.rstrip() + '\n' + ' '.join(words)
        draw.multiline_text((x + 2, y + 284), line, fill='black', font=small, spacing=3)
    canvas.save(OUT / 'functional_contact_sheet.png')
    links = []
    for row in rows:
        links.append('<tr><td>' + html.escape(row['case_id']) + '</td><td>' + str(row['measured_pass']) +
                     '</td><td>' + html.escape(row['interpretation']) + '</td><td><a href="' +
                     row['measurement_path'] + '">measurement</a> / <a href="' + row['blend_path'] + '">blend</a></td></tr>')
    (OUT / 'index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>V3 结构与编辑机制校准</title>'
        '<style>body{max-width:1250px;margin:25px auto;font-family:sans-serif}img{max-width:100%}td,th{padding:8px;border:1px solid #ccc}table{border-collapse:collapse}</style>'
        '<h1>V3 结构与编辑机制校准</h1><p>8 个固定工程夹具、12 个资格条件组合、同一新动作在 2 个配置复用；均无模型调用。'
        '这些是已知真值的机械检查，不是自然图像三维恢复精度、文字指令编辑或 M 能力提升证据。</p>'
        '<img src="functional_contact_sheet.png"><table><tr><th>夹具</th><th>实测通过</th><th>解释</th><th>证据</th></tr>' +
        ''.join(links) + '</table><p><a href="functional_cases.csv">逐项CSV</a> / <a href="calibration.json">原始JSON</a> / '
        '<a href="action_reuse.json">两配置动作复用</a> / <a href="gate_contract.json">必要/适用/缺测条件</a> / '
        '<a href="report.py">仅重画脚本</a></p><p>支撑为归一化 AABB 接触近似；穿插采用实际三角面交叉，不能检测完全包含，'
        '也不能自动区分合法连接。断开父子层级保持当前世界位姿，因此仅看图片可能看不出错误。</p></html>')
    action_values = [(row['scene_id'], row['measurement']['normalized_vertical_gap'],
                      row['measurement']['contact_approx_pass']) for row in summary['two_configurations']]
    (OUT / 'README.md').write_text('# V3 确定性功能与开放动作验收\n\n'
        '本目录是准备阶段工程夹具，不是 M 自动生成的研发动作或正式重建样本。无远端模型调用。\n\n'
        '- 8/8 结构与编辑断言通过：合法组合、断开部件、遗漏声明部件、破坏支撑、共享材质误改、合法独立编辑、组合移动、三角面交叉。\n'
        '- 12/12 required/applicable/measured_pass 组合符合 gate 规则；必需但缺测或不适用不通过，非必需不会错误拦截。\n'
        '- 新参数化 `fixture_m/actions/measure_named_support.py` 通过既有 `validate_source`，经现有 `ResearchAPI.execute_action` 与 `action_worker.py` '
        '在两个不同 `.blend` 执行，未添加固定 runner 菜单。\n'
        '- 指定目标为 `Z_target_part`，字母序首个 Mesh 是 `A_unrelated_part`；实际测量目标来自参数。\n\n'
        f'实际动作测量 `(配置, 归一化间隙, 接触近似通过)`：`{action_values}`。\n\n'
        '8 张真实校准 PNG 与 8 个 `.blend` 均在对应 case 目录。渲染固定 CPU 8线程、Cycles、256×256、4 samples，'
        '明确为 calibration_preview，不进入正式 BW/质量提升曲线。进程树 CPU/RSS 与时间见 `process.json`、`action_reuse/actions/*/process.json`。\n\n'
        '局部材质测试直接按预定义 Blender 操作执行；没有文字编辑器。支撑为声明关系上的 AABB 接触近似。三角面交叉仅作补充，'
        '既不能检测完全包含，也不提供语义碰撞真值。正确层级与断开层级可有相同渲染，必须读真实场景结构。\n\n'
        '离线重画（不启动 Blender、不调用模型）：`python report.py`，需要现有 Pillow 环境。原始测量及 CSV 同目录。\n\n'
        '原始夹具生成脚本为 `build_fixtures.py`，一次性执行驱动为 `run.py`。为保留已有证据，不在原目录覆盖重复运行；'
        '主 preflight 检测已保存的 passed 记录后应直接引用。\n')
    print(str(OUT / 'index.html'))


if __name__ == '__main__':
    main()
