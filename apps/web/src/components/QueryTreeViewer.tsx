import React, { useState } from 'react'
import { GitBranch, Compass, Target, Clock, Globe, ShieldAlert, Sparkles, ChevronRight, ChevronDown, CheckCircle, Loader2 } from 'lucide-react'
import type { QueryTreeNode, InferredScope, ResearchTask } from '../types/research'

interface QueryTreeViewerProps {
  queryTree?: QueryTreeNode | null
  ambiguityScore?: number
  inferredScope?: InferredScope | null
  planExplanation?: string
  replanCount?: number
  tasks?: ResearchTask[]
}

export function QueryTreeViewer({
  queryTree,
  ambiguityScore = 0,
  inferredScope,
  planExplanation,
  replanCount = 0,
  tasks = [],
}: QueryTreeViewerProps) {
  const [collapsedNodes, setCollapsedNodes] = useState<Record<string, boolean>>({})

  const toggleCollapse = (nodeId: string) => {
    setCollapsedNodes(prev => ({ ...prev, [nodeId]: !prev[nodeId] }))
  }

  // Calculate ambiguity rating
  const getAmbiguityMeta = (score: number) => {
    if (score <= 0.2) return { label: 'Crystal Clear', color: 'var(--accent-emerald, #10b981)', badge: 'badge-completed' }
    if (score <= 0.5) return { label: 'Moderately Specified', color: 'var(--accent-blue, #38bdf8)', badge: 'badge-running' }
    if (score <= 0.75) return { label: 'Broad / Ambiguous', color: 'var(--accent-amber, #f59e0b)', badge: 'badge-pending' }
    return { label: 'Highly Underspecified', color: 'var(--accent-rose, #ef4444)', badge: 'badge-failed' }
  }

  const ambMeta = getAmbiguityMeta(ambiguityScore)

  const renderTreeNode = (node: QueryTreeNode, isRoot: boolean = false) => {
    const isCollapsed = collapsedNodes[node.id] || false
    const hasChildren = node.subqueries && node.subqueries.length > 0
    const nodeTasks = tasks.filter(t => t.parent_task_id === node.id || t.objective.toLowerCase().includes(node.question.toLowerCase()))

    return (
      <div
        key={node.id}
        style={{
          marginLeft: isRoot ? '0' : '1.5rem',
          paddingLeft: isRoot ? '0' : '1rem',
          borderLeft: isRoot ? 'none' : '2px dashed var(--border-subtle, rgba(255, 255, 255, 0.1))',
          marginBottom: '1rem',
          position: 'relative',
        }}
      >
        <div
          style={{
            background: isRoot
              ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(129, 140, 248, 0.05) 100%)'
              : 'var(--bg-card, rgba(17, 24, 39, 0.7))',
            border: isRoot
              ? '1px solid var(--accent-blue, #38bdf8)'
              : '1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))',
            borderRadius: 'var(--radius-md, 8px)',
            padding: '1rem',
            boxShadow: 'var(--shadow-card, 0 4px 12px rgba(0,0,0,0.3))',
            transition: 'border-color 0.2s',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1 }}>
              {hasChildren ? (
                <button
                  onClick={() => toggleCollapse(node.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--color-text-muted, #94a3b8)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    padding: 0,
                  }}
                  title={isCollapsed ? 'Expand branch' : 'Collapse branch'}
                >
                  {isCollapsed ? <ChevronRight size={18} /> : <ChevronDown size={18} />}
                </button>
              ) : (
                <div style={{ width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-blue, #38bdf8)' }} />
                </div>
              )}

              <h4 style={{ margin: 0, fontSize: isRoot ? '1.1rem' : '0.95rem', fontWeight: 600, color: 'var(--color-text, #f8fafc)' }}>
                {node.question}
              </h4>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {node.domain_focus && (
                <span
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    background: 'rgba(56, 189, 248, 0.15)',
                    color: '#38bdf8',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {node.domain_focus}
                </span>
              )}
              {node.assigned_agent && (
                <span
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    background: 'rgba(129, 140, 248, 0.15)',
                    color: '#818cf8',
                    fontFamily: 'monospace',
                  }}
                >
                  @{node.assigned_agent}
                </span>
              )}
            </div>
          </div>

          {node.rationale && (
            <p style={{ margin: '0.5rem 0 0 1.6rem', fontSize: '0.85rem', color: 'var(--color-text-muted, #94a3b8)' }}>
              {node.rationale}
            </p>
          )}

          {nodeTasks.length > 0 && (
            <div style={{ marginTop: '0.75rem', marginLeft: '1.6rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {nodeTasks.map(t => (
                <div
                  key={t.id}
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.25rem 0.6rem',
                    borderRadius: '4px',
                    background: t.is_dynamic ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    border: t.is_dynamic ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                  }}
                >
                  {t.status === 'completed' ? (
                    <CheckCircle size={12} color="#10b981" />
                  ) : t.status === 'running' ? (
                    <Loader2 size={12} className="animate-spin" color="#38bdf8" />
                  ) : null}
                  <span>{t.is_dynamic ? '⚡ Dynamic Task: ' : 'Task: '}{t.agent}</span>
                  <span style={{ opacity: 0.6 }}>({t.status})</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {hasChildren && !isCollapsed && (
          <div style={{ marginTop: '0.75rem' }}>
            {node.subqueries!.map(child => renderTreeNode(child, false))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Strategic Header Panel */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          background: 'var(--bg-secondary, #111827)',
          padding: '1.25rem',
          borderRadius: 'var(--radius-lg, 12px)',
          border: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-text-muted, #94a3b8)', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
            <Compass size={16} color="var(--accent-blue, #38bdf8)" /> Ambiguity Score
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: ambMeta.color }}>
              {(ambiguityScore * 100).toFixed(0)}%
            </span>
            <span className={`badge ${ambMeta.badge}`} style={{ fontSize: '0.75rem' }}>
              {ambMeta.label}
            </span>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-text-muted, #94a3b8)', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
            <Target size={16} color="var(--accent-emerald, #10b981)" /> Identified Domain
          </div>
          <p style={{ margin: 0, fontWeight: 600, fontSize: '1.05rem', textTransform: 'capitalize' }}>
            {inferredScope?.domain || 'General Research'}
          </p>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-text-muted, #94a3b8)', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
            <Clock size={16} color="var(--accent-amber, #f59e0b)" /> Time Horizon & Geography
          </div>
          <p style={{ margin: 0, fontWeight: 500, fontSize: '0.9rem', color: 'var(--color-text, #f8fafc)' }}>
            {inferredScope?.time_horizon || 'Immediate / Current'} • {inferredScope?.geography || 'Global'}
          </p>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-text-muted, #94a3b8)', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
            <Sparkles size={16} color="var(--accent-purple, #818cf8)" /> Dynamic Replanning Iterations
          </div>
          <p style={{ margin: 0, fontWeight: 600, fontSize: '1.05rem' }}>
            {replanCount > 0 ? `${replanCount} Replan Triggered` : 'Zero Gaps (Original Plan)'}
          </p>
        </div>
      </div>

      {planExplanation && (
        <div
          style={{
            padding: '1rem',
            background: 'rgba(56, 189, 248, 0.05)',
            borderLeft: '3px solid var(--accent-blue, #38bdf8)',
            borderRadius: '4px',
            fontSize: '0.9rem',
            color: 'var(--color-text, #f8fafc)',
          }}
        >
          <strong>Strategic Strategy: </strong>{planExplanation}
        </div>
      )}

      {/* Query Tree Visualization */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <GitBranch size={20} color="var(--accent-blue, #38bdf8)" />
          <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>Hierarchical Query Tree & Sub-Questions</h3>
        </div>

        {queryTree ? (
          <div style={{ padding: '0.5rem 0' }}>
            {renderTreeNode(queryTree, true)}
          </div>
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted, #94a3b8)', background: 'var(--bg-card)', borderRadius: '8px' }}>
            Query tree will be generated as planning executes.
          </div>
        )}
      </div>
    </div>
  )
}
