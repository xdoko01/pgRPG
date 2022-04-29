# Processor prerequisities

# How to define processor in the quest file (json and/or yaml)
There is a specific section in the quest json or yaml file where you can specify which processors and in which order should be executed in the game world.

It is a good practice to place the `processors` section right after the generic quest definition, but technically it can be placed anywhere.

Example of the section from JSON file:

```
{
    "id" : "new_test01_collisions",
    "name" : "Collisions Test",
    "description" : "Test new collision processors",
    "objective" : "POC of the new collision system",
    "init_phase" : "phase01",

    "processors" : [
        ["new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor", {}],
        ["new.command_system.generate_command_from_brain_processor:GenerateCommandFromBrainProcessor", {}],
        // more processors come here
    ],

    // other quest definitions follow
```

Example of the same section from the YAML file:

```
---
id: new_test01_collisions
name: Collisions Test
description: Test new collision processors
objective: POC of the new collision system
init_phase: phase01

processors:
- ["new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor", {}]
- ["new.command_system.generate_command_from_brain_processor:GenerateCommandFromBrainProcessor", {}]
  
  # more processors to come here
```

The line specifying the processor has several parts that are telling the system where to find the class implementing the processor and the parameters that should be passed to the processor, if any. Processor definition is defined as a list with 2 items:
  1. The path to the processor class
  2. Parameters for the processor passed as a dictionary

Let's take following processor as an example:

```
["new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor", {}]
```
  1. The path to the processor class ... `new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor`. The path is the same as if `import` statement is used in the code. The part `new.command_system` is specifying the package. The `generate_command_from_input_processor` specifies the module, i.e. file in the package. In our case file `generate_command_from_input_processor.py` in which the class `GenerateCommandFromInputProcessor` is located. As you can see, the class name is specified after ":" character.

  Note: The class can be defined in `__init__.py` file of the package. In that case, the module file does not need to be specified and the patch might be shorter. If you want to achieve this, you would need to add the following code into the `__init__.py` file of the desired system package (see also section *How to handle multiple versions of the same processor*).

  ```
  # __init__.py file
  from .generate_command_from_input_processor import GenerateCommandFromInputProcessor
  ```

  2. Parameters of the processor ... `{}` in this case no parameters are passed to the processor. However different processors might have parameters. For example processor `GenerateCommandFromFileProcessor` might have path to the file containing the commands. Definition of such processor might look as follows:

  ```
  ["new.command_system.generate_command_from_file_processor:GenerateCommandFromFileProcessor", {"file" : "pyrpg/resources/quests/new/tests/02_commands/new_test_commands_01_record.json", "mode" : "total_control"}]
  ```

# How to handle multiple versions of the same processor?
Sometimes it is convenient to have several versions of the same processor implemented. The reason for that might be that you are experimenting with performace and need to compare performance of 2 processors that are doing the same thing but using different approach/algorithm. Another reason might be that you are improving the processor over time and do want to have the oportunity to come back to previous versions of the processor in the future if needed.

As an example, let's consider `GenerateCollisionsProcessor` that is checking for collisions between entities and if collision occurs, storing information about the collision into new component `FlagHasCollided`.

In case of this processor there might be one version that is checking for collisions only entities displayed on the camera (game screen) and other version that is checking for collision of the entities in the entire game world. Let's name the first version as `GenerateCollisionsCameraOnlyProcessor` and the second as `GenerateCollisionsFullProcessor`.

If you want to experiment with both processors, it means manual changing of code and quest definition json/yaml files:
  1. Changes in code
    In case `GenerateCollisionsProcessor` is defined as a prerequisity in `PREREQ` of some other processor (see *Processor Prerequisities* section), you need to change the code to use the correct prerequisity. You need to do this action in the code of all processors that have `GenerateCollisionsProcessor` as the prerequisity every time you want to experiment and change the processor implementation class (either to `GenerateCollisionsCameraOnlyProcessor` or `GenerateCollisionsFullProcessor`).
  2. Change in quest definition.
    You would also need to change the quest definition to point to the desired class that is implementing `GenerateCollisionsProcessor` (either `GenerateCollisionsCameraOnlyProcessor` or `GenerateCollisionsFullProcessor`)

As you can see the above can be demanding and chaotic. Ideal would be to have one place where you can define the name of the class that should be used as implementation of `GenerateCollisionsProcessor`. This place can be `__init__.py` of the `collision_system` package.

```
# Import all versions of the generate collisions processor
from .generate_collisions_processor import *

# Assign the selected processor version to the name GenerateCollisionsProcessor
GenerateCollisionsProcessor = GenerateCollisionsOptimizedProcessor
```

Alternativelly, the shorter version of the same might look as follows:

```
from .generate_collisions_processor import GenerateCollisionsOptimizedProcessor as GenerateCollisionsProcessor
```

Doing the above assignment will be the only change that is needed in order to switch between classes implementing collision generation. In the quest definition, we can then use the following definition:

```
"processors" : [
    // ... bunch of other definitions
    ["new.collision_system:GenerateCollisionsProcessor", {}],
    // ... more definitions
]
```

Of course, you can still specify particular processor class in the quest definition. 

```
"processors" : [
    // ... bunch of other definitions
    ["new.collision_system:generate_collisions_processor:GenerateCollisionsCameraOnlyProcessor", {}], // still valid
    // ... more definitions
]
```


# Rules to write processors

    1. Every processor is implemented in separate file.
    2. Processor module file name is named same as the processor name in following format `new_example_processor.py` for processor class `NewExampleProcessor`.
    3. Processors are grouped into systems, if applicable.
    4. Every system has its own package - folder containing modules with processors.

## Processor module structure

    1. `__all__ = ['NewExampleProcessor']` in case that module file contains some 
    2. imports
    3. `NewExampleProcessor(esper.Processor)` class inherited from esper.Processor class
        - Class comment contains:
            - Involved Components
            - Related Processors
            - What if Processor is Disabled?
            - Where the Processor should be planned (order)?
        - `PREREQ` as class attribute specifying processors that must be planned before this processor. It is optional.
        - __init__ method
        - process method
        - pre_save method
        - post_load method
        - finalize method