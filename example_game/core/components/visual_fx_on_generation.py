''' Module "example_game.core.components.visual_fx_on_generation" contains
VisualFXOnGeneration component implemented as a VisualFXOnGeneration class.

Use 'python -m example_game.core.components.visual_fx_on_generation -v' to run
module tests.
'''

from pgrpg.core.ecs import Component

class VisualFXOnGeneration(Component):
    ''' Entity displays selected effect upon generation from factory.

    Used by:
        - GenerateVisualFXOnGenerationProcessor

    Examples of JSON definition:
        {"type" : "VisualFXOnGeneration", "params" : {"effect" : "explosion"}}

    Tests:
        >>> c = VisualFXOnGeneration(**{"effect" : "explosion"})
    '''

    __slots__ = ['effect', 'fixed_position']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new VisualFXOnGeneration component.

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
