import React, { useEffect, useState } from 'react'
import {
  FolderKanban,
  Plus,
  Search,
  FlaskConical,
  FileText,
  Brain,
  Share2,
  CheckCircle2,
  Trash2,
  Archive,
  RefreshCw,
  Users,
} from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'
import { workspaceApi } from '../services/workspaceApi'
import { Project, ProjectMetrics } from '../types/workspace'
import { WorkspaceMembersModal } from '../components/WorkspaceMembersModal'

export const ProjectsPage: React.FC = () => {
  const { currentWorkspace, currentProject, setCurrentProject, projects, refreshProjects, createProject } = useWorkspace()

  const [projectMetrics, setProjectMetrics] = useState<Record<string, ProjectMetrics>>({})
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const loadMetrics = async (projList: Project[]) => {
    const metricsMap: Record<string, ProjectMetrics> = {}
    for (const p of projList) {
      try {
        const overview = await workspaceApi.getProjectOverview(p.id)
        if (overview.metrics) {
          metricsMap[p.id] = overview.metrics
        }
      } catch (e) {
        console.error(`Failed to load metrics for project ${p.id}:`, e)
      }
    }
    setProjectMetrics(metricsMap)
  }

  useEffect(() => {
    if (projects.length > 0) {
      loadMetrics(projects)
    }
  }, [projects])

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !currentWorkspace) return

    setIsLoading(true)
    try {
      await createProject(name.trim(), description.trim() || undefined)
      setName('')
      setDescription('')
      setIsModalOpen(false)
    } catch (err) {
      console.error('Failed to create project:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleArchiveProject = async (proj: Project) => {
    const newStatus = proj.status === 'active' ? 'archived' : 'active'
    try {
      await workspaceApi.updateProject(proj.id, { status: newStatus })
      await refreshProjects()
    } catch (err) {
      console.error('Failed to update project status:', err)
    }
  }

  const handleDeleteProject = async (projId: string) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return
    try {
      await workspaceApi.deleteProject(projId)
      await refreshProjects()
    } catch (err) {
      console.error('Failed to delete project:', err)
    }
  }

  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) || (p.description || '').toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || p.status === filterStatus
    return matchesSearch && matchesStatus
  })

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: '4px' }}>
            <FolderKanban size={24} color="var(--color-primary)" />
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700 }}>Workspace Projects</h1>
          </div>
          <p style={{ margin: 0, color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            Manage research projects, multimodal documents, and knowledge assets in <strong>{currentWorkspace?.name || 'Workspace'}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => setIsTeamModalOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 16px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text)',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <Users size={16} color="var(--color-primary)" />
            Team & Access
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 18px',
              background: 'var(--color-primary)',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <Plus size={16} />
            New Project
          </button>
        </div>
      </div>

      {/* Controls: Search & Filters */}
      <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }} />
          <input
            type="text"
            placeholder="Search projects by name or description..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px 10px 38px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text)',
            }}
          />
        </div>

        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text)',
            cursor: 'pointer',
          }}
        >
          <option value="all">All Statuses</option>
          <option value="active">Active Only</option>
          <option value="archived">Archived Only</option>
        </select>

        <button
          onClick={() => refreshProjects()}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '10px 14px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-text)',
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Projects Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--spacing-lg)' }}>
        {filteredProjects.map(proj => {
          const isSelected = currentProject?.id === proj.id
          const metrics = projectMetrics[proj.id] || { total_jobs: 0, total_documents: 0, total_memories: 0, total_graph_entities: 0 }

          return (
            <div
              key={proj.id}
              style={{
                background: 'var(--color-surface)',
                border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--spacing-lg)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-md)',
                position: 'relative',
                boxShadow: isSelected ? '0 0 16px rgba(99, 102, 241, 0.2)' : 'none',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>{proj.name}</h3>
                    {isSelected && (
                      <span
                        style={{
                          fontSize: '0.65rem',
                          background: 'rgba(99, 102, 241, 0.2)',
                          color: 'var(--color-primary)',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                        }}
                      >
                        Active
                      </span>
                    )}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>slug: {proj.slug}</span>
                </div>

                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontWeight: 600,
                    textTransform: 'capitalize',
                    background: proj.status === 'active' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(234, 179, 8, 0.15)',
                    color: proj.status === 'active' ? '#22c55e' : '#eab308',
                  }}
                >
                  {proj.status}
                </span>
              </div>

              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-text-muted)', minHeight: '36px' }}>
                {proj.description || 'No description provided.'}
              </p>

              {/* Metrics Pills */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', background: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}>
                  <FlaskConical size={14} color="#6366f1" />
                  <span><strong>{metrics.total_jobs}</strong> Research Jobs</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}>
                  <FileText size={14} color="#10b981" />
                  <span><strong>{metrics.total_documents}</strong> Documents</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}>
                  <Brain size={14} color="#ec4899" />
                  <span><strong>{metrics.total_memories}</strong> Memories</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}>
                  <Share2 size={14} color="#f59e0b" />
                  <span><strong>{metrics.total_graph_entities}</strong> Graph Nodes</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: 'var(--spacing-sm)', borderTop: '1px solid var(--color-border)' }}>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button
                    onClick={() => handleArchiveProject(proj)}
                    title={proj.status === 'active' ? 'Archive Project' : 'Activate Project'}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-text-muted)',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                  >
                    <Archive size={16} />
                  </button>
                  <button
                    onClick={() => handleDeleteProject(proj.id)}
                    title="Delete Project"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                <button
                  onClick={() => setCurrentProject(proj)}
                  disabled={isSelected}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    color: isSelected ? 'var(--color-primary)' : 'var(--color-text)',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    cursor: isSelected ? 'default' : 'pointer',
                  }}
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 size={14} /> Selected
                    </>
                  ) : (
                    'Switch to Project'
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* New Project Modal */}
      {isModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--spacing-xl)',
              width: '440px',
              boxShadow: '0 12px 36px rgba(0,0,0,0.5)',
            }}
          >
            <h2 style={{ margin: '0 0 var(--spacing-md) 0', fontSize: '1.25rem' }}>Create New Project</h2>
            <form onSubmit={handleCreateProject} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', fontWeight: 600 }}>
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. mRNA Vaccine Delivery"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', fontWeight: 600 }}>
                  Description (optional)
                </label>
                <textarea
                  rows={3}
                  placeholder="Research goals, target questions, and scope..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  style={{
                    padding: '8px 16px',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  style={{
                    padding: '8px 18px',
                    background: 'var(--color-primary)',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {isLoading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {currentWorkspace && (
        <WorkspaceMembersModal
          workspaceId={currentWorkspace.id}
          workspaceName={currentWorkspace.name}
          isOpen={isTeamModalOpen}
          onClose={() => setIsTeamModalOpen(false)}
        />
      )}
    </div>
  )
}
