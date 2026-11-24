"""Self-owned, annotated piecewise-delay RGB/PCM fixtures for change localization.
Ground truth is the structural output-time delay boundary, not an observed action.
Silence around a boundary intentionally makes its exact time unidentifiable.
"""
from dataclasses import dataclass
import numpy as np
from .data import FPS,SR,content_hash,Clip

@dataclass
class DriftFixture:
    clip: Clip
    change_frames: list
    delay_track: np.ndarray
    source_events: np.ndarray
    condition: str


def make_drift(seed,condition='step',length=160):
    allowed={'stable','step','negative','small_step','ramp','multiple','quiet_gap','noise','exposure','silent'}
    if condition not in allowed:raise ValueError('unknown drift condition')
    if length<120:raise ValueError('fixture needs >=120 frames')
    rng=np.random.default_rng(seed);cp=int(rng.integers(60,length-55));base=int(rng.integers(-3,2));jump=int(rng.integers(2,5));changes=[]
    track=np.full(length,base,dtype=int)
    if condition not in ['stable','silent']:
        if condition=='negative':jump=-jump;base=int(rng.integers(0,4));track[:]=base
        if condition=='small_step':jump=1
        if condition=='ramp':
            end=cp+24;track[cp:end]=base+np.rint(np.linspace(0,jump,end-cp)).astype(int);track[end:]=base+jump
            # Actual integer substeps, not a fake single-point annotation for a ramp.
            changes=(np.flatnonzero(np.diff(track)!=0)+1).tolist()
        elif condition=='multiple':
            cp=50;track[cp:]=base+jump;track[105:]=base;changes=[cp,105]
        else:track[cp:]=base+jump;changes=[cp]
    events=np.zeros(length);available=0
    for i in range(8,length-8):
        if i>=available and rng.random()<.23:
            events[i]=rng.uniform(.6,1);available=i+int(rng.integers(4,7))
    if condition=='quiet_gap':events[max(0,cp-22):cp+25]=0
    if condition=='silent':events[:]=0
    visual=np.convolve(events,[1,.35,.1],mode='full')[:length]
    source=np.convolve(events,[1,.52,.18,.05],mode='full')[:length]
    nuisance=np.zeros(length);indices=rng.choice(np.arange(7,length-7),8,replace=False);nuisance[indices]=rng.uniform(.2,.6,8)
    source+=rng.uniform(0,.35)*np.convolve(nuisance,[1,.4,.12],mode='full')[:length]
    idx=np.arange(length)-track;audio_env=np.where((idx>=0)&(idx<length),source[np.clip(idx,0,length-1)],0)
    # By construction structural boundaries are at OUTPUT frames; no labels in inputs.
    frames=np.full((length,32,32,3),rng.uniform(.06,.18),dtype=np.float32)
    for t in range(length):
        frames[t,10:23,8:24]+=visual[t]*np.array([.6,.8,.7])*.65
        x=3+int(24*(.5+.45*np.sin(t*.17)));frames[t,3:6,x:x+3]=[.2,.5,.7]
    if condition=='exposure':frames+=(.2*np.sin(np.arange(length)*.63))[:,None,None,None]
    frames+=rng.normal(0,.08 if condition=='noise' else .018,frames.shape).astype(np.float32);frames=np.clip(frames,0,1)
    n=SR//FPS;phase=np.arange(n)/SR;carrier=.7*np.sin(2*np.pi*rng.uniform(400,1100)*phase)+.3*rng.normal(0,1,n)
    audio=(audio_env[:,None]*carrier[None,:]*rng.uniform(.35,.8)).reshape(-1)
    audio+=rng.normal(0,.1 if condition=='noise' else .008,len(audio))
    if condition=='silent':audio[:]=0
    c=Clip(frames,audio.astype(np.float32),FPS,SR,base,seed,condition,events)
    return DriftFixture(c,changes,track,events,condition)
