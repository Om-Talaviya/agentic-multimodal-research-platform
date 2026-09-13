import { useState } from 'react'
import {
  RotateCcw,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Search,
  Zap,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Flame,
} from 'lucide-react'
import type { ResearchIteration, DeepResearchConfig } from '../types/research'

interface DeepResearchTrackerProps {
  iterations?: ResearchIteration[]
  config?: DeepResearchConfig | null
  currentConfidence?: number
  isDeepResearchActive?: boolean
}

export function DeepResearchTracker({
  iterations = [],
  config: _config,
  currentConfidence = 0.85,
  isDeepResearchActive: _isDeepResearchActive = false,
}: DeepResearchTrackerProps) {
  const [selectedIteration, setSelectedIteration] = useState<number>(
    iterations.length > 0 ? iterations.length - 1 : 0
  )
  const [isDetailsExpanded, setIsDetailsExpanded] = useState<boolean>(true)

  if (!iterations || iterations.length === 0) {
    return null
  }

  const activeIter = iterations[selectedIteration] || iterations[iterations.length - 1]
  const latestIter = iterations[iterations.length - 1]
  const convergenceReason = latestIter?.convergence_reason || 'In Progress'

  const getReasonBadge = (reason: string) => {
    switch (reason) {
      case 'confidence_threshold_met':
      case 'initial_threshold_met':
        return { label: 'Target Met (Converged)', bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }
      case 'max_iterations_reached':
        return { label: 'Max Rounds Reached', bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }
      case 'diminishing_returns':
        return { label: 'Diminishing Returns (Converged)', bg: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }
      case 'no_further_actionable_subtasks':
        return { label: 'All Gaps Resolved', bg: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6' }
      default:
        return { label: 'Active Investigation', bg: 'rgba(99, 102, 241, 0.15)', color: '#6366f1' }
    }
  }

  const reasonBadge = getReasonBadge(convergenceReason)

  return (
    <div
      style={{
        background: 'linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.75))',
        borderRadius: '1rem',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        backdropFilter: 'blur(12px)',
        padding: '1.5rem',
        marginBottom: '1.5rem',
        color: '#f8fafc',
      }}
    >
      {/* Header Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          paddingBottom: '1rem',
          marginBottom: '1.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              padding: '0.6rem',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)',
            }}
          >
            <RotateCcw size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
                Autonomous Deep Research Engine
              </h3>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '9999px',
                  background: reasonBadge.bg,
                  color: reasonBadge.color,
                  fontWeight: 600,
                  border: `1px solid ${reasonBadge.color}40`,
                }}
              >
                {reasonBadge.label}
              </span>
            </div>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>
              Recursive Multi-Round Hypothesis Loop & Convergence Tracking (Gen 3)
            </p>
          </div>
        </div>

        {/* Global Convergence Metrics */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Confidence Score
            </div>
            <div
              style={{
                fontSize: '1.4rem',
                fontWeight: 800,
                color: (activeIter?.confidence_score ?? currentConfidence) >= 0.85 ? '#10b981' : '#f59e0b',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                gap: '0.35rem',
              }}
            >
              <TrendingUp size={18} />
              {((activeIter?.confidence_score ?? currentConfidence) * 100).toFixed(1)}%
            </div>
          </div>

          <button
            onClick={() => setIsDetailsExpanded(!isDetailsExpanded)}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#e2e8f0',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.85rem',
              transition: 'all 0.2s ease',
            }}
          >
            {isDetailsExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            {isDetailsExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {/* Iteration Stepper Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          overflowX: 'auto',
          paddingBottom: '0.75rem',
          marginBottom: '1.25rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        {iterations.map((iter, idx) => {
          const isSelected = selectedIteration === idx
          const delta = iter.confidence_delta
          return (
            <button
              key={idx}
              onClick={() => setSelectedIteration(idx)}
              style={{
                flex: '0 0 auto',
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.25))'
                  : 'rgba(30, 41, 59, 0.6)',
                border: isSelected
                  ? '1px solid #6366f1'
                  : '1px solid rgba(255, 255, 255, 0.08)',
                padding: '0.6rem 1rem',
                borderRadius: '0.75rem',
                color: isSelected ? '#ffffff' : '#94a3b8',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                transition: 'all 0.2s ease',
                boxShadow: isSelected ? '0 0 12px rgba(99, 102, 241, 0.25)' : 'none',
              }}
            >
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: isSelected ? '#6366f1' : 'rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  color: '#ffffff',
                }}
              >
                R{iter.iteration_index}
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                  Iteration #{iter.iteration_index}
                </div>
                <div style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span>{(iter.confidence_score * 100).toFixed(0)}% conf</span>
                  {delta !== 0 && (
                    <span style={{ color: delta > 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                      {delta > 0 ? `+${(delta * 100).toFixed(0)}%` : `${(delta * 100).toFixed(0)}%`}
                    </span>
                  )}
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Expanded Iteration Details */}
      {isDetailsExpanded && activeIter && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {/* Formulated Hypotheses */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              padding: '1.25rem',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
              <Sparkles size={18} color="#8b5cf6" />
              <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Formulated Hypotheses ({activeIter.hypotheses.length})
              </h4>
            </div>

            {activeIter.hypotheses.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {activeIter.hypotheses.map((hyp, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'rgba(139, 92, 246, 0.08)',
                      border: '1px solid rgba(139, 92, 246, 0.2)',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      fontSize: '0.85rem',
                      lineHeight: '1.4',
                      color: '#e2e8f0',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.5rem',
                    }}
                  >
                    <Flame size={16} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{hyp}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic', margin: 0 }}>
                No active hypotheses required for this iteration.
              </p>
            )}
          </div>

          {/* Unresolved Gaps & Targeted Gap Queries */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              padding: '1.25rem',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
              <Search size={18} color="#38bdf8" />
              <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Critic Gaps & Deep Queries ({activeIter.gap_queries.length || activeIter.unresolved_gaps.length})
              </h4>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {activeIter.unresolved_gaps.map((gap, i) => (
                <div
                  key={`gap-${i}`}
                  style={{
                    background: 'rgba(239, 68, 68, 0.08)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    padding: '0.6rem 0.75rem',
                    borderRadius: '0.5rem',
                    fontSize: '0.82rem',
                    color: '#fca5a5',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                  }}
                >
                  <AlertTriangle size={14} color="#ef4444" style={{ flexShrink: 0 }} />
                  <span>Gap: {gap}</span>
                </div>
              ))}

              {activeIter.gap_queries.map((query, i) => (
                <div
                  key={`query-${i}`}
                  style={{
                    background: 'rgba(56, 189, 248, 0.08)',
                    border: '1px solid rgba(56, 189, 248, 0.2)',
                    padding: '0.6rem 0.75rem',
                    borderRadius: '0.5rem',
                    fontSize: '0.82rem',
                    color: '#7dd3fc',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                  }}
                >
                  <Zap size={14} color="#38bdf8" style={{ flexShrink: 0 }} />
                  <span>Query: {query}</span>
                </div>
              ))}

              {activeIter.unresolved_gaps.length === 0 && activeIter.gap_queries.length === 0 && (
                <p style={{ fontSize: '0.85rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.4rem', margin: 0 }}>
                  <ShieldCheck size={16} />
                  Zero evidentiary gaps or contradictions detected.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
