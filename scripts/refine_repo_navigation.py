"""One-time scoped navigation cleanup for README/docs. Does not edit evidence files."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PREFIX='https://llewynlune.github.io/ai-portfolio/'
START='<!-- project-navigation:start -->';END='<!-- project-navigation:end -->'
def update(path):
 s=path.read_text()
 # Only HTML demonstration links: retain relative code, reports, citations and hashes.
 def target(m):
  text,url=m[1],m[2]
  if '://' in url or not url.split('#')[0].endswith('.html'):return m[0]
  rel=(path.parent/url.split('#')[0]).resolve().relative_to(ROOT).as_posix()
  return '['+text+']('+PREFIX+rel+('#'+url.split('#',1)[1] if '#' in url else '')+')'
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',target,s)
 if path.parent.parent.name=='projects' and path.name=='README.md':
  name=path.parent.name
  if START in s:s=s.split(START,1)[0]+s.split(END,1)[1]
  block=START+'\n[Project Page]('+PREFIX+'projects/'+name+'/project.html) · [运行 Demo]('+PREFIX+'projects/'+name+'/demo.html) · [深化分析]('+PREFIX+'projects/'+name+'/depth-demo.html) · [作品集]('+PREFIX+'index.html#experiments)\n'+END
  lines=s.splitlines();lines.insert(1,'\n'+block+'\n');s='\n'.join(lines).rstrip()+'\n'
 path.write_text(s)
if __name__=='__main__':
 paths=list(ROOT.glob('projects/*/README.md'))+[ROOT/'docs/project-depth.md']
 for p in paths:update(p);print('Refined navigation',p.relative_to(ROOT))
