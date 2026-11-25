# PowerScope · 严格先预测后更新的区间运营：结果讨论

chronological_test fixed：覆盖 92.0%、区间宽 113.7kW、点预测MAE 26.0kW。

chronological_test past_residual_quantile：覆盖 89.7%、区间宽 104.1kW、点预测MAE 26.0kW。

cooling_drift_ood fixed：覆盖 17.3%、区间宽 113.7kW、点预测MAE 120.6kW。

cooling_drift_ood past_residual_quantile：覆盖 87.7%、区间宽 415.4kW、点预测MAE 120.6kW。

## 仍未完成的下一阶段

下一阶段用公开实测负荷并重新冻结时序分割；区间更新不解决点预测漂移。

[原始结果](results.json) · [实验协议与方法](REPORT.md)
