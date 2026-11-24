"""Summarize frozen cross-disciplinary results without selecting favorable runs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=['vision-cal','circuit-id','channel-est','power-scope']
lines=['# 跨学科实验｜阅读与复核指南','', '本批四项目加已有四项，共八个独立研究作品；基线、模块和Demo不重复计数。AI辅助实现，个人独立研究/硬件/生产履历未被验证。不是“满分”或招聘官方标准。','', '## 四条主线','', '|方向|作品|要验证的问题|数据边界|','|---|---|---|---|','|AI算法|VisionCal|校准是否能提高可信度，扰动时是否高置信出错|公开8×8图像；真实小MLP训练|','|电子科学与技术|CircuitID|学习辨识何时胜出，何时物理拟合更稳|理想RC数学仿真；无硬件|','|信息与通信工程|ChannelEst|导频到信道的学习映射能否改善NMSE/BER|理想频域QPSK，多径AWGN；无无线设备|','|AI数据中心/电气工程|PowerScope|计划信息、时间因果与冷却漂移如何影响负荷预测|透明合成时序；仅只读，无设备控制|','', '## 本批冻结结果：不利情况一并看']
for p in P:
 r=json.loads((ROOT/'projects'/p/'artifacts/results.json').read_text());rows=r['metrics'];keys=[k for k,v in rows[0].items() if isinstance(v,(int,float)) and k not in ['seed','bits','bit_errors','flag_tp','flag_fp','flag_fn']]
 lines+=['','### '+r['title'],'',r['protocol'],'','表中多seed组对三个seed均值；原始报告逐seed保留，无统计显著性断言。VisionCal只有一个训练seed；PowerScope时间相关且只有一个主轨迹。','', '|group|model|'+'|'.join(keys)+'|','|---|---|'+'|'.join(['---:']*len(keys))+'|']
 groups=sorted({(x['group'],x['model']) for x in rows})
 for g,m in groups:
  selected=[x for x in rows if x['group']==g and x['model']==m];values=[]
  for k in keys:
   nums=[x[k] for x in selected if x[k] is not None];values.append(f'{sum(nums)/len(nums):.5f}' if nums else '—')
  lines.append('|'+g+'|'+m+'|'+'|'.join(values)+'|')
 lines+=['',f'[可操作页面](../projects/{p}/demo.html) · [逐项实测](../projects/{p}/artifacts/REPORT.md) · [原理与协议](../projects/{p}/METHOD.md) · [模型卡](../projects/{p}/MODEL_CARD.md)']
lines+=['','## 必须保留的发现','', '- VisionCal：验证温度选择并未使测试NLL更好；平移时置信仍高。达到训练迭代上限的优化警告不能解释成收敛证明。','- CircuitID：同分布学习Ridge有用，偏置/慢tau外推显著失败；强噪声或范围外物理拟合更稳。MLP复杂不等于胜出。','- ChannelEst：学习映射比简单插值好，但不等于超过获得真实噪声与先验的LMMSE；长delay OOD仍明显退化。','- PowerScope：计划输入减少大突变RMSE，却可能提高MAE；冷却漂移使经验区间覆盖率与峰值漏报恶化。','', '## 复现与证据','', '训练用 requirements-ml.txt，原始结果记录Python/numpy/sklearn环境。train.py和共享数值函数均有哈希；模型和结果有校验，哈希只发现改动不是第三方签名。所有逐点/帧预测可重算，导出参数在JavaScript与Python之间逐例核验。','', '模型参数推断Demo与训练仿真不是同一件事：浏览器只运行冻结模型，不重新训练，也不访问真实电路/无线/机房。修改输入后来源标签不继续冒充真值。','', '来源：VisionCal公开数据 https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html；RC公式 https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits；通信概念 https://wirelesspi.com/channel-estimation-in-ofdm-systems/；数据中心能效概念 https://www.energy.gov/cmei/femp/energy-efficiency-data-centers。项目数值不来自这些资料，全部由本项目代码产生。','', '## 后续深度不是盲目堆项目','', '各README已有本人能执行的独立修改问题。先重跑、讲清一个失败、做一处有证据的修改再填写个人贡献；不把本批AI辅助代码包装成过去论文/实习/工作成果。真实LLM仍未调用，未授权外发内部数据。GitHub新版尚未核验发布。']
(ROOT/'docs/cross-disciplinary-evidence.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote frozen cross-disciplinary evidence guide')
