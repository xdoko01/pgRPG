''' Module "pyrpg.core.ecs.components.component" contains
parent Component class inherited by every component class.

Use 'python -m pyrpg.core.ecs.components.component -v' to run
module tests.
'''

import sys

class Component(object):
    ''' Parent class for all components. Inheritance from object is a must
    because __slots__ are used in inherited component classes.

    Tests:
        >>> c = Component()
    '''

    def __init__(self):
        pass

    def __str__(self):
        ''' Print representation of the component instance
        '''
        return f"Component '{self.__class__.__name__}' at {hex(id(self))} ({sys.getsizeof(self)} bytes): {self.__dict__}"

    def pre_save(self):
        ''' Prepare component for saving - remove all references to
        non-serializable objects.
        '''
        pass

    def post_load(self):
        ''' Regenerate all non-serializable objects for the component
        '''
        pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
