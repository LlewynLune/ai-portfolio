import json,subprocess
from localize_demo import DETECT_JS
from videoguard.drift import detect
from videoguard.experiment import ROOT,write_json


def run():
    d=ROOT/'artifacts/drift-localization';r=json.loads((d/'results.json').read_text());cases=[]
    for g in r['groups']:
        rows=json.loads((d/f'{g}-records.json').read_text())
        for row in rows[:8]:
            for method,cfg in r['configs'].items():cases.append({'trajectory':row['trajectory'],'method':method,'config':cfg})
    code=DETECT_JS+'const cases='+json.dumps(cases)+';console.log(JSON.stringify(cases.map(c=>detectDrift(c.trajectory,c.method,c.config))));'
    js=json.loads(subprocess.run(['node','--input-type=commonjs'],input=code,text=True,capture_output=True,check=True).stdout)
    for c,j in zip(cases,js):assert j==detect(c['trajectory'],c['method'],**c['config']),c['method']
    write_json(d/'js-parity.json',{'trajectory_cases':len(cases),'exact_alarm_time_boundary_state_parity':True})
    print('Causal detector JS/Python parity',len(cases),'cases')
if __name__=='__main__':run()
