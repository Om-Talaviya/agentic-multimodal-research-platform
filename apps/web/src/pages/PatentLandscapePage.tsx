import React, { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  ShieldCheck,
  Lightbulb,
  Layers,
  Scale,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import {
  PatentCorpus,
  PatentMetrics,
  PatentJurisdiction,
} from '../types/patent';

const SAMPLE_CORPUS: PatentCorpus = {
  id: 'corp-1',
  title: 'Fault-Tolerant Quantum Algorithm Architectures',
  technology_domain: 'quantum_computing',
  cpc_classification: 'G06N 10/00',
  jurisdiction: 'GLOBAL',
  total_patents_indexed: 3,
  freedom_to_operate_verdict: 'clear',
  status: 'active',
  created_at: new Date().toISOString(),
  patents: [
    {
      id: 'p-1',
      patent_number: 'US-11948201-B2',
      title: 'Distributed Hardware-Accelerated Architecture for Quantum Computing',
      abstract: 'Systems and methods for accelerating quantum computations using dynamic tensor systolic arrays and memory-bandwidth pooling.',
      assignee: 'DeepScale Quantum Systems Inc.',
      filing_date: '2023-04-12',
      publication_date: '2025-08-19',
      cpc_classes: ['G06N 10/00', 'H04L 9/08'],
      status: 'granted',
      claims_count: 2,
      claims: [
        {
          id: 'cl-1',
          claim_number: 1,
          claim_type: 'independent',
          claim_text: 'A computing apparatus comprising: a plurality of tensor processing cores; an asynchronous crossbar fabric connecting said cores; and a control scheduler configured to allocate matrix tiles in response to sparsity metrics.',
          parsed_elements: [
            { element_id: 'limitation-1', element_text: 'a plurality of tensor processing cores', keywords: ['plurality', 'tensor', 'processing', 'cores'] },
            { element_id: 'limitation-2', element_text: 'an asynchronous crossbar fabric connecting said cores', keywords: ['asynchronous', 'crossbar', 'fabric', 'connecting'] },
            { element_id: 'limitation-3', element_text: 'a control scheduler configured to allocate matrix tiles in response to sparsity metrics', keywords: ['control', 'scheduler', 'allocate', 'matrix', 'tiles', 'sparsity'] },
          ],
        },
      ],
    },
    {
      id: 'p-2',
      patent_number: 'EP-3849102-A1',
      title: 'Error-Mitigated Parameter Optimization in Variational Quantum Circuits',
      abstract: 'A method for mitigating drift in quantum models using zero-noise extrapolation and adaptive Hamiltonian feedback.',
      assignee: 'European Quantum Labs SE',
      filing_date: '2024-01-15',
      publication_date: '2025-11-04',
      cpc_classes: ['G06N 10/00', 'G06N 99/00'],
      status: 'granted',
      claims_count: 1,
    },
  ],
  evaluations: [
    {
      id: 'eval-1',
      target_invention_claim: 'A quantum compiler comprising: an AST parser; a gate synthesis engine configured to map multi-angle QAOA Hamiltonians to 2D topological clusters; and a calibration feedback loop.',
      novelty_score: 0.88,
      obviousness_score: 0.18,
      overlap_ratio: 0.22,
      verdict: 'distinguishable',
      detailed_rationale: 'Target claim possesses distinct novel limitations not taught or suggested by the cited reference (specifically, the automated 2D topological cluster mapping).',
      mitigation_strategy: 'Claim scope is robust. Recommend filing dependent claims covering implementation details.',
      claim_chart: [
        { element_id: 'lim-1', target_limitation: 'an AST parser', status: 'anticipated', overlap_score: 0.85, matched_terms: ['parser', 'ast'] },
        { element_id: 'lim-2', target_limitation: 'a gate synthesis engine configured to map multi-angle QAOA Hamiltonians to 2D topological clusters', status: 'novel_distinction', overlap_score: 0.15, matched_terms: ['gate'] },
        { element_id: 'lim-3', target_limitation: 'a calibration feedback loop', status: 'obvious_variant', overlap_score: 0.55, matched_terms: ['feedback', 'loop'] },
      ],
      created_at: new Date().toISOString(),
    },
  ],
  fto_reports: [
    {
      id: 'fto-1',
      total_examined_patents: 3,
      high_risk_claims_count: 0,
      medium_risk_claims_count: 1,
      fto_clearance_percentage: 92.5,
      summary_assessment: 'High Freedom to Operate. Commercialization carries minimal litigation risk. The examined claim set is substantially distinguishable from active prior art.',
      white_space_opportunities: [
        {
          domain_subfield: 'Hybrid Multi-Modal Kernel Quantization',
          opportunity_description: 'Zero active patents covering 4-bit attention weight scheduling on edge heterogeneous NPUs.',
          patentability_index: 0.94,
        },
        {
          domain_subfield: 'Continuous Parameter Space Verification',
          opportunity_description: 'Unclaimed claim landscape in formal Lyapunov stability proofs for continuous-time neural ODEs.',
          patentability_index: 0.91,
        },
      ],
      created_at: new Date().toISOString(),
    },
  ],
};

export function PatentLandscapePage() {
  const [corpora, setCorpora] = useState<PatentCorpus[]>([SAMPLE_CORPUS]);
  const [selectedCorpus, setSelectedCorpus] = useState<PatentCorpus>(SAMPLE_CORPUS);
  const [metrics, setMetrics] = useState<PatentMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'patents' | 'chart' | 'fto'>('patents');

  // Claim Search State
  const [targetClaimText, setTargetClaimText] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  // New Corpus Modal
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDomain, setNewDomain] = useState('quantum_computing');
  const [newCPC, setNewCPC] = useState('G06N 10/00');
  const [newJurisdiction, setNewJurisdiction] = useState<PatentJurisdiction>('GLOBAL');

  const fetchCorpora = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/patents/corpora');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setCorpora(data);
          const detailRes = await fetch(`/api/v1/patents/corpora/${data[0].id}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            setSelectedCorpus(detailData);
          }
        }
      }
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/v1/patents/metrics');
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchCorpora();
    fetchMetrics();
  }, []);

  const handleSelectCorpus = async (corpusId: string) => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/patents/corpora/${corpusId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedCorpus(data);
      }
    } catch {
      const found = corpora.find((c) => c.id === corpusId);
      if (found) setSelectedCorpus(found);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetClaimText) return;

    try {
      setSearchLoading(true);
      const res = await fetch(`/api/v1/patents/corpora/${selectedCorpus.id}/evaluate-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_invention_claim: targetClaimText }),
      });
      if (res.ok) {
        const newEval = await res.json();
        setSelectedCorpus((prev) => ({
          ...prev,
          evaluations: [newEval, ...(prev.evaluations || [])],
        }));
        setTargetClaimText('');
        setActiveTab('chart');
      }
    } catch {
      // Ignore
    } finally {
      setSearchLoading(false);
    }
  };

  const handleCreateCorpus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;

    try {
      setLoading(true);
      const res = await fetch('/api/v1/patents/corpora', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          technology_domain: newDomain,
          cpc_classification: newCPC,
          jurisdiction: newJurisdiction,
        }),
      });
      if (res.ok) {
        setShowModal(false);
        setNewTitle('');
        await fetchCorpora();
      }
    } catch {
      setShowModal(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: 'var(--spacing-md)',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '1.75rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-sm)',
            }}
          >
            <Scale size={28} color="var(--color-primary)" />
            Autonomous Patent Landscape Analysis & Prior Art Search Engine
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
            35 U.S.C. 102/103 Novelty Claim Charts, Freedom-to-Operate (FTO) Clearance, and White-Space Discovery.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <button
            onClick={() => {
              fetchCorpora();
              fetchMetrics();
            }}
            className="button button-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="button button-primary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
          >
            <Plus size={16} />
            New Landscape Study
          </button>
        </div>
      </div>

      {/* KPI Stats Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'var(--spacing-md)',
        }}
      >
        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Landscape Corpora</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            {metrics?.total_patent_corpora ?? corpora.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Active IP Domains
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Total Patents Indexed</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10b981' }}>
            {metrics?.total_patents_indexed ?? (selectedCorpus.patents?.length || 0)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            USPTO, EPO & WIPO Assets
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Prior Art Evaluations</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#3b82f6' }}>
            {metrics?.total_prior_art_evaluations ?? (selectedCorpus.evaluations?.length || 0)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            102/103 Claim Charts
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>FTO Clearance Score</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#8b5cf6' }}>
            {selectedCorpus.fto_reports?.[0]?.fto_clearance_percentage
              ? `${selectedCorpus.fto_reports[0].fto_clearance_percentage}%`
              : '92.5%'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Litigation Risk: Low
          </div>
        </div>
      </div>

      {/* Main Studio Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 'var(--spacing-lg)' }}>
        {/* Left Sidebar: Studies List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Landscape Studies</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
            {corpora.map((c) => {
              const isSelected = c.id === selectedCorpus.id;
              return (
                <div
                  key={c.id}
                  onClick={() => handleSelectCorpus(c.id)}
                  style={{
                    padding: 'var(--spacing-md)',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    background: isSelected ? 'var(--color-primary)' + '10' : 'var(--color-surface)',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{c.title}</div>
                  <div
                    style={{
                      display: 'flex',
                      gap: 'var(--spacing-xs)',
                      marginTop: 'var(--spacing-xs)',
                      fontSize: '0.75rem',
                    }}
                  >
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        background: 'var(--color-primary)' + '20',
                        color: 'var(--color-primary)',
                      }}
                    >
                      {c.jurisdiction}
                    </span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        background: '#10b98120',
                        color: '#10b981',
                      }}
                    >
                      {c.cpc_classification}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Stage: Patents, 102/103 Claim Charts, and FTO Clearance */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {/* Active Study Header */}
          <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>{selectedCorpus.title}</h2>
                <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-xs)' }}>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>CPC Class:</strong> {selectedCorpus.cpc_classification}
                  </span>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>Jurisdiction:</strong> {selectedCorpus.jurisdiction}
                  </span>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>FTO Verdict:</strong>{' '}
                    <span
                      style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: selectedCorpus.freedom_to_operate_verdict === 'clear' ? '#10b98120' : '#f59e0b20',
                        color: selectedCorpus.freedom_to_operate_verdict === 'clear' ? '#10b981' : '#f59e0b',
                        fontWeight: 600,
                      }}
                    >
                      {selectedCorpus.freedom_to_operate_verdict.toUpperCase()}
                    </span>
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                <button
                  onClick={() => setActiveTab('patents')}
                  className={`button ${activeTab === 'patents' ? 'button-primary' : 'button-secondary'}`}
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  <Layers size={16} />
                  Patents ({selectedCorpus.patents?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('chart')}
                  className={`button ${activeTab === 'chart' ? 'button-primary' : 'button-secondary'}`}
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  <Scale size={16} />
                  102/103 Claim Charts
                </button>
                <button
                  onClick={() => setActiveTab('fto')}
                  className={`button ${activeTab === 'fto' ? 'button-primary' : 'button-secondary'}`}
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  <ShieldCheck size={16} />
                  FTO & White Space
                </button>
              </div>
            </div>
          </div>

          {/* Tab 1: Patent Specifications Catalog */}
          {activeTab === 'patents' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {selectedCorpus.patents && selectedCorpus.patents.length > 0 ? (
                selectedCorpus.patents.map((pat) => (
                  <div key={pat.id} className="card" style={{ padding: 'var(--spacing-lg)' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 'var(--spacing-xs)',
                      }}
                    >
                      <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>{pat.patent_number}</span>
                        <span
                          style={{
                            padding: '2px 8px',
                            borderRadius: '10px',
                            fontSize: '0.75rem',
                            background: '#10b98120',
                            color: '#10b981',
                            fontWeight: 600,
                          }}
                        >
                          {pat.status.toUpperCase()}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                        Published: {pat.publication_date || '2025-08-19'}
                      </span>
                    </div>

                    <h4 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '4px' }}>{pat.title}</h4>
                    <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-sm)' }}>
                      Assignee: <strong>{pat.assignee}</strong>
                    </div>

                    <p style={{ fontSize: '0.9rem', color: 'var(--color-text)', marginBottom: 'var(--spacing-sm)' }}>
                      {pat.abstract}
                    </p>

                    {/* CPC Class Tags */}
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                      {pat.cpc_classes.map((cls) => (
                        <span
                          key={cls}
                          style={{
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'var(--color-background)',
                            fontSize: '0.75rem',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          {cls}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="card" style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--color-text-secondary)' }}>No patents indexed for this corpus yet.</p>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: 35 U.S.C. 102/103 Claim Charts */}
          {activeTab === 'chart' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {/* Claim Evaluation Input Card */}
              <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
                  Prior Art Search & Claim Chart Generator
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-sm)' }}>
                  Enter an independent or target invention claim to decompose into atomic limitations and evaluate anticipation (102) vs. non-obviousness (103).
                </p>

                <form onSubmit={handleEvaluateClaim} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                  <textarea
                    rows={3}
                    required
                    placeholder="e.g., A quantum compiling system comprising: an AST parser; a gate synthesis engine configured to map Hamiltonians to 2D topological clusters; and a calibration feedback loop."
                    value={targetClaimText}
                    onChange={(e) => setTargetClaimText(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-background)',
                      color: 'var(--color-text)',
                      fontFamily: 'inherit',
                      fontSize: '0.9rem',
                    }}
                  />

                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      type="submit"
                      disabled={searchLoading}
                      className="button button-primary"
                      style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                      {searchLoading ? <Loader2 size={16} className="spinning" /> : <Search size={16} />}
                      Evaluate Claim
                    </button>
                  </div>
                </form>
              </div>

              {/* Historical Evaluations */}
              {selectedCorpus.evaluations && selectedCorpus.evaluations.length > 0 ? (
                selectedCorpus.evaluations.map((ev) => (
                  <div key={ev.id} className="card" style={{ padding: 'var(--spacing-lg)' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 'var(--spacing-sm)',
                      }}
                    >
                      <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
                        <span
                          style={{
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: 700,
                            background:
                              ev.verdict === 'distinguishable' || ev.verdict === 'non_infringing'
                                ? '#10b98120'
                                : '#ef444420',
                            color:
                              ev.verdict === 'distinguishable' || ev.verdict === 'non_infringing'
                                ? '#10b981'
                                : '#ef4444',
                          }}
                        >
                          {ev.verdict.toUpperCase().replace('_', ' ')}
                        </span>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                          Novelty: {(ev.novelty_score * 100).toFixed(0)}% | Overlap: {(ev.overlap_ratio * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                        TARGET INVENTION CLAIM
                      </div>
                      <div
                        style={{
                          padding: 'var(--spacing-sm)',
                          background: 'var(--color-background)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.9rem',
                          marginTop: '4px',
                        }}
                      >
                        {ev.target_invention_claim}
                      </div>
                    </div>

                    {/* Claim Chart Limitations Breakdown */}
                    {ev.claim_chart && ev.claim_chart.length > 0 && (
                      <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-primary)', marginBottom: '6px' }}>
                          LIMITATION-BY-LIMITATION CLAIM CHART
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {ev.claim_chart.map((elem) => (
                            <div
                              key={elem.element_id}
                              style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '8px 12px',
                                background: 'var(--color-background)',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '0.85rem',
                              }}
                            >
                              <span>{elem.target_limitation}</span>
                              <span
                                style={{
                                  padding: '2px 8px',
                                  borderRadius: '6px',
                                  fontSize: '0.75rem',
                                  fontWeight: 600,
                                  background:
                                    elem.status === 'novel_distinction'
                                      ? '#10b98120'
                                      : elem.status === 'obvious_variant'
                                      ? '#f59e0b20'
                                      : '#ef444420',
                                  color:
                                    elem.status === 'novel_distinction'
                                      ? '#10b981'
                                      : elem.status === 'obvious_variant'
                                      ? '#f59e0b'
                                      : '#ef4444',
                                }}
                              >
                                {elem.status.replace('_', ' ')}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                      <strong>Rationale:</strong> {ev.detailed_rationale}
                    </p>
                    {ev.mitigation_strategy && (
                      <p style={{ fontSize: '0.85rem', color: '#10b981', marginTop: '4px' }}>
                        <strong>Design-Around Strategy:</strong> {ev.mitigation_strategy}
                      </p>
                    )}
                  </div>
                ))
              ) : null}
            </div>
          )}

          {/* Tab 3: FTO & White-Space Innovation Opportunities */}
          {activeTab === 'fto' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {selectedCorpus.fto_reports && selectedCorpus.fto_reports.length > 0 ? (
                selectedCorpus.fto_reports.map((fto) => (
                  <div key={fto.id} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                    {/* Clearance Assessment */}
                    <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
                        Freedom to Operate Clearance
                      </h3>
                      <p style={{ fontSize: '0.9rem', color: 'var(--color-text)' }}>{fto.summary_assessment}</p>
                    </div>

                    {/* White-Space Opportunities */}
                    <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
                      <h3
                        style={{
                          fontSize: '1.15rem',
                          fontWeight: 600,
                          marginBottom: 'var(--spacing-md)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 'var(--spacing-xs)',
                        }}
                      >
                        <Lightbulb size={20} color="#f59e0b" />
                        White-Space Innovation Opportunities
                      </h3>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                        {fto.white_space_opportunities.map((ws, i) => (
                          <div
                            key={i}
                            style={{
                              padding: 'var(--spacing-md)',
                              background: 'var(--color-background)',
                              borderRadius: 'var(--radius-md)',
                              border: '1px solid var(--color-border)',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-primary)' }}>
                                {ws.domain_subfield}
                              </h4>
                              <span
                                style={{
                                  padding: '2px 6px',
                                  borderRadius: '8px',
                                  fontSize: '0.75rem',
                                  background: '#10b98120',
                                  color: '#10b981',
                                  fontWeight: 600,
                                }}
                              >
                                Patentability: {(ws.patentability_index * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: '6px' }}>
                              {ws.opportunity_description}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="card" style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--color-text-secondary)' }}>No FTO report available for this corpus.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* New Study Modal */}
      {showModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div
            className="card"
            style={{
              width: '520px',
              padding: 'var(--spacing-xl)',
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
            }}
          >
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 'var(--spacing-md)' }}>
              Create Patent Landscape Study
            </h2>

            <form onSubmit={handleCreateCorpus} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Study Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Quantum Memory Architectures"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-sm)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border)',
                    background: 'var(--color-background)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--spacing-md)' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Technology Domain
                  </label>
                  <input
                    type="text"
                    value={newDomain}
                    onChange={(e) => setNewDomain(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-background)',
                      color: 'var(--color-text)',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    CPC Classification
                  </label>
                  <input
                    type="text"
                    value={newCPC}
                    onChange={(e) => setNewCPC(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-background)',
                      color: 'var(--color-text)',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Jurisdiction
                  </label>
                  <select
                    value={newJurisdiction}
                    onChange={(e) => setNewJurisdiction(e.target.value as PatentJurisdiction)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-background)',
                      color: 'var(--color-text)',
                    }}
                  >
                    <option value="GLOBAL">Global (USPTO/EPO/WIPO)</option>
                    <option value="USPTO">USPTO (United States)</option>
                    <option value="EPO">EPO (Europe)</option>
                    <option value="WIPO">WIPO (International)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="button button-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="button button-primary"
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  {loading && <Loader2 size={16} className="spinning" />}
                  Create & Index Study
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
export default PatentLandscapePage;
