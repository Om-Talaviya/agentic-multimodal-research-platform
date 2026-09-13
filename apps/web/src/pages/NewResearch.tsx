import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Loader2,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  Scale,
  Zap,
  Coins,
  Sparkles,
  Cpu,
  Info,
} from 'lucide-react'
import { api } from '../services/api'
import { OptimizationResult, ProfileType } from '../types/models'
import { clsx } from 'clsx'

const PROFILES: Array<{
  id: ProfileType
  name: string
  icon: typeof Scale
  desc: string
  color: string
}> = [
  {
    id: 'balanced',
    name: 'Balanced',
    icon: Scale,
    desc: 'Optimal trade-off between quality, speed, and cost',
    color: 'var(--color-primary, #6366f1)',
  },
  {
    id: 'quality_maximized',
    name: 'Deep Quality',
    icon: Sparkles,
    desc: 'Frontier reasoning and comprehensive multi-step synthesis',
    color: '#a855f7',
  },
  {
    id: 'speed_maximized',
    name: 'Ultra Fast',
    icon: Zap,
    desc: 'Low-latency streaming & lightweight local inference',
    color: '#eab308',
  },
  {
    id: 'cost_minimized',
    name: 'Cost Efficient',
    icon: Coins,
    desc: 'Budget-first routing prioritizing free & low-cost models',
    color: '#22c55e',
  },
]

export function NewResearch() {
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [context, setContext] = useState('')
  const [constraints, setConstraints] = useState('')
  const [routingProfile, setRoutingProfile] = useState<ProfileType>('balanced')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [simResult, setSimResult] = useState<OptimizationResult | null>(null)
  const [loadingSim, setLoadingSim] = useState(false)

  useEffect(() => {
    let isCancelled = false
    const fetchSimulation = async () => {
      setLoadingSim(true)
      try {
        const res = await api.post('/models/optimize', {
          profile: routingProfile,
          task: 'long_form_research',
        })
        if (!isCancelled) {
          setSimResult(res.data)
        }
      } catch (err) {
        // simulation is advisory, silently catch
      } finally {
        if (!isCancelled) setLoadingSim(false)
      }
    }

    fetchSimulation()
    return () => {
      isCancelled = true
    }
  }, [routingProfile])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setSubmitting(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await api.post('/research', {
        question: question.trim(),
        context: context.trim() || undefined,
        constraints: constraints.trim()
          ? constraints.trim().split('\n').filter(Boolean)
          : [],
        routing_profile: routingProfile,
      })

      setSuccess('Research job created successfully!')
      setTimeout(() => {
        navigate(`/research/${response.data.id}`)
      }, 1000)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create research job')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="card">
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: 'var(--spacing-lg)' }}>
          New Autonomous Research Job
        </h1>

        <form onSubmit={handleSubmit}>
          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: 'var(--spacing-md)',
                background: '#fee2e2',
                color: '#991b1b',
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--spacing-md)',
              }}
            >
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {success && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: 'var(--spacing-md)',
                background: '#d1fae5',
                color: '#065f46',
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--spacing-md)',
              }}
            >
              <CheckCircle size={20} />
              {success}
            </div>
          )}

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="question">
              Research Question *
            </label>
            <textarea
              id="question"
              className="input"
              rows={4}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What would you like to research? (e.g., Comparative analysis of multimodal token pruning algorithms in 2026)..."
              required
              disabled={submitting}
            />
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
              Describe your objective in detail for DAG planning and multi-agent synthesis.
            </p>
          </div>

          {/* Model Ecosystem Routing Profile Selector */}
          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Cpu size={16} /> Intelligent Model Routing Profile
            </label>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                gap: 'var(--spacing-sm)',
                marginTop: 'var(--spacing-xs)',
              }}
            >
              {PROFILES.map((p) => {
                const IconComponent = p.icon
                const isSelected = routingProfile === p.id
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setRoutingProfile(p.id)}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      padding: '12px',
                      borderRadius: 'var(--radius-md)',
                      border: isSelected
                        ? `2px solid ${p.color}`
                        : '1px solid var(--color-border)',
                      background: isSelected ? 'rgba(99, 102, 241, 0.08)' : 'var(--color-surface)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      <IconComponent size={16} color={p.color} />
                      <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{p.name}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', lineHeight: 1.3 }}>
                      {p.desc}
                    </span>
                  </button>
                )
              })}
            </div>

            {/* Live Model Simulation Preview */}
            {simResult && (
              <div
                style={{
                  marginTop: '10px',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--color-border)',
                  fontSize: '0.8rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Info size={14} style={{ color: 'var(--color-primary)' }} />
                  <span>
                    Routing Target: <strong>{simResult.selected_model_id}</strong> ({simResult.selected_provider})
                  </span>
                  {simResult.pareto_frontier.includes(simResult.selected_model_id) && (
                    <span
                      style={{
                        fontSize: '0.7rem',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: 'rgba(34, 197, 94, 0.15)',
                        color: '#22c55e',
                        fontWeight: 600,
                      }}
                    >
                      Pareto Optimal
                    </span>
                  )}
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
                  {loadingSim ? 'Optimizing...' : simResult.tradeoff_analysis.split('.')[0]}
                </div>
              </div>
            )}
          </div>

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="context">
              Additional Context
            </label>
            <textarea
              id="context"
              className="input"
              rows={3}
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Any background knowledge, reference baseline, or project context..."
              disabled={submitting}
            />
          </div>

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="constraints">
              Constraints (one per line)
            </label>
            <textarea
              id="constraints"
              className="input"
              rows={3}
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="peer-reviewed sources only&#10;last 5 years&#10;focus on multimodal architecture"
              disabled={submitting}
            />
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
              Optional constraints to guide the research (one per line).
            </p>
          </div>

          <button
            type="submit"
            className={clsx('btn btn-primary', { 'opacity-50': submitting })}
            disabled={submitting || !question.trim()}
            style={{ width: '100%', padding: 'var(--spacing-md)' }}
          >
            {submitting ? (
              <>
                <Loader2 className="loading-spinner" /> Starting Autonomous Pipeline...
              </>
            ) : (
              <>
                Start Research <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>
      </div>

      <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
          Research Ecosystem Best Practices
        </h3>
        <ul
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--spacing-md)',
            listStyle: 'none',
          }}
        >
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Select Quality Profile for complex multi-variable synthesis</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Use Cost Efficient profile for large bulk sweeps</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Specify strict constraints to anchor evidence verification</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Automatic Knowledge Graph entity linking enabled</span>
          </li>
        </ul>
      </div>
    </div>
  )
}