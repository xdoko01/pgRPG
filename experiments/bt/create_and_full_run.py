import sys
import json, re
from pathlib import Path
from random import choice

def get_dict_from_json(filepath: Path) -> dict:
    ''' Returns dictionary based of json file with C-style 
    comments removed.

    Parameters:
        :param filepath: Path to the json file
        :type filepath: Path

        :returns: Dictionary of json data
    '''

    try:
        with open(filepath, 'r') as json_file:
            json_data = json_file.read()
            return json.loads(re.sub("//.*","", json_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
    except FileNotFoundError:
        raise

def str_to_class(str):
	'''Translate class name to class'''
	return getattr(sys.modules[__name__], str)

class Node:

	def __init__(self, parent, blackboard, tree):
		self.parent = parent
		self.blackboard = blackboard
		self.name = tree['name']
		self.state = None
		

	def init(self):
		pass

	def process(self):
		pass

	def close(self):
		pass

class Composite(Node):
	'''A composite node is a node that can have one or more children.
	They will process one or more of these children in either a first 
	to last sequence or random order depending on the particular composite
	node in question, and at some stage will consider their processing complete 
	and pass either success or failure to their parent, often determined 
	by the success or failure of the child nodes. 
	
	During the time they are processing children, they will continue to return 
	Running to the parent.'''
	
	def __init__(self, parent, blackboard, *args, **kwargs):

		super().__init__(parent, blackboard, *args, **kwargs)
		self.children = []
		self.child_running_idx = None # which child idx is currently in process

	def add_child(self, child: Node):
		self.children.append(child)


class Decorator(Node):
	'''A decorator node, like a composite node, can have a child node. 
	Unlike a composite node, they can specifically only have a single child. 
	Their function is either to transform the result they receive from their 
	child node's status, to terminate the child, or repeat processing of the child, 
	depending on the type of decorator node.'''
	pass

class Leaf(Node):
	'''These are the lowest level node type, and are incapable of having 
	any children. Leafs are however the most powerful of node types, as these 
	will be defined and implemented by your game to do the game specific or character 
	specific tests or actions required to make your tree actually do useful stuff.

	An example of this, as used above, would be Walk. A Walk leaf node would make
	a character walk to a specific point on the map, and return success or failure 
	depending on the result.

	Since you can define what leaf nodes are yourself (often with very minimal code), 
	they can be very expressive when layered on top of composite and decorators, 
	and allow for you to make pretty powerful behavior trees capable of quite complicated 
	layered and intelligently prioritized behaviour.'''
	
	def init(self):
		'''Called the first time a node is visited by its parent during its parents execution. 
		For example a sequence will call this when its the node’s turn to be processed. It will 
		not be called again until the next time the parent node is fired after the parent has 
		finished processing and returned a result to its parent. This function is used to 
		initialise the node and start the action the node represents. Using our walk example, 
		it will retrieve the parameters and perhaps initiate the pathfinding job.'''
		pass

	def process(self):
		'''This is called every tick of the behaviour tree while the node is processing. If this 
		function returns Success or Failure, then its processing will end and the result passed 
		to its parent. If it returns Running it will be reprocessed next tick, and again and again 
		until it returns a Success or Failure. In the Walk example, it will return Running until 
		the pathfinding either succeeds or fails.'''
		res = choice(['SUCCESS', 'RUNNING', 'RUNNING', 'RUNNING', 'FAILURE'])
		self.state = res
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state} - process function returns {res}')
		return res


class Sequence(Composite):
	'''Runs each child in sequence, returning failure at the time
	any of the children fail and returning the success if every child
	returned a successful status. Sequence is analoguous to AND gate.'''
	def __init__(self, parent, blackboard, *args, **kwargs):
		super().__init__(parent, blackboard, *args, **kwargs)
	
	def process(self):
		
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: starting process() function')

		# if status of the sequence is None, call init function, set the child and set status to RUNNING
		if self.state is None:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: running init(), setting child idx to 0')

			self.init()
			self.child_running_idx = 0 # expecting that there are some children
			self.state = 'RUNNING'
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: status changed.')


		# if some child is already running, pass processing to that Node
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: running the process() on child {self.children[self.child_running_idx].name}')
		res = self.children[self.child_running_idx].process()
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}:  process() on child {self.children[self.child_running_idx].name} returned {res} status')

		# if child returns FAILURE then set sequence to FAILURE and run close and also return failure above
		if res == 'FAILURE':
			self.state = 'FAILURE'
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: status changed. Returning {self.state}')
			self.close()
			return 'FAILURE'
		
		# if child returns SUCCESS then continue with the next child next tick
		elif res == 'SUCCESS':
			
			# if it was the last child
			if self.child_running_idx == len(self.children) - 1:
				# fail the whole selector
				self.state = 'SUCCESS'
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: status changed. Returning {self.state}')
				self.close()
				return 'SUCCESS'
			
			# else point to the next child
			else:
				# increase idx
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: moving on to the next child')
				self.child_running_idx += 1
				return 'RUNNING'

		else:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: child is still in RUNNING state')
			return 'RUNNING'


	def init(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}:  init() function executed')

	def close(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}:  close() function executed')

class Selector(Composite):
	'''selector will return a success if any of its children succeed and not process 
	any further children. It will fail if all children fail. This means a selector is 
	analagous with an OR gate.'''
	
	def __init__(self, parent, blackboard, *args, **kwargs):
		super().__init__(parent, blackboard, *args, **kwargs)
	
	def process(self):
		
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: starting process() function')

		# if status of the composite is None, call init function, set the child and set status to RUNNING
		if self.state is None:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: running init(), setting child idx to 0')

			self.init()
			self.child_running_idx = 0 # expecting that there are some children
			self.state = 'RUNNING'
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: status changed.')


		# if some child is already running, pass processing to that Node
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: running the process() on child {self.children[self.child_running_idx].name}')
		res = self.children[self.child_running_idx].process()
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}:  process() on child {self.children[self.child_running_idx].name} returned {res} state')

		# if child returns SUCCESS then set selector to SUCCESS and run close and also return success above
		if res == 'SUCCESS':
			self.state = 'SUCCESS'
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: state changed. Returning {self.state}')
			self.close()
			return 'SUCCESS'
		
		# if child returns FAILURE then continue with the next child next tick
		elif res == 'FAILURE':
			
			# if it was the last child
			if self.child_running_idx == len(self.children) - 1:
				# fail the whole selector
				self.state = 'FAILURE'
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: status changed. Returning {self.state}')
				self.close()
				return 'FAILURE'
			
			# else point to the next child
			else:
				# increase idx
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: moving on to the next child')
				self.child_running_idx += 1
				return 'RUNNING'

		else:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: child is still in RUNNING status')
			return 'RUNNING'


	def init(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: init() function executed')

	def close(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.state}: close() function executed')


class Inverter(Decorator):
	'''A commonly used example of a decorator is the Inverter, which will 
	simply invert the result of the child. A child fails and it will return 
	success to its parent, or a child succeeds and it will return failure to 
	the parent.'''
	pass

class Succeeder(Decorator):
	'''A succeeder will always return success, irrespective of what the child 
	node actually returned. These are useful in cases where you want to process a 
	branch of a tree where a failure is expected or anticipated, but you don’t want 
	to abandon processing of a sequence that branch sits on. The opposite of this 
	type of node is not required, as an inverter will turn a succeeder into a ‘failer’ 
	if a failure is required for the parent.'''
	pass

class Repeater(Decorator):
	'''A repeater will reprocess its child node each time its child returns a result. 
	These are often used at the very base of the tree, to make the tree to run 
	continuously. Repeaters may optionally run their children a set number of times 
	before returning to their parent.'''
	pass

class RepeatUntilFail(Decorator):	
	'''Like a repeater, these decorators will continue to reprocess their child. 
	That is until the child finally returns a failure, at which point the repeater 
	will return success to its parent.'''
	pass

class BehaviorTree:

	def __init__(self, json_tree):
		self.json_tree = json_tree
		self.root = self.create_tree(parent=None, json_tree=self.json_tree)
		self.blackboard = None 

	def create_tree(self, parent, json_tree):

		node_class = str_to_class(json_tree['type'])

		node = node_class(parent=parent, blackboard=None, tree=json_tree)

		children = json_tree.get('children', [])

		for child in children:
			# in case child is a template - path to the json or YAML file
			# read the subtree from the file
			if isinstance(child, str):
				child = get_dict_from_json(child)
			
			result = self.create_tree(node, child)
			node.add_child(result)
		
		return node

	def tick(self):
		# only call if the tree has not finished yet
		if self.root.state not in ['SUCCESS', 'FAILURE']:
			return self.root.process()

if __name__ == "__main__":

	b_tree_data_with_templates = {
			"type": "Selector",
			"name": "AI Root",
			"children": [
				"experiments/bt/chase_player.json", # Sub-tree from json
				"experiments/bt/patrol.json",		 # Sub-tree from json
				{
					"type": "Leaf",
					"name": "Wait",
					"returns": "SUCCESS"
				}
			]
		}

	b_tree_data = {
			"type": "Selector",
			"name": "AI Root",
			"children": [
				{
					"type": "Sequence",
					"name": "Chase Player",
					"children": [
						{
							"type": "Leaf",
							"name": "Rotate to face BB entry",
							"script": ["some_script_name_and_path", {"face_entity": "$target"}],
							"returns": "SUCCESS"
						},
						{
							"type": "Leaf",
							"name": "BTT_ChasePlayer",
							"returns": "SUCCESS"
						},
						{
							"type": "Leaf",
							"name": "Move To",
							"script": ["some_move_to_script", {"position": "$targetPosition"}],
							"returns": "SUCCESS"
						}
					]
				},
				{
					"type": "Sequence",
					"name": "Patrol",
					"children": [
						{
							"type": "Leaf",
							"name": "BTT_FindRandomPatrol",
							"returns": "FAILURE"
						},
						{
							"type": "Leaf",
							"name": "Move To",
							"returns": "SUCCESS"
						},
						{
							"type": "Leaf",
							"name": "Wait",
							"script": ["wait_script", {"time_ms": 1000}],
							"returns": "FAILURE"
						}
					]
				},
				{
					"type": "Leaf",
					"name": "Wait",
					"returns": "SUCCESS"
				}
			]
		}
	
	# Create a tree with the root - no templates for sub-trees
	bt = BehaviorTree(json_tree=b_tree_data)

	print(bt.root)
	print(bt.root.children)

	# Create a tree with the root - templates for some sub-trees
	bt_w_t = BehaviorTree(json_tree=b_tree_data_with_templates)

	print(bt_w_t.root)
	print(bt_w_t.root.children)

	# Lets tick 25 times
	for i in range(25):
		print(f'**** TICK no. {i} **********************')
		bt_w_t.tick()