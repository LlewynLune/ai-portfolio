import json,hashlib
from videoguard.experiment import ROOT


def run():
    d=ROOT/'artifacts/calibration-depth';r=json.loads((d/'results.json').read_text());pct=lambda x:'N/A' if x is None else f'{x*100:.2f}%'
    lines=['# VideoGuard校准纵深：实测报告','',
    '## 判断：不能用覆盖率一个数证明“更可靠”','',
    '原v0.6 LAC分位重算一致，不能据单次83.5%就把原因归为代码错误。24轮LAC平均包含率接近90%，但仍有轮间波动。随机化APS与保守crossing结果不同；后者可通过巨大集合提高包含率，丧失唯一答案信息。补全top1消除空集但不消除错估。','',
    '模型/温度冻结，自建合成媒体，所有新方法均只是诊断对照。没有真实视频效果、生产保证或原创算法声明。','',
    '## 原分位复算与重复验证','',
    f"原250校准阈值绝对差：{r['original_calibration']['threshold_abs_difference']:.12g}；该校准集自身包含率{pct(r['original_calibration']['set_metrics']['coverage'])}。",'',
    '|方法|24轮平均包含率|轮间标准差|5/50/95%分位|低于90%的轮数|平均大小|平均空集|','|---|---:|---:|---|---:|---:|---:|']
    for k,v in r['repeat_summary'].items():lines.append(f"|{k}|{pct(v['mean_coverage'])}|{pct(v['sd_coverage'])}|{' / '.join(map(pct,v['coverage_quantiles_05_50_95']))}|{v['replicates_below_90']}/24|{v['mean_set_size']:.3f}|{pct(v['mean_empty_rate'])}|")
    lines+=['','每轮250新校准＋400新测试，不是固定池bootstrap；每轮模型相同，24轮不代表24独立模型。LAC与对数LAC一致，不支持“改对数就解决了”的宣称。','',
    '## 主实验：1000新ID校准＋八组各600新测试','',
    '|条件|方法|真值包含率|平均大小|空集|单例比例|单例错误率|','|---|---|---:|---:|---:|---:|---:|']
    for group,g in r['conditions'].items():
        for k,v in g['sets'].items():lines.append(f"|{group}|{k}|{pct(v['coverage'])}|{v['mean_size']:.3f}|{pct(v['empty_rate'])}|{pct(v['singleton_rate'])}|{pct(v['singleton_error'])}|")
    lines+=['','legacy_lac是原250校准阈值，所有方法使用同一个新测试池。silent/periodic存在观测可识别性限制；drift真值仅前半段，不能将该组包含率写成漂移检测F1。','',
    '## 拒估后的风险必须带上样本数','',
    '|条件|固定概率门限0.9保留数|保留比例|观察错误率|点态95%上界|21门限同时上界|','|---|---:|---:|---:|---:|---:|']
    for k,v in r['conditions'].items():
        a=v['all_confidence_risk'][18];lines.append(f"|{k}|{a['accepted']}|{pct(a['coverage'])}|{pct(a['error_rate'])}|{pct(a['upper95'])}|{pct(a['simultaneous_upper95'])}|")
    lines+=['','门限0.9仅预先固定展示，不按这些测试结果调参；完整21门限曲线见results.json和Demo。点态上界不能用于事后挑选最佳门限；同时上界保守调整亦只在IID二项假设下解释。','',
    '## 零错误的样本量代价','',
    '|保留数|观察错误数|一侧95%错误率上界|','|---:|---:|---:|']
    for a in r['zero_error_illustration']:lines.append(f"|{a['accepted']}|0|{pct(a['upper95'])}|")
    lines+=['','没有样本时上界为100%，不是0%。真实视频非IID、分布迁移、声源歧义会使二项解释失效。','',
    '## 可复算证据','',
    '- [全体新测试概率、标签、媒体哈希及随机u](probability-pools.json)。','- repeat-00.json到repeat-23.json：每轮独立校准/测试输入与结果。','- [全部结果与按类别覆盖](results.json)。','- [当前新增证据哈希](checksums.json)，原v0.6哈希不改。','',
    f"本轮实际墙钟时间{r['seconds']:.2f}秒；环境{json.dumps(r['environment'],ensure_ascii=False)}。不等于端到端服务性能。",'',
    '## 下一步','',
    '优先补授权真实闪光/打击数据与按会话隔离评测；未经真实验证，不改原模型的生产性质或真实输入强制复核。若进一步做定位，应建立窗口漂移事件真值、匹配容差与检测F1，而非继续只报首半段标签准确率。','']
    (d/'REPORT.md').write_text('\n'.join(lines))
    paths=['videoguard/prediction_sets.py','videoguard/calibration_study.py','enhance_demo.py','build_depth_report.py','tests/test_prediction_sets.py','check_depth_js.py']
    codeh={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths if (ROOT/n).is_file()}
    (d/'code-checksums.json').write_text(json.dumps(codeh,indent=2)+'\n')
    h={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file() and p.name not in ['checksums.json','tests.log']}
    (d/'checksums.json').write_text(json.dumps(h,indent=2)+'\n')
    print('Wrote calibration-depth report and hashes')
if __name__=='__main__':run()
