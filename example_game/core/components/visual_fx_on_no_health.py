''' Module "pyrpg.core.ecs.components.visual_fx_on_no_health" contains
VisualFXOnNoHealth component implemented as a VisualFXOnNoHealth class.

Use 'python -m pyrpg.core.ecs.components.visual_fx_on_no_health -v' to run
module tests.
'''

from pyrpg.core.ecs.components.component import Component

class VisualFXOnNoHealth(Component):
    ''' Entity displays selected effect upon having no health.

    Used by:
        - GenerateVisualFXOnNoHealthProcessor

    Examples of JSON definition:
        {"type" : "VisualFXOnNoHealth", "params" : {"effect" : "explosion"}}

    Tests:
        >>> c = VisualFXOnNoHealth(**{"effect" : "explosion"})
    '''

    __slots__ = ['effect', 'fixed_position']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new VisualFXOnNoHealth component.

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
