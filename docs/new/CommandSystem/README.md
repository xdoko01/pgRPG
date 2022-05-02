# Command System

Command system consists of processors that generate, perform and record commands.

## What is Command and how it is Implemented

Command is a tuple or list (in order to be able to store it in json) where first idx value determines command name and the second idx value the command parameters.

Example of a Command: ("new_move_vect_noadd", {"vector": [0, 10], "entity": 1})

Command is implemented as a separate function that can be found in `core.commands` package. In `core.commands.__init__.py` there is mapping of command name to specific command function that is implemented in separate file.

## What is the Life Cycle of the Command


## Cooperation between Processors

Commands can be generated as a result of user input (pressing arrows) or as based on information stored in the brain of the game entity or based on list of commands recorded in some file.
