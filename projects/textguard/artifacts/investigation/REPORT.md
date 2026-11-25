# TextGuard · 部署先验变化与误报成本

低发生率部署下，旧测试准确率是否掩盖精确率失效？

## 预声明实验协议

{
  "kind": "frozen_test_prediction_reweighting",
  "target_prevalences": [
    0.01,
    0.05,
    0.12,
    0.3,
    0.5
  ],
  "assumption": "label shift p(x|y) unchanged; target prior is given, not estimated",
  "threshold": "original validation-chosen threshold frozen",
  "records_not_new_examples": true
}

## 全部条件结果

|model|mode|target_prior|n|precision|recall|weighted_error|weighted_brier|weighted_nll|
|---|---|---|---|---|---|---|---|---|
|majority|unchanged|0.01|1020|None|0|0.01|0.021302|0.14441|
|majority|prior_odds_adjusted|0.01|1020|None|0|0.01|0.0099|0.056002|
|multinomial_nb|unchanged|0.01|1020|1|0.78151|0.0021849|0.0026831|0.022424|
|multinomial_nb|prior_odds_adjusted|0.01|1020|1|0.36134|0.0063866|0.0049071|0.018746|
|tfidf_logistic|unchanged|0.01|1020|0.32438|0.94958|0.020282|0.017592|0.087347|
|tfidf_logistic|prior_odds_adjusted|0.01|1020|0.64969|0.81513|0.0062439|0.0047247|0.019272|
|majority|unchanged|0.05|1020|None|0|0.05|0.05196|0.22535|
|majority|prior_odds_adjusted|0.05|1020|None|0|0.05|0.0475|0.19852|
|multinomial_nb|unchanged|0.05|1020|1|0.78151|0.010924|0.0096264|0.045332|
|multinomial_nb|prior_odds_adjusted|0.05|1020|1|0.68067|0.015966|0.013413|0.051532|
|tfidf_logistic|unchanged|0.05|1020|0.71442|0.94958|0.0215|0.018549|0.089846|
|tfidf_logistic|prior_odds_adjusted|0.05|1020|0.848|0.94118|0.011376|0.011513|0.054685|
|majority|unchanged|0.12|1020|None|0|0.12|0.10561|0.36697|
|majority|prior_odds_adjusted|0.12|1020|None|0|0.12|0.1056|0.36692|
|multinomial_nb|unchanged|0.12|1020|1|0.78151|0.026218|0.021777|0.085422|
|multinomial_nb|prior_odds_adjusted|0.12|1020|1|0.78992|0.02521|0.021519|0.08482|
|tfidf_logistic|unchanged|0.12|1020|0.86634|0.94958|0.023631|0.020223|0.09422|
|tfidf_logistic|prior_odds_adjusted|0.12|1020|0.85995|0.94958|0.024608|0.020539|0.095638|
|majority|unchanged|0.3|1020|None|0|0.3|0.24357|0.73116|
|majority|prior_odds_adjusted|0.3|1020|None|0|0.3|0.21|0.61086|
|multinomial_nb|unchanged|0.3|1020|1|0.78151|0.065546|0.053022|0.18851|
|multinomial_nb|prior_odds_adjusted|0.3|1020|0.99405|0.86555|0.04189|0.033179|0.13264|
|tfidf_logistic|unchanged|0.3|1020|0.95321|0.94958|0.029111|0.024529|0.10547|
|tfidf_logistic|prior_odds_adjusted|0.3|1020|0.89668|0.96639|0.043491|0.040255|0.16399|
|majority|unchanged|0.5|1020|None|0|0.5|0.39686|1.1358|
|majority|prior_odds_adjusted|0.5|1020|0.5|1|0.5|0.25|0.69315|
|multinomial_nb|unchanged|0.5|1020|1|0.78151|0.10924|0.087739|0.30305|
|multinomial_nb|prior_odds_adjusted|0.5|1020|0.98696|0.92437|0.043919|0.039743|0.15513|
|tfidf_logistic|unchanged|0.5|1020|0.97939|0.94958|0.035199|0.029313|0.11796|
|tfidf_logistic|prior_odds_adjusted|0.5|1020|0.89698|0.96639|0.072301|0.056635|0.20333|

## 发现、失败与适用边界

- 这是原测试预测的假设性重加权，不是新用户或真实部署数据。
- 先验校正依赖标签条件分布不变，不能纠正新词汇/语言/诈骗概念漂移。
- 测试重加权结果不用于重新选择阈值；全部目标先验同时报告。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project textguard。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
