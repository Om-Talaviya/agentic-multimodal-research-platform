import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Clock, CheckCircle, AlertCircle, Loader2, FileText } from 'lucide-react'
import { clsx } from 'clsx'
import { api } from '../services/api'
import type { ResearchJob } from '../types/research'

export function Dashboard() {
  const [jobs, setJobs] = useState<ResearchJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await api.get('/research', { params: { limit: 20 } })
      const data = response.data
      const jobsList = Array.isArray(data) ? data : (data?.jobs || data?.items || [])
      setJobs(jobsList)
      setError(null)
    } catch (err) {
      setError('Failed to load research jobs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'badge-pending',
      running: 'badge-running',
      completed: 'badge-completed',
      failed: 'badge-failed',
    }
    const icons: Record<string, any> = {
      pending: Clock,
      running: Loader2,
      completed: CheckCircle,
      failed: AlertCircle,
    }
    const Icon = icons[status] || Clock
    return (
      <span className={clsx('badge', badges[status])}>
        <Icon size={12} /> {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
        <Loader2 className="loading-spinner" size={32} />
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Research Jobs</h1>
        <Link to="/research/new" className="btn btn-primary">
          <Plus size={18} /> New Research
        </Link>
      </div>

      {error && (
        <div style={{ 
          padding: 'var(--spacing-md)', 
          background: '#fee2e2', 
          color: '#991b1b', 
          borderRadius: 'var(--radius-md)',
          marginBottom: 'var(--spacing-md)'
        }}>
          {error}
        </div>
      )}

      {jobs.length === 0 ? (
        <div className="card empty-state">
          <Search size={48} />
          <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>No research jobs yet</h3>
          <p style={{ marginBottom: 'var(--spacing-md)' }}>Create your first research job to get started</p>
          <Link to="/research/new" className="btn btn-primary">
            <Plus size={18} /> Start Research
          </Link>
        </div>
      ) : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => (
                <tr key={job.id}>
                  <td style={{ maxWidth: '400px' }}>
                    <Link to={`/research/${job.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <p style={{ fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {job.question}
                      </p>
                      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
                        {job.objective.slice(0, 100)}{job.objective.length > 100 ? '...' : ''}
                      </p>
                    </Link>
                  </td>
                  <td>{getStatusBadge(job.status)}</td>
                  <td style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
                    {formatDate(job.created_at)}
                  </td>
                  <td>
                    <Link to={`/research/${job.id}`} className="btn btn-outline" style={{ padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.875rem' }}>
                      <FileText size={16} /> View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}