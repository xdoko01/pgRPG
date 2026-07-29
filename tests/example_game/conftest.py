"""Make the example game's own packages importable.

At runtime `python example_game/game.py` puts example_game/ on sys.path[0]
automatically, which is why engine code can import `core.components.*` and
`core.processors.*`. Tests are launched from the repo root, so that entry has to
be added explicitly before any test here imports game modules.
"""

import os
import sys

_EXAMPLE_GAME = os.path.abspath("example_game")

if _EXAMPLE_GAME not in sys.path:
    sys.path.insert(0, _EXAMPLE_GAME)
