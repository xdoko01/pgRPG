"""Tests for the fixed-timestep accumulator.

plan_steps is deliberately pure — no pygame, no clock, no globals — so the
loop's timing arithmetic is testable without a display.
"""

import pytest

from pgrpg.core.timestep import plan_steps

STEP_MS = 1000 / 60      # 16.666...
MAX_STEPS = 5


def test_steady_rate_runs_exactly_one_step():
    """A machine hitting the target rate steps once per frame."""
    n, acc = plan_steps(0.0, STEP_MS, STEP_MS, MAX_STEPS)

    assert n == 1
    assert acc == pytest.approx(0.0)


def test_short_frame_banks_time_without_stepping():
    """Half a step of real time runs no step and keeps the remainder."""
    n, acc = plan_steps(0.0, STEP_MS / 2, STEP_MS, MAX_STEPS)

    assert n == 0
    assert acc == pytest.approx(STEP_MS / 2)


def test_banked_time_is_spent_on_a_later_frame():
    """Two half-frames make one whole step."""
    n1, acc1 = plan_steps(0.0, STEP_MS / 2, STEP_MS, MAX_STEPS)
    n2, acc2 = plan_steps(acc1, STEP_MS / 2, STEP_MS, MAX_STEPS)

    assert (n1, n2) == (0, 1)
    assert acc2 == pytest.approx(0.0)


def test_slow_machine_alternates_one_and_two_steps():
    """40 fps against a 60 Hz sim averages 1.5 steps per frame."""
    real_dt = 25.0
    acc = 0.0
    counts = []
    for _ in range(4):
        n, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        counts.append(n)

    assert counts == [1, 2, 1, 2]


def test_long_stall_is_clamped_not_replayed():
    """A 3-second stall must not schedule 180 steps (spiral of death)."""
    n, acc = plan_steps(0.0, 3000.0, STEP_MS, MAX_STEPS)

    assert n == MAX_STEPS
    assert acc == pytest.approx(0.0)


def test_simulated_time_tracks_real_time_without_drift():
    """Over many uneven frames, stepped time stays within one step of real time."""
    frames = [16.4, 17.1, 15.9, 16.8, 16.2] * 200
    acc = 0.0
    total_steps = 0
    for real_dt in frames:
        n, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        total_steps += n

    stepped_ms = total_steps * STEP_MS
    assert abs(stepped_ms - sum(frames)) < STEP_MS


def test_accumulator_never_reaches_a_whole_step():
    """The returned remainder is always strictly less than one step."""
    acc = 0.0
    for real_dt in [0.1, 50.0, 16.0, 999.0, 3.3]:
        _, acc = plan_steps(acc, real_dt, STEP_MS, MAX_STEPS)
        assert 0.0 <= acc < STEP_MS


def test_non_positive_step_is_rejected():
    """A zero or negative step would divide by zero or loop forever."""
    with pytest.raises(ValueError):
        plan_steps(0.0, 16.0, 0.0, MAX_STEPS)
