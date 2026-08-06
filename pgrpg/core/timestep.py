"""Fixed-timestep accumulator arithmetic for the main loop.

The game keeps two clocks. Real time is a property of the hardware — how often
this machine can draw a frame. Simulated time is a property of the game — it
advances only in constant chunks of ``1000 / GAME["SIM_HZ"]`` milliseconds.
This module owns the arithmetic that converts the first into the second.

Deliberately free of pygame and of any global state, so the loop's timing can
be unit-tested without a display. See
``.claude/kb/core/bootstrap-and-loop.md``.
"""

# Keep `tuple[int, float]` annotations working on Python 3.9, which evaluates them eagerly.
from __future__ import annotations

__all__ = ['plan_steps']


def plan_steps(accumulator_ms: float,
               real_dt_ms: float,
               step_ms: float,
               max_steps: int) -> tuple[int, float]:
    """Decide how many fixed simulation steps this real frame should run.

    The accumulator is a bank of unspent real time. Real time arrives in
    uneven amounts; it is withdrawn only in whole ``step_ms`` units, and the
    remainder carries to the next frame. Over any interval, simulated time
    therefore tracks real time without drift.

    ``real_dt_ms`` is clamped to ``max_steps * step_ms`` *before* being
    banked. This is what prevents the spiral of death: after a long stall
    (scene load, breakpoint, window drag) an unclamped loop would schedule
    hundreds of steps, each costing time, enlarging the next ``real_dt_ms``
    and scheduling still more. Clamping discards simulated time instead —
    correct, because the player was not playing, and the alternatives are a
    frozen game or an entity teleporting across the map.

    Args:
        accumulator_ms: Unspent real time carried from the previous frame.
            Always less than ``step_ms``.
        real_dt_ms: Real milliseconds elapsed since the previous frame.
        step_ms: Length of one simulation step in milliseconds.
        max_steps: Most steps a single frame may run.

    Returns:
        Tuple of (steps to run this frame, accumulator for the next frame).
        The returned accumulator is always in ``[0, step_ms)``.

    Raises:
        ValueError: If ``step_ms`` is not positive.

    Tests:
        >>> n, acc = plan_steps(0.0, 1000 / 60, 1000 / 60, 5)
        >>> n
        1
        >>> round(acc, 9)
        0.0
        >>> plan_steps(0.0, 3000.0, 1000 / 60, 5)[0]   # a 3-second stall
        5
    """
    if step_ms <= 0:
        raise ValueError(f'step_ms must be positive, got {step_ms}.')

    # Clamp before banking — see the spiral-of-death note above.
    budget_ms = accumulator_ms + min(real_dt_ms, max_steps * step_ms)

    # A tiny epsilon guards against float error understating a budget that is
    # exactly (or almost exactly) a whole number of steps — e.g. repeatedly
    # summing 1000/60 can land a hair below the next multiple, which would
    # otherwise bank a spurious near-full step and drift the sim clock.
    steps = int((budget_ms + 1e-9) // step_ms)

    # Defensive: a caller passing an over-large accumulator cannot exceed the cap.
    steps = min(steps, max_steps)

    # Clamp against the same epsilon pushing the remainder a hair below zero.
    return steps, max(0.0, budget_ms - steps * step_ms)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
