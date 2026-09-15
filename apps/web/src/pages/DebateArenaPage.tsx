import React, { useState, useEffect } from 'react';
import {
  Swords,
  ShieldAlert,
  Award,
  Scale,
  Play,
  RotateCw,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Trash2,
} from 'lucide-react';
import {
  AgentDebate,
  DebateRound,
  DebateMetrics,
  CreateDebatePayload,
} from '../types/debate';
import { useWorkspace } from '../context/WorkspaceContext';

export const DebateArenaPage: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const [activeTab, setActiveTab] = useState<'debates' | 'arena' | 'consensus'>('debates');
  const [debates, setDebates] = useState<AgentDebate[]>([]);
  const [selectedDebate, setSelectedDebate] = useState<AgentDebate | null>(null);
  const [selectedRoundIndex, setSelectedRoundIndex] = useState<number>(0);
  const [metrics, setMetrics] = useState<DebateMetrics>({
    total_debates: 0,
    active_debates: 0,
    concluded_debates: 0,
    mean_confidence: 0.88,
    proposer_avg_elo: 1512.4,
    opposer_avg_elo: 1487.6,
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [executingRound, setExecutingRound] = useState<boolean>(false);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [formData, setFormData] = useState<CreateDebatePayload>({
    topic: '',
    initial_thesis: '',
    counter_thesis: '',
    max_rounds: 3,
    proposer_model: 'gemini-2.5-pro',
    opposer_model: 'gemini-2.5-pro',
    arbiter_model: 'gemini-2.5-pro',
  });

  const fetchDebates = async () => {
    setLoading(true);
    try {
      const queryParams = currentWorkspace?.id ? `?workspace_id=${currentWorkspace.id}` : '';
      const [debatesRes, metricsRes] = await Promise.all([
        fetch(`/api/v1/debates${queryParams}`),
        fetch(`/api/v1/debates/metrics${queryParams}`),
      ]);

      if (debatesRes.ok) {
        const data = await debatesRes.json();
        setDebates(data);
        if (data.length > 0 && !selectedDebate) {
          fetchDebateDetails(data[0].id);
        }
      }
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (err) {
      console.error('Failed to load debates:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDebateDetails = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/debates/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedDebate(data);
        if (data.rounds && data.rounds.length > 0) {
          setSelectedRoundIndex(data.rounds.length - 1);
        }
      }
    } catch (err) {
      console.error('Failed to load debate details:', err);
    }
  };

  useEffect(() => {
    fetchDebates();
  }, [currentWorkspace]);

  const handleCreateDebate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        workspace_id: currentWorkspace?.id,
      };
      const res = await fetch('/api/v1/debates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowCreateModal(false);
        setFormData({
          topic: '',
          initial_thesis: '',
          counter_thesis: '',
          max_rounds: 3,
          proposer_model: 'gemini-2.5-pro',
          opposer_model: 'gemini-2.5-pro',
          arbiter_model: 'gemini-2.5-pro',
        });
        await fetchDebates();
      }
    } catch (err) {
      console.error('Failed to create debate:', err);
    }
  };

  const handleAdvanceRound = async (debateId: string, runAll: boolean = false) => {
    setExecutingRound(true);
    try {
      const res = await fetch(`/api/v1/debates/${debateId}/rounds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ run_to_completion: runAll }),
      });
      if (res.ok) {
        await fetchDebateDetails(debateId);
        await fetchDebates();
      }
    } catch (err) {
      console.error('Failed to advance round:', err);
    } finally {
      setExecutingRound(false);
    }
  };

  const handleDeleteDebate = async (debateId: string) => {
    if (!confirm('Are you sure you want to permanently delete this debate?')) return;
    try {
      const res = await fetch(`/api/v1/debates/${debateId}`, { method: 'DELETE' });
      if (res.ok) {
        if (selectedDebate?.id === debateId) setSelectedDebate(null);
        await fetchDebates();
      }
    } catch (err) {
      console.error('Failed to delete debate:', err);
    }
  };

  const currentRound: DebateRound | undefined =
    selectedDebate?.rounds && selectedDebate.rounds[selectedRoundIndex];

  return (
    <div className="container" style={{ paddingBottom: '3rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            <Swords style={{ color: 'var(--color-primary)' }} />
            Adversarial Debate Arena & Consensus Engine
          </h1>
          <p style={{ color: 'var(--color-text-muted)', marginTop: '0.5rem', marginBottom: 0 }}>
            Generation 7 dialectical research: Proposer vs. Opposer multi-round arguments evaluated by an impartial Arbiter with Elo rating adjustments.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={fetchDebates} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <RotateCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Plus size={16} />
            Launch Debate
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1.25rem', background: 'var(--color-surface)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Total Debates</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>{metrics.total_debates}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-primary)', marginTop: '0.25rem' }}>{metrics.active_debates} Active Arenas</div>
        </div>
        <div className="card" style={{ padding: '1.25rem', background: 'var(--color-surface)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Proposer Avg Elo</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#38bdf8' }}>{metrics.proposer_avg_elo}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Affirmative Defense</div>
        </div>
        <div className="card" style={{ padding: '1.25rem', background: 'var(--color-surface)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Opposer Avg Elo</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f87171' }}>{metrics.opposer_avg_elo}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Skeptical Scrutiny</div>
        </div>
        <div className="card" style={{ padding: '1.25rem', background: 'var(--color-surface)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Consensus Confidence</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#34d399' }}>{(metrics.mean_confidence * 100).toFixed(0)}%</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Dialectical Synthesis</div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--color-border)', marginBottom: '1.5rem' }}>
        <button
          className={`btn ${activeTab === 'debates' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('debates')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderRadius: '8px 8px 0 0' }}
        >
          <Swords size={16} />
          Debate Sessions ({debates.length})
        </button>
        <button
          className={`btn ${activeTab === 'arena' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('arena')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderRadius: '8px 8px 0 0' }}
        >
          <Scale size={16} />
          Dialectical Arena Inspector
        </button>
        <button
          className={`btn ${activeTab === 'consensus' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('consensus')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderRadius: '8px 8px 0 0' }}
        >
          <Award size={16} />
          Synthesized Consensus Vault
        </button>
      </div>

      {/* Tab 1: Debates Overview */}
      {activeTab === 'debates' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
          {debates.length === 0 ? (
            <div className="card" style={{ gridColumn: '1 / -1', padding: '3rem', textAlign: 'center' }}>
              <Scale size={48} style={{ color: 'var(--color-text-muted)', margin: '0 auto 1rem' }} />
              <h3 style={{ margin: '0 0 0.5rem' }}>No Active Debates</h3>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
                Launch an adversarial multi-agent debate to stress-test hypotheses and synthesize grounded consensus.
              </p>
              <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                Launch First Debate
              </button>
            </div>
          ) : (
            debates.map((debate) => (
              <div
                key={debate.id}
                className="card"
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: selectedDebate?.id === debate.id ? '1px solid var(--color-primary)' : undefined,
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <span
                      style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background:
                          debate.status === 'concluded'
                            ? 'rgba(52, 211, 153, 0.15)'
                            : debate.status === 'active'
                            ? 'rgba(56, 189, 248, 0.15)'
                            : 'rgba(248, 113, 113, 0.15)',
                        color:
                          debate.status === 'concluded'
                            ? '#34d399'
                            : debate.status === 'active'
                            ? '#38bdf8'
                            : '#f87171',
                      }}
                    >
                      {debate.status.toUpperCase()}
                    </span>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                        Round {debate.current_round} / {debate.max_rounds}
                      </span>
                      <button
                        onClick={() => handleDeleteDebate(debate.id)}
                        style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', padding: '0.2rem' }}
                        title="Delete Debate"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: '0 0 0.5rem' }}>{debate.topic}</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', margin: '0 0 1rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    <strong>Thesis:</strong> {debate.initial_thesis}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', borderRadius: '8px', background: 'rgba(255,255,255,0.03)', marginBottom: '1rem', fontSize: '0.8rem' }}>
                    <div>
                      <span style={{ color: '#38bdf8', fontWeight: 600 }}>Proposer:</span> {debate.proposer_elo.toFixed(0)} Elo
                    </div>
                    <div>
                      <span style={{ color: '#f87171', fontWeight: 600 }}>Opposer:</span> {debate.opposer_elo.toFixed(0)} Elo
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.85rem' }}
                    onClick={() => {
                      fetchDebateDetails(debate.id);
                      setActiveTab('arena');
                    }}
                  >
                    Open Arena
                  </button>
                  {debate.status === 'active' && (
                    <button
                      className="btn btn-primary"
                      style={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                      onClick={() => handleAdvanceRound(debate.id, false)}
                      disabled={executingRound}
                    >
                      <Play size={14} />
                      Next Round
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Dialectical Arena Inspector */}
      {activeTab === 'arena' && selectedDebate && (
        <div>
          {/* Arena Subheader */}
          <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem', background: 'var(--color-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: 600 }}>
                  ARENA TOPIC
                </span>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700, margin: '0.25rem 0' }}>{selectedDebate.topic}</h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                  <strong>Thesis:</strong> {selectedDebate.initial_thesis}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {selectedDebate.status === 'active' && (
                  <>
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleAdvanceRound(selectedDebate.id, false)}
                      disabled={executingRound}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                      <Play size={16} />
                      Advance 1 Round
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleAdvanceRound(selectedDebate.id, true)}
                      disabled={executingRound}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                      <Sparkles size={16} />
                      Run to Consensus
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Round Stepper */}
            {selectedDebate.rounds && selectedDebate.rounds.length > 0 && (
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                {selectedDebate.rounds.map((round, idx) => (
                  <button
                    key={round.id}
                    onClick={() => setSelectedRoundIndex(idx)}
                    className={`btn ${selectedRoundIndex === idx ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ fontSize: '0.85rem', padding: '0.4rem 0.8rem' }}
                  >
                    Round {round.round_number} ({round.round_winner?.toUpperCase() || 'EVAL'})
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Split Screen Argument Feed */}
          {currentRound ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
              {/* Proposer Column */}
              <div className="card" style={{ padding: '1.5rem', borderTop: '4px solid #38bdf8' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ShieldAlert style={{ color: '#38bdf8' }} size={20} />
                    <span style={{ fontWeight: 700, color: '#38bdf8' }}>PROPOSER (Affirmative)</span>
                  </div>
                  <span style={{ fontSize: '0.85rem', padding: '0.2rem 0.6rem', borderRadius: '12px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8' }}>
                    Score: {(currentRound.proposer_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ lineHeight: 1.6, fontSize: '0.95rem', color: 'var(--color-text)', whiteSpace: 'pre-line', marginBottom: '1.5rem' }}>
                  {currentRound.proposer_argument}
                </div>

                {currentRound.proposer_citations && currentRound.proposer_citations.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                      CITED EVIDENCE:
                    </div>
                    {currentRound.proposer_citations.map((cite, i) => (
                      <div key={i} style={{ padding: '0.5rem', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                        <div style={{ fontWeight: 600, color: '#38bdf8' }}>{cite.title}</div>
                        <div style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', marginTop: '0.2rem' }}>"{cite.snippet}"</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Opposer Column */}
              <div className="card" style={{ padding: '1.5rem', borderTop: '4px solid #f87171' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Swords style={{ color: '#f87171' }} size={20} />
                    <span style={{ fontWeight: 700, color: '#f87171' }}>OPPOSER (Skeptical Rebuttal)</span>
                  </div>
                  <span style={{ fontSize: '0.85rem', padding: '0.2rem 0.6rem', borderRadius: '12px', background: 'rgba(248, 113, 113, 0.1)', color: '#f87171' }}>
                    Score: {(currentRound.opposer_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ lineHeight: 1.6, fontSize: '0.95rem', color: 'var(--color-text)', whiteSpace: 'pre-line', marginBottom: '1.5rem' }}>
                  {currentRound.opposer_argument}
                </div>

                {currentRound.opposer_citations && currentRound.opposer_citations.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                      COUNTER-EVIDENCE:
                    </div>
                    {currentRound.opposer_citations.map((cite, i) => (
                      <div key={i} style={{ padding: '0.5rem', borderRadius: '6px', background: 'rgba(255,255,255,0.02)', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                        <div style={{ fontWeight: 600, color: '#f87171' }}>{cite.title}</div>
                        <div style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', marginTop: '0.2rem' }}>"{cite.snippet}"</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
              <Play size={36} style={{ color: 'var(--color-primary)', margin: '0 auto 1rem' }} />
              <h3>Debate Ready to Start</h3>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
                Click "Advance 1 Round" to initiate Round 1 between the Proposer and Opposer agents.
              </p>
              <button
                className="btn btn-primary"
                onClick={() => handleAdvanceRound(selectedDebate.id, false)}
                disabled={executingRound}
              >
                Start Round 1
              </button>
            </div>
          )}

          {/* Arbiter Round Evaluation Box */}
          {currentRound && (
            <div className="card" style={{ padding: '1.5rem', background: 'rgba(20, 30, 45, 0.6)', borderLeft: '4px solid var(--color-primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Scale style={{ color: 'var(--color-primary)' }} size={20} />
                  <span style={{ fontWeight: 700 }}>ARBITER EVALUATION (Round {currentRound.round_number})</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontSize: '0.85rem' }}>
                  <span>
                    Winner: <strong style={{ color: 'var(--color-primary)' }}>{currentRound.round_winner?.toUpperCase()}</strong>
                  </span>
                  <span>
                    Elo Delta: <strong>{currentRound.elo_delta > 0 ? `+${currentRound.elo_delta}` : currentRound.elo_delta}</strong>
                  </span>
                </div>
              </div>
              <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text)', lineHeight: 1.5 }}>
                {currentRound.arbiter_critique || 'Evaluation in progress...'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Synthesized Consensus Vault */}
      {activeTab === 'consensus' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {debates.filter((d) => d.status === 'concluded').length === 0 ? (
            <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
              <Award size={48} style={{ color: 'var(--color-text-muted)', margin: '0 auto 1rem' }} />
              <h3>No Concluded Debates</h3>
              <p style={{ color: 'var(--color-text-muted)' }}>
                Complete all rounds of a debate to synthesize and view dialectical consensus reports.
              </p>
            </div>
          ) : (
            debates
              .filter((d) => d.status === 'concluded')
              .map((debate) => (
                <div key={debate.id} className="card" style={{ padding: '1.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', padding: '0.2rem 0.6rem', borderRadius: '12px', background: 'rgba(52, 211, 153, 0.15)' }}>
                        DIALECTICAL CONSENSUS REACHED
                      </span>
                      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0.5rem 0' }}>{debate.topic}</h2>
                    </div>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        fetchDebateDetails(debate.id);
                        setActiveTab('arena');
                      }}
                      style={{ fontSize: '0.85rem' }}
                    >
                      View Arena Logs
                    </button>
                  </div>

                  <div style={{ padding: '1rem', borderRadius: '8px', background: 'rgba(255,255,255,0.03)', marginBottom: '1.25rem', fontSize: '0.95rem', lineHeight: 1.6 }}>
                    <div style={{ fontWeight: 600, color: 'var(--color-primary)', marginBottom: '0.5rem' }}>Synthesized Statement:</div>
                    {debate.consensus?.consensus_statement || 'Consensus synthesized across rounds.'}
                  </div>

                  {debate.consensus && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div style={{ padding: '1rem', borderRadius: '8px', background: 'rgba(52, 211, 153, 0.05)', border: '1px solid rgba(52, 211, 153, 0.2)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#34d399', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                          <CheckCircle2 size={16} />
                          ACCEPTED & QUALIFIED CLAIMS
                        </div>
                        {debate.consensus.accepted_claims?.map((c, i) => (
                          <div key={i} style={{ fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                            • {c.claim}
                          </div>
                        ))}
                      </div>

                      <div style={{ padding: '1rem', borderRadius: '8px', background: 'rgba(248, 113, 113, 0.05)', border: '1px solid rgba(248, 113, 113, 0.2)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#f87171', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                          <AlertTriangle size={16} />
                          REFUTED / RESTRICTED POINTS
                        </div>
                        {debate.consensus.refuted_claims?.map((c, i) => (
                          <div key={i} style={{ fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                            • {c.claim} ({c.reason})
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
          )}
        </div>
      )}

      {/* Modal: Start New Debate */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '2rem', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.35rem', fontWeight: 700 }}>Launch Adversarial Debate</h2>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Configure participating models, initial thesis, and adversarial constraints.
            </p>

            <form onSubmit={handleCreateDebate}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                  Debate Topic / Research Inquiry
                </label>
                <input
                  type="text"
                  className="input"
                  required
                  placeholder="e.g. Ambient-pressure superconductivity in modified lead apatite structures"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                  Initial Thesis to Defend (Proposer Position)
                </label>
                <textarea
                  className="input"
                  required
                  rows={3}
                  placeholder="State the affirmative proposition substantiated by initial findings..."
                  value={formData.initial_thesis}
                  onChange={(e) => setFormData({ ...formData, initial_thesis: e.target.value })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                  Counter-Thesis (Optional Opposer Stance)
                </label>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Optional specific skepticism or boundary constraints to test..."
                  value={formData.counter_thesis || ''}
                  onChange={(e) => setFormData({ ...formData, counter_thesis: e.target.value })}
                  style={{ width: '100%', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                    Debate Rounds
                  </label>
                  <select
                    className="input"
                    value={formData.max_rounds}
                    onChange={(e) => setFormData({ ...formData, max_rounds: parseInt(e.target.value, 10) })}
                    style={{ width: '100%' }}
                  >
                    <option value={2}>2 Rounds (Quick Dialectic)</option>
                    <option value={3}>3 Rounds (Standard Synthesis)</option>
                    <option value={5}>5 Rounds (Deep Adversarial Audit)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                    Arbiter Model
                  </label>
                  <select
                    className="input"
                    value={formData.arbiter_model}
                    onChange={(e) => setFormData({ ...formData, arbiter_model: e.target.value })}
                    style={{ width: '100%' }}
                  >
                    <option value="gemini-2.5-pro">Google Gemini 2.5 Pro</option>
                    <option value="llama3:latest">Local Ollama Llama 3</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Initialize Arena
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
