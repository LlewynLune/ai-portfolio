"""Freeze trained TinyAttention; adapt q/v/output via genuine low-rank updates."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from frontier_support import *
ROOT=Path(__file__).resolve().parent

def main():
 basepath=ROOT.parent/'tiny-attention/artifacts/model.json';base=restore(json.loads(basepath.read_text()));x,y,ids=generate(1000,50,shift=1);va,vy,vid=generate(300,51,shift=1,exclude=ids);te,ty,tid=generate(500,52,shift=1,exclude=ids+vid);orig,oy,_=generate(500,53);ood,ody,_=generate(300,54,pairs=5,shift=1)
 variants={'frozen':base};history={};counts={'frozen':0}
 for rank in [1,4]:
  torch.manual_seed(70+rank);m=copy.deepcopy(base)
  for p in m.parameters():p.requires_grad=False
  for name in ['q','v','head']:setattr(m,name,LowRankLinear(getattr(m,name),rank))
  counts['lora_r'+str(rank)]=param_count(m);history['lora_r'+str(rank)]=train_model(m,x,y,450,.003,seed=42);variants['lora_r'+str(rank)]=m
 full=copy.deepcopy(base);counts['full_finetune']=param_count(full);history['full_finetune']=train_model(full,x,y,450,.003);variants['full_finetune']=full
 chosen=max(['lora_r1','lora_r4'],key=lambda n:evaluate(variants[n],va,vy)[0]['accuracy']);rows=[];predictions=[];examples=[]
 for group,xx,yy in [('validation_shift1',va,vy),('test_shift1',te,ty),('original_task_retention',orig,oy),('length5_shift1_ood',ood,ody)]:
  for n,m in variants.items():
   met,p=evaluate(m,xx,yy);rows.append({'group':group,'model':n,'trainable_parameters':counts[n],**met});predictions += [{'group':group,'model':n,'index':i,'truth':int(v),'probabilities':pp} for i,(v,pp) in enumerate(zip(yy,p))]
  _,p=evaluate(variants[chosen],xx,yy)
  for i in [0,1]:examples.append({'group':group,'tokens':xx[i].tolist(),'truth':int(yy[i]),'probabilities':p[i]})
 for n in ['lora_r1','lora_r4']:
  assert all(torch.equal(getattr(variants[n],layer).base.weight,getattr(base,layer).weight) for layer in ['q','v','head'])
 model=merged_export(variants[chosen]);merged=restore(model)
 with torch.no_grad():parity=float((merged(te[:16])-variants[chosen](te[:16])).abs().max())
 assert parity<1e-5
 save(ROOT,{'title':'LoRA-Lab','protocol':'Shared pretrained TinyAttention from this portfolio. New rule:answer value+1 mod8.1000train/300validation/500test disjoint within adaptation; original-task retention500; length5 OOD300.450steps each; choose rank1 vs4 by validation accuracy only.',
 'base_model_sha256':digest(basepath),'selected':chosen,'merge_max_abs_logit_error':parity,'metrics':rows,'predictions':predictions,'examples':examples,'loss_curves':history,'split_ids':{'train':ids,'validation':vid,'test':tid},
 'limits':['Not pretrained large language model; base task and synthetic prefixes shared in family.','q/v/head adapted; frozen embedding/FFN limits adaptation, results not universal optimal layer recipe.','Output merged forDemo; adapter tensors retained below; merge reduces extra branches but no GPU latency claim.','Original-task retention may fall, LoRA does not eliminate forgetting.','Same optimizer steps not equal FLOPs/memory; parameter count not measured energy saving.','No real finetuning corpus, human task or original contribution implied.']},dict(model,adapter_state={k:v.tolist() for k,v in variants[chosen].state_dict().items() if '.A' in k or '.B' in k},adapter_scale='1/r'))
if __name__=='__main__':main()
