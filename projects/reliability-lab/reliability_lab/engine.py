from __future__ import annotations
import asyncio
from collections import Counter
import hashlib
import json
import time
from typing import Protocol
from pathlib import Path
from .config import Config, POLICIES, STAGES, VERSION, SLOW_DELAY_MS, fault_for, manifest, unit
from .store import Store

class RetryableError(Exception):
    pass

class PermanentError(Exception):
    pass

class AttemptTimeoutError(RetryableError):
    pass

class Worker(Protocol):
    async def execute(self, task: int, stage: str, attempt: int, previous: dict) -> dict: ...

class SyntheticWorker:
    """Deterministic local fault injection + real async wait, NOT model inference."""
    workload_id = "synthetic_async_io_no_llm"

    def __init__(self, config: Config, store: Store, scope: str, idempotent: bool):
        self.config, self.store, self.scope, self.idempotent = config,store,scope,idempotent

    async def execute(self, task, stage, attempt, previous):
        cfg = self.config
        fault = fault_for(cfg,task,stage)
        duration = cfg.base_ms * (.7 + unit(cfg.seed,task,stage,"duration") * .6) / 1000
        if fault == "slow" and attempt == 1:
            duration = SLOW_DELAY_MS / 1000
        await asyncio.sleep(duration)
        if fault == "transient" and attempt == 1:
            raise RetryableError("synthetic transient failure")
        if fault in ("permanent", "invalid"):
            raise PermanentError("synthetic permanent error" if fault == "permanent" else "output schema validation rejected")
        digest = hashlib.sha256(json.dumps(previous,sort_keys=True).encode()).hexdigest()[:16]
        output = {"task":task, "stage":stage, "input_digest":digest,
                  "content":f"local synthetic {stage} output", "valid":True}
        if stage == "commit":
            self.store.commit(self.scope,task,output,self.idempotent)
            # The side effect exists but its acknowledgement was lost.
            if fault == "ack_lost" and attempt == 1:
                raise RetryableError("side effect committed; synthetic acknowledgement lost")
        return output


def quantile(values, q):
    if not values:
        return None
    values = sorted(values)
    x = (len(values)-1)*q
    lo, hi = int(x), min(int(x)+1,len(values)-1)
    return values[lo] + (values[hi]-values[lo])*(x-lo)

async def run_experiment(config: Config, policy="resilient", *, store=None, scope="experiment", worker=None, pause_after=None):
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    if pause_after is not None and pause_after not in STAGES:
        raise ValueError("unknown pause stage")
    owned = store is None
    store = store or Store()
    worker = worker or SyntheticWorker(config,store,scope,policy == "resilient")
    workload_id = getattr(worker,"workload_id",worker.__class__.__module__+":"+worker.__class__.__qualname__)
    core = Path(__file__).resolve().parent
    code_signature = hashlib.sha256(b"".join((core/name).read_bytes() for name in
                                            ("config.py","engine.py","store.py"))).hexdigest()
    identity = f"{config.signature()}:{policy}:{workload_id}:{code_signature}"
    try:
        store.bind(scope,identity)
    except Exception:
        if owned:
            store.close()
        raise
    start = time.perf_counter()
    events, rows = [], []
    semaphore = asyncio.Semaphore(config.concurrency)
    active = 0
    peak_active = 0

    def emit(task,stage,status,attempt=0,detail=""):
        events.append({"seq":len(events)+1,"time_ms":round((time.perf_counter()-start)*1000,3),
                       "task":task,"stage":stage,"status":status,"attempt":attempt,"detail":detail})

    async def workflow(task):
        nonlocal active, peak_active
        submitted = time.perf_counter()
        queue_ms, attempts, hits = 0.,0,0
        admitted = False
        status, error, output = "succeeded", "", {"task":task,"seed":config.seed}
        emit(task,"workflow","queued")
        async def body():
            nonlocal active,peak_active,queue_ms,attempts,hits,output,status,admitted
            async with semaphore:
                admitted = True
                queue_ms = (time.perf_counter()-submitted)*1000
                active += 1
                peak_active = max(peak_active,active)
                emit(task,"workflow","running")
                try:
                    for stage in STAGES:
                        if policy == "resilient":
                            cached = store.get(scope,task,stage)
                            if cached is not None:
                                output = cached
                                hits += 1
                                emit(task,stage,"checkpoint_hit")
                                continue
                        maximum = 1 if policy == "baseline" else config.attempts
                        for attempt in range(1,maximum+1):
                            attempts += 1
                            emit(task,stage,"attempt_started",attempt)
                            try:
                                operation = worker.execute(task,stage,attempt,output)
                                if policy == "no_timeout":
                                    output = await operation
                                else:
                                    output = await asyncio.wait_for(operation,config.timeout_ms/1000)
                                if not isinstance(output,dict) or output.get("valid") is not True:
                                    raise PermanentError("worker output failed required validity contract")
                            except PermanentError as exc:
                                emit(task,stage,"permanent_error",attempt,str(exc))
                                raise
                            except (RetryableError,TimeoutError) as exc:
                                kind = "attempt_timeout" if isinstance(exc,TimeoutError) else "retryable_error"
                                emit(task,stage,kind,attempt,str(exc))
                                if attempt == maximum:
                                    if isinstance(exc,TimeoutError):
                                        raise AttemptTimeoutError("attempt timeout after retry limit") from exc
                                    raise
                                jitter = .75 + unit(config.seed,task,stage,f"backoff-{attempt}")*.5
                                delay = config.backoff_ms * 2**(attempt-1)*jitter
                                emit(task,stage,"retry_scheduled",attempt,f"backoff_ms={delay:.3f}")
                                await asyncio.sleep(delay/1000)
                            else:
                                emit(task,stage,"stage_succeeded",attempt)
                                if policy == "resilient":
                                    store.save(scope,task,stage,output)
                                break
                        if pause_after == stage:
                            status = "paused"
                            emit(task,"workflow","paused",detail=f"after {stage}")
                            return
                finally:
                    active -= 1
        try:
            await asyncio.wait_for(body(),config.budget_ms/1000)
        except TimeoutError:
            status,error = "budget_exhausted", "workflow deadline includes queue and retries"
        except RetryableError as exc:
            status,error = "retry_exhausted",str(exc)
        except PermanentError as exc:
            status,error = "permanent_failed",str(exc)
        except Exception as exc:
            status,error = "internal_failed",f"{type(exc).__name__}: {exc}"
        if not admitted:
            queue_ms = (time.perf_counter()-submitted)*1000
        emit(task,"workflow",status,detail=error)
        rows.append({"task":task,"status":status,"latency_ms":round((time.perf_counter()-submitted)*1000,3),
                     "queue_ms":round(queue_ms,3),"attempts":attempts,"checkpoint_hits":hits,"error":error,
                     "output":output if status == "succeeded" else None})

    try:
        await asyncio.gather(*(workflow(task) for task in range(config.count)))
        elapsed = time.perf_counter()-start
        rows.sort(key=lambda row:row["task"])
        latencies = [row["latency_ms"] for row in rows]
        successes = [row["latency_ms"] for row in rows if row["status"] == "succeeded"]
        failures = Counter(row["status"] for row in rows)
        summary = {"count":len(rows),"succeeded":len(successes),"success_rate":len(successes)/len(rows),
                   "elapsed_ms":round(elapsed*1000,3),"p50_ms":quantile(latencies,.5),
                   "p95_ms":quantile(latencies,.95),"p99_ms":quantile(latencies,.99),
                   "success_p95_ms":quantile(successes,.95),
                   "completion_per_second":len(rows)/elapsed,"success_per_second":len(successes)/elapsed,
                   "attempts":sum(row["attempts"] for row in rows),
                   "checkpoint_hits":sum(row["checkpoint_hits"] for row in rows),
                   "retries":sum(e["status"] == "retry_scheduled" for e in events),
                   "attempt_timeouts":sum(e["status"] == "attempt_timeout" for e in events),
                   "peak_active":peak_active,"status_counts":dict(failures),**store.stats(scope)}
        faults = manifest(config)
        fault_hash = hashlib.sha256(json.dumps(faults,sort_keys=True).encode()).hexdigest()
        return {"schema_version":1,"version":VERSION,"workload":workload_id,"runtime_hash":code_signature,
                "config":config.dict(),"policy":policy,"manifest_hash":fault_hash,
                "manifest":faults,"summary":summary,"tasks":rows,"events":events,
                "measurement_note":"real local wall clock; synthetic workloads; ledger counts cumulative within scope"}
    finally:
        if owned:
            store.close()

async def compare(config, policies=("baseline","retry","resilient")):
    results=[]
    for policy in policies:
        results.append(await run_experiment(config,policy))
    return {"schema_version":1,"kind":"paired_policy_comparison","results":results}
