import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { AgentEvaluationRecord, AgentMetricsSummary } from '../types/agentEvaluations'
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Play,
  RefreshCw,
  Activity,
  Bot,
  Cpu,
  Layers,
  Search,
  FileText,
  FileCheck,
  TrendingUp,
} from 'lucide-react'

export function AgentEvaluationPage() {
  const [evaluations, setEvaluations] = useState<AgentEvaluationRecord[]>([])
  const [summary, setSummary] = useState<AgentMetricsSummary | null>(null)
  const [selectedEvaluation, setSelectedEvaluation] = useState<AgentEvaluationRecord | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false)
  const [showRunModal, setShowRunModal] = useState<boolean>(false)
  const [targetAgent, setTargetAgent] = useState<string>('PlannerAgent')
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      const [evalsRes, summaryRes] = await Promise.all([
        api.get('/agents/evaluations'),
        api.get('/agents/metrics/summary')
      ])
      setEvaluations(evalsRes.data || [])
      setSummary(summaryRes.data || null)
    } catch (err) {
      console.error('Failed to load agent evaluation metrics:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsEvaluating(true)
    setFeedbackMsg(null)

    try {
      const payload = {
        agent_name: targetAgent,
        research_objective: 'Evaluate autonomous synthesis and citation extraction accuracy',
        plan_tasks: [
          { title: 'Decompose prompt into primary research questions', description: 'Analyze research domain scope' },
          { title: 'Query vector knowledge store and retrieve grounded context', description: 'Execute hybrid search' },
          { title: 'Synthesize findings with claim-level citation markers', description: 'Generate final report' }
        ],
        step_telemetry: [
          {
            step_index: 1,
            agent_type: targetAgent,
            action_type: 'plan',
            tool_name: 'KnowledgeSearchTool',
            tool_args: { query: 'quantum materials' },
            tool_output_length: 420,
            success: true,
            latency_ms: 180,
            tokens_consumed: 65
          },
          {
            step_index: 2,
            agent_type: targetAgent,
            action_type: 'tool_call',
            tool_name: 'DataAnalysisTool',
            tool_args: { operation: 'descriptive' },
            tool_output_length: 280,
            success: true,
            latency_ms: 220,
            tokens_consumed: 90
          }
        ],
        evidence_items: [
          { content: 'Superconducting quantum circuits operate at millikelvin temperatures and utilize Josephson junctions.' },
          { content: 'Topological qubits offer theoretical hardware-level fault tolerance against decoherence.' }
        ],
        report_text: 'Superconducting quantum circuits operate at millikelvin temperatures utilizing Josephson junctions. Furthermore, topological qubits provide intrinsic fault tolerance.',
        claims: [
          'Superconducting quantum circuits operate at millikelvin temperatures.',
          'Topological qubits provide intrinsic fault tolerance against decoherence.'
        ],
        execution_time_ms: 400,
        total_tokens: 155,
        cost_usd: 0.00004
      }

      const res = await api.post('/agents/evaluate', payload)
      setFeedbackMsg({
        type: 'success',
        text: `Evaluation completed for ${targetAgent} (Overall Score: ${(res.data.overall_score * 100).toFixed(1)}%)`
      })
      setShowRunModal(false)
      await fetchData()

      const detailRes = await api.get(`/agents/evaluations/${res.data.id}`)
      setSelectedEvaluation(detailRes.data)
    } catch (err: any) {
      setFeedbackMsg({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to trigger agent evaluation'
      })
    } finally {
      setIsEvaluating(false)
    }
  }

  const handleSelectRecord = async (record: AgentEvaluationRecord) => {
    try {
      const detailRes = await api.get(`/agents/evaluations/${record.id}`)
      setSelectedEvaluation(detailRes.data)
    } catch {
      setSelectedEvaluation(record)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.85) return 'var(--color-success, #10b981)'
    if (score >= 0.70) return 'var(--color-primary, #6366f1)'
    if (score >= 0.50) return 'var(--color-warning, #f59e0b)'
    return 'var(--color-danger, #ef4444)'
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
      {/* Header Banner */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%)',
        padding: 'var(--spacing-xl)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
            <Activity size={28} color="var(--color-success, #10b981)" />
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700 }}>Agent Observability & Evaluation</h1>
          </div>
          <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
            Telemetry, plan precision, tool execution accuracy, evidence coverage, and hallucination tracking across autonomous agents.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
          <button
            onClick={fetchData}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
              padding: '0.65rem 1.1rem',
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text)',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            <RefreshCw size={16} className={isLoading ? 'loading-spinner' : ''} />
            Refresh
          </button>
          <button
            onClick={() => setShowRunModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-xs)',
              padding: '0.65rem 1.25rem',
              background: 'var(--color-primary)',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              color: '#ffffff',
              cursor: 'pointer',
              fontWeight: 600,
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
            }}
          >
            <Play size={16} />
            Run Agent Audit
          </button>
        </div>
      </div>

      {feedbackMsg && (
        <div style={{
          padding: 'var(--spacing-md)',
          borderRadius: 'var(--radius-md)',
          background: feedbackMsg.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${feedbackMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          color: feedbackMsg.type === 'success' ? 'var(--color-success, #10b981)' : 'var(--color-danger, #ef4444)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-sm)'
        }}>
          <CheckCircle2 size={18} />
          <span>{feedbackMsg.text}</span>
        </div>
      )}

      {/* KPI Cards */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--spacing-md)' }}>
          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              <span>Overall Quality</span>
              <TrendingUp size={18} color="var(--color-primary)" />
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 700, color: getScoreColor(summary.avg_score), marginTop: '8px' }}>
              {(summary.avg_score * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Across {summary.total_evaluations} evaluated runs
            </div>
          </div>

          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              <span>Hallucination Rate</span>
              <ShieldAlert size={18} color={summary.avg_hallucination_rate < 0.05 ? '#10b981' : '#ef4444'} />
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 700, color: summary.avg_hallucination_rate < 0.05 ? '#10b981' : '#ef4444', marginTop: '8px' }}>
              {(summary.avg_hallucination_rate * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Ungrounded assertion frequency
            </div>
          </div>

          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              <span>Tool Call Accuracy</span>
              <Cpu size={18} color="#6366f1" />
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#6366f1', marginTop: '8px' }}>
              {(summary.avg_tool_accuracy * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Zero-crash execution rate
            </div>
          </div>

          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-lg)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              <span>Evidence Coverage</span>
              <FileCheck size={18} color="#a855f7" />
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#a855f7', marginTop: '8px' }}>
              {(summary.avg_evidence_coverage * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Grounded claim percentage
            </div>
          </div>
        </div>
      )}

      {/* Per-Agent Core Architecture Breakdown */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: 'var(--spacing-md)'
      }}>
        {[
          { name: 'PlannerAgent', icon: Layers, role: 'Decomposition & Replanning', color: '#6366f1' },
          { name: 'WebResearchAgent', icon: Search, role: 'SSRF-Safe Web Sourcing', color: '#38bdf8' },
          { name: 'DocumentAnalysisAgent', icon: FileText, role: 'Multimodal Chunking & Tables', color: '#10b981' },
          { name: 'CriticAgent', icon: AlertTriangle, role: 'Contradiction & Gap Audits', color: '#f59e0b' },
          { name: 'ReportAgent', icon: FileCheck, role: 'Citation-Grounded Synthesis', color: '#a855f7' }
        ].map(agent => (
          <div
            key={agent.name}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-md)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-xs)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', color: agent.color }}>
              <agent.icon size={18} />
              <strong style={{ fontSize: '0.85rem' }}>{agent.name}</strong>
            </div>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              {agent.role}
            </p>
          </div>
        ))}
      </div>

      {/* Historical Agent Runs Table */}
      <div style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: 'var(--spacing-lg)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
            <Bot size={20} color="var(--color-primary)" />
            <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600 }}>Agent Execution Scorecards</h2>
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
            {evaluations.length} evaluation records
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>AGENT / PIPELINE</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>OVERALL SCORE</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>PLAN PRECISION</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>TOOL ACCURACY</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>EVIDENCE COV</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>HALLUCINATION</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>STEPS</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>DATE</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: 'var(--spacing-xl)', color: 'var(--color-text-secondary)' }}>
                    No agent evaluations recorded. Click "Run Agent Audit" to perform telemetry evaluation.
                  </td>
                </tr>
              ) : (
                evaluations.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => handleSelectRecord(row)}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      cursor: 'pointer',
                      background: selectedEvaluation?.id === row.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                      transition: 'background 0.2s'
                    }}
                  >
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      <div style={{ fontWeight: 600 }}>{row.agent_name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                        {row.job_id ? `Job: ${row.job_id.slice(0, 8)}...` : 'Standalone Audit'}
                      </div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      <span style={{ fontWeight: 700, color: getScoreColor(row.overall_score), fontSize: '0.95rem' }}>
                        {(row.overall_score * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.plan_precision * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.tool_accuracy * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.evidence_coverage * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background: row.hallucination_rate < 0.05 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: row.hallucination_rate < 0.05 ? '#10b981' : '#ef4444'
                      }}>
                        {(row.hallucination_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                      {row.successful_steps} / {row.total_steps}
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detailed Scorecard & Step Telemetry Drawer */}
      {selectedEvaluation && (
        <div style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700 }}>
                Scorecard Breakdown: {selectedEvaluation.agent_name}
              </h3>
              <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                Synthesis Fidelity: {(selectedEvaluation.synthesis_fidelity * 100).toFixed(1)}% • Execution Time: {selectedEvaluation.execution_time_ms} ms • Tokens: {selectedEvaluation.total_tokens}
              </p>
            </div>
            <button
              onClick={() => setSelectedEvaluation(null)}
              style={{
                padding: '0.4rem 0.8rem',
                background: 'transparent',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-text-secondary)',
                cursor: 'pointer'
              }}
            >
              Close
            </button>
          </div>

          {/* Step Timeline */}
          {selectedEvaluation.steps && selectedEvaluation.steps.length > 0 && (
            <div>
              <h4 style={{ margin: '0 0 var(--spacing-md) 0', fontSize: '1rem', fontWeight: 600 }}>
                Sequential Action Step Telemetry
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                {selectedEvaluation.steps.map((step) => (
                  <div
                    key={step.id || step.step_index}
                    style={{
                      padding: 'var(--spacing-sm) var(--spacing-md)',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>
                        Step #{step.step_index}: {step.action_type}
                      </span>
                      {step.tool_name && (
                        <span style={{ marginLeft: '8px', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                          Tool: <code>{step.tool_name}</code>
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-md)', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                      <span>{step.latency_ms} ms</span>
                      <span>{step.tokens_consumed} tokens</span>
                      <span style={{ color: step.success ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                        {step.success ? 'SUCCESS' : 'FAILED'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Run Audit Modal */}
      {showRunModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--spacing-xl)',
            width: '100%',
            maxWidth: '480px',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)'
          }}>
            <h3 style={{ margin: '0 0 var(--spacing-md) 0', fontSize: '1.25rem', fontWeight: 700 }}>
              Trigger Agent Evaluation Audit
            </h3>
            <p style={{ margin: '0 0 var(--spacing-lg) 0', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              Run multi-dimensional evaluation measuring plan precision, tool execution accuracy, and hallucination bounds.
            </p>

            <form onSubmit={handleRunEvaluation} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
                  Target Agent / Subsystem
                </label>
                <select
                  value={targetAgent}
                  onChange={(e) => setTargetAgent(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text)',
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="PlannerAgent" style={{ background: '#1e1e2e' }}>PlannerAgent</option>
                  <option value="WebResearchAgent" style={{ background: '#1e1e2e' }}>WebResearchAgent</option>
                  <option value="DocumentAnalysisAgent" style={{ background: '#1e1e2e' }}>DocumentAnalysisAgent</option>
                  <option value="CriticAgent" style={{ background: '#1e1e2e' }}>CriticAgent</option>
                  <option value="ReportAgent" style={{ background: '#1e1e2e' }}>ReportAgent</option>
                  <option value="ResearchPipeline" style={{ background: '#1e1e2e' }}>Full Research Pipeline</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-md)' }}>
                <button
                  type="button"
                  disabled={isEvaluating}
                  onClick={() => setShowRunModal(false)}
                  style={{
                    padding: '0.6rem 1.2rem',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isEvaluating}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-xs)',
                    padding: '0.6rem 1.4rem',
                    background: 'var(--color-primary)',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    color: '#ffffff',
                    fontWeight: 600,
                    cursor: isEvaluating ? 'not-allowed' : 'pointer',
                    boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
                  }}
                >
                  {isEvaluating ? (
                    <>
                      <RefreshCw size={16} className="loading-spinner" />
                      Auditing...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      Run Audit
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
