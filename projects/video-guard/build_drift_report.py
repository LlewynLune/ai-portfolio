import json,hashlib
from videoguard.experiment import ROOT


def run():
    d=ROOT/'artifacts/drift-localization';r=json.loads((d/'results.json').read_text());fmt=lambda v:'N/A' if v is None else f'{v:.3f}'
    lines=['# 因果音画漂移定位：实测报告','',
    '## 判断：定位更有信息，但检测仍有延迟与漏检','',
    '旧模型冻结，新增结构性变化点真值与因果尾随窗。不能只报“发现漂移”：同时报告漏检、误报、定位误差与发警报延迟。本轮为自建RGB/PCM，未做真实数据泛化。','',
    '## 固定协议与参数选择','',
    r['protocol'], '',
    '验证160个；十组各120测试；三次独立重复各200。窗口32帧/步进4帧；模型/温度不重训。', '',
    '|方法|置信门限|最小变化帧|确认次数|','|---|---:|---:|---:|']
    for m,c in r['configs'].items():lines.append(f"|{m}|{c['confidence']}|{c['min_jump']}|{c['patience']}|")
    lines+=['','相关性置信与softmax概率不是同一含义；门限在相同验证集独立选择，不按测试调。','',
    '## 总体：事件匹配与时间代价','',
    '|方法|P|R|F1|TP / FP / FN|匹配定位MAE ms|匹配警报延迟中位 ms|匹配警报P90 ms|','|---|---:|---:|---:|---|---:|---:|---:|']
    for m,v in r['overall'].items():lines.append(f"|{m}|{v['precision']:.3f}|{v['recall']:.3f}|{v['f1']:.3f}|{v['tp']} / {v['fp']} / {v['fn']}|{fmt(v['matched_localization_mae_ms'])}|{fmt(v['matched_alarm_delay_median_ms'])}|{fmt(v['matched_alarm_delay_p90_ms'])}|")
    pair=r['mlp_minus_onset_exact_clip_success'];lines+=['',f"MLP相对onset的完整clip成功率差：{pair['difference']:.4f}，配对95%bootstrap CI {pair['ci95']}。成功定义为所有真值匹配且无额外警报，无变化视频需无警报。不能与事件F1差混淆。",'',
    '时间只统计匹配事件，FN单列。窗口中心的回溯定位不是报警可得时刻；警报用窗口结束。默认800ms容差，不将其隐藏。','',
    '## 十类失败分组','',
    '|组|方法|F1|TP|FP|FN|无变化视频误报率|定位MAE ms（匹配）|','|---|---|---:|---:|---:|---:|---:|---:|']
    for g,methods in r['groups'].items():
        for m,v in methods.items():lines.append(f"|{g}|{m}|{v['f1']:.3f}|{v['tp']}|{v['fp']}|{v['fn']}|{fmt(v['stable_false_alarm_rate'])}|{fmt(v['matched_localization_mae_ms'])}|")
    lines+=['','stable/silent组F1为0因没有正事件，应看误报；不能写为检测性能0%。ramp按实际整数子变化标注，多个变化可能被检测器合并。quiet_gap附近无事件，使结构性时间不可直接辨认。','',
    '## 容差敏感性：精确定位不能靠放宽容差','',
    '|±容差 ms|raw F1|onset F1|MLP F1|','|---:|---:|---:|---:|']
    for tol,methods in r['tolerance_sweep'].items():lines.append(f"|{tol}|{methods['raw']['f1']:.3f}|{methods['onset']['f1']:.3f}|{methods['mlp']['f1']:.3f}|")
    lines+=['','## 三次独立重复','',
    '|重复|raw F1|onset F1|MLP F1|','|---:|---:|---:|---:|']
    for rep in r['repeats']:lines.append(f"|{rep['repeat']}|{rep['methods']['raw']['f1']:.3f}|{rep['methods']['onset']['f1']:.3f}|{rep['methods']['mlp']['f1']:.3f}|")
    lines+=['','固定验证参数，不重复选最佳配置；每重复200个独立media seed。','',
    '## 可核验材料','',
    '- [验证全参数表](validation-grid.json)与[验证逐样本轨迹](validation-records.json)。','- 每组xxx-records.json：media seed/哈希、变化点、全延时真值、因果窗口轨迹。','- [十组示例与原始报警](examples.json)。','- [JS/Python报警时间与边界一致性](js-parity.json)。','- [冻结哈希](checksums.json)。','',
    f"本轮耗时{r['seconds']:.2f}秒，包含生成与评价；不是生产端到端时延基准。",'',
    '## 明确边界','',
    '没有真实拍摄数据、实验设备、专用DSP硬件、多声源定位或生产发布。因果前缀不泄漏测试未来，但模型本身在短窗口迁移仍会错；静默、渐变、多个变化应单独复核。下一阶段需要授权真实媒体与会话隔离标注，不是宣称本项目已达真人或工业要求。','']
    (d/'REPORT.md').write_text('\n'.join(lines))
    files=['videoguard/drift.py','videoguard/drift_data.py','videoguard/drift_experiment.py','localize_demo.py','check_drift_js.py','build_drift_report.py','tests/test_drift.py']
    (d/'code-checksums.json').write_text(json.dumps({n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files},indent=2)+'\n')
    (d/'checksums.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file() and p.name not in ['checksums.json','tests.log']},indent=2)+'\n')
    print('Wrote causal localization report')
if __name__=='__main__':run()
