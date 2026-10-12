#!/usr/bin/env python3
"""Vendor a pinned workflow into an application repository without overwriting files."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE=Path(__file__).resolve().parent

def install(target):
    target=target.resolve()
    if not (target/'.git').exists():
        raise ValueError('Initialize the target Git repository first.')
    kit=target/'.workflow-kit'
    if kit.exists():
        raise ValueError('.workflow-kit already exists; upgrades require an explicit reviewed replacement.')
    names=sorted(p.name for p in (SOURCE/'workflow/skills').iterdir())
    destinations=[target/scope/name for scope in ('.agents/skills','.claude/skills') for name in names]
    for path in destinations:
        if path.exists() or path.is_symlink():
            raise ValueError(f'Skill collision: {path}')
    shutil.copytree(SOURCE/'workflow',kit,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(SOURCE/'templates/config.toml',kit/'config.toml')
    revision=subprocess.run(['git','rev-parse','HEAD'],cwd=SOURCE,capture_output=True,text=True)
    (kit/'VERSION').write_text((revision.stdout.strip() or 'uncommitted-source')+'\n')
    for path in destinations:
        path.parent.mkdir(parents=True,exist_ok=True)
        # Both engines discover the same canonical file. All links remain inside the app repo.
        path.symlink_to(Path('../../.workflow-kit/skills')/path.name,target_is_directory=True)
    if not (target/'AGENTS.md').exists():
        shutil.copyfile(SOURCE/'templates/AGENTS.md',target/'AGENTS.md')
    if not (target/'CLAUDE.md').exists():
        (target/'CLAUDE.md').write_text('# Project instructions\n\nRead `AGENTS.md` and `.workflow-kit/autonomy.md`. Shared skills are in `.workflow-kit/skills`.\n')
    else:
        print('Existing CLAUDE.md preserved. Add a reference to AGENTS.md yourself.')
    ignored=target/'.gitignore'
    content=ignored.read_text() if ignored.exists() else ''
    if '.workflow/' not in content.splitlines():
        ignored.write_text(content+('' if not content or content.endswith('\n') else '\n')+'\n# Local runner state and private session logs\n.workflow/\n')
    (target/'context').mkdir(exist_ok=True)
    print(f'Installed in {target}. Configure gates and project rules, then commit the installation.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',type=Path)
    args=parser.parse_args()
    try:
        install(args.target)
    except (ValueError,OSError) as e:
        print(f'Not installed: {e}',file=sys.stderr); return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
