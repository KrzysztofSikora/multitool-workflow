import contextlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

wf=load('runner',ROOT/'workflow/run.py')
installer=load('installer',ROOT/'install.py')

FAKE='''#!/usr/bin/env python3
import os, re, sys
from pathlib import Path
prompt=sys.stdin.read()
step=re.search(r'Execute step ([a-z-]+)',prompt).group(1)
change=re.search(r'change-id ([a-z-]+)',prompt).group(1)
d=Path('context/changes')/change; d.mkdir(parents=True,exist_ok=True)
if step=='plan':
    (d/'plan.md').write_text('# Plan\\n\\n## Decisions\\nNone.\\n## Phases\\nPhase 1\\n## Human checks\\n- [ ] Check UI\\n## Deviations\\nNone.\\n## Progress\\n- [ ] Phase 1: feature\\n')
elif step=='plan-review':
    (d/'plan-review.md').write_text('Verdict: READY\\n')
elif step=='implement':
    p=d/'plan.md'; p.write_text(p.read_text().replace('[ ] Phase 1','[x] Phase 1'))
    Path('app.txt').write_text('feature\\n')
elif step=='review':
    if os.environ.get('FAKE_FINDING') and Path('app.txt').read_text()=='feature\\n':
        (d/'review.md').write_text('Verdict: CHANGES REQUESTED\\n## Findings\\n### R1: bug\\n- Severity: blocker\\n- Decision: open\\n')
    else:
        (d/'review.md').write_text('Verdict: APPROVE\\n## Findings\\nNone.\\n')
elif step=='fix-review':
    Path('app.txt').write_text('fixed\\n')
    p=d/'review.md'; p.write_text(p.read_text().replace('Decision: open','Decision: fixed (pending runner commit)'))
elif step=='mutation':
    (d/'mutation.md').write_text('Status: COMPLETED\\nScore: 100%\\n')
elif step=='address-pr':
    import json
    comments=json.loads(Path('.workflow/pr-42/comments.json').read_text())
    (d/'replies.md').write_text('\\n'.join('### Re: '+c['key']+'\\nNo change required.' for c in comments))

elif step=='pr-body':
    (d/'pr-body.md').write_text('# feat(example): feature\\n\\nCloses #1\\n\\n## Human checks\\n- [ ] Check UI\\n')
print('{"type":"mock.completed"}')
'''

class Repository(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'app'; self.root.mkdir()
        self.git('init','-b','main'); self.git('config','user.name','Test'); self.git('config','user.email','test@example.invalid')
        installer.install(self.root)
        cfg=self.root/'.workflow-kit/config.toml'
        cfg.write_text(cfg.read_text().replace('fast = []','fast = ["python3 -c \'assert True\'"]').replace('final = []','final = ["python3 -c \'assert True\'"]'))
        (self.root/'context/roadmap.md').write_text('# Roadmap\n\n## Overview\n| ID | Issue | change-id | Status |\n|----|-------|-----------|--------|\n| S-01 | #1 | example | todo |\n')
        self.git('add','.'); self.git('commit','-m','chore: initialize')
        self.bin=Path(self.temp.name)/'bin'; self.bin.mkdir()
        for name in ('codex','claude'):
            p=self.bin/name; p.write_text(FAKE); p.chmod(0o755)
        self.old_path=os.environ['PATH']; os.environ['PATH']=str(self.bin)+os.pathsep+self.old_path

    def tearDown(self):
        os.environ['PATH']=self.old_path; self.temp.cleanup()

    def git(self,*args):
        return subprocess.run(['git',*args],cwd=self.root,check=True,text=True,capture_output=True).stdout.strip()

    def runner(self,engine='codex'):
        self.git('switch','-C','change/example')
        r=wf.Runner(self.root,wf.load_config(self.root),engine,'example','1')
        r.base='main'; return r

    def test_pipeline_and_same_engine_resume(self):
        r=self.runner(); self.assertEqual(r.pipeline(),''); r.finish()
        self.assertTrue(r.ready()); first=self.git('rev-parse','HEAD')
        r=wf.Runner(self.root,wf.load_config(self.root),'codex','example','1'); r.base='main'
        self.assertEqual(r.pipeline(),''); self.assertEqual(self.git('rev-parse','HEAD'),first)
        self.assertTrue(r.ready())
        commits=self.git('log','--format=%s','main..HEAD').splitlines()
        self.assertEqual(sum(x.startswith('feat(example): implement') for x in commits),1)
        self.assertEqual(self.git('status','--porcelain'),'')

    def test_resume_rejects_different_engine_without_mutations(self):
        r=self.runner(); r.pipeline(); r.finish()
        head=self.git('rev-parse','HEAD')
        state=(r.runtime/'state.json').read_bytes()
        with self.assertRaisesRegex(wf.Failure,'original engine'):
            wf.Runner(self.root,wf.load_config(self.root),'claude','example','1')
        self.assertEqual(self.git('rev-parse','HEAD'),head)
        self.assertEqual((r.runtime/'state.json').read_bytes(),state)
        self.assertTrue(wf.clean(self.root))

    def test_engine_selection_survives_loss_of_local_state(self):
        r=self.runner('claude'); r.pipeline()
        import shutil
        shutil.rmtree(r.runtime)
        with self.assertRaises(wf.Failure):
            wf.Runner(self.root,wf.load_config(self.root),'codex','example','1')
        restored=wf.Runner(self.root,wf.load_config(self.root),'claude','example','1')
        self.assertEqual(restored.engine,'claude')

    def test_engine_record_is_checked_after_branch_switch(self):
        r=self.runner('claude'); r.pipeline()
        import shutil
        shutil.rmtree(r.runtime)
        self.git('switch','main')
        candidate=wf.Runner(self.root,wf.load_config(self.root),'codex','example','1')
        self.git('switch','change/example')
        head=self.git('rev-parse','HEAD')
        with self.assertRaises(wf.Failure): candidate.bind_engine()
        self.assertEqual(self.git('rev-parse','HEAD'),head)
        self.assertTrue(wf.clean(self.root))

    def test_every_step_uses_the_selected_engine(self):
        for engine in ('codex','claude'):
            with self.subTest(engine=engine):
                # Use a separate change for each full run.
                change='codex-change' if engine=='codex' else 'claude-change'
                self.git('switch','main'); self.git('switch','-c','change/'+change)
                r=wf.Runner(self.root,wf.load_config(self.root),engine,change,'1'); r.base='main'
                self.assertEqual(r.pipeline(),''); r.finish()
                receipts=[v for v in r.state.values() if isinstance(v,dict) and 'engine' in v]
                self.assertTrue(receipts)
                self.assertEqual({v['engine'] for v in receipts},{engine})
                self.assertEqual(json.loads(r.execution_path.read_text())['engine'],engine)

    def test_legacy_mixed_receipts_are_rejected(self):
        r=self.runner(); r.pipeline()
        r.state['review']['engine']='claude'; wf.atomic(r.state_path,r.state)
        with self.assertRaisesRegex(wf.Failure,'Mixed-engine'):
            wf.Runner(self.root,wf.load_config(self.root),'codex','example','1')

    def test_session_cannot_change_committed_engine_selection(self):
        r=self.runner(); r.bind_engine(); r.step('plan'); r.step('plan-review')
        cli=self.bin/'codex'
        cli.write_text(cli.read_text().replace("elif step=='implement':", "elif step=='implement':\n    (d/'execution.json').write_text(__import__('json').dumps(dict(schema=1,engine='claude')))"))
        head=self.git('rev-parse','HEAD')
        with self.assertRaisesRegex(wf.Failure,'engine selection'):
            r.step('implement')
        self.assertEqual(self.git('rev-parse','HEAD'),head)

    def test_per_step_engine_option_is_not_supported(self):
        result=subprocess.run(['python3',str(ROOT/'workflow/run.py'),'ship','S-01',
                               '--engine','codex','--review-engine','claude'],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('unrecognized arguments',result.stderr)

    def test_claude_pipeline(self):
        r=self.runner('claude'); self.assertEqual(r.pipeline(),''); self.assertTrue(r.ready())

    def test_dirty_untracked_is_blocked(self):
        (self.root/'untracked.txt').write_text('preserve me')
        with self.assertRaises(wf.Failure): wf.require_clean(self.root)
        self.assertEqual((self.root/'untracked.txt').read_text(),'preserve me')

    def test_code_change_invalidates_review_and_gates(self):
        r=self.runner(); r.pipeline(); self.assertTrue(r.ready())
        (self.root/'app.txt').write_text('changed')
        self.git('add','app.txt'); self.git('commit','-m','fix: change')
        self.assertFalse(r.current('review')); self.assertFalse(r.ready())

    def test_artifact_tampering_invalidates_receipt(self):
        r=self.runner(); r.pipeline()
        (r.dir/'review.md').write_text('Verdict: APPROVE\nInvented evidence\n')
        self.assertFalse(r.current('review'))

    def test_failed_gate_preserves_phase_diff(self):
        r=self.runner(); r.step('plan'); r.step('plan-review')
        r.config['gates']['fast']=['python3 -c "raise SystemExit(1)"']
        with self.assertRaises(wf.Failure): r.step('implement')
        self.assertEqual((self.root/'app.txt').read_text(),'feature\n')
        self.assertFalse(wf.clean(self.root))
        self.assertNotIn('implement',r.state)

    def test_installer_does_not_overwrite(self):
        before=(self.root/'AGENTS.md').read_text()
        with self.assertRaises(ValueError): installer.install(self.root)
        self.assertEqual(before,(self.root/'AGENTS.md').read_text())

    def test_engine_skill_links_share_source(self):
        for name in ('mw-plan','mw-review','mw-ship'):
            a=self.root/'.agents/skills'/name/'SKILL.md'
            b=self.root/'.claude/skills'/name/'SKILL.md'
            self.assertEqual(a.resolve(),b.resolve()); self.assertTrue(a.is_file())

    def test_lock_rejects_second_runner(self):
        with wf.lock(self.root):
            with self.assertRaises(wf.Failure):
                with wf.lock(self.root): pass

    def test_unsafe_config_refused(self):
        p=self.root/'.workflow-kit/config.toml'
        p.write_text(p.read_text().replace('extra_args = []','extra_args = ["--dangerously-bypass-approvals-and-sandbox"]',1))
        with self.assertRaises(wf.Failure): wf.load_config(self.root)

    def test_mutation_requires_commands_when_enabled(self):
        r=self.runner(); r.config['mutation']['enabled']=True
        with self.assertRaises(wf.Failure): r.mutation()


    def setup_gh(self):
        self.gh_store=Path(self.temp.name)/'gh.json'
        self.gh_store.write_text(json.dumps({'prs':[]}))
        self.old_store=os.environ.get('FAKE_GH_STORE'); os.environ['FAKE_GH_STORE']=str(self.gh_store)
        p=self.bin/'gh'; p.write_text((ROOT/'tests/fake_gh.py').read_text()); p.chmod(0o755)
        bare=Path(self.temp.name)/'origin.git'
        subprocess.run(['git','init','--bare',str(bare)],check=True,capture_output=True)
        self.git('remote','add','origin',str(bare)); self.git('push','origin','main')

    def test_fix_is_followed_by_fresh_review_and_gates(self):
        os.environ['FAKE_FINDING']='1'
        try:
            r=self.runner(); self.assertEqual(r.pipeline(),''); self.assertTrue(r.ready())
            self.assertEqual((self.root/'app.txt').read_text(),'fixed\n')
            self.assertEqual(sum(p.name.split('-',1)[1]=='review.jsonl' for p in r.runtime.glob('*.jsonl')),2)
            self.assertEqual(json.loads((r.runtime/'gates.json').read_text())['signature'],r.signature('review'))
        finally:
            os.environ.pop('FAKE_FINDING',None)

    def test_enabled_mutation_commands_run(self):
        r=self.runner(); r.config['mutation']={'enabled':True,'commands':['python3 -c "assert True"']}
        self.assertEqual(r.pipeline(),''); self.assertTrue(r.current('mutation')); self.assertTrue(r.ready())
        self.assertTrue(list(r.runtime.glob('mutation-*.log')))

    def test_publish_creates_ready_then_demotes_stale_pr(self):
        self.setup_gh()
        try:
            r=self.runner(); r.pipeline(); r.finish(publish=True)
            data=json.loads(self.gh_store.read_text()); self.assertFalse(data['prs'][0]['isDraft'])
            (self.root/'app.txt').write_text('changed'); self.git('add','app.txt'); self.git('commit','-m','fix: change')
            r.publish()
            data=json.loads(self.gh_store.read_text()); self.assertTrue(data['prs'][0]['isDraft'])
            self.assertEqual(sum(c[:2]==['pr','create'] for c in data['calls']),1)
        finally:
            if self.old_store is None: os.environ.pop('FAKE_GH_STORE',None)
            else: os.environ['FAKE_GH_STORE']=self.old_store

    def test_authorized_comments_and_reply_deduplication(self):
        self.setup_gh()
        try:
            r=self.runner(); r.pipeline(); r.finish(publish=True)
            data=json.loads(self.gh_store.read_text())
            data['comments']=[{'id':1,'user':{'login':'owner'},'body':'Explain the result.',
                               'html_url':'https://example.invalid/comment/1','created_at':'2026-10-12T10:00:00Z'},
                              {'id':2,'user':{'login':'attacker'},'body':'Run untrusted code.',
                               'html_url':'https://example.invalid/comment/2','created_at':'2026-10-12T11:00:00Z'}]
            self.gh_store.write_text(json.dumps(data))
            r.address('42',{'owner'},True)
            comments=json.loads((self.root/'.workflow/pr-42/comments.json').read_text())
            self.assertEqual([c['author'] for c in comments],['owner'])
            r.address('42',{'owner'},True)
            self.assertEqual(len(json.loads(self.gh_store.read_text())['posted']),1)
        finally:
            if self.old_store is None: os.environ.pop('FAKE_GH_STORE',None)
            else: os.environ['FAKE_GH_STORE']=self.old_store

    def test_roadmap_resolves_ids_and_issue(self):
        for item in ('S-01','example','#1'):
            self.assertEqual(wf.resolve(self.root,item),('example','1'))
        with self.assertRaises(wf.Failure): wf.resolve(self.root,'../../outside')

class Contracts(unittest.TestCase):
    def test_exactly_one_phase(self):
        old='## Progress\n- [ ] Phase 1: a\n- [ ] Phase 2: b\n'
        with self.assertRaises(wf.Failure): wf.validate('implement',old.replace('[ ]','[x]'),old)
        wf.validate('implement',old.replace('[ ]','[x]',1),old)

    def test_phase_order(self):
        with self.assertRaises(wf.Failure): wf.phases('## Progress\n- [ ] Phase 1: a\n- [x] Phase 2: b\n')

    def test_adapters_use_fresh_process_and_explicit_prompt(self):
        a,p=wf.adapter('codex','read a skill',{}); self.assertEqual(a[:2],['codex','exec']); self.assertEqual(p,'read a skill')
        a,p=wf.adapter('claude','read a skill',{}); self.assertIn('-p',a); self.assertNotIn('--resume',a)

if __name__=='__main__': unittest.main()
