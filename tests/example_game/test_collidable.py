"""Tests for the Collidable component's tile-relative extents.

A collision box describes the entity's body, and the body is drawn at
GAME["TILE_RES_PX"]. Authoring the box in tiles is what keeps the two in
proportion at any resolution.
"""

import pytest

import pgrpg.core.config as config
from core.components.collidable import Collidable


# The character body box, as authored against a 64 px tile: 15 x 27 px.
CHARACTER_X_TILES = 15 / 64
CHARACTER_Y_TILES = 27 / 64


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def test_tile_relative_extents_are_exact_at_64(tile_res):
    """The migrated values must reproduce the original pixels exactly at 64.

    Every authored half-extent divided by 64 is a dyadic rational, so it is
    represented exactly in binary floating point and multiplies back cleanly.
    Guards against the migration silently changing gameplay at the default.
    """
    tile_res(64)

    box = Collidable(x_tiles=CHARACTER_X_TILES, y_tiles=CHARACTER_Y_TILES)

    assert (box.x, box.y) == (15, 27)


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_tile_relative_extents_keep_their_proportion(tile_res_px, tile_res):
    """The box stays the same fraction of a tile at every resolution."""
    tile_res(tile_res_px)

    box = Collidable(x_tiles=CHARACTER_X_TILES, y_tiles=CHARACTER_Y_TILES)

    assert box.x / tile_res_px == pytest.approx(CHARACTER_X_TILES, abs=0.02)
    assert box.y / tile_res_px == pytest.approx(CHARACTER_Y_TILES, abs=0.02)


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_tile_relative_offsets_scale_too(tile_res_px, tile_res):
    """dx/dy shift the box centre in pixels, so they must scale as well.

    111 of the project's definitions carry a non-zero offset, typically dy=8.
    """
    tile_res(tile_res_px)

    box = Collidable(x_tiles=CHARACTER_X_TILES, y_tiles=CHARACTER_Y_TILES,
                     dx_tiles=0.0, dy_tiles=8 / 64)

    assert box.dy / tile_res_px == pytest.approx(8 / 64, abs=0.02)
    assert box.dx == 0


def test_absolute_pixel_extents_are_still_supported(tile_res):
    """Bare x/y stay literal pixels and are not scaled.

    Same contract as Position.x, so a box that genuinely must be a fixed pixel
    size can still be expressed.
    """
    tile_res(96)

    box = Collidable(x=15, y=27)

    assert (box.x, box.y) == (15, 27)


def test_extents_remain_integers(tile_res):
    """Downstream tile maths divides these, so they must stay ints."""
    tile_res(96)

    box = Collidable(x_tiles=CHARACTER_X_TILES, y_tiles=CHARACTER_Y_TILES)

    assert isinstance(box.x, int)
    assert isinstance(box.y, int)
    assert isinstance(box.dx, int)
    assert isinstance(box.dy, int)


def test_missing_extents_are_rejected(tile_res):
    """Neither form supplied is still an error."""
    tile_res(64)

    with pytest.raises(ValueError):
        Collidable()
