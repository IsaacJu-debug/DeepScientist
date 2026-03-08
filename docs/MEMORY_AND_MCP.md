# Memory and MCP

This document defines the durable information model and the built-in MCP surface for `DeepScientist Core`.

## 1. Core Rule

The Core owns only two built-in MCP namespaces:

- `memory`
- `artifact`

There is no separate public `git` MCP.
Git operations are internal to `artifact`.

## 1.1 Current implementation paths

The current codebase implements this contract primarily in:

- `src/deepscientist/mcp/context.py`
- `src/deepscientist/mcp/server.py`
- `src/deepscientist/memory/service.py`
- `src/deepscientist/artifact/service.py`
- `src/deepscientist/runners/codex.py`

The Codex runner injects exactly two built-in quest-local MCP servers:

- `memory`
- `artifact`

Both resolve quest context automatically through injected environment variables such as:

- `DS_HOME`
- `DS_QUEST_ID`
- `DS_QUEST_ROOT`
- `DS_RUN_ID`

## 2. Two Durable Scopes

The system needs both **global** and **quest-local** durable information.

## 2.1 Global memory

Global memory lives under:

```text
~/DeepScientist/memory/
```

Use it for cross-quest durable knowledge:

- papers
- methods
- reusable ideas
- lessons learned
- templates

## 2.2 Quest-local state

Quest-local durable state lives under:

```text
<quest_root>/
```

That includes:

- quest-local memory
- quest-local artifacts
- baselines
- experiments
- writing outputs

## 3. Memory Model

Memory is human-readable and file-first.

Memory cards must be stored as:

- Markdown body
- YAML front matter at the top

The runtime should automatically recognize and parse memory cards by reading the front matter from `*.md` files.

Recommended quest-local memory layout:

```text
<quest_root>/memory/
  papers/
  ideas/
  decisions/
  episodes/
  knowledge/
  _index.jsonl
```

Recommended global memory layout:

```text
~/DeepScientist/memory/
  papers/
  ideas/
  decisions/
  episodes/
  knowledge/
  templates/
  _index.jsonl
```

For v1, these memory kinds should stay fixed rather than registry-driven:

- `papers`
- `ideas`
- `decisions`
- `episodes`
- `knowledge`
- `templates` for global scope only

This keeps the core simple and the UI predictable.

Each memory card should be Markdown with front matter:

```yaml
---
id: paper-20260308-001
kind: paper
scope: quest
quest_id: q-20260308-001
created_at: 2026-03-08T18:00:00Z
tags: [transformers, baseline, evaluation]
source:
  type: arxiv
  ref: 2401.12345
confidence: medium
---
```

Then the body contains the actual summary, insights, or note.

## 3.1 Memory auto-recognition contract

`memory` should automatically detect memory cards by:

- scanning `*.md`
- checking for top-of-file YAML front matter
- normalizing recognized metadata into index records

`memory.write()` should accept either:

- structured arguments that are rendered into Markdown + YAML, or
- raw Markdown that already contains front matter

If front matter is incomplete, the tool should fill the required fields before writing.

`memory.search()` should search both:

- front matter fields
- Markdown body text

## 3.2 Memory in the UI

The frontend should be able to read memory cleanly without exposing raw memory folders by default.

Recommended UI behavior:

- show recent memory cards in the quest workspace
- allow filtering by kind, tags, and scope
- open memory cards in the same polished document sheet used for plans and notes
- support both quest-local memory and global memory views

Recommended read APIs:

- `GET /api/quests/<quest_id>/memory`
- `GET /api/memory`

Memory remains file-native underneath.
The UI should simply present it in a cleaner form.

## 4. Artifact Model

Artifacts are the machine-readable quest ledger.

They belong inside the quest:

```text
<quest_root>/artifacts/
```

Recommended layout:

```text
<quest_root>/artifacts/
  baselines/
  ideas/
  decisions/
  progress/
  milestones/
  runs/
  reports/
  approvals/
  graphs/
  _index.jsonl
```

Artifact record kinds:

- `baseline`
- `idea`
- `decision`
- `progress`
- `milestone`
- `run`
- `report`
- `approval`
- `graph`

For v1, artifact kinds should also stay fixed and explicit.
Do not make artifact kinds plugin-driven until there is a real need for multiple implementations.

`analysis` should not be a separate top-level artifact kind.
Analysis results should be represented as:

- `kind: run`
- `run_kind: analysis`
- `analysis_campaign_id: <campaign_id>`

Artifact records should be written automatically in structured form, preferably as one JSON file per record plus `_index.jsonl` for fast scanning.

Recommended path pattern:

```text
<quest_root>/artifacts/<kind>/<record_id>.json
```

## 4.1 Progress-bearing artifact mapping

To make user-facing progress reporting reliable, the artifact layer should distinguish:

- direct artifact kinds:
  - `progress`
  - `milestone`
  - `run`
  - `report`
  - `graph`
- interaction-facing labels:
  - `decision_request`
    - stored as `kind: decision` with request semantics
  - `approval_result`
    - stored as `kind: approval` with result semantics

Artifacts are for structured facts such as:

- which baseline is active
- which idea is currently preferred
- whether a decision approved another experiment
- what a main run produced
- which analysis runs belong to a campaign
- whether writing is evidence-complete

## 5. Why Memory and Artifact Are Separate

They are related but different:

- `memory` is for human-readable knowledge
- `artifact` is for machine-readable quest state
- `git` versions both, but is not the same concept as either one

From the agent's perspective:

- use `memory` for notes, paper summaries, lessons, long-term context
- use `artifact` for decisions, run records, milestone reports, baseline publication, checkpointing, and graph export

Canonical JSON examples for each fixed artifact kind are provided in:

- `docs/ARTIFACT_EXAMPLES.md`

## 6. Quest Context Auto-Resolution

Built-in MCP calls should not require the quest id when invoked from a quest-bound agent.

The daemon must inject session context into the MCP runtime:

```text
DS_HOME
DS_QUEST_ID
DS_QUEST_ROOT
DS_RUN_ID
DS_ACTIVE_ANCHOR
DS_CONVERSATION_ID
DS_AGENT_ROLE
DS_WORKER_ID
DS_WORKTREE_ROOT
DS_TEAM_MODE
```

Then:

- `memory.write()` defaults to quest-local scope
- `artifact.record()` writes under the current `quest_root`
- `artifact.checkpoint()` commits in the current quest repo
- `artifact.prepare_branch()` uses the current quest repo

If no quest context exists, quest-local writes should fail with a clear error.

## 7. Built-In MCP Operations

These are namespace operations, not separate namespaces.

## 7.1 `memory`

Recommended minimal operations:

- `write`
- `read`
- `search`
- `list_recent`
- `promote_to_global`

Typical use:

- summarize a paper into quest memory
- record a lesson learned after a failed run
- promote a reusable idea note into global memory

## 7.2 `artifact`

Recommended minimal operations:

- `record`
- `interact`
- `checkpoint`
- `prepare_branch`
- `publish_baseline`
- `attach_baseline`
- `refresh_summary`
- `render_git_graph`

Structured interaction should also use artifact record kinds such as:

- `progress`
- `milestone`
- `decision`
  - with `interaction_phase: request`
- `approval`
  - with `interaction_phase: result`

## 7.2.1 `artifact` common record envelope

Every structured artifact record should contain at least:

- `kind`
- `schema_version`
- `artifact_id`
- `quest_id`
- `created_at`
- `updated_at`
- `source`
- `status`

Recommended `source.kind` values:

- `agent`
- `user`
- `daemon`

For decision-like records, the following should be required:

- `verdict`
- `action`
- `reason`

`action` should come from the canonical decision action set defined in `docs/WORKFLOW_AND_SKILLS.md`.

Recommended optional fields:

- `next_direction`
- `evidence_paths`
- `metrics_focus`
- `related_run_ids`
- `related_event_ids`

Typical use:

- record an accepted idea
- checkpoint the quest after a milestone
- prepare an idea or run branch
- publish a reusable baseline to the global registry
- attach a published baseline into a new quest
- regenerate `SUMMARY.md`
- render the Git history graph
- emit a structured milestone that the daemon can push to UI and connectors
- emit a structured decision request that can pause and wait for the user
- send a free-form user-facing progress message while also receiving recent inbound messages

## 8. Artifact-Managed Git

Git behavior is internal to `artifact`.

Typical internal flow after a durable `artifact` write:

1. write the artifact record
2. update `artifacts/_index.jsonl`
3. refresh `status.md` or `SUMMARY.md` when appropriate
4. stage the touched files
5. create a Git commit with a standard message
6. optionally push if configured

This is why a separate public `git` MCP is not needed.

## 8.1 Standard artifact guidance return

Every stage-significant `artifact` mutation should return a small guidance payload.

Recommended shape:

```yaml
status: ok
quest_id: q-20260308-001
anchor: experiment
recorded:
  kind: milestone
  id: milestone-021
completed_now:
  - main experiment run-004 recorded
suggested_next:
  action: start_analysis_campaign
  reason: main result beat baseline and now needs robustness checks
inspect:
  summary: <quest_root>/SUMMARY.md
  status: <quest_root>/status.md
  latest_artifact: <quest_root>/artifacts/reports/report-021.json
recent_inbound_messages: []
```

This guidance should stay small.
It is an operational hint, not a dump of all context.

For user-facing experiment reporting, the daemon should derive short cards from this guidance plus the underlying artifact record.

## 8.2 Why this guidance matters

This gives three benefits:

1. the agent gets an explicit next-step hint after writing structured state
2. the daemon has a stable compact object to forward to UI and connectors
3. the system preserves the two-namespace rule without inventing a third `status` MCP

## 8.4 `artifact.interact` behavior

`artifact.interact` should be the structured interaction bridge inside the `artifact` namespace.

It should:

- persist an interaction artifact
- optionally send a user-facing message to bound surfaces
- return any latest serialized inbound user messages that arrived since the last interaction check

Recommended return shape:

```yaml
status: ok
delivered: true
response_phase: ack
recent_inbound_messages:
  - message_id: msg-001
    source: qq
    conversation_id: qq:group:123
    sender: user
    created_at: 2026-03-08T18:10:00Z
    text: 能不能先给我看现在的baseline结果？
```

This preserves the useful behavior of the old `status` tool while keeping the public Core MCP surface minimal.

## 8.5 `artifact.interact` input contract

Recommended input shape:

```yaml
kind: progress
message: Baseline finished; I am preparing the first idea shortlist.
response_phase: ack
importance: info
deliver_to_bound_conversations: true
include_recent_inbound_messages: true
recent_message_limit: 8
attachments:
  - kind: path
    path: <quest_root>/status.md
```

Recommended fields:

- `kind`
  - one of `progress`, `milestone`, `decision_request`, `approval_result`
- `message`
- `response_phase`
  - one of `ack`, `update`, `final`
- `importance`
  - one of `low`, `info`, `answer`, `warning`
- `deliver_to_bound_conversations`
- `include_recent_inbound_messages`
- `recent_message_limit`
- `attachments`

## 8.6 `artifact.interact` output contract

Recommended output shape:

```yaml
status: ok
artifact_id: interact-021
delivered: true
response_phase: ack
delivery_targets:
  - local-ui:default
  - qq:group:123
recent_inbound_messages:
  - message_id: msg-001
    source: qq
    conversation_id: qq:group:123
    sender: user
    created_at: 2026-03-08T18:10:00Z
    text: 能不能先给我看现在的baseline结果？
```

Rules:

- `recent_inbound_messages` may be empty
- messages should be returned in chronological order
- each message should be serialized and self-contained
- the tool should not hide whether nothing new arrived
- interaction labels such as `decision_request` and `approval_result` are transport-facing labels; persisted artifact primary kinds should still remain fixed

## 8.7 Experiment progress reporting contract

The artifact layer should support three reporting levels for experiments:

### level 1: in-flight progress

Use `progress` records to report:

- run id
- current phase
- percent or step progress when available
- latest heartbeat time
- optional short note

### level 2: run completion

Use `run` or `milestone` records to report:

- run id
- status
- primary metrics
- metric deltas vs baseline when available
- paths to machine-readable and human-readable outputs

### level 3: aggregated summary

Use `report` records to summarize:

- what has been completed
- what the main numbers mean
- what the suggested next action is
- which files to inspect for details

If the report contains a decision, it must also include the decision reason.

Recommended `run` result fields, inspired by old DS experiment payloads:

- `run_id`
- `status`
- `method_id`
- `method_name`
- `method_summary`
- `method_branch`
- `baseline_ref`
- `metrics`
- `metrics_trend`
- `metrics_series`
- `delta_vs_baseline`
- `metrics_json_path`
- `metrics_md_path`
- `summary_path`
- `report_md_path`
- `runlog_summary_path`
- `claim_verdict`
- `go_decision`

## 8.8 Every main experiment run must record the new-method result

For main experiments, every completed run should write a structured result for the proposed new method.

This is not optional.

At minimum the run artifact should capture:

- which new method or idea was tested
- which baseline or baseline variant it was compared against
- the measured metrics of the new method
- the metric deltas vs baseline
- the verdict about whether the new method is worth continuing

Recommended example:

```yaml
kind: run
run_id: run-004
status: success
method_id: idea-003-method-a
method_name: Method A with adaptive routing
baseline_ref:
  baseline_id: baseline-001
  variant_id: resnet50-main
metrics:
  accuracy: 0.955
  f1: 0.948
delta_vs_baseline:
  accuracy: +0.012
  f1: +0.009
claim_verdict: support
go_decision: go
metrics_json_path: <quest_root>/experiments/main/run-004/metrics.json
summary_path: <quest_root>/experiments/main/run-004/summary.md
```

Without this record, the daemon should not treat the main experiment as properly complete.

## 8.9 What the user should receive

For a completed run, the daemon should be able to tell the user at least:

- which run finished
- whether it succeeded / failed / was partial
- the primary metric and key deltas
- where to inspect the detailed metrics
- whether the next step is more experiments, analysis, or writing
- why that next step is recommended

For example:

```yaml
message: run-004 completed successfully
primary_metric:
  key: accuracy
  value: 0.943
  delta_vs_baseline: +0.012
next_action: start_analysis_campaign
inspect:
  metrics_json: <quest_root>/experiments/main/run-004/metrics.json
  summary: <quest_root>/experiments/main/run-004/summary.md
  git_graph: <quest_root>/artifacts/graphs/git-graph.svg
```

## 8.3 Structured interaction via `artifact`, not a new public MCP

The old DS `mcp_status_update` and question tools are useful behavioral references, but the Core should stay stricter:

- do not add a new public `status` namespace
- encode structured progress and decisions as `artifact` records
- let `artifact.interact` act as the structured send/pull bridge when needed
- let the daemon route them to bound conversations
- keep direct human-agent conversation in the normal text stream

## 9. Baseline Reuse Model

Baseline reuse should work like this:

The durable baseline registry protocol itself is specified in `docs/REGISTRIES.md`.

### 9.1 Source quest

The source quest stores an accepted baseline at:

```text
<quest_root>/baselines/local/<baseline_id>/
```

Recommended contents:

```text
baseline.yaml
summary.md
metrics.json
environment.md
code_snapshot/
```

### 9.2 Publish

`artifact.publish_baseline()`:

- records the baseline artifact
- writes provenance
- updates:
  - `~/DeepScientist/config/baselines/index.jsonl`

### 9.3 Attach or import

A new quest can:

- attach by metadata only, or
- import a reusable baseline package

Imported location:

```text
<quest_root>/baselines/imported/<baseline_id>/
```

Imported baseline records must preserve:

- source quest id
- source path
- source commit
- metric contract
- environment contract

## 10. Analysis Campaign Records

Analysis is not a single run.

One quest can contain many analysis ids:

```text
<quest_root>/experiments/analysis/
  campaign-001/
    analysis-001/
    analysis-002/
    analysis-003/
```

The artifact layer should be able to record:

- a campaign record
- multiple run records under the campaign
- an aggregated analysis summary report

## 11. Git Graph Export

`artifact.render_git_graph()` should produce:

```text
<quest_root>/artifacts/graphs/git-graph.svg
<quest_root>/artifacts/graphs/git-graph.png
<quest_root>/artifacts/graphs/git-graph.json
```

This gives the UI and connectors a durable report of the quest history.

## 12. Recommended Write Governance

To keep the system recoverable:

- every meaningful milestone should produce a `report` artifact
- every branch or pivot should produce a `decision` artifact
- every accepted run should produce a `run` artifact
- every plan change after user intervention should produce a `report` or `decision`

This keeps the quest understandable even after daemon restarts.

## 13. Concrete Examples

### 13.1 Idea rejected

1. agent writes `memory/ideas/idea-004.md`
2. agent records `artifacts/ideas/idea-004.json`
3. agent records `artifacts/decisions/decision-010.json` with `outcome=rejected`
4. `artifact.checkpoint()` commits the state

### 13.2 Main experiment succeeds

1. agent writes experiment outputs under `experiments/main/run-003/`
2. agent records `artifacts/runs/run-003.json`
3. agent records `artifacts/reports/report-021.json` summarizing the result
4. the daemon pushes a milestone update to the UI and bound connectors

### 13.3 Baseline published for reuse

1. agent finalizes `<quest_root>/baselines/local/baseline-002/`
2. `artifact.publish_baseline()` updates the global baseline index
3. a future quest uses `artifact.attach_baseline()` to import it

## 14. Reference Anchors

- prompt / memory index ideas:
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/prompt_compiler.py`
- structured status / question behavior:
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/mcp/tools.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/tests/test_mcp_status_update.py`
- old DS baseline and experiment payloads:
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/reproducer.md`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/services/quest/schemas.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/tests/test_mcp_lab_baseline_payload.py`
- skill and workspace sync:
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/template_manager.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/tests/test_agent_kernel_workspace.py`
- connector / routing inspirations:
  - `/ssdwork/deepscientist/_references/nanoclaw/src/channels/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/types.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/ipc.ts`
