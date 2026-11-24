"""Encode a self-owned synthetic fixture, decode it, verify adapter pipeline.
Does NOT measure real-world generalization; MP4 produced by this fixture script.
"""
import tempfile,subprocess,json,hashlib
from pathlib import Path
import numpy as np
from videoguard.data import make_clip
from videoguard.media import decode,assess
from videoguard.features import extract
from videoguard.experiment import ROOT,write_json


def run():
    c=make_clip(250001,delay=3);out=ROOT/'artifacts'
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);v=d/'frames.rgb';a=d/'audio.f32'
        v.write_bytes((c.frames*255).astype(np.uint8).tobytes());a.write_bytes(c.audio.astype('<f4').tobytes())
        path=d/'synthetic.mp4'
        subprocess.run(['ffmpeg','-v','error','-nostdin','-f','rawvideo','-pixel_format','rgb24','-video_size','32x32','-framerate','20','-i',str(v),'-f','f32le','-ar','8000','-ac','1','-i',str(a),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(path)],check=True,capture_output=True,timeout=60)
        f,au,meta=decode(path);s=extract(f,au,20,8000);m=json.loads((out/'model.json').read_text());r=assess(s,m)
        assert len(f)>=60 and np.isfinite(au).all()
        write_json(out/'media-smoke.json',{'fixture_seed':250001,'true_synthetic_delay_ms':150,'metadata':meta,
                   'encoded_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'diagnosis':r,
                   'note':'Self-generated MP4 transcoding smoke only; no natural-media accuracy claim.'})
        # Store only signal report, no large video bundle; source fixture is reproducible.
        write_json(out/'local-report-example.json',{'metadata':meta,**r,'signals':s,'requires_human_review':True,'decision':'review','distribution_status':'decoded synthetic smoke; no real-world calibration'})
    print('Synthetic MP4 encode/decode/analysis smoke passed')

if __name__=='__main__':run()
