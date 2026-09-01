import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, Clock, CheckCircle, AlertCircle, FileText, Search, FlaskConical, Layers, FileCheck } from 'lucide-react'
import { api, getResearchWebSocketUrl } from '../services/api'
import type { ResearchJob, ResearchTask, Source, Evidence, ResearchReport } from '../types/research'

export function ResearchDetail() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<ResearchJob | null>(null)
  const [tasks, setTasks] = useState<ResearchTask[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [report, setReport] = useState<ResearchReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'plan' | 'tasks' | 'sources' | 'evidence' | 'report'>('overview')
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<any>(null)

  const fetchData = useCallback(async () => {
    if (!id) return
    try {
      const [jobRes, tasksRes, sourcesRes, evidenceRes, reportRes] = await Promise.all([
        api.get(`/research/${id}`),
        api.get(`/research/${id}/tasks`),
        api.get(`/research/${id}/sources`),
        api.get(`/research/${id}/evidence`),
        api.get(`/research/${id}/report`).catch(() => ({ data: null })),
      ])
      setJob(jobRes.data)
      setTasks(tasksRes.data.tasks || tasksRes.data)
      setSources(sourcesRes.data.sources || sourcesRes.data)
      setEvidence(evidenceRes.data.evidence || evidenceRes.data)
      setReport(reportRes.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (!id) return

    let isMounted = true
    let reconnectAttempts = 0

    const connectWebSocket = () => {
      if (!isMounted) return

      try {
        const wsUrl = getResearchWebSocketUrl(id)
        const ws = new WebSocket(wsUrl)
        socketRef.current = ws

        ws.onopen = () => {
          reconnectAttempts = 0
        }

        ws.onmessage = (event) => {
          if (!isMounted) return
          try {
            const message = JSON.parse(event.data)
            if (message.type === 'snapshot' && message.data) {
              const data = message.data
              if (data.job) setJob(data.job)
              if (data.tasks) setTasks(data.tasks)
              if (data.sources) setSources(data.sources)
              if (data.evidence) setEvidence(data.evidence)
              if (data.report) setReport(data.report)
              setLoading(false)
            } else if (message.type === 'event' && message.event) {
              const ev = message.event
              const evType = ev.type
              const evData = ev.data || {}

              if (evType === 'job_started' || evType === 'job_completed' || evType === 'job_failed') {
                setJob(prev => prev ? {
                  ...prev,
                  status: evData.status || prev.status,
                  error_message: evData.error || prev.error_message,
                  completed_at: evType === 'job_completed' ? new Date().toISOString() : prev.completed_at,
                } : null)
                if (evType === 'job_completed') {
                  fetchData()
                }
              } else if (evType === 'tasks_created' && evData.tasks) {
                fetchData()
              } else if (evType === 'task_started' || evType === 'task_completed' || evType === 'task_failed') {
                setTasks(prev => prev.map(t => {
                  if (t.id === evData.task_id) {
                    return {
                      ...t,
                      status: evData.status || t.status,
                      error_message: evData.error || t.error_message,
                      completed_at: (evType === 'task_completed' || evType === 'task_failed') ? new Date().toISOString() : t.completed_at,
                    }
                  }
                  return t
                }))
                if (evType === 'task_completed' || evType === 'task_failed') {
                  fetchData()
                }
              } else if (
                evType === 'sources_added' ||
                evType === 'evidence_added' ||
                evType === 'verification_completed' ||
                evType === 'report_generated'
              ) {
                fetchData()
              }
            }
          } catch (parseErr) {
            console.error('Failed to parse WebSocket message', parseErr)
          }
        }

        ws.onerror = () => {
          fetchData()
        }

        ws.onclose = () => {
          if (!isMounted) return
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000)
          reconnectAttempts++
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, delay)
        }
      } catch (err) {
        console.error('WebSocket connection initialization failed', err)
        fetchData()
      }
    }

    fetchData()
    connectWebSocket()

    return () => {
      isMounted = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socketRef.current) {
        socketRef.current.close()
        socketRef.current = null
      }
    }
  }, [id, fetchData])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="text-warning" />
      case 'running': return <Loader2 className="text-primary animate-spin" />
      case 'completed': return <CheckCircle className="text-success" />
      case 'failed': return <AlertCircle className="text-error" />
      default: return <Clock className="text-muted" />
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'Pending',
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed',
    }
    return labels[status] || status
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
        <Loader2 className="loading-spinner" size={32} />
      </div>
    )
  }

  if (!job) {
    return (
      <div className="card empty-state">
        <AlertCircle size={48} />
        <h3>Research job not found</h3>
        <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 'var(--spacing-md)' }}>
          <ArrowLeft size={18} /> Back to Dashboard
        </Link>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FlaskConical },
    { id: 'plan', label: 'Plan', icon: Layers },
    { id: 'tasks', label: 'Tasks', icon: Search },
    { id: 'sources', label: 'Sources', icon: FileText },
    { id: 'evidence', label: 'Evidence', icon: FileCheck },
    { id: 'report', label: 'Report', icon: FileText, disabled: !report },
  ]

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
        <Link to="/dashboard" className="btn btn-outline" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
          <ArrowLeft size={18} /> Back
        </Link>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{job.question}</h1>
          <p style={{ color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
            {job.objective}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
          {getStatusIcon(job.status)}
          <span style={{ fontWeight: 500, textTransform: 'capitalize' }}>{getStatusLabel(job.status)}</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-lg)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--spacing-sm)' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => !tab.disabled && setActiveTab(tab.id as any)}
            disabled={tab.disabled}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-sm) var(--spacing-md)',
              borderRadius: 'var(--radius-md)',
              background: activeTab === tab.id ? 'var(--color-primary)' + '15' : 'transparent',
              color: activeTab === tab.id ? 'var(--color-primary)' : tab.disabled ? 'var(--color-text-muted)' : 'var(--color-text)',
              fontWeight: activeTab === tab.id ? 600 : 400,
              border: 'none',
              cursor: tab.disabled ? 'not-allowed' : 'pointer',
              opacity: tab.disabled ? 0.5 : 1,
              transition: 'all 0.2s',
            }}
          >
            <tab.icon size={18} />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="card">
        {activeTab === 'overview' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
              <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-background)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Status</p>
                <p style={{ fontWeight: 600, textTransform: 'capitalize' }}>{getStatusLabel(job.status)}</p>
              </div>
              <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-background)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Domain</p>
                <p style={{ fontWeight: 600 }}>{job.domain || 'Not specified'}</p>
              </div>
              <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-background)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Created</p>
                <p style={{ fontWeight: 600 }}>{new Date(job.created_at).toLocaleDateString()}</p>
              </div>
              <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-background)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Tasks</p>
                <p style={{ fontWeight: 600 }}>{tasks.filter(t => t.status === 'completed').length} / {tasks.length} completed</p>
              </div>
            </div>

            {job.constraints.length > 0 && (
              <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Constraints</h3>
                <ul style={{ listStyle: 'none', display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)' }}>
                  {job.constraints.map((c, i) => (
                    <li key={i} className="badge badge-pending">{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'plan' && (
          <div>
            <p style={{ color: 'var(--color-text-muted)' }}>
              Research plan will be displayed here after planning phase completes.
            </p>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div>
            {tasks.length === 0 ? (
              <div className="empty-state">
                <Search size={48} />
                <p>No tasks yet</p>
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Task</th>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Started</th>
                    <th>Completed</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(task => (
                    <tr key={task.id}>
                      <td>
                        <p style={{ fontWeight: 500 }}>{task.objective.slice(0, 80)}...</p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{task.type}</p>
                      </td>
                      <td>{task.agent}</td>
                      <td>{getStatusIcon(task.status)} <span style={{ textTransform: 'capitalize' }}>{task.status}</span></td>
                      <td style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                        {task.started_at ? new Date(task.started_at).toLocaleTimeString() : '-'}
                      </td>
                      <td style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                        {task.completed_at ? new Date(task.completed_at).toLocaleTimeString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'sources' && (
          <div>
            {sources.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} />
                <p>No sources collected yet</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                {sources.map(source => (
                  <div key={source.id} style={{ padding: 'var(--spacing-md)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)' }}>
                      <h4 style={{ fontWeight: 600 }}>{source.title}</h4>
                      <span className="badge badge-pending">{source.type}</span>
                    </div>
                    {source.url && (
                      <a href={source.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.875rem', wordBreak: 'break-all' }}>
                        {source.url}
                      </a>
                    )}
                    <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
                      Retrieved: {new Date(source.retrieved_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'evidence' && (
          <div>
            {evidence.length === 0 ? (
              <div className="empty-state">
                <FileCheck size={48} />
                <p>No evidence extracted yet</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                {evidence.map(e => (
                  <div key={e.id} style={{ padding: 'var(--spacing-md)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)' }}>
                      <span style={{ fontWeight: 500 }}>{e.claim}</span>
                      <span className="badge badge-pending">{Math.round(e.confidence * 100)}% confidence</span>
                    </div>
                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>{e.supporting_text.slice(0, 300)}...</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
                      Verification: {e.verification_status}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'report' && report && (
          <div style={{ maxWidth: '800px' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 'var(--spacing-sm)' }}>{report.title}</h2>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-lg)' }}>
              Generated: {new Date(report.generated_at).toLocaleString()}
            </p>
            
            {report.executive_summary && (
              <div style={{ marginBottom: 'var(--spacing-lg)', padding: 'var(--spacing-md)', background: 'var(--color-background)', borderRadius: 'var(--radius-md)' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Executive Summary</h3>
                <p>{report.executive_summary}</p>
              </div>
            )}

            {report.methodology && (
              <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Methodology</h3>
                <p>{report.methodology}</p>
              </div>
            )}

            {report.findings.length > 0 && (
              <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Key Findings</h3>
                {report.findings.map((f, i) => (
                  <div key={i} style={{ marginBottom: 'var(--spacing-md)', padding: 'var(--spacing-md)', borderLeft: '3px solid var(--color-primary)' }}>
                    <h4 style={{ fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>{f.topic}</h4>
                    <p style={{ marginBottom: 'var(--spacing-sm)' }}>{f.summary}</p>
                    <div style={{ display: 'flex', gap: 'var(--spacing-md)', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                      <span>Confidence: {Math.round(f.confidence * 100)}%</span>
                      {f.uncertainty && <span>Uncertainty: {f.uncertainty}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {report.conclusions.length > 0 && (
              <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Conclusions</h3>
                <ul style={{ listStyle: 'disc', paddingLeft: 'var(--spacing-lg)' }}>
                  {report.conclusions.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}

            {report.limitations.length > 0 && (
              <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)' }}>Limitations</h3>
                <ul style={{ listStyle: 'disc', paddingLeft: 'var(--spacing-lg)' }}>
                  {report.limitations.map((l, i) => <li key={i}>{l}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'report' && !report && job.status === 'completed' && (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
            <Loader2 className="loading-spinner" size={32} style={{ margin: '0 auto var(--spacing-md)' }} />
            <p>Report is being generated...</p>
          </div>
        )}

        {activeTab === 'report' && !report && job.status !== 'completed' && (
          <div className="empty-state">
            <FileText size={48} />
            <p>Report not available yet</p>
            <p style={{ fontSize: '0.875rem', marginTop: 'var(--spacing-sm)' }}>
              Report will be generated after research completes
            </p>
          </div>
        )}
      </div>
    </div>
  )
}