''' Module "pyrpg.core.ecs.components.damaging" contains
Damaging component implemented as a Damaging class.

Use 'python -m pyrpg.core.ecs.components.damaging -v' to run
module tests.
'''

from .component import Component

class Damaging(Component):
    ''' Entity containing this component is hurting
    entities upon collision - for example projectile.

    Used by:
        - CollisionDamageProcessor

    Examples of JSON definition:
        {"type" : "Damaging", "params" : {}}
        {"type" : "Damaging", "params" : {"damage" : 20}}

    Tests:
        >>> c = Damaging()
        >>> c = Damaging(**{"damage" : 20})
        >>> c.damage
        20
    '''

    __slots__ = ['damage']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the Damaging component.
        '''
        super().__init__()

        self.damage = kwargs.get("damage", 10)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
