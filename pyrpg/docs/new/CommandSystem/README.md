# Command System

*Command system* consists of processors that generate, perform and record commands.

## What is Command and how it is Implemented

Command is a way of telling the entity what to do in the game world - for example to move, to attack, to search for enemy etc.

Technically, command is defined as a list consisting of 2 items - name (str) and params (dict) in the scene file.

Example of a Command: ("new_move_vect_noadd", {"vector": [0, 10], "entity": 1})

Commands can originate from different components. The most common are the following:
 - The `Controllable` component is using commands to define what should happen at the moment when the key is pressed. For example, when left arrow button is pressed, system generates and processes the command for moving the entity (owner of `Controllable` component) left.
 - The `BrainAI` component represents the brain of the component and generates the commands based on predefined AI structures. At the moment, 2 structures can be used: behavior trees (`btree`) and simpler behavior lists (`blist`).

Every command is implemented as a separate python file (module) that can be found in `pyrpg.core.commands.commands` package.

## What is the Lifecycle of the Command
![Command Lifecycle](pyRPG%20-%20CommandSystem%20-%20Command%20Lifecycle.jpg "Command Lifecycle")

## Interaction with Other Systems
The *Command System* can be indirectly related to any system and at the same time there is no direct connection with any specific system. The most common way how *Command System* interacts with other systems is by creation of new components on entities by execution of the command. For example interaction with *Movement System* can look as follows: command `move` generates `FlagDoMove` component on the entity resulting in moving of the entity.

## Specifics

### AI structures

### Command, CommandGenerator and CommandContext

## Components

### The `Controllable` Component
The `Controllable` component is generating commands in order to tell entity what to do upon key pressed.

 - TODO - simple commands, multiple commands, brain modification with complicated command patterns

### The `BTreeAI` Component
The `BTreeAI` component is generating commands typically for NPCs, based on logic stored in a form of the behavioral tree.

### The `BListAI` Component
The `BListAI` component is generating commands typically for NPCs, based on logic stored in a form of the list - I call it behavioral list for my purposes, but there is no such official structure defined. Behavioral lists are less capable, shorter and better readable than behavioral trees.

### The `BrainAI` Component
The `BrainAI` component is generating commands typically for NPCs, based on either behavioral list or behavioral tree. It is more convenient to use just this component and within it define the AI logic either by list or tree as convenient.

## Processors

* **Command Generation and Processing Flow**
The main logic is implemented by the following sequence of processors.

  ```mermaid
  flowchart LR
    GenerateCommandFromInputProcessor-->PerformCommandProcessor
	GenerateCommandFromBTreeProcessor-->PerformCommandProcessor
	GenerateCommandFromBListProcessor-->PerformCommandProcessor
	GenerateCommandFromBrainProcessor-->PerformCommandProcessor
  ```

* **Command Recording Flow**
This flow serves for recording of commands into the file, if needed (demo level).

  ```mermaid
  flowchart LR
    GenerateCommandFromXXXProcessor-->RecordCommandToFileProcessor-->PerformCommandProcessor
  ```
* **Command Playback Flow**
This flow serves for playback of commands from the file, if needed (demo level).

  ```mermaid
  flowchart LR
    GenerateCommandFromFileProcessor-->PerformCommandProcessor
  ```

### The `GenerateCommandFromInputProcessor` Processor

### The `GenerateCommandFromBrainProcessor` Processor
This processor is more generic than `GenerateCommandFromBTreeProcessor` and `GenerateCommandFromBListProcessor` but works the same - extracts the next command from `CommandGenerator` (behavior tree or list) and passes it to `CommandManager` for adding into the command queue and processing. 

### The `GenerateCommandFromFileProcessor` Processor

### The `PerformCommandProcessor` Processor

### The `RecordCommandToFileProcessor` Processor
