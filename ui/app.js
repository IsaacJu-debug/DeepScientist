const state = {
  locale: 'en',
  quests: [],
  activeQuestId: null,
  activeDocument: null,
}

const messages = {
  en: {
    quests: 'Quests',
    createQuest: 'Create quest',
    copilot: 'Copilot',
    send: 'Send',
    runSkill: 'Run skill',
    run: 'Run',
    status: 'Status',
    memory: 'Memory',
    documents: 'Documents',
    graph: 'Git graph',
    assets: 'Assets',
    settings: 'Settings',
  },
  zh: {
    quests: '课题',
    createQuest: '新建课题',
    copilot: '对话',
    send: '发送',
    runSkill: '执行技能',
    run: '运行',
    status: '状态',
    memory: '记忆',
    documents: '文档',
    graph: 'Git 图',
    assets: '资产',
    settings: '设置',
  },
}

function t(key) {
  return messages[state.locale][key] || key
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text)
  }
  const contentType = response.headers.get('Content-Type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

function el(id) {
  return document.getElementById(id)
}

function applyLocale() {
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n)
  })
  el('locale-button').textContent = state.locale === 'en' ? '中文' : 'EN'
}

async function refreshQuests() {
  state.quests = await api('/api/quests')
  renderQuestList()
  if (!state.activeQuestId && state.quests.length) {
    state.activeQuestId = state.quests[0].quest_id
  }
  if (state.activeQuestId) {
    await loadQuest(state.activeQuestId)
  }
}

function renderQuestList() {
  const root = el('quest-list')
  root.innerHTML = ''
  for (const quest of state.quests) {
    const card = document.createElement('button')
    card.className = `quest-card ${quest.quest_id === state.activeQuestId ? 'active' : ''}`
    card.innerHTML = `
      <div><strong>${quest.title}</strong></div>
      <div class="muted">${quest.quest_id}</div>
      <div class="muted">${quest.active_anchor} · ${quest.status}</div>
    `
    card.onclick = async () => {
      state.activeQuestId = quest.quest_id
      renderQuestList()
      await loadQuest(quest.quest_id)
    }
    root.appendChild(card)
  }
}

async function loadQuest(questId) {
  const [snapshot, history, memory, documents, graph] = await Promise.all([
    api(`/api/quests/${questId}`),
    api(`/api/quests/${questId}/history`),
    api(`/api/quests/${questId}/memory`),
    api(`/api/quests/${questId}/documents`),
    api(`/api/quests/${questId}/graph`),
  ])
  el('active-quest-chip').textContent = questId
  el('topbar-title').textContent = snapshot.title || questId
  renderStatus(snapshot)
  renderHistory(history)
  renderMemory(memory)
  renderDocuments(documents)
  renderGraph(graph)
}

function renderStatus(snapshot) {
  const root = el('quest-status')
  root.innerHTML = ''
  const fields = [
    ['quest_id', snapshot.quest_id],
    ['status', snapshot.status],
    ['anchor', snapshot.active_anchor],
    ['runner', snapshot.runner || snapshot.default_runner],
    ['branch', snapshot.branch],
    ['head', snapshot.head],
  ]
  for (const [key, value] of fields) {
    const card = document.createElement('div')
    card.className = 'mini-card'
    card.innerHTML = `<div class="muted">${key}</div><div>${value ?? ''}</div>`
    root.appendChild(card)
  }
}

function renderHistory(history) {
  const root = el('history-list')
  root.innerHTML = ''
  for (const item of history) {
    const card = document.createElement('div')
    card.className = `message-card ${item.role === 'assistant' ? 'assistant' : 'user'}`
    card.innerHTML = `
      <div class="role">${item.role} · ${item.source || ''}</div>
      <div>${(item.content || '').replace(/</g, '&lt;')}</div>
    `
    root.appendChild(card)
  }
}

function renderMemory(memoryItems) {
  const root = el('memory-list')
  root.innerHTML = ''
  for (const item of memoryItems) {
    const card = document.createElement('button')
    card.className = 'mini-card'
    card.innerHTML = `
      <div><strong>${item.title || item.path}</strong></div>
      <div class="muted">${item.type || ''}</div>
      <div class="muted">${item.excerpt || ''}</div>
    `
    if (item.document_id) {
      card.onclick = () => openDocument(item.document_id)
    }
    root.appendChild(card)
  }
}

function renderDocuments(documents) {
  const root = el('document-list')
  root.innerHTML = ''
  for (const item of documents) {
    const card = document.createElement('button')
    card.className = 'mini-card'
    card.innerHTML = `
      <div><strong>${item.title}</strong></div>
      <div class="muted">${item.kind}</div>
    `
    card.onclick = () => openDocument(item.document_id)
    root.appendChild(card)
  }
}

function renderGraph(graph) {
  el('graph-box').textContent = (graph.lines || []).join('\n')
}

async function openDocument(documentId) {
  if (!state.activeQuestId) return
  const payload = await api(`/api/quests/${state.activeQuestId}/documents/open`, {
    method: 'POST',
    body: JSON.stringify({ document_id: documentId }),
  })
  state.activeDocument = payload
  el('document-title').textContent = payload.title
  el('document-editor').value = payload.content
  el('document-editor').readOnly = !payload.writable
  el('save-document-button').disabled = !payload.writable
  el('save-document-button').textContent = payload.writable ? 'Save' : 'Read only'
  el('document-dialog').showModal()
}

async function saveDocument() {
  if (!state.activeDocument) return
  if (!state.activeDocument.writable) {
    return
  }
  const content = el('document-editor').value
  const path = state.activeDocument.configName
    ? `/api/config/${state.activeDocument.configName}`
    : `/api/quests/${state.activeQuestId}/documents/${state.activeDocument.document_id}`
  const payload = await api(path, {
    method: 'PUT',
    body: JSON.stringify({ content, revision: state.activeDocument.revision }),
  })
  if (payload.ok) {
    el('document-dialog').close()
    if (state.activeQuestId) {
      await loadQuest(state.activeQuestId)
    }
  }
}

async function sendChat(event) {
  event.preventDefault()
  if (!state.activeQuestId) return
  const input = el('chat-input')
  const text = input.value.trim()
  if (!text) return
  await api(`/api/quests/${state.activeQuestId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ text, source: 'web' }),
  })
  input.value = ''
  await loadQuest(state.activeQuestId)
}

async function runSkill(event) {
  event.preventDefault()
  if (!state.activeQuestId) return
  const payload = await api(`/api/quests/${state.activeQuestId}/runs`, {
    method: 'POST',
    body: JSON.stringify({
      skill_id: el('run-skill').value,
      model: el('run-model').value.trim(),
      message: el('run-message').value.trim(),
    }),
  })
  el('run-output').textContent = JSON.stringify(payload, null, 2)
  await loadQuest(state.activeQuestId)
}

async function createQuest(event) {
  event.preventDefault()
  const goal = el('create-quest-goal').value.trim()
  if (!goal) return
  const createResponse = await api('/api/quests', {
    method: 'POST',
    body: JSON.stringify({ goal }),
  })
  if (createResponse.ok) {
    state.activeQuestId = createResponse.snapshot.quest_id
    el('create-quest-goal').value = ''
    await refreshQuests()
  }
}

async function loadSettings() {
  const items = await api('/api/config/files')
  const root = el('settings-list')
  root.innerHTML = ''
  for (const item of items) {
    const card = document.createElement('button')
    card.className = 'setting-card'
    card.innerHTML = `
      <div><strong>${item.name}</strong></div>
      <div class="muted">${item.path}</div>
      <div class="muted">${item.required ? 'required' : 'optional'}</div>
    `
    card.onclick = async () => {
      const payload = await api(`/api/config/${item.name}`)
      state.activeDocument = { ...payload, configName: item.name }
      el('document-title').textContent = payload.title
      el('document-editor').value = payload.content
      el('document-editor').readOnly = false
      el('save-document-button').disabled = false
      el('save-document-button').textContent = 'Save'
      el('settings-dialog').close()
      el('document-dialog').showModal()
    }
    root.appendChild(card)
  }
}

async function loadAssets() {
  try {
    const assetIndex = await api('/assets/text/index.json')
    const root = el('asset-list')
    root.innerHTML = ''
    for (const item of assetIndex.items || []) {
      const card = document.createElement('a')
      card.className = 'mini-card'
      card.href = item.path
      card.target = '_blank'
      card.rel = 'noreferrer'
      card.innerHTML = `
        <div><strong>${item.title}</strong></div>
        <div class="muted">${item.path}</div>
      `
      root.appendChild(card)
    }
  } catch (error) {
    el('asset-list').textContent = String(error)
  }
}

function wireEvents() {
  el('refresh-button').onclick = refreshQuests
  el('settings-button').onclick = async () => {
    await loadSettings()
    el('settings-dialog').showModal()
  }
  el('locale-button').onclick = () => {
    state.locale = state.locale === 'en' ? 'zh' : 'en'
    applyLocale()
  }
  el('chat-form').onsubmit = sendChat
  el('run-form').onsubmit = runSkill
  el('create-quest-form').onsubmit = createQuest
  el('save-document-button').onclick = saveDocument
}

async function boot() {
  applyLocale()
  wireEvents()
  await loadAssets()
  await refreshQuests()
}

boot().catch((error) => {
  console.error(error)
  el('run-output').textContent = String(error)
})
