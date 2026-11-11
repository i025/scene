# A03 暂停后的只读记录与成本清算

审计时间：2026-11-07T00:10:23.817230+00:00。只读分析，未应用协议、未改主源码/状态/分数，模型与Blender调用均为0。

真实 budget.current：115 个CLI会话，257 渲染扣额，已知输入 8,221,059 / 输出 290,983 token。usage已知 114、未知 1；未知不计成零。研究阶段剩余已知输入额度 19,778,941，研究帽28M；全局帽40M不变。

## 最小记录方案

保存H01/bw0031/r1全部原件：它实际1次CLI，2次runtime ask尝试，首个构建/渲染成功；随后调用被operator pause拦截。旧attempt是operator_interrupted、primary=false，不把它解释成算法失败或第二次真实调用。
显式矩阵：H_start与H01的bw0031选repeat2，另两张Selection选repeat1；H02至H10三图均repeat1。repeat2是ID，每个H仍只有3个主场景槽，不是每图两次抽样。新repeat2失败也不能回退旧repeat1。新矩阵在新分数前冻结，理由仅为统一operator暂停的执行机会。
raw表保留所有attempt和原始值，派生is_primary_for_selection、attempt_role、excluded_primary_reason、selection_plan_version、evaluator_evidence_version。主均值/分母/图/资格统一只用primary；调用、token、渲染成本仍计全部raw。无record.json的中断用operator attempt sidecar列出，不能补造测量。
当前analyze尚未有primary筛选；get_scenes读所有repeat，group_statistics会分母3却叠加repeat1+2，quality/function图亦会混入。须统一分开raw与primary入口。新A03评价修订另留旧3baseline和原round0，不改历史分数；候选与baseline的selection入口、boundary入口均读取同一显式矩阵。

## 取消一组边界复评能否支付本次补救

三个实际Selection judge输入分别为242,406 / 284,542 / 324,631；完整三图一次851,579。取消同一边界案例的父/子两端三图评审，历史率预计节约1,703,158输入token。15个完整H场景平均3个CLI、92,466.4输入、11,587.2输出；新lighting的实际usage尚未测得。
|方案|新H场景|新judge|预计新增input|较取消6judge的input余量|净CLI增量（H均值）|
|---|---:|---:|---:|---:|---:|
|Canonical primary only|2|4|1,278,917.8|424,240.2|4|
|Also A03-rejudge obsolete baseline bw0031/r1 as raw-only|2|5|1,521,323.8|181,834.2|5|

最小主统计只需4个新judge：新H_start/bw0031/r2与两张复用baseline共3，加H01/bw0031/r2共1。这里已包含新两H的两次BW，不能把baseline/r2再重复计。若另给废弃baseline/r1补A03 raw-only评分，则是5judge情形，非主比较必需。取消边界只省judge；不省新H输出与新渲染，预计两新H最多30帧预算扣额，已有视图的边界复评本来不增加视图。服务重试不含在这些均值预测中。

## 十轮余程重新核算

保守按后续H都变化并保留：尚需27个后续开发H场景+30个候选Selection场景+1个新baseline/bw0031/r2=58个完整H生成；第1轮M已有1个真实提案并复用，后9轮最多27个M会话。3个A03 baseline judge+30个候选judge+每个剩余边界案例6judge。20次校准已消费，不再重复作为未来成本。

|剩余边界案例|后续M输入倍率|预计研究总input|28M余量|
|---|---:|---:|---:|
|1|1|28,859,104.2|-859,104.2|
|1|1.25|29,910,220.9|-1,910,220.9|
|0|1|27,155,946.2|844,053.8|
|0|1.25|28,207,062.9|-207,062.9|

**结论：取消一组6judge在历史率下预计足以覆盖局部补救输入token，但不能据此保证完整十轮预算。** 继续保留一组边界时，当前率完整余程预计研究input28.859M，超过28M约0.859M；取消所有未执行边界后均值预测约27.156M，但M输入1.25倍仍约28.207M。新lighting元数据、未来场景复杂度、重试与未知usage均可能增加成本；这些不是费用或硬上界证明。
阈值2不变、不依据Selection调整容差；A02校准原记录沿用，但A03 lighting修订没有重新量化噪声，应明确此局限。工程师不重采M或替候选改思路。

完整来源、显式11×3矩阵、15个H原始token合计、实际session路径与敏感性见 [budget_A03.json](budget_A03.json)。
