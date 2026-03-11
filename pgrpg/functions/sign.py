"""Sign functions for numeric values."""

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)
"""Return the sign of x: -1, 0, or 1."""

sign_wo_zero = lambda x: -1 if x < 0 else 1
"""Return the sign of x without zero: -1 or 1."""
