import React, { useEffect, useState } from 'react'
import {
  UserPlus,
  Users,
  Shield,
  Trash2,
  Copy,
  Check,
  Clock,
  X,
  Send,
  AlertCircle,
} from 'lucide-react'
import { CollaborationRole, WorkspaceInvite } from '../types/collaboration'
import { WorkspaceMember } from '../types/workspace'
import { collaborationApi } from '../services/collaborationApi'
import { workspaceApi } from '../services/workspaceApi'

interface WorkspaceMembersModalProps {
  workspaceId: string
  workspaceName: string
  isOpen: boolean
  onClose: () => void
}

export const WorkspaceMembersModal: React.FC<WorkspaceMembersModalProps> = ({
  workspaceId,
  workspaceName,
  isOpen,
  onClose,
}) => {
  const [members, setMembers] = useState<WorkspaceMember[]>([])
  const [invites, setInvites] = useState<WorkspaceInvite[]>([])
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<CollaborationRole>('researcher')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [copiedToken, setCopiedToken] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const loadData = async () => {
    if (!workspaceId) return
    setLoading(true)
    try {
      const [wsData, inviteList] = await Promise.all([
        workspaceApi.getWorkspace(workspaceId),
        collaborationApi.listWorkspaceInvites(workspaceId),
      ])
      setMembers(wsData.members || [])
      setInvites(inviteList || [])
    } catch (err: any) {
      console.error('Failed to load team data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadData()
      setStatusMessage(null)
    }
  }, [isOpen, workspaceId])

  if (!isOpen) return null

  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    setSubmitting(true)
    setStatusMessage(null)
    try {
      await collaborationApi.createInvite(workspaceId, {
        email: email.trim(),
        role,
      })
      setStatusMessage({ type: 'success', text: `Invitation generated for ${email.trim()}` })
      setEmail('')
      loadData()
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Failed to send invite'
      setStatusMessage({ type: 'error', text: errMsg })
    } finally {
      setSubmitting(false)
    }
  }

  const handleRevokeInvite = async (inviteId: string) => {
    try {
      await collaborationApi.revokeInvite(inviteId)
      setInvites(prev => prev.filter(inv => inv.id !== inviteId))
      setStatusMessage({ type: 'success', text: 'Invitation revoked' })
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: 'Failed to revoke invite' })
    }
  }

  const handleCopyLink = (token: string) => {
    const origin = window.location.origin
    const url = `${origin}/invites/${token}`
    navigator.clipboard.writeText(url)
    setCopiedToken(token)
    setTimeout(() => setCopiedToken(null), 2500)
  }

  const roleColors: Record<string, string> = {
    owner: '#a855f7',
    admin: '#3b82f6',
    researcher: '#10b981',
    analyst: '#f59e0b',
    reviewer: '#ec4899',
    viewer: '#6b7280',
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(5, 7, 15, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1.5rem',
    }}>
      <div style={{
        backgroundColor: '#0f172a',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '680px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#818cf8',
            }}>
              <Users size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                Team & Access Control
              </h2>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '2px 0 0 0' }}>
                {workspaceName}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '8px',
              display: 'flex',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status Notification */}
        {statusMessage && (
          <div style={{
            margin: '1rem 1.5rem 0',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: statusMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${statusMessage.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            color: statusMessage.type === 'success' ? '#34d399' : '#f87171',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}>
            <AlertCircle size={16} />
            <span>{statusMessage.text}</span>
          </div>
        )}

        {/* Scrollable Content */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Invite New Member Form */}
          <div style={{
            backgroundColor: 'rgba(30, 41, 59, 0.5)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: '12px',
            padding: '1.25rem',
          }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#e2e8f0', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UserPlus size={16} color="#818cf8" />
              Invite Team Member
            </h3>
            <form onSubmit={handleSendInvite} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <input
                type="email"
                placeholder="colleague@domain.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                style={{
                  flex: '1 1 240px',
                  backgroundColor: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '8px',
                  padding: '0.6rem 0.85rem',
                  color: '#f8fafc',
                  fontSize: '0.875rem',
                }}
              />
              <select
                value={role}
                onChange={e => setRole(e.target.value as CollaborationRole)}
                style={{
                  backgroundColor: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '8px',
                  padding: '0.6rem 0.85rem',
                  color: '#f8fafc',
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                }}
              >
                <option value="researcher">Researcher</option>
                <option value="analyst">Analyst</option>
                <option value="reviewer">Reviewer</option>
                <option value="admin">Admin</option>
                <option value="viewer">Viewer</option>
              </select>
              <button
                type="submit"
                disabled={submitting || !email.trim()}
                style={{
                  backgroundColor: '#4f46e5',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.6rem 1.25rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  opacity: submitting ? 0.7 : 1,
                }}
              >
                <Send size={15} />
                {submitting ? 'Inviting...' : 'Send Invite'}
              </button>
            </form>
          </div>

          {/* Current Workspace Members */}
          <div>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#cbd5e1', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={16} color="#38bdf8" />
              Active Members ({members.length})
            </h3>
            {loading ? (
              <div style={{ color: '#64748b', fontSize: '0.85rem', padding: '1rem 0' }}>Loading team members...</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {members.map(member => (
                  <div
                    key={member.id}
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.3)',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                      borderRadius: '10px',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 600,
                        fontSize: '0.85rem',
                        color: '#f8fafc',
                      }}>
                        {member.user_id.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: '#f1f5f9', fontWeight: 500 }}>
                          User ({member.user_id.slice(0, 8)}...)
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          Joined {new Date(member.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '6px',
                    backgroundColor: `${roleColors[member.role] || '#6b7280'}20`,
                    color: roleColors[member.role] || '#9ca3af',
                    border: `1px solid ${roleColors[member.role] || '#6b7280'}40`,
                  }}>
                    {member.role}
                  </span>
                </div>
              ))}
            </div>
            )}
          </div>

          {/* Pending Invites */}
          {invites.length > 0 && (
            <div>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#cbd5e1', margin: '0 0 0.75rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock size={16} color="#fbbf24" />
                Pending Invitations ({invites.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {invites.map(inv => (
                  <div
                    key={inv.id}
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.3)',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                      borderRadius: '10px',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '0.75rem',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.875rem', color: '#f8fafc', fontWeight: 500 }}>
                        {inv.email}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        Role: <span style={{ color: roleColors[inv.role] || '#cbd5e1', fontWeight: 500 }}>{inv.role}</span> &bull; Sent {new Date(inv.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <button
                        onClick={() => handleCopyLink(inv.token)}
                        title="Copy Invitation Link"
                        style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.06)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '6px',
                          color: copiedToken === inv.token ? '#10b981' : '#cbd5e1',
                          padding: '0.4rem 0.6rem',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                        }}
                      >
                        {copiedToken === inv.token ? <Check size={14} /> : <Copy size={14} />}
                        {copiedToken === inv.token ? 'Copied' : 'Link'}
                      </button>
                      <button
                        onClick={() => handleRevokeInvite(inv.id)}
                        title="Revoke Invite"
                        style={{
                          backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.2)',
                          borderRadius: '6px',
                          color: '#f87171',
                          padding: '0.4rem 0.6rem',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
