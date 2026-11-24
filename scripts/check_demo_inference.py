"""Check native JavaScript inference against recorded Python examples; no browser API."""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STUB="""
class El{constructor(){this.value='';this.textContent='';this.children=[];}append(x){this.children.push(x);}replaceChildren(){this.children=[];}addEventListener(){} }
const els={};const document={getElementById(id){return els[id]||(els[id]=new El());},createElement(){return new El();}};
"""
for project in ('textguard','novelty-lab','cite-rag'):
 html=(ROOT/'projects'/project/'demo.html').read_text();data=re.search(r'<script id="data" type="application/json">(.*?)</script>',html,re.S)[1];js=re.search(r'</script><script>(.*?)</script>',html,re.S)[1]
 setup=f"document.getElementById('data').textContent={json.dumps(data)};document.getElementById('examples').value='0';document.getElementById('method').value='hybrid';document.getElementById('input').value='retry';"
 if project=='textguard':assertion="data.results.examples.forEach(e=>{if(Math.abs(infer(e.text).p-e.probability)>1e-10)throw Error('text parity failure');});"
 elif project=='novelty-lab':assertion="data.results.examples.forEach(e=>{document.getElementById('input').value=JSON.stringify(e.values);predict();if(Math.abs(Number(document.getElementById('score').textContent)-e.score)>.001)throw Error('distance parity failure');});"
 else:assertion="data.metrics.forEach(m=>m.cases.forEach(e=>{const a=rank(e.q,m.method).slice(0,3);a.forEach((h,i)=>{if(h.id!==e.hits[i].id||Math.abs(h.score-e.hits[i].score)>1e-10)throw Error('ranking parity failure');});}));"
 subprocess.run(['node','--input-type=commonjs'],input=STUB+setup+js+assertion,check=True,capture_output=True,text=True)
 print(project+': JS/Python example and score parity passed')
