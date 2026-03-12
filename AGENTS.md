# DeepScientist Repository Guide

This `AGENTS.md` applies to the entire `DeepScientist/` repository tree.

## Mission

Build `DeepScientist Core` as a small, local-first research operating system that:

- runs fully on the user's machine by default
- installs cleanly through `npm`
- keeps the authoritative runtime in Python
- uses `codex` or `claude` as the execution engine
- keeps durable state in files plus Git
- can finish a full scientific loop
- stays understandable and extensible

The target is a focused core runtime, not a large product platform.

## Current Source Of Truth

- This branch no longer contains the old docs bundle such as `docs/CORE_BLUEPRINT.md`, `docs/CORE_ARCHITECTURE.md`, or `docs/WORKFLOW_AND_SKILLS.md`.
- If older comments, prompts, or README text mention those deleted files, treat them as historical references, not current instructions.
- Start with the files that actually exist in this checkout:
  - `README.md`
  - `docs/en/TUI_USAGE.md`
  - `src/deepscientist/`
  - `src/prompts/`
  - `src/skills/`
  - `src/ui/src/`
  - `src/tui/src/`
  - `tests/`
- When docs and code disagree, prefer the current runtime behavior and tests, then fix the docs in the same change.
- Do not add new doc links to files that do not exist in the repository.

## Non-Negotiable Decisions

1. **One quest = one Git repository**
   - Every quest lives under one absolute `quest_root`.
   - All durable quest content must remain inside that path.
   - Branches and worktrees express divergence inside that quest repo.

2. **Python runtime, npm-friendly launcher**
   - The authoritative core lives in `src/deepscientist/`.
   - `npm` is the normal install and launch path, but it bootstraps the Python runtime instead of replacing it.
   - `bin/ds.js` should remain a thin launcher over the Python daemon and built UI bundles.

3. **Only three built-in MCP namespaces**
   - Built-in Core MCP must stay limited to:
     - `memory`
     - `artifact`
     - `bash_exec`
   - Do not expose a separate public `git`, `status`, or `connector` MCP namespace.
   - Git behavior belongs inside `artifact`.
   - Shell execution, detached command management, progress tracking, and quest-local bash logs belong inside `bash_exec`.

4. **Prompt-led, skill-led workflow**
   - The prompt defines workflow expectations, filesystem contract, Git contract, and response style.
   - Skills provide specialized execution behavior.
   - The daemon persists, restores, routes, and validates lightly.
   - Avoid hard-coding a large stage scheduler when prompt plus skills are enough.

5. **Registry-first extension points**
   - Extension points should use small self-registration registries.
   - This applies at least to:
     - runners
     - channels
     - connector bridges
     - skill discovery
     - optional plugin adapters
   - Prefer `register_*()`, `get_*()`, `list_*()` APIs over branching dispatch logic.

6. **Skills must sync into runner-visible locations**
   - First-party stage skills live under `src/skills/`.
   - Installation must sync them into `~/.codex/skills/` and `~/.claude/agents/`.
   - Each quest should also mirror them into:
     - `<quest_root>/.codex/skills/`
     - `<quest_root>/.claude/agents/`
   - Prompts must reference the actual installed first-party skills.

7. **Required local TUI + local web UI**
   - Both a local TUI and a local web UI are part of the product shape.
   - They must consume the same daemon API and event protocol.
   - The default local web address is `127.0.0.1:20999`.
   - The web app should feel closer to a copilot workspace than an admin console.
   - The first web page should remain a quests home page with DS_2027-style project/workspace cues.

8. **QQ is a first-class connector target**
   - The design should support direct QQ conversation, quest switching, milestone push, and collaboration.
   - QQ is special enough to deserve explicit support, but it should still fit the generic channel and bridge model.

9. **Structured interaction stays minimal**
   - Milestone push, decision requests, approvals, and threaded follow-up should flow through `artifact` plus daemon event delivery.
   - `artifact.interact(...)` is the long-lived structured interaction spine across TUI, web, and connectors.

## Current Implementation Snapshot

The repository already contains real runtime code, not just a blueprint.

- Launcher and install:
  - `bin/ds.js`
  - `install.sh`
  - `package.json`
- Python CLI and daemon:
  - `src/deepscientist/cli.py`
  - `src/deepscientist/daemon/app.py`
  - `src/deepscientist/daemon/api/router.py`
  - `src/deepscientist/daemon/api/handlers.py`
- Quest and durable state:
  - `src/deepscientist/quest/layout.py`
  - `src/deepscientist/quest/service.py`
  - `src/deepscientist/artifact/service.py`
  - `src/deepscientist/memory/service.py`
  - `src/deepscientist/gitops/`
- Prompts and skills:
  - `src/prompts/system.md`
  - `src/deepscientist/prompts/builder.py`
  - `src/skills/`
- Extension registries:
  - `src/deepscientist/runners/registry.py`
  - `src/deepscientist/channels/registry.py`
  - `src/deepscientist/bridges/registry.py`
  - `src/deepscientist/skills/registry.py`
- Interaction surfaces:
  - web app: `src/ui/`
  - Ink TUI: `src/tui/`
  - daemon-side fallback text watcher: `src/deepscientist/tui.py`
- MCP surface:
  - `src/deepscientist/mcp/server.py`

## Approval-First Change Policy

- For non-trivial requests, present one primary implementation plan before editing code.
- That plan should refine underspecified user requirements into a more executable proposal instead of mirroring them mechanically.
- Do not modify repository code until the user clearly approves the proposed plan.
- After approval, execute the change end-to-end, including wiring, verification, and doc updates when architecture or behavior changed.
- If a request is truly trivial and the safe implementation is obvious, you may skip a long proposal, but still state the immediate action before editing.

## Current Runtime Reality

- The built-in MCP surface is implemented around `memory`, `artifact`, and `bash_exec`.
- The daemon already owns:
  - quest lifecycle
  - turn scheduling
  - mailbox delivery
  - session snapshots
  - connector routing
  - shared web/TUI API routes
- `artifact` already owns:
  - artifact persistence
  - Git checkpoints
  - branch and worktree preparation
  - baseline publishing and attaching
  - summary refresh
  - threaded interaction delivery
- `quest` already owns:
  - quest creation
  - quest snapshots
  - runtime state files
  - conversation history
  - pending user-message queue
  - node trace data
- `memory` already supports quest-scoped and global Markdown cards.
- `bash_exec` should own:
  - quest-local managed bash sessions
  - detached execution ids
  - per-call log folders under `.ds/bash_exec/`
  - progress markers and status markers
  - session listing, readback, and stop control
- The web and TUI are expected to share the same API contract; `tests/test_api_contract_surface.py` and `tests/test_tui.py` enforce that.
- `config/runners.yaml` reserves `codex` and `claude`, but the built-in runner registry currently registers only `codex`.
- Do not describe Claude support as implemented unless you also add the runner factory, runtime wiring, and tests.

## Canonical Runtime Layout

Repository code and assets currently live here:

- `README.md`
- `docs/`
- `assets/`
- `bin/`
- `src/deepscientist/`
- `src/prompts/`
- `src/skills/`
- `src/ui/`
- `src/tui/`
- `tests/`

Default runtime data lives under:

- `~/DeepScientist/runtime/`
- `~/DeepScientist/config/`
- `~/DeepScientist/memory/`
- `~/DeepScientist/quests/`
- `~/DeepScientist/plugins/`
- `~/DeepScientist/logs/`
- `~/DeepScientist/cache/`

The current home bootstrap also creates:

- `~/DeepScientist/runtime/venv`
- `~/DeepScientist/runtime/bundle`
- `~/DeepScientist/config/baselines/entries`
- `~/DeepScientist/cache/skills`

Each `~/DeepScientist/quests/<quest_id>/` directory is its own Git repository.

## Quest Layout Contract

The current quest scaffold in `src/deepscientist/quest/layout.py` includes:

- root files:
  - `quest.yaml`
  - `brief.md`
  - `plan.md`
  - `status.md`
  - `SUMMARY.md`
  - `.gitignore`
- artifact directories:
  - `artifacts/approvals`
  - `artifacts/baselines`
  - `artifacts/decisions`
  - `artifacts/graphs`
  - `artifacts/ideas`
  - `artifacts/milestones`
  - `artifacts/progress`
  - `artifacts/reports`
  - `artifacts/runs`
- baseline directories:
  - `baselines/imported`
  - `baselines/local`
- experiment directories:
  - `experiments/main`
  - `experiments/analysis`
- knowledge and handoff directories:
  - `literature`
  - `handoffs`
  - `paper`
- quest memory directories:
  - `memory/decisions`
  - `memory/episodes`
  - `memory/ideas`
  - `memory/knowledge`
  - `memory/papers`
- mirrored skill directories:
  - `.codex/skills`
  - `.claude/agents`
- daemon/runtime directories:
  - `.ds/conversations`
  - `.ds/codex_history`
  - `.ds/bash_exec`
  - `.ds/runs`
  - `.ds/worktrees`

Important runtime files used by the current mailbox and interaction flow:

- `.ds/runtime_state.json`
- `.ds/user_message_queue.json`
- `.ds/interaction_journal.jsonl`
- `.ds/events.jsonl`
- `.ds/bash_exec/index.jsonl`

Do not move these casually. Update services, API handlers, UI, TUI, and tests together if they change.

## Design Rules

- Keep the core minimal, but do not force an artificial LOC ceiling.
- Prefer simple files, subprocess calls, JSONL, Markdown, YAML, and Git over extra services.
- Keep the daemon thin; put domain behavior into prompts and skills where practical.
- Keep all durable quest content inside `quest_root`.
- Make `quest_root` explicit in runner context and built-in MCP context.
- Keep milestone reporting, direct chat, and plan refresh behavior consistent across CLI, UI, and connectors.
- Keep the TUI and web UI protocol-identical even if their presentation differs.
- Support both Chinese and English interaction flows. Current defaults lean Chinese (`zh-CN`), but the product is bilingual.
- Keep baseline reuse first-class through the baseline registry and attachment flow.
- Keep analysis campaigns first-class: one quest can contain many analysis run ids.
- Support Git graph export to JSON, SVG, and PNG under the quest.
- Make registries tiny and readable.
- Make `artifact` return lightweight guidance after stage-significant writes.
- Prefer `bash_exec` over ad hoc shell execution when a command should be durable, reviewable, stoppable, or monitored after the immediate tool call.
- Keep GitHub push support simple: native `git remote` and `git push`, no required GitHub API layer.
- Do not reintroduce deleted top-level `skills/` docs or parallel skill roots. The source of truth is `src/skills/`.

## Mailbox And Interaction Rules

The current runtime behavior in code and `docs/en/TUI_USAGE.md` is:

1. The first plain user message for an idle quest may start a turn directly.
2. Later user messages while a run is active are queued in `.ds/user_message_queue.json`.
3. Those queued messages are delivered when the agent calls `artifact.interact(...)`.
4. Threaded progress and milestone updates should stay non-blocking.
5. True unresolved user decisions should use blocking interaction semantics.
6. Approvals and replies must remain traceable through artifact records and interaction journal state.

If you change this model, update the daemon, quest state handling, TUI/web clients, prompts, and tests together.

## Working Rules By Subsystem

### Quests, state, and Git

- Preserve the one-quest-one-repo contract everywhere.
- Keep Git operations routed through `artifact` and `gitops`, not ad hoc shell calls spread across the codebase.
- If you change quest layout, also change snapshot generation and route consumers.

### MCP

- Keep public built-in MCP limited to `memory`, `artifact`, and `bash_exec`.
- Put Git-backed durable quest state under `artifact` and managed shell execution under `bash_exec` instead of inventing extra public namespaces.
- Keep quest-aware context explicit through `McpContext`.

### Prompts and skills

- First-party stage skills currently expected by tests are:
  - `scout`
  - `baseline`
  - `idea`
  - `experiment`
  - `analysis-campaign`
  - `write`
  - `finalize`
  - `decision`
- When adding or renaming a stage skill:
  - update `STANDARD_SKILLS`
  - update skill discovery and installer behavior
  - update prompt builder output
  - update tests

### Runners

- Use the runner registry for new backends.
- Keep the config shape honest: if a runner is only reserved, mark it as reserved and do not present it as ready.
- Interrupt handling, prompt building, history capture, and artifact integration must all work before calling a runner implemented.

### Connectors and bridges

- Connector config defaults belong in `src/deepscientist/config/models.py`.
- Validation and test helpers belong in `src/deepscientist/config/service.py`.
- User-facing connector delivery belongs in channels.
- Provider/webhook adaptation belongs in bridges.
- QQ remains a first-class target, but new connectors should still fit the channel plus bridge pattern.

### UI and TUI

- The shared contract is more important than any single client implementation detail.
- If you change an API route, update:
  - daemon router and handlers
  - web client usage
  - TUI client usage
  - tests that enforce the contract
- Preserve `/projects` and `/projects/:quest_id` style routing in the web app.
- Keep the workspace copilot-first and mobile-tolerant.
- The web tree is larger than the current DeepScientist-specific surface. For core workflow work, prioritize files already exercised by tests.

## Change Checklists

When changing quest layout or durable state:

- update `src/deepscientist/quest/layout.py`
- update `src/deepscientist/quest/service.py`
- update API handlers or snapshot consumers if fields change
- update `tests/test_init_and_quest.py`
- update `tests/test_daemon_api.py`

When changing artifact or interaction behavior:

- update `src/deepscientist/artifact/schemas.py`
- update `src/deepscientist/artifact/service.py`
- update `src/deepscientist/mcp/server.py` if the tool contract changes
- update UI and TUI event rendering if payloads change
- update `tests/test_memory_and_artifact.py`
- update `tests/test_mcp_servers.py`
- update `tests/test_daemon_api.py`

When changing prompts or stage skills:

- update `src/prompts/system.md` or `src/deepscientist/prompts/builder.py`
- update `src/skills/<skill_id>/SKILL.md`
- keep installer and mirrored-skill behavior in sync
- update `tests/test_stage_skills.py`
- update `tests/test_prompt_builder.py`

When changing connectors or QQ behavior:

- update defaults in `src/deepscientist/config/models.py`
- update validation/help text in `src/deepscientist/config/service.py`
- update `src/deepscientist/channels/`
- update `src/deepscientist/bridges/`
- update daemon routes and handlers if webhook or inbound flow changes
- update connector tests such as:
  - `tests/test_connector_bridges.py`
  - `tests/test_connector_config_validation.py`
  - `tests/test_generic_connectors.py`
  - `tests/test_qq_connector.py`
  - `tests/test_acp_bridge.py`

When changing API surface used by web and TUI:

- update `src/deepscientist/daemon/api/router.py`
- update `src/ui/src/lib/api.ts`
- update `src/tui/src/lib/api.ts`
- update the relevant workspace and TUI components
- update `tests/test_api_contract_surface.py`
- update `tests/test_tui.py`

When changing runner support:

- update config defaults and validation
- register the runner in `src/deepscientist/runners/`
- ensure daemon wiring and interrupt behavior work
- ensure prompt builder and artifact integration work
- add or update tests

## References To Reuse

- Current repo entry points:
  - `README.md`
  - `docs/en/TUI_USAGE.md`
  - `src/deepscientist/cli.py`
  - `src/deepscientist/daemon/app.py`
  - `src/deepscientist/mcp/server.py`
  - `src/deepscientist/prompts/builder.py`
  - `src/deepscientist/quest/layout.py`
  - `src/deepscientist/quest/service.py`
  - `src/deepscientist/artifact/service.py`
- UI and interaction references:
  - `/home/air/DeepScientist_latest/DS_2027/frontend/app/(main)/projects/page.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/app/(main)/projects/[projectId]/page.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/features/projects/ProjectsAppBar.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/features/projects/ProjectsHero.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/features/projects/ProjectCard.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/features/projects/CreateProjectDialog.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/features/projects/WorkspaceCreateCard.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/workspace/WorkspaceLayout.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/workspace/CopilotDockOverlay.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/aceternity/aurora-background.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/app/AppContainer.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/components/MainContent.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/components/Composer.tsx`
- Prompt, role, and runner references:
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/prompt_compiler.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/pi.md`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/reproducer.md`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/analysis-experimenter.md`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/writer.md`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/services/codex_service.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/services/claude_service.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/mcp/codex_config.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/template_manager.py`
- Connector registry and queue references:
  - `/ssdwork/deepscientist/_references/nanoclaw/src/channels/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/channels/registry.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/types.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/group-queue.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/ipc.ts`
- QQ connector background:
  - `https://cloud.tencent.com.cn/developer/article/2635190`

## When Editing This Repo

- Read the files that currently exist first: `README.md`, `docs/en/TUI_USAGE.md`, and the relevant code.
- Do not tell contributors to read deleted `docs/CORE_BLUEPRINT.md`-style files.
- Keep the quest-per-repo model consistent everywhere.
- Keep `memory`, `artifact`, and `bash_exec` as the durable built-in MCP contract.
- If adding behavior, decide whether it belongs in:
  - core runtime
  - skill
  - connector
  - bridge
  - plugin
  - UI
- Update docs whenever architecture changes.
- If the only stable documentation for a change is the code and tests, update `AGENTS.md` or `README.md` instead of inventing dead links.
