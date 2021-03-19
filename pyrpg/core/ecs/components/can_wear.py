''' Module "pyrpg.core.ecs.components.can_wear" contains
CanWear component implemented as a CanWear class.

Use 'python -m pyrpg.core.ecs.components.can_wear -v' to run
module tests.
'''

from .component import Component

class CanWear(Component):
    ''' Entity can pickup and wear Wearable entities

    Used by:
        - CollisionWearableProcessor

    Examples of JSON definition:
        {"type" : "CanWear", "params" : {}}
        {"type" : "CanWear", "params" : {"head" : "golden_helmet"}}

    Tests:
        >>> c = CanWear()
        >>> c = CanWear(**{"head" : "golden_helmet"})
        >>> c.wearables['head']
        'golden_helmet'
    '''

    __slots__ = ['wearables']

    BODYPARTS = ['head', 'hands', 'feet', 'belt', 'legs', 'torso']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new CanWear component.

        Parameters:
            :param head: What entity should be wear on the head (optional, default None).
            :type head: int

            :param hands: What entity should be wear on the hands (optional, default None).
            :type hands: int

            :param feet: What entity should be wear on the feet (optional, default None).
            :type feet: int

            :param belt: What entity should be wear on the belt (optional, default None).
            :type belt: int

            :param legs: What entity should be wear on the legs (optional, default None).
            :type legs: int

            :param torso: What entity should be wear on the torso (optional, default None).
            :type torso: int

            :raise: ValueError - in case of incorrect item to wear.
        '''

        super().__init__()

        # Initiate the wardrobe
        self.wearables = {
            'head' : None,
            'hands' : None,
            'feet' : None,
            'belt' : None,
            'legs' : None,
            'torso' : None
        }

        # Try to wear the entity
        try:
            for w_key, w_value in kwargs.items():

                # Translate the value (Wearable) to Entity instance if necessary
                #wearable_entity = engine.alias_to_entity.get(w_value) if isinstance(w_value, str) else w_value
                #wearable_entity = self.alias_dict.get(w_value) if isinstance(w_value, str) else w_value

                # If it is possible to wear the entity (known bodypart and empty slot for wearable) then wear it
                if w_key in CanWear.BODYPARTS and not self.wearables.get(w_key):
                    self.wearables.update({w_key : w_value})

        except KeyError:
            # Notify component factory that initiation has failed
            print(f'Problem with wearing of the entity - {w_key} : {w_value}')
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
