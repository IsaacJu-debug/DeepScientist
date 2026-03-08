# DeepScientist Docs

This folder defines the canonical architecture for `DeepScientist Core`.

## Reading Order

Read in this order if the goal is to implement the system:

1. `CORE_BLUEPRINT.md`
   - the smallest coherent system worth building
   - the non-negotiable design decisions
2. `CORE_ARCHITECTURE.md`
   - runtime home, config, daemon, sessions, UI, connectors, Git, baseline reuse
3. `CONFIG_AND_DISCOVERY.md`
   - what belongs in config, what is discovered from files, what can be edited from UI/TUI, and what must never be configured manually
4. `UI_AND_WEB.md`
   - dual local UI design, shared API, settings surfaces, TUI vs web workspace, mobile behavior, visual direction
5. `MEMORY_AND_MCP.md`
   - the built-in `memory` and `artifact` contract
6. `ARTIFACT_EXAMPLES.md`
   - canonical JSON examples for every fixed artifact kind
7. `PROTOCOL_SCHEMAS.md`
   - the fixed v1 shapes for quest snapshots, documents, saves, runner events, and commands
8. `WORKFLOW_AND_SKILLS.md`
   - the default research graph, decision model, analysis campaigns, skill packs
9. `TEAM_LIFECYCLE.md`
   - reserved lead/worker/worktree lifecycle and handoff model
10. `PROMPTS_AND_CONNECTORS.md`
   - the system prompt contract, installed skill references, connector interaction rules
11. `SRC_IMPLEMENTATION.md`
   - concrete code structure and install/runtime mechanics
12. `REGISTRIES.md`
   - protocol-oriented registry model, baseline registry, command and extension registries
13. `CHECKLIST.md`
   - implementation checklist, reference-before-code rules, testing examples, e2e gates
14. `IMPLEMENTATION_PLAN.md`
   - phased build order
15. `PLUGINS_AND_MARKETPLACE.md`
   - plugin kinds, OpenClaw compatibility, QQ extension strategy

## Canonical Direction

The docs assume:

- Python daemon core under `src/deepscientist/`
- `npm`-friendly bootstrap and UI delivery
- one quest = one Git repository
- default home at `~/DeepScientist`
- only two built-in MCP namespaces:
  - `memory`
  - `artifact`
- Git handled internally by `artifact`
- installed skills mirrored into `codex` and `claude` skill directories
- skill source bundles follow the Codex/OpenAI `SKILL.md` pattern, with exact Claude-compatible projection on sync
- agent-led workflow with thin daemon control
- required local TUI + local web UI and active connectors
- optional reserved `deepscientist.cc` bridge that must never replace the local-first path

## Current Code Map

The current repository now includes a working core skeleton aligned to these docs:

- runner entry:
  - `src/deepscientist/runners/codex.py`
- built-in MCP servers:
  - `src/deepscientist/mcp/context.py`
  - `src/deepscientist/mcp/server.py`
- durable services:
  - `src/deepscientist/memory/service.py`
  - `src/deepscientist/artifact/service.py`
  - `src/deepscientist/registries/baseline.py`
- quest and document model:
  - `src/deepscientist/quest/service.py`
- git branch / worktree / graph support:
  - `src/deepscientist/gitops/service.py`
  - `src/deepscientist/gitops/graph.py`
- daemon and shared API:
  - `src/deepscientist/daemon/app.py`
  - `src/deepscientist/daemon/api/handlers.py`
- local web UI and TUI entry:
  - `ui/index.html`
  - `ui/app.css`
  - `ui/app.js`
  - `src/deepscientist/tui.py`
- first-party skills:
  - `skills/*/SKILL.md`

Validated working slices now include:

- `ds init`
- `ds new`
- `ds run ...` with real Codex
- quest-local built-in `memory` + `artifact` MCP injection
- local daemon HTTP API
- quest memory / documents / config editing
- baseline publish + attach
- Git graph JSON + SVG + PNG export

## Reference Map

The following external codebases and files are intentionally referenced throughout the docs:

- old DeepScientist UI and prompt system:
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/app/AppContainer.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/components/MainContent.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/ui/src/components/Composer.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/prompt_compiler.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/core/meta/agents/`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/mcp/tools.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/tests/test_mcp_status_update.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/services/codex_service.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/services/claude_service.py`
  - `/home/air/DeepScientist_latest/DS_2027/cli/backend/app/agent_kernel/template_manager.py`
- DS_2027 web workspace and visual system:
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
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/ai-manus/AiManusChatView.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/ai-manus/components/NotebookChatBox.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/ai-manus/components/ChatMessage.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/components/plugin/PluginRenderer.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/app/globals.css`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/markdown-viewer/MarkdownViewerPlugin.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/code-viewer/CodeViewerPlugin.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/code-editor/CodeEditorPlugin.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/notebook/components/NotebookEditor.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/i18n/useI18n.ts`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/i18n/messages/projects.ts`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/lab/components/LabSurface.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/lab/components/LabQuestPage.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/lab/components/LabCopilotPanel.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/lab/components/LabOverviewCanvas.tsx`
  - `/home/air/DeepScientist_latest/DS_2027/frontend/lib/plugins/lab/components/LabQuestGraphCanvas.tsx`
- `nanoclaw` connector orchestration:
  - `/ssdwork/deepscientist/_references/nanoclaw/src/channels/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/channels/registry.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/types.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/index.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/group-queue.ts`
  - `/ssdwork/deepscientist/_references/nanoclaw/src/ipc.ts`
- `openclaw` extensibility references:
  - `/ssdwork/deepscientist/_references/openclaw/src/context-engine/registry.ts`
  - `/ssdwork/deepscientist/_references/openclaw/docs/tools/plugin.md`
  - `/ssdwork/deepscientist/_references/openclaw/extensions/telegram/index.ts`
- QQ connector background:
  - `https://cloud.tencent.com.cn/developer/article/2635190`
  - `https://cloud.tencent.com.cn/developer/article/2626045`
  - `https://cloud.tencent.com.cn/developer/article/2628828`
