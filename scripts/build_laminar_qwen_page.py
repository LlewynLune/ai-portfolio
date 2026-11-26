"""Build self-contained study from the frozen, CPU-audited Qwen evidence."""
from pathlib import Path
import json,html
from build_laminar_pages import P,shell


def build():
    root=P/'artifacts'; rows=json.loads((root/'qwen-audit.json').read_text())['runs']; selected=[r for r in rows if r['protocol']=='qwen-centered']; raw=[r for r in rows if r['protocol']=='qwen-policy']; mp=lambda rs:sum(r['informative_groups'] for r in rs)
    table='<div class="table-scroll"><table class="paper-table"><thead><tr><th>Seed</th><th>Lag</th><th>Test / 64</th><th>Length shift / 64</th><th>Test NLL</th><th>Peak clipped fraction</th></tr></thead><tbody>' + ''.join(f'<tr><td>{r["seed"]}</td><td>{r["lag"]}</td><td>{r["final"]["test"]["correct"]}</td><td>{r["final"]["ood"]["correct"]}</td><td>{r["final"]["test"]["nll"]:.3f}</td><td>{r["max_clip_fraction"]:.1%}</td></tr>' for r in selected) + '</tbody></table></div>'
    def section(title,body):return f'<section class="project-section"><h2>{title}</h2>{body}</section>'
    text=section('Qwen LoRA · Why did reward stop teaching?',f'<p class="abstract">在本地对公开 4B 量化语言模型做真实 LoRA 反向传播。算术任务限制模型只选 A/B；每道题采样 8 次。第一批 576 组只有 {mp(raw)} 组的奖励有区分度。即使参数指纹变了，六次运行仍全选 A：固定留出和长度迁移均是 32/64。把参数变化当学习成功，会漏掉这个故障。</p><p>后续只用 96 条训练输入的冻结模型 logit 差中位数做中心化，不用评估标签。用相同任务和种子重新训练后，有区分度的组增至 {mp(selected)}/576，但准确率并未稳定改善。本实验是在发现失败后设计的消融，不是预注册实验。</p>')
    text+=section('Same seeds, two policy ages','<p>三种子各比较 lag 0 和 lag 2。配对固定初始化、训练顺序和随机数，动作仍随策略变化。每次 12 个批次、每批两次 Adam 更新；只训练末两层注意力 q/v 的 81,920 个 LoRA 参数。用旧策略概率做裁剪目标，并加入冻结参考策略 KL。lag 2 是单机顺序切换历史快照，不是异步 GPU 跑分。</p><p>校准但不训练的基准：留出 40/64，长度迁移 35/64，留出 NLL 0.686。确定性求和规则 128/128。</p>'+table+'<p>最高留出正确数来自 seed 7 / lag 0，但三组配对方向不一致。校准后的 lag 2 三次运行峰值裁剪比例更高；不等同于平均裁剪率，也不是因果上的质量排名。特别是 lag 0 的 seed 19：留出 64 题全选 B，NLL 同时恶化。线上准入若只看训练奖励或准确率，会误读这个批次。</p>')
    text+=section('What does a score tie mean?', '<p>重载六个校准后的适配器，768次预测的二动作概率与记录完全相同；其中21次预测概率恰好相等，评估规则固定按 argmax 首项选 A。相同准确率可能来自大量接近五五开的概率，不代表模型确信答案。下一步是完整回答序列和多轮环境，而不是把二选一分数包装成通用推理。</p>')
    text+=section('Inspect a real update','<p>选择运行和批次，可查看行为策略版本、概率、动作、奖励和两次优化的裁剪诊断。</p><div class="explorer-controls"><label>Run<select id="q-run"></select></label><label>Update<select id="q-update"></select></label></div><p id="q-meta" aria-live="polite"></p><pre id="q-detail"></pre><p class="caption">页面回放冻结记录，不执行模型。CPU 审计复算抽样、奖励和评分，不是独立复算 GPU 梯度。训练/留出没有完全相同或 A/B 互换的数列，仍共享任务语法，不能外推自然语言推理。</p>')
    d=[]
    for folder in ['qwen-policy','qwen-centered']:
        for p in sorted((root/folder).glob('*-lag*.json')):
            r=json.loads(p.read_text());d.append(dict(protocol=folder,seed=r['seed'],lag=r['lag'],updates=r['updates']))
    payload=json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    text+='<script>const DATA='+payload+''';const r=document.querySelector('#q-run'),u=document.querySelector('#q-update');function option(el,value,text){const o=document.createElement('option');o.value=value;o.textContent=text;el.append(o)}DATA.forEach((d,i)=>option(r,i,`${d.protocol} · ${d.seed} · lag ${d.lag}`));function show(){const d=DATA[+r.value],x=d.updates[+u.value];document.querySelector('#q-meta').textContent=`Behavior v${x.behavior_version} → learner v${x.learner_version} · batch ${x.step}`;document.querySelector('#q-detail').textContent=JSON.stringify(x,null,2)}function reset(){u.replaceChildren();DATA[+r.value].updates.forEach((x,i)=>option(u,i,String(x.step)));show()}r.onchange=reset;u.onchange=show;reset();</script>'''
    (P/'qwen-study.html').write_text(shell('Laminar-Lab | Qwen LoRA and policy staleness',text),encoding='utf-8')
    project=P/'project.html';page=project.read_text();marker='<section class="project-section narrow" id="qwen-study"><h2>Qwen LoRA · Reward and Policy Age</h2><p>本地实测量化语言模型：单 token A/B 强化学习、训练集校准、两档策略滞后对照。恢复奖励差异后仍有退化；完整记录包含无效批次和逐组采样。</p><p><a class="resource" href="qwen-study.html">Qwen Study / 训练证据</a></p></section>'
    if 'id="qwen-study"' not in page:project.write_text(page.replace('<main>','<main>'+marker,1),encoding='utf-8')

if __name__=='__main__':build()
