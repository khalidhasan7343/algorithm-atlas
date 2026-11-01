"""CNF Cocke–Younger–Kasami recognition and one deterministic parse witness."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ParseTree:
    symbol: str
    children: tuple

    def to_tuple(self):
        return (self.symbol,*(child.to_tuple() if isinstance(child,ParseTree) else child for child in self.children))


class CYKParser:
    """Explicit grammar rules (lhs,tuple(rhs)); no implicit CFG conversion."""
    def __init__(self,start,productions):
        if not isinstance(start,str) or not start or len(start)>32:
            raise ValueError('bounded nonempty start nonterminal required')
        if not isinstance(productions,(list,tuple)) or not 1<=len(productions)<=128:
            raise ValueError('1..128 explicit CNF productions required')
        rules=[]
        for rule in productions:
            if not isinstance(rule,(list,tuple)) or len(rule)!=2:
                raise ValueError('production is (lhs,tuple(rhs))')
            lhs,rhs=rule
            if not isinstance(lhs,str) or not lhs or len(lhs)>32 or not isinstance(rhs,tuple) or len(rhs)>2 or any(not isinstance(s,str) or not s or len(s)>128 for s in rhs):
                raise ValueError('bounded lhs and tuple rhs of length0..2 required')
            rules.append((lhs,rhs))
        nonterminals={lhs for lhs,_ in rules}
        if start not in nonterminals or len(nonterminals)>32:
            raise ValueError('start must occur as lhs;at most32 nonterminals')
        epsilon=False
        for lhs,rhs in rules:
            if not rhs:
                if lhs!=start:raise ValueError('epsilon only allowed at start')
                epsilon=True
            elif len(rhs)==1:
                if rhs[0] in nonterminals:raise ValueError('unit nonterminal productions are not CNF')
            elif any(s not in nonterminals for s in rhs):
                raise ValueError('binary rhs must contain two defined nonterminals')
        if epsilon and any(start in rhs for _,rhs in rules):
            raise ValueError('epsilon start must not occur in any rhs')
        self.start_=start;self.productions_=tuple(sorted(set(rules)))
        self.nonterminals_=frozenset(nonterminals);self.epsilon_=epsilon
        self.terminals_=tuple((a,rhs[0]) for a,rhs in self.productions_ if len(rhs)==1)
        self.binaries_=tuple((a,*rhs) for a,rhs in self.productions_ if len(rhs)==2)

    @staticmethod
    def _tokens(tokens):
        if not isinstance(tokens,(list,tuple)) or len(tokens)>32 or any(not isinstance(t,str) or not t or len(t)>128 for t in tokens):
            raise ValueError('0..32 bounded nonempty token strings required')
        return tuple(tokens)

    def _chart(self,tokens):
        n=len(tokens);chart={(i,j):set() for i in range(n) for j in range(i+1,n+1)};back={}
        for i,token in enumerate(tokens):
            for a,terminal in self.terminals_:
                if terminal==token:
                    chart[i,i+1].add(a);back[i,i+1,a]=('terminal',token)
        for length in range(2,n+1):
            for i in range(n-length+1):
                j=i+length
                for split in range(i+1,j):
                    for a,b,c in self.binaries_:
                        if a not in chart[i,j] and b in chart[i,split] and c in chart[split,j]:
                            chart[i,j].add(a);back[i,j,a]=('binary',split,b,c)
        return chart,back

    def chart(self,tokens):
        tokens=self._tokens(tokens)
        return {key:frozenset(value) for key,value in self._chart(tokens)[0].items()}

    def recognize(self,tokens):
        tokens=self._tokens(tokens)
        if not tokens:return self.epsilon_
        return self.start_ in self._chart(tokens)[0][0,len(tokens)]

    def parse(self,tokens):
        tokens=self._tokens(tokens)
        if not tokens:return ParseTree(self.start_,()) if self.epsilon_ else None
        chart,back=self._chart(tokens)
        if self.start_ not in chart[0,len(tokens)]:return None
        def build(i,j,a):
            record=back[i,j,a]
            if record[0]=='terminal':return ParseTree(a,(record[1],))
            _,k,b,c=record
            return ParseTree(a,(build(i,k,b),build(k,j,c)))
        return build(0,len(tokens),self.start_)
