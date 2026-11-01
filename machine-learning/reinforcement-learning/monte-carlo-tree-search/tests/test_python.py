import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=[pytest.mark.ml,pytest.mark.oracle]


def walk(root):
    yield root
    for child in root.children.values():yield from walk(child)


def test_tree_initialization_terminal_and_uct_hand_value(rl):
    m=rl.load('monte-carlo-tree-search');model=m.TinyPlanning()
    node=m.Node((0,0));assert node.visits==0 and node.mean==0
    assert m.uct(node,1)==float('inf')
    node.visits=4;node.value_sum=2
    assert_allclose(m.uct(node,16,2),.5+2*np.sqrt(np.log(16)/4))
    action,root=m.search(model,(3,7),iterations=10)
    assert action is None and root.visits==0 and not root.children


def test_visit_counts_backpropagation_single_agent_perspective(rl):
    m=rl.load('monte-carlo-tree-search');root=m.Node((0,0));child=m.Node((1,1),root,1)
    m.backpropagate(child,.75);m.backpropagate(child,.25)
    assert root.visits==child.visits==2 and root.value_sum==child.value_sum==1
    assert root.mean==child.mean==.5  # No alternating-player sign flip.


@pytest.mark.parametrize('seed',[91,92,93])
def test_seeded_planning_tree_invariants_and_legal_expansion(rl,seed):
    m=rl.load('monte-carlo-tree-search');model=m.TinyPlanning()
    action,root=m.search(model,(0,0),iterations=200,max_depth=3,seed=seed)
    other_action,other=m.search(model,(0,0),iterations=200,max_depth=3,seed=seed)
    assert action==other_action==1 and root.visits==200
    assert len(list(walk(root)))<=201
    assert sum(c.visits for c in root.children.values())==root.visits
    for a,b in zip(walk(root),walk(other)):
        assert (a.state,a.visits,a.value_sum)==(b.state,b.visits,b.value_sum)
        assert 0<=a.value_sum<=a.visits
        assert set(a.children)<=set(model.legal_actions(a.state))
        for act,child in a.children.items():
            assert child.state==model.transition(a.state,act) and child.parent is a
    # Follow separately replanned decisions, not a stored rollout.
    state=(0,0)
    while not model.terminal(state):
        a,_=m.search(model,state,iterations=100,max_depth=3,seed=seed)
        state=model.transition(state,a)
    assert model.outcome(state)==1


def test_rollout_reward_and_budget_exhaustion(rl):
    m=rl.load('monte-carlo-tree-search');model=m.TinyPlanning()
    assert m.rollout(model,(3,7),np.random.default_rng(1),0)==1
    assert m.rollout(model,(3,0),np.random.default_rng(1),0)==0
    with pytest.raises(ValueError,match='depth'):m.search(model,(0,0),max_depth=1)
    with pytest.raises(ValueError):m.search(model,(0,0),iterations=0)
    with pytest.raises(ValueError):m.search(model,(0,0),iterations=10001)


def test_unvisited_children_and_small_search_budget(rl):
    m=rl.load('monte-carlo-tree-search');action,root=m.search(m.TinyPlanning(),(0,0),iterations=1,max_depth=3,seed=4)
    assert action in (0,1) and root.visits==1 and len(root.children)==1
    assert len(root.untried)==1


def test_invalid_legal_actions_and_nonfinite_outcomes(rl):
    m=rl.load('monte-carlo-tree-search')
    class Bad(m.TinyPlanning):
        def legal_actions(self,s):return [0,0]
    with pytest.raises(ValueError):m.search(Bad(),(0,0))
    class NaN(m.TinyPlanning):
        def outcome(self,s):return np.nan
    with pytest.raises(ValueError):m.search(NaN(),(3,1))


def test_oversized_action_iterator_stops_before_materializing_unbounded_output(rl):
    m=rl.load('monte-carlo-tree-search');seen=[]
    class Infinite(m.TinyPlanning):
        def legal_actions(self,state):
            def values():
                i=0
                while True:
                    seen.append(i);yield i;i+=1
            return values()
    with pytest.raises(ValueError,match='at most32'):m.legal(Infinite(),(0,0))
    assert seen==list(range(33))


@pytest.mark.parametrize('bad',[[0],{'action':0},True,'0'])
def test_invalid_action_type_rejected_before_uniqueness_hashing(rl,bad):
    m=rl.load('monte-carlo-tree-search')
    class Malformed(m.TinyPlanning):
        def legal_actions(self,state):return [bad]
    with pytest.raises(ValueError,match='legal action'):m.legal(Malformed(),(0,0))
