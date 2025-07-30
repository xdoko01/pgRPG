''' Module "example_game.core.components.visual_fx_on_creation" contains
VisualFXOnCreation component implemented as a VisualFXOnCreation class.

Use 'python -m example_game.core.components.visual_fx_on_creation -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class VisualFXOnCreation(Component):
    ''' Entity displays selected effect upon creatiom from factory.

    Used by:
        - GenerateVisualFXOnCreationProcessor

    Examples of JSON definition:
        {"type" : "VisualFXOnCreation", "params" : {"effect" : "explosion"}}

    Tests:
        >>> c = VisualFXOnCreation(**{"effect" : "explosion"})
    '''

    __slots__ = ['effect', 'fixed_position']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new VisualFXOnCreation component.

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
