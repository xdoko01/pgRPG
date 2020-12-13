from .component import Component

class Damageable(Component):
    ''' Entity has some health, i.e. is damageable 

    Used by:
        - TBD

    Examples of JSON definition:
        {"type" : "Damageable", "params" : {}}
        {"type" : "Damageable", "params" : {"health" : 50}}

   Tests:
        >>> c = Damageable()
    '''

    __slots__ = ['health']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the  Health component.
        '''
        super().__init__()

        self.health = kwargs.get("health", 100)
