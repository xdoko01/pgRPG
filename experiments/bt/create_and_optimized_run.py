import sys
import json, re
from pathlib import Path
from random import choice
from enum import Enum

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

class TreeNode:
	'''Basic class representing the behavior tree node.'''
	
	class Status(Enum):
		'''Class representing possible statuses of the TreeNode'''

		NONE = 'NONE'
		RUNNING = 'RUNNING'
		SUCCESS = 'SUCCESS'
		FAILURE = 'FAILURE'

	__slots__ = ['name', 'parent', 'children', 'status', 'blackboard']

	def __init__(self, name: str, parent=None, children=None, blackboard=None):
		'''Create a new behavior tree node. Every node must have at least a name.

			:param name: Mandatory name of the behavior tree node
			:type name: str

			:param parent: Reference to parent node. Can be None, in case of root node.
			:type parent: TreeNode or None

			:param children: None in case of leaf node or list of references to the TreeNodes
			:type children: list of TreeNodes or None

			:param blackboard: Reference to instance holding information about the context of the
				whole behavior tree.
			:type blackboard: Blackboard
		'''

		print(f'Running TreeNode __init__()')
		self.name = name
		self.parent = parent
		self.children = children
		self.blackboard = blackboard
		self.status = TreeNode.Status.NONE # Create node without status
		print(f'Finishing TreeNode __init__(). Status set to {self.status}')


	def init(self):
		'''Method called when the TreeNode is ticked for the first time (in status None).'''
		pass

	def process(self):
		'''Method called everytime the TreeNode is ticked.'''
		pass

	def close(self):
		'''Method called when the TreeNode returns final result (SUCCESS, FAILURE).'''
		pass

	def __str__(self):
		return f'{self.name}, Type: {self.__class__.__name__}, Status: {self.status}'

class Composite(TreeNode):
	'''A composite node is a node that can have one or more children.
	They will process one or more of these children in either a first 
	to last sequence or random order depending on the particular composite
	node in question, and at some stage will consider their processing complete 
	and pass either success or failure to their parent, often determined 
	by the success or failure of the child nodes. 
	
	During the time they are processing children, they will continue to return 
	Running to the parent.'''
	
	def __init__(self, name, parent=None, children=None, blackboard=None):
		
		print(f'Running Composite __init__()')

		super().__init__(name=name, parent=parent, children=children, blackboard=blackboard)
		
		if self.children is None: self.children = []

		self.child_running_idx = None # which child idx is currently in process

	def add_child(self, child: TreeNode):
		self.children.append(child)


class Decorator(TreeNode):
	'''A decorator node, like a composite node, can have a child node. 
	Unlike a composite node, they can specifically only have a single child. 
	Their function is either to transform the result they receive from their 
	child node's status, to terminate the child, or repeat processing of the child, 
	depending on the type of decorator node.'''
	pass

class Behavior(TreeNode):
	'''These are the lowest level node types, and are incapable of having 
	any children. Leafs (behaviors) are however the most powerful of node types, as these 
	will be defined and implemented by your game to do the game specific or character 
	specific tests or actions required to make your tree actually do useful stuff.

	An example of this, as used above, would be Walk. A Walk leaf node would make
	a character walk to a specific point on the map, and return success or failure 
	depending on the result.

	Since you can define what leaf nodes are yourself (often with very minimal code), 
	they can be very expressive when layered on top of composite and decorators, 
	and allow for you to make pretty powerful behavior trees capable of quite complicated 
	layered and intelligently prioritized behaviour.'''
	
	def __init__(self, name, parent=None, blackboard=None):
		print(f'Running Behavior __init__()')

		super().__init__(name=name, parent=parent, blackboard=blackboard)
		

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
		res = choice(
			[
				TreeNode.Status.SUCCESS, 
				TreeNode.Status.FAILURE,
				TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING,
				TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING, TreeNode.Status.RUNNING
			]
		)

		self.status = res
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status} - process function returns {res}')
		
		# Just tell the blackboard that I am the only running node and they should call me directly
		# I do not need to inform anybody that I am running. Only when I stop with some other status.
		if res == TreeNode.Status.RUNNING:
			self.blackboard.running_behavior = self
		# Now, I am not running anymore and hence I need to inform all the parent nodes about my new status.
		# So that the tree can find the new running node to run.
		else:
			self.blackboard.running_behavior = None # reset
			self.parent.notify_from_child(res=res)


class Sequence(Composite):
	'''Runs each child in sequence, returning failure at the time
	any of the children fail and returning the success if every child
	returned a successful status. Sequence is analoguous to AND gate.'''

	def __init__(self, name, parent=None, children=None, blackboard=None):
		print(f'Running Sequence __init__()')
		super().__init__(name, parent=parent, children=children, blackboard=blackboard)
	
	def process(self):
		'''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: starting process() function')

		# if status of the sequence is None, call init function, set the child and set status to RUNNING
		if self.status == TreeNode.Status.NONE:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: running init(), setting child idx to 0')

			self.init()
			self.child_running_idx = 0 # expecting that there are some children
			self.status = TreeNode.Status.RUNNING
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: status changed.')


		# if some child is already running, pass processing to that Node
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: running the process() on child {self.children[self.child_running_idx].name}')
		self.children[self.child_running_idx].process()


	def notify_from_child(self, res):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}:  process() on child {self.children[self.child_running_idx].name} returned {res} status')

		# if child returns FAILURE then set sequence to FAILURE and run close and also return failure above
		if res == TreeNode.Status.FAILURE:
			self.status = TreeNode.Status.FAILURE
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: status changed. Returning {self.status}')
			self.close()
			if self.parent is not None: self.parent.notify_from_child(res=TreeNode.Status.FAILURE)
		
		# if child returns SUCCESS then continue with the next child next tick
		elif res == TreeNode.Status.SUCCESS:
			
			# if it was the last child
			if self.child_running_idx == len(self.children) - 1:
				# fail the whole selector
				self.status = TreeNode.Status.SUCCESS
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: status changed. Returning {self.status}')
				self.close()
				if self.parent is not None: self.parent.notify_from_child(res=TreeNode.Status.SUCCESS)

			
			# else point to the next child
			else:
				# increase idx
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: moving on to the next child')
				self.child_running_idx += 1
				# do nothing return 'RUNNING'

		else:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: child is still in RUNNING state')
			# do nothing return 'RUNNING'


	def init(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}:  init() function executed')

	def close(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}:  close() function executed')


class Selector(Composite):
	'''selector will return a success if any of its children succeed and not process 
	any further children. It will fail if all children fail. This means a selector is 
	analagous with an OR gate.'''
	
	def __init__(self, name, parent=None, children=None, blackboard=None):
		print(f'Running Selector __init__()')
		super().__init__(name, parent=parent, children=children, blackboard=blackboard)
	
	def process(self):
		'''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: starting process() function')

		# if status of the composite is None, call init function, set the child and set status to RUNNING
		if self.status == TreeNode.Status.NONE:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: running init(), setting child idx to 0')

			self.init()
			self.child_running_idx = 0 # expecting that there are some children
			self.status = TreeNode.Status.RUNNING
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: status changed.')


		# if some child is already running, pass processing to that Node
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: running the process() on child {self.children[self.child_running_idx].name}')
		self.children[self.child_running_idx].process()

	def notify_from_child(self, res):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}:  process() on child {self.children[self.child_running_idx].name} returned {res} status')

		# if child returns SUCCESS then set selector to SUCCESS and run close and also return success above
		if res == TreeNode.Status.SUCCESS:
			self.status = TreeNode.Status.SUCCESS
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: state changed. Returning {self.status}')
			self.close()
			if self.parent is not None: self.parent.notify_from_child(res=TreeNode.Status.SUCCESS)
		
		# if child returns FAILURE then continue with the next child next tick
		elif res == TreeNode.Status.FAILURE:
			
			# if it was the last child
			if self.child_running_idx == len(self.children) - 1:
				# fail the whole selector
				self.status = TreeNode.Status.FAILURE
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: status changed. Returning {self.status}')
				self.close()
				if self.parent is not None: self.parent.notify_from_child(res=TreeNode.Status.FAILURE)
			
			# else point to the next child
			else:
				# increase idx
				print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: moving on to the next child')
				self.child_running_idx += 1
				# notify nothing return 'RUNNING'

		else:
			print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: child is still in RUNNING status')
			# notify nothing return 'RUNNING'

	def init(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: init() function executed')

	def close(self):
		print(f'{self.name}, type: {self.__class__.__name__}, status: {self.status}: close() function executed')


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

class Blackboard:

	def __init__(self, blackboard={}):
		self.running_behavior = None # point to the currently running node
		self.blackboard=blackboard

class BehaviorTree:

	def __init__(self, json_tree):
		self.blackboard = Blackboard(blackboard=json_tree.get('blackboard', {}))
		self.root = self.create_tree(parent=None, json_tree=json_tree['tree'])


	def create_tree(self, parent, json_tree):
		'''Create behavior tree from json definition'''

		# First substitute the parameters with the values from the blackboard
		# stored in self.blackboard.blackboard
		json_tree_translated = translate(self.blackboard.blackboard, json_tree)

		node_class = str_to_class(json_tree_translated['type'])
		node_name = json_tree_translated['name']

		node = node_class(name=node_name, parent=parent, blackboard=self.blackboard)

		json_children = json_tree_translated.get('children', [])

		for json_child in json_children:
			# in case child is a template - path to the json or YAML file
			# read the subtree from the file
			if isinstance(json_child, str):
				json_child = get_dict_from_json(json_child)
			
			result = self.create_tree(parent=node, json_tree=json_child)
			node.add_child(result)
		
		return node

	def print_tree(self, node=None, depth=0):
		
		if node is None: node = self.root

		offset = depth * '>>'
		print(f'{offset} {node.status}')
		
		for child in (node.children or []):
			self.print_tree(node=child, depth=depth+1)


	def tick(self):
		# TODO -this condition should go directly to process function probably
		# only call if the tree has not finished yet
		if self.root.status not in [TreeNode.Status.SUCCESS, TreeNode.Status.FAILURE]:

			# if some node is RUNNING, execute him directly
			if self.blackboard.running_behavior is not None:
				self.blackboard.running_behavior.process()
			# else search for some next leaf node to run
			else:
				self.root.process()

if __name__ == "__main__":

	b_tree_data_with_templates = {
	"blackboard": {
		"$target": "player01"
	},
	"tree": {
			"type": "Selector",
			"name": "AI Root",
			"children": [
				"experiments/bt/chase_player($target)", # Sub-tree from json file with parameters - first the parameter is substituted by blackboard value
				"experiments/bt/patrol()",		 # Sub-tree from json
				{
					"type": "Behavior",
					"name": "Wait"
				}
			]
		}
	}

	b_tree_data = {
		'blackboard': {},
		'tree': {
			"type": "Selector",
			"name": "AI Root",
			"children": [
				{
					"type": "Sequence",
					"name": "Chase Player",
					"children": [
						{
							"type": "Behavior",
							"name": "Rotate to face BB entry",
							"script": ["some_script_name_and_path", {"face_entity": "$target"}]
						},
						{
							"type": "Behavior",
							"name": "BTT_ChasePlayer"
						},
						{
							"type": "Behavior",
							"name": "Move To",
							"script": ["some_move_to_script", {"position": "$targetPosition"}]
						}
					]
				},
				{
					"type": "Sequence",
					"name": "Patrol",
					"children": [
						{
							"type": "Behavior",
							"name": "BTT_FindRandomPatrol"
						},
						{
							"type": "Behavior",
							"name": "Move To"
						},
						{
							"type": "Behavior",
							"name": "Wait",
							"script": ["wait_script", {"time_ms": 1000}]
						}
					]
				},
				{
					"type": "Behavior",
					"name": "Wait"
				}
			]
		}
	}
	
	# Create a tree with the root - no templates for sub-trees
	bt = BehaviorTree(json_tree=b_tree_data)

	# Create a tree with the root - templates for some sub-trees
	bt_w_t = BehaviorTree(json_tree=b_tree_data_with_templates)

	print(bt_w_t.root)
	print(bt_w_t.root.children)
	
	bt.print_tree()

	# Lets tick 25 times
	for i in range(50):
		print(f'**** TICK no. {i} **********************')
		bt_w_t.tick()
		
	print('*** SHOW TREE - START ***')
	bt.print_tree()
	print('*** SHOW TREE - END ***')
