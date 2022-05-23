''' Module "pyrpg.core.ecs.components.damaging" contains
Damaging component implemented as a Damaging class.

Use 'python -m pyrpg.core.ecs.components.damaging -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class Damaging(Component):
    ''' Entity containing this component is hurting
    entities upon collision - for example projectile.

    Used by:
        - CollisionDamageProcessor

    Examples of JSON definition:
        {"type" : "Damaging", "params" : {}}
        {"type" : "Damaging", "params" : {"damage" : 20}}
        {"type" : "Damaging", "params" : {"damage" : 10, "parent" : 2}}


    Tests:
        >>> c = Damaging()
        >>> c = Damaging(**{"damage" : 10, "parent" : 2})
        >>> c.damage
        10
        >>> c.parent
        2
    '''

    __slots__ = ['damage', 'parent']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Damaging component.

        Parameters:
            :param damage: Count of Damage points caused by the entity hit
            :type damage: int

            :param parent: Originator of the damage (optional)
            :type parent: entity_id
        '''
        super().__init__()

        self.damage = kwargs.get("damage")
        self.parent = kwargs.get("parent", None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
