''' pyrpg/pyrpg/main.py - called from pyrpg/pyrpg.py 

	Called from:
	-> pyrpg/pyrpg.py (init module)

	Aim:
	-> Loads configuration by importing the config module	
	-> Initiates game engine module and runs the game.

	Usage:
	-> Run the pyrpg game
	
	Notes:
	
	Examples:

'''

import logging

# Load and store config dict as cfg.config by importing
# Here necessary for loading logger configuration
import pyrpg.constants.config as cfg 

# Load whole engine module
import pyrpg.core.engine as engine

# Create local logger
logger = logging.getLogger(__name__)

def main():
	''' Call engine that handles the game itself
	'''

	# Initiate global engine variables
	engine.init_globals()
	
	# Load game from the quest - no parameter marks that init quest is in config file
	engine.load_game()

	# Show Game info - what has been loaded so far
	print(engine.game_info())

	# Enter the main loop
	engine.run()

logger.info('Game main.py module successfully loaded/imported.')