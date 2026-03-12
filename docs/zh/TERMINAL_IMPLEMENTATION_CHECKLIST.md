# Terminal 实现 Checklist

这份 checklist 用来跟踪 quest-local “交互式 Terminal”能力的分阶段落地。

Terminal 需要保持：

- `bash_exec`-native（不新增 MCP namespace）
- quest-local（默认 cwd 在当前 quest 的 workspace）
- 刷新/重连可恢复
- connector 可用（`/terminal` 与 `-R` 恢复）
- UI 极简、玻璃/莫兰迪风格一致

## 1. Scope 锁定

- [x] 主架构：Terminal 是 `bash_exec` 的一种会话子类型，不是新 MCP。
- [x] 默认 terminal cwd：当前 active workspace root；否则回退到 `quest_root`。
- [x] agent 的正式实验执行仍走结构化 `bash_exec`（可审计），而不是人工 Terminal。
- [ ] 文档化清楚两类会话的分工：
  - `exec`：agent 管理的运行（训练/评测）
  - `terminal`：人类交互连续的 shell（类似 screen）

## 2. 后端会话模型

- [ ] 扩展 `bash_exec` session meta：`kind: exec | terminal`。
- [ ] 终端会话在 `.ds/bash_exec/<session_id>/` 下保存：
  - `meta.json`
  - `log.jsonl`
  - `terminal.log`
  - `input.jsonl`
  - `input.cursor.json`
  - `history.jsonl`
  - `progress.json`
- [ ] 每个 quest 一个稳定默认 session id，例如 `terminal-main`。
- [ ] 终端会话需要跨页面刷新、daemon 重连仍可恢复。
- [ ] 追踪当前 cwd（写入 meta）。
- [ ] 维护最近命令摘要，用于 `/terminal -R` 快速恢复。

## 3. Monitor / PTY 运行时

- [ ] 扩展 `src/deepscientist/bash_exec/monitor.py`：支持交互式 PTY 输入回放。
- [ ] 轮询 `input.jsonl` 并把新增输入写入 live PTY。
- [ ] 每条接受的输入写入 `history.jsonl`。
- [ ] 注入并解析稳定的 prompt marker，用于安全更新 cwd。
- [ ] stop/terminate 语义与现有 `bash_exec` 保持一致。
- [ ] 同时保留：
  - 原始输出：`terminal.log`
  - 结构化输出：`log.jsonl`

## 4. 后端 API

- [ ] `POST /api/quests/<quest_id>/terminal/session/ensure`
- [ ] `POST /api/quests/<quest_id>/terminal/sessions/<session_id>/input`
- [ ] `GET /api/quests/<quest_id>/terminal/sessions/<session_id>/restore`
- [ ] `GET /api/quests/<quest_id>/terminal/sessions/<session_id>/stream`
- [ ] `GET /api/quests/<quest_id>/terminal/history`
- [ ] 保持 `/api/quests/<quest_id>/bash/sessions/*` 仍可用于历史回放与审计。

## 5. 命令与 Connector 路由

- [ ] 在 ACP slash commands 中加入 `/terminal`。
- [ ] 支持 `/terminal`（无参数）：
  - ensure 默认 session
  - 返回 session id、cwd、status
- [ ] 支持 `/terminal <command>`：
  - ensure 默认 session
  - 提交输入
  - 立即 ack
- [ ] 支持 `/terminal -R`：
  - 返回 cwd
  - 返回最近 10 条命令
  - 返回 status
  - 返回最近输出 tail
- [ ] connector 的 `/terminal` 回复应是定向 ack/restore，而不是广播放大号 milestone。
- [ ] 常规研究进度仍走 `artifact.interact(...)`。

## 6. Web UI

- [ ] 在 workspace 中新增 `Terminal` 视图（与 `Studio`/`Chat` 并列）。
- [ ] 复用 `src/ui/src/lib/plugins/cli` 的 xterm 能力。
- [ ] 风格保持极简：
  - 低噪声玻璃卡片
  - 细边框
  - 莫兰迪色系
  - 强可读性
- [ ] 左侧 rail：
  - 默认 live quest terminal
  - 最近的 `bash_exec` sessions
- [ ] 右侧主区：
  - header（cwd/status）
  - restore / clear / search
  - live xterm
- [ ] 历史 `bash_exec` 上方复用 `AgentCommentBlock`。
- [ ] Web 刷新后自动恢复 terminal 状态。

## 7. TUI / 共享协议

- [ ] 复用同一套后端 routes 与 payload shape。
- [ ] TUI 支持 `/terminal`、`/terminal -R`、`/terminal <command>`。
- [ ] ACP 作为轻量 terminal 生命周期事件的统一 envelope。
- [ ] raw terminal output 走 terminal stream，不要塞进主 copilot feed（避免污染）。

## 8. 文档

- [ ] 在 `docs/zh/TUI_USAGE.md` 增加 `/terminal` 用法说明。
- [ ] 在 `docs/zh/RUNTIME_FLOW_AND_CANVAS.md` 增加 terminal session 语义说明。
- [ ] 增加一份 terminal protocol 文档：
  - session model
  - API
  - connector 行为
  - restore 行为
  - Web UI 映射

## 9. 测试

- [ ] 后端：terminal session ensure 可用。
- [ ] 后端：terminal 输入可持久更新 cwd。
- [ ] 后端：`/terminal -R` 返回 cwd + 最近命令。
- [ ] 后端：stop/reconnect 行为正确。
- [ ] 后端：connector `/terminal` 路由正确。
- [ ] Web：Terminal view 可渲染并可恢复。
- [ ] Web：历史 `bash_exec` 显示 `comment`。
- [ ] Web：live terminal 可输入，刷新后输出可恢复。

## 10. 完成标准

- [ ] Web 刷新仍可看到并恢复 quest terminal。
- [ ] `/terminal pwd` 能从命令面执行。
- [ ] `/terminal -R` 能从 connector 执行。
- [ ] 历史 `bash_exec` 回放与 live terminal 能在 UI 中清晰共存。
- [ ] 文档与测试同时通过。

