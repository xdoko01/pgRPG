from pyrpg.core.managers.ecs_manager import ECSManager
from pyrpg.core.btrees.btree import BTree

class Command:
    ''' Parent class of all commands
    
    Instance should have access to all parameters of the command

        When creating command, fill the following params That remain unchanged for the cmd instance
        constant ...world = kwargs["world"]
        constant ...ecs_mng = kwargs["ecs_mng"]
        constant ...entity = kwargs["entity"]
        constant ...brain = kwargs["brain"]
         ... or better 
            constant ref ...bb_globals = kwargs["brain"].blackboard
            constant ref ...bb_locals = kwargs["brain"].blackboard.running_behavior.bb
                                init_time = kwargs["brain"].blackboard.running_behavior.init_time
                                duration = kwargs["brain"].blackboard.running_behavior.duration
                                ticks_count = kwargs["brain"].blackboard.running_behavior.ticks_count
    
    '''
    def __init__(self, entity_id: int, brain, ecs_mng: ECSManager) -> None:
        '''
        Parameters:
            :param entity_id: Entity ID to which the command associates.
            :type entity_id: int

            :param brain: Reference to BTRee instance or classic brain
            :type brain: ref

            :param ecs_mng: Reference to manager of the entities in the game world
            :type ecs_mng: ECSManager
        '''
        self.ecs_mng = ecs_mng
        self.world = ecs_mng._world
        self.brain = brain
        self.entity_id = entity_id

class BTreeCommand(Command):
    def __init__(self, entity_id: int, brain: BTree, ecs_mng: ECSManager):
        super()._init__(entity_id, brain, ecs_mng)

        self.bb_globals = self.brain.blackboard
        self.bb_locals = self.brain.blackboard.running_behavior.bb
        self.init_time = self.brain.blackboard.running_behavior.init_time
        self.duration = self.brain.blackboard.running_behavior.duration
        self.ticks_count = self.brain.blackboard.running_behavior.ticks_count

{"cycle": 208, "commands": [["new_move_add", {"moves": ["down"], "entity": 1}]]}
{"cycle": 208, "commands": [[1, "new_move_add", {"moves": ["down"]}]]}

(1, 'btree.DummyCommand', {"msg": "test", "repeat": 10})

# Every entity has its command factory - it is brain component probably
# btree component must have COmmand factory - every entity that can follow commands must have command factory
>>> command_factory = CommandFactory(entity, brain, ecs_mng)
>>> command_factory(cmd='DummyCommand', msg, repeat) -> call DummyCOmmand with all necessary parameters


"""
Command
- must be implemented in separate files - in order to support modularity - easy adding of the new commands
- command must be loosely-coupled on other components
  - define input/output parameters
    - context
      - read information stored by other commands from the blackboard
      - write information for other commands to the blackboard
      - read/write information about progress of the currently running command - because command is not atomicd
    - entity_id
      - what entity should do the command. It is not necessarily the brain owner
    - esp_mng
      - in order for the command to actualy do something in the game world, it needs to have functions to perform the changes
      
class DummyCommand(Command)
  def __init__(self, context: Blackboard, entity_id: int, **params)


- command can be fired from multiple sources
  - console - I write move command there and it is added into the queue and processed
  - btree component that generates the command based on the logic
  - brain component that generates the command based on the logic

"""