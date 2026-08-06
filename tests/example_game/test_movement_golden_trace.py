"""A reference movement trace captured before the fixed-timestep change.

At TILE_RES_PX 64 the migration in Task 8 converts every velocity by an exact
power-of-two division, so movement must remain numerically identical. This
test is the evidence for that claim: it is written against the pre-change code
and must still pass after Task 8.
"""

import pytest

import pgrpg.core.config as config
from pgrpg.core.ecs import World
from core.components.position import Position
from core.components.movable import Movable
from core.components.flag_do_move import FlagDoMove
from core.processors.movement_system.perform_movement_processor import PerformMovementProcessor

STEP_MS = 1000 / 60
STEPS = 10


@pytest.fixture
def tile_res(monkeypatch):
    def _set(value):
        monkeypatch.setitem(config.GAME, "TILE_RES_PX", value)
    return _set


def build_moving_entity(world, velocity, accelerate=0):
    """Create an entity at tile (0,0) moving right at `velocity`.

    `velocity` is in whatever unit Movable currently accepts: pixels/second
    before Task 6, tiles/second after. Callers convert.
    """
    return world.create_entity(
        Position(x=0, y=0, map="test_map"),
        Movable(velocity=velocity, accelerate=accelerate),
        FlagDoMove(moves=["right"]),
    )


def run_trace(world, entity, steps=STEPS, step_ms=STEP_MS):
    """Process `steps` fixed steps, returning the position after each."""
    proc = PerformMovementProcessor()
    proc.world = world
    trace = []
    for _ in range(steps):
        world.add_component(entity, FlagDoMove(moves=["right"]))
        proc.process(dt=step_ms)
        pos = world.component_for_entity(entity, Position)
        trace.append((pos.x, pos.y))
    return trace


def test_golden_trace_at_64px(tile_res):
    """velocity 100 px/s at 64 px, 60 Hz, 10 steps: 1.5625 tiles/s."""
    tile_res(64)
    world = World()
    # Task 8 replaces `100` with `100 / 64` here — the trace must not change.
    entity = build_moving_entity(world, velocity=100)

    trace = run_trace(world, entity)

    assert trace[0] == pytest.approx((100 * STEP_MS / 1000, 0.0))
    assert trace[-1] == pytest.approx((100 * STEPS * STEP_MS / 1000, 0.0))
    assert len(trace) == STEPS
