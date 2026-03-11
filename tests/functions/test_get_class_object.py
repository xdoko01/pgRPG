import pytest
import sys

from pgrpg.functions.get_class_object import (
    str_to_class,
    get_class_from_def,
)


class TestStrToClass:
    def test_valid_module_returns_class(self):
        import pgrpg.core.ecs as ecs_module
        cls = str_to_class(ecs_module, "Component")
        assert cls is ecs_module.Component

    def test_invalid_attribute_raises_error(self):
        import pgrpg.core.ecs as ecs_module
        with pytest.raises(ValueError, match="has no class named"):
            str_to_class(ecs_module, "NonExistentClass")


class TestGetClassFromDef:
    def test_with_real_pgrpg_class(self):
        cls = get_class_from_def("event:Event", class_package="pgrpg.core.events")
        from pgrpg.core.events.event import Event
        assert cls is Event
