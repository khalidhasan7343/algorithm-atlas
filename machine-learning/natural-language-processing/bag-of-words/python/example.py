import importlib.util
from pathlib import Path
import sys,json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('bag-of-words')

texts=['Cat cat dog','DOG!','']
a=m.BagOfWords().fit(texts)
print(json.dumps(dict(texts=texts,features=a.feature_names_,counts=a.transform(texts).tolist(),query=a.transform(['cat unseen']).tolist())))
