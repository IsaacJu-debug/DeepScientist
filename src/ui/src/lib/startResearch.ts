export type ResearchScope = 'baseline_only' | 'baseline_plus_direction' | 'full_research'
export type BaselineMode =
  | 'existing'
  | 'restore_from_url'
  | 'allow_degraded_minimal_reproduction'
  | 'stop_if_insufficient'
export type ResourcePolicy = 'conservative' | 'balanced' | 'aggressive'
export type GitStrategy =
  | 'branch_per_analysis_then_paper'
  | 'semantic_head_plus_controlled_integration'
  | 'manual_integration_only'
export type StartResearchContractPresetId = 'safe_baseline' | 'direction_probe' | 'full_sprint'

export type StartResearchTemplate = {
  title: string
  quest_id: string
  goal: string
  baseline_id: string
  baseline_variant_id: string
  baseline_urls: string
  paper_urls: string
  runtime_constraints: string
  objectives: string
  scope: ResearchScope
  baseline_mode: BaselineMode
  resource_policy: ResourcePolicy
  time_budget_hours: string
  git_strategy: GitStrategy
  user_language: 'en' | 'zh'
}

export type StartResearchContractFields = Pick<
  StartResearchTemplate,
  'scope' | 'baseline_mode' | 'resource_policy' | 'time_budget_hours' | 'git_strategy'
>

export type StartResearchTemplateEntry = StartResearchTemplate & {
  id: string
  updated_at: string
  compiled_prompt: string
}

const START_RESEARCH_CONTRACT_PRESETS: Record<
  StartResearchContractPresetId,
  {
    id: StartResearchContractPresetId
    contract: StartResearchContractFields
  }
> = {
  safe_baseline: {
    id: 'safe_baseline',
    contract: {
      scope: 'baseline_only',
      baseline_mode: 'stop_if_insufficient',
      resource_policy: 'conservative',
      time_budget_hours: '8',
      git_strategy: 'manual_integration_only',
    },
  },
  direction_probe: {
    id: 'direction_probe',
    contract: {
      scope: 'baseline_plus_direction',
      baseline_mode: 'restore_from_url',
      resource_policy: 'balanced',
      time_budget_hours: '24',
      git_strategy: 'semantic_head_plus_controlled_integration',
    },
  },
  full_sprint: {
    id: 'full_sprint',
    contract: {
      scope: 'full_research',
      baseline_mode: 'allow_degraded_minimal_reproduction',
      resource_policy: 'aggressive',
      time_budget_hours: '48',
      git_strategy: 'branch_per_analysis_then_paper',
    },
  },
}

export const START_RESEARCH_CONTRACT_PRESET_ORDER: StartResearchContractPresetId[] = [
  'safe_baseline',
  'direction_probe',
  'full_sprint',
]

export const START_RESEARCH_STORAGE_KEY = 'ds:start-research:v3'
export const START_RESEARCH_HISTORY_KEY = 'ds:start-research:history:v2'
const MAX_TEMPLATE_HISTORY = 8

export function slugifyQuestRepo(value: string) {
  const normalized = value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return normalized.slice(0, 80)
}

export function deriveQuestRepoId(input: { title?: string; goal?: string }) {
  const fromTitle = slugifyQuestRepo(input.title || '')
  if (fromTitle) {
    return fromTitle
  }
  const fromGoal = slugifyQuestRepo((input.goal || '').split(/\n+/)[0] || '')
  return fromGoal
}

export function defaultStartResearchTemplate(language: 'en' | 'zh'): StartResearchTemplate {
  return {
    title: '',
    quest_id: '',
    goal: '',
    baseline_id: '',
    baseline_variant_id: '',
    baseline_urls: '',
    paper_urls: '',
    runtime_constraints: '',
    objectives: '',
    scope: 'full_research',
    baseline_mode: 'stop_if_insufficient',
    resource_policy: 'balanced',
    time_budget_hours: '',
    git_strategy: 'branch_per_analysis_then_paper',
    user_language: language,
  }
}

export function listStartResearchContractPresets() {
  return START_RESEARCH_CONTRACT_PRESET_ORDER.map((presetId) => START_RESEARCH_CONTRACT_PRESETS[presetId])
}

export function applyStartResearchContractPreset(
  input: StartResearchTemplate,
  presetId: StartResearchContractPresetId
): StartResearchTemplate {
  return {
    ...input,
    ...START_RESEARCH_CONTRACT_PRESETS[presetId].contract,
  }
}

export function detectStartResearchContractPreset(
  input: Pick<StartResearchTemplate, keyof StartResearchContractFields>
): StartResearchContractPresetId | null {
  const fields: (keyof StartResearchContractFields)[] = [
    'scope',
    'baseline_mode',
    'resource_policy',
    'time_budget_hours',
    'git_strategy',
  ]
  return (
    START_RESEARCH_CONTRACT_PRESET_ORDER.find((presetId) =>
      fields.every((field) => START_RESEARCH_CONTRACT_PRESETS[presetId].contract[field] === input[field])
    ) ?? null
  )
}

function sanitizeLines(text: string) {
  return text
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function sanitizeTemplate(input: StartResearchTemplate): StartResearchTemplate {
  const legacyBaselineId = (input as StartResearchTemplate & { baseline_root_id?: string }).baseline_root_id
  return {
    ...input,
    title: input.title.trim(),
    quest_id: slugifyQuestRepo(input.quest_id),
    goal: input.goal.trim(),
    baseline_id: String(input.baseline_id || legacyBaselineId || '').trim(),
    baseline_variant_id: input.baseline_variant_id.trim(),
    baseline_urls: input.baseline_urls.trim(),
    paper_urls: input.paper_urls.trim(),
    runtime_constraints: input.runtime_constraints.trim(),
    objectives: input.objectives.trim(),
    time_budget_hours: input.time_budget_hours.trim(),
  }
}

function stableId(input: StartResearchTemplate) {
  const source = JSON.stringify(sanitizeTemplate(input))
  let hash = 0
  for (let index = 0; index < source.length; index += 1) {
    hash = (hash * 31 + source.charCodeAt(index)) >>> 0
  }
  return `tmpl_${hash.toString(36)}`
}

function labelScope(value: ResearchScope) {
  switch (value) {
    case 'baseline_only':
      return 'Baseline only: stop after a solid reusable baseline is established.'
    case 'baseline_plus_direction':
      return 'Baseline + direction: secure the baseline, then test one promising improvement direction.'
    default:
      return 'Full research: baseline, idea selection, implementation, analysis, and writing readiness.'
  }
}

function labelBaselineMode(value: BaselineMode) {
  switch (value) {
    case 'existing':
      return 'Use existing baseline: select a reusable baseline entry and let runtime attach and confirm it before the quest begins.'
    case 'restore_from_url':
      return 'Restore from URL: recover the baseline from provided repositories or artifact links.'
    case 'allow_degraded_minimal_reproduction':
      return 'Allow degraded minimal reproduction: accept a weaker but still measurable baseline if exact recovery is impossible.'
    default:
      return 'Stop if insufficient: pause the quest instead of faking a baseline when evidence is missing.'
  }
}

function labelResourcePolicy(value: ResourcePolicy) {
  switch (value) {
    case 'conservative':
      return 'Conservative: minimize compute and only run the most justified steps.'
    case 'aggressive':
      return 'Aggressive: spend more resources to search broadly and move faster.'
    default:
      return 'Balanced: keep progress steady while still controlling cost and risk.'
  }
}

function labelGitStrategy(value: GitStrategy) {
  switch (value) {
    case 'semantic_head_plus_controlled_integration':
      return 'Semantic head + controlled integration: keep a cleaner main line and merge only reviewed branches.'
    case 'manual_integration_only':
      return 'Manual integration only: avoid automatic integration and require explicit merge decisions.'
    default:
      return 'Branch per analysis then paper: split main experiment and downstream analysis branches before final paper integration.'
  }
}

export function compileStartResearchPrompt(input: StartResearchTemplate) {
  const normalized = sanitizeTemplate(input)
  const baselineUrls = sanitizeLines(normalized.baseline_urls)
  const paperUrls = sanitizeLines(normalized.paper_urls)
  const baselineVariant = normalized.baseline_variant_id
  const baselineContext = normalized.baseline_id
    ? `Runtime will attach and confirm baseline_id ${normalized.baseline_id}${baselineVariant ? ` (variant ${baselineVariant})` : ''} before the quest starts. Treat it as the pre-bound baseline unless you find a concrete incompatibility, corruption, or missing-evidence problem.`
    : baselineUrls.length > 0
      ? baselineUrls.map((url) => `- ${url}`).join('\n')
      : 'No baseline link has been attached yet. The first obligation is to discover, repair, or reconstruct a reusable baseline.'
  const questRepo = normalized.quest_id || deriveQuestRepoId(normalized) || 'auto-generated-on-create'
  const objectiveLines = normalized.objectives
    ? sanitizeLines(normalized.objectives).map((line) => `- ${line}`).join('\n')
    : '- Produce a trustworthy baseline\n- Decide whether the current direction is worth implementation\n- Preserve clean artifacts, metrics, and reasons for each decision'

  return [
    'Quest Bootstrap',
    `- Quest title: ${normalized.title || 'Untitled quest'}`,
    `- Quest repository id: ${questRepo}`,
    `- User language: ${normalized.user_language === 'zh' ? 'Chinese' : 'English'}`,
    '',
    'Primary Research Request',
    normalized.goal || 'No goal provided.',
    '',
    'Research Goals',
    objectiveLines,
    '',
    'Baseline Context',
    baselineContext,
    '',
    'Reference Papers / Repositories',
    paperUrls.length > 0 ? paperUrls.map((url) => `- ${url}`).join('\n') : '- None provided',
    '',
    'Operational Constraints',
    normalized.runtime_constraints || 'No explicit runtime, privacy, dataset, or hardware constraints were provided.',
    '',
    'Research Contract',
    `- Scope: ${labelScope(normalized.scope)}`,
    `- Baseline policy: ${labelBaselineMode(normalized.baseline_mode)}`,
    `- Resource policy: ${labelResourcePolicy(normalized.resource_policy)}`,
    `- Git strategy: ${labelGitStrategy(normalized.git_strategy)}`,
    `- Time budget per research round: ${normalized.time_budget_hours ? `${normalized.time_budget_hours} hour(s)` : 'Not specified. Treat each round as bounded and report before starting another expensive round.'}`,
    '',
    'Mandatory Working Rules',
    '- Keep all durable files inside the quest root.',
    '- Reuse existing baseline artifacts whenever possible before rebuilding them.',
    '- Emit explicit milestone updates after each meaningful step.',
    '- Every decision must include reasons, evidence, and the next recommended action.',
    '- Ask the user before crossing a major cost, scope, or direction boundary.',
  ].join('\n')
}

export function loadStartResearchTemplate(language: 'en' | 'zh') {
  if (typeof window === 'undefined') {
    return defaultStartResearchTemplate(language)
  }
  try {
    const raw = window.localStorage.getItem(START_RESEARCH_STORAGE_KEY)
    if (!raw) {
      return defaultStartResearchTemplate(language)
    }
    const parsed = JSON.parse(raw) as Partial<StartResearchTemplate>
    const base = {
      ...defaultStartResearchTemplate(language),
      ...parsed,
      baseline_id: String(
        (parsed as Partial<StartResearchTemplate> & { baseline_root_id?: string }).baseline_root_id || parsed.baseline_id || ''
      ),
      user_language: language,
    }
    return {
      ...base,
      quest_id: base.quest_id || deriveQuestRepoId(base),
    }
  } catch {
    return defaultStartResearchTemplate(language)
  }
}

export function saveStartResearchDraft(input: StartResearchTemplate) {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.setItem(START_RESEARCH_STORAGE_KEY, JSON.stringify(sanitizeTemplate(input)))
}

export function loadStartResearchHistory(): StartResearchTemplateEntry[] {
  if (typeof window === 'undefined') {
    return []
  }
  try {
    const raw = window.localStorage.getItem(START_RESEARCH_HISTORY_KEY)
    if (!raw) {
      return []
    }
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      return []
    }
    return parsed
      .filter((item) => item && typeof item === 'object')
      .map((item) => {
        const rawItem = item as Partial<StartResearchTemplateEntry> & { baseline_root_id?: string }
        const normalized = sanitizeTemplate({
          ...defaultStartResearchTemplate((rawItem.user_language as 'en' | 'zh') || languageFromHistory(rawItem)),
          ...rawItem,
          baseline_id: String(rawItem.baseline_id || rawItem.baseline_root_id || ''),
        })
        return {
          ...rawItem,
          ...normalized,
        } as StartResearchTemplateEntry
      })
      .sort((left, right) => right.updated_at.localeCompare(left.updated_at))
      .slice(0, MAX_TEMPLATE_HISTORY)
  } catch {
    return []
  }
}

function languageFromHistory(item: Partial<StartResearchTemplateEntry>): 'en' | 'zh' {
  return item.user_language === 'en' ? 'en' : 'zh'
}

export function saveStartResearchTemplate(input: StartResearchTemplate): StartResearchTemplateEntry {
  const normalized = sanitizeTemplate(input)
  const next: StartResearchTemplateEntry = {
    ...normalized,
    quest_id: normalized.quest_id || deriveQuestRepoId(normalized),
    id: stableId(normalized),
    updated_at: new Date().toISOString(),
    compiled_prompt: compileStartResearchPrompt(normalized),
  }

  if (typeof window !== 'undefined') {
    saveStartResearchDraft(next)
    const current = loadStartResearchHistory().filter((item) => item.id !== next.id)
    const merged = [next, ...current].slice(0, MAX_TEMPLATE_HISTORY)
    window.localStorage.setItem(START_RESEARCH_HISTORY_KEY, JSON.stringify(merged))
  }

  return next
}
