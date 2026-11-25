import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PersonalBackgroundTests(unittest.TestCase):
 def test_ownership_links_in_supplement(self):
  for path in [ROOT/'README.md',ROOT/'profile/README.md',ROOT/'index.html']:
   text=path.read_text();self.assertIn('愤怒的墨镜',text);self.assertIn('小青年广场',text);self.assertIn('https://mp.weixin.qq.com/s/F12ydRzh1u-T2M8EuSPWJg',text);self.assertIn('https://www.xiaoyuzhoufm.com/podcast/615ffb31ef56f237f8e18917',text)
  home=(ROOT/'index.html').read_text();self.assertEqual(home.count('data-track="'),15);self.assertEqual(home.count('class="experience-project work-row"'),4);self.assertIn('id="more"',home)
 def test_full_original_text_and_metadata(self):
  p=ROOT/'profile/writing';text=(p/'verification-layer.md').read_text();self.assertGreater(len(text),12000)
  for section in range(1,10):self.assertIn('## '+str(section).zfill(2),text)
  self.assertIn('过去一年，AI 应用的合同的写法',text);self.assertIn('我的答案是，至少不该只有 10 倍。',text);self.assertIn('现在现在',text)
  data=json.loads((p/'sources.json').read_text());self.assertEqual(data['article']['sha256'],hashlib.sha256((p/'verification-layer.md').read_bytes()).hexdigest());self.assertTrue((p/'verification-layer.html').is_file())
if __name__=='__main__':unittest.main()
