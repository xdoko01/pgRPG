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