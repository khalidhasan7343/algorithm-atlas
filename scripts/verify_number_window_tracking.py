"""Verify report existence, completion pointer and Git inclusion readiness."""
import json
from pathlib import Path
import subprocess
import yaml
from review_paths import report_paths

ROOT=Path(__file__).resolve().parents[1]


def main():
    catalog=yaml.safe_load((ROOT/"catalog.yaml").read_text())
    completion=catalog["development"]["completion_reports"]
    reports=sorted(set(report_paths(ROOT))|set(completion.values()))
    tracked=set(subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0"))
    available=set(subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard","-z"],cwd=ROOT).decode().split("\0"))
    rows={}
    for name in reports:
        assert (ROOT/name).is_file() and (ROOT/name).stat().st_size>0,name
        ignored=subprocess.run(["git","check-ignore","--no-index","--quiet",name],cwd=ROOT)
        assert ignored.returncode==1,name
        assert name in available,name
        rows[name]=dict(nonempty=True,ignored=False,tracked=name in tracked,
                        git_state="tracked" if name in tracked else "unignored new file ready to track")
    modified=subprocess.check_output(["git","diff","--name-only"],cwd=ROOT,text=True).splitlines()
    new=subprocess.check_output(["git","ls-files","--others","--exclude-standard"],cwd=ROOT,text=True).splitlines()
    result=dict(reports=rows,report_count=len(rows),completion_report=catalog["development"]["completion_report"],
                completion_reports=completion,git_snapshot="working source, including unignored new files; index not changed",status="passed",
                clean_tracked_checkout="not run; source-only package extraction is validated separately")
    additions=[]
    for category in ('number-theory','two-pointers-sliding-window'):
        prefix=f'artifacts/review-packages/{category}/algorithm-atlas-{category}-review'
        additions.extend(prefix+suffix for suffix in ('.zip','.zip.sha256','.json'))
        additions.extend(f'docs/{category}-evidence/'+name for name in ('changed-files.txt','tracking-results.json'))
    manifest="\n".join(sorted(set(modified+new+additions)))+"\n"
    for category in ('number-theory','two-pointers-sliding-window'):
        evidence=ROOT/f'docs/{category}-evidence'
        (evidence/'changed-files.txt').write_text(manifest)
        (evidence/'tracking-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"{len(rows)} nonempty, unignored reports; completion pointer verified")


if __name__=="__main__":main()
