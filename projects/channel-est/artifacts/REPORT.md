# ChannelEst｜本次实际运行

Ideal frequency-domain OFDM-equivalent:32 subcarriers,8 unit pilots,24 QPSK data tones; AWGN complex variance=10^(-SNR/10), block-static channel. Train3600 frames at5/15/25dB, validation600 at15dB. Test4groups x3seeds x220 paired frames.

|group|seed|model|nmse|ber|bit_errors|bits|
|---|---|---|---|---|---|---|
|snr5|31|linear_interpolation|0.32492|0.16383|1730|10560|
|snr5|31|learned_ridge|0.18518|0.13769|1454|10560|
|snr5|31|known_prior_lmmse4|0.16618|0.13598|1436|10560|
|snr5|31|perfect_CSI_oracle|0.00000|0.10066|1063|10560|
|snr5|32|linear_interpolation|0.32314|0.17292|1826|10560|
|snr5|32|learned_ridge|0.19117|0.14896|1573|10560|
|snr5|32|known_prior_lmmse4|0.17325|0.14896|1573|10560|
|snr5|32|perfect_CSI_oracle|0.00000|0.11155|1178|10560|
|snr5|33|linear_interpolation|0.33736|0.16951|1790|10560|
|snr5|33|learned_ridge|0.20325|0.14877|1571|10560|
|snr5|33|known_prior_lmmse4|0.18206|0.14867|1570|10560|
|snr5|33|perfect_CSI_oracle|0.00000|0.11108|1173|10560|
|snr15|31|linear_interpolation|0.06175|0.03627|383|10560|
|snr15|31|learned_ridge|0.02216|0.02045|216|10560|
|snr15|31|known_prior_lmmse4|0.02028|0.01932|204|10560|
|snr15|31|perfect_CSI_oracle|0.00000|0.01326|140|10560|
|snr15|32|linear_interpolation|0.06391|0.03996|422|10560|
|snr15|32|learned_ridge|0.02301|0.02500|264|10560|
|snr15|32|known_prior_lmmse4|0.02099|0.02453|259|10560|
|snr15|32|perfect_CSI_oracle|0.00000|0.01619|171|10560|
|snr15|33|linear_interpolation|0.06509|0.04100|433|10560|
|snr15|33|learned_ridge|0.02397|0.02311|244|10560|
|snr15|33|known_prior_lmmse4|0.02241|0.02348|248|10560|
|snr15|33|perfect_CSI_oracle|0.00000|0.01676|177|10560|
|snr25|31|linear_interpolation|0.03540|0.01657|175|10560|
|snr25|31|learned_ridge|0.00596|0.00208|22|10560|
|snr25|31|known_prior_lmmse4|0.00208|0.00189|20|10560|
|snr25|31|perfect_CSI_oracle|0.00000|0.00114|12|10560|
|snr25|32|linear_interpolation|0.03810|0.01894|200|10560|
|snr25|32|learned_ridge|0.00629|0.00275|29|10560|
|snr25|32|known_prior_lmmse4|0.00215|0.00208|22|10560|
|snr25|32|perfect_CSI_oracle|0.00000|0.00095|10|10560|
|snr25|33|linear_interpolation|0.03830|0.01799|190|10560|
|snr25|33|learned_ridge|0.00621|0.00350|37|10560|
|snr25|33|known_prior_lmmse4|0.00230|0.00294|31|10560|
|snr25|33|perfect_CSI_oracle|0.00000|0.00189|20|10560|
|long_delay_ood|31|linear_interpolation|0.22924|0.11752|1241|10560|
|long_delay_ood|31|learned_ridge|0.20066|0.09223|974|10560|
|long_delay_ood|31|known_prior_lmmse4|0.19984|0.09138|965|10560|
|long_delay_ood|31|perfect_CSI_oracle|0.00000|0.01525|161|10560|
|long_delay_ood|32|linear_interpolation|0.23228|0.12102|1278|10560|
|long_delay_ood|32|learned_ridge|0.19595|0.09299|982|10560|
|long_delay_ood|32|known_prior_lmmse4|0.19516|0.09261|978|10560|
|long_delay_ood|32|perfect_CSI_oracle|0.00000|0.01714|181|10560|
|long_delay_ood|33|linear_interpolation|0.22854|0.11506|1215|10560|
|long_delay_ood|33|learned_ridge|0.20071|0.09678|1022|10560|
|long_delay_ood|33|known_prior_lmmse4|0.19874|0.09678|1022|10560|
|long_delay_ood|33|perfect_CSI_oracle|0.00000|0.01799|190|10560|

## 明确局限
- Frequency-domain idealization; no actual radio, antenna, SDR, CP timing/CFO/ICI/channel coding simulation.
- Known_prior_lmmse4 receives true noise variance and assumed4-tap prior; privileged comparator, not a learned method.
- Perfect CSI is an oracle upper reference; noise still causes bit errors.
- Training/test taps from authored exponential power profile; not standardized3GPP channels.
- 10-tap OOD violates training prior and pilot alias constraints; learned method can fail.
- No claim of5G/6G product or original algorithm. AI assisted independent learning implementation.

[逐样本/逐帧结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
