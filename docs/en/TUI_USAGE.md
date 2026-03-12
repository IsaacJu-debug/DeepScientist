# TUI Usage

This document is the single repo-level reference for the current DeepScientist TUI workflow.

For the current runtime control flow, prompt/skill execution model, MCP surface, and Canvas reconstruction logic, also see `docs/en/RUNTIME_FLOW_AND_CANVAS.md`.

## Install And Start

Use the current workspace install:

```bash
pip install -e .
npm install
```

Common launcher commands:

```bash
node bin/ds.js
node bin/ds.js --tui
node bin/ds.js --web
node bin/ds.js --status
node bin/ds.js --stop
```

Notes:

- `node bin/ds.js` starts the managed daemon and opens the local UI surfaces.
- `node bin/ds.js --tui` starts daemon plus TUI only.
- `node bin/ds.js --stop` stops the managed daemon itself, not just one quest.
- `python -m deepscientist.cli ...` remains available for low-level commands, but the launcher is the normal path.

## Core TUI Flow

Inside the TUI:

- `/home`: leave the current quest and return to request mode.
- `/projects`: open the quest browser.
- `/use <quest_id>`: bind the current TUI session to one quest.
- `/new`: create a quest from inside the TUI.
- `/delete <quest_id> --yes`: delete a quest (destructive; requires confirmation).
- plain text: send a normal user message to the bound quest.
- `/status`: inspect the current quest state.
- `/graph`: inspect the current quest graph.
- `/config`: open the local config browser.
- `/pause`: pause the current quest; if no quest is bound, choose one in the panel.
- `/resume`: resume the current quest; if no quest is bound, choose one in the panel.
- `/stop`: stop the current quest; if no quest is bound, choose one in the panel.
- `/stop <quest_id>`: stop a specific quest explicitly.

If you are already inside a quest, `/pause`, `/resume`, and `/stop` target that quest automatically.

## Message Delivery Model

The TUI, web UI, and connectors now share the same mailbox semantics.

1. The first plain user message for an idle quest starts a turn directly.
2. That first launch message is claimed by the run and does not get re-delivered later through the mailbox.
3. Later user messages that arrive while the agent is already running are written into `.ds/user_message_queue.json`.
4. Those queued messages are delivered only when the agent calls `artifact.interact(...)`.
5. When delivery happens, the agent receives the queued bundle as the latest user requirements and the queue entries move from `pending` to completed audit records.
6. If there is no new user message, the runtime returns recent interaction records plus the instruction that the user did not send anything new.

Durable files used by this flow:

- `.ds/runtime_state.json`
- `.ds/user_message_queue.json`
- `.ds/interaction_journal.jsonl`
- `.ds/events.jsonl`

## Stop, Pause, Resume

Quest-level control:

- `/pause` interrupts the active runner and marks the quest as `paused`.
- `/resume` moves a `paused` or `stopped` quest back to `active`.
- `/stop` interrupts the active runner, clears `active_run_id`, and marks the quest as `stopped`.
- `/pause`, `/resume`, and `/stop` also append a visible assistant-side control notice into the quest chat history and push the same notice to bound connectors using the normal connector routing policy.

`/stop` semantics are intentionally stronger than `/pause`:

- queued but not yet delivered user mailbox messages are cancelled
- those cancelled messages are preserved in the queue audit trail with terminal status fields such as `cancelled_by_stop`
- the currently executing launch message is recorded as `accepted_by_run`
- the next user message after stop starts a fresh turn in the same quest context without silently replaying stale queued text
- stop does not rewrite Git state: the current branch, worktree, and already written files remain in place, so follow-up work resumes from the same repository context

Daemon-level stop:

- `node bin/ds.js --stop` shuts down the managed daemon
- it validates both `home` and `daemon_id` before touching the daemon
- it first asks the daemon to stop cleanly
- if needed it escalates to `SIGTERM`, then `SIGKILL`
- if shutdown succeeds, the launcher clears the daemon state file and prints `DeepScientist daemon stopped.`
- a clean daemon shutdown stops any actively running quests first, emits the same stop notice, and leaves Git/worktree state untouched for the next daemon start

## Artifact Interaction Expectations

The agent should use `artifact.interact(...)` as the long-lived conversation thread:

- `progress` and `milestone` updates are threaded, non-blocking status messages
- `decision_request` is the blocking form
- a blocking decision request should provide 1 to 3 concrete options, explain pros and cons, wait up to 1 day when feasible, then self-resolve and notify the user if the timeout expires

## Troubleshooting

If the TUI looks idle after you send text:

- confirm the quest is actually bound
- check the quest status with `/status`
- inspect `.ds/runtime_state.json` for `status`, `active_run_id`, and `pending_user_message_count`
- inspect `.ds/events.jsonl` for `runner.turn_error`, `quest.control`, or `artifact.recorded`

If a follow-up user message does not seem to reach the agent:

- check whether the quest is currently running
- inspect `.ds/user_message_queue.json`
- confirm the agent is calling `artifact.interact(...)` during long work

If stop appears ineffective:

- use `/stop` inside the quest first
- verify the quest becomes `stopped`
- for a full daemon shutdown use `node bin/ds.js --stop`
