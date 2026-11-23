import hashlib
from http.server import ThreadingHTTPServer
import http.client
import json
from pathlib import Path
import re
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'projects/reliability-lab'
sys.path.insert(0,str(LAB))
from reliability_lab.server import Handler

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
    def request(self,path='/',method='GET',body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        try:
            c.request(method,path,body=body,headers=headers or {})
            r=c.getresponse(); return r.status,r.read()
        finally: c.close()
    def test_health(self):
        status,body=self.request('/health')
        self.assertEqual(status,200); self.assertEqual(json.loads(body)['llm_calls'],0)
    def test_no_arbitrary_file_routes(self):
        self.assertEqual(self.request('/../../.git/config')[0],404)
    def test_host_rejected(self):
        self.assertEqual(self.request('/health',headers={'Host':'example.com'})[0],403)
    def test_cross_origin_rejected(self):
        self.assertEqual(self.request('/api/compare','POST','{}',{'Content-Type':'application/json','Origin':'https://other.example'})[0],403)
    def test_bad_config_rejected(self):
        headers={'Content-Type':'application/json','Origin':f'http://127.0.0.1:{self.server.server_port}'}
        self.assertEqual(self.request('/api/compare','POST','{"count":999}',headers)[0],400)
    def test_real_comparison(self):
        headers={'Content-Type':'application/json','Origin':f'http://127.0.0.1:{self.server.server_port}'}
        status,body=self.request('/api/compare','POST','{"count":2,"profile":"clean","base_ms":1}',headers)
        self.assertEqual(status,200)
        data=json.loads(body)
        self.assertEqual(len(data['results']),3)
        self.assertTrue(all(r['summary']['succeeded']==2 for r in data['results']))

class EvidenceTests(unittest.TestCase):
    def test_reference_runtime_code_hashes(self):
        report=json.loads((LAB/'results/reference/benchmark.json').read_text())
        for name,digest in report['code_sha256'].items():
            self.assertEqual(hashlib.sha256((LAB/'reliability_lab'/name).read_bytes()).hexdigest(),digest,name)
    def test_reference_checksums(self):
        folder=LAB/'results/reference'
        checks=json.loads((folder/'checksums.json').read_text())
        for name,digest in checks.items():
            self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest,name)
    def test_paired_manifest_and_recomputed_success(self):
        folder=LAB/'results/reference'
        report=json.loads((folder/'benchmark.json').read_text())
        for group in report['groups']:
            for repeat in range(report['repeats']):
                runs=[r for r in group['runs'] if r['repeat']==repeat]
                self.assertEqual(len({r['manifest_hash'] for r in runs}),1)
                for run in runs:
                    data=json.loads((folder/run['file']).read_text())
                    success=sum(r['status']=='succeeded' for r in data['tasks'])
                    self.assertEqual(data['summary']['succeeded'],success)
                    self.assertEqual(data['summary']['count'],len(data['tasks']))
                    self.assertEqual(data['summary']['attempts'],sum(r['attempts'] for r in data['tasks']))
    def test_embedded_measured_data(self):
        html=(LAB/'demo.html').read_text()
        match=re.search(r'<script id="reference-data" type="application/json">(.*?)</script>',html,re.S)
        data=json.loads(match[1]); self.assertEqual(len(data['results']),24)
        self.assertTrue(all(r['workload']=='synthetic_async_io_no_llm' for r in data['results']))

if __name__ == '__main__': unittest.main()
