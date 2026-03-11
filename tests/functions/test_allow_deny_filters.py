import pytest

from pgrpg.functions.allow_deny_filters import (
    allow_deny_list_filter,
    allow_deny_item_filter,
)


class TestAllowDenyListFilter:
    def test_empty_both_passes_all(self):
        result = allow_deny_list_filter({1, 2, 3}, set(), set())
        assert result == {1, 2, 3}

    def test_allowlist_only(self):
        result = allow_deny_list_filter({1, 2, 3, 4}, {1, 2}, set())
        assert result == {1, 2}

    def test_denylist_only(self):
        result = allow_deny_list_filter({1, 2, 3, 4}, set(), {3, 4})
        assert result == {1, 2}

    def test_denylist_all_blocks_everything(self):
        result = allow_deny_list_filter({1, 2, 3}, set(), {"ALL"})
        assert result == set()

    def test_allowlist_and_denylist_combined(self):
        result = allow_deny_list_filter({1, 2, 3, 4, 5}, {2, 3, 4}, {3})
        assert result == {2, 4}


class TestAllowDenyItemFilter:
    def test_empty_both_allows(self):
        assert allow_deny_item_filter(5) is True

    def test_in_allowlist(self):
        assert allow_deny_item_filter(1, allowlist={1, 2}) is True

    def test_not_in_allowlist(self):
        assert allow_deny_item_filter(3, allowlist={1, 2}) is False

    def test_in_denylist(self):
        assert allow_deny_item_filter(2, denylist={2, 3}) is False

    def test_not_in_denylist(self):
        assert allow_deny_item_filter(1, denylist={2, 3}) is True

    def test_denylist_all_blocks(self):
        assert allow_deny_item_filter(1, denylist={"ALL"}) is False
