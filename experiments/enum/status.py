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

if __name__ == '__main__':

	print(Status.NONE) # -> Status.NONE
	print(Status.(0)) # -> Status.NONE

	print(Status.NONE.value) # -> "NONE"
	print(f'{Status.NONE==0}')

	print(f'Status in Status: {"SUCCESS" in [Status.SUCCESS, Status.NONE]}')
	result1 = 0