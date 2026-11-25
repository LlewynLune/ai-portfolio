"""Extra scheduler sensitivity: disable per-token delays; same known toy task.
Exploratory follow-up, not fresh holdout or dataset, not hardware speedup.
"""
import asyncio,json
from pathlib import Path
from .experiment import run

def main():
 out=Path('artifacts/no-token-delay');out.mkdir(parents=True,exist_ok=True);rows=[]
 for seed in [7,19,41]:
  for mode in ['synchronous','async_ratio']:
   path=out/f'{seed}-{mode}.json'
   if path.exists():raise FileExistsError(path)
   r=asyncio.run(run(seed,mode,40,delay_scale=0));path.write_text(json.dumps(r,allow_nan=False));rows.append(r['summary'])
 (out/'summary.json').write_text(json.dumps({'runs':rows,'note':'Per-token artificial delay disabled; 2ms per-update control overhead remains. Exploratory follow-up on same grammar.'},indent=2))
if __name__=='__main__':main()
