"""Crash only this experiment child, at explicitly selected persistence boundaries."""
import argparse
import asyncio
import os
from .config import Config
from .engine import run_experiment
from .store import Store

class CrashStore(Store):
    def __init__(self,path,point):
        super().__init__(path); self.point=point
    def save(self,scope,task,stage,output):
        super().save(scope,task,stage,output)
        if self.point=='after_checkpoint' and task==0 and stage=='analyze':
            os._exit(73)
    def commit(self,scope,task,output,idempotent):
        result=super().commit(scope,task,output,idempotent)
        if self.point=='after_commit' and task==0:
            os._exit(73)
        return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--database',required=True)
    p.add_argument('--point',choices=('after_checkpoint','after_commit'),required=True)
    p.add_argument('--policy',choices=('retry','resilient'),default='resilient')
    args=p.parse_args()
    if args.point=='after_checkpoint' and args.policy!='resilient':
        p.error('checkpoint crash requires resilient policy')
    s=CrashStore(args.database,args.point)
    try:
        asyncio.run(run_experiment(Config(count=4,concurrency=1,profile='clean',base_ms=1),
                                   args.policy,store=s,scope='crash-probe'))
    finally: s.close()

if __name__=='__main__': main()
