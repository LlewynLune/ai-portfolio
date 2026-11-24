"""Check complete JS feature extraction + frozen parameter inference against Python."""
import json,subprocess
import numpy as np
from build_demo import ENGINE
from videoguard.experiment import ROOT,write_json
from videoguard.features import lag_features
from videoguard.model import predict
from videoguard.diagnostics import decision


def run():
    examples=json.loads((ROOT/'artifacts/examples.json').read_text())
    m=json.loads((ROOT/'artifacts/model.json').read_text())
    payload={'model':m,'examples':examples}
    code=ENGINE+'\nconst D='+json.dumps(payload)+';console.log(JSON.stringify(D.examples.map(e=>({features:features(e.signals),result:assessSignals(e.signals,D.model)}))));'
    out=subprocess.run(['node','--input-type=commonjs'],input=code,text=True,capture_output=True,check=True)
    js=json.loads(out.stdout);errors=[]
    for e,j in zip(examples,js):
        f=lag_features(e['signals']);p=predict(f[None],m['parameters'],m['temperature'])[0]
        ferr=float(np.max(np.abs(f-np.asarray(j['features']))));perr=float(np.max(np.abs(p-np.asarray(j['result']['probabilities']))))
        assert ferr<1e-9 and perr<1e-9,(e['condition'],ferr,perr)
        py=decision(e['signals'],m)
        assert py['lag']==j['result']['lag'] and py['accept']==j['result']['accept']
        errors.append({'condition':e['condition'],'feature_max_abs_error':ferr,'probability_max_abs_error':perr,'decision_equal':True})
    result={'cases':len(errors),'tolerance':1e-9,'results':errors}
    write_json(ROOT/'artifacts/js-parity.json',result)
    print('Full JS/Python feature + model + decision parity passed:',len(errors),'cases')

if __name__=='__main__':run()
