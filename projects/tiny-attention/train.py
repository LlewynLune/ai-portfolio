"""Causal attention learns key-value association; train/held-out prefixes disjoint."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from frontier_support import *
ROOT=Path(__file__).resolve().parent

def main():
 x,y,ids=generate(3000,10);va,vy,vid=generate(500,20,exclude=ids);te,ty,tid=generate(600,30,exclude=ids+vid);ood,oy,oid=generate(600,40,pairs=5)
 torch.manual_seed(42);net=TinyAttention();loss=train_model(net,x,y,1000);torch.manual_seed(42);abl=TinyAttention(attention=False);aloss=train_model(abl,x,y,1000)
 rows=[];predictions=[];examples=[]
 for group,xx,yy in [('validation',va,vy),('heldout3pairs',te,ty),('length5pairs_ood',ood,oy)]:
  for name,m in [('causal_attention',net),('no_attention_ablation',abl)]:
   met,prob=evaluate(m,xx,yy);rows.append({'group':group,'model':name,'trainable_parameters':param_count(m),**met});predictions += [{'group':group,'model':name,'index':i,'truth':int(t),'probabilities':p} for i,(t,p) in enumerate(zip(yy,prob))]
  _,p=evaluate(net,xx,yy)
  for i in [0,1,2]:
   with torch.no_grad():logits,att=net(xx[i:i+1],True)
   examples.append({'group':group,'tokens':xx[i].tolist(),'truth':int(yy[i]),'probabilities':p[i],'attention_last_query':att[0,:,-1].tolist()})
 save(ROOT,{'title':'TinyAttention','protocol':'3000 train,500 validation,600 held-out3pair prefixes disjoint;600 authored5pair OOD. Fixed1000 Adam steps and no-attention ablation. Only final query value is supervised, not full language modeling.',
 'metrics':rows,'predictions':predictions,'examples':examples,'loss_curve':loss,'ablation_loss':aloss,'split_ids':{'train':ids,'validation':vid,'test':tid},
 'limits':['One tiny causal block,2heads,d32; no natural-language pretraining or foundation model.','Synthetic associative lookup; train and test generator shared,5pair length OOD has untrained positional slots.','Validation reported only; fixed hyperparameters, no test selection.','No-attention model has fewer active computation paths, not matched-FLOP comparison.','PyTorch autograd provides differentiation; algorithm implementation AI assisted.','Attention weights are not a causal explanation or proof of reasoning.']},export(net))
if __name__=='__main__':main()
