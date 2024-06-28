'''Classes implementing the behavior tree functionality

Behavior tree is a tree where the leafs (class Behavior) represents actions and
conditions performed by the game scripts and other/upper nodes represent the
logic.

Use 'python -m pyrpg.core.commands.generators.btree.btree -v' to run
module tests.
'''

# Initiate logging
import logging
logger = logging.getLogger(__name__)

import sys
import pygame

from functools import reduce
from pathlib import Path
from enum import Enum

# BTree must follow all command related protocols
from pyrpg.core.commands import CommandStatus, CommandGenerator, CommandContext, Container
from pyrpg.functions import str_to_class, get_dict_params

class BTreeCommandStatus(Enum):
    '''Mapping of ComandStatus to internal Statuses used in the behavior tree implementation.'''
    NONE = CommandStatus.NONE
    RUNNING = CommandStatus.RUNNING
    SUCCESS = CommandStatus.SUCCESS
    FAILURE = CommandStatus.FAILURE

    @property
    def is_valid(cls) -> bool: return cls in [cls.SUCCESS, cls.FAILURE, cls.RUNNING, cls.NONE]

    @property
    def is_completed(cls) -> bool: return cls in [cls.SUCCESS, cls.FAILURE]

    @property
    def is_failure(cls) -> bool: return cls in [cls.FAILURE]

    @property
    def is_success(cls) -> bool: return cls in [cls.SUCCESS]

    @property
    def is_running(cls) -> bool: return cls in [cls.RUNNING]

class TreeNode:
    '''Basic class representing the behavior tree's node'''

    __slots__ = ['name', '_parent', '_children', '_status', '_depth']

    PRINT_COLOR = {
        BTreeCommandStatus.NONE: "\033[00m", #white
        BTreeCommandStatus.RUNNING: "\033[93m", #yellow
        BTreeCommandStatus.SUCCESS: "\033[92m", #green
        BTreeCommandStatus.FAILURE: "\033[91m" #red
    }

    def __init__(self, name: str, parent=None):
        '''Create a new behavior tree node. Every node must have at least a name.

            :param name: Mandatory name of the behavior tree node
            :type name: str

            :param parent: Reference to parent node. Can be None, in case of root node.
            :type parent: TreeNode or None
        '''
        self.name = name
        self._parent = parent
        self._children = None
        self._status = BTreeCommandStatus.NONE
        self._depth = 0

    def __str__(self) -> str:
        '''String representation of TreeNode'''
        return f'{TreeNode.PRINT_COLOR[self._status]}{self.__class__.__name__} ({self.name}), Status: {self._status}, Depth: {self._depth}\033[00m' # return to white at the end

    def __repr__(self) -> str:
        '''String representation of TreeNode'''
        return f'{self.__class__.__name__} ({self.name}), Status: {self._status}, Depth: {self._depth}'

    def _set_status(self, status: BTreeCommandStatus) -> None:
        '''Method logging changes of TreeNode statuses'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Original status: {self._status} -> New status {status}')
        self._status = status

    def set_none(self) -> None: self._set_status(status=BTreeCommandStatus.NONE)
    def set_running(self) -> None: self._set_status(status=BTreeCommandStatus.RUNNING)
    def set_failure(self) -> None: self._set_status(status=BTreeCommandStatus.FAILURE)
    def set_success(self) -> None: self._set_status(status=BTreeCommandStatus.SUCCESS)

    def _is_status(self, status: BTreeCommandStatus) -> bool:
        '''Method checking the status'''
        return self._status == status

    @property
    def is_none(self) -> bool: return self._is_status(status=BTreeCommandStatus.NONE)

    @property
    def is_running(self) -> bool: return self._is_status(status=BTreeCommandStatus.RUNNING)

    @property
    def is_failure(self) -> bool: return self._is_status(status=BTreeCommandStatus.FAILURE)

    @property
    def is_success(self) -> bool: return self._is_status(status=BTreeCommandStatus.SUCCESS)

    @property
    def is_completed(self) -> bool: return self.is_failure or self.is_success

    @property
    def is_child(self) -> bool: return True if self._parent is not None else False

    @property
    def is_parent(self) -> bool: return True if self._children else False

    def check(self) -> bool:
        '''Return True if the subtree is correct Behavior Tree - all leafs are behaviors with command'''

        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting check() function')

        if self.is_parent:
            # you must have some childred AND all your children must be ok - their check returns True
            #res = (len(self._children) != 0) and reduce(lambda ch1_res, ch2_res: ch1_res and ch2_res, map(lambda ch: ch.check(), self._children))

            has_children = (len(self._children) != 0)
            if not has_children:
                raise InvalidBehaviorTreeNodeError(f'Behavior Tree Node has no children. Node: "{self}"')

            children_ok = reduce(lambda ch1_res, ch2_res: ch1_res and ch2_res, map(lambda ch: ch.check(), self._children))
            if not children_ok:
                raise InvalidBehaviorTreeNodeError(f'Behavior Tree Node childrens are not ok. Node: "{self}"')

            res = has_children and children_ok

        else:
            res = self.check()

            if not res:
                raise InvalidBehaviorTreeNodeError(f'Behavior Tree Node problem. Node: "{self}"')

        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Returning check() function with {res = }')

        return res

    def process(self) -> None:
        '''Method called everytime the TreeNode is ticked.
        Calls on_init() function in case if ticked for the first time.'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting process() function')

        # If this is the first time the TreeNode is called, run the init function
        if self.is_none:
            self.on_init()

    def reset(self) -> None:
        '''Reset any state of the TreeNode back to NONE with all the children'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting reset() function.')
        self.set_none()

        for child in self._children or []:
            child.reset()

    def on_init(self) -> None:
        '''Method called when the TreeNode is ticked for the first time (in status None).

        Called the first time a node is visited by its parent during its parents execution. 
        For example a sequence will call this when its the node’s turn to be processed. It will 
        not be called again until the next time the parent node is fired after the parent has 
        finished processing and returned a result to its parent. This function is used to 
        initialise the node and start the action the node represents. Using our walk example, 
        it will retrieve the parameters and perhaps initiate the pathfinding job.
        '''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting on_init() function')

        # Change status after first tick to RUNNING
        self.set_running()

    def on_completion(self, result: BTreeCommandStatus) -> None:
        '''Method called when the TreeNode returns final result (SUCCESS or FAILURE).'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting on_completion({result}) function')

        try:
            assert result.is_completed
        except AssertionError:
            raise InvalidBTreeCommandStatusError(f'Success or Failure status expected, received: {result}')

        if result.is_failure: self.on_failure()
        if result.is_success: self.on_success()

    def on_success(self) -> None:
        '''Method called when the TreeNode returns final result (SUCCESS).'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting on_success() function')
        self.set_success()

    def on_failure(self) -> None:
        '''Method called when the TreeNode returns final result (FAILURE).'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting on_failure() function')
        self.set_failure()

    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Notification about the result from child node - should be either SUCCESS or FAILURE.'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting notify_from_child({result}) function from child idx ({self.child_running_idx}) - "{self._children[self.child_running_idx].name}"')

        try:
            assert result.is_completed
        except AssertionError:
            raise InvalidBTreeCommandStatusError(f'{result = } is invalid status.')

    def notify_from_child_success(self): self.notify_from_child(result=BTreeCommandStatus.SUCCESS)
    def notify_from_child_failure(self): self.notify_from_child(result=BTreeCommandStatus.FAILURE)

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

    __slots__ = ['command']

    def __init__(self, name: str, command: list, parent=None, **kwargs):
        # Run TreeNode constructor
        super().__init__(name=name, parent=parent)

        # Behavior must have command representing action or condition
        #self.command = kwargs['command']
        self.command = command

    def __str__(self) -> str:
        '''String representation of Behavior TreeNode'''
        return f'{TreeNode.PRINT_COLOR[self._status]}{self.__class__.__name__} ({self.name}), Status: {self._status}, Depth: {self._depth}, Command: {self.command}\033[00m'

    def __repr__(self) -> str:
        '''String representation of BehaviorTreeNode'''
        return f'{self.__class__.__name__} ({self.name}), Status: {self._status}, Depth: {self._depth}, Command: {self.command}'

    def check(self) -> bool:
        '''Check that the behavior node is ok - i.e. has some command assigned'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting Behavior check() function')
        res = self.command is not None
        if not res:
            raise InvalidBehaviorTreeNodeError(f'Behavior Tree Node problem - missing "command" on the behavior node. Node: "{self}"')
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Return from  Behavior check() function: {res =}')
        return res

    def process(self):
        '''This is called every tick of the behaviour tree while the node is processing. If this 
        function returns Success or Failure, then its processing will end and the result passed 
        to its parent. If it returns Running it will be reprocessed next tick, and again and again 
        until it returns a Success or Failure. In the Walk example, it will return Running until 
        the pathfinding either succeeds or fails.
        '''
        # Call TreeNode process function - calls on_init when it is the first call of the Node
        super().process()

        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Returning command {self.command}')
        
        # Return the tuple with action node and command - in order to identify if the action node has changed
        return (self, self.command)

    def on_init(self):
        '''This method is called when the Behavior is ticked for the first time'''

        # Call TreeNode init function - sets status to RUNNING
        super().on_init()

        # Notify the blackboard that this Behavior is the running behavior leaf
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Running behavior init() function')

    def on_completion(self, result: BTreeCommandStatus) -> None:
        '''Function is called when the status of the node is set to SUCCESS or FAILURE'''

        # Call TreeNode super class method on_completion() - updates the status of the TreeNode to SUCCESS or FAILURE
        super().on_completion(result)

        # Reset the running node reference - Behavior is no longer running
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Reseting On completion on node "{self.name}"')

        # Notify the upper parent node about the result
        self._parent.notify_from_child(result=result)

    def set_result(self, result: CommandStatus) -> None:
        """Callback from BTree component and PerformCommandProcessor - Sets the result of the Behavior. 
        The Command manager calls BTree component function process_result. 
        The function then calls this set_result function. All of that 
        to remain compatible with Brain component.
        """

        # New code that requires returns as 'SUCCESS', 'FAILURE', 'RUNNING'
        #assert result in ['SUCCESS', 'FAILURE', 'RUNNING']
        
        if result != CommandStatus.RUNNING:
            self.on_completion(BTreeCommandStatus(CommandStatus(result)))

class Composite(TreeNode):
    '''A composite node is a node that can have one or more children.
    They will process one or more of these children in either a first 
    to last sequence or random order depending on the particular composite
    node in question, and at some stage will consider their processing complete 
    and pass either success or failure to their parent, often determined 
    by the success or failure of the child nodes. 
    
    During the time they are processing children, they will continue to return 
    Running to the parent.'''

    __slots__ = ['child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None,  **kwargs):
        '''Create instance of composite node with children'''

        # Call TreeNode constructor
        super().__init__(name=name, parent=parent)
        
        self._children = []

        # Which child idx is currently in process
        self.child_running_idx = None 

        # Keeping the amount of children for easier manipulation
        self.no_of_children = 0

    def add_child(self, child: TreeNode) -> None:
        '''Add new child node to the Composite'''
        self._children.append(child)
        self.no_of_children += 1

    def on_init(self) -> None:
        '''This method is called when the Sequence is ticked for the first time'''

        # Call TreeNode init function - sets status to RUNNING
        super().on_init()

        # Set the index to the first child
        self.child_running_idx = 0 

    def on_completion(self, result: BTreeCommandStatus) -> None:
        '''Method called when the Composite returns final result (SUCCESS or FAILURE).'''

        # Call TreeNode on_completion function - calls on_failure or on success
        super().on_completion(result)

    def on_failure(self) -> None:
        '''Method called when the Composite returns final result (FAILURE).'''
        
        # Call TreeNode on_failure function - sets status to FAILURE
        super().on_failure()

        # Recursivelly call the parent and notify it about the result
        if self.is_child: self._parent.notify_from_child_failure()

    def on_success(self) -> None:
        '''Method called when the Composite returns final result (SUCCESS).'''

        # Call TreeNode on_failure function - sets status to SUCCESS
        super().on_success()

        # Recursivelly call the parent and notify it about the result
        if self.is_child: self._parent.notify_from_child_success()

class Sequence(Composite):
    '''Runs each child in sequence, returning failure at the time
    any of the children fail and returning the success if every child
    returned a successful status. Sequence is analoguous to AND gate.'''

    #__slots__ = ['child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None, **kwargs):
        '''Create instance of Sequence node'''

        # Run Composite constructor
        super().__init__(name, parent=parent)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and 
        to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Calling process() on child with idx ({self.child_running_idx}) - "{self._children[self.child_running_idx].name}"')
        return self._children[self.child_running_idx].process()

    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).'''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports success and there are more children to process, continue running
        # on the next child
        if result.is_success and self.child_running_idx < self.no_of_children - 1:
            self.child_running_idx += 1
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Moving to the next child idx ({self.child_running_idx}) - "{self._children[self.child_running_idx].name}"')

        # Otherwise complete the Sequence - either FAILURE or SUCCESS and no more child nodes to continue with 
        else:
            # Call the super-class method - calls either on_failure or on_success methods
            self.on_completion(result)

class Selector(Composite): 
    '''Selector will return a success if any of its children succeeds and not process 
    any further children. It will fail if all children fail. This means a selector is 
    analagous with an OR gate.'''

    __slots__ = ['child_running_idx', 'no_of_children']

    def __init__(self, name, parent=None, **kwargs):
        '''Create instance of Selector node with children'''

        # Call Composite constructor
        super().__init__(name, parent=parent)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self.__class__.__name__} ({self.name}), Status: {self._status}: Calling process() on child with idx ({self.child_running_idx}) - "{self._children[self.child_running_idx].name}"')
        return self._children[self.child_running_idx].process()
    
    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).'''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports failure and there are more children to process, continue running
        # on the next child
        if result.is_failure and self.child_running_idx < self.no_of_children - 1:
            self.child_running_idx += 1
            logger.debug(f'{self.__class__.__name__} ({self.name}), Status: {self._status}: Moving to the next child idx ({self.child_running_idx}) - "{self._children[self.child_running_idx].name}"')

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

    def __init__(self, name, parent=None, **kwargs):
        '''Create instance of composite node with children'''

        # Call TreeNode constructor
        super().__init__(name=name, parent=parent)

        self._children = []

    def add_child(self, child: TreeNode) -> None:
        '''Add new child node to the Decorator.
        Always has one child and not more.'''
        try:
            assert len(self._children) == 0, f'Decorator already has a child. Decorator can have only one child.'
        except AssertionError:
            raise InvalidNumberOfChildrenError (f'Decorator node can have only one child.')

        self._children.append(child)
    
    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Notification about the result from child node.'''
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Starting notify_from_child({result}) function from child "{self._children[0].name}"')

    def on_init(self) -> None:
        '''This method is called when the Decorator is ticked for the first time'''

        # Call TreeNode init function - sets status to RUNNING
        super().on_init()
    
    def on_completion(self, result: BTreeCommandStatus) -> None:
        '''Method called when the Decorator returns final result (SUCCESS or FAILURE).'''

        # Call TreeNode on_completion function - calls on_failure or on success
        super().on_completion(result)
        
    def on_failure(self) -> None:
        '''Method called when the Decorator returns final result (FAILURE).'''
        
        # Call TreeNode on_failure function - sets status to FAILURE
        super().on_failure()

        # Recursivelly call the parent and notify it about the result
        if self.is_child: self._parent.notify_from_child_failure()

    def on_success(self) -> None:
        '''Method called when the Composite returns final result (SUCCESS).'''

        # Call TreeNode on_failure function - sets status to SUCCESS
        super().on_success()

        # Recursivelly call the parent amd notify it about the result
        if self.is_child: self._parent.notify_from_child_success()

class Inverter(Decorator):
    '''A commonly used example of a decorator is the Inverter, which will 
    simply invert the result of the child. A child fails and it will return 
    success to its parent, or a child succeeds and it will return failure to 
    the parent.'''

    def __init__(self, name, parent=None, **kwargs):
        '''Create instance of Inverter node'''

        # Call Decorator constructor
        super().__init__(name, parent=parent)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Calling process() on child "{self._children[0].name}"')
        return self._children[0].process()

    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).
        If child returns success, return FAILURE.
        If child returns failure, return SUCCESS.
        '''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports FAILURE, return SUCCESS
        if result.is_failure:
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received FAILURE from child, returning SUCCESS to the parent.')
            #self.on_completion(BTreeCommandStatus.SUCCESS)
            self.on_success()

        # IN case child returns SUCCESS, return FAILURE
        else:
            logger.debug(f'{self.depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received SUCCESS from child, returning FAILURE to the parent.')
            #self.on_completion(BTreeCommandStatus.FAILURE)
            self.on_failure()

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
    before returning to their parent.
    '''
    
    def __init__(self, name, repeat: int=None, parent=None, **kwargs):
        '''Create instance of a Repeater node'''

        # Call Decorator constructor
        super().__init__(name, parent=parent)

        # Number of repeat cycles
        #self.repeat = kwargs.get("repeat")
        self.repeat = repeat
        self._repeat_cnt = 0

    def __str__(self) -> str:
        '''String representation of Behavior TreeNode'''
        return f'{TreeNode.PRINT_COLOR[self._status]}{self.__class__.__name__} ({self.name}), Status: {self._status}, Depth: {self._depth}, Repeat: {self.repeat}, Cycle_Cnt: {self._repeat_cnt}\033[00m'

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Calling process() on child "{self._children[0].name}"')
        return self._children[0].process()

    def notify_from_child(self, result: BTreeCommandStatus) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).
        
        If no repeat parameter present, repeat forever, else repeat n-times.
        '''
        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        self._repeat_cnt += 1 # increase repeat counter

        if not self.repeat or self.repeat > self._repeat_cnt:
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received {result} from child, ({self.repeat=}, {self._repeat_cnt=}) reseting the child sub-tree and starting the processing again.')
            self._children[0].reset() # Set the node status to None and the whole subtree
            self._children[0].process() # Start over
        else:
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received {result} from child, returning {result} to the parent ({self.repeat=}, {self._repeat_cnt=}).')
            self.on_success()



class RepeatUntilFail(Decorator):	
    '''Like a repeater, these decorators will continue to reprocess their child. 
    That is until the child finally returns a failure, at which point the repeater 
    will return success to its parent.'''

    def __init__(self, name, parent=None, **kwargs):
        '''Create instance of RepeatUntilFail node'''

        # Call Decorator constructor
        super().__init__(name, parent=parent)

    def process(self) -> None:
        '''Top-down process of searching the leaf node to execute and to have the RUNNING status.'''

        # Call the super-class method - calls on_init function if it is the first tick
        super().process()

        # Call process() on the proper child - eventually trying to reach the Behavior leaf node
        logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Calling process() on child "{self._children[0].name}"')
        return self._children[0].process()

    def notify_from_child(self, result: CommandStatus) -> None:
        '''Callback from child to parent to notify the parent about the final 
        status (SUCCESS, FAILURE).
        If child returns success, start the child again and remain in RUNNING.
        If child returns failure, return SUCCESS to the parrent.
        '''

        # Call the super-class method - just logs the child and status
        super().notify_from_child(result)

        # In case child reports FAILURE, return SUCCESS
        if BTreeCommandStatus(result).is_failure:
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received FAILURE from child, returning SUCCESS to the parent.')
            #self.on_completion(BTreeCommandStatus.SUCCESS)
            self.on_success()

        # IN case child returns SUCCESS, start the child again
        else:
            logger.debug(f'{self._depth * ">>> "}{self.__class__.__name__} ({self.name}), Status: {self._status}: Received SUCCESS from child, reseting the child sub-tree and starting the processing again.')
            self._children[0].reset()
            self._children[0].process()

class InvalidNumberOfChildrenError(Exception):
    '''Raised when other than expected children nodes'''
    pass

class InvalidBTreeCommandStatusError(Exception):
    '''Raised when other than expected command status received.'''
    pass

class InvalidBehaviorTreeError(Exception):
    '''Raised when the behavior tree does not have commands on all leaves.'''
    pass

class InvalidBehaviorTreeNodeError(Exception):
    pass

class BTreeBlackboard(CommandContext):

    def __init__(self, global_bb: dict={}):
        assert pygame.get_init() # without initialization get_ticks function will not work properly
        self.globals = Container(attrs=global_bb)
        self.locals = Container()
        self.init_time = None
        self.duration = None
        self.tick_count = None
        self.current_time = pygame.time.get_ticks()

    def reset(self):
        self.locals = Container() # Every Action Node starts with clear memory
        self.init_time = pygame.time.get_ticks()
        self.duration = 0
        self.tick_count = 1
        self.current_time = pygame.time.get_ticks()

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.duration = self.current_time - self.init_time
        self.tick_count += 1

class BTree(CommandGenerator):
    '''Particular CommandGenerator implementation where command
    logic is kept in a form of behavior tree.
    '''

    def __init__(self, tree_def: dict, cmd_factory=(lambda x: x), template_path: Path=Path(''), val_check: bool=False) -> None:
        '''Read the behavior tree from dictionary'''

        # Store cmd factory for init and later usage in reset method in order
        # for the reset method to be executed always with the same command factory
        # that was defined during the init.
        self.cmd_factory = cmd_factory
        self.tree_def = tree_def
        self.reset(new_ai_structure=tree_def, template_path=template_path, val_check=val_check)
        '''
        self._root_node = create_tree(tree_def=tree_def['cmd_tree'], cmd_factory=cmd_factory, template_path=template_path)

        # Check that all leafs are behavior nodes with commands
        if val_check and not self._root_node.check(): 
            raise InvalidBehaviorTreeError('Behavior tree is invalid')

        self._action_node = None
        self._new_action_node_found = False
        self.bb = BTreeBlackboard(global_bb=tree_def.get('blackboard'))
        '''

    def print_tree(self, node: TreeNode=None, depth: int=0, lvl_str: str=" |_ ") -> None:
        '''Print the behavior tree on the console'''

        if not node:
            print(f'ROOT_NODE: {self._root_node.name}, ACTION_NODE: {self._action_node.name if self._action_node else None}')

        node = node or self._root_node

        print(f'{(depth-1) * " | "}{(1 if depth else 0) * lvl_str}{node}')

        for child in (node._children or []):
            self.print_tree(node=child, depth=depth+1, lvl_str=lvl_str)

    def __str__(self):
        return f'ROOT_NODE: {self._root_node.name}, ACTION_NODE: {self._action_node.name if self._action_node else None}'

    def reset(self, new_ai_structure: dict, template_path: Path=Path(''), val_check: bool=False) -> None:
        '''Read the behavior tree from dictionary'''
        self._root_node = create_tree(tree_def=new_ai_structure['cmd_tree'], cmd_factory=self.cmd_factory, template_path=template_path)

        # Check that all leafs are behavior nodes with commands
        if val_check and not self._root_node.check(): 
            raise InvalidBehaviorTreeError('Behavior tree is invalid')

        self._action_node = None
        self._new_action_node_found = False
        self.bb = BTreeBlackboard(global_bb=new_ai_structure.get('blackboard', {}))

    def get_command(self) -> (any, bool):
        ''' Return the command from the Behavior node of the tree and additionally indicate
        if it is the first return of this particular tree node or not. 

        :returns: Tuple consisting of any object stored in Behavior node Command attribute and
            information if this object is being obtained for the first time.
        '''
        # If the root node is in status SUCCESS or FAILURE, do not continue as the tree has finished.
        if self._root_node.is_completed:
            logger.debug(f'Behavior tree is completed, no more command to return')
            return (None, False)

        cmd = None

        # If we have some action node, use it
        if self._action_node:
            action_node, cmd = self._action_node.process() # call action node again
            return (cmd, False) # indicate that it is not a first call of the command

        else:
            action_node, cmd = self._root_node.process() # find new action node
            self._action_node = action_node
            # Indicate that the new action node has been assigned
            self._new_action_node_found = True
            return (cmd, True) # indicate that it is a first call of the command


    def process_command_result(self, result: BTreeCommandStatus) -> None:
        '''Callback the result of the command in order to update
        CommandGenerator internal state.'''

        self._action_node.set_result(result) 

        # here eventually the action node can be in None status due to reset. Hence we need to remember the original result
        # and act based on the original result.
        if BTreeCommandStatus(result).is_completed:
            self._action_node = None


    def notify_command_start(self) -> None:
        '''Callback from command manager before the command starts
        in order to set the CommandContext statistics.'''

        # calculate the init time and others when it is the first call of the action
        if self._new_action_node_found: 
            self.bb.reset() # Reset statistics for the new action node
            self._new_action_node_found = False
        else:
            self.bb.update() # Update statistics

    def restart_brain(self, bb: dict=None):
        '''Start processing from the root again - usually after event is received'''
        self.reset(new_ai_structure=self.tree_def)

        if bb is not None:
            self.bb = BTreeBlackboard(global_bb=bb)

def create_tree(tree_def: dict, parent: TreeNode=None, depth: int=0, cmd_factory=(lambda x: x), template_path: Path=Path('')) -> TreeNode:
    '''Create recursively behavior tree from json definition.
    
        cmd_factory - function that will translate command definition from the dict to some object/function etc.
    '''

    # Check if node definition contains template key. In that case read the
    # tree from the file
    tree_template = tree_def.get("template")

    if tree_template:
        logger.debug(f'{depth * ">>> "}Creating Tree from template "{tree_template}".')
        result = create_tree(tree_def=get_dict_params(definition=tree_template, dir=template_path), parent=parent, cmd_factory=cmd_factory)
        logger.debug(f'{depth * ">>> "}Creating Tree from template "{tree_template}". Returns {result}')
        return result

    else:
        # Get TreeNode parameters
        ##node_type = tree_def['type'] # mandatory
        ##node_name = tree_def['name'] # mandatory
        node_type = tree_def.pop('type') # mandatory
        
        # Optional for Behavior - None if not present
        try:
            tree_def['command'] = cmd_factory(tree_def['command'])
        except KeyError:
            pass

        # Get TreeNode class object based on 'type' from the JSON
        node_class = str_to_class(module=sys.modules[__name__], class_name=node_type)

        ##logger.debug(f'{depth * ">>> "}Creating TreeNode: class="{node_class}", name="{node_name}", command="{node_command}"')

        ## Remove children from the tree_def
        children_def = tree_def.pop('children', [])

        ##node = node_class(
        ##            name=node_name,
        ##            parent=parent,
        ##            command=node_command
        ##)

        node = node_class(parent=parent, **tree_def)
        ##print(f'CREATING {node_class=}, {tree_def=}, {children_def=}')

        ##children_def = tree_def.get('children', [])

        for child_def in children_def:
            result = create_tree(tree_def=child_def, parent=node, depth=depth+1, cmd_factory=cmd_factory, template_path=template_path)
            node.add_child(result)
        
        node._depth = depth
        return node


if __name__ == '__main__':
    import doctest
    doctest.testmod()