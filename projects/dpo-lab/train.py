"""Actual DPO objective on one-token synthetic preferences with frozen reference."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from frontier_support import *
ROOT=Path(__file__).resolve().parent

def dpo_loss(policy_logp,reference_logp,chosen,rejected,beta):
 i=torch.arange(len(chosen));margin=(policy_logp[i,chosen]-policy_logp[i,rejected])-(reference_logp[i,chosen]-reference_logp[i,rejected]);return -F.logsigmoid(beta*margin).mean()
def fit(model,ref,x,chosen,rejected,beta,steps=400):
 for name,p in model.named_parameters():p.requires_grad=name.startswith('head.')
 opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=.003);torch.manual_seed(42);history=[]
 with torch.no_grad():rp=ref(x)[:,-1].log_softmax(-1)
 for step in range(steps):
  ids=torch.randint(len(x),(64,));lp=model(x[ids])[:,-1].log_softmax(-1);loss=dpo_loss(lp,rp[ids],chosen[ids],rejected[ids],beta);opt.zero_grad();loss.backward();opt.step()
  if step%50==0:history.append({'step':step,'loss':float(loss.detach())})
 return history

def main():
 path=ROOT.parent/'tiny-attention/artifacts/model.json';ref=restore(json.loads(path.read_text()));x,rejected,ids=generate(1000,60);chosen=(rejected-8+2)%8+8
 va,vrej,vid=generate(300,61,exclude=ids);vc=(vrej-8+2)%8+8;te,rej,tid=generate(500,62,exclude=ids+vid);ch=(rej-8+2)%8+8
 variants={'reference':ref};losses={}
 for beta in [.1,.5]:
  m=copy.deepcopy(ref);n='dpo_beta'+str(beta);losses[n]=fit(m,ref,x,chosen,rejected,beta);variants[n]=m
 sft=copy.deepcopy(ref)
 for name,p in sft.named_parameters():p.requires_grad=name.startswith('head.')
 losses['sft_chosen']=train_model(sft,x,chosen,400,.003);variants['sft_chosen']=sft
 with torch.no_grad():vref=ref(va)[:,-1].softmax(-1)
 def selection(n):
  with torch.no_grad():p=variants[n](va)[:,-1].softmax(-1);win=(p[torch.arange(len(vc)),vc]>p[torch.arange(len(vc)),vrej]).float().mean();kl=(p*(p.clamp_min(1e-10).log()-vref.clamp_min(1e-10).log())).sum(-1).mean();return float(win-.05*kl)
 selected=max(['dpo_beta0.1','dpo_beta0.5'],key=selection);rows=[];predictions=[];examples=[]
 for group,xx,cc,rr in [('validation',va,vc,vrej),('heldout_pairs',te,ch,rej)]:
  with torch.no_grad():rp=ref(xx)[:,-1].softmax(-1)
  for name,m in variants.items():
   with torch.no_grad():p=m(xx)[:,-1].softmax(-1);i=torch.arange(len(cc));win=p[i,cc]>p[i,rr];kl=(p*(p.clamp_min(1e-10).log()-rp.clamp_min(1e-10).log())).sum(-1)
   rows.append({'group':group,'model':name,'pair_win_rate':float(win.float().mean()),'chosen_top1_accuracy':float((p.argmax(-1)==cc).float().mean()),'original_top1_retention':float((p.argmax(-1)==rr).float().mean()),'kl_to_reference':float(kl.mean())})
   predictions.extend({'group':group,'model':name,'index':j,'chosen':int(c),'rejected':int(r),'probabilities':v} for j,(c,r,v) in enumerate(zip(cc,rr,p.tolist())))
  p=variants[selected](xx)[:,-1].softmax(-1).detach().tolist()
  for j in [0,1,2]:examples.append({'group':group,'tokens':xx[j].tolist(),'truth':int(cc[j]),'rejected':int(rr[j]),'probabilities':p[j]})
 save(ROOT,{'title':'DPO-Lab','protocol':'Shared pretrained TinyAttention; synthetic1-token preference prefers(value+2)%8 and rejects original value.1000train/300validation/500test disjoint prefixes; head-only400steps. DPO beta0.1/0.5 selected by validation win-.05KL, chosen-onlySFT baseline same head.',
 'base_model_sha256':digest(path),'selected':selected,'metrics':rows,'predictions':predictions,'examples':examples,'loss_curves':losses,'split_ids':{'train':ids,'validation':vid,'test':tid},
 'limits':['One-token closed-form preferences, not human feedback or natural-language alignment.','DPO preference ordering can improve while chosen top1 remains bad; both reported.','Original answer retention intentionally conflicts with preference; drift is not proof of safer behavior.','No PPO/RLHF online rollout/reward model; PyTorch objective independently implemented.','Frozen reference must remain unchanged; beta comparisons not matchedKL training budget.','Shared tiny base disclosed; no foundation-model finetuning or paper-scale claims.']},export(variants[selected]))
if __name__=='__main__':main()
