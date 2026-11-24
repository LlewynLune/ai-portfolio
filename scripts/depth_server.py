"""Read-only localhost API for depth evidence. No credentials, remote calls, file writes or model training."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
import json,argparse
PROJECTS={'textguard','cite-rag','novelty-lab','vision-cal','circuit-id','channel-est','power-scope','tiny-attention','lora-lab','dpo-lab','moe-lab','spec-decode','video-guard','reliability-lab'}
ROOT=Path(__file__).resolve().parents[1]
def query(project,condition=None,model=None,offset=0,limit=50):
    if project not in PROJECTS:raise ValueError('unknown project')
    if not 0<=offset or not 1<=limit<=200:raise ValueError('offset >=0, limit1..200')
    d=json.loads((ROOT/'projects'/project/'artifacts/depth/results.json').read_text());rows=[r for r in d['records'] if (condition is None or r['condition']==condition) and (model is None or r['model']==model)]
    return dict(project=project,total=len(rows),offset=offset,limit=limit,rows=rows[offset:offset+limit],metrics=[r for r in d['metrics'] if (condition is None or r['condition']==condition) and (model is None or r['model']==model)],source_hashes=d['source_hashes'],scope=d['scope'])
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlsplit(self.path);q=parse_qs(u.query)
        try:
            if u.path=='/health':data={'status':'ok','mode':'read_only_localhost'}
            elif u.path=='/api/projects':data={'projects':sorted(PROJECTS)}
            elif u.path=='/api/evidence':data=query(q.get('project',[''])[0],q.get('condition',[None])[0],q.get('model',[None])[0],int(q.get('offset',['0'])[0]),int(q.get('limit',['50'])[0]))
            else:self.send_error(404);return
            body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode();self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
        except (ValueError,KeyError,FileNotFoundError) as e:
            body=json.dumps({'error':'invalid_request','detail':str(e)}).encode();self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
    def do_POST(self):self.send_error(405,'Read-only API')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8766);a=p.parse_args();ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
