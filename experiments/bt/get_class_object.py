from importlib import import_module

def str_to_package_module(package: str, module: str):
    '''Gets reference to the module in the package

    Parameters:
        :param package: Path to the package, for example pyrpg.core.ecs
        :type package: str

        :param module: Path to the module, relative to the package
        :type module: str
    '''
    try:
        return import_module(module, package=package)
    except ModuleNotFoundError:
        raise ValueError(f'Incorrect package.module name "{package}.{module}"')

def str_to_class(module, class_name):
    '''Translate class name to class'''
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ValueError(f'Module "{module.__name__}" has no class named "{class_name}"')

def get_class_object(package: str, module: str, class_name: str) -> type:
    '''Gets reference to the the class given the package, module and the class name strings
    
    Parameters:
        :param package: Path to the package, for example pyrpg.core.ecs
        :type package: str

        :param module: Path to the module, relative to the package
        :type module: str

        :param class_name: Name of the class in the module
        :type class_name: str

        :returns: Reference to the class
    '''

    try:
        module = str_to_package_module(package=package, module=module)
        return str_to_class(module=module, class_name=class_name)
    except ValueError:
        ValueError(f'Error getting class reference for package "{package}", module "{module}" and class "{class_name}"')

def get_class_from_def(class_def: str, class_package: str='pyrpg.core.ecs'):
    '''Returns class object based on string path.

    :param class_def: Path to the  class in format of path.to.module:Class
    :type class_def: str

    :return: Returns reference to the Class.
    :raises: ValueException, if class cannot be identified
    '''

    try:
        module, name = class_def.split(':')
        return get_class_object(None, class_package + '.' + module, name)
    except ValueError:
        ValueError(f'Error during loading of class "{name}"')


if __name__ == '__main__':

    # Case 1/ Get the class from the current module
    class Test:
        '''Test class'''
        pass

    import sys
    print(f'{str_to_class(sys.modules[__name__], "Test")}')

    #ref = get_class_object('functions', 'wait', 'Brain')
    #ref = get_class_object(None, 'wait', 'Brain')

    #print(f'Class is: {ref}')