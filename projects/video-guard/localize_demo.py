"""Append causal localization view to existing demo, keeping prior pages intact."""
import json
from videoguard.experiment import ROOT
from enhance_demo import build as build_previous

DETECT_JS=r'''
function detectDrift(rows,method,cfg){let state=null,candidate=null,count=0,first=null,alarms=[],recent=[];
for(let r of rows){let valid=r.energy>.008&&r[method+'_confidence']>=cfg.confidence;if(!valid){candidate=null;count=0;first=null;continue}let lag=r[method+'_lag'];
if(state===null){recent.push(lag);if(recent.length>=cfg.patience){let a=recent.slice(-cfg.patience).sort((a,b)=>a-b),n=a.length;state=Math.trunc(n%2?a[Math.floor(n/2)]:(a[n/2-1]+a[n/2])/2);recent=[]}continue}
if(Math.abs(lag-state)<cfg.min_jump){candidate=null;count=0;first=null;continue}
if(candidate===null||Math.abs(lag-candidate)>=cfg.min_jump){candidate=lag;count=1;first=r}else count++;
if(count>=cfg.patience){alarms.push({estimated_frame:first.center,alarm_frame:r.end,from_lag:state,to_lag:candidate,confidence:r[method+'_confidence']});state=candidate;candidate=null;count=0;first=null}}
return alarms}
'''

PANEL=r'''<section id="localization" hidden><div class="panel"><div class="eyebrow">CAUSAL CHANGE LOCALIZATION / VERSION 0.3</div><h2>变化在何时发生？多久后才发出警报？</h2><p>结构性延时边界有独立真值；模型只读取已到达的尾随窗口。预测边界与发出警报时间分别报告，不用窗口中心冒充实时发现时刻。</p><div class="two"><div><label for="driftGroup">新留出场景</label><select id="driftGroup"></select></div><div><label for="driftMethod">定位方法</label><select id="driftMethod"><option value="mlp">冻结MLP</option><option value="onset">onset相关性基线</option><option value="raw">原始相关性基线</option></select></div></div><div class="metrics"><div class="metric"><b id="driftF1">—</b><span>一对一事件匹配F1 / ±800ms</span></div><div class="metric"><b id="driftMiss">—</b><span>漏检事件数 / 全组</span></div><div class="metric"><b id="driftDelay">—</b><span>匹配事件的警报延迟中位数 / ms</span></div></div><div id="driftWarning" class="status" aria-live="polite"></div><canvas id="driftCanvas" width="820" height="260" aria-label="延时真值、尾随窗口估计、边界和警报时刻"></canvas><p class="tiny">绿色：输出时间定义的延时真值；金色：模型/基线尾随窗延时（横坐标窗结束）；虚线红：真实变化点；蓝：实际发警报时间。低证据窗口会保留错误候选，只在检测器中筛选。</p><h3>逐事件解释</h3><pre id="driftEvidence"></pre><h3>同场比较，误报与漏报不能省略</h3><div class="scroll" id="driftTable"></div><h3>匹配容差敏感性</h3><div class="scroll" id="driftTolerance"></div><p class="tiny">参数仅从160个验证媒体选择；十组各120测试＋三次独立重复。时间误差只统计匹配事件，不能掩盖漏检。多次变更、缓慢漂移和静默区有不同可识别性。</p><p><a href="DRIFT.md">定位方法与因果协议</a> · <a href="artifacts/drift-localization/REPORT.md">定位实测与失败</a></p></div></section>'''

SCRIPT=r'''
const DRIFT=__DRIFT__;
const driftNames={stable:'恒定延时 / 无变化',step:'正向突变',negative:'负向突变',small_step:'50ms小变化',ramp:'渐变阶梯',multiple:'两次变化',quiet_gap:'变化点附近静默',noise:'高噪声',exposure:'曝光干扰',silent:'静音 / 无可估证据'};
Object.entries(driftNames).forEach(([k,v])=>{let op=document.createElement('option');op.value=k;op.textContent=v;$('driftGroup').append(op)});
function renderDrift(){let group=$('driftGroup').value||'stable',method=$('driftMethod').value,e=DRIFT.examples.find(x=>x.condition===group),cfg=DRIFT.results.configs[method],a=detectDrift(e.trajectory,method,cfg),r=DRIFT.results.groups[group][method];
$('driftF1').textContent=r.f1.toFixed(3);$('driftMiss').textContent=r.fn;$('driftDelay').textContent=r.matched_alarm_delay_median_ms===null?'—':r.matched_alarm_delay_median_ms.toFixed(0);
$('driftWarning').textContent=group==='quiet_gap'?'静默区没有足够观察事件：结构性真值不等于可从媒体精确识别的时刻。':group==='ramp'?'逐整数延时变化点标注：渐变可能被检测器合并，不能当单次突变同样解释。':group==='silent'?'无对应音画事件，真值仅“没有变化”，不具备延时估计证据。':'合成RGB/PCM新留出；仅观察到尾随窗口结束，未来帧不参与当前预测。';
$('driftEvidence').textContent=JSON.stringify({fixture_seed:e.seed,structural_truth_frames:e.changes,config_from_validation:cfg,alarms:a,estimated_boundary_is_not_alarm_time:true,real_media_human_review_required:true},null,2);
let ctx=$('driftCanvas').getContext('2d');ctx.clearRect(0,0,820,260);ctx.fillStyle='#f5f7f2';ctx.fillRect(0,0,820,260);let N=e.delay_track.length,X=x=>40+x/N*750,Y=y=>120-y*15;ctx.strokeStyle='#d8e0d9';for(let lag=-6;lag<=6;lag+=2){ctx.beginPath();ctx.moveTo(40,Y(lag));ctx.lineTo(790,Y(lag));ctx.stroke();ctx.fillStyle='#66756f';ctx.font='11px system-ui';ctx.fillText(lag*50+'ms',1,Y(lag)+4)}
ctx.strokeStyle='#225d48';ctx.lineWidth=2;ctx.beginPath();e.delay_track.forEach((v,i)=>{i?ctx.lineTo(X(i),Y(v)):ctx.moveTo(X(i),Y(v))});ctx.stroke();ctx.strokeStyle='#a6772c';ctx.beginPath();e.trajectory.forEach((r,i)=>{let x=X(r.end),y=Y(r[method+'_lag']);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();
e.changes.forEach(c=>{ctx.strokeStyle='#b65345';ctx.setLineDash([4,4]);ctx.beginPath();ctx.moveTo(X(c),20);ctx.lineTo(X(c),225);ctx.stroke();ctx.setLineDash([])});
a.forEach(r=>{ctx.strokeStyle='#647dba';ctx.beginPath();ctx.moveTo(X(r.alarm_frame),20);ctx.lineTo(X(r.alarm_frame),225);ctx.stroke();ctx.fillStyle='#647dba';ctx.fillText('警报 '+(r.alarm_frame/20).toFixed(1)+'s',X(r.alarm_frame)-20,245)});
$('driftTable').innerHTML='<table><tr><th>方法</th><th>Precision</th><th>Recall</th><th>F1</th><th>TP / FP / FN</th><th>定位MAE（匹配）</th><th>警报P90延迟</th></tr>'+Object.entries(DRIFT.results.groups[group]).map(([k,v])=>`<tr><td>${k}</td><td>${v.precision.toFixed(3)}</td><td>${v.recall.toFixed(3)}</td><td>${v.f1.toFixed(3)}</td><td>${v.tp} / ${v.fp} / ${v.fn}</td><td>${v.matched_localization_mae_ms===null?'—':v.matched_localization_mae_ms.toFixed(0)+'ms'}</td><td>${v.matched_alarm_delay_p90_ms===null?'—':v.matched_alarm_delay_p90_ms.toFixed(0)+'ms'}</td></tr>`).join('')+'</table>';
$('driftTolerance').innerHTML='<table><tr><th>匹配容差</th><th>raw F1</th><th>onset F1</th><th>MLP F1</th></tr>'+Object.entries(DRIFT.results.tolerance_sweep).map(([k,v])=>`<tr><td>±${k}ms</td><td>${v.raw.f1.toFixed(3)}</td><td>${v.onset.f1.toFixed(3)}</td><td>${v.mlp.f1.toFixed(3)}</td></tr>`).join('')+'</table>';
}
['driftGroup','driftMethod'].forEach(id=>$(id).addEventListener('input',renderDrift));renderDrift();
'''


def build():
    build_previous();html=(ROOT/'demo.html').read_text();d=ROOT/'artifacts/drift-localization'
    data={'results':json.loads((d/'results.json').read_text()),'examples':json.loads((d/'examples.json').read_text())}
    html=html.replace('<button data-tab="research"','<button data-tab="localization" aria-pressed="false">漂移定位</button><button data-tab="research"',1)
    html=html.replace('<section id="research"',PANEL+'<section id="research"',1)
    html=html.replace("['lab','evidence','depth','research'].forEach","['lab','evidence','depth','localization','research'].forEach")
    script=DETECT_JS+SCRIPT.replace('__DRIFT__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    html=html.replace('</script>',script+'</script>',1);(ROOT/'demo.html').write_text(html)
    print('Causal localization demo built',len(html.encode()),'bytes')
if __name__=='__main__':build()
