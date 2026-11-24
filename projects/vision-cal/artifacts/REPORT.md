# VisionCal｜本次实际运行

1797 public 8x8 images; fixed 60/20/20 stratified split. MLP trained only train; temperature minimizes validation NLL only; clean and corrupted test share held-out image IDs.

|group|model|accuracy|nll|ece10|coverage90|selective_error90|
|---|---|---|---|---|---|---|
|clean|logistic|0.95556|0.19277|0.07449|0.64444|0.00000|
|clean|mlp_raw|0.97222|0.11267|0.01236|0.89167|0.00623|
|clean|mlp_temperature|0.97222|0.12101|0.01658|0.92778|0.00898|
|noise_sigma0.25|logistic|0.87500|0.41101|0.08690|0.42222|0.00658|
|noise_sigma0.25|mlp_raw|0.83611|0.48207|0.06421|0.72222|0.07308|
|noise_sigma0.25|mlp_temperature|0.83611|0.56556|0.09170|0.78889|0.07746|
|shift_right1px|logistic|0.39444|2.22489|0.28029|0.18611|0.44776|
|shift_right1px|mlp_raw|0.49722|3.04769|0.33904|0.51944|0.40107|
|shift_right1px|mlp_temperature|0.49722|3.93613|0.38164|0.62500|0.44000|

## 明确局限
- Not MNIST, CNN, foundation model or real OCR; small sklearn MLP.
- Digits split has no writer IDs; writer leakage cannot be ruled out.
- Temperature can improve NLL without raising accuracy; ECE bins arbitrary.
- Corruptions are authored tests, not real deployment distribution.
- Confidence0.9 is a fixed demo threshold, not a safety guarantee.
- AI assisted; no prior personal research or production achievement implied.

[逐样本/逐帧结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
