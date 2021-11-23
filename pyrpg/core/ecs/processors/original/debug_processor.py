__all__ = ['DebugProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class DebugProcessor(esper.Processor):
    ''' Prints all the information about entities and components

    Involved components:

    Related processors:

    What if this processor is disabled?
        -   normaly, should be disabled

    Where the processor should be planned?
        -   whereever we need to find out the status of entities
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    def __init__(self, *args, **kwargs):
        ''' Init the processor.

            :param caption: String that will be printed at the beginning of debug output - to differentiate in case planned on many places
            :param entities: List of entities that we want to see in the debug output. If empty, all are listed.
        '''
        super().__init__()

        self.caption = kwargs.get('caption', '')
        self.list_of_entities = kwargs.get('entities', [])

    def process(self, *args, **kwargs):
        ''' Print all the information about entities and components
        '''

        print(f'*** DebugProcessor - START - {self.caption}')

        for ent in self.world._entities if not self.list_of_entities else self.list_of_entities:
            print(f'*** ENTITY {ent} ***')
            for comp in self.world.components_for_entity(ent):
                print(f'{comp}')

        print(f'*******************************************')


    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass