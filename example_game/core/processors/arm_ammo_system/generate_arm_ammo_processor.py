__all__ = ['GenerateArmAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.ammo_pack import AmmoPack
from core.components.factory import Factory
from core.components.flag_was_picked_by import FlagWasPickedBy
from core.components.flag_is_about_to_arm_ammo import FlagIsAboutToArmAmmo

# Logger init
logger = logging.getLogger(__name__)

class GenerateArmAmmoProcessor(Processor):
    ''' Detects entities that act as ammo + have been picked and assigns
    the FlagIsAboutToArmAmmo to all their colliders (potentional fighters).

    Involved components:
        -   AmmoPack
        -   FlagWasPickedBy
        -   FlagIsAboutToArmAmmo

    Related processors:
        -   PerformArmAmmoProcessor
        -   RemoveFlagIsAboutToArmAmmoProcessor

    What if this processor is disabled?
        -   ammo is not being armed

    Where the processor should be planned?
        -   after PerformPickupProcessor
        -   before PerformArmAmmoProcessor
        -   before RemoveFlagIsAboutToArmAmmoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'pickup_system.perform_pickup_processor:PerformPickupProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are ammo packs + have been picked, and assigns
        the FlagIsAboutToArmAmmo to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have AmmoPack, Factory and FlagWasPickedBy - those are candidates for arming the ammo
        # AmmoPack is nothing without the Factory component, AmmoPack component only marks that the factory can be armed to some weapon
        for ent_ammo, (ammo, factory, flag_was_picked_by) in self.world.get_components(AmmoPack, Factory, FlagWasPickedBy):

            # Get the information from the Factory about number of projectiles that are available in the AmmoPack 
            #   max_units ... max units that can be generated, 
            #   current_units ... how many already has been generated
            self.world.add_component(flag_was_picked_by.picker, FlagIsAboutToArmAmmo(
                ammo=ent_ammo,
                weapon=ammo.weapon,
                type=ammo.type,
                total_units=factory.max_units,
                used_units=factory.current_units))

            logger.debug(f'({self.cycle}) - Entity {flag_was_picked_by.picker} is trying to arm as ammo entity {ent_ammo}.')

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

