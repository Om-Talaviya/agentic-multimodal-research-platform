import React, { useState, useEffect } from 'react';
import {
  Clock,
  Play,
  Pause,
  Trash2,
  Bell,
  CheckCircle,
  Plus,
  RefreshCw,
  Zap,
  Radio,
  Sparkles,
} from 'lucide-react';
import {
  ScheduledResearch,
  ResearchSweepResult,
  AutomationAlert,
  AutomationMetrics,
  CreateSchedulePayload,
} from '../types/automation';

export const ResearchAutomationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'schedules' | 'sweeps' | 'alerts'>('schedules');
  const [schedules, setSchedules] = useState<ScheduledResearch[]>([]);
  const [sweeps, setSweeps] = useState<ResearchSweepResult[]>([]);
  const [alerts, setAlerts] = useState<AutomationAlert[]>([]);
  const [metrics, setMetrics] = useState<AutomationMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [title, setTitle] = useState<string>('');
  const [queryTopic, setQueryTopic] = useState<string>('');
  const [cronExpr, setCronExpr] = useState<string>('0 9 * * 1-5');
  const [routingProfile, setRoutingProfile] = useState<string>('balanced');
  const [noveltyThreshold, setNoveltyThreshold] = useState<number>(0.30);
  const [contradictionAlert, setContradictionAlert] = useState<boolean>(true);
  const [webhookUrl, setWebhookUrl] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Trigger loading state
  const [triggeringId, setTriggeringId] = useState<string | null>(null);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

      const [schedulesRes, alertsRes, metricsRes] = await Promise.all([
        fetch('/api/v1/automation/schedules', { headers }),
        fetch('/api/v1/automation/alerts', { headers }),
        fetch('/api/v1/automation/metrics', { headers }),
      ]);

      if (schedulesRes.ok) {
        const sData: ScheduledResearch[] = await schedulesRes.json();
        setSchedules(sData);

        // Fetch sweeps for top active schedules
        const scheduleSweeps: ResearchSweepResult[] = [];
        for (const s of sData.slice(0, 5)) {
          const swRes = await fetch(`/api/v1/automation/schedules/${s.id}/sweeps`, { headers });
          if (swRes.ok) {
            const swData = await swRes.json();
            scheduleSweeps.push(...swData);
          }
        }
        setSweeps(scheduleSweeps);
      }

      if (alertsRes.ok) {
        const aData = await alertsRes.json();
        setAlerts(aData);
      }

      if (metricsRes.ok) {
        const mData = await metricsRes.json();
        setMetrics(mData);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch automation data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleCreateSchedule = async () => {
    if (!title.trim() || !queryTopic.trim()) return;
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const payload: CreateSchedulePayload = {
        title: title.trim(),
        query_topic: queryTopic.trim(),
        cron_expression: cronExpr,
        routing_profile: routingProfile,
        source_types: ['web', 'academic', 'knowledge_vault'],
        novelty_threshold: noveltyThreshold,
        confidence_threshold: 0.85,
        contradiction_alert: contradictionAlert,
        webhook_url: webhookUrl.trim() || undefined,
      };

      const res = await fetch('/api/v1/automation/schedules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to create research schedule');
      setShowCreateModal(false);
      setTitle('');
      setQueryTopic('');
      setWebhookUrl('');
      fetchAllData();
    } catch (err: any) {
      alert(err.message || 'Error creating schedule');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTogglePause = async (schedule: ScheduledResearch) => {
    try {
      const token = localStorage.getItem('token');
      const action = schedule.status === 'active' ? 'pause' : 'resume';
      const res = await fetch(`/api/v1/automation/schedules/${schedule.id}/${action}`, {
        method: 'PATCH',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Failed to ${action} schedule`);
      fetchAllData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    if (!confirm('Are you sure you want to delete this scheduled research sweep?')) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/automation/schedules/${scheduleId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to delete schedule');
      fetchAllData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleTriggerSweepNow = async (scheduleId: string) => {
    setTriggeringId(scheduleId);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/automation/schedules/${scheduleId}/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) throw new Error('Failed to trigger sweep run');
      await fetchAllData();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setTriggeringId(null);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/automation/alerts/${alertId}/acknowledge`, {
        method: 'PATCH',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to acknowledge alert');
      fetchAllData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <div style={{ padding: '0.6rem', borderRadius: '10px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Radio size={26} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: '700', margin: 0 }}>Research Automation & Scheduled Sweeps</h1>
              <p style={{ margin: '0.25rem 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Continuous monitoring, autonomous topic sweeps, semantic diffing, and multi-channel alerting.
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={fetchAllData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 0.9rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: 'none',
              background: 'var(--accent)',
              color: '#fff',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            <Plus size={16} /> New Scheduled Sweep
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Active Schedules</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem', color: '#38bdf8' }}>
            {metrics?.active_schedules ?? schedules.filter(s => s.status === 'active').length}
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: '400' }}> / {schedules.length} total</span>
          </div>
        </div>

        <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Total Sweeps Executed</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem', color: 'var(--success)' }}>
            {metrics?.total_sweeps ?? sweeps.length}
          </div>
        </div>

        <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Average Novelty Score</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem', color: '#a855f7' }}>
            {metrics?.average_novelty_score ? `${(metrics.average_novelty_score * 100).toFixed(1)}%` : '42.5%'}
          </div>
        </div>

        <div style={{ padding: '1.25rem', borderRadius: '10px', background: 'var(--card-bg)', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Unacknowledged Alerts</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', marginTop: '0.25rem', color: (metrics?.unacknowledged_alerts ?? alerts.filter(a => !a.is_acknowledged).length) > 0 ? '#f59e0b' : 'var(--text-secondary)' }}>
            {metrics?.unacknowledged_alerts ?? alerts.filter(a => !a.is_acknowledged).length}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('schedules')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'schedules' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'schedules' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'schedules' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Clock size={16} /> Sweeps & Cron Schedules ({schedules.length})
        </button>

        <button
          onClick={() => setActiveTab('sweeps')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'sweeps' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'sweeps' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'sweeps' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Zap size={16} /> Sweep History & Diff Explorer ({sweeps.length})
        </button>

        <button
          onClick={() => setActiveTab('alerts')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'alerts' ? '2px solid var(--accent)' : '2px solid transparent',
            color: activeTab === 'alerts' ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: activeTab === 'alerts' ? '600' : '400',
            cursor: 'pointer',
          }}
        >
          <Bell size={16} /> Dispatched Alerts ({alerts.length})
        </button>
      </div>

      {/* TAB 1: Schedules */}
      {activeTab === 'schedules' && (
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', overflow: 'hidden' }}>
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>Active Monitoring Schedules</h3>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Automated background sweeps & novelty triggers</span>
          </div>

          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading research schedules...</div>
          ) : error ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger)' }}>{error}</div>
          ) : schedules.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Clock size={36} style={{ opacity: 0.4, marginBottom: '0.5rem' }} />
              <p>No scheduled research sweeps yet. Click "New Scheduled Sweep" to configure automatic monitoring.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Title & Topic</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Cron Frequency</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Novelty Threshold</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Sweeps Run</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Next Run</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {schedules.map(s => (
                    <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{s.title}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                          {s.query_topic}
                        </div>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ fontFamily: 'monospace', padding: '0.2rem 0.5rem', borderRadius: '4px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', fontSize: '0.8rem' }}>
                          {s.cron_expression}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ fontWeight: '600', color: '#a855f7' }}>
                          {(s.novelty_threshold * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>
                        {s.total_sweeps_count}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        {s.next_run_at ? new Date(s.next_run_at).toLocaleString() : 'Scheduled'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.3rem',
                            fontSize: '0.8rem',
                            color: s.status === 'active' ? 'var(--success)' : 'var(--text-secondary)',
                          }}
                        >
                          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: s.status === 'active' ? 'var(--success)' : '#64748b' }}></span>
                          {s.status.toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
                          <button
                            onClick={() => handleTriggerSweepNow(s.id)}
                            disabled={triggeringId === s.id}
                            title="Run Sweep Immediately"
                            style={{
                              padding: '0.35rem 0.6rem',
                              borderRadius: '6px',
                              border: '1px solid var(--border)',
                              background: 'rgba(56, 189, 248, 0.1)',
                              color: '#38bdf8',
                              cursor: triggeringId === s.id ? 'not-allowed' : 'pointer',
                            }}
                          >
                            <Play size={14} />
                          </button>

                          <button
                            onClick={() => handleTogglePause(s)}
                            title={s.status === 'active' ? 'Pause Schedule' : 'Resume Schedule'}
                            style={{
                              padding: '0.35rem 0.6rem',
                              borderRadius: '6px',
                              border: '1px solid var(--border)',
                              background: 'transparent',
                              color: 'var(--text-secondary)',
                              cursor: 'pointer',
                            }}
                          >
                            {s.status === 'active' ? <Pause size={14} /> : <Play size={14} />}
                          </button>

                          <button
                            onClick={() => handleDeleteSchedule(s.id)}
                            title="Delete Schedule"
                            style={{
                              padding: '0.35rem 0.6rem',
                              borderRadius: '6px',
                              border: '1px solid var(--border)',
                              background: 'transparent',
                              color: 'var(--text-secondary)',
                              cursor: 'pointer',
                            }}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Sweep History */}
      {activeTab === 'sweeps' && (
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: '600' }}>Sweep Execution History & Semantic Diff Logs</h3>

          {sweeps.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Zap size={36} style={{ opacity: 0.4, marginBottom: '0.5rem' }} />
              <p>No sweep execution logs found. Trigger a scheduled sweep to observe automated diffing.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {sweeps.map(sw => (
                <div key={sw.id} style={{ padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-primary)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span
                        style={{
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '700',
                          background: sw.alert_dispatched ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                          color: sw.alert_dispatched ? 'var(--danger)' : 'var(--success)',
                        }}
                      >
                        {sw.status.toUpperCase()}
                      </span>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {new Date(sw.executed_at).toLocaleString()}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem' }}>
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Novelty: </span>
                        <strong style={{ color: '#a855f7' }}>{(sw.novelty_score * 100).toFixed(1)}%</strong>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>New Claims: </span>
                        <strong style={{ color: '#38bdf8' }}>{sw.novel_claims_count}</strong>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Latency: </span>
                        <span>{sw.execution_duration_ms}ms</span>
                      </div>
                    </div>
                  </div>

                  {sw.novel_claims.length > 0 && (
                    <div style={{ marginTop: '0.5rem', padding: '0.6rem', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '0.3rem', textTransform: 'uppercase' }}>
                        Discovered Novel Claims:
                      </div>
                      <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                        {sw.novel_claims.map((c, i) => (
                          <li key={i} style={{ margin: '0.2rem 0' }}>{c.claim || c.summary}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Dispatched Alerts */}
      {activeTab === 'alerts' && (
        <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: '600' }}>Dispatched Notification & Webhook Alerts</h3>

          {alerts.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Bell size={36} style={{ opacity: 0.4, marginBottom: '0.5rem' }} />
              <p>No alerts triggered yet. Alerts will appear here when novel discoveries exceed set thresholds.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {alerts.map(a => (
                <div key={a.id} style={{ padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-primary)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                        <span
                          style={{
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            fontWeight: '700',
                            background: a.severity === 'critical' ? 'rgba(239, 68, 68, 0.2)' : a.severity === 'warning' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                            color: a.severity === 'critical' ? 'var(--danger)' : a.severity === 'warning' ? '#f59e0b' : '#38bdf8',
                            textTransform: 'uppercase',
                          }}
                        >
                          {a.severity}
                        </span>
                        <span style={{ fontSize: '0.75rem', padding: '0.15rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                          {a.channel.toUpperCase()}
                        </span>
                        <strong style={{ fontSize: '0.95rem' }}>{a.title}</strong>
                      </div>
                      <p style={{ margin: '0.2rem 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        {a.message}
                      </p>
                    </div>

                    {!a.is_acknowledged ? (
                      <button
                        onClick={() => handleAcknowledgeAlert(a.id)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                          padding: '0.35rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid var(--accent)',
                          background: 'rgba(56, 189, 248, 0.1)',
                          color: 'var(--accent)',
                          fontSize: '0.8rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                        }}
                      >
                        <CheckCircle size={14} /> Acknowledge
                      </button>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <CheckCircle size={14} /> Acknowledged
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MODAL: Create Scheduled Sweep */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1.5rem', width: '100%', maxWidth: '540px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#38bdf8' }}>
              <Sparkles size={20} />
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>New Scheduled Research Sweep</h3>
            </div>
            <p style={{ margin: '0 0 1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Configure autonomous background research queries with automatic novelty diffing and alerts.
            </p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Schedule Label</label>
              <input
                type="text"
                placeholder="e.g. Solid-State Battery Breakthroughs 2026"
                value={title}
                onChange={e => setTitle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Research Query Topic</label>
              <textarea
                rows={2}
                placeholder="What are the newly published papers and clinical/experimental trials in..."
                value={queryTopic}
                onChange={e => setQueryTopic(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  resize: 'vertical',
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Sweep Frequency</label>
                <select
                  value={cronExpr}
                  onChange={e => setCronExpr(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '0.85rem',
                  }}
                >
                  <option value="@hourly">Every Hour (@hourly)</option>
                  <option value="every_6h">Every 6 Hours (every_6h)</option>
                  <option value="@daily">Daily at Midnight (@daily)</option>
                  <option value="0 9 * * 1-5">Weekdays 9:00 AM (0 9 * * 1-5)</option>
                  <option value="@weekly">Weekly (@weekly)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Routing Profile</label>
                <select
                  value={routingProfile}
                  onChange={e => setRoutingProfile(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)',
                    background: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '0.85rem',
                  }}
                >
                  <option value="balanced">Balanced Adaptive</option>
                  <option value="quality_maximized">Deep Quality Maximized</option>
                  <option value="cost_minimized">Cost Efficient</option>
                  <option value="speed_maximized">Speed Maximized</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Novelty Alert Threshold</label>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#a855f7' }}>{(noveltyThreshold * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={noveltyThreshold}
                onChange={e => setNoveltyThreshold(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent)' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Trigger notification when new claims diff exceeds {(noveltyThreshold * 100).toFixed(0)}%</span>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.85rem',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  checked={contradictionAlert}
                  onChange={e => setContradictionAlert(e.target.checked)}
                  style={{ cursor: 'pointer' }}
                />
                <span>Alert immediately on factual contradictions with prior reports</span>
              </label>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-secondary)' }}>Webhook URL (Optional)</label>
              <input
                type="url"
                placeholder="https://webhook.site/your-endpoint"
                value={webhookUrl}
                onChange={e => setWebhookUrl(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
              <button
                onClick={() => setShowCreateModal(false)}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSchedule}
                disabled={submitting || !title.trim() || !queryTopic.trim()}
                style={{
                  padding: '0.5rem 1.25rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: 'var(--accent)',
                  color: '#fff',
                  fontWeight: '600',
                  cursor: submitting || !title.trim() || !queryTopic.trim() ? 'not-allowed' : 'pointer',
                  opacity: submitting || !title.trim() || !queryTopic.trim() ? 0.6 : 1,
                }}
              >
                {submitting ? 'Creating...' : 'Schedule Sweep'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
