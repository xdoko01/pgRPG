"""Resolve Python class references from string paths.

Provides utilities for dynamically importing modules and retrieving
class objects given package, module, and class name strings.
"""

from importlib import import_module

def str_to_package_module(package: str, module: str):
    """Import and return a module from a package.

    Args:
        package: Package path, e.g. ``"pgrpg.core.ecs"``.
        module: Module path relative to the package.

    Returns:
        The imported module object.

    Raises:
        ValueError: If the module cannot be found.
    """
    try:
        return import_module(module, package=package)
    except ModuleNotFoundError:
        raise ValueError(f'Incorrect package.module name "{package}.{module}"')

def str_to_class(module, class_name):
    """Get a class from a module by name.

    Args:
        module: Module object to look up the class in.
        class_name: Name of the class to retrieve.

    Returns:
        The class object.

    Raises:
        ValueError: If the class does not exist in the module.
    """
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ValueError(f'Module "{module.__name__}" has no class named "{class_name}"')

def get_class_object(package: str, module: str, class_name: str) -> type:
    """Get a class reference given package, module, and class name strings.

    Args:
        package: Package path, e.g. ``"pgrpg.core.ecs"``.
        module: Module path relative to the package.
        class_name: Name of the class in the module.

    Returns:
        Reference to the class.

    Raises:
        ValueError: If the class cannot be resolved.
    """

    try:
        module = str_to_package_module(package=package, module=module)
        return str_to_class(module=module, class_name=class_name)
    except ValueError:
        raise ValueError(f'Error getting class reference for "{package=}","{module=}" and "{class_name=}"')

def get_class_from_def(class_def: str, class_package: str='pgrpg.core.ecs'):
    """Return a class object from a ``"module:ClassName"`` string path.

    Args:
        class_def: Class definition in ``"path.to.module:ClassName"``
            format.
        class_package: Base package to prefix the module path with.

    Returns:
        Reference to the class.

    Raises:
        ValueError: If the class cannot be identified.
    """

    try:
        module, name = class_def.split(':')
        return get_class_object(None, class_package + '.' + module, name)
    except ValueError:
        raise ValueError(f'Error during loading of class "{name}"')


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
