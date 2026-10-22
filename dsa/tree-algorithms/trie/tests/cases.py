import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='trie'
SEED=8303

def vectors():return _o.trie_vectors()
def encode(case):return _o.encode_trie(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def invalid():
    return [dict(operations=[[op,word]]) for op in range(4) for word in ('A','a b','é','🙂','a'*257,None,True)]+[dict(operations=[[True,'a']]),dict(operations=[[4,'a']]),dict(operations=[[0]]),dict(operations=[[0,'a']]*1001)]
def invalid_cli():return ['', '-1','1001','1 0 A','1 0 é','1 0 '+('a'*257),'0 extra','1 4 a','1.0']
def boundaries(module):
    trie=module.Trie();assert trie.starts_with('') and not trie.contains('')
    assert trie.insert('a'*256) and trie.erase('a'*256) and trie._nodes==1
    def key(i):return ''.join(chr(97+(i//26**p)%26) for p in (2,1,0))
    for i in range(10000):assert trie.insert(key(i))
    assert not trie.insert(key(0)) and trie.size==10000
    try:trie.insert(key(10000))
    except ValueError:pass
    else:raise AssertionError('word cap')
    for i in range(10000):assert trie.erase(key(i))
    assert trie.size==0 and trie._nodes==1
    inserted=[]
    for i in range(500):
        word=key(i)+'x'*253
        try:trie.insert(word);inserted.append(word)
        except ValueError:break
    assert trie._nodes<=100000 and 300<len(inserted)<500
    size=trie.size
    assert trie.erase(inserted[-1]) and trie.insert('z'*256) and trie.size==size

DRIVER="int count=static_cast<int>(token());while(count--){trie_cli(false);std::cout<<'\\n';}"
BOUNDARY_DRIVER='Trie tree;bool ok=tree.starts_with("") && !tree.contains("");std::string longword(256,\'a\');ok=ok&&tree.insert(longword)&&tree.erase(longword);auto key=[](int i){std::string word;word+=static_cast<char>(\'a\'+i/676);word+=static_cast<char>(\'a\'+(i/26)%26);word+=static_cast<char>(\'a\'+i%26);return word;};for(int i=0;i<10000;++i)ok=ok&&tree.insert(key(i));try{tree.insert(key(10000));ok=false;}catch(const std::invalid_argument&){}for(int i=0;i<10000;++i)ok=ok&&tree.erase(key(i));std::vector<std::string> words;bool capped=false;for(int i=0;i<500;++i){auto word=key(i)+std::string(253,\'x\');try{tree.insert(word);words.push_back(word);}catch(const std::invalid_argument&){capped=true;break;}}ok=ok&&capped&&words.size()>300&&tree.erase(words.back())&&tree.insert(std::string(256,\'z\'));emit(ok);'
