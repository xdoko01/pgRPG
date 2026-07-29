"""Tests for pgrpg.core.models.model — load-time normalization of models.

Every model is scaled to a single target resolution when it is loaded. These
tests pin down that the target is honoured whatever the asset's native size,
and that the model cache cannot serve a model whose pixels were scaled for a
different target.
"""

from pathlib import Path

import pygame
import pytest

import pgrpg.core.models.model as model_module
from pgrpg.core.models.model import clear_cache, load_model


MODEL_DIR = Path("example_game/resources/models")

# Native 64x64 - the resolution almost every model in the project uses.
MODEL_64 = MODEL_DIR / "darkfemale.json"

# Native 32x32 - an in-use asset that must be upscaled to the target.
MODEL_32 = MODEL_DIR / "generic" / "item" / "coin_gold.json"


@pytest.fixture(autouse=True)
def display_surface():
    """Model loading calls Surface.convert(), which needs a display surface.

    The dummy SDL video driver from conftest makes this work headlessly.
    """
    pygame.display.set_mode((64, 64))
    yield


@pytest.fixture(autouse=True)
def clean_model_cache():
    """Start and end each test with an empty model cache.

    Model is lru_cache'd, so without this a model loaded by an earlier test
    would be reused here and the test would not exercise a real load.
    """
    clear_cache()
    yield
    clear_cache()


def _idle_frame_bytes(m):
    """Raw pixels of the model's canonical static frame, for exact comparison."""
    return pygame.image.tobytes(m.get_idle_image(), "RGBA")


@pytest.mark.parametrize("target", [32, 64, 96])
def test_native_64_model_is_normalized_to_target(target):
    """A 64px model reports the requested target size, up or down.

    96 matters: it is neither a power of two nor an integer multiple of 64.
    Would fail if load_model stopped scaling, or scaled to a hardcoded size.
    """
    m = load_model(MODEL_64, (target, target))

    assert (m.dim.x, m.dim.y) == (target, target)
    assert m.get_idle_image().get_size() == (target, target)


@pytest.mark.parametrize("target", [32, 64, 96])
def test_native_32_model_is_normalized_to_target(target):
    """A 32px asset (coin_gold) is scaled to the target like any other.

    This is the upscale path that produces the tile/sprite mismatch the
    normalization contract exists to absorb.
    """
    m = load_model(MODEL_32, (target, target))

    assert (m.dim.x, m.dim.y) == (target, target)
    assert m.get_idle_image().get_size() == (target, target)


def test_loading_at_one_target_does_not_corrupt_a_later_load_at_another():
    """Pixels must never be scaled twice by successive loads.

    Model is cached on the model file. If a load mutates the cached instance
    in place, then loading at 32 and then at 64 returns images that were
    downscaled to 32 and blown back up to 64, instead of the pristine native
    64px art. Sizes look right either way, so this asserts on pixel content.
    """
    pristine_64 = _idle_frame_bytes(load_model(MODEL_64, (64, 64)))

    clear_cache()
    load_model(MODEL_64, (32, 32))
    after_32_then_64 = _idle_frame_bytes(load_model(MODEL_64, (64, 64)))

    assert after_32_then_64 == pristine_64


def test_concurrently_held_models_at_different_targets_stay_independent():
    """Two live references at different targets must not share scaled pixels.

    Holding a 32px and a 64px view of the same model file at once is what a
    zoom level or an inventory thumbnail would need. If the cache is keyed on
    the filename alone, the second load resizes the object the first caller is
    still holding.
    """
    small = load_model(MODEL_64, (32, 32))
    large = load_model(MODEL_64, (64, 64))

    assert small.get_idle_image().get_size() == (32, 32)
    assert large.get_idle_image().get_size() == (64, 64)


def test_repeated_load_at_same_target_returns_the_cached_model():
    """Identical requests are served from cache rather than re-decoded."""
    first = load_model(MODEL_64, (64, 64))
    second = load_model(MODEL_64, (64, 64))

    assert first is second
