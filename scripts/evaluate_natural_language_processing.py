"""Execute all11 bounded educational examples; preserve actual output, not quality claims."""
from pathlib import Path
import json,os,subprocess,sys,time
from verify_natural_language_processing_scope import TOPICS
ROOT=Path(__file__).resolve().parents[1]

def main():
    records=[]
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
    for topic in TOPICS:
        script='machine-learning/natural-language-processing/'+topic+'/python/example.py';before=time.monotonic()
        result=subprocess.run([sys.executable,script],cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
        assert result.returncode==0,(topic,result.stderr)
        records.append(dict(topic=topic,command=['python',script],returncode=0,elapsed_seconds=round(time.monotonic()-before,6),output=json.loads(result.stdout)))
    data=dict(protocol='Actual11 toy examples:fit/training objectives and inference outputs,not held-out semantic accuracy or production pretraining',records=records,network=False,pretrained_weights=False,bert_gpt_training='head only;backbone frozen')
    (ROOT/'docs/natural-language-processing-evidence/educational-training-results.json').write_text(json.dumps(data,indent=2)+'\n')
    print('11 bounded offline NLP examples executed;actual training/inference output retained;no semantic quality claim.')

if __name__=='__main__':main()
