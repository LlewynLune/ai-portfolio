# ChannelEst｜导频驱动的学习型信道估计｜原理、对照与失败

## 理想链路定义

只实现频域理想OFDM等效链路 $Y_k=H_kS_k+W_k$。32频点，导频为0/4/8/.../28，值为1；剩余24点为独立QPSK，幅度归一化。4tap复高斯信道，功率随delay指数下降并使平均频域增益功率约1。

SNR是平均符号能量与复噪声方差之比，噪声每个实/虚分量方差为 $10^{-\mathrm{SNR}/10}/2$。不是 $E_b/N_0$；没有编码、CP能量/导频开销调整，不把结果偷换为射频系统链路预算。

### 公平与先验

1. 周期线性插值，频域边界连接最后导频与第0导频。
2. 学习Ridge：导频实部/虚部16维 → 全信道实部/虚部64维；训练5/15/25dB共3600帧，15dB验证600选择alpha0.01/1/10/100，测试不用来调参。
3. 先验LMMSE：$\widehat H=R_{hp}(R_{pp}+\sigma^2I)^{-1}Z$；4tap协方差与真实噪声方差提供给算法，属于特权对照，不写成学习模型胜利。
4. 真CSI：使用生成器H，只作为oracle，不是可部署算法；即使CSI完美，噪声仍导致误码。

### 下游验证

固定类ZF均衡 $\widehat S=Y\widehat H^*/(|\widehat H|^2+10^{-6})$，按实虚正负判位。所有方法共享同帧、同噪声、同比特；NMSE按帧先归一化再平均，BER按总错误比特/总数据比特累计。保存每帧NMSE和错误数，可重算而非只看图。

三个SNR与10tap长delay OOD，每组3seed×220帧。长delay打破训练4tap先验以及8导频可辨识范围；学习/先验对照都可能错误。稀疏导频 alias 与信道建模偏差不能靠“AI”标题解决。

### 未实现与术语边界

没有实际OFDM时域发射/接收、CP插入、定时同步、CFO、ICI、信道编码、MIMO、天线、无线发射或SDR。不是5G/6G或3GPP实测。Ridge为数据驱动线性估计器，不是深度网络，也不是原创论文算法。源码为独立实现，不复制参考站点代码。

## 本批原始证据

Ideal frequency-domain OFDM-equivalent:32 subcarriers,8 unit pilots,24 QPSK data tones; AWGN complex variance=10^(-SNR/10), block-static channel. Train3600 frames at5/15/25dB, validation600 at15dB. Test4groups x3seeds x220 paired frames.

[完整表](artifacts/REPORT.md)保留所有组与seed；[JSON](artifacts/results.json)保留逐项预测、样本与运行环境。SHA校验只能发现变更，不是第三方签名。重新修改train.py或共享生成器后必须重跑，不得把旧结果重新打hash当新证据。

来源：https://wirelesspi.com/channel-estimation-in-ofdm-systems/
