"""Tests for pgrpg.core.maps.map — load-time normalization of tile images.

The project's tilesets are authored at 32x32 while its models are 64x64. The
engine absorbs that by scaling every tile image to GAME["TILE_RES_PX"] when the
map is loaded, so no part of the engine needs to know an asset's native size.
These tests pin that down at several resolutions, including one that is not an
integer multiple of the 32px source art.
"""

from pathlib import Path

import pygame
import pytest

import pgrpg.core.maps.map as map_module
from pgrpg.core.maps.map import Map, images_rescale


# Small map (10x11 tiles, 3 layers) drawn from a 32x32 native tileset.
# Small matters: Map builds a pathfinding graph and a full-size pre-rendered
# surface per layer at construction time.
SMALL_MAP = "game_sokoban_lvl01"

NATIVE_TILESET_RES = 32


@pytest.fixture(autouse=True)
def display_surface():
    """pytmx converts loaded tiles, which needs a display surface."""
    pygame.display.set_mode((64, 64))
    yield


@pytest.fixture(autouse=True)
def map_path(monkeypatch):
    """Point MAP_PATH at the example game's maps without loading a full config.

    Patches the dict in place — it is the same object map.py bound at import.
    """
    monkeypatch.setitem(
        map_module.FILEPATHS, "MAP_PATH", Path("example_game/resources/maps")
    )


@pytest.fixture
def tile_res(monkeypatch):
    """Set GAME["TILE_RES_PX"] for the duration of a test."""
    def _set(value):
        monkeypatch.setitem(map_module.GAME, "TILE_RES_PX", value)
    return _set


@pytest.mark.parametrize("target", [32, 64, 96])
def test_every_tile_image_is_scaled_to_the_configured_resolution(target, tile_res):
    """All tile images come out at TILE_RES_PX regardless of native size.

    96 is the important case: neither a power of two nor an integer multiple of
    the 32px source tiles. Would fail if any scale target were hardcoded.
    """
    tile_res(target)

    game_map = Map(map_name=SMALL_MAP)

    rendered_sizes = {img.get_size() for img in game_map.tmxdata.images if img}
    assert rendered_sizes == {(target, target)}


@pytest.mark.parametrize("target", [32, 64, 96])
def test_map_pixel_dimensions_follow_the_configured_resolution(target, tile_res):
    """Map pixel size is tile count times TILE_RES_PX, not times native size."""
    tile_res(target)

    game_map = Map(map_name=SMALL_MAP)

    assert game_map.width == game_map.tmxdata.width * target
    assert game_map.height == game_map.tmxdata.height * target


@pytest.mark.parametrize("target", [32, 96])
def test_prerendered_layer_surfaces_match_the_map_pixel_size(target, tile_res):
    """The pre-rendered static surfaces are built at the scaled map size.

    Guards the tile_px used by _build_static_surfaces against drifting away
    from the value used for map.width/height, which would misalign every
    blitted layer.
    """
    tile_res(target)

    game_map = Map(map_name=SMALL_MAP)

    assert game_map.static_surfaces
    for surface in game_map.static_surfaces.values():
        assert surface.get_size() == (game_map.width, game_map.height)


def test_native_resolution_tileset_is_left_at_its_own_size(tile_res):
    """Setting TILE_RES_PX to the tileset's native size is a no-op scale."""
    tile_res(NATIVE_TILESET_RES)

    game_map = Map(map_name=SMALL_MAP)

    rendered_sizes = {img.get_size() for img in game_map.tmxdata.images if img}
    assert rendered_sizes == {(NATIVE_TILESET_RES, NATIVE_TILESET_RES)}


def test_images_rescale_requires_an_explicit_target_size():
    """images_rescale must not fall back to a hardcoded size.

    A (64, 64) default produced correct output only for as long as TILE_RES_PX
    happened to be 64; at any other resolution it would silently scale tiles to
    the wrong size. The caller has to say what it wants.
    """
    source = [pygame.Surface((NATIVE_TILESET_RES, NATIVE_TILESET_RES))]

    with pytest.raises(TypeError):
        images_rescale(source)


def test_images_rescale_scales_surfaces_and_passes_gaps_through():
    """Tiles are scaled to the requested size; empty tile slots stay None.

    pytmx leaves None in its image list for unused GIDs, and the map's tile
    lookup relies on those staying None rather than becoming blank surfaces.
    """
    source = [pygame.Surface((NATIVE_TILESET_RES, NATIVE_TILESET_RES)), None]

    result = images_rescale(source, (96, 96))

    assert result[0].get_size() == (96, 96)
    assert result[1] is None


def test_tile_lookup_by_pixel_rect_uses_the_configured_resolution(tile_res):
    """Camera-rect to tile-range conversion scales with TILE_RES_PX.

    At 64px a 128px-wide rect spans 2 tile columns; at 32px it spans 4.
    """
    tile_res(64)
    game_map = Map(map_name=SMALL_MAP)
    at_64 = {x for x, _, _ in game_map.get_tile_images_by_rect(0, (0, 0, 127, 127))}

    tile_res(32)
    game_map = Map(map_name=SMALL_MAP)
    at_32 = {x for x, _, _ in game_map.get_tile_images_by_rect(0, (0, 0, 127, 127))}

    assert max(at_64) < max(at_32)
