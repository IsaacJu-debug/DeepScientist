import { AlertTriangle, ArrowUpRight, Sparkles } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Modal, ModalFooter } from "@/components/ui/modal"
import type { Locale } from "@/types"

const REGISTER_URL = "https://data.rag.ac.cn/register"
const GUIDE_IMAGE = "/assets/images/deepxiv/register-guide.png"

const copy = {
  en: {
    title: "DeepXiv guided setup",
    description: "Use the official Agentic Data Interface registration flow, then paste the token into DeepScientist settings.",
    eyebrow: "Literature provider",
    summary: "DeepXiv gives `idea` and `scout` a stronger paper-discovery and paper-triage path. The token stays local and should never be pasted into prompts or chat.",
    disclaimer: "Disclaimer: The DeepXiv project is supported and developed by Beijing Academy of Artificial Intelligence, and still carries potential risks.",
    openRegister: "Open DeepXiv register",
    close: "Close",
    screenshotCaption: "Registration page captured from the official DeepXiv site, with an added warning banner for local operator guidance.",
    steps: [
      {
        title: "1. Create a DeepXiv account",
        body: "Open the official register page, complete verification, and keep the token issuance page open until you finish copying the value.",
      },
      {
        title: "2. Copy the token into Settings",
        body: "Paste the token into the DeepXiv settings card, or store it in an environment variable and reference that variable name instead.",
      },
      {
        title: "3. Save before running idea / scout",
        body: "Once saved, DeepScientist can enable the DeepXiv route in prompts and backend tools. If it is not saved, the prompt should stay on the legacy route.",
      },
      {
        title: "4. Keep the token private",
        body: "The token should stay in config or env only. Do not paste it into prompts, issues, logs, screenshots, or chat transcripts.",
      },
    ],
  },
  zh: {
    title: "DeepXiv 分步配置",
    description: "使用官方 Agentic Data Interface 注册页获取 token，然后回到 DeepScientist 设置中保存。",
    eyebrow: "文献能力提供方",
    summary: "DeepXiv 可以为 `idea` 和 `scout` 提供更强的论文发现与论文速读路径。token 只保留在本地配置中，不应该出现在系统提示词或聊天里。",
    disclaimer: "免责声明：此 DeepXiv 项目系智源研究院负责支持和开发，仍然存有一定的潜在风险。",
    openRegister: "打开 DeepXiv 注册页",
    close: "关闭",
    screenshotCaption: "该截图来自官方 DeepXiv 注册页面，并额外加上了本地操作提示用的红色免责声明。",
    steps: [
      {
        title: "1. 创建 DeepXiv 账号",
        body: "打开官方注册页，完成验证，并在拿到 token 后先不要关闭页面。",
      },
      {
        title: "2. 把 token 填回设置页",
        body: "将 token 粘贴到 DeepScientist 的 DeepXiv 配置中；如果你更偏好环境变量，也可以只填写环境变量名。",
      },
      {
        title: "3. 保存后再进入 idea / scout",
        body: "保存成功后，DeepScientist 才会在系统提示词和后端工具中启用 DeepXiv；如果没有保存，系统应继续使用旧路线。",
      },
      {
        title: "4. 注意保密",
        body: "token 只应该保留在本地配置或环境变量里，不应粘贴到 prompt、issue、日志、截图或聊天记录中。",
      },
    ],
  },
} satisfies Record<Locale, {
  title: string
  description: string
  eyebrow: string
  summary: string
  disclaimer: string
  openRegister: string
  close: string
  screenshotCaption: string
  steps: Array<{ title: string; body: string }>
}>

export function DeepXivSetupDialog({
  open,
  onClose,
  locale,
}: {
  open: boolean
  onClose: () => void
  locale: Locale
}) {
  const t = copy[locale]

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t.title}
      description={t.description}
      size="xl"
      className="w-full max-w-[min(1100px,96vw)]"
    >
      <div className="space-y-5">
        <section className="rounded-[24px] border border-[rgba(45,42,38,0.08)] bg-[linear-gradient(145deg,rgba(253,247,241,0.94),rgba(239,229,220,0.84)_42%,rgba(226,235,239,0.82))] px-5 py-5 shadow-[0_24px_80px_-60px_rgba(44,39,34,0.4)]">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="rounded-full bg-white/75 px-3 py-1 text-[11px] font-semibold text-[#4f4a43]">
              DeepXiv
            </Badge>
            <div className="inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#8f8578]">
              <Sparkles className="h-3.5 w-3.5" />
              {t.eyebrow}
            </div>
          </div>
          <div className="mt-3 max-w-[820px] text-sm leading-7 text-[#4f4a43]">{t.summary}</div>
        </section>

        <section className="overflow-hidden rounded-[24px] border border-[rgba(45,42,38,0.08)] bg-white shadow-[0_22px_70px_-54px_rgba(44,39,34,0.28)]">
          <img src={GUIDE_IMAGE} alt="DeepXiv register guide" className="block h-auto w-full object-cover" />
          <div className="border-t border-[rgba(45,42,38,0.08)] px-4 py-3 text-xs leading-6 text-[#6e675f]">
            {t.screenshotCaption}
          </div>
        </section>

        <section className="rounded-[20px] border border-[#d85d5d] bg-[#fff3f3] px-4 py-3 text-sm leading-7 text-[#a01818]">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>{t.disclaimer}</div>
          </div>
        </section>

        <section className="grid gap-3 md:grid-cols-2">
          {t.steps.map((step) => (
            <div
              key={step.title}
              className="rounded-[18px] border border-[rgba(45,42,38,0.08)] bg-[rgba(255,250,245,0.84)] px-4 py-4 shadow-[0_16px_42px_-34px_rgba(44,39,34,0.24)]"
            >
              <div className="text-sm font-semibold text-[#2f2b27]">{step.title}</div>
              <div className="mt-2 text-sm leading-7 text-[#5d5953]">{step.body}</div>
            </div>
          ))}
        </section>
      </div>
      <ModalFooter className="-mx-6 -mb-4 mt-5">
        <Button variant="secondary" onClick={onClose}>
          {t.close}
        </Button>
        <Button
          onClick={() => window.open(REGISTER_URL, '_blank', 'noopener,noreferrer')}
          className="gap-2"
        >
          {t.openRegister}
          <ArrowUpRight className="h-4 w-4" />
        </Button>
      </ModalFooter>
    </Modal>
  )
}

export default DeepXivSetupDialog
