"""Deeper, bounded experiments: actual local retrieval, child crash, policy sweep."""
import asyncio
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
from .config import Config
from .engine import run_experiment
from .retrieval import RetrievalWorker, quality_report
from .store import Store
from .cli import environment, write_json

LAB=Path(__file__).resolve().parents[1]

def crash_probe(point,policy='resilient'):
    with tempfile.TemporaryDirectory(prefix='flowbench-crash-') as temp:
        database=Path(temp)/'state.sqlite3'
        result=subprocess.run([sys.executable,'-m','reliability_lab.crash_child',
                               '--database',str(database),'--point',point,'--policy',policy],
                              cwd=LAB,timeout=20,capture_output=True,text=True)
        if result.returncode!=73:
            raise RuntimeError(f'expected child crash 73, got {result.returncode}: {result.stderr}')
        s=Store(database)
        cfg=Config(count=4,concurrency=1,profile='clean',base_ms=1)
        try:
            before=s.stats('crash-probe')
            integrity=s.conn.execute('PRAGMA integrity_check').fetchone()[0]
            recovered=asyncio.run(run_experiment(cfg,policy,store=s,scope='crash-probe'))
        finally: s.close()
        return {'point':point,'policy':policy,'child_exit_code':result.returncode,
                'integrity_check':integrity,'before_recovery':before,'recovered':recovered,
                'note':'abrupt os._exit of dedicated child after durable boundary; not power loss or network partition'}

async def retrieval_runs():
    runs=[]
    for seed in (42,43,44):
        cfg=Config(count=20,profile='mixed',seed=seed)
        for policy in ('baseline','retry','resilient'):
            store=Store()
            try:
                worker=RetrievalWorker(cfg,store,'retrieval',policy=='resilient')
                r=await run_experiment(cfg,policy,store=store,scope='retrieval',worker=worker)
                r['environment']=environment()
                runs.append(r)
            finally: store.close()
    return {'kind':'local_retrieval_experiments','quality':quality_report(),'runs':runs,
            'note':'actual BM25 CPU work with authored fixture; latency also includes synthetic waits/faults'}

async def sweep():
    rows=[]
    for seed in (42,43,44):
        # Rotate order to reduce fixed sequencing bias; workload delays stay 140 ms.
        settings=[(c,t) for c in (1,4,8) for t in (35,70,200)]
        settings=settings[seed%9:]+settings[:seed%9]
        for concurrency,timeout in settings:
            cfg=Config(count=24,concurrency=concurrency,timeout_ms=timeout,profile='slow',seed=seed)
            r=await run_experiment(cfg,'resilient')
            rows.append(r)
    aggregates=[]
    for c in (1,4,8):
        for t in (35,70,200):
            selected=[r for r in rows if r['config']['concurrency']==c and r['config']['timeout_ms']==t]
            aggregates.append({'concurrency':c,'timeout_ms':t,'repeats':len(selected),
                'success_rate_mean':statistics.mean(r['summary']['success_rate'] for r in selected),
                'success_rate_range':[min(r['summary']['success_rate'] for r in selected),max(r['summary']['success_rate'] for r in selected)],
                'p95_ms_mean':statistics.mean(r['summary']['p95_ms'] for r in selected),
                'attempts_mean':statistics.mean(r['summary']['attempts'] for r in selected),
                'budget_exhausted_total':sum(r['summary']['status_counts'].get('budget_exhausted',0) for r in selected)})
    return {'kind':'parameter_sweep','aggregates':aggregates,'runs':rows,
            'note':'fixed slow first attempt = 140ms, independent of timeout; count=24 budget=1000ms; actual local timing'}

def main(output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    probes=[crash_probe('after_checkpoint'),crash_probe('after_commit','retry'),crash_probe('after_commit','resilient')]
    write_json(output/'crash.json',{'probes':probes})
    retrieval=asyncio.run(retrieval_runs()); write_json(output/'retrieval.json',retrieval)
    scanning=asyncio.run(sweep()); write_json(output/'sweep.json',scanning)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((LAB/'reliability_lab').glob('*.py'))}
    report={'version':'0.2.0','environment':environment(),'code_sha256':hashes,
            'retrieval_workflows':sum(len(r['tasks']) for r in retrieval['runs']),
            'sweep_workflows':sum(len(r['tasks']) for r in scanning['runs']),
            'crash_probes':len(probes),'sweep':scanning['aggregates'],
            'quality':retrieval['quality']['metrics'],
            'crash':[{k:v for k,v in p.items() if k!='recovered'}|{'summary':p['recovered']['summary']} for p in probes]}
    write_json(output/'advanced.json',report)
    checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.glob('*.json')) if p.name!='checksums.json'}
    write_json(output/'checksums.json',checks)
    lines=['# FlowBench v0.2 深化实验','',
           '真实本地检索运算 + 合成等待/故障；受控子进程崩溃；固定负载参数扫描。不包含 LLM、生产数据或分布式集群。','',
           '## 子进程崩溃恢复','',
           '|崩溃边界|策略|退出码|数据库检查|恢复成功|检查点命中|重复副作用|',
           '|---|---|---:|---|---:|---:|---:|']
    for p in probes:
        s=p['recovered']['summary']
        lines.append(f"|{p['point']}|{p['policy']}|{p['child_exit_code']}|{p['integrity_check']}|{s['succeeded']}|{s['checkpoint_hits']}|{s['duplicate_effects']}|")
    lines+=['','## 检索质量（自建小型样本，非公开 Benchmark）','',
            '|集合|方法|问题数|Recall@3|MRR|','|---|---|---:|---:|---:|']
    for m in retrieval['quality']['metrics']:
        lines.append(f"|{m['split']}|{m['method']}|{m['count']}|{m['recall3']:.3f}|{m['mrr']:.3f}|")
    lines+=['','问题直接对应自建文档，存在明显作者选择偏差；高分不能证明真实任务泛化，也不强求 BM25 胜过 overlap。','',
            '## 固定 140ms 慢操作的参数对照','',
            '|并发|超时 ms|成功率均值|全部 P95 均值 ms|预算耗尽总数|',
            '|---:|---:|---:|---:|---:|']
    for r in scanning['aggregates']:
        lines.append(f"|{r['concurrency']}|{r['timeout_ms']}|{r['success_rate_mean']:.1%}|{r['p95_ms_mean']:.2f}|{r['budget_exhausted_total']}|")
    lines+=['','[全部深化结果](advanced.json) · [检索原始结果](retrieval.json) · [崩溃原始结果](crash.json) · [参数扫描](sweep.json) · [完整性](checksums.json)','',
            '复现：python3 -m reliability_lab deepen --output results/advanced-reproduced。',
            '每次仅杀掉实验自己创建的子进程，不操作其他应用。os._exit 在持久边界强制退出，不证明主机断电、磁盘故障或网络分区容错。']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'retrieval':report['retrieval_workflows'],'sweep':report['sweep_workflows'],'crash_probes':len(probes)}))
