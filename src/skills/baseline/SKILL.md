---
name: baseline
description: Use when a quest needs to attach, import, reproduce, repair, verify, compare, or publish a baseline and its metrics.
skill_role: stage
---

# Baseline

This skill establishes the reference system the quest will compare against.
The real goal is to secure one trustworthy comparator and then get out of the way so the next scientific step can begin.
The target is one trustworthy baseline line, not an endless reproduction diary.

## Interaction discipline

- Follow the shared interaction contract injected by the system prompt.
- Keep ordinary setup and debugging updates concise.
- Use richer milestone updates only when the baseline becomes trusted, caveated, blocked, waived, or route-changing.

## Tool discipline

- **Do not use native `shell_command` / `command_execution` in this skill.**
- **All shell, CLI, Python, bash, node, git, npm, uv, and environment work must go through `bash_exec(...)`.**
- **For git work inside the current quest repository or worktree, prefer `artifact.git(...)` before raw shell git commands.**
- **If a generic git smoke test is needed outside the quest repo, use `bash_exec(...)` in an isolated scratch repository.**
- Use web search for discovering papers or repos, but use `artifact.arxiv(paper_id=..., full_text=False)` for actually reading a source arXiv paper when it exists.
- Set `full_text=True` only when the short form is insufficient.

## Planning surfaces

- keep quest-root `plan.md` as the quest-level research map for the whole loop
- use workspace `PLAN.md` or compatibility alias `analysis_plan.md` only when the baseline route is non-trivial, blocked, or expensive
- use workspace `CHECKLIST.md` or compatibility alias `REPRO_CHECKLIST.md` as the baseline execution frontier
- once the baseline line is confirmed, waived, or blocked, record the next edge explicitly in quest-root `plan.md`

## Non-negotiable rules

- no fabricated metrics, logs, run status, or success claims
- do not skip baseline steps or silently simplify the route when that would change trust or comparability
- do not claim a baseline is ready before verification is complete
- do not infer missing commands, scripts, or parameters when the uncertainty could change the result
- record any guess that could affect comparison in a brief caveat
- once a baseline is accepted, leave the authoritative comparison contract in `<baseline_root>/json/metric_contract.json`
- for Python baselines, prefer `uv`, but follow a repo-native environment route when it is clearly more trustworthy or required
- if the same failure class appears again without new evidence, code changes, or a route change, stop looping and route through `repair`, `decision`, `blocked`, or one bounded clarification

## Stage purpose

The baseline stage should produce a usable reference point through one of five routes:

1. attach an existing reusable baseline
2. import a reusable baseline package
3. verify an existing local code path or local service as the comparator
4. reproduce a baseline from source
5. repair a broken or stale baseline

Keep the classic control flow:

1. analysis
2. setup
3. execution
4. verification

These are control gates, not paperwork walls.

Default outcomes:

- `comparison_ready`: one comparator is trustworthy enough for downstream comparison, and the core metric contract is durably recorded
- `reproduction_complete`: a fuller paper-grade or reuse-grade baseline package is ready
- `blocked` or `waived`: the current route cannot clear the gate cleanly, and the next move is explicit

Not every baseline needs a paper-grade exact reproduction.
Once one comparator is trustworthy enough and the core contract is durable, prefer leaving baseline and advancing.

## Quick workflow

1. If source reproduction or repair is the chosen route, read the source paper and source repo first; otherwise inspect only the minimum evidence needed to trust the provided or local comparator, or record what is missing and why.
2. Choose the lightest trustworthy route: attach, import, verify-local-existing, reproduce, or repair.
3. Start with the fast path whenever the current baseline object, command path, and acceptance target are already clear enough to validate cheaply.
4. For expensive, unclear, or multi-step routes, create `PLAN.md` and `CHECKLIST.md`; for fast-path verify/reuse/attach work, a concise `CHECKLIST.md` is usually enough, and `PLAN.md` only becomes necessary when the route or fallback is still non-obvious.
5. Keep one dominant phase visible: analysis -> setup -> execution -> verification.
6. Keep one dominant baseline route active at a time.
7. A bounded smoke test is usually helpful only when command path or environment viability is still unclear; otherwise go straight to real verification or the real run.
8. Retry only when smoke, verification, or runtime evidence shows a concrete failure or incompatibility.
9. Close the stage by confirming or waiving the gate, then hand off with a concise `1-2` sentence summary of trust status, core contract coverage, and next anchor.

When the baseline route cost differs dramatically, prefer an explicit short plan before execution.
Typical examples:

- verify local existing service vs full source reproduction
- repair stale local baseline vs full clean rebuild
- accept comparison-ready comparator vs require paper-grade exact reproduction

In those cases, write the bounded plan first and, if the cost gap or acceptance target materially changes the work, a short user confirmation is reasonable.

## Fast-path first

Default to the lightest baseline path that can still establish a trustworthy comparison.
Default to a fast path when it can establish trust with less work.

Fast path is the default when any of the following is true:

- `requested_baseline_ref` or `confirmed_baseline_ref` already points to the active baseline object
- the route is clearly `attach`, `import`, or `verify-local-existing`
- a local code path or local service already exists and the metric path is concrete enough to verify as the comparator
- reproduction requires no meaningful code changes and the main uncertainty is only whether the command still runs

Fast path means:

- do not restart broad baseline discovery by default
- do not front-load a full codebase audit when the entrypoint is already concrete
- use a minimal checklist, plus a short `PLAN.md` only when route cost or uncertainty makes it necessary
- default to reuse-and-verify when runtime already attached a concrete baseline
- if the startup contract says `execution_start_mode=plan_then_execute`, produce a bounded startup-baseline plan first before heavy reproduction or expensive baseline setup

Escalate from fast path to fuller audit only when:

- the paper and repo disagree materially
- the real run or eval entrypoint is unclear
- code changes are likely required
- the core contract still spans multiple metrics, datasets, subtasks, or splits that need interpretation before comparison is honest
- the quest is trying to publish a reusable global baseline rather than only clear the current gate

## Use when

- no credible baseline exists yet
- the current baseline is unverified or stale
- the user already has a baseline package that should be attached or imported
- a reproduction failed earlier and now needs repair
- the quest resumed and the baseline trust state is unclear

## Do not use when

- the quest already has a verified active baseline and the next move is ideation or execution
- the user explicitly waived the baseline gate and that waiver is durably recorded

## Stage gate

For comparison-heavy downstream work, the default expectation is that one of the following is durably true:

- a baseline has been attached and accepted
- a baseline has been imported and accepted
- a verified local-existing comparator has been accepted
- a baseline reproduction has completed and been verified
- an explicit waiver decision exists with a clear reason

Operationally:

- call `artifact.confirm_baseline(...)` once the accepted baseline root and core trusted comparison contract are clear
- call `artifact.waive_baseline(...)` when the quest must continue without a baseline
- attach, import, or publish alone do not open the downstream gate
- a full exact reproduction is not always required: if the acceptance target is only comparison-ready, a verified attached/imported/local-existing comparator can be enough to confirm the baseline
- the comparison-ready minimum still requires `<baseline_root>/json/metric_contract.json`
- once a comparison-ready baseline is durably confirmed, prefer leaving baseline and advancing instead of continuing baseline polish

## Required plan and checklist

Before expensive, unclear, or multi-step baseline work, create a quest-visible `PLAN.md` and `CHECKLIST.md`.
For fast-path verify/reuse/attach work, a concise `CHECKLIST.md` is usually enough, and `PLAN.md` only becomes necessary when the route, proof obligation, or fallback is still non-trivial.

- Use `references/baseline-plan-template.md` as the canonical structure for `PLAN.md`.
- Use `references/baseline-checklist-template.md` as the canonical structure for `CHECKLIST.md`.
- `analysis_plan.md` and `REPRO_CHECKLIST.md` remain acceptable compatibility alias files when an older quest already depends on them.
- Then record the chosen route, source identity, command path, expected outputs, acceptance condition, core metric contract scope, and fallback.
- If the route or acceptance condition changes materially, revise `PLAN.md` before continuing.

Default retry discipline:

- do not rerun the same unchanged smoke command just to reconfirm the same fact
- treat baseline smoke work as a `0-2` budget, not as a mandatory repeated substage
- allow a second smoke only after a real code, command, environment, or evaluator change
- treat one autonomous retry for the same failure class as the normal upper bound
- if the same failure class appears again, switch explicitly into `repair`, record `blocked`, or route through `decision`

## Durable outputs and paths

The baseline stage should usually leave behind:

- a baseline directory under `baselines/local/` or `baselines/imported/`
- `PLAN.md` and `CHECKLIST.md` when the route is non-trivial
- one accepted baseline artifact or blocked report
- a confirmed baseline gate via `artifact.confirm_baseline(...)`, or an explicit waiver via `artifact.waive_baseline(...)`
- `<baseline_root>/json/metric_contract.json` as the canonical accepted comparison contract
- `attachment.yaml` for attached or imported baselines under `baselines/imported/`
- optional registry publication only when the baseline is reusable beyond this quest

For simple attach/import flows or a straightforward reproduce flow, do not stall just to precreate every optional note file.

Useful optional notes:

- `setup.md` when environment or layout choices are non-trivial
- `execution.md` when the run is long, multi-step, or rerun-heavy
- `verification.md` as a filename when a separate verification note is clearer, though verification is required in substance before acceptance

Canonical quest-local paths:

- reproduced baseline root: `<quest_root>/baselines/local/<baseline_id>/`
- attached or imported baseline root: `<quest_root>/baselines/imported/<baseline_id>/`
- canonical baseline metric contract JSON: `<baseline_root>/json/metric_contract.json`
- baseline artifact record: `<quest_root>/artifacts/baselines/<artifact_id>.json`
- baseline reports: `<quest_root>/artifacts/reports/<artifact_id>.json`
- confirmed baseline reference: `quest.yaml -> confirmed_baseline_ref`

## Baseline id and variant rules

- `baseline_id` should be short, stable, and filesystem-safe
- use letters, digits, `.`, `_`, or `-`
- do not use spaces, `/`, `\\`, or `..`
- if one codebase contains multiple comparable baselines, prefer one `baseline_id` with structured variants instead of inventing many near-duplicate entries
- when variants exist, keep `default_variant_id`, `baseline_variants`, and per-variant metric summaries stable enough that later `experiment` and `write` stages can cite them directly

Do not invent parallel durable locations when these runtime contracts already exist.
Do not leave the authoritative metric contract only in chat, memory, or prose once the baseline is accepted.

## Route choice

Choose the route that maximizes trust per unit time and compute; do not follow a fixed ritual.

- attach when a trustworthy reusable baseline already exists
- import when a package or bundle is already available and readable
- verify local existing when a local code path or service is already concrete enough to validate cheaply
- reproduce when reuse would leave too much ambiguity in the comparison contract
- repair when an existing baseline line is close enough that bounded fixes are cheaper than a clean restart

Prefer reuse over redundant reproduction, but prefer reproduction or repair when reuse would still leave the baseline incomparable.
For a clearer attach/import/verify-local-existing/reproduce/repair rubric, read `references/route-selection.md`.

## Workflow

### Phase 1. Analysis

Before running anything substantial, determine:

- exact task
- dataset and split contract
- metric contract scope
- source baseline identity or concrete local comparator
- expected run command or evaluation path

Default analysis discipline:

- if source reproduction or repair is actually active, read the source paper and source repo first
- if the user or runtime already points to a credible comparator candidate, validate that object before broad source reproduction
- identify the real run or evaluation entrypoint
- define the cheapest credible proof step, which may be a smoke test, direct verification, or the real run

Escalate to a fuller audit only when the command path is unclear, the repo is large or confusing, repair mode is active, or custom code changes look likely.
Use `references/codebase-audit-checklist.md` only when the entrypoint or metric path still depends on a fuller repo audit.

### Phase 2. Setup

Prepare the selected route:

- attach: validate the selected baseline id and variant
- import: place the imported baseline metadata under the quest and confirm the package is readable
- reproduce: prepare the baseline work directory, commands, config pointers, and environment notes
- repair: identify the precise broken point before rerunning blindly

For Python baselines, prefer `uv`.

### Python environment rule: prefer `uv`

- if the repo already contains `uv.lock` or a solid `pyproject.toml`, use `uv sync`
- otherwise create a local virtual environment with `uv venv` and install dependencies with `uv pip install ...`
- run setup and real commands through `uv run ...`
- if a repo-native conda, docker, or poetry route is clearly more trustworthy or required, use that route explicitly instead of forcing `uv`

Setup should record:

- baseline id and source identity
- working directory
- command template
- expected outputs
- the chosen environment route

### Phase 3. Execution

Run only the work required to establish the baseline credibly.

Execution rules:

- keep commands auditable and avoid uncontrolled side experiments
- use one bounded smoke test only when command, environment, or evaluator risk is still unresolved
- once the path is trusted enough, launch the real run with `bash_exec(mode='detach', ...)` and inspect managed sessions instead of rerunning blindly
- do not report final success until the command actually finished and the expected result files exist

Retry discipline:

- treat baseline smoke work as a `0-2` budget
- allow a second smoke only after a real change in code, command path, environment, or evaluator wiring
- if the same failure class returns, stop looping

### Phase 4. Verification

Verification is mandatory before baseline acceptance.

Verify:

- the run actually finished
- the reported metrics came from the intended dataset and split
- the metric definitions match the quest contract
- the result is comparable to the paper, source repo, or selected target
- any deviations are explicitly stated

If later `experiment` work would still have to guess the comparison contract, the baseline is not ready.

## Core metric contract

The baseline stage is not complete just because something ran.
It is complete when later stages can compare against it fairly.

Before declaring a baseline usable, make the core comparison contract explicit:

- task identity
- dataset identity and split contract
- evaluation script or evaluation path
- required metric keys for the current downstream comparison
- metric directions
- source commit or source package identity
- known deviations from the source reference

Unless the user explicitly specifies otherwise, treat the original paper's evaluation protocol as the canonical starting point.
If any of these fields are still materially unknown, do not pretend the baseline is a clean downstream reference.
`<baseline_root>/json/metric_contract.json` is the canonical accepted comparison contract.
A core contract is enough to confirm a `comparison_ready` baseline; expand it later when paper claims, registry publication, or variant-heavy comparison need more coverage.

## Feasibility and trust classes

Keep the acceptance verdict simple and explicit:

- usable now
- usable with caveats
- blocked

Do not silently upgrade a degraded or merely operational result into a normal trusted baseline.

## Minimum baseline artifact content

The accepted baseline artifact should include at least:

- `baseline_id`
- `baseline_kind`
- `path`
- `task`
- `dataset`
- `primary_metric`
- `metrics_summary`
- `environment`
- `source`
- `summary`

If variants exist, also include:

- `default_variant_id`
- `baseline_variants`

Metric-contract rules:

- keep `primary_metric` as the headline metric only; do not let it erase the rest of the comparison surface
- when confirming a baseline, submit the canonical `metrics_summary` as a flat top-level dictionary keyed by the paper-facing metric ids
- every canonical baseline metric entry should include `description`, either `derivation` or `origin_path`, and `source_ref`
- mark only the currently required canonical metrics as required; additional metrics can be added later or kept supplementary
- if the accepted baseline contract already needs multiple metrics, datasets, subtasks, splits, or variants, record them in `<baseline_root>/json/metric_contract.json`
- if the paper reports both aggregate and per-dataset or per-task results, preserve both whenever feasible through `metrics_summary` plus structured rows rather than one cherry-picked scalar
- if the source package already has a richer leaderboard table, structured result file, or `json/metric_contract.json`, reuse that richer contract instead of hand-writing a thinner one that keeps only one averaged scalar
- `Result/metric.md` is optional temporary scratch memory only; reconcile against it before calling `artifact.confirm_baseline(...)`, but do not treat it as a required durable file

For the fuller checklist and verdict meanings, read `references/comparability-contract.md`.

## Publication and reuse

- if the quest should reuse an existing baseline, attach it through `artifact.attach_baseline(...)`; if runtime already exposes `requested_baseline_ref` or `confirmed_baseline_ref`, default to reuse-and-verify
- publish through `artifact.publish_baseline(...)` only when reuse beyond the current quest is justified and verification is complete
- for reuse-oriented packaging expectations, read `references/publishable-baseline-package.md`

## Memory and artifact notes

- do not require a fresh memory pass for every fast-path validation
- use `memory.list_recent(...)` or `memory.search(...)` when resuming, reopening an old command path, or avoiding repeated failures
- fast-path exception: if the quest already exposes a clear `requested_baseline_ref` or `confirmed_baseline_ref` and the immediate task is only to validate or reattach that concrete baseline, you may skip broad retrieval
- write memory only when baseline work produces a durable reproduction lesson, verification caveat, environment incident, or route rationale that later stages are likely to reuse
- when calling `memory.write(...)`, pass `tags` as an array like `["stage:baseline", "baseline:<baseline_id>", "type:repro-lesson"]`
- for stable field shapes, read `references/artifact-payload-examples.md`

## Failure and blocked handling

Do not hide failures.

If blocked, record the class explicitly:

- `missing_source_or_code`
- `missing_metric_contract`
- `environment_or_command`
- `run_or_verification_failed`

A blocked result must state:

- what failed
- what was tried
- which paths or logs show the issue
- whether the next best move is attach, import, retry, repair, reset, or ask the user

Bounded autonomous fixes are acceptable only when they do not change confirmed scope, metrics, permissions, or resource assumptions.

## Exit criteria

Exit the baseline stage once one of the following is durably true:

- a baseline is attached and accepted
- an imported baseline is accepted
- a verified local-existing comparator is accepted
- a reproduced baseline is verified and accepted
- a broken route has been declared blocked and a next decision is recorded
- a waiver decision explicitly leaves the baseline gate

Typical next anchors:

- `idea`
- `experiment` in tightly scoped follow-on cases
- `decision` if the baseline line remains contested

A good baseline pass leaves one trusted comparator, one explicit blocker, or one explicit route change, not a vague promise to keep rechecking baseline.
