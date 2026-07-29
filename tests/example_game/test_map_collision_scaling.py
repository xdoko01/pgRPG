"""Map-collision behaviour across resolutions.

An entity standing still in a walkable tile must never be reported as hitting a
wall. Whether that holds must not depend on GAME["TILE_RES_PX"]: the collision
box describes the entity's body, and the body is drawn at TILE_RES_PX.
"""

from pathlib import Path

import pygame
import pytest

import pgrpg.core.maps.map as map_module
from pgrpg.core.ecs import World
from pgrpg.core.maps.map import Map

from core.components.collidable import Collidable
from core.components.position import Position
from core.processors.collision_system.resolve_map_collisions_processor import (
    ResolveMapCollisionsProcessor,
)


MAP_NAME = "game_sokoban_lvl01"

# The character body box: 92 of the project's 180 Collidable definitions use it.
# Authored as a fraction of a tile, which is 15 x 27 px at the default 64 px.
CHARACTER_BOX = {"x_tiles": 15 / 64, "y_tiles": 27 / 64}

# Sentinel for the "previous position" so a rollback is observable.
ROLLBACK_MARKER = (-1, -1)


@pytest.fixture(autouse=True)
def display_surface():
    pygame.display.set_mode((64, 64))
    yield


@pytest.fixture(autouse=True)
def map_path(monkeypatch):
    monkeypatch.setitem(
        map_module.FILEPATHS, "MAP_PATH", Path("example_game/resources/maps")
    )


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(map_module.GAME, "TILE_RES_PX", value)
    return _set


def _walkable_tile_beside_a_wall(game_map):
    """A walkable tile with at least one wall orthogonally adjacent.

    The ordinary case of standing next to a wall, and the case where an
    oversized collision box begins probing into that wall.
    """
    for y in range(game_map.tmxdata.height):
        for x in range(game_map.tmxdata.width):
            if not game_map.is_walkable((x, y)):
                continue
            if any(
                not game_map.is_walkable(n)
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            ):
                return (x, y)
    raise AssertionError("no walkable tile adjacent to a wall in the test map")


def _is_rolled_back(game_map, tile):
    """Place a stationary entity on tile, run the processor, report rollback.

    True means the processor decided the entity hit a wall.
    """
    world = World()
    processor = ResolveMapCollisionsProcessor(maps={MAP_NAME: game_map})
    world.add_processor(processor)

    position = Position(tile_x=tile[0], tile_y=tile[1], map=MAP_NAME)
    position.lastx, position.lasty = ROLLBACK_MARKER

    entity = world.create_entity(position, Collidable(**CHARACTER_BOX))
    processor.process()

    moved = world.component_for_entity(entity, Position)
    return (moved.x, moved.y) == ROLLBACK_MARKER


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_stationary_entity_beside_a_wall_is_not_reported_as_colliding(
    tile_res_px, tile_res
):
    """The character box must fit its own tile at every resolution.

    At 64 the box is 30x54 px in a 64 px tile and fits. The pixel values are
    fixed, so at 32 the same box is 30x54 px in a 32 px tile - nearly two tiles
    tall - and its corner probes reach into the neighbouring wall, wrongly
    shoving a standing entity back to its previous position.
    """
    tile_res(tile_res_px)
    game_map = Map(map_name=MAP_NAME)
    tile = _walkable_tile_beside_a_wall(game_map)

    assert not _is_rolled_back(game_map, tile), (
        f"entity standing on walkable tile {tile} was reported as hitting a wall "
        f"at TILE_RES_PX={tile_res_px}"
    )


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_collision_box_keeps_its_proportion_of_a_tile(tile_res_px, tile_res):
    """The box must stay the same fraction of a tile at every resolution.

    This is the invariant behind both failure modes. The box describes the
    entity's body and the body is drawn at TILE_RES_PX, so the ratio has to
    hold. Authored against a 64 px tile, 15x27 means 0.47 x 0.84 of a tile.

    Too large a ratio (at 32) probes into neighbouring tiles and the entity gets
    stuck; too small (at 96) lets the drawn sprite sink into walls before
    anything collides.
    """
    tile_res(tile_res_px)

    box = Collidable(**CHARACTER_BOX)

    expected_x = CHARACTER_BOX["x_tiles"]
    expected_y = CHARACTER_BOX["y_tiles"]

    assert box.x / tile_res_px == pytest.approx(expected_x, abs=0.02), (
        f"box half-width is {box.x / tile_res_px:.2f} of a tile at "
        f"TILE_RES_PX={tile_res_px}, expected {expected_x:.2f}"
    )
    assert box.y / tile_res_px == pytest.approx(expected_y, abs=0.02), (
        f"box half-height is {box.y / tile_res_px:.2f} of a tile at "
        f"TILE_RES_PX={tile_res_px}, expected {expected_y:.2f}"
    )


@pytest.mark.parametrize("tile_res_px", [32, 64, 96])
def test_collision_box_fits_within_one_tile(tile_res_px, tile_res):
    """The box must stay within a tile, so four-corner probing is sound.

    resolve_map_collisions_processor samples only the four corners of the box.
    A box wider or taller than a tile can straddle a wall tile lying between
    those corners, missing it entirely so the entity walks through the wall.
    """
    tile_res(tile_res_px)

    box = Collidable(**CHARACTER_BOX)

    assert 2 * box.x <= tile_res_px, f"box width {2 * box.x}px exceeds tile {tile_res_px}px"
    assert 2 * box.y <= tile_res_px, f"box height {2 * box.y}px exceeds tile {tile_res_px}px"
