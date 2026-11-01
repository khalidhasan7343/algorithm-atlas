from collections import deque
from itertools import product
import pytest
pytestmark=[pytest.mark.ml]

# No CYK chart,span iteration,split or backpointer is used in this oracle.
def derives(start,rules,target):
 if not target:return (start,()) in rules
 nts={a for a,_ in rules};n=len(target);queue=deque([((start,),0)]);seen={(start,)}
 while queue:
  form,steps=queue.popleft()
  if all(s not in nts for s in form):
   if form==tuple(target):return True
   continue
  if steps>=2*n-1:continue
  pos=next(i for i,s in enumerate(form) if s in nts)
  if tuple(target[:pos])!=form[:pos]:continue
  for lhs,rhs in rules:
   if lhs!=form[pos] or not rhs:continue
   candidate=form[:pos]+rhs+form[pos+1:]
   if len(candidate)<=n and candidate not in seen:
    seen.add(candidate);queue.append((candidate,steps+1))
 return False

GRAMMARS=[
 [('S',('a',))],
 [('S',('A','B')),('A',('a',)),('B',('b',))],
 [('S',('A','C')),('C',('A','B')),('A',('a',)),('B',('b',))],
 [('S',('S','S')),('S',('a',))],
 [('S',('A','A')),('A',('A','A'))],
 [('S',()),('S',('A','B')),('A',('a',)),('B',('b',))]
]

def validate_tree(tree,rules):
 children=tree.children
 if not children:
  assert (tree.symbol,()) in rules;return []
 if len(children)==1:
  assert isinstance(children[0],str) and (tree.symbol,(children[0],)) in rules
  return [children[0]]
 assert len(children)==2
 assert (tree.symbol,tuple(c.symbol for c in children)) in rules
 return validate_tree(children[0],rules)+validate_tree(children[1],rules)

@pytest.mark.oracle
@pytest.mark.parametrize('rules',GRAMMARS)
def test_exhaustive_independent_leftmost_derivation_oracle_and_trees(b13,rules):
 m=b13.load('cyk-parsing');parser=m.CYKParser('S',rules)
 for n in range(5):
  for seq in product('ab',repeat=n):
   expected=derives('S',rules,seq)
   assert parser.recognize(seq)==expected
   tree=parser.parse(seq)
   assert (tree is not None)==expected
   if tree is not None:
    assert tree.symbol=='S';assert validate_tree(tree,rules)==list(seq)

@pytest.mark.oracle
def test_hand_chart_tree_and_unknown_terminals(b13):
 p=b13.load('cyk-parsing').CYKParser('S',GRAMMARS[1]);chart=p.chart(['a','b'])
 assert chart=={(0,1):frozenset({'A'}),(1,2):frozenset({'B'}),(0,2):frozenset({'S'})}
 assert p.parse(['a','b']).to_tuple()==('S',('A','a'),('B','b'))
 assert not p.recognize(['unknown']) and p.parse([]) is None
 assert p.chart([])=={}

@pytest.mark.parametrize('rules',[
 [],None,[('S',('S',))],[('A',('a',))],[('S',('A','B')),('A',('a',))],
 [('S',('a','b'))],[('S',('a','b','c'))],[('S','a')],[('S',('A','A')),('A',())],
 [('S',()),('S',('S','S'))],[('',('a',))],[('S',(1,))],[('S',('',))],[('S',('a',))]*129,
 [(str(i),('a',)) for i in range(33)]+[('S',('a',))]])
def test_invalid_grammar_cnf_and_resource_limits(b13,rules):
 with pytest.raises(ValueError):b13.load('cyk-parsing').CYKParser('S',rules)

@pytest.mark.parametrize('bad',[None,'a',1,[None],[''],['a'*129],['a']*33])
def test_invalid_tokens_and_resource_bounds(b13,bad):
 p=b13.load('cyk-parsing').CYKParser('S',GRAMMARS[0])
 for method in (p.chart,p.parse,p.recognize):
  with pytest.raises(ValueError):method(bad)

@pytest.mark.parametrize('bad',[None,'','S'*33,1])
def test_invalid_start(b13,bad):
 with pytest.raises(ValueError):b13.load('cyk-parsing').CYKParser(bad,GRAMMARS[0])

def test_ambiguous_deterministic_grammar_order_and_owned_chart(b13):
 m=b13.load('cyk-parsing');rules=GRAMMARS[3]
 a=m.CYKParser('S',rules);b=m.CYKParser('S',list(reversed(rules))+rules)
 assert a.parse(['a']*4).to_tuple()==b.parse(['a']*4).to_tuple()
 chart=a.chart(['a']);chart[0,1]=frozenset()
 assert a.recognize(['a'])

@pytest.mark.parametrize('word',['猫','A','!'])
def test_literal_unicode_and_case_sensitive_terminals(b13,word):
 p=b13.load('cyk-parsing').CYKParser('S',[('S',(word,))])
 assert p.recognize([word]) and p.parse([word]).to_tuple()==('S',word)


def test_start_only_epsilon_and_unproductive_grammar(b13):
 cls=b13.load('cyk-parsing').CYKParser
 assert cls('S',[('S',())]).parse([]).to_tuple()==('S',)
 assert not cls('S',GRAMMARS[4]).recognize(['a']*32)
