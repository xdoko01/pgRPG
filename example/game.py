# Path to the pyrpg engine module
pyrpg_path = '../pyrpg'

# Bring pyrpg package onto the path
import sys, os
from pathlib import Path

print(f'Path before change: {sys.path}')
#sys.path.append(os.path.abspath(os.path.join('..', 'pyrpg')))
sys.path.append(os.path.abspath(Path(pyrpg_path)))
print(f'Path after change: {sys.path}')

# Now do your import
from pyrpg.main import init

console = True
filepath = 'new/tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_template.jsonc'

init(console=console, filepath=filepath, timed=False)
