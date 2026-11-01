import importlib.util
from pathlib import Path
import sys,json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('n-gram-language-models')

a=m.NGramLanguageModel(2,k=1).fit(['a b','a a'])
print(json.dumps(dict(training=['a b','a a'],tokens=a.tokens_,start_probabilities=a.distribution(['<BOS>']).tolist(),query='a b',log_probability=a.log_probability('a b'),perplexity=a.perplexity('a b'),generated=a.generate(max_tokens=8,random_state=7))))
