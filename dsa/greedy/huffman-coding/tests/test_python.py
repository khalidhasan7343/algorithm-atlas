"""Exhaustive merge optimality, prefix freedom, round trips and rejection contracts."""
import copy,json,subprocess,sys
from pathlib import Path
import pytest

def test_independent_optimality_and_round_trips(python_algorithm,cases):
    for args,expected in cases.vectors():
        frequencies,message=args;before=copy.deepcopy(frequencies)
        codec=python_algorithm.HuffmanCodec(frequencies);bits=codec.encode(message)
        result={'codes':list(codec.codes.items()),'bits':bits,'decoded':list(codec.decode(bits)),'cost':codec.weighted_length()}
        cases.validate(result,args,expected)
        assert frequencies==before

def test_determinism_and_codebook_ownership(python_algorithm):
    codec=python_algorithm.HuffmanCodec({65:5,66:2,67:1})
    assert codec.codes=={65:'1',66:'01',67:'00'}
    assert codec.encode(b'ABCA')=='101001'
    assert python_algorithm.HuffmanCodec({67:1,66:2,65:5}).codes==codec.codes
    equal=python_algorithm.HuffmanCodec({65:1,66:1,67:1,68:1})
    assert equal.codes=={65:'00',66:'01',67:'10',68:'11'}
    copy_of_codes=codec.codes;copy_of_codes[65]='bad'
    assert codec.decode('101001')==b'ABCA'
    single=python_algorithm.HuffmanCodec({0:7})
    assert single.codes=={0:'0'} and single.weighted_length()==7
    assert single.decode(single.encode(bytes([0])*10000))==bytes([0])*10000

def test_invalid_and_resource_boundaries(python_algorithm):
    for frequencies in [{0:0},{0:-1},{0:10**9+1},{0:True},{0:1.5},{True:1},{-1:1},{256:1},{'a':1},[]]:
        with pytest.raises(ValueError):python_algorithm.HuffmanCodec(frequencies)
    codec=python_algorithm.HuffmanCodec({65:5,66:2,67:1})
    for bits in ['0','2','01x',123,'0'*1000001]:
        with pytest.raises(ValueError):codec.decode(bits)
    for message in [b'Z',b'A'*10001,[65],bytearray(b'A')]:
        with pytest.raises(ValueError):codec.encode(message)
    empty=python_algorithm.HuffmanCodec({})
    assert empty.decode('')==b'' and empty.encode(b'')==''
    with pytest.raises(ValueError):empty.decode('0')
    single=python_algorithm.HuffmanCodec({65:1})
    for bits in ['1','0'*10001]:
        with pytest.raises(ValueError):single.decode(bits)

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='3 65 5 66 2 67 1 4 65 66 67 65\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and not result.stderr
    assert result.stdout.strip()=='{"codes":[[65,"1"],[66,"01"],[67,"00"]],"bits":"101001","decoded":[65,66,67,65],"cost":11}'
    for text in ['', '-1', '1 65 0 0','2 65 1 65 2 0','1 65 1 1 66','0 1 256','0 0 extra','1 256 1 0','1 65 1 1','0 0_0']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
