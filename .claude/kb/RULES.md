# pgrpg Knowledge Base — AI Maintenance Rules

> Last updated: 2026-07-30 | Verified by: initial authoring of the KB from full source analysis at
> commit `c7b9a5f1`; rules adapted from the Orisales KB maintenance rules

## Purpose

This file defines how AI agents must maintain the knowledge base under `.claude/kb/`.
The knowledge base is **self-improving**: any new verified fact discovered while working in this
repository must be added to the appropriate knowledge file before the session ends.

The KB describes **how the engine works**. It is not a changelog, not a task list, and not a
substitute for reading code — it is the map that tells you *which* code to read.

---

## Rule 1 — Canonical Location

Every fact has exactly one canonical home. Before adding a fact, search the existing files to
determine whether it already exists or belongs on an existing page.

| Fact type | Where it goes |
|-----------|---------------|
| Boot order, game loop, state machine, `reinit` | `core/bootstrap-and-loop.md` |
| Config merge, config sections, prep/init phases | `core/configuration.md` |
| Scene loading order, cleanup, prereqs, two-pass entities | `core/scene-pipeline.md` |
| A manager's responsibility / public functions / `game_functions` key | `core/managers.md` |
| Event queue, handler dispatch, `json_logic`, script modules | `core/events-and-scripts.md` |
| Command queue, blackboards, BTree / BList semantics | `core/commands-and-ai.md` |
| `World` internals, queries, caching, entity lifecycle, esper deltas | `ecs/world.md` |
| How to write a Component; Component lifecycle hooks | `ecs/components.md` |
| How to write a Processor; groups, priority, throttling, `PREREQ` | `ecs/processors.md` |
| Scene-file key reference (what a key means, what type it takes) | `authoring/scene-format.md` |
| Entity / template definition syntax, `vars`, `$` substitution | `authoring/entity-and-template.md` |
| Component `params` syntax, tile-relative vs pixel params | `authoring/component-params.md` |
| `cmd_tree` / `cmd_list` syntax, `^blackboard` references | `authoring/ai-definitions.md` |
| Handler syntax, `json_logic` operators, `%event-param` substitution | `authoring/handlers-and-actions.md` |
| JSON Schema files and editor validation | `authoring/schemas.md` |
| `TILE_RES_PX` and the single-resolution model | `_shared/resolution.md` |
| Entity alias lifecycle and alias→id translation | `_shared/aliases.md` |
| Which directory / module path the engine searches for what | `_shared/filepaths-modulepaths.md` |
| House conventions for *editing* this repo | `_shared/conventions.md` |
| Inventory of components / processors / commands / events / scripts / states | `reference/index.md` |
| A capability's status (WORKING / PARTIAL / BROKEN / UNUSED) | `SCOPE.md` |

If a fact genuinely fits nowhere, apply **Rule 11** before inventing a page.

## Rule 2 — When to Add a Fact

Add a fact when **all** of these are true:

1. It was discovered or confirmed during the current session (source read, test run, game run).
2. It is not already documented.
3. It is reusable — it would save time in a future session.
4. It is verified against the source, a passing test, or observed runtime behaviour.

Do **not** add speculative facts. If a fact is inferred from reading code but not observed at
runtime, mark it:

> ⚠️ Source-inferred — not runtime-verified as of YYYY-MM-DD

## Rule 3 — Provenance

Every page must carry a provenance line in its header (see Rule 7). Use one of:

- `Source-verified <path>[:<lines>] @ <commit>` — you read that code this session.
- `Test-verified <test path>` — a test in `tests/` asserts it and passes.
- `Runtime-verified <how>` — you ran the game or a module `__main__` / doctest and observed it.
- `Source-inferred from <paths>` — read, reasoned, not executed.

Never write `Runtime-verified` for something you did not run. When you *do* verify a
source-inferred fact at runtime, upgrade the label.

Cite code as `path/to/file.py:123` — it is clickable in Claude Code.

## Rule 4 — No Duplication

If a fact is needed in more than one place, write it once and link to it.
Use markdown relative links rather than restating — e.g. from `authoring/component-params.md`,
link to `../_shared/resolution.md#tile-relative-params` instead of repeating the scaling rule.
Never copy-paste a fact to a second location.

## Rule 5 — File Length and Splitting

- If a knowledge file exceeds ~400 lines, evaluate whether to split it.
- Splitting criterion: does it contain two topics that are independently useful?
- `reference/index.md` is an inventory and may exceed 400 lines; split it only when a single
  inventory grows large enough to be looked up on its own.
- If you split, update every link and the domain `index.md`.

## Rule 6 — Index Files Must Stay Current

After adding a page or a major section:

1. Add or update the link in the domain `index.md`.
2. If the fact is cross-domain or commonly looked up, add a row to `README.md` §Quick Lookup.

## Rule 7 — "Last updated" Header

Every knowledge file must begin with:

```
> Last updated: YYYY-MM-DD | Verified by: <provenance, per Rule 3>
```

Update it whenever the file is modified. Use today's date for `Last updated` only. Use exactly
the label `Verified by:` — not `Source:` — so the header can be checked mechanically.

## Rule 8 — Restructure When Needed

If a file's organisation makes facts hard to find, restructure it and say so in the commit
message: `KB: restructured <file> — <reason>`.

## Rule 9 — CLAUDE.md Is Not the Knowledge Base

`CLAUDE.md` at the repo root is the **onboarding entry point**. It should contain only:

- What the project is (one paragraph).
- The repository layout at a glance.
- How to install, run, and test.
- A pointer to `.claude/kb/README.md`.
- The handful of hard rules an agent must not violate.

It must **not** contain engine facts. Move any engine fact found in `CLAUDE.md` into the correct
knowledge file and replace it with a link. `AGENTS.md` is a one-line redirect to `CLAUDE.md` and
must stay that way.

## Rule 10 — Fact Lifecycle

When a source read or a test run contradicts a documented fact:

1. Update the fact to the correct value.
2. Add: `> Corrected YYYY-MM-DD: previously stated <old value>`.
3. Update the provenance line.

Do not silently delete a corrected fact — the correction note tells the next agent that the old
belief was wrong, which is itself useful.

## Rule 11 — Adding a New Domain

First confirm the facts do not belong in an existing domain (Rule 1). Add a domain only for a
genuinely separate area of the engine, not for a sub-topic of an existing one.

To add domain `<new-domain>`:

1. Create `.claude/kb/<new-domain>/index.md`. Decide its shape by size:
   - Large or multi-concern → `index.md` is a **pure hub**: scope + links to sub-pages.
   - Small, single-concern → `index.md` **holds the content directly**; no sub-pages.
2. Start `index.md` and every sub-page with the Rule 7 header.
3. Add a row to `README.md` §Domain Map, and a Quick Lookup row if it introduces a
   commonly-looked-up fact.
4. Extend the Rule 1 routing table above with the new fact types.
5. Put anything shared in `_shared/` and link to it — never copy (Rule 4).
6. Verify every new relative link and anchor resolves before finishing.

## Rule 12 — Keep the KB and the Code in Step

The KB lives inside the repository, so a KB edit travels with the code change that motivated it.

1. When a change alters engine behaviour the KB describes, update the KB **in the same change**.
2. Report the changed KB files alongside the changed source files.
3. **Never run `git commit` or `git push`** — the repository owner commits. State what changed and
   let them commit. (See the project memory note on this.)

A KB that describes last month's engine is worse than no KB, because it is trusted.

## Rule 13 — Status, Not Judgement

Several parts of this engine are half-built, experimental, or provably broken. Record that as a
neutral fact in `SCOPE.md` with the evidence, the same way a working feature is recorded. Do not
"fix" code as a side effect of documenting it, and do not quietly omit a broken path — an agent
that assumes an unused pipeline step works will waste a session on it.
