"""Generate report from actual frozen numerical outputs, never hardcode wins."""
import json,hashlib
from videoguard.experiment import ROOT


def run():
    d=ROOT/'artifacts';r=json.loads((d/'results.json').read_text());c=json.loads((d/'contrastive-results.json').read_text());g=json.loads((d/'diagnostics.json').read_text())
    pct=lambda x:f'{x*100:.2f}%'
    lines=['# VideoGuard-Lab：实际实验报告','',
    '## 结论：深度在于可反驳，不在于包装满分','',
    '主模型在ID下未超越相关性基线；复杂特征在曝光干扰组相对raw correlation有帮助，但onset相关性在该组更好，不能说复杂特征胜过所有简单基线。在噪声/漂移等组也未稳定胜出。双塔学习未带来稳定优势。校准预测集覆盖在ID也低于名义90%，OOD下降更大；拒估机制仍会放过无对应结构的样本。','',
    '全部实验为自建合成RGB/音频；不代表Seedance、Claude、LatentSync或真实自然视频成绩。','',
    '## 1. 数据与训练','',
    f"训练/验证/校准/主测试样本数：{r['sizes']}。三MLP optimizer seeds7/19/31；三个双塔seeds43/57/71。主模型seed7固定；按验证NLL选checkpoint。前半校准仅温度，后半仅阈值/集合。数据生成开发修改与pilot已明确披露，不称预注册盲测。",'',
    '主训练日志：'+', '.join(f'[seed {x}](training-seed-{x}.json)' for x in [7,19,31])+'. 双塔：[完整结果](contrastive-results.json)。','',
    '## 2. 同场基线，不默认学习更强','',
    '|条件|n|共享MLP|原始相关性|onset相关性|双塔seed43|MLP − raw配对95%CI|','|---|---:|---:|---:|---:|---:|---|']
    for name,v in r['conditions'].items():
        ci=v['mlp_minus_raw_xcorr']['ci_95_percentile'];ct=c['seeds'][0]['conditions'][name]['accuracy']
        lines.append(f"|{name}|{v['n']}|{pct(v['accuracy'])}|{pct(v['baselines']['raw_xcorr']['accuracy'])}|{pct(v['baselines']['onset_xcorr']['accuracy'])}|{pct(ct)}|[{ci[0]*100:.2f}, {ci[1]*100:.2f}] pp|")
    lines+=['','配对bootstrap单元为clip，1000次；跨组同生成器结果不视作现实泛化。drift标签为前半段延时，后半段已变，单值准确率不应解释为完整漂移检测成绩。静音/周期亦存在可识别性问题。','',
    f"仅raw correlation一维的同架构消融在ID精确率为{pct(r['ablation_raw_correlation_only']['accuracy'])}。ID不足以证明丰富特征必要。",'',
    '## 3. 三种子重复','',
    '|MLP seed|选定epoch|温度|ID精确率|NLL|ECE|','|---|---:|---:|---:|---:|---:|']
    for run in r['runs']:
        v=run['test'];lines.append(f"|{run['optimizer_seed']}|{run['selected_epoch']}|{run['temperature']:.4f}|{pct(v['accuracy'])}|{v['nll']:.6f}|{v['ece_10_equal_width']:.6f}|")
    lines+=['','|双塔seed|选定epoch|ID|噪声|曝光干扰|漂移|','|---|---:|---:|---:|---:|---:|']
    for run in c['seeds']:
        v=run['conditions'];lines.append(f"|{run['seed']}|{run['selected_epoch']}|{pct(v['id']['accuracy'])}|{pct(v['noise']['accuracy'])}|{pct(v['distractor']['accuracy'])}|{pct(v['drift']['accuracy'])}|")
    lines+=['','更复杂的可学习时序编码器是实际训练对照，不是改进承诺；未按测试选择模型或seed。','',
    '## 4. 校准失效也必须报告','',
    '|条件|raw NLL|温度后NLL|温度后ECE|名义90%预测集实测覆盖|平均集合大小|','|---|---:|---:|---:|---:|---:|']
    for name,v in r['conditions'].items():lines.append(f"|{name}|{v['raw_uncalibrated']['nll']:.5f}|{v['nll']:.5f}|{v['ece_10_equal_width']:.4f}|{pct(v['prediction_set_coverage'])}|{v['prediction_set_mean_size']:.3f}|")
    lines+=['','**不能声称已实现90%覆盖保证。** 校准集合简单且有限、概率极端、分布差异/开发选择都限制理论条件；结果原样保留。空集不是自动扩成唯一答案，而是拒估。','',
    '## 5. 固定诊断门限与滑窗一致性','',
    '后续独立240样本/组；概率floor0.9、唯一候选、事件证据充足、无≥100ms高置信局部矛盾才保留。不是风险保证。','',
    '|条件|样本|保留估计|保留比例|保留部分误差率|窗口矛盾率|','|---|---:|---:|---:|---:|---:|']
    for name,v in g['conditions'].items():lines.append(f"|{name}|{v['n']}|{v['accepted']}|{pct(v['coverage'])}|{'N/A（全拒）' if v['accepted_error'] is None else pct(v['accepted_error'])}|{pct(v['window_disagreement_rate'])}|")
    lines+=['','“保留部分0错误”并非全样本0错误；大量拒估换取保守输出。窗口规则存在误拒，不具备完整事件定位F1或IoU证明。','',
    '## 6. 负对照：有拒估机制不等于可靠','',
    '|负对照|n|仍被保留唯一估计的比例|解释|','|---|---:|---:|---|']
    for name,v in g['negative_controls'].items():lines.append(f"|{name}|{v['n']}|{pct(v['incorrect_unique_estimate_rate'])}|{'低视觉证据下仍接受，不一定延时错误，不能当错误率' if name=='low_visual_evidence' else '缺乏有效稳定对应，接受即不受支持的唯一估计'}|")
    lines+=['','无对应声源、反转、超范围等对照不是自然视频全集；0漏过不能证明普遍安全。负对照逐样本记录同时保留。','',
    '## 7. 工程核验','',
    '- RGB/PCM哈希与base seed隔离；推断不读取标签/events。','- 主模型和双塔梯度有限差分，概率归一化、延时符号、非循环shift、静音/NaN/短音频边界。','- [JS/Python全特征/参数/决策一致性](js-parity.json)。','- [自建MP4编码/解码烟雾测试](media-smoke.json)，不代表真实视频效果。','- [全部冻结证据哈希](checksums.json)。','',
    '主实验生成/训练/评价总墙钟时间：'+f"{r['wall_seconds']:.2f}秒；双塔流程{c['wall_seconds']:.2f}秒。仅当前环境实测，不是标准性能基准。主模型批量推断计时不包含解码与特征提取，不能换算为端到端媒体吞吐。",'',
    '环境：'+json.dumps(r['environment'],ensure_ascii=False)+'.','',
    '## 8. 未完成的真实世界验证','',
    '没有授权自然拍摄数据、专家标注、唇形/语义/物理一致性、公开benchmark排名或生产测试。真实视频入口强制人工复核；不会修改源媒体、调用生成API或自动发布。下一步应先采集按会话隔离的真实闪光/打击数据，而不是继续换模型名。','',
    '## 9. 可回查失败','',
    '原始results.json包含每组前15个失败的seed、媒体哈希、真值/预测/置信度；完整预测见各组predictions.json。pilot-easy-results.json记录最初太简单的满分实验。','']
    (d/'REPORT.md').write_text('\n'.join(lines))
    codehash={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*.py') if '__pycache__' not in p.parts}
    (d/'code-checksums.json').write_text(json.dumps(codehash,indent=2)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file() and p.name not in {'checksums.json','tests.log'}}
    (d/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print('Generated report from measured results')
if __name__=='__main__':run()
