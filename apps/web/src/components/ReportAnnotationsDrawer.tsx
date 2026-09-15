import React, { useEffect, useState } from 'react'
import {
  MessageSquare,
  CheckCircle2,
  Trash2,
  Send,
  Check,
  X,
} from 'lucide-react'
import { ReportAnnotation } from '../types/collaboration'
import { collaborationApi } from '../services/collaborationApi'

interface ReportAnnotationsDrawerProps {
  reportId: string
  isOpen: boolean
  onClose: () => void
  onAnnotationCountChange?: (count: number) => void
}

export const ReportAnnotationsDrawer: React.FC<ReportAnnotationsDrawerProps> = ({
  reportId,
  isOpen,
  onClose,
  onAnnotationCountChange,
}) => {
  const [annotations, setAnnotations] = useState<ReportAnnotation[]>([])
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'resolved'>('all')
  const [commentText, setCommentText] = useState('')
  const [selectedText, setSelectedText] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const loadAnnotations = async () => {
    if (!reportId) return
    setLoading(true)
    try {
      const data = await collaborationApi.listAnnotations(
        reportId,
        statusFilter === 'all' ? undefined : statusFilter
      )
      setAnnotations(data)
      if (onAnnotationCountChange) {
        onAnnotationCountChange(data.filter(a => a.status === 'open').length)
      }
    } catch (err) {
      console.error('Failed to load annotations:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadAnnotations()
    }
  }, [isOpen, reportId, statusFilter])

  if (!isOpen) return null

  const handleAddAnnotation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentText.trim()) return
    setSubmitting(true)
    try {
      await collaborationApi.createAnnotation(reportId, {
        comment_text: commentText.trim(),
        selected_text: selectedText.trim() || undefined,
      })
      setCommentText('')
      setSelectedText('')
      loadAnnotations()
    } catch (err) {
      console.error('Failed to create annotation:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleResolve = async (id: string) => {
    try {
      await collaborationApi.resolveAnnotation(id)
      loadAnnotations()
    } catch (err) {
      console.error('Failed to resolve annotation:', err)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await collaborationApi.deleteAnnotation(id)
      setAnnotations(prev => prev.filter(a => a.id !== id))
    } catch (err) {
      console.error('Failed to delete annotation:', err)
    }
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '100%',
      maxWidth: '420px',
      backgroundColor: '#0f172a',
      borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.5)',
      zIndex: 900,
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{
        padding: '1.25rem 1.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <MessageSquare size={18} color="#818cf8" />
          <h2 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
            Report Review Comments
          </h2>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#64748b',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '6px',
            display: 'flex',
          }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{
        display: 'flex',
        padding: '0.75rem 1.25rem',
        gap: '0.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        backgroundColor: 'rgba(15, 23, 42, 0.4)',
      }}>
        {(['all', 'open', 'resolved'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setStatusFilter(tab)}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              fontSize: '0.8rem',
              fontWeight: 500,
              textTransform: 'capitalize',
              cursor: 'pointer',
              backgroundColor: statusFilter === tab ? '#3730a3' : 'rgba(255, 255, 255, 0.04)',
              color: statusFilter === tab ? '#e0e7ff' : '#94a3b8',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Annotations List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {loading ? (
          <div style={{ color: '#64748b', fontSize: '0.85rem', textAlign: 'center', padding: '2rem 0' }}>
            Loading comments...
          </div>
        ) : annotations.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.85rem', textAlign: 'center', padding: '2rem 0' }}>
            No comments found for this report.
          </div>
        ) : (
          annotations.map(ann => (
            <div
              key={ann.id}
              style={{
                backgroundColor: ann.status === 'resolved' ? 'rgba(30, 41, 59, 0.3)' : 'rgba(30, 41, 59, 0.65)',
                border: `1px solid ${ann.status === 'resolved' ? 'rgba(255, 255, 255, 0.04)' : 'rgba(99, 102, 241, 0.25)'}`,
                borderRadius: '10px',
                padding: '0.85rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
                opacity: ann.status === 'resolved' ? 0.75 : 1,
              }}
            >
              {/* Top Row */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f1f5f9' }}>
                  {ann.author_username || `User (${ann.user_id.slice(0, 6)}...)`}
                </span>
                <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                  {new Date(ann.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Quoted Snippet if present */}
              {ann.selected_text && (
                <div style={{
                  fontSize: '0.75rem',
                  fontStyle: 'italic',
                  color: '#94a3b8',
                  borderLeft: '2px solid #6366f1',
                  paddingLeft: '0.5rem',
                  margin: '0.2rem 0',
                }}>
                  "{ann.selected_text}"
                </div>
              )}

              {/* Comment Body */}
              <p style={{ fontSize: '0.85rem', color: '#e2e8f0', margin: 0, lineHeight: 1.45 }}>
                {ann.comment_text}
              </p>

              {/* Action Buttons */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '0.4rem',
                borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                marginTop: '0.25rem',
              }}>
                {ann.status === 'open' ? (
                  <button
                    onClick={() => handleResolve(ann.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#10b981',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      padding: '2px 0',
                    }}
                  >
                    <CheckCircle2 size={13} />
                    Resolve
                  </button>
                ) : (
                  <span style={{ fontSize: '0.72rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Check size={12} /> Resolved
                  </span>
                )}
                <button
                  onClick={() => handleDelete(ann.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ef4444',
                    cursor: 'pointer',
                    padding: '2px',
                    opacity: 0.7,
                  }}
                  title="Delete comment"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* New Comment Input Box */}
      <form
        onSubmit={handleAddAnnotation}
        style={{
          padding: '1rem 1.25rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.6rem',
        }}
      >
        <textarea
          placeholder="Leave an inline review note or recommendation..."
          value={commentText}
          onChange={e => setCommentText(e.target.value)}
          rows={3}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.5)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
            padding: '0.6rem 0.75rem',
            color: '#f8fafc',
            fontSize: '0.85rem',
            resize: 'none',
          }}
        />
        <button
          type="submit"
          disabled={submitting || !commentText.trim()}
          style={{
            alignSelf: 'flex-end',
            backgroundColor: '#4f46e5',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            padding: '0.45rem 1rem',
            fontSize: '0.8rem',
            fontWeight: 500,
            cursor: submitting || !commentText.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            opacity: submitting || !commentText.trim() ? 0.6 : 1,
          }}
        >
          <Send size={13} />
          {submitting ? 'Posting...' : 'Comment'}
        </button>
      </form>
    </div>
  )
}
