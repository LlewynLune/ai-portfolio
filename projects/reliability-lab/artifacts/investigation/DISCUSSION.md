# FlowBench · 崩溃窗口与端到端期限：结果讨论

18次真实进程退出恢复：retry重复副作用6次，resilient 0次；仅局部SQLite边界。

## 仍未完成的下一阶段

下一阶段跨进程并发与模拟外部服务协议，不把SQLite幂等当分布式exactly-once。

[原始结果](results.json) · [实验协议与方法](REPORT.md)
