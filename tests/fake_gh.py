#!/usr/bin/env python3
"""GitHub CLI test double; all data are stored locally, never sent to a server."""
import json
import os
from pathlib import Path
import sys

store=Path(os.environ['FAKE_GH_STORE'])
data=json.loads(store.read_text())
a=sys.argv[1:]
def finish(value):
    store.write_text(json.dumps(data))
    print(value if isinstance(value,str) else json.dumps(value)); raise SystemExit(0)

data.setdefault('calls',[]).append(a)
if a[:2]==['api','user']:
    finish('owner')
if a[:2]==['pr','list']:
    finish(data.get('prs',[]))
if a[:2]==['pr','view']:
    finish({'headRefName':'change/example','baseRefName':'main','isCrossRepository':False,'state':'OPEN'})
if a[:2]==['pr','create']:
    data['prs']=[{'number':42,'url':'https://example.invalid/pull/42','isDraft':'--draft' in a}]
    finish(data['prs'][0]['url'])
if a[:2]==['pr','ready']:
    data['prs'][0]['isDraft']='--undo' in a; finish('')
if a[0]=='api':
    path=next(x for x in a[1:] if x.startswith('repos/'))
    if '-X' in a:
        method=a[a.index('-X')+1]
        if method=='POST' and path.endswith('/comments'):
            body=next(x[6:] for x in a if x.startswith('body=@'))
            data.setdefault('posted',[]).append({'id':100+len(data.get('posted',[])),
                'user':{'login':'owner'},'body':Path(body).read_text(),
                'html_url':'https://example.invalid/reply','created_at':'2026-10-12T12:00:00Z'})
        finish({})
    if path.endswith('/reviews'):
        finish([data.get('reviews',[])])
    if '/issues/' in path and path.endswith('/comments'):
        finish([data.get('comments',[])+data.get('posted',[])])
    if '/pulls/' in path and path.endswith('/comments'):
        finish([data.get('inline',[])])
raise SystemExit('Unsupported fake gh call')
