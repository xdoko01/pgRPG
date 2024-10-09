'''I need to be able to return and process all these options

'SUCCESS' == 0 == Status.SUCCESS = Status('SUCCESS')
'RUNNING' == -1 == Status.RUNNING = Status('RUNNING')
'''
from enum import Enum

class Status(Enum):
	'''Class representing possible statuses of the TreeNode'''

	NONE = 0
	RUNNING = 'RUNNING' # due to compatibility with commands written for Brain
	SUCCESS = 'SUCCESS'  # due to compatibility with commands written for Brain
	FAILURE = 'FAILURE'

class OtherStatus(Enum):
	BCM = 'Hello'
	DFS = 1

from collections import namedtuple

PathfindComb = namedtuple('PathfindComb',('method', 'checkpoint', 'inc_first'))

class PathfindOption(Enum):
	BFS = PathfindComb('BFS', False, False)
	BFS_CHECKPOINTS = PathfindComb('BFS_CHECKPOINTS', True, False)
	BFS_CHECKPOINTS_W_FIRST = PathfindComb('BFS_CHECKPOINTS_W_FIRST', True, True)


if __name__ == '__main__':

	print(Status.NONE) # -> Status.NONE

	print(Status.NONE.value) # -> "NONE"
	print(f'{Status.NONE==0}')

	print(f'Status in Status: {"SUCCESS" in [Status.SUCCESS, Status.NONE]}')
	result1 = 0

	print(OtherStatus.BCM.value)
	print(OtherStatus.DFS.name)
	print(OtherStatus['BCM']) #!!!

	print(type(PathfindOption.BFS.name))
	print(PathfindOption.BFS.value.checkpoint)
	print(PathfindOption._member_names_)
	
	# re-casting to strings
	from functools import reduce
	cmd_results = [Status.FAILURE, Status.SUCCESS]
	res = reduce(lambda x, y: x+y, map(lambda cs: cs.value[0], cmd_results))
	print(res)

	r = "SUCCESS"
	print(Status[r])

	FILEPATHS = {
		"FONT_PATH" : "resources/fonts/",
		"FRAME_PATH" : "resources/frames/",
		"DIALOG_PATH" : "resources/dialogs/",
		"MODEL_PATH" : "resources/models/",
		"IMAGE_PATH" : "resources/images/",
		"SCENE_PATH" : "resources/scenes/",
		"ENTITY_PATH" : "resources/entities/",
		"BTREE_PATH" : "resources/btrees/",
		"MAP_PATH" : "resources/maps/",
		"SOUND_PATH" : "resources/sounds/",
		"LOG_PATH" : "logs/",
		"SAVE_PATH" : "save/",
		"MENU_BACKGROUND_PATH" : "resources/images/menu_background/waterfall/"
	}

	class Filepath(Enum):
		FONT_PATH = "resources/fonts/"
		FRAME_PATH = "resources/frames/"

	print(f'{Filepath.FONT_PATH.value}')