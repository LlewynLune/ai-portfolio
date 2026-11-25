"""Offline MLX adapter. Loading only a pre-downloaded safetensors directory.
No credential discovery, HTTP server, tool execution, or trust_remote_code.
"""
import hashlib,time
from pathlib import Path
MODEL_ID='mlx-community/Qwen3-4B-Instruct-2507-4bit'
REVISION='50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b'
class LocalModel:
 def __init__(self,path):
  from mlx_lm import load
  path=Path(path).resolve()
  if not path.is_dir() or not (path/'model.safetensors').is_file():raise ValueError('downloaded safetensors model directory required')
  self.path=path;start=time.perf_counter()
  self.model,self.tokenizer=load(str(path),tokenizer_config={'trust_remote_code':False,'local_files_only':True})
  self.load_seconds=time.perf_counter()-start;self.calls=0
 def count(self,text):return len(self.tokenizer.encode(text))
 def call(self,system,user,max_tokens=256):
  from mlx_lm import stream_generate
  from mlx_lm.sample_utils import make_sampler
  import mlx.core as mx
  if not 1<=max_tokens<=1024:raise ValueError('bounded output required')
  prompt=self.tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
  if self.count(prompt)>8192:raise ValueError('prompt exceeds local experiment cap')
  mx.reset_peak_memory();start=time.perf_counter();parts=[];last=None;first=None
  for response in stream_generate(self.model,self.tokenizer,prompt,max_tokens=max_tokens,sampler=make_sampler(temp=0)):
   if first is None:first=time.perf_counter()-start
   parts.append(response.text);last=response
  elapsed=time.perf_counter()-start;self.calls+=1
  output=''.join(parts)
  return {'text':output,'llm_used':True,'model':MODEL_ID,'revision':REVISION,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
   'prompt_tokens':self.count(prompt),'completion_tokens':int(last.generation_tokens) if last else 0,'elapsed_seconds':elapsed,'first_token_seconds':first,
   'peak_gpu_memory_bytes':int(mx.get_peak_memory()),'max_tokens':max_tokens,'temperature':0,'finish_reason':getattr(last,'finish_reason',None),'raw_output_sha256':hashlib.sha256(output.encode()).hexdigest()}
