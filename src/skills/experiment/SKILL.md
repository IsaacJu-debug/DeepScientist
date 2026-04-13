---
name: experiment
description: Use when a quest is ready for a concrete implementation pass or a main experiment run tied to a selected idea and an accepted baseline.
skill_role: stage
---

# Experiment

Use this skill for the main evidence-producing runs of the quest.
The goal is to turn one selected route into one trustworthy measured result with the smallest valid amount of execution.

## Interaction discipline

- Follow the shared interaction contract injected by the system prompt.
- For ordinary active work, prefer a concise progress update once work has crossed roughly 6 tool calls with a human-meaningful delta, and do not drift beyond roughly 12 tool calls or about 8 minutes without a user-visible update.
- Keep ordinary subtask completions concise. When a main experiment actually finishes or reaches a stage-significant checkpoint, upgrade to a richer `artifact.interact(kind='milestone', reply_mode='threaded', ...)` report rather than another short progress line.
- That richer experiment-stage milestone report should normally cover: what run finished, the headline result versus baseline or expectation, the main caveat, and the exact recommended next action.
- That richer milestone report is still normally non-blocking. If the next route is already justified locally, continue automatically after reporting rather than idling for acknowledgment.
- If the active communication surface is QQ and QQ milestone media is enabled in config, a completed main experiment may attach one summary PNG to that richer milestone update, but do not auto-send every training curve, per-step plot, or intermediate image.
- That PNG should be a connector-facing report chart, not a raw debug plot and not a draft paper figure.
- Preferred connector-chart palettes are Morandi-like and restrained:
  - `sage-clay`: `#E7E1D6`, `#B7A99A`, `#7F8F84`
  - `mist-stone`: `#F3EEE8`, `#D8D1C7`, `#8A9199`
  - `dust-rose`: `#F2E9E6`, `#D8C3BC`, `#B88C8C`
- Connector-facing chart requirements:
  - white or near-white background
  - low saturation, simple legend, readable labels, and no dashboard clutter
  - summarize only the evidence needed for the milestone
- If the figure matters beyond transient debugging, open `figure-polish/SKILL.md` and follow its render-inspect-revise workflow before treating the image as final.
- If plotting in Python, reuse the fixed Morandi plotting starter from the system prompt rather than inventing a new bright style for each run.
- If the runtime starts an auto-continue turn with no new user message, continue from the current run state, logs, artifacts, and active requirements instead of replaying the previous user turn.

## Planning surfaces

- keep quest-root `plan.md` as the quest-level research map and loop tracker
- use workspace `PLAN.md` as the active experiment-node contract when the run is non-trivial, code-touching, or meant to become a durable main result
- use workspace `CHECKLIST.md` as the active execution frontier with one real in-progress item and a short `Next` list
- if the checklist stops changing across repeated passes, revise the node contract or route instead of nesting more execution subtasks
- after each measured result, update quest-root `plan.md` with the actual next edge: analysis, write, decision, or a new loop entry
- Progress message templates are references only. Adapt to the actual context and vary wording so messages feel human, respectful, and non-robotic.
- If a threaded user reply arrives, interpret it relative to the latest experiment progress update before assuming the task changed completely.
- Hard execution rule: every terminal command in this stage must go through `bash_exec`; do not use any other terminal path for smoke tests, real runs, Git, Python, package-manager, or file-inspection commands.
- Prefer `bash_exec` for experiment commands so each run gets a durable session id, quest-local log folder, and later `read/list/kill` control.
- For meaningful long-running runs, include the estimated next reply time or next check-in window whenever it is defensible.

## Tool discipline

- **Do not use native `shell_command` / `command_execution` in this skill.**
- **All smoke tests, real runs, shell, CLI, Python, bash, node, git, npm, uv, and environment work must go through `bash_exec(...)`.**
- **For git work inside the current quest repository or worktree, prefer `artifact.git(...)` before raw shell git commands.**
- **If a scratch repository or isolated test environment is needed, create and drive it through `bash_exec(...)`, not native shell tools.**

## Stage purpose

The experiment stage should turn a selected idea into auditable evidence.
It should preserve the strongest old experiment-planning and execution discipline:

- define the run contract before execution
- keep the run comparable to baseline
- capture configs, commands, logs, and metrics
- report both success and failure honestly
- route the next action through an explicit decision

The experiment stage is not just "run code".
It is the stage that converts an idea contract into evidence that other stages can trust.
It is also the stage that should decide the next route once the measured result exists.
Within the user's explicit constraints, maximize valid evidence per unit time and compute.
Prefer equivalence-preserving efficiency upgrades first: larger safe batch size, mixed precision, gradient accumulation, dataloader workers, cache reuse, checkpoint resume, precomputed features, and smaller pilots.
If a proposed efficiency change alters optimization dynamics, effective budget, or baseline comparability, treat it as a real experiment change and record it as such.

Use `references/evidence-ladder.md` when deciding whether the current package is merely executable, solid enough to carry the main claim, or already in the stage where broader polish is justified.

Completing one main run is not quest completion.
After reporting the run, keep moving to iterate, analyze, write, or finalize unless a genuine blocking decision remains.

When the quest is algorithm-first, treat `experiment` as the execution surface of `optimize`, not as the terminal goal of the workflow.
After a measured result, the default next move is frontier review and optimize-side route selection rather than paper packaging.

## Quick workflow

Treat this as the short run-order summary. The detailed run contract, execution rules, and recording rules remain in `Workflow`.

1. Restate the selected idea in `1-2` sentences and confirm the baseline comparison contract.
2. Split the work mentally into either a lightweight run or a durable main run.
3. Before substantial code edits or a durable main run, create `PLAN.md` and `CHECKLIST.md`; for smaller validated follow-up runs, update the existing control surface instead of rebuilding a heavy plan package.
4. Materialize or confirm a dedicated child `run/*` branch/worktree only when this run is meant to become a durable main-experiment node.
5. Use `PLAN.md` to lock the concrete run path only when the route is still non-trivial, and use `CHECKLIST.md` as the living control surface while planning, implementing, testing, running, and validating.
6. Use a bounded smoke test or pilot only when the command path, output schema, or environment viability is still unverified; otherwise launch the real run directly with durable logging and monitor it through `bash_exec`.
7. Treat experiment smoke/pilot work as a `0-2` budget: `0` when direct real execution is already the cheapest discriminative check, `1` for one unresolved execution risk, and `2` only after a real code, command, environment, or evaluator change.
8. Once the route is concrete, prefer one clean implementation pass and one real run; retries should happen only after a concrete failure, invalidity, or genuinely new evidence justifies another attempt.
9. Revise the plan if implementation, comparability, runtime, or route assumptions change materially, and close each real main-run milestone with a concise `1-2` sentence summary that says what was tested, whether performance improved / worsened / stayed mixed, and the exact next action.

## Non-negotiable rules

- Do not fabricate metrics, logs, claims, or improvement narratives.
- Do not introduce a new dataset or silently change splits or evaluation protocol.
- Do not change metric definitions or evaluation logic unless the change is explicitly justified and durably recorded.
- Do not stop after a quick sanity run if the agreed goal is a real experiment.
- Do not claim success before durable artifacts exist and the acceptance gate passes.
- Implement the claimed mechanism, not a convenient shortcut that changes the theory.
- Keep the baseline reference read-only.
- Avoid asking the user to fix the environment unless there is no credible agent-side path left.
- Do not record a durable main experiment from an idea branch, quest root branch, or paper branch as if that were the final result node; every durable main experiment should land on its own `run/*` branch.
- After each `artifact.record_main_experiment(...)`, route from the measured result:
  - if paper mode is enabled, decide whether to strengthen evidence, analyze, or write
  - if paper mode is disabled, prefer iterate / revise-idea / branch over default writing
- In algorithm-first work, after each main run, return to `optimize` or `decision` for frontier review before launching another large run.

## Experiment mental guardrails

- Baseline reproduction is not wasted time; untrusted comparison is wasted time.
- Failed runs are still data when the delta and diagnosis are recorded clearly.
- Suspiciously good results deserve the same skepticism as obvious failures.
- Change less, learn more.
- If a retry does not add new evidence, it is budget burn rather than progress.

## Use when

- a baseline is accepted
- an idea has been selected
- the evaluation contract is explicit
- the quest is ready for implementation and measurement

## Do not use when

- the baseline gate is unresolved
- the idea stage still has unresolved tradeoffs
- the main need is writing or follow-up analysis rather than a main run

## Preconditions and gate

Before a main run starts, confirm:

- selected idea or hypothesis
- baseline reference
- dataset and split
- primary metric
- stop condition
- resource budget
- dedicated `run/*` target branch or isolated worktree for this exact main experiment
- exact output location
- required metric keys for acceptance
- minimal experiment and abandonment condition from the idea stage

If any of these are materially unknown, stop and resolve them through `decision`.

Two execution tiers are acceptable:

- `lightweight run`
  - minimal code touch
  - already-trusted command path
  - no major branch or environment change
  - one compact control-surface update plus durable result recording is usually enough
- `durable main run`
  - substantial code changes, new evaluator wiring, long runtime, or paper-facing claim-carrying evidence
  - use the fuller `PLAN.md` / `CHECKLIST.md` contract and dedicated `run/*` surface

## Required plan and checklist

Before substantial implementation work or a durable main run, create a quest-visible `PLAN.md` and `CHECKLIST.md`.

- Use `references/main-experiment-plan-template.md` as the canonical structure for `PLAN.md`.
- Use `references/main-experiment-checklist-template.md` as the canonical structure for `CHECKLIST.md`.
- keep quest-root `plan.md` synced with the current experiment map node, incumbent context, and next-loop transitions
- `PLAN.md` should lead with the selected idea summarized in `1-2` sentences, put the user's explicit requirements and non-negotiable constraints first, and then make the run contract concrete: baseline and comparability rules, safe efficiency levers, code touchpoints, minimal code-change map, smoke / pilot path, full-run path, fallback options, expected outputs, and a revision log.
- `CHECKLIST.md` is the living execution list; update it during planning, implementation, testing, main execution, validation, and every material route change.
- If the code path, comparability contract, runtime strategy, or execution route changes materially, revise `PLAN.md` before spending more code or compute.
- For a lightweight run, a compact control-surface update is enough if the route, outputs, and next decision remain obvious.
- The later `RUN.md`, `summary.md`, and artifact payloads remain required outputs for durable main runs, but `PLAN.md` and `CHECKLIST.md` are the canonical planning-and-control surface before and during execution.
- Once `PLAN.md` makes the implementation route concrete, do not keep reshaping code and commands speculatively. The normal default is one real run, with a bounded smoke or pilot only when the path is still unverified, and retries only after a documented failure, invalidity, or new evidence that changes the expected outcome.

## Working-boundary rules

Only modify the active quest workspace for this experiment line.

- treat the accepted baseline workspace as read-only
- do not derive branch or worktree assumptions from guesswork
- keep all durable outputs inside the quest
- if the runtime gives an explicit worktree path, use it exactly

## Resource and environment rules

- Follow the explicit resource assignment if one exists.
- If GPU assignment is explicit, respect it exactly and record it in the run manifest.
- Do not silently consume extra GPUs or broaden resource scope.
- Capture enough environment information that the run can later be reconstructed.
- If a new dependency appears necessary, record it as a risk and prefer a fallback if possible.

## Truth sources

Use:

- idea-stage outputs
- baseline artifacts
- current codebase and configs
- recent decisions
- task and metric contract
- shell logs and generated outputs from the actual run
- `bash_exec` session ids, progress markers, and exported logs from the actual run
- the selected idea handoff contract
- incident or failure-pattern memory from earlier runs

Do not claim run success without durable outputs.

## Required durable outputs

A meaningful experiment pass should leave behind:

- a run directory under `artifacts/experiment/<run_id>/` or the quest-equivalent canonical location
- `artifact_manifest.json`, `run_manifest.json`, `metrics.json`, and `summary.md`
- `metrics.md` and `runlog.summary.md` for durable main runs
- durable command, config, and log pointers
- exported shell log, typically `bash.log`
- a run artifact with explicit deltas versus baseline
- a decision about what should happen next

Recommended additional files:

- `claim_validation.md`
- environment snapshot files such as Python version, package freeze, and GPU info when applicable
- a live execution note or rolling run log when the experiment spans multiple implementation or execution steps

`run_manifest.json` should capture at least:

- `run_id`
- quest / branch context
- baseline reference or commit
- full commands
- config paths and key resolved hyperparameters
- dataset identifier or version
- seeds
- environment snapshot paths
- start time, end time, and final status

If a command needed for environment capture is unavailable, record that gap in the manifest and summary.

## Workflow

### 1. Define the run contract

Before implementation or execution, state:

- `run_id`
- experiment tier: `auxiliary/dev` or `main/test`
- research question
- null hypothesis
- alternative hypothesis
- hypothesis
- baseline id or variant
- metric targets
- expected changed files
- expected outputs
- stop condition
- compute or runtime budget
- minimal experiment
- abandonment condition
- strongest alternative hypothesis
- exact metric keys that will decide success or failure

Prefer to write this contract first in `PLAN.md` using `references/main-experiment-plan-template.md`, then keep the current execution state visible in `CHECKLIST.md` using `references/main-experiment-checklist-template.md`.

For substantial runs, also record the following seven experiment fields early and keep them updated during execution:

1. research question
2. research type
3. research objective
4. experimental setup
5. experimental results
6. experimental analysis
7. experimental conclusions

If the run contract changes materially later, record the change durably.

Treat the run contract as a research question contract, not only an execution checklist.
Before coding, be able to explain:

- why this run is the best current route rather than the main alternatives
- what observation would count as a real answer to the research question
- what result would force a downgrade, retry, or route change
- what confounder would make the run non-comparable even if it finishes successfully

If multiple candidate experiment packages exist, prefer the one with the best balance of technical feasibility, research importance, and methodological rigor.
Do not choose a package only because it sounds ambitious.

For paper-facing lines, default to this evidence ladder:

- `auxiliary/dev`
  - clarify parameters, settings, mechanisms, or diagnostics
- `main/test`
  - carry the core comparison the paper will rely on
- `minimum -> solid -> maximum`
  - first make the result executable and comparable
  - then make it strong enough to carry the claim
  - only then spend effort on broader supporting polish

### 2. Run a preflight check

Before editing or executing:

- confirm the dataset path, version, and split contract
- confirm the baseline metrics reference
- if durable state exposes `active_baseline_metric_contract_json`, read that JSON file before planning commands or comparisons
- treat `active_baseline_metric_contract_json` as the default authoritative baseline comparison contract unless you record a concrete reason to override it
- confirm the selected idea claim and code-level plan
- look up prior incidents or repeated failure patterns when available
- confirm output directories and naming
- confirm that the intended run still matches the current quest decision

If a repeated failure pattern already exists, apply the mitigation first and record that choice.

Also confirm before comparison work:

- the baseline verification is trustworthy enough
- the planned comparison still uses the same metric contract
- the metric keys and primary metric still match `active_baseline_metric_contract_json` when that file is available
- every main experiment submission still covers all required baseline metric ids from `active_baseline_metric_contract_json`; extra metrics are allowed, but missing required metrics are not
- the required baseline metrics still use the same evaluation code and metric definitions; if an extra evaluator is genuinely necessary, record it as supplementary output rather than replacing the canonical comparator
- if the run is `main/test` and superiority is likely to be claimed, define the significance-testing plan before execution rather than after seeing the numbers
- if `Result/metric.md` was used during the run, treat it as optional scratch memory only and reconcile it against the final submitted metrics before `artifact.record_main_experiment(...)`

Before you begin a substantial run, send a concise threaded `artifact.interact(kind='progress', ...)` update naming:

- the run contract you are about to execute
- the main evidence it is testing
- the expected durable outputs
- the next checkpoint for reporting back

### 2.1 Diagnostic mode trigger

Switch from ordinary execution mode into diagnosis mode when any of the following becomes true:

- two retries in a row add no new evidence or no interpretable delta
- the baseline gap is much larger than expected and the cause is unclear
- the metrics are suspiciously strong, suspiciously identical to baseline, or highly unstable
- logs, checkpoints, or intermediate outputs conflict with the claimed behavior

In diagnosis mode:

- stop brute-force retrying
- prefer the smallest discriminative test that can separate competing hypotheses
- resolve obvious environment or data-contract issues before launching another comparison run
- make the diagnosis goal explicit: explain the behavior, not just "try something else"

### 3. Confirm the execution workspace

The normal experiment workspace is the current active idea worktree returned by `artifact.submit_idea(...)`.

- do not create a fresh manual branch for the main experiment unless recovery or debugging truly requires it
- implement and run inside the current active idea workspace
- if the idea package changes materially before execution, submit a new durable idea branch with `artifact.submit_idea(mode='create', lineage_intent='continue_line'|'branch_alternative', ...)` instead of silently mutating the old node
- after a real main run finishes, record it with `artifact.record_main_experiment(...)` before moving to analysis or writing
- once that durable main result exists, treat the branch as a fixed round node; a later new optimization round should usually compare foundations and create a new `continue_line` child branch or `branch_alternative` sibling-like branch
- after `artifact.record_main_experiment(...)`, if QQ milestone media is enabled and the metrics are stable enough to summarize honestly, prefer one concise summary PNG over multiple attachments

### 4. Implement the minimum required change

Implementation rules:

- keep the change hypothesis-bound
- prefer small, explainable edits
- avoid unrelated cleanup during a main run
- record which files matter for later review
- preserve theory fidelity between the idea claim and the code change
- add robustness checks when the mechanism risks NaN, inf, or unstable behavior
- implement according to the current `PLAN.md` instead of repeatedly improvising a new method after each small observation
- avoid repeated code churn between the smoke test and the real run unless the smoke test exposes a specific problem that the next change is meant to fix

Prefer to complete one experiment cleanly before expanding to the next, unless parallel execution is explicitly justified and isolated.
For substantial experiment packages, the default is one experiment at a time, with each one reaching a recoverable recorded state before the next begins.

Retry-delta discipline:

- unless the current state is completely non-executable, change only one major variable per retry
- if broader recovery is unavoidable, record exactly which layer changed: data, preprocessing, model, objective, optimization, evaluation, or environment
- before each retry, state the expected effect and the fastest falsification signal
- if the retry produced no interpretable delta, do not treat it as meaningful evidence about the underlying research hypothesis
- if the retry does not change the hypothesis, code path, command path, or evidence surface, stop rerunning and route through `decision`

### 5. Execute the run

Run with auditable commands and durable outputs.

Execution rules:

- use non-interactive commands
- prefer `bash_exec` instead of ephemeral shell invocations
- use the intended dataset and split
- keep logs durable
- report progress for long runs
- avoid silent metric-definition changes
- do not drift away from `active_baseline_metric_contract_json` silently when that file exists
- avoid silently changing the baseline comparison recipe
- run the full agreed evaluation, not only a smoke test

You may do a quick sanity run first, but if the stage goal is a real experiment you must continue to the real evaluation unless the run is blocked and recorded.

Pilot-before-scale rule:

- start with a bounded pilot only when the modification is non-trivial and that pilot resolves a real execution uncertainty
- use the pilot to catch implementation mistakes early
- record pilot outcomes explicitly
- do not mistake pilot success for final evidence

Incremental-recording rule:

- do not wait until the end to reconstruct the run from memory
- update the durable run note after:
  - contract definition
  - important code changes
  - pilot validation
  - full execution checkpoints
  - post-run analysis
- update `CHECKLIST.md` alongside those durable notes so the current execution frontier is obvious without replaying the whole log
- include timestamps when they materially help reconstruction
- preserve failed attempts, anomalies, and partial outcomes rather than overwriting them

Last-known-good rule:

- keep track of the most recent state that was executable, comparable, and explainable
- when a new attempt breaks that state, debug forward from the last-known-good point instead of stacking more speculative edits on top of the broken state
- if the last-known-good state is unclear, reconstruct it before spending more budget on new hypotheses

### 5.1 Long-running command protocol

For commands that may run longer than a few minutes:

- if command paths, outputs, or basic metrics are still unverified, execute one bounded smoke test or pilot first
- keep smoke/pilot budget at `0-2` for the current experiment pass
- allow a second smoke/pilot only after a real code, command, environment, or evaluator change
- once the path is verified, launch the real run with `bash_exec(mode='detach', ...)` and normally leave `timeout_seconds` unset for that long run
- monitor through durable logs rather than only live terminal output
- `bash_exec(mode='read', id=...)` returns the full rendered log when it is 2000 lines or fewer; for longer logs it returns the first 500 lines plus the last 1500 lines and a hint to inspect omitted sections with `start` and `tail`
- if the middle of a long saved log matters, inspect that omitted region with `bash_exec(mode='read', id=..., start=..., tail=...)`
- use `bash_exec(mode='list')` and `bash_exec(mode='read', id=..., tail_limit=..., order='desc')` to monitor or revisit managed commands while focusing on the newest evidence first
- after the first read, prefer `bash_exec(mode='read', id=..., after_seq=last_seen_seq, tail_limit=..., order='asc')` so later checks only fetch new evidence
- if you need to recover ids or sanity-check the active session ordering, use `bash_exec(mode='history')`
- launch important runs with a structured `comment` such as `{stage, goal, action, expected_signal, next_check}`
- use `silent_seconds`, `progress_age_seconds`, `signal_age_seconds`, and `watchdog_overdue` from `bash_exec(mode='list'|'read', ...)` as your default watchdog signals
- use an explicit wait-and-check loop such as:
  - wait about `60s`, then inspect logs
  - wait about `120s`, then inspect logs
  - wait about `300s`, then inspect logs
  - wait about `600s`, then inspect logs
  - wait about `1800s`, then inspect logs
  - then keep checking about every `1800s` while the run is still active
- if needed, use an explicit bounded wait such as `bash_exec(command='sleep 60', mode='await', timeout_seconds=70)` or `bash_exec(mode='await', id=..., timeout_seconds=...)` between checks
- canonical sleep choice:
  - if you only need wall-clock waiting between checks, use `bash_exec(command='sleep N', mode='await', timeout_seconds=N+buffer, ...)`
  - keep a real buffer on that sleep timeout; do not set `timeout_seconds` exactly equal to `N`
  - if you are waiting on an already running managed session, prefer `bash_exec(mode='await', id=..., timeout_seconds=...)` instead of starting a new sleep command
- after every completed sleep / await cycle, inspect logs first; only send `artifact.interact(kind='progress', ...)` when the user-visible state, frontier, blocker status, or ETA materially changed
- after the first meaningful signal and then at real checkpoints (e.g., completion, recovery, blocker, or a materially widened comparable surface), keep those progress updates going rather than waiting silently
- if the run is clearly invalid, wedged, or superseded, stop it with `bash_exec(mode='kill', id=..., wait=true, timeout_seconds=...)`; if it must die immediately, add `force=true`, record the reason, fix the issue, and relaunch cleanly
- do not report completion until logs and output files both confirm completion

Always preserve the managed `bash_exec` log and export it into the experiment artifact directory when the run artifact is written.

### 5.2 Progress marker protocol

Long loops should emit structured progress markers rather than noisy raw progress bars.

- use single-line JSON progress markers
- keep them throttled
- treat them as UI signals, not narrative prose
- do not paste raw progress lines into summaries
- when possible include `eta` in seconds and `next_reply_at` or `next_check_at` so web/TUI can show the next expected update

If you control the code, prefer a throttled `tqdm`-style progress reporter for the run itself and pair it with concise structured `__DS_PROGRESS__` lines when feasible so monitoring remains machine-readable.

### 6. Validate the outputs

After the run, verify:

- outputs correspond to the intended code/config
- metrics are complete and interpretable
- comparison to baseline is fair
- any failure mode or confounder is visible
- required metric keys are present and finite
- the result can be mapped back to the original claim
- the summary states a clear go or no-go recommendation

Create a durable claim-validation record that maps:

- claim
- metric key
- expected direction
- observed result
- verdict:
  - `supported`
  - `refuted`
  - `inconclusive`

Also verify baseline comparability before claiming deltas:

- was the baseline verification stable?
- was the evaluation path the same?
- are the compared metric keys identical?
- if the run is claim-carrying, are the significance results or uncertainty estimates strong enough for main-text use?
- do known caveats make the delta weaker than it first appears?

### 7. Record the run

Every meaningful main run must be recorded through `artifact.record_main_experiment(...)`.

That call is responsible for writing:

- `experiments/main/<run_id>/RUN.md`
- `experiments/main/<run_id>/RESULT.json`
- the durable `run` artifact payload
- baseline comparisons
- breakthrough status derived by the system

`artifact.record_main_experiment(...)` should include at least:

- `run_id`
- title
- hypothesis
- setup
- execution
- results
- conclusion
- baseline reference
- `metrics_summary`
- `metric_rows` when available
- the metric contract actually used
- verdict
- evidence paths
- changed files
- relevant config paths when applicable
- `evaluation_summary` with exactly these six fields:
  - `takeaway`
  - `claim_update`
  - `baseline_relation`
  - `comparability`
  - `failure_mode`
  - `next_action`

Use `evaluation_summary` as the short structured judgment layer on top of the longer narrative fields:

- `takeaway`: one sentence the next reader can reuse directly
- `claim_update`: `strengthens`, `weakens`, `narrows`, or `neutral`
- `baseline_relation`: `better`, `worse`, `mixed`, or `not_comparable`
- `comparability`: `high`, `medium`, or `low`
- `failure_mode`: `none`, `implementation`, `evaluation`, `environment`, or `direction`
- `next_action`: the immediate route such as `continue`, `revise_idea`, `analysis_campaign`, `write`, or `stop`

After `artifact.record_main_experiment(...)` succeeds, do not assume the same branch should absorb the next round by default.
Interpret the measured result first, then either:

- launch analysis from this branch, or
- compare candidate foundations and create the next child research branch

Use `artifact.create_analysis_campaign(...)` only when the extra slices have clear academic or claim-level value relative to their resource cost.
If the main need is simply to continue optimization from a measured result, prefer a new durable child idea branch instead of an expensive analysis package by reflex.
If the extra work should happen on an older durable branch rather than the current head, first switch the runtime back there with `artifact.activate_branch(...)`, then launch the analysis campaign from that activated workspace.

When `artifact.record_main_experiment(...)` succeeds, send a richer threaded `artifact.interact(kind='milestone', ...)` update rather than a generic one-line progress ping.
Lead that milestone with a concise `1-2` sentence outcome summary before expanding into more detail.
That milestone should state:

- the research question that was tested
- the primary result and baseline delta
- whether the run supports, weakens, or leaves the idea inconclusive
- the main caveat or confidence note that still matters
- the exact recommended next move

Do not treat a main run as durably complete until `artifact.record_main_experiment(...)` succeeds.

Recommended per-run documentation fields:

1. research question
2. research type
3. research objective
4. experimental setup
5. experimental results
6. experimental analysis
7. experimental conclusions

For durable main runs, these seven fields should be progressively filled as the run advances, not only at final packaging time.
For lightweight runs, a shorter summary is acceptable if the route remains obvious and the result is still durably recorded.

`RUN.md` should make it easy for later stages to answer:

- what changed?
- how can this run be reproduced?
- what are the main results?
- why did it work or fail?
- what should happen next?

Recording rules:

- record results incrementally, not only at the end
- include timestamps when helpful
- include failed attempts, partial runs, and unexpected outcomes
- do not leave placeholder sections for later if the information is already known
- report exactly what happened, not what you hoped would happen

### 8. Decide the next move

The experiment stage should normally end with one of:

- continue the current line
- branch a new line
- launch an analysis campaign
- move to writing
- reset or stop

Do not let the stage end without an explicit next direction.
If analysis is selected, record why the expected information gain is strong enough to justify the added compute, time, or annotation budget.

## Run-quality rules

A credible main run should satisfy:

- comparable against baseline
- method change is knowable from code and config
- metric source is durable
- outcome can be explained by the intended intervention or its failure
- commands, configs, and seeds are reconstructable
- environment context is reconstructable
- frontend or later readers can trace code and diff context to command, logs, and metrics

If the result is confounded, say so directly.

## Acceptance gate

Before marking the run complete, verify all of the following:

- all required baseline metric keys are present
- the reported comparison contract still matches `active_baseline_metric_contract_json` when that file exists
- metric values are finite numbers
- claim-to-metric traceability is recorded
- run manifest includes exact command, config, seed, and environment snapshot
- the summary states go or no-go and why
- artifacts are sufficient for another stage to reconstruct the run

If these checks fail, record the run as partial or blocked rather than pretending it is complete.

## Memory rules

Stage-start requirement:

- begin every experiment pass with `memory.list_recent(scope='quest', limit=5)`
- then run at least one experiment-relevant `memory.search(...)` before a new run, retry, or material execution change
- before reopening a previously tested command path, pilot, or environment fix, search memory for the last trusted result or explicit non-repeat rule
- if several idea or experiment lines exist, narrow retrieval to the current `idea_id`, `branch`, and `run_id`; do not casually reuse memory from another idea line unless you are explicitly comparing lines

Write to memory only when the lesson is reusable, such as experiment failure patterns, stable implementation lessons, evaluation pitfalls, or validated mechanism scope and caveats.
The canonical record of the run itself belongs in `artifact`, not only in memory.
When calling `memory.write(...)`, pass `tags` as an array like `["stage:experiment", "type:failure-pattern", "topic:<mechanism>"]`, not as one comma-joined string.

Stage-end requirement:

- successful runs should leave at least one reusable knowledge note if the lesson generalizes
- failed or partial runs should leave an incident note when the failure pattern is reusable
- if a smoke test or pilot established a reusable execution fact, evaluator fact, or non-repeat rule, write that lesson before the next retry or route change depends on it
- every experiment `memory.write(...)` must state whether the outcome was `success`, `partial`, or `failure`
- every experiment `memory.write(...)` should also include the current `idea_id`, `branch`, and `run_id` so later retrieval does not mix different experiment lines

## Artifact rules

- use `progress` for long-running execution updates
- use `artifact.record_main_experiment(...)` for each meaningful completed main experiment
- use `report` for suspicious-result investigations or analysis-rich summaries when they materially help the next route
- use `decision` for continue / branch / analysis / write / reset / stop
- use `approval` when an explicit user approval is captured for an expensive or risky run change
- use `artifact.checkpoint(...)` when code evolution is meaningful and should be preserved in Git
- after a meaningful experiment checkpoint or completion, emit `artifact.interact(kind='progress' | 'milestone', ...)` so the user sees the concrete result and next step

## Failure and blocked handling

A failed main run is still useful if it is explained well.

Record what was attempted, where the failure occurred, whether it was methodological or infrastructural, what retry/branch/reset is justified, and the single best next action.
Prefer a primary failure type such as `data_contract_mismatch`, `resource_exhausted`, `numeric_instability`, `implementation_bug`, `evaluation_pipeline_failure`, `external_dependency_blocked`, or `direction_underperforming`.
Also classify the broader failure layer when possible: implementation, evaluation, environment, or direction.
Blocked experiment states commonly include missing baseline reference, unknown metric contract, environment failure, run failure before metrics, or metrics that are not comparable.
When results are suspicious, fix the subset and seeds, isolate preprocessing/model/training/evaluation one by one, compare intermediate outputs on the same inputs, and run the cheapest discriminative check before another full retry.

## Exit criteria

Exit the experiment stage once one of the following is durably true:

- a main run is completed and recorded
- the run failed and the blocker is durably recorded
- the next step is clearly `analysis-campaign`, `write`, another `experiment`, or `reset`

A good experiment pass leaves one interpretable result or one explicit blocker, not another vague promise to rerun later.
