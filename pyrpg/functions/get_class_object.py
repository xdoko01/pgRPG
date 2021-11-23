from importlib import import_module

def get_class_object(package : str, module : str, class_name : str) -> type:
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

    # Get the module from package
    try:
        module = import_module(module, package=package)
    except ModuleNotFoundError:
        raise ValueError(f'Incorrect package.module name "{package}.{module}"')

    # Get the class from the module
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ValueError(f'Module "{module.__name__}" has no class named "{class_name}"')

if __name__ == '__main__':
    #ref = get_class_object('functions', 'wait', 'Brain')
    ref = get_class_object(None, 'wait', 'Brain')

    print(f'Class is: {ref}')