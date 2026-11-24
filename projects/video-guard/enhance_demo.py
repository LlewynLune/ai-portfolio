"""Add calibration-depth view without modifying legacy model or build_demo engine.
The panel uses NEW stored holdout probabilities. Labels only grade, never build sets.
"""
import json
from build_demo import TEMPLATE,ENGINE
from videoguard.experiment import ROOT

SET_ENGINE=r'''
function setFor(p,q,method,u){let set=[];
if(method==='legacy_lac'||method==='lac'||method==='lac_top1'){set=p.map((v,i)=>1-v<=q+1e-12?i:null).filter(v=>v!==null);if(method==='lac_top1'){let k=p.indexOf(Math.max(...p));if(!set.includes(k))set.push(k)}}
else if(method==='log_lac'){set=p.map((v,i)=>-Math.log(Math.max(v,Number.MIN_VALUE))<=q+1e-12?i:null).filter(v=>v!==null)}
else {let order=p.map((v,i)=>i).sort((a,b)=>p[b]-p[a]||a-b),total=0;for(let j=0;j<order.length;j++){let k=order[j],before=total;total+=p[k];if(method==='aps_randomized'){if(total-u*p[k]<=q+1e-12)set.push(k)}else if(j===0||before<q){set.push(k)}}}
return set.sort((a,b)=>a-b)}
function riskFor(pool,t){let accepted=pool.probabilities.map((p,i)=>({p,i})).filter(o=>Math.max(...o.p)>=t),err=accepted.filter(o=>o.p.indexOf(Math.max(...o.p))!==pool.labels[o.i]).length;return {n:accepted.length,coverage:accepted.length/pool.labels.length,errors:err,error_rate:accepted.length?err/accepted.length:null}}
'''

PANEL=r'''<section id="depth" hidden><div class="panel"><div class="eyebrow">CALIBRATION DEPTH / VERSION 0.2</div><h2>从“有校准”到可检查的覆盖—效率—错误</h2><p>模型和温度全部冻结，新增1000个校准样本、八组各600个新留出，24轮独立校准/测试。不是用旧测试调一个更好数字。原v0.6结果仍在“实测与失败”。</p><div class="two"><div><label for="depthGroup">新留出场景</label><select id="depthGroup"></select></div><div><label for="depthMethod">集合方法（全列，不选赢家）</label><select id="depthMethod"><option value="legacy_lac">原v0.6 LAC / 250校准</option><option value="lac">新1000校准 LAC</option><option value="log_lac">对数LAC</option><option value="aps_randomized">随机化APS / 保存独立u</option><option value="aps_crossing">APS crossing / 保守超集</option><option value="lac_top1">LAC补全top1 / 非拒估证明</option></select></div></div><div class="metrics"><div class="metric"><b id="depthCoverage">—</b><span>真值包含率（不是唯一正确率）</span></div><div class="metric"><b id="depthSize">—</b><span>平均集合大小（不是质量评分）</span></div><div class="metric"><b id="depthEmpty">—</b><span>空集比例</span></div></div><div id="depthWarning" class="status" aria-live="polite"></div><div class="scroll" id="depthTable"></div><h3>直接复核一个新留出样本</h3><label for="depthSample">样本索引 <b id="sampleValue">0</b>（真值仅评价，不用于构造集合）</label><input id="depthSample" type="range" min="0" max="599" value="0"><pre id="setEvidence"></pre><h3>保留估计比例—误差曲线</h3><p class="tiny">以下按模型最大概率门限筛选全部新留出，不含窗口/集合过滤；不是生产准入策略。零错误只说明该样本没观察到错误。</p><label for="riskThreshold">置信门限 <b id="thresholdValue">0.90</b></label><input id="riskThreshold" type="range" min="0" max="20" value="18"><canvas id="riskCanvas" width="800" height="210" aria-label="保留比例与错误率曲线"></canvas><div id="riskStats" class="status"></div><p class="tiny">上界为独立同分布二项假设的一侧95% Clopper–Pearson上界；同时门限上界对21个门限作Bonferroni调整。重复/相关采样会破坏假设，不能套用真实视频。</p><h3>24轮独立校准，不再只看一次</h3><div class="scroll" id="repeatTable"></div><p class="tiny">各轮250校准＋400测试，冻结模型；每轮新base-media seeds。某一轮低于90%不自动推翻边际保证，平均覆盖也不能证明OOD保证。</p><h3>“0错例”到底说明多少？</h3><div id="zeroError"></div><p>更大的集合可能提高包含率，却让唯一答案更少；强制补全top1可能消除空集，却保留错误唯一答案。<b>不把“集合不为空”包装成“可放心自动化”。</b></p><p><a href="CALIBRATION.md">纵深方法与协议</a> · <a href="artifacts/calibration-depth/REPORT.md">全部实测与不利结果</a></p></div></section>'''

SCRIPT=r'''
const DEPTH=__DEPTH__;
const methodNames={legacy_lac:'原v0.6 LAC',lac:'新LAC',log_lac:'对数LAC',aps_randomized:'随机化APS',aps_crossing:'APS crossing保守超集',lac_top1:'LAC补全top1'};
Object.entries(names).forEach(([k,v])=>{let op=document.createElement('option');op.value=k;op.textContent=v;$('depthGroup').append(op)});
function renderDepth(){let group=$('depthGroup').value||'id',method=$('depthMethod').value,pool=DEPTH.pools[group],metrics=DEPTH.results.conditions[group].sets[method],i=+$('depthSample').value,p=pool.probabilities[i],q=method==='legacy_lac'?DATA.model.conformal_q:DEPTH.results.fresh_thresholds[method],set=setFor(p,q,method,pool.uniforms[i]);
$('depthCoverage').textContent=pct(metrics.coverage);$('depthSize').textContent=metrics.mean_size.toFixed(2);$('depthEmpty').textContent=pct(metrics.empty_rate);
$('depthWarning').textContent=group==='drift'?'该组真值仅前半段延时，不是全片稳定对应；覆盖率不得解释为漂移检出率。':group==='silent'||group==='periodic'?'该场景存在可识别性问题：包含生成器选定标签不等于现实可归因。':'合成新留出统计；真实视频仍未知分布、强制人工复核。';
$('depthTable').innerHTML='<table><tr><th>方法</th><th>包含率</th><th>平均大小</th><th>空集</th><th>单例比例</th><th>单例错误</th></tr>'+Object.entries(DEPTH.results.conditions[group].sets).map(([k,r])=>`<tr><td>${methodNames[k]}</td><td>${pct(r.coverage)}</td><td>${r.mean_size.toFixed(2)}</td><td>${pct(r.empty_rate)}</td><td>${pct(r.singleton_rate)}</td><td>${pct(r.singleton_error)}</td></tr>`).join('')+'</table>';
$('sampleValue').textContent=i;$('setEvidence').textContent=JSON.stringify({seed:pool.records[i].seed,method,threshold:q,uniform:method==='aps_randomized'?pool.uniforms[i]:null,truth_delay_ms:(pool.labels[i]-6)*50,predicted_delay_ms:(p.indexOf(Math.max(...p))-6)*50,candidate_delay_ms:set.map(k=>(k-6)*50),truth_included:set.includes(pool.labels[i]),not_a_release_approval:true},null,2);
let step=+$('riskThreshold').value,t=step/20,r=riskFor(pool,t),stored=DEPTH.results.conditions[group].all_confidence_risk[step];$('thresholdValue').textContent=t.toFixed(2);$('riskStats').textContent=`保留 ${r.n}/600（${pct(r.coverage)}） · 观察错误 ${r.errors} · 错误率 ${pct(r.error_rate)} · 一侧95%上界 ${pct(stored.upper95)} · 21门限同时上界 ${pct(stored.simultaneous_upper95)}`;
let ctx=$('riskCanvas').getContext('2d'),rows=DEPTH.results.conditions[group].all_confidence_risk;ctx.clearRect(0,0,800,210);ctx.fillStyle='#f5f7f2';ctx.fillRect(0,0,800,210);ctx.strokeStyle='#d8e0d9';for(let j=0;j<=4;j++){let y=180-j*40;ctx.beginPath();ctx.moveTo(40,y);ctx.lineTo(770,y);ctx.stroke();ctx.fillStyle='#66756f';ctx.font='11px system-ui';ctx.fillText(j*25+'%',5,y+4)}
[['coverage','#225d48'],['error_rate','#a6772c'],['upper95','#889ab0']].forEach(([key,col])=>{ctx.beginPath();ctx.strokeStyle=col;ctx.lineWidth=2;let started=false;rows.forEach(o=>{if(o[key]===null){started=false;return}let x=40+o.threshold*730,y=180-o[key]*160;started?ctx.lineTo(x,y):ctx.moveTo(x,y);started=true});ctx.stroke()});ctx.fillStyle='#192a27';ctx.fillText('绿色 保留比例 / 金色 错误率 / 蓝灰 单门限95%上界 · 横轴置信门限',40,202);
$('repeatTable').innerHTML='<table><tr><th>方法</th><th>平均包含率</th><th>标准差</th><th>5/50/95%分位</th><th>低于90%的轮数</th><th>平均大小</th></tr>'+Object.entries(DEPTH.results.repeat_summary).map(([k,r])=>`<tr><td>${methodNames[k]}</td><td>${pct(r.mean_coverage)}</td><td>${pct(r.sd_coverage)}</td><td>${r.coverage_quantiles_05_50_95.map(pct).join(' / ')}</td><td>${r.replicates_below_90}/24</td><td>${r.mean_set_size.toFixed(2)}</td></tr>`).join('')+'</table>';
$('zeroError').innerHTML='<p>'+DEPTH.results.zero_error_illustration.map(r=>`${r.accepted}个样本0错误：上界仍为${pct(r.upper95)}`).join('<br>')+'</p>';
}
['depthGroup','depthMethod','depthSample','riskThreshold'].forEach(id=>$(id).addEventListener('input',renderDepth));renderDepth();
'''


def build():
    def read(n):return json.loads((ROOT/'artifacts'/n).read_text())
    data={'model':read('model.json'),'results':read('results.json'),'examples':read('examples.json'),'diagnostics':read('diagnostics.json'),'contrastive':read('contrastive-results.json')}
    depth={'results':read('calibration-depth/results.json'),'pools':read('calibration-depth/probability-pools.json')}
    html=TEMPLATE.replace('__ENGINE__',ENGINE+SET_ENGINE).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    html=html.replace('<button data-tab="research"','<button data-tab="depth" aria-pressed="false">校准纵深</button><button data-tab="research"',1)
    html=html.replace('<section id="research"',PANEL+'<section id="research"',1)
    html=html.replace("['lab','evidence','research'].forEach","['lab','evidence','depth','research'].forEach")
    # Keep 24 replicate summaries, not their full pools, in single-page demo.
    payload=json.dumps(depth,ensure_ascii=False).replace('</','<\\/')
    html=html.replace('</script>',SCRIPT.replace('__DEPTH__',payload)+'</script>',1)
    (ROOT/'demo.html').write_text(html)
    print('Extended single-file demo',len(html.encode()),'bytes')

if __name__=='__main__':build()
