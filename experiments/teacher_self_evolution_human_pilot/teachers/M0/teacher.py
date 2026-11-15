"""Initial language teacher. These shared policy functions may self-modify once."""
import json


def initial_hint(context):
    return (
        '你是三维重建学生的教师。查看真实参考图，为从零重建生成可操作的自然语言指导。'
        '先辨认构图、可见环境与主要对象，再决定有限指导空间中最值得强调的事项。'
        '不要生成场景代码，不提供数值参数表，不把猜测当成确定几何事实。'
        '返回JSON：draft为完整指导草稿；hint为最多1200个Unicode字符的最终指导；'
        'observations为依据；correction_record为本题纠错记录；change_reason说明优先级依据。'
        '所有字段为字符串；没有历史时纠错记录可以为空。不得给质量分数。\n'
        +json.dumps(context,ensure_ascii=False))


def update_hint(context):
    return (
        '你是同一题的教师。附件按顺序是原图和上一学生最终渲染（若有效）。'
        '根据真实结果、有界执行轨迹和旧指导，更新本题纠错记录，然后压缩为新指导。'
        '若没有渲染，明确无图，只能诊断实际错误。下一学生完全从零开始，'
        '看不到旧代码、参数、渲染或对话；指导必须独立可理解。'
        '区分观察事实与可能解释，保留有用指导、纠正被证据否定的建议。'
        '返回JSON字符串字段draft、hint、observations、correction_record、change_reason；'
        'hint最多1200个Unicode字符，纯自然语言，不含代码、文件路径、网址或参数表。'
        '不输出质量分数或比较其他教师。\n'+json.dumps(context,ensure_ascii=False))


def compress_hint(context):
    return ('把以下指导重新整理成最多1200个Unicode字符的独立自然语言Hint。'
            '保留对学生有用且有证据的优先级，删除重复和冲突，不能简单截断。'
            '返回相同JSON字段draft、hint、observations、correction_record、change_reason。\n'
            +json.dumps(context,ensure_ascii=False))


def self_modify(context):
    return (
        '你现在执行教师自身的单次共享程序研发。只依据以下两题各两轮实际开发记录，'
        '自行判断当前教师程序有什么通用问题，以及是否值得提出一个共享策略修改。'
        '不要假定必须修改某一策略；可以返回unchanged。学生固定，跨学生只传自然语言Hint。'
        '你可以改变教师诊断顺序、证据组织、纠错记录更新、压缩、停止或自修改策略。'
        '只能替换teacher.py，保持initial_hint(context)、update_hint(context)、'
        'compress_hint(context)、self_modify(context)四个纯Python函数，均返回调用提示字符串。'
        '可新增纯函数，允许json/re/math/textwrap/statistics/copy标准库；禁止文件读写、'
        '外部执行、网络、导入其他模块、修改学生或固定runner、预算、图片划分与Hint约束。'
        '不要硬编码题号、图像路径、特定场景答案或开发图专属分支。'
        'M1只携带共享源码，不携带开发题记忆。若仅改提示模板，change_type如实说明。'
        '返回JSON字符串字段decision（modify或unchanged）、teacher_py（完整文件）、'
        'evidence、expected_effect、change_type。不得宣称已有质量提升。\n'
        +json.dumps(context,ensure_ascii=False))
