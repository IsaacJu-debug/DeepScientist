# Baseline Memory Playbook

Use this reference when deciding what should be stored in quest memory versus global memory during `baseline`.
Do not treat this as a reason to block a simple fast-path baseline.

## Quest memory

Use quest memory for:

- baseline-specific setup failures
- dataset or metric caveats tied to this quest
- route-selection rationale
- paper-to-code mismatch notes
- accepted baseline caveats that later stages must remember

## Global memory

Promote to global only when the lesson is reusable, such as:

- stable environment fixes
- reproducibility heuristics
- broadly useful dataset or benchmark caveats

## Promotion rule

Do not promote a lesson to global just because it was painful.
Promote it only if another quest is likely to benefit from it.
