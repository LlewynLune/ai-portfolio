"""Bounded local media adapter: ffprobe metadata + ffmpeg decode, no network.
Caller supplies a LOCAL regular file; maximum 30 s, fixed 20 fps / 96x96.
FFmpeg runs as an ordinary subprocess, not a security sandbox. Untrusted complex
media decoders require OS-level isolation in any deployment, not implemented here.
"""
from pathlib import Path
import json, subprocess
import numpy as np
from .features import extract,lag_features,signal_quality,windows
from .model import predict

ROOT=Path(__file__).resolve().parents[1]


def decode(path):
    path=Path(path).resolve()
    if not path.is_file() or path.stat().st_size>100*1024*1024:
        raise ValueError('need a local regular media file <=100 MiB')
    # Local file allowlist. No URL input, shell expansion, or remote model calls.
    metadata=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe',
                             '-show_format','-show_streams','-of','json',str(path)],
                             check=True,capture_output=True,text=True,timeout=20)
    info=json.loads(metadata.stdout)
    duration=float(info.get('format',{}).get('duration',0))
    if not 1.2<=duration<=30:
        raise ValueError('duration must be 1.2 to 30 seconds')
    types={s['codec_type'] for s in info['streams']}
    if not {'audio','video'}<=types:
        raise ValueError('both audio and video tracks required')
    base=['ffmpeg','-v','error','-nostdin','-protocol_whitelist','file,pipe','-i',str(path),'-t','30']
    v=subprocess.run(base+['-an','-vf','fps=20,scale=96:96','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],
                     check=True,capture_output=True,timeout=60).stdout
    a=subprocess.run(base+['-vn','-ac','1','-ar','8000','-f','f32le','pipe:1'],
                     check=True,capture_output=True,timeout=60).stdout
    frames=np.frombuffer(v,np.uint8).reshape(-1,96,96,3).astype(np.float32)/255
    audio=np.frombuffer(a,dtype='<f4')
    n=min(len(frames),len(audio)//400)
    if n<24:
        raise ValueError('insufficient jointly decodable duration')
    return frames[:n],audio[:n*400],{'duration':duration,'decoded_frames':n,'fps':20,'sample_rate':8000}


def assess(signals,model):
    p=model['parameters'];temp=model['temperature']
    probs=predict(lag_features(signals)[None],p,temp)[0]
    quality=signal_quality(signals);candidate=np.where(probs>=1-model['conformal_q']-1e-12)[0]-6
    segment=[]
    for i,s in windows(signals):
        pr=predict(lag_features(s)[None],p,temp)[0];q=signal_quality(s)
        segment.append({'start_s':i/20,'end_s':(i+32)/20,'delay_ms':int((pr.argmax()-6)*50),
                        'confidence':float(pr.max()),'scorable':q['scorable']})
    confident=quality['scorable'] and probs.max()>=max(.9,model['threshold']) and len(candidate)==1
    delays=[x['delay_ms'] for x in segment if x['scorable'] and x['confidence']>=max(.9,model['threshold'])]
    drift=len(delays)>=2 and max(delays)-min(delays)>=100
    return {'delay_ms':int((probs.argmax()-6)*50),'probabilities':probs.tolist(),
            'confidence':float(probs.max()),'prediction_set_ms':(candidate*50).tolist(),
            'quality':quality,'decision':'review' if not confident or drift else 'estimate_only',
            'window_disagreement':drift,'windows':segment,
            'scope':'flash/percussion synthetic-trained; NOT lipsync, meaning, identity, video quality or safe-to-publish approval'}


def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();frames,audio,meta=decode(args.input)
    s=extract(frames,audio,20,8000);m=json.loads((ROOT/'artifacts/model.json').read_text())
    report={'metadata':meta,**assess(s,m),'signals':s,
            'distribution_status':'unknown real-world distribution; probability calibration NOT transferable',
            'decision':'review','requires_human_review':True}
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('Local report saved; all real media remains OOD / human review required.')

if __name__=='__main__':main()
