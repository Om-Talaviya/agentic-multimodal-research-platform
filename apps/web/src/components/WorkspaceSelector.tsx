import React, { useState } from 'react'
import { Building2, ChevronDown, FolderKanban, Plus, Check } from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'

export const WorkspaceSelector: React.FC = () => {
  const {
    workspaces,
    currentWorkspace,
    projects,
    currentProject,
    setCurrentWorkspace,
    setCurrentProject,
    createProject,
    createWorkspace,
  } = useWorkspace()

  const [isOpen, setIsOpen] = useState(false)
  const [showNewProjModal, setShowNewProjModal] = useState(false)
  const [showNewWsModal, setShowNewWsModal] = useState(false)
  const [newProjName, setNewProjName] = useState('')
  const [newProjDesc, setNewProjDesc] = useState('')
  const [newWsName, setNewWsName] = useState('')

  const handleCreateProj = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProjName.trim()) return
    await createProject(newProjName.trim(), newProjDesc.trim() || undefined)
    setNewProjName('')
    setNewProjDesc('')
    setShowNewProjModal(false)
    setIsOpen(false)
  }

  const handleCreateWs = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newWsName.trim()) return
    await createWorkspace(newWsName.trim())
    setNewWsName('')
    setShowNewWsModal(false)
    setIsOpen(false)
  }

  return (
    <div style={{ position: 'relative', marginBottom: 'var(--spacing-md)' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--spacing-sm) var(--spacing-md)',
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-text)',
          cursor: 'pointer',
          textAlign: 'left',
          fontSize: '0.875rem',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
            <Building2 size={14} color="var(--color-primary)" />
            <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
              {currentWorkspace?.name || 'Select Workspace'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            <FolderKanban size={12} />
            <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
              {currentProject?.name || 'Select Project'}
            </span>
          </div>
        </div>
        <ChevronDown size={14} style={{ opacity: 0.7 }} />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '105%',
            left: 0,
            right: 0,
            zIndex: 100,
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
            padding: 'var(--spacing-xs)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          {/* Workspaces Section */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--color-text-muted)', fontWeight: 600 }}>
              <span>Workspaces</span>
              <button
                onClick={() => setShowNewWsModal(true)}
                style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '2px', fontSize: '0.7rem' }}
              >
                <Plus size={10} /> New
              </button>
            </div>
            {workspaces.map(ws => (
              <div
                key={ws.id}
                onClick={() => {
                  setCurrentWorkspace(ws)
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '6px 8px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  background: currentWorkspace?.id === ws.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                  color: currentWorkspace?.id === ws.id ? 'var(--color-primary)' : 'var(--color-text)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Building2 size={12} />
                  <span>{ws.name}</span>
                </div>
                {currentWorkspace?.id === ws.id && <Check size={12} />}
              </div>
            ))}
          </div>

          <div style={{ height: '1px', background: 'var(--color-border)' }} />

          {/* Projects Section */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--color-text-muted)', fontWeight: 600 }}>
              <span>Projects</span>
              <button
                onClick={() => setShowNewProjModal(true)}
                style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '2px', fontSize: '0.7rem' }}
              >
                <Plus size={10} /> New
              </button>
            </div>
            {projects.length === 0 ? (
              <div style={{ padding: '6px 8px', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                No projects yet
              </div>
            ) : (
              projects.map(proj => (
                <div
                  key={proj.id}
                  onClick={() => {
                    setCurrentProject(proj)
                    setIsOpen(false)
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '6px 8px',
                    borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    background: currentProject?.id === proj.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    color: currentProject?.id === proj.id ? 'var(--color-primary)' : 'var(--color-text)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <FolderKanban size={12} />
                    <span>{proj.name}</span>
                  </div>
                  {currentProject?.id === proj.id && <Check size={12} />}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* New Project Modal */}
      {showNewProjModal && (
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
              padding: 'var(--spacing-lg)',
              width: '380px',
            }}
          >
            <h3 style={{ margin: '0 0 var(--spacing-sm) 0', fontSize: '1.1rem' }}>Create New Project</h3>
            <form onSubmit={handleCreateProj} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '4px' }}>Project Name</label>
                <input
                  type="text"
                  value={newProjName}
                  onChange={e => setNewProjName(e.target.value)}
                  placeholder="e.g. CRISPR Therapeutics"
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '4px' }}>Description (optional)</label>
                <textarea
                  value={newProjDesc}
                  onChange={e => setNewProjDesc(e.target.value)}
                  placeholder="Goals and objectives of this research project..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                    resize: 'vertical',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowNewProjModal(false)}
                  style={{
                    padding: '6px 12px',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '6px 14px',
                    background: 'var(--color-primary)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Workspace Modal */}
      {showNewWsModal && (
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
              padding: 'var(--spacing-lg)',
              width: '380px',
            }}
          >
            <h3 style={{ margin: '0 0 var(--spacing-sm) 0', fontSize: '1.1rem' }}>Create New Workspace</h3>
            <form onSubmit={handleCreateWs} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '4px' }}>Workspace Name</label>
                <input
                  type="text"
                  value={newWsName}
                  onChange={e => setNewWsName(e.target.value)}
                  placeholder="e.g. BioTech Research Labs"
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowNewWsModal(false)}
                  style={{
                    padding: '6px 12px',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--color-text)',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '6px 14px',
                    background: 'var(--color-primary)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    color: '#fff',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
