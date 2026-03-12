# Terminal Implementation Checklist

This checklist tracks the staged rollout of the quest-local interactive Terminal surface.

The Terminal feature should stay:

- `bash_exec`-native
- quest-local
- recoverable after refresh
- connector-compatible
- minimal in UI surface
- visually consistent with the existing Morandi / glass / clean workspace style

## 1. Scope Lock

- [x] Choose the primary architecture: interactive terminal as a `bash_exec` session subtype, not a new MCP namespace.
- [x] Keep the default terminal root at the active quest workspace root, falling back to `quest_root`.
- [x] Keep formal agent experiment execution on structured `bash_exec`, not on the live terminal shell.
- [ ] Document the split between:
  - `exec` sessions for agent-managed runs
  - `terminal` sessions for human-interactive shell continuity

## 2. Backend Session Model

- [ ] Extend `bash_exec` session metadata with `kind: exec | terminal`.
- [ ] Add durable terminal session files under `.ds/bash_exec/<session_id>/`:
  - `meta.json`
  - `log.jsonl`
  - `terminal.log`
  - `input.jsonl`
  - `input.cursor.json`
  - `history.jsonl`
  - `progress.json`
- [ ] Add a stable default session id for each quest, for example `terminal-main`.
- [ ] Ensure terminal sessions survive page refresh and daemon reconnect.
- [ ] Track current cwd in terminal metadata.
- [ ] Track latest command summary for quick restore payloads.

## 3. Monitor / PTY Runtime

- [ ] Extend `src/deepscientist/bash_exec/monitor.py` to support interactive PTY input replay.
- [ ] Poll `input.jsonl` and forward newly appended input into the live PTY.
- [ ] Record every accepted user input in `history.jsonl`.
- [ ] Inject and parse a shell prompt marker that updates cwd safely.
- [ ] Keep stop / terminate semantics compatible with existing `bash_exec`.
- [ ] Preserve raw output in `terminal.log` and structured line output in `log.jsonl`.

## 4. Backend API

- [ ] Add `POST /api/quests/<quest_id>/terminal/session/ensure`
- [ ] Add `POST /api/quests/<quest_id>/terminal/sessions/<session_id>/input`
- [ ] Add `GET /api/quests/<quest_id>/terminal/sessions/<session_id>/restore`
- [ ] Add `GET /api/quests/<quest_id>/terminal/sessions/<session_id>/stream`
- [ ] Add `GET /api/quests/<quest_id>/terminal/history`
- [ ] Keep existing `/api/quests/<quest_id>/bash/sessions/*` endpoints working for replay and historic session inspection.

## 5. Command And Connector Routing

- [ ] Add `/terminal` to ACP slash command descriptors.
- [ ] Support `/terminal` with no args:
  - ensure the default session
  - return current session id, cwd, and status
- [ ] Support `/terminal <command>`:
  - ensure the default session
  - submit the command as terminal input
  - return immediate ack
- [ ] Support `/terminal -R`:
  - return current cwd
  - return latest 10 commands
  - return current status
  - return recent output tail
- [ ] Route connector `/terminal` output as targeted ack / restore, not as broad milestone broadcast.
- [ ] Keep regular research progress delivery on `artifact.interact(...)`.

## 6. Web UI

- [ ] Add a dedicated `Terminal` workspace view next to existing `Studio` / `Chat`.
- [ ] Reuse the existing xterm-based terminal shell from `src/ui/src/lib/plugins/cli`.
- [ ] Keep the page style minimal and clear:
  - low-noise glass cards
  - thin borders
  - soft Morandi palette
  - strong readability
- [ ] Show a left rail with:
  - the default live quest terminal
  - recent `bash_exec` sessions
- [ ] Show a right main pane with:
  - terminal header
  - cwd
  - status
  - restore / clear / search actions
  - live xterm shell
- [ ] Reuse `AgentCommentBlock` above historic `bash_exec` sessions.
- [ ] Show command, cwd, and latest output summary in the left rail.
- [ ] Support reload recovery on every Web reopen.

## 7. TUI / Shared Protocol

- [ ] Reuse the same backend routes and payload shape from Web.
- [ ] Ensure TUI can issue `/terminal`, `/terminal -R`, and `/terminal <command>`.
- [ ] Keep ACP as the source of lightweight terminal lifecycle events.
- [ ] Keep raw terminal output on terminal-specific stream endpoints instead of dumping it into the main copilot feed.

## 8. Docs

- [ ] Update `docs/en/TUI_USAGE.md` with `/terminal` usage.
- [ ] Update `docs/en/RUNTIME_FLOW_AND_CANVAS.md` with terminal session semantics.
- [ ] Add a terminal protocol doc with:
  - session model
  - API
  - connector behavior
  - restore behavior
  - Web UI mapping

## 9. Tests

- [ ] Backend: ensure terminal session creation.
- [ ] Backend: ensure terminal input changes cwd persistently.
- [ ] Backend: ensure `/terminal -R` returns cwd + latest commands.
- [ ] Backend: ensure stop / reconnect still work.
- [ ] Backend: ensure connector command routing supports `/terminal`.
- [ ] Web: ensure the Terminal view renders and restores state.
- [ ] Web: ensure historic `bash_exec` sessions show `comment`.
- [ ] Web: ensure live terminal accepts input and reload restores output.

## 10. Finish Criteria

- [ ] Web refresh keeps the quest terminal visible and restorable.
- [ ] `/terminal pwd` works from command surfaces.
- [ ] `/terminal -R` works from connector surfaces.
- [ ] Historic `bash_exec` replay and live terminal shell coexist in one clear UI.
- [ ] Docs and tests pass together.
