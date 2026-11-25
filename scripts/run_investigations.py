"""Run project-specific investigations. Original results never overwritten."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'projects'))
from investigations import classification,algorithms,engineering,systems,retrieval
RUNNERS={'textguard':classification.textguard,'novelty-lab':classification.novelty,'vision-cal':classification.vision,'tiny-attention':algorithms.tiny,'lora-lab':algorithms.lora,'dpo-lab':algorithms.dpo,'moe-lab':algorithms.moe,'spec-decode':algorithms.spec,'circuit-id':engineering.circuit,'channel-est':engineering.channel,'power-scope':engineering.power,'video-guard':systems.video,'reliability-lab':systems.reliability}
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=list(RUNNERS)+['cite-rag','all'],required=True);p.add_argument('--model-path');a=p.parse_args()
 if a.project in ('all','cite-rag') and not a.model_path:p.error('--model-path required for cite-rag actual local model')
 selected=list(RUNNERS) if a.project=='all' else [a.project]
 for project in selected:
  if project in RUNNERS:RUNNERS[project]()
 if a.project in ('cite-rag','all'):retrieval.cite(a.model_path)
if __name__=='__main__':main()
