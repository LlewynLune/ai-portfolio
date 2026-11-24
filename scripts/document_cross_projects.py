"""Generate project-specific methodological documentation from actual results."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS={
'vision-cal':{
'name':'VisionCal｜小型神经网络校准与鲁棒性',
'domain':'AI算法 / 视觉分类 / 概率校准',
'question':'网络准确率更高时，置信度是否更可信？验证集选择的温度能否迁移到噪声和平移数据？',
'architecture':'公开8×8灰度样本 → 固定训练/验证/测试 → 64输入/48 ReLU隐藏/10类别MLP → 验证温度搜索 → 清洁/噪声/平移对照 → 高置信度错误分析 → JSON参数与浏览器推断。',
'source':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html',
'method':r'''## 从算法到实验

输入是64维0–1像素，固定除以16，不估计测试统计量。单隐藏层 MLP 使用 sklearn 实际训练，不把库的反向传播包装成自己编写的框架。线性 Logistic 为同数据分集基线；不同模型超参数预先固定，没有统一超参数竞赛。

神经网络为 $a=\operatorname{ReLU}(xW_1+b_1)$，$z=aW_2+b_2$。温度缩放 $p_k=\exp(z_k/T)/\sum_j\exp(z_j/T)$。正温度不改变argmax，因此准确率不应该被“校准提升”修改；若准确率变化说明实现错误。

### 分集与校准

1797个样本固定stratified60/20/20；仅训练集拟合分类权重，验证集搜索0.5–3的51个温度，最小化NLL。训练停止使用训练损失，没有读取外部测试。参数/训练轮数/loss_curve留在结果；达到max_iter不等于收敛，不能隐瞒优化警告。

### 评测问题

1. 清洁留出：Accuracy、NLL、10-bin ECE。
2. 固定高置信阈值0.9：Coverage与Selective Error分别报告，不能以拒答多来冒充精度高。
3. 与同一批留出ID配对的高斯噪声、右移1像素：标签不变，但分布变化。右移零填充而不是环形移位。
4. 对三个模型raw/temperature/linear全部报告，不删除温度选择失败。

ECE按10个等宽置信区间加权计算，不同分箱可得到不同值。验证最优温度并不保证测试NLL或ECE变好；尤其分布迁移时可能更自信、更错误。项目因此着重“可检验的可信度”，而非只展示干净集高分。

### 贡献边界

Digits不是MNIST，也没有writer分组，随机划分不能证明跨书写者泛化；不是CNN或大型视觉模型。点击编辑像素只是定制输入，没有人工正确标签。概率非安全级判断，不部署到身份识别、支付或关键决策。
''',
'next':'本人可新增一个只在验证集选择的噪声增强模型，保留本批原始对照；独立实现ECE，解释一个高置信错例。不能在测试上反复调温度后仍称独立留出。'},
'circuit-id':{
'name':'CircuitID｜噪声RC阶跃的学习型系统辨识',
'domain':'电子科学与技术 / 信号处理 / 系统辨识',
'question':'已知输入和采样条件时，学习回归是否优于简单阈值？物理拟合在哪些分布变化下更可靠？',
'architecture':'理想RC阶跃生成 → 随机tau/增益/噪声 → 32点观测 → 63%规则/物理拟合/Ridge/MLP → 验证选型 → 多seed与OOD → 波形重建和残差带。',
'source':'https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits',
'method':r'''## 物理任务而非算法名字

理想归一化输入阶跃下，$v(t)=1-\exp(-t/\tau)$，$\tau=RC$。单个归一化阶跃只能辨识乘积RC；本实验不会输出独立R和C，也不把tau称为元件寿命或故障概率。

固定0–10ms共32采样点。训练/验证tau0.5–3ms，增益0.98–1.02，独立高斯噪声幅度0.005–0.025。生成器解析公式是模型假设，不是测量数据。所有测试seed不与训练验证重合，同seed各方法共享同一波形。

### 四个对照

- 63%穿越规则：第一次超过 $1-e^{-1}$ 的采样时刻；采样离散会偏差。
- 物理曲线拟合：最小化单位指数响应误差，在logtau区间0.1–12ms求解。已知函数族且搜索范围更宽，不是完全同条件学习对照。
- Ridge：标准化只fit训练，学习logtau，alpha仅验证从0.1/1/10选择。
- MLP：32→48 tanh→1，训练logtau；对比非线性模型不自动代表更强。

只比较两类学习模型的验证MAE，确定默认模型；物理法始终在完整测试表展示。学习输出经过exp还原，确保正tau。浏览器按导出参数推断，不依赖后端或预设答案。

### 泛化与不确定性

训练1800，验证400；4个组×3seed×160测试：同分布、强噪声、+0.10固定偏置、慢tau4–6ms。报告MAE、RMSE、绝对误差95分位；各seed不只报一个漂亮结果。每组保留最坏示例，说明采样/范围/模型假设如何失败。

残差带从验证绝对误差有限样本90%分位计算，仅作为经验区间。分布外偏置/慢响应不满足相同条件，实际覆盖率可接近0；不称“90%可靠”或元件验收公差。

### 工程边界

没有SPICE、PCB、示波器、真实ADC/寄生参数/温漂/量化模型；不是电路设计签核。32点采样已假设对齐，缺失采样和输入幅值误差未解决。项目只在离线低压归一化数学仿真中学习，不接触实际设备或高压电气操作。
''',
'next':'本人可在新版本加入未知增益/偏置联合物理拟合，公平比较；或用授权低压台架测量集独立验证，但必须保留硬件条件、校准和测量权限，不替换本批仿真结果。'},
'channel-est':{
'name':'ChannelEst｜导频驱动的学习型信道估计',
'domain':'信息与通信工程 / 数字信号处理 / 通信AI',
'question':'从稀疏导频学出的线性映射是否能降低信道误差及误码？与拥有信道先验的LMMSE相比差在哪里？',
'architecture':'Rayleigh多径仿真 → 32频点/8单位导频/24 QPSK数据 → 复AWGN → 导频特征 → 插值/学习Ridge/先验LMMSE/真CSI → 固定均衡 → NMSE与BER。',
'source':'https://wirelesspi.com/channel-estimation-in-ofdm-systems/',
'method':r'''## 理想链路定义

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
''',
'next':'本人可新建不同导频间隔或错误噪声先验的消融，重新生成独立实验；再补时域IFFT/CP等模块时必须验证频域等效性，不能把本批改名为完整射频链路。'},
'power-scope':{
'name':'PowerScope｜AI数据中心电力负荷的离线预测与漂移',
'domain':'AI数据中心 / 电气工程 / 时序机器学习',
'question':'下一5分钟电力需求能否利用作业计划更好预测？突变与冷却漂移会不会使经验区间失效？',
'architecture':'合成作业计划/室外温度 → 透明IT/冷却/损耗模型 → 当前及历史特征 → 时间留出Ridge/持久性/季节基线 → 计划特征消融 → 峰值标记和漂移分析 → 只读Dashboard。',
'source':'https://www.energy.gov/cmei/femp/energy-efficiency-data-centers',
'method':r'''## 数据的真实边界

本项目完全是作者仿真，没有字节机房遥测或公开真实AI机房数据。36天、5分钟粒度，日周期与随机批作业形成IT功率；冷却/损耗系数是源码明确的玩具假设，不能作为供应商设备曲线、工程额定或节能依据。

IT计划来自生成器作业schedule，加35kW噪声；使用下一时段计划而不是下一时段实测功率。仿真假设计划可提前知道，因此比完全不可知突变拥有额外信息；真实scheduler误差和延迟未验证。必须对“无计划”模型消融，否则优势来源不清楚。

### 时间因果协议

第1天用作lag288预热，前20天训练、后6天验证、最后10天测试。输入当前/滞后1/12/288时段总功率、当前IT、当前温度、时钟sin/cos与下一期计划IT。目标是下一步总功率，删掉跨训练/验证边界的目标行，不把未来目标引入fit。lag可使用已观测过去值，测试采用滚动一步预测，不是10天开放式多步预测。

StandardScaler只fit训练；Ridge alpha按验证MAE选。时间序列禁止随机打散Kfold。新增冷却漂移OOD是独立seed10天序列，冷却功率变为额外线性项+高温阶跃，不重新fit。

### 模型和结果

- Persistence：下一期等于当前值，强短期基线。
- 同日时刻lag288：当天同一时刻代替未来，验证作业随机性影响。
- Ridge_no_plan：移除计划特征，固定alpha10。
- Ridge_full：完整9维，预先规定其作为部署展示模型，即使验证MAE或测试MAE未胜出也不偷偷换口径。

MAE、RMSE、绝对误差95分位不等价：计划可降低突变的大误差，但平稳时引入噪声，提高MAE。必须分别解释，不能挑一个“提升率”。

验证残差90%经验带与玩具1200kW阈值只做离线标记，报告TP/FP/FN。不保证90%覆盖：时序相关破坏exchangeability，漂移会显著失效。其他模型共享该残差带仅作为统一flag规则，不代表各自校准区间。

### 电气工程底线

仅区间平均kW，不评估毫秒级电力暂态、电能质量、谐波、短路、保护配合、N+1/2N冗余、UPS/autonomy、切换控制或额定容量。窗口能量按5分钟求和折算kWh；同窗口facility/IT比值不是审计的年度PUE。不给真实控制指令，不输出设备设定值或投运建议。没有实测降本收益，也没有模型自动闭环。
''',
'next':'本人可用有权限的脱敏遥测另建独立数据版本（先确认可以公开），引入计划预测误差/数据缺失/多步预测；实际控制和工程验收需专业安全流程，不能由作品集模型直接执行。'}
}

def main():
 for p,d in DOCS.items():
  folder=ROOT/'projects'/p;r=json.loads((folder/'artifacts/results.json').read_text());m=json.loads((folder/'artifacts/model.json').read_text())
  (folder/'README.md').write_text(f"# {d['name']}\n\n状态：核心真实训练/数值评测与本地模型推断已完成；AI辅助研究原型，不是生产项目或过往本人独立履历。\n\n**方向：{d['domain']}**\n\n## 值得追问的问题\n\n{d['question']}\n\n## 完整入口\n\n[交互Demo](demo.html) · [方法与评测](METHOD.md) · [模型卡](MODEL_CARD.md) · [全部实测](artifacts/REPORT.md) · [逐条结果](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)\n\n## 实现结构\n\n{d['architecture']}\n\n## 复现\n\n仓库根目录先按 requirements-ml.txt 建立隔离环境。\n\n```bash\n.venv/bin/python projects/{p}/train.py\npython3 scripts/build_cross_demos.py\n.venv/bin/python -m unittest discover -s tests -p test_cross_projects.py -v\n```\n\n第一次批量重建页面需全部四个结果文件存在。直接双击demo.html即可推断；不连接设备，不上传输入，不需要密钥。训练代码与共享数值函数都在仓库内。\n\n## 下一步本人可完成的深度贡献\n\n{d['next']}\n\n## 参考与归属\n\n概念/数据参考：{d['source']}。本实验结果只由本仓库代码产生，不是参考材料作者的结果。用户选方向；代码、实验、文档与展示由AI辅助完成，本人亲自修改/复核贡献待记录。没有虚构作者、论文、实习身份或上线指标。\n",encoding='utf-8')
  (folder/'METHOD.md').write_text('# '+d['name']+'｜原理、对照与失败\n\n'+d['method']+'\n## 本批原始证据\n\n'+r['protocol']+'\n\n[完整表](artifacts/REPORT.md)保留所有组与seed；[JSON](artifacts/results.json)保留逐项预测、样本与运行环境。SHA校验只能发现变更，不是第三方签名。重新修改train.py或共享生成器后必须重跑，不得把旧结果重新打hash当新证据。\n\n来源：'+d['source']+'\n',encoding='utf-8')
  (folder/'MODEL_CARD.md').write_text('# '+d['name']+'｜模型卡\n\n## 模型与预期用途\n\n'+d['architecture']+'\n\n默认导出类型：'+m['kind']+'；输入维数'+str(len(m['mean']))+'。仅离线学习、参数推断、复现与失败分析。\n\n## 数据、训练与测试\n\n'+r['protocol']+'\n\n[实际指标](artifacts/REPORT.md)不是生产指标，也没有第三方审计。训练环境记录在[结果](artifacts/results.json)中，代码和数据/参数哈希不证明专业资质。\n\n## 禁止外推\n\n'+'\n'.join('- '+l for l in r['limits'])+'\n\n## 人机分工与退出\n\n页面只显示模型输出和假设；缺失输入/维数错误/非有限数拒绝。修改输入后不再显示预设样本标签作为真值。分布外、无真实标签、数据可用性不足时必须人工调查，不把模型倾向写成事实。\n\n## 贡献与许可\n\nAI辅助学习实现，用户提出范围；本人独立贡献尚待亲自修改与验证，不以此冒充已掌握的研究经历。数据/参考许可分别适用，仓库暂未统一授予开源许可证。\n',encoding='utf-8')
 print('Documented four independent projects')
if __name__=='__main__':main()
