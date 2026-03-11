import pytest

from pgrpg.functions.str_utils import parse_fnc_list, parse_fnc_str


class TestParseFncList:
    def test_only_name(self):
        name, args, kwargs = parse_fnc_list(["sum"])
        assert name == "sum"
        assert args == []
        assert kwargs == {}

    def test_name_and_args(self):
        name, args, kwargs = parse_fnc_list(["sum", [1, 2]])
        assert name == "sum"
        assert args == [1, 2]
        assert kwargs == {}

    def test_name_args_kwargs(self):
        name, args, kwargs = parse_fnc_list(["sum", [1, 2], {"a": 23}])
        assert name == "sum"
        assert args == [1, 2]
        assert kwargs == {"a": 23}

    def test_name_and_kwargs_only(self):
        name, args, kwargs = parse_fnc_list(["sum", {"a": 23}])
        assert name == "sum"
        assert args == []
        assert kwargs == {"a": 23}


class TestParseFncStr:
    def test_function_call_string(self):
        name, args, kwargs = parse_fnc_str("sum(1, 2)")
        assert name == "sum"
        assert args == [1, 2]
        assert kwargs == {}

    def test_no_parentheses(self):
        name, args, kwargs = parse_fnc_str("sum")
        assert name == "sum"
        assert args == []
        assert kwargs == {}

    def test_empty_parentheses(self):
        name, args, kwargs = parse_fnc_str("sum()")
        assert name == "sum"
        assert args == []
        assert kwargs == {}

    def test_with_kwargs_and_custom_sep(self):
        name, args, kwargs = parse_fnc_str(
            "sum(1;2;3; map=unknown; position=[3,5])", sep=";"
        )
        assert name == "sum"
        assert args == [1, 2, 3]
        assert kwargs["map"] == "unknown"
        assert kwargs["position"] == [3, 5]


class TestStrToPackageModuleClass:
    """Test parsing of 'module:ClassName' style strings via parse_fnc_list/str."""

    def test_basic_parsing_via_split(self):
        # The convention used in pgrpg is "module_path:ClassName"
        class_def = "my_module:MyClass"
        module, name = class_def.split(":")
        assert module == "my_module"
        assert name == "MyClass"

    def test_dotted_module_path(self):
        class_def = "render_system.some_processor:SomeProcessor"
        module, name = class_def.split(":")
        assert module == "render_system.some_processor"
        assert name == "SomeProcessor"
