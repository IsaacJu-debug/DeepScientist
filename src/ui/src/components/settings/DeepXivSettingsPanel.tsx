import { ArrowUpRight, CheckCircle2, Loader2, Save, Sparkles } from "lucide-react"
import { useEffect, useMemo, useState, type ReactNode } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { HintDot } from "@/components/ui/hint-dot"
import { Input } from "@/components/ui/input"
import { client } from "@/lib/api"
import { cn } from "@/lib/utils"
import type { Locale, OpenDocumentPayload } from "@/types"

import { DeepXivSetupDialog } from "./DeepXivSetupDialog"

const REGISTER_URL = "https://data.rag.ac.cn/register"
const GUIDE_IMAGE = "/assets/images/deepxiv/register-guide.png"

type DeepXivDraft = {
  enabled: boolean
  base_url: string
  token: string
  token_env: string
  default_result_size: string
  preview_characters: string
  request_timeout_seconds: string
}

const DEFAULT_DRAFT: DeepXivDraft = {
  enabled: false,
  base_url: "https://data.rag.ac.cn",
  token: "",
  token_env: "DEEPXIV_TOKEN",
  default_result_size: "10",
  preview_characters: "1200",
  request_timeout_seconds: "20",
}

const copy = {
  en: {
    title: "DeepXiv",
    subtitle: "Structured paper discovery and paper triage for `idea` and `scout`.",
    eyebrow: "Literature provider",
    setup: "Guided setup",
    openRegister: "Register",
    save: "Save",
    saving: "Saving…",
    saved: "Saved.",
    loadingLabel: "Loading…",
    statusConfigured: "Configured",
    statusLegacy: "Legacy route",
    statusEnabled: "Enabled",
    statusDisabled: "Disabled",
    statusToken: "Token ready",
    statusTokenMissing: "Token missing",
    summary: "When a token is configured, DeepScientist can expose a DeepXiv-first route for literature discovery and shortlist paper reading. Without a token, the prompt should explicitly forbid DeepXiv and stay on the legacy route.",
    disclaimer: "Disclaimer: The DeepXiv project is supported and developed by Beijing Academy of Artificial Intelligence, and still carries potential risks.",
    accessTitle: "Access",
    accessHint: "These values are stored locally and are never inserted into the prompt as raw secrets.",
    behaviorTitle: "Runtime policy",
    behaviorHint: "These defaults shape how DeepScientist should query DeepXiv once backend support is enabled.",
    screenshotTitle: "Register page reference",
    screenshotBody: "This screenshot was captured from the official DeepXiv register page and then annotated locally with a warning banner.",
    promptTitle: "Prompt behavior",
    promptBodyEnabled: "If enabled and a token is present, the system prompt can state that DeepXiv is available and that paper-centric search should prefer the DeepXiv route.",
    promptBodyDisabled: "If the token is missing, the system prompt should explicitly forbid the DeepXiv route and force the legacy route: memory reuse, web discovery, and artifact.arxiv(...).",
    fieldEnabled: "Enable DeepXiv",
    fieldEnabledHelp: "Turn the DeepXiv route on or off at the runtime level.",
    fieldBaseUrl: "Base URL",
    fieldToken: "Direct token",
    fieldTokenEnv: "Token env var",
    fieldResultSize: "Default retrieve size",
    fieldPreviewChars: "Preview characters",
    fieldTimeout: "Request timeout (s)",
    directSecretHint: "Prefer `token_env` in shared or production environments.",
    tokenEnvHint: "Use the environment variable name exported on this machine if you do not want to store the token directly in config.",
    resultSizeHint: "Suggested default result count for paper retrieval queries.",
    previewCharsHint: "Suggested preview length for paper preview reads.",
    timeoutHint: "Maximum HTTP timeout used by the backend DeepXiv client.",
  },
  zh: {
    title: "DeepXiv",
    subtitle: "为 `idea` 与 `scout` 提供结构化论文检索与论文速读。",
    eyebrow: "文献能力提供方",
    setup: "分步配置",
    openRegister: "前往注册",
    save: "保存",
    saving: "保存中…",
    saved: "已保存。",
    loadingLabel: "加载中…",
    statusConfigured: "已配置",
    statusLegacy: "旧路线",
    statusEnabled: "已启用",
    statusDisabled: "未启用",
    statusToken: "Token 已就绪",
    statusTokenMissing: "缺少 Token",
    summary: "当 token 已配置时，DeepScientist 可以为文献发现和候选论文速读提供 DeepXiv 优先路径；如果没有 token，系统提示词应明确禁止使用 DeepXiv，并继续走旧路线。",
    disclaimer: "免责声明：此 DeepXiv 项目系智源研究院负责支持和开发，仍然存有一定的潜在风险。",
    accessTitle: "接入配置",
    accessHint: "这些值只保存在本地配置中，不会以明文 secret 的形式写进 prompt。",
    behaviorTitle: "运行时策略",
    behaviorHint: "这些默认值会影响 DeepScientist 后续如何调用 DeepXiv。",
    screenshotTitle: "注册页参考截图",
    screenshotBody: "这张截图来自官方 DeepXiv 注册页面，并在本地额外叠加了红色免责声明。",
    promptTitle: "Prompt 行为",
    promptBodyEnabled: "当启用且 token 存在时，系统提示词可以声明 DeepXiv 可用，并要求以论文为中心的检索优先走 DeepXiv 路线。",
    promptBodyDisabled: "当 token 缺失时，系统提示词应明确禁止 DeepXiv 路线，并强制使用旧路线：memory reuse、web discovery、artifact.arxiv(...).",
    fieldEnabled: "启用 DeepXiv",
    fieldEnabledHelp: "在运行时层面开启或关闭 DeepXiv 路线。",
    fieldBaseUrl: "基础 URL",
    fieldToken: "直接 Token",
    fieldTokenEnv: "Token 环境变量",
    fieldResultSize: "默认检索数量",
    fieldPreviewChars: "预览字符数",
    fieldTimeout: "请求超时（秒）",
    directSecretHint: "在共享环境或生产环境里，更推荐使用 `token_env`。",
    tokenEnvHint: "如果你不想直接把 token 写进配置，请填写这台机器上已经导出的环境变量名。",
    resultSizeHint: "论文检索默认返回的建议数量。",
    previewCharsHint: "论文 preview 读取时默认返回的字符数。",
    timeoutHint: "后端 DeepXiv 客户端使用的最大 HTTP 超时。",
  },
} satisfies Record<Locale, Record<string, string>>

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {}
}

function buildDraft(document: OpenDocumentPayload | null): DeepXivDraft {
  const structured = document?.meta?.structured_config && typeof document.meta.structured_config === "object"
    ? (document.meta.structured_config as Record<string, unknown>)
    : {}
  const literature = asObject(structured.literature)
  const deepxiv = asObject(literature.deepxiv)
  return {
    enabled: Boolean(deepxiv.enabled ?? DEFAULT_DRAFT.enabled),
    base_url: typeof deepxiv.base_url === "string" ? deepxiv.base_url : DEFAULT_DRAFT.base_url,
    token: typeof deepxiv.token === "string" ? deepxiv.token : DEFAULT_DRAFT.token,
    token_env: typeof deepxiv.token_env === "string" ? deepxiv.token_env : DEFAULT_DRAFT.token_env,
    default_result_size: String(deepxiv.default_result_size ?? DEFAULT_DRAFT.default_result_size),
    preview_characters: String(deepxiv.preview_characters ?? DEFAULT_DRAFT.preview_characters),
    request_timeout_seconds: String(deepxiv.request_timeout_seconds ?? DEFAULT_DRAFT.request_timeout_seconds),
  }
}

function mergeDraft(document: OpenDocumentPayload | null, draft: DeepXivDraft) {
  const structured = document?.meta?.structured_config && typeof document.meta.structured_config === "object"
    ? ({ ...(document.meta.structured_config as Record<string, unknown>) })
    : {}
  const literature = { ...asObject(structured.literature) }
  literature.deepxiv = {
    enabled: draft.enabled,
    base_url: draft.base_url.trim() || DEFAULT_DRAFT.base_url,
    token: draft.token.trim() || null,
    token_env: draft.token_env.trim() || null,
    default_result_size: Number(draft.default_result_size || DEFAULT_DRAFT.default_result_size),
    preview_characters: Number(draft.preview_characters || DEFAULT_DRAFT.preview_characters),
    request_timeout_seconds: Number(draft.request_timeout_seconds || DEFAULT_DRAFT.request_timeout_seconds),
  }
  structured.literature = literature
  return structured
}

function SettingRow({
  label,
  help,
  children,
}: {
  label: string
  help: string
  children: ReactNode
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm font-medium text-[#2f2b27]">
        <span>{label}</span>
        <HintDot label={help} />
      </div>
      {children}
    </div>
  )
}

export function DeepXivSettingsPanel({ locale }: { locale: Locale }) {
  const t = copy[locale]
  const [document, setDocument] = useState<OpenDocumentPayload | null>(null)
  const [draft, setDraft] = useState<DeepXivDraft>(DEFAULT_DRAFT)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState("")
  const [setupOpen, setSetupOpen] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const next = await client.configDocument('config')
      setDocument(next)
      setDraft(buildDraft(next))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const hasToken = useMemo(() => Boolean(draft.token.trim() || draft.token_env.trim()), [draft.token, draft.token_env])
  const promptReady = draft.enabled && hasToken

  const handleField = (key: keyof DeepXivDraft, value: string | boolean) => {
    setDraft((current) => ({ ...current, [key]: value } as DeepXivDraft))
    setMessage("")
  }

  const handleSave = async () => {
    if (!document) return
    setSaving(true)
    try {
      const result = await client.saveConfig('config', {
        structured: mergeDraft(document, draft),
        revision: document.revision,
      })
      if (result.ok) {
        setMessage(t.saved)
        await load()
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-[rgba(45,42,38,0.08)] bg-[linear-gradient(145deg,rgba(253,247,241,0.94),rgba(239,229,220,0.84)_42%,rgba(226,235,239,0.82))] px-6 py-6 shadow-[0_30px_100px_-68px_rgba(44,39,34,0.45)]">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" className="rounded-full bg-white/80 px-3 py-1 text-[11px] font-semibold text-[#4f4a43]">
                DeepXiv
              </Badge>
              <div className="inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#8f8578]">
                <Sparkles className="h-3.5 w-3.5" />
                {t.eyebrow}
              </div>
            </div>
            <div className="mt-3 text-3xl font-semibold tracking-[-0.03em] text-[#2f2b27]">{t.title}</div>
            <div className="mt-2 max-w-[860px] text-sm leading-7 text-[#5d5953]">{t.summary}</div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge className={cn('rounded-full px-3 py-1 text-[11px]', draft.enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-zinc-100 text-zinc-600')}>
                {draft.enabled ? t.statusEnabled : t.statusDisabled}
              </Badge>
              <Badge className={cn('rounded-full px-3 py-1 text-[11px]', hasToken ? 'bg-sky-100 text-sky-700' : 'bg-amber-100 text-amber-700')}>
                {hasToken ? t.statusToken : t.statusTokenMissing}
              </Badge>
              <Badge className={cn('rounded-full px-3 py-1 text-[11px]', promptReady ? 'bg-[#efe3d0] text-[#7a5432]' : 'bg-[#f0f0f0] text-[#6f6a64]')}>
                {promptReady ? t.statusConfigured : t.statusLegacy}
              </Badge>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button variant="secondary" className="rounded-full" onClick={() => setSetupOpen(true)}>
              {t.setup}
            </Button>
            <Button variant="outline" className="rounded-full gap-2" onClick={() => window.open(REGISTER_URL, '_blank', 'noopener,noreferrer')}>
              {t.openRegister}
              <ArrowUpRight className="h-4 w-4" />
            </Button>
            <Button className="rounded-full gap-2" onClick={() => void handleSave()} isLoading={saving}>
              <Save className="h-4 w-4" />
              {saving ? t.saving : t.save}
            </Button>
          </div>
        </div>
      </section>

      {message ? (
        <div className="text-sm text-emerald-700">{message}</div>
      ) : null}

      <section className="rounded-[22px] border border-[#d85d5d] bg-[#fff3f3] px-5 py-4 text-sm leading-7 text-[#a01818]">
        {t.disclaimer}
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
        <section className="space-y-6 rounded-[28px] border border-[rgba(45,42,38,0.08)] bg-[rgba(255,250,245,0.84)] px-5 py-5 shadow-[0_22px_70px_-58px_rgba(44,39,34,0.28)]">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#8f8578]">
              <CheckCircle2 className="h-4 w-4" />
              {t.accessTitle}
            </div>
            <div className="mt-2 text-sm leading-7 text-[#5d5953]">{t.accessHint}</div>
          </div>

          {loading ? (
            <div className="flex items-center gap-3 text-sm text-[#6e675f]">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t.loadingLabel}
            </div>
          ) : (
            <div className="space-y-5">
              <SettingRow label={t.fieldEnabled} help={t.fieldEnabledHelp}>
                <label className="flex items-center gap-3 rounded-[14px] border border-[rgba(45,42,38,0.08)] bg-white/72 px-4 py-3 text-sm text-[#2f2b27]">
                  <input
                    type="checkbox"
                    checked={draft.enabled}
                    onChange={(event) => handleField('enabled', event.target.checked)}
                    className="h-4 w-4 rounded border-[rgba(45,42,38,0.18)] text-[#7c5a37]"
                  />
                  <span>{draft.enabled ? t.statusEnabled : t.statusDisabled}</span>
                </label>
              </SettingRow>

              <SettingRow label={t.fieldBaseUrl} help={t.fieldBaseUrl}>
                <Input value={draft.base_url} onChange={(event) => handleField('base_url', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
              </SettingRow>

              <SettingRow label={t.fieldToken} help={t.directSecretHint}>
                <Input type="password" value={draft.token} onChange={(event) => handleField('token', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
              </SettingRow>

              <SettingRow label={t.fieldTokenEnv} help={t.tokenEnvHint}>
                <Input value={draft.token_env} onChange={(event) => handleField('token_env', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
              </SettingRow>

              <div className="grid gap-4 sm:grid-cols-3">
                <SettingRow label={t.fieldResultSize} help={t.resultSizeHint}>
                  <Input value={draft.default_result_size} onChange={(event) => handleField('default_result_size', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
                </SettingRow>
                <SettingRow label={t.fieldPreviewChars} help={t.previewCharsHint}>
                  <Input value={draft.preview_characters} onChange={(event) => handleField('preview_characters', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
                </SettingRow>
                <SettingRow label={t.fieldTimeout} help={t.timeoutHint}>
                  <Input value={draft.request_timeout_seconds} onChange={(event) => handleField('request_timeout_seconds', event.target.value)} className="rounded-[14px] border-black/[0.08] bg-white/72" />
                </SettingRow>
              </div>
            </div>
          )}
        </section>

        <section className="space-y-5">
          <div className="rounded-[28px] border border-[rgba(45,42,38,0.08)] bg-white px-4 py-4 shadow-[0_22px_70px_-58px_rgba(44,39,34,0.28)]">
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#8f8578]">{t.screenshotTitle}</div>
            <div className="overflow-hidden rounded-[20px] border border-[rgba(45,42,38,0.08)]">
              <img src={GUIDE_IMAGE} alt="DeepXiv register guide" className="block h-auto w-full object-cover" />
            </div>
            <div className="mt-3 text-sm leading-7 text-[#5d5953]">{t.screenshotBody}</div>
          </div>

          <div className="rounded-[28px] border border-[rgba(45,42,38,0.08)] bg-[rgba(255,250,245,0.84)] px-5 py-5 shadow-[0_22px_70px_-58px_rgba(44,39,34,0.28)]">
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#8f8578]">{t.promptTitle}</div>
            <div className="mt-3 text-sm leading-7 text-[#5d5953]">
              {promptReady ? t.promptBodyEnabled : t.promptBodyDisabled}
            </div>
          </div>
        </section>
      </div>

      <DeepXivSetupDialog open={setupOpen} onClose={() => setSetupOpen(false)} locale={locale} />
    </div>
  )
}

export default DeepXivSettingsPanel
