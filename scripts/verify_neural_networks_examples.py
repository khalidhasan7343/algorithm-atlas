"""Execute B7 worked examples/JSON CLIs, including the preserved shared B5 example."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/neural-networks-and-deep-learning-evidence'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--topics',nargs='+');p.add_argument('--check-only',action='store_true');a=p.parse_args()
 manifest=json.loads((E/'example-inputs.json').read_text());records=[]
 env=os.environ.copy();env.update(PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 for name,item in manifest.items():
  if a.topics and name not in a.topics:continue
  folder=ROOT/item['canonical_location'];outputs=[];durations=[]
  for script,stdin in [('example.py',None),('solution.py',json.dumps(item['payload']))]:
   started=time.monotonic()
   r=subprocess.run([sys.executable,str(folder/'python'/script)],input=stdin,text=True,capture_output=True,timeout=60,cwd=ROOT,env=env)
   durations.append(round(time.monotonic()-started,6))
   assert r.returncode==0,(name,r.stderr);outputs.append(json.loads(r.stdout))
  assert outputs[0]==outputs[1],name
  for key,value in outputs[0].items():
   if key!='optimization_status':assert np.isfinite(np.asarray(value,dtype=float)).all(),(name,key)
  if name=='multilayer-perceptron':assert outputs[0]['prediction']==[0,1,1,0] and outputs[0]['loss_final']<.1
  if name=='vanilla-autoencoders':assert np.array(outputs[0]['embedding']).shape==(3,1)
  invalid=dict(item['payload'],X=[])
  r=subprocess.run([sys.executable,str(folder/'python/solution.py')],input=json.dumps(invalid),text=True,capture_output=True,timeout=30,cwd=ROOT,env=env)
  assert r.returncode==2 and r.stderr and not r.stdout,(name,r.stderr)
  records.append(dict(id=name,example='passed',equivalent_cli='passed',invalid_cli='passed',elapsed_seconds=dict(example=durations[0],equivalent_cli=durations[1]),interpreter=sys.executable,output=outputs[0]))
 assert records
 if not a.check_only:
  suffix='' if not a.topics else '-'+('-'.join(a.topics));(E/('examples-results'+suffix+'.json')).write_text(json.dumps(records,indent=2)+'\n')
 print(f'{len(records)} examples + equivalent/invalid CLIs passed')
if __name__=='__main__':main()
