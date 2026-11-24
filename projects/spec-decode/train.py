"""Greedy speculative block verification: exact target argmax path, not sampling algorithm."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from frontier_support import *
ROOT=Path(__file__).resolve().parent

def corpus():
 seq=[]
 for a in range(8):
  for b in range(8):
   row=[a,b]
   for _ in range(11):row.append((row[-1]+row[-2])%8)
   seq.append(row)
 return torch.tensor(seq)
def fit_lm(m,rows,steps,seed):
 torch.manual_seed(seed);opt=torch.optim.Adam(m.parameters(),lr=.004);losses=[]
 for step in range(steps):
  ids=torch.randint(len(rows),(32,));xx=rows[ids,:-1];yy=rows[ids,1:];logits=m(xx);loss=F.cross_entropy(logits.reshape(-1,V),yy.reshape(-1));opt.zero_grad();loss.backward();opt.step()
  if step%50==0:losses.append({'step':step,'loss':float(loss.detach())})
 return losses

@torch.inference_mode()
def greedy(m,prefix,count=8):
 seq=list(prefix);calls=0
 for _ in range(count):
  seq.append(int(m(torch.tensor([seq]))[0,-1].argmax()));calls+=1
 return seq[len(prefix):],calls
@torch.inference_mode()
def speculative(target,draft,prefix,count=8,k=4):
 seq=list(prefix);initial=len(seq);tc=0;dc=0;accepted=0;proposed=0;trace=[]
 while len(seq)-initial<count:
  length=min(k,count-(len(seq)-initial));temp=list(seq);proposal=[]
  for _ in range(length):
   token=int(draft(torch.tensor([temp]))[0,-1].argmax());proposal.append(token);temp.append(token);dc+=1
  # One causal forward yields probabilities for each drafted-prefix position.
  logits=target(torch.tensor([seq+proposal]))[0];tc+=1;offset=len(seq)-1;checks=[];matched=0
  for i,token in enumerate(proposal):
   actual=int(logits[offset+i].argmax());ok=token==actual;checks.append({'draft':token,'target':actual,'accepted':ok});proposed+=1
   seq.append(token if ok else actual)
   if not ok:break
   matched+=1;accepted+=1
  if matched==len(proposal) and len(seq)-initial<count:seq.append(int(logits[-1].argmax()))
  trace.append({'proposal':proposal,'checks':checks,'accepted_count':matched,'output_so_far':seq[initial:]})
 return seq[initial:],{'target_calls':tc,'draft_calls':dc,'accepted':accepted,'proposed_checked':proposed,'trace':trace}

def main():
 seq=corpus();order=torch.randperm(len(seq),generator=torch.Generator().manual_seed(10));tr=order[:48];va=order[48:56];te=order[56:]
 torch.manual_seed(42);target=TinyAttention(d=32);loss=fit_lm(target,seq[tr],700,42);target.eval()
 torch.manual_seed(43);draft=TinyAttention(d=16);dloss=fit_lm(draft,seq[tr],250,43);draft.eval();rows=[];raw=[];examples=[]
 # Same prompts paired for baseline and k2/k4; 3 repeats. Warm up before timing.
 prompts=[seq[i,:4].tolist() for i in te];greedy(target,prompts[0]);speculative(target,draft,prompts[0],k=4)
 for k in [2,4]:
  for repeat in range(3):
   bt=0;st=0;tc=0;dc=0;accept=0;proposed=0;equal=0
   for i,prefix in enumerate(prompts):
    start=time.perf_counter();g,calls=greedy(target,prefix);bm=(time.perf_counter()-start)*1000;bt+=bm
    start=time.perf_counter();s,stats=speculative(target,draft,prefix,k=k);sm=(time.perf_counter()-start)*1000;st+=sm
    assert g==s
    tc+=stats['target_calls'];dc+=stats['draft_calls'];accept+=stats['accepted'];proposed+=stats['proposed_checked'];equal+=int(g==s)
    raw.append({'k':k,'repeat':repeat,'prompt':i,'baseline_ms':bm,'speculative_ms':sm,'baseline_calls':calls,'target_calls':stats['target_calls'],'draft_calls':stats['draft_calls'],'exact':g==s})
    if repeat==0 and i<2:examples.append({'group':'greedy_k'+str(k),'tokens':prefix,'baseline_output':g,'speculative_output':s,**stats})
   rows.append({'k':k,'repeat':repeat,'prompts':len(prompts),'exact_prompts':equal,'baseline_ms':bt,'speculative_ms':st,'speed_ratio_baseline_over_spec':bt/st,'target_calls':tc,'draft_calls':dc,'acceptance_checked':accept/max(1,proposed)})
 save(ROOT,{'title':'SpecDecode-Lab','protocol':'Independent tiny causal next-token models trained on48 synthetic modular-recurrence initial states;8validation/8test states. Target700steps d32, draft250steps d16. Evaluation measures greedy equivalence and actual CPU timing,8outputs after4token prompt,k2/k4,3 paired repeats,warmup; noKV cache.',
 'metrics':rows,'timings':raw,'examples':examples,'loss_curve':loss,'draft_loss':dloss,'split':{'train':tr.tolist(),'validation':va.tolist(),'test':te.tolist()},
 'limits':['Implements deterministic greedy block verification only, not rejection-sampling distribution preservation.','Synthetic recurrence state paths overlap later; test is inference-correctness probe, not generalization score.','NoKV cache/GPU/parallel kernels; Python tiny CPU models can be slower despite fewer target calls.','Includes draft time and verification time; speed ratio is actual this environment only, not service throughput.','Target path is reference, not correctness against arithmetic labels.','No inference service, foundation-model accelerator or original algorithm claims.']},{'target':export(target),'draft':export(draft),'kind':'greedy_speculation'})
if __name__=='__main__':main()
