import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react'
import { api } from '../services/api'
import { clsx } from 'clsx'

export function NewResearch() {
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [context, setContext] = useState('')
  const [constraints, setConstraints] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

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
        constraints: constraints.trim() ? constraints.trim().split('\n').filter(Boolean) : [],
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
    <div style={{ maxWidth: '700px' }}>
      <div className="card">
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: 'var(--spacing-lg)' }}>
          New Research Job
        </h1>
        
        <form onSubmit={handleSubmit}>
          {error && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-md)', 
              background: '#fee2e2', 
              color: '#991b1b', 
              borderRadius: 'var(--radius-md)',
              marginBottom: 'var(--spacing-md)'
            }}>
              <AlertCircle size={20} />
              {error}
            </div>
          )}
          
          {success && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-md)', 
              background: '#d1fae5', 
              color: '#065f46', 
              borderRadius: 'var(--radius-md)',
              marginBottom: 'var(--spacing-md)'
            }}>
              <CheckCircle size={20} />
              {success}
            </div>
          )}

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="question">Research Question *</label>
            <textarea
              id="question"
              className="input"
              rows={4}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What would you like to research? Be specific and detailed..."
              required
              disabled={submitting}
            />
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
              Describe your research question or objective in detail.
            </p>
          </div>

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="context">Additional Context</label>
            <textarea
              id="context"
              className="input"
              rows={3}
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Any additional context, background information, or specific requirements..."
              disabled={submitting}
            />
          </div>

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <label className="label" htmlFor="constraints">Constraints (one per line)</label>
            <textarea
              id="constraints"
              className="input"
              rows={3}
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="peer-reviewed sources only&#10;last 5 years&#10;focus on North America"
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
                <Loader2 className="loading-spinner" /> Starting research...
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
          Tips for better research
        </h3>
        <ul style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)', listStyle: 'none' }}>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Be specific about your research question</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Add context to guide the approach</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Set constraints to filter sources</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)' }}>
            <CheckCircle size={18} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
            <span>Upload relevant documents if available</span>
          </li>
        </ul>
      </div>
    </div>
  )
}