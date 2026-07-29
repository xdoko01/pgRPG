"""Tests for example_game.core.processors.functions.

Focus: the camera visibility filter must scale its cull margin with the
configured resolution. Sprites are blitted centred on their position (see
RenderableModel.topleft, which subtracts half the model size), so an entity up
to half a sprite outside the camera rect is still partly on screen and must not
be culled.
"""

import pytest

import pgrpg.core.config as config
from core.processors.functions import filter_only_visible_on_camera


CAMERA_RECT = (0, 0, 640, 480)


class FakeCamera:
    """Minimal stand-in exposing only what the filter reads."""

    def __init__(self, map_screen_rect):
        self.map_screen_rect = map_screen_rect


class FakePosition:
    """Minimal stand-in exposing only what the filter reads."""

    def __init__(self, x, y):
        self.x = x
        self.y = y


def _entity_at(x, y):
    """Build the (entity_id, (position, ...)) tuple the filter expects."""
    return (1, (FakePosition(x, y),))


@pytest.fixture
def camera():
    return FakeCamera(CAMERA_RECT)


@pytest.fixture
def tile_res(monkeypatch):
    """Set GAME["TILE_RES_PX"] for the duration of a test.

    Patches the dict in place, which is the same object the game modules bound
    at import time.
    """
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def test_sprite_half_outside_left_edge_is_visible_at_large_tile_res(camera, tile_res):
    """At 128px, an entity 40px off the left edge is still half on screen.

    Would fail if the margin were fixed at 32: 40 > 32, so the entity would be
    culled while three quarters of its sprite was still visible.
    """
    tile_res(128)

    assert filter_only_visible_on_camera(camera, _entity_at(-40, 240)) is True


def test_sprite_fully_outside_left_edge_is_culled_at_large_tile_res(camera, tile_res):
    """At 128px the margin is 64, so 70px out is genuinely off screen."""
    tile_res(128)

    assert filter_only_visible_on_camera(camera, _entity_at(-70, 240)) is False


def test_margin_is_half_a_tile_at_the_default_resolution(camera, tile_res):
    """At 64px the derived margin is 32 - the value previously hardcoded.

    Pins the derivation to half a tile rather than to any particular number.
    """
    tile_res(64)

    assert filter_only_visible_on_camera(camera, _entity_at(-20, 240)) is True
    assert filter_only_visible_on_camera(camera, _entity_at(-40, 240)) is False


def test_margin_scales_on_every_edge(camera, tile_res):
    """The derived margin applies to right and bottom edges too, not just left."""
    tile_res(128)

    assert filter_only_visible_on_camera(camera, _entity_at(680, 240)) is True
    assert filter_only_visible_on_camera(camera, _entity_at(320, 520)) is True
    assert filter_only_visible_on_camera(camera, _entity_at(710, 240)) is False
    assert filter_only_visible_on_camera(camera, _entity_at(320, 550)) is False


def test_entity_inside_the_camera_rect_is_visible(camera, tile_res):
    """The ordinary case: well inside the view."""
    tile_res(64)

    assert filter_only_visible_on_camera(camera, _entity_at(320, 240)) is True


def test_explicit_corr_overrides_the_derived_margin(camera, tile_res):
    """Callers can still pass an explicit margin."""
    tile_res(128)

    assert filter_only_visible_on_camera(camera, _entity_at(-40, 240), corr=8) is False
