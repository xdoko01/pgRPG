import pytest
from unittest.mock import MagicMock

from pgrpg.functions.json_logic import json_logic, get_var


class TestGetVar:
    def test_existing_key(self):
        assert get_var({"a": 10}, "a") == 10

    def test_missing_key_returns_none(self):
        assert get_var({"a": 10}, "b") is None

    def test_none_data_returns_none(self):
        assert get_var(None, "a") is None


class TestJsonLogicLiterals:
    def test_literal_string(self):
        assert json_logic(expr="hello") == "hello"

    def test_literal_number(self):
        assert json_logic(expr=42) == 42

    def test_literal_bool(self):
        assert json_logic(expr=True) is True

    def test_literal_with_value_fnc(self):
        assert json_logic(expr=5, value_fnc=lambda x: x * 2) == 10


class TestJsonLogicEmptyList:
    def test_empty_list_returns_true(self):
        assert json_logic(expr=[]) is True


class TestJsonLogicAnd:
    def test_and_all_true(self):
        assert json_logic(expr=["AND", True, True, True]) is True

    def test_and_one_false(self):
        assert not json_logic(expr=["AND", True, False, True])


class TestJsonLogicOr:
    def test_or_one_true(self):
        assert json_logic(expr=["OR", False, True, False]) is True

    def test_or_all_false(self):
        assert not json_logic(expr=["OR", False, False])


class TestJsonLogicOneof:
    def test_oneof_exactly_one_true(self):
        assert json_logic(expr=["ONEOF", True, False, False]) is True

    def test_oneof_two_true(self):
        assert json_logic(expr=["ONEOF", True, True, False]) is False

    def test_oneof_none_true(self):
        assert json_logic(expr=["ONEOF", False, False]) is False


class TestJsonLogicVar:
    def test_var_returns_value(self):
        assert json_logic(expr=["VAR", "x"], data={"x": 99}) == 99

    def test_var_missing_returns_none(self):
        assert json_logic(expr=["VAR", "missing"], data={"x": 1}) is None


class TestJsonLogicList:
    def test_list_returns_list(self):
        assert json_logic(expr=["LIST", [1, 2, 3]]) == [1, 2, 3]

    def test_list_with_value_fnc(self):
        result = json_logic(expr=["LIST", [10, 20]], value_fnc=lambda x: x)
        assert result == [10, 20]


class TestJsonLogicIf:
    def test_if_true_branch(self):
        result = json_logic(expr=["IF", True, "yes"])
        assert result == "yes"

    def test_if_false_branch_returns_none(self):
        result = json_logic(expr=["IF", False, "yes"])
        assert result is None


class TestJsonLogicScript:
    def test_script_calls_script_fnc(self):
        mock_script = MagicMock(return_value="done")
        result = json_logic(
            expr=["SCRIPT", "my_script", {"arg": 1}],
            script_fnc=mock_script,
        )
        mock_script.assert_called_once_with("my_script", {"arg": 1})
        assert result == "done"


class TestJsonLogicIn:
    def test_in_found(self):
        data = {"items": [1, 2, 3]}
        assert json_logic(expr=["IN", ["VAR", "val"], ["VAR", "items"]], data={"val": 2, "items": [1, 2, 3]}) is True

    def test_in_not_found(self):
        assert json_logic(expr=["IN", ["VAR", "val"], ["VAR", "items"]], data={"val": 9, "items": [1, 2, 3]}) is False


class TestJsonLogicErrors:
    def test_unknown_operator_raises_value_error(self):
        with pytest.raises(ValueError, match="Not supported logical operator"):
            json_logic(expr=["NOTREAL", True])

    def test_data_must_be_dict(self):
        with pytest.raises(AssertionError):
            json_logic(expr="x", data="not_a_dict")
