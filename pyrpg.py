''' pyrpg/pyrpg.py

    Called from:
    -> None (init module)

    Aim:
    -> Starts pyrpg.core.main.init() function which initiates pygame and starts the game.

    Usage:
    -> Run the pyrpg game

    Notes:

    Examples:
'''

import pyrpg.main

pyrpg.main.init(state='GAME', cons_enabled=True)