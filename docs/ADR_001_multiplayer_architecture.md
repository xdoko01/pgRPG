# ADR 001: Multiplayer Architecture

## Status

Proposed

## Context

pgrpg is currently a single-player game engine. All game state lives in one process,
all managers are module-level singletons with in-process mutable state, and the game
loop is tightly coupled to a local pygame display. A future goal is to support
client-server multiplayer, where one authoritative server runs the simulation and
multiple clients connect to it.

This ADR documents the current architecture blockers, the proposed approach, and
a phased plan for introducing multiplayer without breaking the single-player path.

## Current Architecture Blockers

### 1. Manager singletons are process-local

Every manager (`ecs_manager`, `event_manager`, `command_manager`, etc.) holds mutable
state as module-level globals (`_event_queue`, `_command_queue`, `_world`, etc.). This
state cannot be shared across a network boundary without explicit serialization.

### 2. Events are not serializable

`Event` is a Python dataclass with `generator_obj` and `other_obj` fields that may
contain arbitrary Python objects (pygame Surfaces, class instances). These cannot be
sent over a network as-is.

### 3. Entity IDs are process-local auto-incremented integers

The esper `World` assigns entity IDs as sequential integers starting from 0. In a
multiplayer context, two clients creating entities simultaneously would generate
conflicting IDs. Entity IDs must be globally unique or server-assigned.

### 4. No concept of entity ownership or authority

Any processor can mutate any entity's components. In multiplayer, only the server
should authoritatively modify simulation state; clients should only predict their
own entity's movement and receive corrections.

### 5. Commands execute synchronously on local entities

`command_manager.process_commands()` pops commands and executes them immediately.
In multiplayer, client commands would need to be sent to the server, validated,
executed server-side, and results broadcast back.

### 6. Game loop is tied to pygame display

`main.py:run()` calls `pygame.event.get()`, `pygame.display.flip()`, and passes
display-dependent objects through the frame pipeline. A headless server cannot
import pygame at all.

### 7. Script manager executes game logic client-side

`script_manager.execute_event_actions()` runs arbitrary Python scripts in response
to events. In multiplayer, scripts are server-side logic. Clients should receive
only the outcomes (state changes) as events.

## Proposed Architecture: Authoritative Server

The recommended approach is an **authoritative server** model:

- The **server** runs the full ECS simulation (processors, commands, events, scripts)
  without a display.
- **Clients** handle input, rendering, and client-side prediction only.
- Communication uses a lightweight event-based protocol over TCP/UDP.

### Key seams to introduce

1. **Event serialization**
   - Add `Event.to_dict()` and `Event.from_dict()` methods.
   - Audit all `Event.params` values for JSON-serializability.
   - Remove or replace `generator_obj` / `other_obj` with serializable identifiers.

2. **Entity ownership**
   - Add an `owner: int | None` field to the entity alias registry.
   - Server (owner=0) owns all simulation entities by default.
   - Client-controlled entities (e.g., player) have `owner=client_id`.

3. **Transport abstraction**
   - Introduce a `NetworkTransport` Protocol in `event_manager`:
     ```python
     class NetworkTransport(Protocol):
         def send_event(self, event_dict: dict) -> None: ...
         def receive_events(self) -> list[dict]: ...
     ```
   - Single-player uses a no-op `LocalTransport` (current behavior, zero overhead).
   - Multiplayer plugs in a `TCPTransport` or `UDPTransport`.

4. **Headless server runner**
   - Extract the simulation loop from `main.py` into a `server.py` that:
     - Does not import pygame.
     - Accepts client connections.
     - Runs processors and dispatches events over the network.
   - `main.py` becomes the client entry point.

5. **Client-side prediction and reconciliation**
   - Clients optimistically apply their own movement commands locally.
   - Server sends authoritative `ENTITY_STATE_UPDATE` events.
   - On mismatch, client applies an `ENTITY_STATE_CORRECTION`.

### Separation of concerns

| Concern | Server | Client |
|---|---|---|
| ECS World (entities, components) | Authoritative | Predicted subset |
| Processors | All simulation processors | Render + input only |
| event_manager | Full dispatch | Receives from server |
| command_manager | Processes all commands | Sends commands to server |
| script_manager | Executes scripts | Not used |
| pathfind_manager | Full pathfinding | Not used |
| map_manager | Loads maps | Loads maps (for rendering) |
| gui_manager | Not used | Full rendering |
| sound_manager | Not used | Full audio |

## Recommended Implementation Phases

### Phase A: Event serializability audit

- Add `to_dict()` / `from_dict()` to `Event`.
- Audit all processors that call `event_manager.add_event()` to ensure params are
  JSON-serializable (no pygame objects, no class instances).
- No networking yet — just confirm the data model is ready.

### Phase B: NetworkTransport Protocol

- Define `NetworkTransport` Protocol in `event_manager`.
- Implement `LocalTransport` (no-op, default for single-player).
- Wire `event_manager.process_events()` to optionally broadcast via transport.
- Still fully single-player; no actual network code.

### Phase C: Headless server loop

- Create `pgrpg/core/server.py` with a simulation loop that:
  - Initializes config without pygame.
  - Loads scenes.
  - Runs `ecs_manager.process()` in a fixed-timestep loop.
- Factor out pygame-specific code from `main.py` initialization.

### Phase D: Entity ownership

- Add `owner` field to `ecs_manager._alias_to_entity` (or a parallel dict).
- Server validates that commands target entities owned by the requesting client.
- Introduce `ENTITY_CREATE` / `ENTITY_DELETE` network events.

### Phase E: Client-side prediction and reconciliation

- Client-side prediction for movement commands.
- Server sends periodic `ENTITY_STATE_SNAPSHOT` events.
- Client reconciliation logic corrects prediction drift.

## Consequences

### Pros

- Clean separation of simulation and rendering.
- Single-player path has zero overhead (no-op transport).
- Phased approach — each phase is independently testable and deployable.
- Event-based protocol aligns with existing event_manager architecture.

### Cons

- Event serialization audit may require refactoring some processors.
- Entity ID scheme change may break save/load compatibility.
- Headless server requires careful separation of pygame imports.
- Client-side prediction adds complexity to the client state management.

### Risks

- **Latency**: TCP may be too slow for real-time movement; UDP with reliability
  layer may be needed for action-heavy games.
- **State divergence**: Client prediction can cause visible rubber-banding if
  server correction is too aggressive.
- **Scope creep**: Multiplayer touches nearly every manager; discipline is needed
  to keep phases small and testable.
