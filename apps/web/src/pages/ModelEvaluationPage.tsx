import React, { useState, useEffect } from 'react'
import { api } from '../services/api'
import { LeaderboardEntry, EvaluationRecord } from '../types/models'
import {
  Trophy,
  Play,
  CheckCircle2,
  Clock,
  Coins,
  BarChart3,
  RefreshCw,
  Award,
  ChevronRight,
  Zap,
  BookOpen,
  Scale,
  Target
} from 'lucide-react'

export function ModelEvaluationPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [history, setHistory] = useState<EvaluationRecord[]>([])
  const [selectedEvaluation, setSelectedEvaluation] = useState<EvaluationRecord | null>(null)
  const [availableModels, setAvailableModels] = useState<string[]>([])
  
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false)
  const [evalModel, setEvalModel] = useState<string>('')
  const [showRunModal, setShowRunModal] = useState<boolean>(false)
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      const [leaderboardRes, historyRes, modelsRes] = await Promise.all([
        api.get('/models/leaderboard'),
        api.get('/models/evaluations'),
        api.get('/models/profiles')
      ])

      setLeaderboard(Array.isArray(leaderboardRes.data) ? leaderboardRes.data : (leaderboardRes.data.leaderboard || []))
      setHistory(Array.isArray(historyRes.data) ? historyRes.data : (historyRes.data.evaluations || []))
      
      const registered = Object.keys(modelsRes.data.profiles || {})
      const modelOptions = registered.length > 0 ? registered : ['gemini-2.0-flash', 'gemini-1.5-pro', 'gpt-4o-mini', 'llama3:8b']
      setAvailableModels(modelOptions)
      if (modelOptions.length > 0 && !evalModel) {
        setEvalModel(modelOptions[0])
      }
    } catch (err: any) {
      console.error('Failed to load evaluation data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!evalModel) return
    setIsEvaluating(true)
    setFeedbackMsg(null)

    try {
      const res = await api.post('/models/evaluate', {
        model_id: evalModel,
        benchmark_name: 'research_core_eval_v1',
      })
      setFeedbackMsg({
        type: 'success',
        text: `Evaluation completed for ${evalModel} (Overall Score: ${(res.data.overall_score * 100).toFixed(1)}%)`
      })
      setShowRunModal(false)
      await fetchData()
      // Automatically load detailed evaluation run
      const detailRes = await api.get(`/models/evaluations/${res.data.id}`)
      setSelectedEvaluation(detailRes.data)
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to execute model evaluation' })
    } finally {
      setIsEvaluating(false)
    }
  }

  const handleSelectRecord = async (record: EvaluationRecord) => {
    try {
      const detailRes = await api.get(`/models/evaluations/${record.id}`)
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
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%)',
        padding: 'var(--spacing-xl)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
            <Trophy size={28} color="var(--color-primary)" />
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700 }}>Model Benchmark Leaderboard</h1>
          </div>
          <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
            Empirical ground-truth evaluation harness measuring factual accuracy, reasoning depth, retrieval faithfulness, latency, and cost.
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
            Run Benchmark
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

      {/* Main Leaderboard Table */}
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
            <Award size={20} color="var(--color-primary)" />
            <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600 }}>Active Model Rankings</h2>
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
            Evaluated on Research Ground-Truth Dataset (5 Multi-Domain Tasks)
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>RANK</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>MODEL</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>OVERALL SCORE</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>FACTUALITY</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>REASONING</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>FAITHFULNESS</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>LATENCY</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>COST / 1K</th>
                <th style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.85rem', color: 'var(--color-text-secondary)', fontWeight: 600 }}>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: 'var(--spacing-xl)', color: 'var(--color-text-secondary)' }}>
                    No evaluations recorded yet. Click "Run Benchmark" to evaluate models!
                  </td>
                </tr>
              ) : (
                leaderboard.map((row) => (
                  <tr
                    key={row.model_id}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      transition: 'background 0.2s',
                    }}
                  >
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontWeight: 700 }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '26px',
                        height: '26px',
                        borderRadius: '50%',
                        background: row.rank === 1 ? 'rgba(234, 179, 8, 0.2)' : row.rank === 2 ? 'rgba(148, 163, 184, 0.2)' : row.rank === 3 ? 'rgba(217, 119, 6, 0.2)' : 'transparent',
                        color: row.rank === 1 ? '#eab308' : row.rank === 2 ? '#94a3b8' : row.rank === 3 ? '#d97706' : 'var(--color-text-secondary)',
                        fontSize: '0.85rem'
                      }}>
                        {row.rank}
                      </span>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      <div style={{ fontWeight: 600 }}>{row.model_id}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>{row.provider_name}</div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div style={{
                          flex: 1,
                          height: '8px',
                          background: 'rgba(255, 255, 255, 0.08)',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          minWidth: '60px'
                        }}>
                          <div style={{
                            width: `${(row.overall_score * 100).toFixed(0)}%`,
                            height: '100%',
                            background: getScoreColor(row.overall_score),
                            borderRadius: '4px'
                          }} />
                        </div>
                        <span style={{ fontWeight: 700, color: getScoreColor(row.overall_score), minWidth: '42px', fontSize: '0.9rem' }}>
                          {(row.overall_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.factual_accuracy * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.reasoning_depth * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      {(row.retrieval_faithfulness * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-secondary)' }}>
                        <Clock size={14} />
                        {row.mean_latency_ms.toFixed(0)} ms
                      </div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)', fontSize: '0.9rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-secondary)' }}>
                        <Coins size={14} />
                        ${row.cost_per_1k_usd.toFixed(5)}
                      </div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md) var(--spacing-lg)' }}>
                      {row.is_pareto_optimal ? (
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '3px 8px',
                          background: 'rgba(99, 102, 241, 0.15)',
                          color: 'var(--color-primary)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          border: '1px solid rgba(99, 102, 241, 0.3)'
                        }}>
                          <Zap size={12} />
                          Pareto Optimal
                        </span>
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Standard</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Grid: Benchmark Breakdown & Evaluation Run History */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-lg)' }}>
        {/* Metric Dimensions Explained */}
        <div style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-md)' }}>
            <BarChart3 size={20} color="var(--color-primary)" />
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>Automated Evaluation Metrics</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'flex-start' }}>
              <Target size={18} color="#10b981" style={{ marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem' }}>Factual Accuracy (Weight: 35%)</strong>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                  Evaluates exact match, semantic cosine overlap, and absence of hallucinated statements.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'flex-start' }}>
              <Scale size={18} color="#6366f1" style={{ marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem' }}>Reasoning Depth (Weight: 25%)</strong>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                  Assesses structured multi-step deduction, constraint satisfaction, and logical coherence.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'flex-start' }}>
              <BookOpen size={18} color="#a855f7" style={{ marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem' }}>Retrieval Faithfulness & Citations (Weight: 25%)</strong>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                  Verifies claims against ground-truth context and measures precision of provided references.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'flex-start' }}>
              <Zap size={18} color="#f59e0b" style={{ marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.9rem' }}>Efficiency & Pareto Frontier (Weight: 15%)</strong>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                  Measures P95 latency and token cost to surface cost-effective and ultra-low latency alternatives.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* History List */}
        <div style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--spacing-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>Recent Benchmark Runs</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>{history.length} runs</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', maxHeight: '280px', overflowY: 'auto' }}>
            {history.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 'var(--spacing-lg)', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                No recent runs recorded.
              </div>
            ) : (
              history.map((record) => (
                <div
                  key={record.id}
                  onClick={() => handleSelectRecord(record)}
                  style={{
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    borderRadius: 'var(--radius-md)',
                    background: selectedEvaluation?.id === record.id ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${selectedEvaluation?.id === record.id ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.2s'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{record.model_id}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                      {new Date(record.created_at).toLocaleString()} • {record.benchmark_name}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <span style={{
                      fontWeight: 700,
                      color: getScoreColor(record.overall_score),
                      fontSize: '0.9rem'
                    }}>
                      {(record.overall_score * 100).toFixed(1)}%
                    </span>
                    <ChevronRight size={16} color="var(--color-text-secondary)" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Evaluation Details Drawer */}
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
                Evaluation Breakdown: {selectedEvaluation.model_id}
              </h3>
              <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                Benchmark: {selectedEvaluation.benchmark_name} • Pass Rate: {(selectedEvaluation.pass_rate * 100).toFixed(1)}% • Latency: {selectedEvaluation.mean_latency_ms.toFixed(0)} ms
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

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Factual Accuracy</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#10b981', marginTop: '4px' }}>
                {(selectedEvaluation.mean_accuracy * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Reasoning Depth</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#6366f1', marginTop: '4px' }}>
                {(selectedEvaluation.mean_reasoning * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Retrieval Faithfulness</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#a855f7', marginTop: '4px' }}>
                {(selectedEvaluation.mean_faithfulness * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Citation Precision</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f59e0b', marginTop: '4px' }}>
                {(selectedEvaluation.mean_citation_precision * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Sample Results */}
          {selectedEvaluation.sample_results && selectedEvaluation.sample_results.length > 0 && (
            <div>
              <h4 style={{ margin: '0 0 var(--spacing-md) 0', fontSize: '1rem', fontWeight: 600 }}>
                Sample Benchmark Questions & Ground Truth Matches
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                {selectedEvaluation.sample_results.map((sample, idx) => (
                  <div
                    key={sample.sample_id || idx}
                    style={{
                      padding: 'var(--spacing-md)',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--spacing-xs)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-primary)' }}>
                        Task #{idx + 1}: {sample.sample_id} ({sample.category})
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background: sample.score >= 0.7 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: sample.score >= 0.7 ? '#10b981' : '#ef4444'
                      }}>
                        Score: {(sample.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '0.85rem' }}>
                      <strong>Prompt:</strong> {sample.prompt}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', background: 'rgba(0,0,0,0.2)', padding: 'var(--spacing-xs) var(--spacing-sm)', borderRadius: 'var(--radius-sm)' }}>
                      <strong>Model Output:</strong> {sample.response_text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Run Benchmark Modal */}
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
              Run Ground-Truth Benchmark
            </h3>
            <p style={{ margin: '0 0 var(--spacing-lg) 0', color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
              Execute the standard 5-task benchmark suite against the chosen model to evaluate accuracy, reasoning, faithfulness, and speed.
            </p>

            <form onSubmit={handleRunEvaluation} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
                  Target Model
                </label>
                <select
                  value={evalModel}
                  onChange={(e) => setEvalModel(e.target.value)}
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
                  {availableModels.map(model => (
                    <option key={model} value={model} style={{ background: '#1e1e2e' }}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
                  Benchmark Suite
                </label>
                <input
                  type="text"
                  disabled
                  value="Research Ground Truth Benchmark v1.0 (5 Tasks)"
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-text-secondary)',
                    fontSize: '0.85rem'
                  }}
                />
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
                      Evaluating...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      Start Run
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
