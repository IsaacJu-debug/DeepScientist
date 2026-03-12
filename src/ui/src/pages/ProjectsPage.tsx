import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog'
import { OpenQuestDialog } from '@/components/projects/OpenQuestDialog'
import { ProjectsAppBar } from '@/components/projects/ProjectsAppBar'
import { ProjectsHero } from '@/components/projects/ProjectsHero'
import { client } from '@/lib/api'
import { useI18n } from '@/lib/i18n'
import type { QuestSummary } from '@/types'

function sortProjects(items: QuestSummary[]) {
  return [...items].sort((left, right) => {
    const leftTime = new Date(left.updated_at || 0).getTime()
    const rightTime = new Date(right.updated_at || 0).getTime()
    return rightTime - leftTime
  })
}

export function ProjectsPage() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [projects, setProjects] = useState<QuestSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [openDialogOpen, setOpenDialogOpen] = useState(false)

  const loadProjects = async () => {
    setLoading(true)
    try {
      const payload = await client.quests()
      setProjects(sortProjects(payload))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t('loadProjectsFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadProjects()
  }, [])

  const pendingCount = useMemo(
    () => projects.reduce((total, item) => total + (item.pending_decisions?.length ?? item.counts?.pending_decision_count ?? 0), 0),
    [projects]
  )

  const createAndOpen = async (payload: {
    title: string
    goal: string
    quest_id?: string
    requested_baseline_ref?: { baseline_id: string; variant_id?: string | null } | null
    startup_contract?: Record<string, unknown> | null
  }) => {
    if (!payload.goal.trim()) {
      return
    }
    setCreating(true)
    try {
      const result = await client.createQuestWithOptions({
        goal: payload.goal.trim(),
        title: payload.title.trim() || undefined,
        quest_id: payload.quest_id?.trim() || undefined,
        requested_baseline_ref: payload.requested_baseline_ref ?? undefined,
        startup_contract: payload.startup_contract ?? undefined,
      })
      setCreateDialogOpen(false)
      navigate(`/projects/${result.snapshot.quest_id}`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t('createFailed'))
    } finally {
      setCreating(false)
    }
  }

  const deleteQuest = async (questId: string) => {
    if (!questId.trim()) return
    setDeleting(questId)
    try {
      await client.deleteQuest(questId)
      setProjects((current) => current.filter((item) => item.quest_id !== questId))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t('deleteFailed'))
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="font-project flex h-screen flex-col overflow-hidden px-4 pb-4 pt-4 sm:px-6 sm:pb-6">
      <ProjectsAppBar title={t('projectsTitle')} subtitle={t('sharedApiHint')} />

      <main className="mx-auto flex min-h-0 w-full max-w-[1520px] flex-1">
        <ProjectsHero
          projectCount={projects.length}
          pendingCount={pendingCount}
          loading={loading}
          creating={creating}
          error={error}
          onCreate={() => setCreateDialogOpen(true)}
          onOpen={() => setOpenDialogOpen(true)}
        />
      </main>

      <CreateProjectDialog
        open={createDialogOpen}
        loading={creating}
        error={error}
        onClose={() => setCreateDialogOpen(false)}
        onCreate={createAndOpen}
      />

      <OpenQuestDialog
        open={openDialogOpen}
        quests={projects}
        loading={loading}
        error={error}
        onClose={() => setOpenDialogOpen(false)}
        onOpenQuest={(questId) => navigate(`/projects/${questId}`)}
        onDeleteQuest={deleteQuest}
        deletingQuestId={deleting}
      />
    </div>
  )
}
