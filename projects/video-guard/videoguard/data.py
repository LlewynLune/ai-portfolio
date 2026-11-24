"""Self-owned percussion/flash fixtures. No people, private video, or model API.
Delay sign: positive means audio occurs AFTER the corresponding visible flash.
Labels and clean signals are kept out of the estimator input.
"""
from dataclasses import dataclass
import hashlib
import numpy as np

FPS = 20
SR = 8000
LAGS = np.arange(-6, 7)

@dataclass
class Clip:
    frames: np.ndarray
    audio: np.ndarray
    fps: int
    sample_rate: int
    delay: int
    seed: int
    condition: str
    events: np.ndarray


def shift(x, amount):
    out = np.zeros_like(x)
    if amount == 0:
        return x.copy()
    if abs(amount) >= len(x):
        return out
    if amount > 0:
        out[amount:] = x[:-amount]
    else:
        out[:amount] = x[-amount:]
    return out


def make_clip(seed, delay=None, condition='id', length=64):
    if condition not in {'id', 'noise', 'periodic', 'silent', 'distractor', 'drift', 'missing', 'long'}:
        raise ValueError('unknown condition')
    rng = np.random.default_rng(seed)
    delay = int(rng.choice(LAGS)) if delay is None else int(delay)
    if condition == 'long':
        length = 128
    events = np.zeros(length)
    if condition == 'periodic':
        events[8:length-8:6] = .9
    elif condition != 'silent':
        count = int(rng.integers(5, 10))
        available = np.arange(8, length-8)
        for _ in range(count):
            if len(available) == 0:
                break
            idx = int(rng.choice(available))
            events[idx] = rng.uniform(.55, 1.)
            available = available[np.abs(available-idx) > 3]
    # Independent but related impulse responses: visual flash and acoustic decay.
    visual = np.convolve(events, [1., .35, .10], mode='full')[:length]
    acoustic = shift(np.convolve(events, [1., .52, .18, .05], mode='full')[:length], delay)
    # Development revision 2: nuisance processes sampled independently of labels.
    # Competing off-screen sound, echoes and exposure pulses make inference nontrivial.
    nuisance = np.zeros(length)
    nuisance[rng.choice(np.arange(5,length-5),int(rng.integers(3,10)),replace=False)] = rng.uniform(.3,1.,int(1))
    strength = rng.uniform(.0, .9 if condition == 'id' else 1.3)
    acoustic = acoustic + strength*np.convolve(nuisance,[1.,.4,.12],mode='full')[:length]
    echo = int(rng.integers(2,6))
    acoustic += rng.uniform(0,.65)*shift(acoustic,echo)
    if condition == 'periodic':
        # A second periodic source makes a uniquely attributable delay unidentifiable.
        acoustic += .85*shift(np.convolve(events,[1.,.5,.15],mode='full')[:length],delay+6)
    exposure = np.zeros(length)
    exposure[rng.choice(np.arange(6,length-6),int(rng.integers(1,6)),replace=False)] = rng.uniform(0,.22)
    if condition == 'drift':
        acoustic[length//2:] = shift(acoustic, 4)[length//2:]
    if condition == 'missing':
        acoustic[length//3:2*length//3] = 0
    background = rng.uniform(.06, .20)
    frames = np.full((length, 32, 32, 3), background, dtype=np.float32)
    yy, xx = np.mgrid[:32, :32]
    frames += (xx[None,:,:,None]/32)*.03
    pad_color = rng.uniform(.5, 1., 3)
    for t in range(length):
        # Fixed percussion pad with flash; not an oracle segmentation annotation.
        frames[t, 10:23, 8:24] += visual[t]*pad_color*.65
        x = 3 + int(25*(.5+.4*np.sin(t*.17)))
        frames[t, 3:6, x:x+3] = [.2, .5, .7]
    frames += exposure[:,None,None,None]
    if condition == 'distractor':
        # Moving exposure unrelated to audio; deliberate feature-extractor failure.
        frames += (.25*np.sin(np.arange(length)*.73))[:,None,None,None]
    vnoise = .018 if condition != 'noise' else .10
    frames += rng.normal(0, vnoise, frames.shape).astype(np.float32)
    frames = np.clip(frames, 0, 1)
    n = SR // FPS
    phase = np.arange(n)/SR
    tone = np.sin(2*np.pi*rng.uniform(400, 1100)*phase)
    # Per-frame burst energy; independent gain and ambient noise.
    carrier = .7*tone + .3*rng.normal(0, 1, n)
    audio = (acoustic[:,None]*carrier[None,:]*rng.uniform(.35, .8)).reshape(-1)
    anoise = rng.uniform(.002, .015) if condition != 'noise' else .1
    audio += rng.normal(0, anoise, len(audio))
    if condition == 'silent':
        audio[:] = 0
    return Clip(frames, audio.astype(np.float32), FPS, SR, delay, seed, condition, events)


def content_hash(clip):
    h = hashlib.sha256()
    h.update(clip.frames.astype('<f4').tobytes())
    h.update(clip.audio.astype('<f4').tobytes())
    return h.hexdigest()
