"""Tests for engine configuration defaults and merging.

Guards the rule that a game config may omit a section and still get a usable
value from pgrpg/core/config/defaults.jsonc.
"""

import json

import pytest

import pgrpg.core.config as config


# Sections a game config must supply because the engine currently ships no
# defaults for them. GAME is deliberately absent — that is what these tests
# are about.
_MINIMAL_GAME_CONFIG = {
    "FILEPATHS": {
        "GAME_PATH": "example_game",
        "pgrpg_PATH": "pgrpg",
    },
    "DISPLAY": {
        "RESOLUTION": [640, 480],
        "FULLSCREEN": False,
    },
    "MODULEPATHS": {
        "CONSOLE_COMMAND_MODULE_PATH": "core.console.commands",
        "SCRIPT_MODULE_PATH": "core.scripts",
        "COMMAND_MODULE_PATH": "core.commands",
        "PROCESSOR_MODULE_PATH": "core.processors",
        "COMPONENT_MODULE_PATH": "core.components",
        "STATE_MODULE_PATH": "core.states",
    },
    "FONTS": {
        "GAME_INVENTORY_FONT": "good_neighbours_font.json",
        "GAME_DEBUG_FONT": "small_font.json",
        "PLAYER_TALK_FONT": "good_neighbours_font.json",
        "GAME_MSG_FONT": "good_neighbours_font.json",
        "GUI_MANAGER_FONT": "good_neighbours_font.json",
    },
    "FRAMES": {
        "PLAYER_TALK_FRAME": "small_frame.json",
        "GAME_DEBUG_FRAME": "debug_frame.json",
    },
}


@pytest.fixture
def restore_config():
    """Snapshot and restore config module globals.

    config.load() writes to module-level globals, so a test that calls it
    would otherwise leak state into the rest of the session.
    """
    names = [
        "pgrpg", "LOGGING", "CONSOLE", "DISPLAY", "GUI", "SOUND", "KEYS",
        "FILEPATHS", "GAME", "MESSAGES", "MODULEPATHS", "FONTS", "FRAMES",
        "STATES", "CONFIG_FILEPATH",
    ]
    saved = {name: getattr(config, name) for name in names}
    yield
    for name, value in saved.items():
        setattr(config, name, value)


@pytest.fixture
def config_without_game_section(tmp_path):
    """Write a valid game config that omits the GAME section entirely."""
    path = tmp_path / "config_no_game.jsonc"
    path.write_text(json.dumps(_MINIMAL_GAME_CONFIG), encoding="utf-8")
    return path


def test_tile_res_px_has_engine_default(config_without_game_section, restore_config):
    """A game config omitting GAME still gets TILE_RES_PX from the engine.

    Would fail if defaults.jsonc lost its GAME section: GAME would merge to {}
    and every GAME["TILE_RES_PX"] read in the engine would raise KeyError.
    """
    config.load(config_file=config_without_game_section)

    assert config.GAME["TILE_RES_PX"] == 64


def test_game_config_overrides_tile_res_px_default(tmp_path, restore_config):
    """A game config setting TILE_RES_PX wins over the engine default."""
    overridden = dict(_MINIMAL_GAME_CONFIG, GAME={"TILE_RES_PX": 96})
    path = tmp_path / "config_tile_96.jsonc"
    path.write_text(json.dumps(overridden), encoding="utf-8")

    config.load(config_file=path)

    assert config.GAME["TILE_RES_PX"] == 96
