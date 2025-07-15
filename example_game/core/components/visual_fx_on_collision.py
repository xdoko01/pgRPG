''' Module "pyrpg.core.ecs.components.visual_fx_on_collision" contains
VisualFXOnCollision component implemented as a VisualFXOnCollision class.

Use 'python -m pyrpg.core.ecs.components.visual_fx_on_collision -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class VisualFXOnCollision(Component):
    ''' Entity displayes selected effect upon collision with other entity.

    Used by:
        - GenerateVisualFXOnCollisionProcessor

    Examples of JSON definition:
        {"type" : "VisualFXOnCollision", "params" : {"effect" : "explosion"}}

    Tests:
        >>> c = VisualFXOnCollision(**{"effect" : "explosion"})
    '''

    __slots__ = ['effect', 'fixed_position']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new VisualFXOnCollision component.

        Parameters:
            :param effect: Name of the visual effect - reference to template.
            :type effect: str

            :param fixed_position: If False, follow the position of the entity.
            :type effect: bool
        '''
        super().__init__()

        # Get the effect name
        self.effect = kwargs.get('effect', '')

        self.fixed_position = kwargs.get('fixed_position', False)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
