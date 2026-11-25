# FlowBench · 崩溃窗口与端到端期限

真正进程退出发生在提交与检查点之间时，重启会重复副作用吗？

## 预声明实验协议

{
  "kind": "real_process_abrupt_exit_and_queue_deadline",
  "crash_points": [
    "before_effect",
    "after_effect_before_checkpoint",
    "after_checkpoint"
  ],
  "strategies": [
    "retry",
    "resilient"
  ],
  "repeats": 3,
  "subprocess_exit": 73,
  "effects": "local SQLite only",
  "deadline_budget_ms": [
    30,
    80,
    200
  ],
  "concurrency": [
    1,
    4
  ]
}

## 全部条件结果

|kind|policy|budget_ms|concurrency|seed|succeeded|count|p95_ms|retries|duplicate_effects|crash_point|
|---|---|---|---|---|---|---|---|---|---|---|
|deadline_load|retry|30|1|198001|1|12|30.43|0|0|—|
|deadline_load|resilient|30|1|198001|1|12|30.414|0|0|—|
|deadline_load|retry|30|1|198002|1|12|30.204|1|0|—|
|deadline_load|resilient|30|1|198002|1|12|30.174|1|0|—|
|deadline_load|retry|30|1|198003|1|12|30.349|1|1|—|
|deadline_load|resilient|30|1|198003|1|12|30.286|1|0|—|
|deadline_load|retry|30|4|198001|2|12|30.146|3|0|—|
|deadline_load|resilient|30|4|198001|2|12|30.086|3|0|—|
|deadline_load|retry|30|4|198002|6|12|30.105|3|1|—|
|deadline_load|resilient|30|4|198002|4|12|30.166|3|0|—|
|deadline_load|retry|30|4|198003|3|12|30.159|3|1|—|
|deadline_load|resilient|30|4|198003|3|12|30.238|3|0|—|
|deadline_load|retry|80|1|198001|2|12|80.234|2|0|—|
|deadline_load|resilient|80|1|198001|2|12|80.186|2|0|—|
|deadline_load|retry|80|1|198002|4|12|80.288|2|1|—|
|deadline_load|resilient|80|1|198002|4|12|80.217|2|0|—|
|deadline_load|retry|80|1|198003|2|12|80.145|2|1|—|
|deadline_load|resilient|80|1|198003|2|12|80.272|2|0|—|
|deadline_load|retry|80|4|198001|9|12|59.327|4|0|—|
|deadline_load|resilient|80|4|198001|9|12|62.228|4|0|—|
|deadline_load|retry|80|4|198002|12|12|69.938|6|1|—|
|deadline_load|resilient|80|4|198002|12|12|69.975|6|0|—|
|deadline_load|retry|80|4|198003|10|12|70.504|8|2|—|
|deadline_load|resilient|80|4|198003|10|12|70.764|8|0|—|
|deadline_load|retry|200|1|198001|7|12|200.19|3|0|—|
|deadline_load|resilient|200|1|198001|7|12|200.52|3|0|—|
|deadline_load|retry|200|1|198002|9|12|200.47|4|1|—|
|deadline_load|resilient|200|1|198002|9|12|200.55|4|0|—|
|deadline_load|retry|200|1|198003|7|12|200.69|5|2|—|
|deadline_load|resilient|200|1|198003|7|12|200.93|5|0|—|
|deadline_load|retry|200|4|198001|9|12|58.917|4|0|—|
|deadline_load|resilient|200|4|198001|9|12|59.194|4|0|—|
|deadline_load|retry|200|4|198002|12|12|69.76|6|1|—|
|deadline_load|resilient|200|4|198002|12|12|69.459|6|0|—|
|deadline_load|retry|200|4|198003|10|12|69.762|8|2|—|
|deadline_load|resilient|200|4|198003|10|12|69.718|8|0|—|
|abrupt_exit|retry|None|None|0|1|1|None|None|0|before_effect|
|abrupt_exit|retry|None|None|1|1|1|None|None|0|before_effect|
|abrupt_exit|retry|None|None|2|1|1|None|None|0|before_effect|
|abrupt_exit|retry|None|None|0|1|1|None|None|1|after_effect_before_checkpoint|
|abrupt_exit|retry|None|None|1|1|1|None|None|1|after_effect_before_checkpoint|
|abrupt_exit|retry|None|None|2|1|1|None|None|1|after_effect_before_checkpoint|
|abrupt_exit|retry|None|None|0|1|1|None|None|1|after_checkpoint|
|abrupt_exit|retry|None|None|1|1|1|None|None|1|after_checkpoint|
|abrupt_exit|retry|None|None|2|1|1|None|None|1|after_checkpoint|
|abrupt_exit|resilient|None|None|0|1|1|None|None|0|before_effect|
|abrupt_exit|resilient|None|None|1|1|1|None|None|0|before_effect|
|abrupt_exit|resilient|None|None|2|1|1|None|None|0|before_effect|
|abrupt_exit|resilient|None|None|0|1|1|None|None|0|after_effect_before_checkpoint|
|abrupt_exit|resilient|None|None|1|1|1|None|None|0|after_effect_before_checkpoint|
|abrupt_exit|resilient|None|None|2|1|1|None|None|0|after_effect_before_checkpoint|
|abrupt_exit|resilient|None|None|0|1|1|None|None|0|after_checkpoint|
|abrupt_exit|resilient|None|None|1|1|1|None|None|0|after_checkpoint|
|abrupt_exit|resilient|None|None|2|1|1|None|None|0|after_checkpoint|

## 发现、失败与适用边界

- 子进程真实os._exit，在SQLite commit与checkpoint边界注入退出，恢复重新打开数据库。
- 幂等仅此单数据库范围，不代表分布式exactly-once或外部API保护。
- 排队期限含等待/重试/失败，短期限结果不只统计成功延迟；异步IO负载非模型推断。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project reliability-lab。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
