import importlib.util
from pathlib import Path
import sys,json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('cyk-parsing')

rules=[('S',('A','C')),('C',('A','B')),('A',('a',)),('B',('b',))]
p=m.CYKParser('S',rules)
tokens=['a','a','b']
print(json.dumps(dict(start='S',rules=rules,tokens=tokens,recognized=p.recognize(tokens),tree=p.parse(tokens).to_tuple(),chart={str(k):sorted(v) for k,v in p.chart(tokens).items()},unknown=p.recognize(['unknown']))))
