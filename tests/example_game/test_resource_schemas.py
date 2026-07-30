"""Validate every component definition in the game resources against its schema.

The JSON Schemas under example_game/core/schemas/ are authoring aids: nothing
loads them at runtime. Without a check like this they drift silently from the
resources they describe, which is exactly what happened before #80 - a `$ref`
beside `properties` suppressed the validation, so the schemas went years without
being exercised.

This is a ratchet, not a clean bill of health. A known set of violations remains
(see KNOWN_VIOLATIONS); the test fails if a *new* component type starts
violating, or if a known one gets worse.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

from pgrpg.functions import get_dict_from_file

jsonschema = pytest.importorskip(
    "jsonschema",
    reason="schema validation needs the 'test' extra: pip install -e .[test]",
)
from jsonschema import Draft202012Validator  # noqa: E402
from referencing import Registry, Resource  # noqa: E402
from referencing.jsonschema import DRAFT202012  # noqa: E402


SCHEMA_ROOT = Path("example_game/core/schemas")
COMPONENT_SCHEMAS = SCHEMA_ROOT / "components"
RESOURCES = Path("example_game/resources")

# Component types with violations that are known and not yet resolved. Counts are
# ceilings: fixing some is fine, adding any is not. Lower the number when you fix
# them, and delete the entry when it reaches zero.
#
# brain_ai: the command-generator schema
#   (commands/generators/generator.schema.json#/command_generator) has drifted
#   from the cmd_list / cmd_tree / blackboard shapes the resources actually use.
#   Reconciling it is engine design work, tracked in the follow-up.
# btree: entities/_special/{guard,hunter}.json pass "tree" where the BTreeAI
#   component reads "cmd_tree". A genuine data bug, in kill_all content already
#   marked as needing rework.
KNOWN_VIOLATIONS = {
    "brain_ai:BrainAI": 32,
    "btree:BTree": 2,
}


@pytest.fixture(scope="module")
def registry():
    """Every schema file, keyed by its path relative to the schemas root.

    Eager rather than lazy: Registry is immutable, so a retrieve callback would
    re-read from disk on every validation and make this unusably slow.

    Keys must be the true relative path and nothing else. Registering bare
    basenames as aliases collides - commands/generators/btree.schema.json and
    components/btree.schema.json share one - and the wrong resolution surfaces as
    a phantom "valid under each of" ambiguity.
    """
    resources = {}
    for path in sorted(SCHEMA_ROOT.rglob("*.json")):
        resources[path.relative_to(SCHEMA_ROOT).as_posix()] = Resource.from_contents(
            json.loads(path.read_text(encoding="utf-8")),
            default_specification=DRAFT202012,
        )
    return Registry().with_resources(resources.items())


@pytest.fixture(scope="module")
def validators(registry):
    """Map each component `type` string to a validator for its schema."""
    index = {}
    for path in sorted(COMPONENT_SCHEMAS.rglob("*.json")):
        if "_old" in path.parts:
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        for type_string in schema.get("properties", {}).get("type", {}).get("enum", []):
            index[type_string] = Draft202012Validator(schema, registry=registry)
    return index


def _components(node, out):
    """Collect every dict that looks like a component definition."""
    if isinstance(node, dict):
        if isinstance(node.get("type"), str) and "params" in node:
            out.append(node)
        for value in node.values():
            _components(value, out)
    elif isinstance(node, list):
        for value in node:
            _components(value, out)
    return out


@pytest.fixture(scope="module")
def resource_components():
    """Every component definition found in the resources, with its file."""
    found = []
    files = (
        set(RESOURCES.rglob("*.jsonc"))
        | set(RESOURCES.rglob("*.json"))
        | set(RESOURCES.rglob("*.yaml"))
    )
    for path in sorted(files):
        try:
            data = get_dict_from_file(filepath=path)
        except Exception:
            continue  # not a resource document; other tests cover parsing
        for component in _components(data, []):
            found.append((path, component))
    return found


@pytest.fixture(scope="module")
def violations(validators, resource_components):
    """(type_string, file, message) for every component that fails its schema."""
    out = []
    for path, component in resource_components:
        validator = validators.get(component["type"])
        if validator is None:
            continue
        try:
            errors = list(validator.iter_errors(component))
        except Exception as exc:  # unresolvable $ref, malformed schema
            out.append((component["type"], path, f"schema error: {exc}"))
            continue
        for error in errors:
            out.append((component["type"], path, error.message))
    return out


def test_resources_are_discovered(resource_components, validators):
    """Guard against the sweep silently finding nothing.

    Without this, a bad glob or a renamed directory would make every other test
    here pass by validating zero components.
    """
    assert len(validators) > 40
    assert len(resource_components) > 1000


def test_no_unexpected_component_type_violates_its_schema(violations):
    """Only the documented component types may violate."""
    offending = {type_string for type_string, _, _ in violations}
    unexpected = offending - set(KNOWN_VIOLATIONS)

    detail = "\n".join(
        f"  {t}  {p}\n      {m[:120]}"
        for t, p, m in violations
        if t in unexpected
    )
    assert not unexpected, (
        f"component types newly violating their schema: {sorted(unexpected)}\n{detail}"
    )


def test_known_violations_do_not_grow(violations):
    """Known violation counts are ceilings, so regressions fail the build."""
    counts = Counter(type_string for type_string, _, _ in violations)

    grown = {
        t: (counts[t], ceiling)
        for t, ceiling in KNOWN_VIOLATIONS.items()
        if counts[t] > ceiling
    }
    assert not grown, f"violations increased (actual, ceiling): {grown}"


def test_every_schema_is_a_valid_2020_12_schema():
    """The schemas themselves must be well-formed.

    They declare 2020-12 and rely on `prefixItems`, which draft-07 ignores - the
    mismatch that silently disabled tuple validation across 148 files.
    """
    invalid = []
    for path in sorted(SCHEMA_ROOT.rglob("*.json")):
        try:
            Draft202012Validator.check_schema(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except Exception as exc:
            invalid.append(f"{path.relative_to(SCHEMA_ROOT)}: {exc}")
    assert not invalid, "invalid schemas:\n" + "\n".join(invalid)


def test_no_ref_sits_beside_keywords_it_would_suppress():
    """Keep #80 fixed.

    2020-12 permits siblings beside `$ref`, so this is no longer fatal, but the
    schemas are also consumed by editors whose draft support varies. Keeping the
    reference inside `allOf` stays unambiguous under either draft.
    """
    suppressed = {"properties", "required", "anyOf", "allOf", "oneOf", "not"}
    offenders = []

    def walk(node, path, filename):
        if isinstance(node, dict):
            if "$ref" in node and (suppressed & set(node)):
                offenders.append(f"{filename}{path}")
            for key, value in node.items():
                walk(value, f"{path}/{key}", filename)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]", filename)

    for path in sorted(SCHEMA_ROOT.rglob("*.json")):
        walk(
            json.loads(path.read_text(encoding="utf-8")),
            "",
            path.relative_to(SCHEMA_ROOT).as_posix(),
        )

    assert not offenders, (
        "$ref beside keywords it suppresses under draft-07:\n  " + "\n  ".join(offenders)
    )
