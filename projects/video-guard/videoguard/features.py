"""Signal-derived metrics only. No semantic/identity/safety classifier is claimed."""
import numpy as np
from .data import LAGS


def positive_diff(x):
    return np.maximum(0, np.diff(x, prepend=x[0]))


def normalize(x):
    x = np.asarray(x, dtype=float)
    std = x.std()
    return (x-x.mean())/(std+1e-8)


def extract(frames, audio, fps, sample_rate):
    if not np.isfinite(frames).all() or not np.isfinite(audio).all():
        raise ValueError('non-finite media')
    if frames.ndim != 4 or frames.shape[-1] != 3 or len(frames) < 24:
        raise ValueError('need >=24 RGB frames')
    if fps <= 0 or sample_rate <= 0 or audio.ndim != 1:
        raise ValueError('invalid rates or audio shape')
    lum = frames.mean(axis=-1)
    # Brightest quartile is a transparent approximation of flashing pad activity.
    visual = np.quantile(lum, .88, axis=(1, 2))
    global_lum = lum.mean(axis=(1, 2))
    n = len(frames)
    bounds = np.rint(np.arange(n+1)*sample_rate/fps).astype(int)
    if bounds[-1] > len(audio):
        raise ValueError('audio shorter than frame duration')
    rms = np.array([np.sqrt(np.mean(audio[bounds[i]:bounds[i+1]]**2)) for i in range(n)])
    return {'visual':visual.tolist(), 'audio':rms.tolist(),
            'visual_onset':positive_diff(visual).tolist(), 'audio_onset':positive_diff(rms).tolist(),
            'global':global_lum.tolist()}


def overlap(v, a, lag):
    if lag >= 0:
        return v[:len(v)-lag or None], a[lag:]
    return v[-lag:], a[:len(a)+lag]


def corr(v, a):
    v, a = normalize(v), normalize(a)
    return float(np.mean(v*a))


def lag_features(signals):
    v = normalize(signals['visual'])
    a = normalize(signals['audio'])
    vo = normalize(signals['visual_onset'])
    ao = normalize(signals['audio_onset'])
    features=[]
    for lag in LAGS:
        x,y=overlap(v,a,int(lag));u,w=overlap(vo,ao,int(lag))
        # Windows use observed order; labels, seed, events, clean references excluded.
        blocks = np.array_split(np.arange(len(x)), 4)
        cs = np.array([corr(x[b],y[b]) for b in blocks])
        os = np.array([corr(u[b],w[b]) for b in blocks])
        features.append([corr(x,y),corr(u,w),float(np.mean(np.abs(x-y))),
                         float(np.mean(np.abs(u-w))),float(np.min(cs)),float(np.std(cs)),
                         float(np.max(cs)),float(np.min(os)),float(np.std(os)),
                         float(np.mean(x*y*u*w)),float(np.mean(np.minimum(np.maximum(u,0),np.maximum(w,0)))),
                         float(np.mean(np.maximum(u,0)*np.maximum(w,0)))])
    return np.asarray(features)


def baseline(signals, onset=False):
    v=signals['visual_onset' if onset else 'visual']
    a=signals['audio_onset' if onset else 'audio']
    scores=[corr(*overlap(np.asarray(v),np.asarray(a),int(k))) for k in LAGS]
    return int(LAGS[np.argmax(scores)])


def signal_quality(signals):
    vo=np.asarray(signals['visual_onset']);ao=np.asarray(signals['audio_onset'])
    energy = min(float(vo.std()),float(ao.std()))
    return {'evidence_energy':energy, 'scorable':energy > .008,
            'visual_activity':float(vo.std()),'audio_activity':float(ao.std())}


def windows(signals, size=32, stride=16):
    n=len(signals['visual'])
    return [(i,{k:v[i:i+size] for k,v in signals.items()}) for i in range(0,n-size+1,stride)]
