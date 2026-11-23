from __future__ import annotations
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import platform
import statistics
from pathlib import Path
from .config import Config, PROFILES, POLICIES
from .engine import compare, run_experiment
from .store import Store


def environment():
    # No hostname, username, absolute project path, IP, or company identifiers.
    return {"python":platform.python_version(),"os":platform.system(),
            "os_release":platform.release(),"machine":platform.machine(),
            "timestamp_utc":datetime.now(timezone.utc).isoformat()}


def write_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


async def suite(output: Path, repeats=5):
    output.mkdir(parents=True,exist_ok=True)
    groups=[]
    for profile in ("clean","transient","mixed","ack_loss","permanent","slow"):
        runs=[]
        for repeat in range(repeats):
            cfg=Config(profile=profile,seed=42+repeat)
            policies=("baseline","retry","resilient","no_timeout")
            order=policies[repeat % len(policies):]+policies[:repeat % len(policies)]
            paired=await compare(cfg,order)
            for result in paired["results"]:
                result["repeat"]=repeat
                result["environment"]=environment()
                filename=f"{profile}-{repeat}-{result['policy']}.json"
                write_json(output/filename,result)
                runs.append({"file":filename,"policy":result["policy"],"repeat":repeat,
                             "manifest_hash":result["manifest_hash"],"summary":result["summary"]})
        aggregated=[]
        for policy in policies:
            values=[r["summary"] for r in runs if r["policy"] == policy]
            aggregated.append({"policy":policy,"runs":len(values),
                "success_rate_mean":statistics.mean(x["success_rate"] for x in values),
                "success_rate_min":min(x["success_rate"] for x in values),
                "success_rate_max":max(x["success_rate"] for x in values),
                "p95_ms_mean":statistics.mean(x["p95_ms"] for x in values),
                "elapsed_ms_mean":statistics.mean(x["elapsed_ms"] for x in values),
                "duplicate_effects_total":sum(x["duplicate_effects"] for x in values),
                "attempts_total":sum(x["attempts"] for x in values),
                "attempt_timeouts_total":sum(x["attempt_timeouts"] for x in values)})
        groups.append({"profile":profile,"aggregated":aggregated,"runs":runs})
    store=Store(output/"resume.sqlite3")
    cfg=Config(count=8,profile="clean")
    # Keep demonstration independent of previous suite invocations.
    import uuid
    scope="recovery-"+uuid.uuid4().hex
    try:
        pause=await run_experiment(cfg,"resilient",store=store,scope=scope,pause_after="analyze")
        resumed=await run_experiment(cfg,"resilient",store=store,scope=scope)
        warm=await run_experiment(cfg,"resilient",store=store,scope=scope)
    finally:
        store.close()
    recovery={"pause":pause,"resumed":resumed,"warm":warm,
              "note":"controlled boundary pause, not simulated machine crash; WAL persistence is covered by tests"}
    write_json(output/"recovery.json",recovery)
    source=Path(__file__).resolve().parent
    code_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.glob('*.py'))}
    report={"schema_version":1,"kind":"benchmark_suite","environment":environment(),
            "code_sha256":code_hashes,
            "repeats":repeats,"count_per_run":24,"groups":groups,
            "recovery_file":"recovery.json","recovery":{k:v["summary"] for k,v in recovery.items() if isinstance(v,dict)},
            "limits":["synthetic I/O, not LLM inference","local single-process, not distributed",
                      "sequential policy runs; timing sensitive to machine load",
                      "same seed fixes fault manifest, not wall-clock timing",
                      "5-run summaries are descriptive, not causal production estimates"]}
    write_json(output/"benchmark.json",report)
    lines=["# 本地合成负载评测报告","",f"重复次数：{repeats}；每次每策略 24 个工作流；6 类负载；4 种策略。",
           "真实计时，合成故障，无模型调用，无业务降本结论。","",
           "|负载|策略|成功率均值|成功率范围|全部请求 P95 均值 ms|重复副作用总数|",
           "|---|---|---:|---|---:|---:|"]
    for group in groups:
        for row in group["aggregated"]:
            lines.append(f"|{group['profile']}|{row['policy']}|{row['success_rate_mean']:.1%}|{row['success_rate_min']:.1%}–{row['success_rate_max']:.1%}|{row['p95_ms_mean']:.2f}|{row['duplicate_effects_total']}|")
    lines += ["","## 口径与解释","",
              "baseline：同样并发和工作流预算；每节点只尝试一次，设单次超时。",
              "retry：允许有限重试及指数退避；没有检查点和幂等提交。",
              "resilient：与 retry 同样重试和超时，增加检查点和本地 ledger 幂等。",
              "no_timeout：与 retry 相同，但取消单次超时；仍有全工作流截止时间。它是超时消融，不是无预算运行。",
              "成功率以工作流最终 succeeded 为分子、全部提交为分母；P95 基于所有完成状态的端到端时间，包括排队。成功请求 P95 在原始结果中单列。",
              "重复副作用统计提交次数减不同任务数量，不意味着业务事故或远程系统 exactly-once。",
              "故障清单哈希在同 seed 的不同策略间一致，可直接复核；原始事件与逐任务结果保存在每个 JSON 文件中。",
              "","## 恢复演示","",
              f"阶段边界暂停后恢复：命中 {resumed['summary']['checkpoint_hits']} 个检查点；新增 {resumed['summary']['attempts']} 次尝试。",
              f"完全完成后重新启动：命中 {warm['summary']['checkpoint_hits']} 个检查点；新增 {warm['summary']['attempts']} 次尝试。",
              "演示是受控阶段暂停；不据此宣称耐受主机断电或分布式网络分区。",
              "","## 文件与完整性","","[汇总 JSON](benchmark.json) · [恢复事件](recovery.json) · [完整性清单](checksums.json)",
              "运行复现：在项目目录执行 python3 -m reliability_lab suite --output results/reproduced --repeats 5。"]
    (output/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    files={path.name:hashlib.sha256(path.read_bytes()).hexdigest()
           for path in sorted(output.glob("*.json")) if path.name != "checksums.json"}
    write_json(output/"checksums.json",files)
    return report


def main():
    parser=argparse.ArgumentParser(description="Synthetic local workflow reliability laboratory")
    sub=parser.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run")
    run.add_argument("--policy",choices=POLICIES,default="resilient")
    run.add_argument("--profile",choices=PROFILES,default="mixed")
    run.add_argument("--count",type=int,default=24)
    run.add_argument("--concurrency",type=int,default=4)
    run.add_argument("--seed",type=int,default=42)
    run.add_argument("--database",type=Path)
    run.add_argument("--scope",default="manual-run")
    run.add_argument("--pause-after",choices=("ingest","retrieve","analyze","validate"))
    run.add_argument("--output",type=Path)
    batch=sub.add_parser("suite")
    batch.add_argument("--output",type=Path,default=Path("results/reproduced"))
    batch.add_argument("--repeats",type=int,choices=range(1,11),default=5)
    serve=sub.add_parser("serve")
    serve.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    if args.command == "serve":
        from .server import serve as start_server
        start_server(args.port)
    elif args.command == "suite":
        report=asyncio.run(suite(args.output,args.repeats))
        print(json.dumps({"profiles":len(report["groups"]),"repeats":report["repeats"]},indent=2))
    else:
        cfg=Config(count=args.count,concurrency=args.concurrency,seed=args.seed,profile=args.profile)
        store=Store(args.database) if args.database else None
        try:
            result=asyncio.run(run_experiment(cfg,args.policy,store=store,scope=args.scope,pause_after=args.pause_after))
        finally:
            if store:
                store.close()
        if args.output:
            write_json(args.output,result)
        print(json.dumps(result["summary"],ensure_ascii=False,indent=2))
