"""Read-only inventory with heuristic checks; no publication approval or upload."""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.venv','data','artifacts','node_modules','.git','__pycache__','.pytest_cache','.ipynb_checkpoints','.vscode'}
PATTERNS={
    'private_key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token':re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'openai_key_shape':re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),
    'postgres_password_url':re.compile(r'postgres(?:ql)?://[^\s/:]+:[^\s/@]+@'),
}

def inventory(root=ROOT):
    rows=[];findings=[]
    for parent,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[n for n in dirs if n not in SKIP and not (Path(parent)/n).is_symlink()]
        for name in names:
            p=Path(parent)/name;relative=p.relative_to(root).as_posix()
            if p.is_symlink() or name.startswith('.env') or name=='secrets.toml' or p.suffix in ('.pyc','.pyo'):continue
            if relative.startswith('reports/github_preparation/'):continue
            raw=p.read_bytes();rows.append({'path':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            if len(raw)>5*1024*1024:findings.append({'path':relative,'category':'large_file_manual_review'})
            try:text=raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                findings.append({'path':relative,'category':'binary_manual_review'});continue
            for category,pattern in PATTERNS.items():
                if pattern.search(text):findings.append({'path':relative,'category':category})
            if p.suffix=='.ipynb':
                try:
                    if any(cell.get('outputs') for cell in json.loads(text).get('cells',[])):
                        findings.append({'path':relative,'category':'notebook_outputs_manual_review'})
                except (ValueError,AttributeError):findings.append({'path':relative,'category':'notebook_parse_failed'})
    return {'candidate_count':len(rows),'candidate_bytes':sum(r['bytes'] for r in rows),
        'files':sorted(rows,key=lambda r:r['path']),'findings':findings,
        'git_ignore_engine_used':False,'actual_git_index_checked':False,
        'content_rights_approved':False,'secret_scan_exhaustive':False,'ready_to_publish':False}

if __name__=='__main__':print(json.dumps(inventory(),indent=2))
