'''Classes implementing the behavior tree functionality

Behavior tree is a tree where the leafs (class Behavior) represents actions and
conditions performed by the game scripts and other/upper nodes represent the
logic.
'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

import sys

from enum import Enum
from pyrpg.functions import str_to_class, translate, get_dict_from_json

class TreeNode:
    '''Basic class representing the behavior tree's node'''
    
    class Status(Enum):
        '''Class representing possible statuses of the TreeNode'''

        NONE = 'NONE'
        RUNNING = -1 # due to compatibility with commands written for Brain
        SUCCESS = 0  # due to compatibility with commands written for Brain
        FAILURE = 'FAILURE'

    __slots__ = ['name', 'parent', 'children', 'status', 'blackboard']

    def __init__(self, name: str, parent=None, blackboard=None):
        '''Create a new behavior tree node. Every node must have at least a name.

            :param name: Mandatory name of the behavior tree node
            :type name: str

            :param parent: Reference to parent node. Can be None, in case of root node.
            :type parent: TreeNode or None

            :param blackboard: Reference to instance holding information about the context of the
                whole behavior tree.
            :type blackboard: Blackboard
        '''
        self.name = name
        self.parent = parent
        self.blackboard = blackboard
        self.children = None
        self.status = TreeNode.Status.NONE # Create node without status

    def __str__(self) -> str:
        '''String representation of TreeNode'''
        return f'{self.name}, Type: "{self.__class__.__name__}", Status: "{self.status}"'

    def _set_status(self, status) -> None:
        '''Method logging changes of TreeNode statuses'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Original status: "{self.status}" -> New status "{status}"')
        self.status = status

    def is_child(self) -> bool:
        '''Returns True if the TreeNode is not root'''
        return True if self.parent is not None else False

    def process(self) -> None:
        '''Method called everytime the TreeNode is ticked.
        Calls on_init() function in case if ticked for the first time.'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting process() function')

        # If this is the first time the TreeNode is called, run the init function
        if self.status == TreeNode.Status.NONE:
            self.on_init()

    def on_init(self) -> None:
        '''Method called when the TreeNode is ticked for the first time (in status None).

        Called the first time a node is visited by its parent during its parents execution. 
        For example a sequence will call this when its the node’s turn to be processed. It will 
        not be called again until the next time the parent node is fired after the parent has 
        finished processing and returned a result to its parent. This function is used to 
        initialise the node and start the action the node represents. Using our walk example, 
        it will retrieve the parameters and perhaps initiate the pathfinding job.
        '''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting on_init() function')

        # Change status after first tick to RUNNING
        self._set_status(TreeNode.Status.RUNNING)

    def on_completion(self, result) -> None:
        '''Method called when the TreeNode returns final result (SUCCESS or FAILURE).'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting on_completion() function')

        assert result in [TreeNode.Status.FAILURE,TreeNode.Status.SUCCESS]

        if result == TreeNode.Status.FAILURE:
            self.on_failure()
        if result == TreeNode.Status.SUCCESS:
            self.on_success()

    def on_success(self) -> None:
        '''Method called when the TreeNode returns final result (SUCCESS).'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting on_success() function')

        # Set status to success
        self._set_status(TreeNode.Status.SUCCESS)

    def on_failure(self) -> None:
        '''Method called when the TreeNode returns final result (FAILURE).'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting on_failure() function')

        # Set status to failure
        self._set_status(TreeNode.Status.FAILURE)

    def is_finished(self) -> bool:
        return True if self.status in [TreeNode.Status.SUCCESS, TreeNode.Status.FAILURE] else False

    def is_running(self) -> bool:
        return True if self.status in TreeNode.Status.RUNNING else False

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

    __slots__ = ['name', 'parent', 'children', 'status', 'blackboard', 'command']

    def __init__(self, name, parent=None, blackboard=None, **kwargs):

        # Run TreeNode constructor
        super().__init__(name=name, parent=parent, blackboard=blackboard)

        # Behavior must have command representing action or condition
        self.command = kwargs['command']

    def process(self) -> None:
        '''This is called every tick of the behaviour tree while the node is processing. If this 
        function returns Success or Failure, then its processing will end and the result passed 
        to its parent. If it returns Running it will be reprocessed next tick, and again and again 
        until it returns a Success or Failure. In the Walk example, it will return Running until 
        the pathfinding either succeeds or fails.
        '''
        # Call TreeNode process function - calls on_init when it is the first call of the Node
        super().process()

        # Return the list with command name and command parameters
        return self.command

    def on_init(self) -> None:
        '''This method is called when the Behavior is ticked for the first time'''

        # Call TreeNode init function - sets status to RUNNING
        super().on_init()

        # Notify the blackboard that this Behavior is the running behavior leaf
        self.blackboard.set_running_behavior(self)

        # TODO - here i can return some init command that can be put into the command
        # queue in order to initiate some value on the blackboard
        # return self.init_cmd

    def on_completion(self, result: TreeNode.Status) -> None:
        '''Function is called when the status of the node is set to SUCCESS or FAILURE'''

        # Call TreeNode super class method on_completion() - updates the status of the TreeNode to SUCCESS or FAILURE
        super().on_completion(result)

        # Reset the running node reference - Behavior is no longe running
        self.blackboard.set_running_behavior(None)

        # Notify the upper parent node about the result
        self.parent.notify_from_child(result=result)

    def set_result(self, result: TreeNode.Status) -> None:
        '''Callback from BTree component and PerformCommandProcessor - Sets the result of the Behavior. 
        The Command manager calls BTree component function process_result. 
        The function then calls this set_result function. All of that 
        to remain compatible with Brain component.
        '''

        # Never set status back to NONE
        assert result != TreeNode.Status.NONE

        if result != TreeNode.Status.RUNNING:
            # The real change of the node status is done in on_success, on_failure methods
            # that are called from on_completion
            self.on_completion(result)

class Composite(TreeNode):
    '''A composite node is a node that can have one or more children.
    They will process one or more of these children in either a first 
    to last sequence or random order depending on the particular composite
    node in question, and at some stage will consider their processing complete 
    and pass either success or failure to their parent, often determined 
    by the success or failure of the child nodes. 
    
    During the time they are processing children, they will continue to return 
    Running to the parent.'''

    __slots__ = ['name', 'parent', 'children', 'status', 'blackboard', 
                'child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None, blackboard=None):
        '''Create instance of composite node with children'''

        # Call TreeNode constructor
        super().__init__(name=name, parent=parent, blackboard=blackboard)
        
        self.children = []

        # Which child idx is currently in process
        self.child_running_idx = None 

        # Keeping the amount of children for easier manipulation
        self.no_of_children = 0

    def add_child(self, child: TreeNode) -> None:
        '''Add new child node to the Composite'''
        self.children.append(child)
        self.no_of_children += 1
    
    def notify_from_child(self, result: TreeNode.Status) -> None:
        '''Notification about the result from child node.'''
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Starting notify_from_child({result}) function from child idx "{self.child_running_idx}"')

    def on_init(self) -> None:
        '''This method is called when the Sequence is ticked for the first time'''

        # Call TreeNode init function - sets status to RUNNING
        super().on_init()

        # Set the index to the first child
        self.child_running_idx = 0 

    def on_completion(self, result: TreeNode.Status) -> None:
        '''Method called when the Composite returns final result (SUCCESS or FAILURE).'''

        # Call TreeNode on_completion function - calls on_failure or on success
        super().on_completion(result)

    def on_failure(self) -> None:
        '''Method called when the Composite returns final result (FAILURE).'''
        
        # Call TreeNode on_failure function - sets status to FAILURE
        super().on_failure()

        # Recursivelly call the parent amd notify it about the result
        if self.is_child(): self.parent.notify_from_child(result=TreeNode.Status.FAILURE)

    def on_success(self) -> None:
        '''Method called when the Composite returns final result (SUCCESS).'''

        # Call TreeNode on_failure function - sets status to SUCCESS
        super().on_success()

        # Recursivelly call the parent amd notify it about the result
        if self.is_child(): self.parent.notify_from_child(res=TreeNode.Status.SUCCESS)

class Sequence(Composite):
    '''Runs each child in sequence, returning failure at the time
    any of the children fail and returning the success if every child
    returned a successful status. Sequence is analoguous to AND gate.'''

    __slots__ = ['name', 'parent', 'children', 'status', 'blackboard', 
                'child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None, blackboard=None, **kwargs):
        '''Create instance of Sequence node'''

        # Run Composite constructor
        super().__init__(name, parent=parent, blackboard=blackboard)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and 
        to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Calling process() on child with idx "{self.child_running_idx}"')
        return self.children[self.child_running_idx].process()

    def notify_from_child(self, result: TreeNode.Status) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).'''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports success and there are more children to process, continue running
        # on the next child
        if result == TreeNode.Status.SUCCESS and self.child_running_idx < self.no_of_children - 1:
            self.child_running_idx += 1
            logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Moving to the next child idx "{self.child_running_idx}"')

        # Otherwise complete the Sequence
        else:
            # Call the super-class method - calls either on_failure or on_success methods
            self.on_completion(result)

class Selector(Composite): 
    '''Selector will return a success if any of its children succeed and not process 
    any further children. It will fail if all children fail. This means a selector is 
    analagous with an OR gate.'''

    __slots__ = ['name', 'parent', 'children', 'status', 'blackboard', 
                'child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None, blackboard=None, **kwargs):
        '''Create instance of Selector node with children'''

        # Call Composite constructor
        super().__init__(name, parent=parent, blackboard=blackboard)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Calling process() on child with idx "{self.child_running_idx}"')
        return self.children[self.child_running_idx].process()
    
    def notify_from_child(self, result: TreeNode.Status) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).'''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports failure and there are more children to process, continue running
        # on the next child
        if result == TreeNode.Status.FAILURE and self.child_running_idx < self.no_of_children - 1:
            self.child_running_idx += 1
            logger.debug(f'{self.__class__.__name__} - {self.name} - {self.status}: Moving to the next child idx "{self.child_running_idx}"')

        # Otherwise complete the Selector
        else:
            # Call the super-class method - calls either on_failure or on_success methods
            self.on_completion(result)

class Decorator(TreeNode):
	'''A decorator node, like a composite node, can have a child node. 
	Unlike a composite node, they can specifically only have a single child. 
	Their function is either to transform the result they receive from their 
	child node's status, to terminate the child, or repeat processing of the child, 
	depending on the type of decorator node.'''
	pass

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
    '''Class representing the data structure where the nodes can share information
    about the context of the whole tree logic.'''

    __slots__ = ['running_behavior', 'blackboard']

    def __init__(self, blackboard: dict={}):
        '''Create the blackboard filled with input data'''
        
        # Pointer to the currently running Behavior leaf node representing some action
        self.running_behavior = None

        # Shared dictionary where all tree nodes can store/read data
        self.blackboard = blackboard

    def set_running_behavior(self, node: Behavior|None) -> None:
        '''Set the running Behavior leaf node. This value is used not to go through the
        whole btree everytime when searching the behavior for execution.
        '''
        logger.debug(f'{self.__class__.__name__}: Setting running_behavior from "{self.running_behavior}" to "{node}"')
        self.running_behavior = node

def create_tree(parent: TreeNode, json_tree: dict, blackboard: Blackboard) -> TreeNode:
    '''Create behavior tree from json definition'''

    # First substitute the parameters with the values from the blackboard
    # stored in self.blackboard.blackboard
    json_tree_translated = translate(trans_dict=blackboard.blackboard, value=json_tree)

    node_class = str_to_class(module=sys.modules[__name__], class_name=json_tree_translated['type'])
    node_name = json_tree_translated['name']
    node_cmd = json_tree_translated.get('command', None)

    logger.debug(f'Creating TreeNode: class="{node_class}", name="{node_name}", command="{node_cmd}"')
    node = node_class(name=node_name, parent=parent, blackboard=blackboard, command=node_cmd)

    json_children = json_tree_translated.get('children', [])

    for json_child in json_children:
        # in case child is a template - path to the json or YAML file
        # read the subtree from the file
        if isinstance(json_child, str):
            json_child = get_dict_from_json(json_child)
        
        result = create_tree(parent=node, json_tree=json_child, blackboard=blackboard)
        node.add_child(result)
    
    return node

def print_tree(node: TreeNode, depth: int=0) -> None:
    '''Print the behavior tree on the console'''

    offset = depth * '>>'
    print(f'{offset}{node}')
    
    for child in (node.children or []):
        print_tree(node=child, depth=depth+1)


def tick(root_node: TreeNode, blackboard: Blackboard) -> None:
    '''This will be the processor eventually'''
    # TODO -this condition should go directly to process function probably
    # only call if the tree has not finished yet
    if root_node.status not in [TreeNode.Status.SUCCESS, TreeNode.Status.FAILURE]:

        # if some node is RUNNING, execute him directly
        if blackboard.running_behavior is not None:
            blackboard.running_behavior.process()
        # else search for some next leaf node to run
        else:
            root_node.process()

if __name__ == "__main__":

    b_tree_data_with_templates = {
    "blackboard": {
        "$target": "player01"
    },
    "tree": {
            "type": "Selector",
            "name": "AI Root",
            "children": [
                "experiments/bt/chase_player.json", # Sub-tree from json file with parameters - first the parameter is substituted by blackboard value
                "experiments/bt/patrol.json",		 # Sub-tree from json
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
                            "cmd": ["some_script_name_and_path", {"face_entity": "$target"}]
                        },
                        {
                            "type": "Behavior",
                            "name": "BTT_ChasePlayer",
                            "cmd": ["some_script_name_and_path", {"face_entity": "$target"}]

                        },
                        {
                            "type": "Behavior",
                            "name": "Move To",
                            "cmd": ["some_move_to_script", {"position": "$targetPosition"}]
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
    
    bb = Blackboard(blackboard=b_tree_data('blackboard', {}))

    # Create a tree with the root - no templates for sub-trees
    root_node = create_tree(parent=None, json_tree=b_tree_data['tree'], blackboard=bb)

    # Create a tree with the root - templates for some sub-trees
    #root_node_t = BehaviorTree(json_tree=b_tree_data_with_templates)

    print(root_node)
    #print(bt_w_t.root.children)
    
    print_tree(node=root_node)

    # Lets tick 25 times
    #for i in range(50):
    #    print(f'**** TICK no. {i} **********************')
    #    bt_w_t.tick()
    #    
    #print('*** SHOW TREE - START ***')
    #bt.print_tree()
    #print('*** SHOW TREE - END ***')
