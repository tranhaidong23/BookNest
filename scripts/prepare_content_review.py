"""Offline packet/prompt/draft preparation. No provider calls or database writes."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from booknest.content_review import build_prompt,check_draft

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet',type=Path)
    parser.add_argument('--draft',type=Path)
    parser.add_argument('--model-version')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.draft and not args.model_version:parser.error('--draft requires --model-version (use human-draft for manual text)')
    packet=json.loads(args.packet.read_text(encoding='utf-8'))
    result=check_draft(packet,json.loads(args.draft.read_text(encoding='utf-8')),args.model_version) if args.draft else build_prompt(packet)
    output=args.output.resolve()
    if not output.is_relative_to((ROOT/'data/dev').resolve()):parser.error('Output must be inside data/dev; never overwrite catalogue or reports')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Created local review artifact; not approved for publication.')

if __name__=='__main__':main()
