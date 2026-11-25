"""Physics, communications and time-series identification investigations."""
from .common import *

def circuit():
 folder='circuit-id';p=PROJECTS/folder;protocol={'kind':'finite_observation_identifiability','time_horizons_ms':[1,3,10],'taus_ms':[.5,2,6,12],'noise':[0,.02,.08],'samples_per_cell':12,'profile_grid':100,'profile_set':'MSE <= minimum + noise_variance; heuristic not confidence interval','seed':196001};freeze(folder,protocol)
 rng=np.random.default_rng(196001);rows=[];metrics=[]
 for horizon in [1,3,10]:
  timegrid=np.linspace(0,horizon,32);grid=np.geomspace(.1,30,100)
  for tau in [.5,2,6,12]:
   for noise in [0,.02,.08]:
    fits=[];widths=[];conds=[]
    for i in range(12):
     gain=rng.uniform(.5,1.5);offset=rng.uniform(-.2,.2);y=gain*(1-np.exp(-timegrid/tau))+offset+rng.normal(0,noise,32);loss=[];condition=[]
     for t in grid:
      design=np.column_stack([1-np.exp(-timegrid/t),np.ones(32)]);theta=np.linalg.lstsq(design,y,rcond=None)[0];loss.append(float(np.mean((design@theta-y)**2)));condition.append(float(np.linalg.cond(design)))
     best=int(np.argmin(loss));admitted=grid[np.array(loss)<=min(loss)+max(noise**2,1e-8)];fit=float(grid[best]);width=float(admitted[-1]-admitted[0]);fits.append(abs(fit-tau));widths.append(width);conds.append(condition[best]);rows.append(dict(horizon_ms=horizon,tau_ms=tau,noise=noise,index=i,gain=gain,offset=offset,fit_tau_ms=fit,absolute_error=abs(fit-tau),profile_width_ms=width,condition_number=condition[best],profile_tau_ms=grid.tolist(),profile_mse=loss))
    metrics.append(dict(horizon_ms=horizon,tau_ms=tau,noise=noise,n=12,mae_ms=float(np.mean(fits)),mean_profile_width_ms=float(np.mean(widths)),mean_design_condition=float(np.mean(conds))))
 return save(folder,'CircuitID · 观察窗与参数可辨识性','观察窗短于时间常数时，低残差为何仍可能给出不可靠RC参数？',rows,metrics,['真实运行变量投影profile grid，gain/offset每个候选tau重拟合。','profile范围是噪声MSE启发式，不是校准置信区间或电气容差。','tau=RC不能分别辨识R/C；只有模拟阶跃，无设备实测。'],protocol,files=[Path(__file__),p/'depth.py'])

def channel():
 folder='channel-est';p=PROJECTS/folder;protocol={'kind':'pilot_geometry_vs_model_order','actual_taps':[2,4,8],'assumed_taps':4,'snr_db':20,'n_per_group':120,'pilot_indices':{'spread':[0,8,16,24],'clustered':[0,4,8,12],'full':[0,4,8,12,16,20,24,28]},'seed':197001,'baselines':['4tap_ls','ridge_regularized_ls']};freeze(folder,protocol)
 rng=np.random.default_rng(197001);rows=[];metrics=[];N=32;F=np.exp(-2j*np.pi*np.arange(N)[:,None]*np.arange(4)[None,:]/N)
 for taps in [2,4,8]:
  pow=np.exp(-np.arange(taps)/2);pow/=pow.sum();h=(rng.normal(size=(120,taps))+1j*rng.normal(size=(120,taps)))*np.sqrt(pow/2);H=np.fft.fft(h,n=N,axis=1)
  for geometry,pilots in protocol['pilot_indices'].items():
   P=np.array(pilots);z=H[:,P]+(rng.normal(size=(120,len(P)))+1j*rng.normal(size=(120,len(P))))*np.sqrt(.01/2);design=F[P]
   for method in protocol['baselines']:
    if method=='4tap_ls':est=np.linalg.lstsq(design,z.T,rcond=None)[0].T@F.T
    else:est=np.linalg.solve(design.conj().T@design+.01*np.eye(4),design.conj().T@z.T).T@F.T
    nmse=np.sum(abs(est-H)**2,1)/np.sum(abs(H)**2,1);metrics.append(dict(actual_taps=taps,geometry=geometry,method=method,n=120,observations=len(P),rank=int(np.linalg.matrix_rank(design)),condition_number=float(np.linalg.cond(design)),mean_nmse=float(nmse.mean()),p95_nmse=float(np.quantile(nmse,.95))))
    rows+= [dict(actual_taps=taps,geometry=geometry,method=method,id=i,nmse=float(nmse[i])) for i in range(120)]
 return save(folder,'ChannelEst · 导频几何与错误模型阶数','观测数量够了是否就可可靠估计？导频几何和错误四径假设带来什么风险？',rows,metrics,['秩、condition number与NMSE一起报告，观测数量不等于可辨识质量。','ridge正则固定0.01与已知噪声，未在测试选参数；8tap是模型阶数失配。','理想频域仿真，无射频硬件/5G6G指标或现场性能。'],protocol,files=[Path(__file__),p/'depth.py'])

def power():
 folder='power-scope';p=PROJECTS/folder;protocol={'kind':'prequential_residual_recalibration','history':288,'alpha':.1,'evaluation':'old chronological/cooling OOD forecasts','update_order':'predict interval using past residuals, then observe current residual','no_retraining':True};freeze(folder,protocol)
 old=load(p/'artifacts/results.json');m=load(p/'artifacts/model.json');rows=[];metrics=[]
 for group in ['chronological_test','cooling_drift_ood']:
  rr=sorted([r for r in old['predictions'] if r['group']==group and r['model']=='ridge_full'],key=lambda r:r['time_index']);history=[];coverage={n:[] for n in ['fixed','past_residual_quantile']};widths={n:[] for n in coverage};errors=[]
  for i,r in enumerate(rr):
   err=abs(r['forecast_kw']-r['actual_kw']);q=float(np.quantile(history[-288:],.9)) if len(history)>=32 else m['interval_abs_kw']
   for method,radius in [('fixed',m['interval_abs_kw']),('past_residual_quantile',q)]:
    covered=err<=radius;coverage[method].append(covered);widths[method].append(2*radius);rows.append(dict(condition=group,method=method,time_index=r['time_index'],history_count=min(len(history),288),radius_kw=float(radius),error_kw=float(err),covered=bool(covered)))
   history.append(err);errors.append(err)
  for method in coverage:metrics.append(dict(condition=group,method=method,n=len(rr),coverage=float(np.mean(coverage[method])),mean_width_kw=float(np.mean(widths[method])),mae_kw=float(np.mean(errors)),p95_absolute_error_kw=float(np.quantile(errors,.95))))
 return save(folder,'PowerScope · 严格先预测后更新的区间运营','只用过去误差在线更新区间，冷却漂移下能否恢复覆盖，而代价多大？',rows,metrics,['每个时点区间先由过去残差确定，当前真值仅在预测后更新。','更新仅区间宽度，预测点及MAE不变；不能当作解决了负荷漂移。','时序依赖/非平稳下无IID conformal覆盖保证，warm-start样本数公开。'],protocol,files=[Path(__file__),p/'artifacts/results.json',p/'artifacts/model.json'])
