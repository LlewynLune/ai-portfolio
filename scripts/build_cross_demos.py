"""Self-contained native model demos for four cross-disciplinary projects."""
import json,sys
from pathlib import Path
from build_ai_demos import build
ROOT=Path(__file__).resolve().parents[1]
ENGINE='''function modelForward(x,m){let a=x.map((v,i)=>(v-m.mean[i])/m.scale[i]);if(m.kind==='mlp'){m.weights.forEach((w,k)=>{const b=m.bias[k];a=b.map((v,j)=>v+a.reduce((s,t,i)=>s+t*w[i][j],0));if(k<m.weights.length-1)a=a.map(v=>m.activation==='relu'?Math.max(0,v):Math.tanh(v));});return a;}return m.weights.map((w,j)=>m.bias[j]+w.reduce((s,v,i)=>s+v*a[i],0));}function modelPredict(x,m){if(x.length!==m.mean.length||!x.every(Number.isFinite))throw Error('无效输入');const v=modelForward(x,m);if(!v.every(Number.isFinite))throw Error('输入超出数值范围');if(m.temperature){const z=v.map(t=>t/m.temperature),hi=Math.max(...z),e=z.map(t=>Math.exp(t-hi)),s=e.reduce((a,b)=>a+b,0);return e.map(t=>t/s);}if(m.target_transform==='exp(log_tau_ms)'){const out=v.map(Math.exp);if(!out.every(Number.isFinite))throw Error('指数输出超出数值范围');return out;}return v;}
// END MODEL ENGINE
'''
CHART='''function chart(id,series){const el=$(id);el.replaceChildren();const W=520,H=210,pad=25,all=series.flatMap(s=>s.values),lo=Math.min(...all),hi=Math.max(...all),range=hi-lo||1;const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.setAttribute('width','100%');svg.setAttribute('role','img');svg.setAttribute('aria-label','样本曲线对照');series.forEach(s=>{const path=document.createElementNS('http://www.w3.org/2000/svg','polyline');path.setAttribute('points',s.values.map((v,i)=>(pad+i*(W-2*pad)/(s.values.length-1||1))+','+(H-pad-(v-lo)*(H-2*pad)/range)).join(' '));path.setAttribute('fill','none');path.setAttribute('stroke',s.color);path.setAttribute('stroke-width','2');svg.append(path);});el.append(svg);series.forEach(s=>el.append(text('span',s.name+'　')));el.append(text('div','纵轴范围 '+lo.toFixed(2)+' – '+hi.toFixed(2)+'；横轴为样本点/子载波。'));}
'''
HEADS={
 'vision-cal':('VisionCal｜神经网络校准与鲁棒性','AI 算法：实际训练 64→48→10 小型网络，比较线性基线、温度缩放、噪声和平移。', '64个0–1像素；下方可编辑8×8像素，不是MNIST/CNN。', ['group','model','accuracy','nll','ece10','coverage90']),
 'circuit-id':('CircuitID｜电子电路参数识别','电子科学与技术：从噪声RC阶跃波形估计时间常数，比较规则、物理拟合和学习模型。', '32个归一化波形点，0–10ms；仅仿真，不能由此分辨R与C。',['group','seed','model','mae','rmse','coverage90']),
 'channel-est':('ChannelEst｜学习型通信信道估计','信息与通信工程：32子载波的理想频域链路，导频估计、均衡与误码率对照。', '8个导频实部+8个虚部；理想仿真，无无线设备。',['group','seed','model','nmse','ber']),
 'power-scope':('PowerScope｜AI数据中心负荷预测','电气工程交叉：时序留出、计划输入消融和冷却漂移；只做离线预测，不控制设备。', '9维观测/计划；下一5分钟kW预测。容量阈值仅假设，非设备额定。',['group','model','mae','rmse','interval90_coverage','flag_fn'])}

def main():
 for p,(title,subtitle,hint,keys) in HEADS.items():
  folder=ROOT/'projects'/p/'artifacts';r=json.loads((folder/'results.json').read_text());m=json.loads((folder/'model.json').read_text());d={'model':m,'metrics':r['metrics'],'examples':r['examples'],'limits':r['limits'],'protocol':r['protocol']}
  rows=''.join('<th>'+k+'</th>' for k in keys)
  body=f'''<section class="card"><h2>实际参数推断</h2><select id="examples" aria-label="分组样本"></select><p>{hint}</p><div id="pixels" style="display:grid;grid-template-columns:repeat(8,1fr);max-width:300px"></div><textarea id="input" aria-label="模型输入JSON数组"></textarea><button id="predict">运行已训练模型</button><div id="summary" role="status"></div><div id="curve"></div><div id="extra"></div><p class="warning">示例包含普通和失败样本；输出由参数实时计算，不读取预设答案。自定义输入不自动拥有真实标签。</p></section><section class="card"><h2>冻结评测与方法边界</h2><p id="protocol"></p><div class="scroll"><table><thead><tr>{rows}</tr></thead><tbody id="scores"></tbody></table></div><p><a href="artifacts/REPORT.md">完整评测</a> · <a href="artifacts/results.json">逐条证据</a> · <a href="METHOD.md">原理与协议</a> · <a href="MODEL_CARD.md">模型卡</a></p><div id="limits"></div></section>'''
  js=ENGINE+CHART+'''const m=data.model;let current=null,edited=false;const fmt=v=>v===null?'—':typeof v==='number'?v.toFixed(4):v;
 function input(){const x=JSON.parse($('input').value);if(!Array.isArray(x)||x.length!==m.mean.length||!x.every(v=>typeof v==='number'&&Number.isFinite(v)))throw Error('需要'+m.mean.length+'个有限数字');return x;}
 function example(){current=data.examples[Number($('examples').value)];edited=false;$('input').value=JSON.stringify(current.input);predict();}
 '''
  if p=='vision-cal':
   js+='''function pixels(x){const el=$('pixels');el.replaceChildren();x.forEach((v,i)=>{const b=text('button','');b.style.cssText='margin:0;padding:0;border:1px solid #d8e0d9;height:28px;border-radius:0;background:rgb('+[1,1,1].map(()=>Math.round((1-v)*255)).join(',')+')';b.setAttribute('aria-label','像素'+i);b.addEventListener('click',()=>{const a=input();a[i]=a[i]>.5?0:1;$('input').value=JSON.stringify(a);edited=true;predict();});el.append(b);});}
 function predict(){try{const x=input();if(!x.every(v=>v>=0&&v<=1))throw Error('像素须在0–1');const out=modelPredict(x,m),max=Math.max(...out),cls=out.indexOf(max);$('summary').textContent='预测数字 '+cls+' / 最大倾向 '+(max*100).toFixed(1)+'% / '+(max>=.9?'固定阈值接收':'建议人工复核')+(current&&!edited?' / 来源标签 '+current.label:' / 自定义输入无标签');pixels(x);chart('curve',[{name:'各类别概率0–9',values:out,color:'#225d48'}]);$('extra').textContent='温度 '+m.temperature.toFixed(2)+'；高置信度也会出错，平移不具备不变性。';}catch(e){$('summary').textContent=e.message;$('curve').replaceChildren();$('extra').replaceChildren();}}
 '''
  elif p=='circuit-id':
   js+='''function predict(){try{const x=input(),tau=modelPredict(x,m)[0];if(!Number.isFinite(tau))throw Error('输出超出有限范围');$('summary').textContent='预测时间常数 '+tau.toFixed(3)+'ms / 验证残差带 ±'+m.interval_abs_ms.toFixed(3)+'ms'+(current&&!edited?' / 真值 '+current.truth.toFixed(3)+'ms':'');const predicted=m.time_ms.map(t=>1-Math.exp(-t/tau));chart('curve',[{name:'输入测量仿真',values:x,color:'#a7752d'},{name:'单位RC重建',values:predicted,color:'#225d48'}]);$('extra').textContent='默认 '+m.selected+'；固定输入幅值假设。OOD残差带不保证覆盖。';}catch(e){$('summary').textContent=e.message;$('curve').replaceChildren();$('extra').replaceChildren();}}
 '''
  elif p=='channel-est':
   js+='''function predict(){try{const x=input(),v=modelPredict(x,m),N=m.subcarriers;chart('curve',[{name:'估计实部',values:v.slice(0,N),color:'#225d48'},{name:'估计虚部',values:v.slice(N),color:'#a7752d'}]);$('summary').textContent='已从'+m.pilot_indices.length+'个导频预测'+N+'个复信道';if(current&&!edited){const truth=current.truth_real.concat(current.truth_imag),e=v.reduce((s,z,i)=>s+(z-truth[i])**2,0)/truth.reduce((s,z)=>s+z*z,0);$('extra').textContent='此示例NMSE '+e.toFixed(4)+' / '+current.group;}else $('extra').textContent='自定义输入没有真信道，不能计算质量或BER。';}catch(e){$('summary').textContent=e.message;$('curve').replaceChildren();$('extra').replaceChildren();}}
 '''
  else:
   js+='''function predict(){try{const x=input(),p=modelPredict(x,m)[0],q=m.interval_abs_kw;$('summary').textContent='下一5分钟 '+p.toFixed(1)+' kW / 残差带 ±'+q.toFixed(1)+' kW';$('extra').replaceChildren();x.forEach((v,i)=>$('extra').append(text('div',m.features[i]+' = '+v.toFixed(3))));$('extra').append(text('p',p+q>m.capacity_scenario_kw?'超过假设阈值，仅建议人工复核；无控制动作。':'未超过假设阈值，不是容量/安全保证。'));if(current&&!edited)$('extra').append(text('p','示例真值 '+current.truth.toFixed(1)+' kW / '+current.group));chart('curve',[{name:'当前观测 → 下一步预测',values:[x[0],p],color:'#225d48'}]);}catch(e){$('summary').textContent=e.message;$('curve').replaceChildren();$('extra').replaceChildren();}}
 '''
  js+='''data.examples.forEach((e,i)=>{const op=text('option',e.group+' / 样本'+i);op.value=i;$('examples').append(op);});$('examples').value='0';$('examples').addEventListener('change',example);$('input').addEventListener('input',()=>{edited=true;});$('predict').addEventListener('click',predict);$('protocol').textContent=data.protocol;data.limits.forEach(l=>{const e=text('p',l);e.className='warning';$('limits').append(e);});'''
  js+='table("scores",data.metrics.map(r=>'+json.dumps(keys)+'.map(k=>fmt(r[k]))));example();'
  build(p,title,subtitle,body,js,d)
  print('Built',p)
if __name__=='__main__':main()
