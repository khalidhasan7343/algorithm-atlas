import importlib.util, sys, itertools
from pathlib import Path
from fractions import Fraction
import numpy as np
ROOT=Path('.')
B='machine-learning/unsupervised-learning/association-rule-learning/'
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
ap=load(B+'apriori'); ec=load(B+'eclat'); fp=load(B+'fp-growth')
rs=importlib.util.spec_from_file_location('rules',ROOT/B/'rules.py'); rules=importlib.util.module_from_spec(rs); rs.loader.exec_module(rules)
def brute(rows,minsup):
    items=sorted(set().union(*rows)); n=len(rows); out={}
    for k in range(1,len(items)+1):
        for combo in itertools.combinations(items,k):
            c=sum(set(combo)<=r for r in rows)
            if Fraction(c,n)>=Fraction(str(minsup)): out[frozenset(combo)]=c
    return out
rng=np.random.default_rng(66); ok=[True,True,True]; total=0
for trial in range(40):
    n=int(rng.integers(3,25)); m=int(rng.integers(2,7)); dens=rng.uniform(0.2,0.8)
    rows=[set(int(i) for i in np.flatnonzero(rng.random(m)<dens)) for _ in range(n)]
    minsup=float(rng.choice([0.1,0.2,0.25,0.3,0.5,0.6]))
    ref=brute(rows,minsup); total+=1
    for idx,mod in enumerate((ap,ec,fp)):
        got=dict(getattr(mod,['apriori','eclat','fp_growth'][idx])([list(r) for r in rows],minsup))
        if got!=ref: ok[idx]=False; print('mismatch',['apriori','eclat','fp'][idx],trial,len(got),len(ref))
check(f'Apriori == brute force on {total} random DBs',ok[0]); check(f'Eclat == brute force on {total} random DBs',ok[1]); check(f'FP-Growth == brute force on {total} random DBs',ok[2])
# textbook example (Han & Kamber): 9 transactions min_sup 2/9
T=[['I1','I2','I5'],['I2','I4'],['I2','I3'],['I1','I2','I4'],['I1','I3'],['I2','I3'],['I1','I3'],['I1','I2','I3','I5'],['I1','I2','I3']]
res=ap.apriori(T,0.2)
check('Han&Kamber: 13 frequent itemsets, {I1,I2,I3}=2,{I1,I2,I5}=2',len(res)==13 and res[frozenset({'I1','I2','I3'})]==2 and res[frozenset({'I1','I2','I5'})]==2 and res[frozenset({'I2'})]==7)
# rules: brute-force check of confidence/lift against raw transactions
rows=[set(r) for r in T]; n=len(rows)
rl=rules.generate_rules(res,n,0.5)
def sup(s): return sum(s<=r for r in rows)
allok=True; count=0
for r in rl:
    a,c=frozenset(r.antecedent),frozenset(r.consequent); sc=sup(a|c)
    conf=Fraction(sc,sup(a)); lift=Fraction(sc*n,sup(a)*sup(c))
    allok&= (sc==r.support_count and abs(float(conf)-r.confidence)<1e-12 and abs(float(lift)-r.lift)<1e-12 and conf>=Fraction(1,2)); count+=1
# every qualifying rule enumerated?
expected=0
for items,sc in res.items():
    if len(items)<2: continue
    for k in range(1,len(items)):
        for ant in itertools.combinations(sorted(items),k):
            if Fraction(sc,sup(frozenset(ant)))>=Fraction(1,2): expected+=1
check(f'Rules: confidence/lift/support exact & complete ({count} rules)',allok and count==expected,f'{count} vs {expected}')
# known: {I1,I5}->{I2}: conf 2/2=1, lift = 1/(7/9)=9/7
r15=[r for r in rl if frozenset(r.antecedent)=={'I1','I5'} and frozenset(r.consequent)=={'I2'}]
check('Rule {I1,I5}->{I2} conf 1.0 lift 9/7',len(r15)==1 and r15[0].confidence==1.0 and abs(r15[0].lift-9/7)<1e-12)
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
