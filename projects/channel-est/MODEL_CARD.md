# ChannelEst｜导频驱动的学习型信道估计｜模型卡

## 模型与预期用途

Rayleigh多径仿真 → 32频点/8单位导频/24 QPSK数据 → 复AWGN → 导频特征 → 插值/学习Ridge/先验LMMSE/真CSI → 固定均衡 → NMSE与BER。

默认导出类型：linear；输入维数16。仅离线学习、参数推断、复现与失败分析。

## 数据、训练与测试

Ideal frequency-domain OFDM-equivalent:32 subcarriers,8 unit pilots,24 QPSK data tones; AWGN complex variance=10^(-SNR/10), block-static channel. Train3600 frames at5/15/25dB, validation600 at15dB. Test4groups x3seeds x220 paired frames.

[实际指标](artifacts/REPORT.md)不是生产指标，也没有第三方审计。训练环境记录在[结果](artifacts/results.json)中，代码和数据/参数哈希不证明专业资质。

## 禁止外推

- Frequency-domain idealization; no actual radio, antenna, SDR, CP timing/CFO/ICI/channel coding simulation.
- Known_prior_lmmse4 receives true noise variance and assumed4-tap prior; privileged comparator, not a learned method.
- Perfect CSI is an oracle upper reference; noise still causes bit errors.
- Training/test taps from authored exponential power profile; not standardized3GPP channels.
- 10-tap OOD violates training prior and pilot alias constraints; learned method can fail.
- No claim of5G/6G product or original algorithm. AI assisted independent learning implementation.

## 人机分工与退出

页面只显示模型输出和假设；缺失输入/维数错误/非有限数拒绝。修改输入后不再显示预设样本标签作为真值。分布外、无真实标签、数据可用性不足时必须人工调查，不把模型倾向写成事实。

## 贡献与许可

AI辅助学习实现，用户提出范围；本人独立贡献尚待亲自修改与验证，不以此冒充已掌握的研究经历。数据/参考许可分别适用，仓库暂未统一授予开源许可证。
