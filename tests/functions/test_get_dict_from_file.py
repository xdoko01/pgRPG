import json
import pytest
from pathlib import Path

from pgrpg.functions.get_dict_from_file import get_dict_from_file


class TestLoadJson:
    def test_load_json_file(self, tmp_path):
        data = {"key": "value", "num": 42}
        filepath = tmp_path / "test.json"
        filepath.write_text(json.dumps(data))

        result = get_dict_from_file(filepath=filepath)
        assert result == data


class TestLoadJsonc:
    def test_jsonc_comment_stripped(self, tmp_path):
        content = '{\n  // This is a comment\n  "key": "value"\n}'
        filepath = tmp_path / "test.jsonc"
        filepath.write_text(content)

        result = get_dict_from_file(filepath=filepath)
        assert result == {"key": "value"}


class TestMissingFile:
    def test_missing_file_raises_error(self, tmp_path):
        filepath = tmp_path / "nonexistent.json"
        with pytest.raises((FileNotFoundError, ValueError)):
            get_dict_from_file(filepath=filepath)
