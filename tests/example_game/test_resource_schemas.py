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
import os
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


@pytest.fixture(scope="module")
def resource_documents():
    """Every parseable resource document, with its path."""
    files = (
        set(RESOURCES.rglob("*.jsonc"))
        | set(RESOURCES.rglob("*.json"))
        | set(RESOURCES.rglob("*.yaml"))
    )
    out = []
    for path in sorted(files):
        try:
            out.append((path, get_dict_from_file(filepath=path)))
        except Exception:
            continue  # not a resource document; other tests cover parsing
    return out


def _template_references(node, out):
    """Collect every string/list entry of a `templates` array.

    Dict entries are skipped: a scene's `templates` holds whole template
    *definitions*, while a template's or entity's `templates` holds *references*
    to them. Only the latter are what `template_ref` describes.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "templates" and isinstance(value, list):
                out.extend(item for item in value if not isinstance(item, dict))
            _template_references(value, out)
    elif isinstance(node, list):
        for value in node:
            _template_references(value, out)
    return out


def test_every_template_reference_validates(registry, resource_documents):
    """Keep #95 fixed.

    `template_ref` is reached from both entity.schema.json and
    template.schema.json, so every template reference in the resources is
    authored against it. The fragments it replaced could not match anything at
    all - `\\(` and `\\)` are literal parens in ECMA-262, not grouping - and the
    tuple form declared only [name, {kwargs}] where the loader
    (pgrpg.functions.str_utils.parse_fnc_list) accepts four shapes.
    """
    validator = Draft202012Validator(
        {"$ref": "definitions.schema.json#/definitions/template_ref"},
        registry=registry,
    )
    failures = [
        f"  {path}\n      {reference!r}\n      {error.message[:120]}"
        for path, document in resource_documents
        for reference in _template_references(document, [])
        for error in validator.iter_errors(reference)
    ]
    references = [
        r for _, d in resource_documents for r in _template_references(d, [])
    ]
    assert len(references) > 1000, "template references were not discovered"
    assert not failures, "template references failing their schema:\n" + "\n".join(failures)


def test_every_class_string_matches_class_def(registry, resource_documents):
    """`class_def` must match the real 'module:ClassName' corpus.

    It is `$ref`d by nothing today, so nothing else would notice it drifting -
    and before #95 it matched none of these 54 strings.
    """
    validator = Draft202012Validator(
        {"$ref": "definitions.schema.json#/definitions/class_def"},
        registry=registry,
    )

    def walk(node, out):
        if isinstance(node, dict):
            if isinstance(node.get("type"), str) and "params" in node:
                out.add(node["type"])
            if isinstance(node.get("class"), str):
                out.add(node["class"])
            for value in node.values():
                walk(value, out)
        elif isinstance(node, list):
            for value in node:
                walk(value, out)
        return out

    strings = set()
    for _, document in resource_documents:
        walk(document, strings)

    assert len(strings) > 40, "class strings were not discovered"
    failures = [
        f"  {string}: {error.message[:120]}"
        for string in sorted(strings)
        for error in validator.iter_errors(string)
    ]
    assert not failures, "class strings failing class_def:\n" + "\n".join(failures)


def test_every_ref_resolves():
    """A `$ref` into a fragment that no longer exists fails open, not loud.

    jsonschema raises on an unresolvable pointer, but only for the documents it
    is actually asked to validate - a stale `$ref` on a rarely exercised branch
    can sit unnoticed. #95 left one behind by design: the fragments once held
    under a non-standard top-level `basics` key now live under `definitions`.
    """
    documents = {
        path.relative_to(SCHEMA_ROOT).as_posix(): json.loads(
            path.read_text(encoding="utf-8")
        )
        for path in sorted(SCHEMA_ROOT.rglob("*.json"))
    }
    unresolved = []

    def resolve(filename, ref):
        target, _, pointer = ref.partition("#")
        if target.startswith(("http://", "https://")):
            return
        if target:
            # Relative to the referring file, normalised so that '../' collapses
            # into the same keys the registry uses.
            key = Path(os.path.normpath(Path(filename).parent / target)).as_posix()
        else:
            key = filename
        document = documents.get(key)
        if document is None:
            unresolved.append(f"{filename}: $ref {ref} - no such schema file")
            return
        node = document
        for part in [p for p in pointer.split("/") if p]:
            part = part.replace("~1", "/").replace("~0", "~")
            if not isinstance(node, dict) or part not in node:
                unresolved.append(f"{filename}: $ref {ref} - pointer is dangling")
                return
            node = node[part]

    def walk(node, filename):
        if isinstance(node, dict):
            if isinstance(node.get("$ref"), str):
                resolve(filename, node["$ref"])
            for value in node.values():
                walk(value, filename)
        elif isinstance(node, list):
            for value in node:
                walk(value, filename)

    for filename, document in documents.items():
        walk(document, filename)

    assert not unresolved, "unresolvable $refs:\n  " + "\n  ".join(unresolved)


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
