import React, { useState, useEffect, useMemo } from 'react';
import {
  Database,
  Plus,
  Download,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Sliders,
  FileCode,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import {
  SyntheticDataset,
  DatasetSynthesisMetrics,
  DatasetFormat,
} from '../types/datasetSynthesis';

const SAMPLE_DATASET: SyntheticDataset = {
  id: 'ds-1',
  name: 'Quantum Fault-Tolerance Instruction Corpus',
  description: 'Synthesized high-entropy SFT and DPO alignment dataset derived from multi-agent quantum computing dossiers.',
  dataset_format: 'dpo_preference',
  domain_field: 'quantum_physics',
  target_model_family: 'llama_3_70b',
  total_samples: 4,
  quality_filter_threshold: 0.85,
  status: 'curated',
  created_at: new Date().toISOString(),
  samples: [
    {
      id: 'sample-1',
      sample_index: 1,
      instruction: 'Derive the asymptotic fault-tolerance threshold for surface codes under non-Markovian phase noise.',
      input_context: 'Topic: Quantum Error Mitigation | Dossier: QAOA Benchmarks',
      chosen_response: '### Formal Derivation of Fault-Tolerance Threshold\n\nUnder non-Markovian noise correlation length $\\xi$, the effective error rate $\\epsilon_{\\text{eff}}$ satisfies:\n$$\\epsilon_{\\text{eff}} \\le p_{\\text{th}} \\left(1 - e^{-t/\\tau}\\right)$$\n\nApplying topological subsystem code decoding, the physical threshold asymptotes to $p_{\\text{th}} \\approx 0.94\\%$ with $O(N)$ matching complexity.',
      rejected_response: 'Surface codes usually have a 1% threshold, but non-Markovian noise makes it difficult without specific numbers.',
      cot_reasoning_trace: 'Step 1: Formalize non-Markovian noise kernel.\nStep 2: Map to 2D topological stabilizer lattice.\nStep 3: Calculate minimum-weight perfect matching bound.',
      evolution_strategy: 'in_depth_expansion',
      quality_score: 0.96,
      toxicity_score: 0.01,
      hallucination_risk: 0.02,
      curation_verdict: 'accepted',
    },
    {
      id: 'sample-2',
      sample_index: 2,
      instruction: 'Identify the critical security vulnerability or out-of-distribution failure mode in variational quantum circuit gradient estimation.',
      input_context: 'Topic: Variational Quantum Algorithms',
      chosen_response: '**Barren Plateau Threat Model:**\n\nRandomly initialized parameter vectors in Hilbert spaces of dimension $2^N$ suffer from exponentially vanishing gradient variance:\n$$\\text{Var}[\\nabla E] \\in \\mathcal{O}(2^{-N})$$\n\n**Defensive Countermeasure:** Enforce layer-by-layer pre-training and local Hamiltonian observables.',
      rejected_response: 'Gradients get small when the quantum circuit is deep. You just need to run more shots.',
      cot_reasoning_trace: 'Step 1: Formulate adversarial expressibility landscape.\nStep 2: Derive variance bound under Haar measure.\nStep 3: Prescribe mitigation protocol.',
      evolution_strategy: 'adversarial_redteaming',
      quality_score: 0.94,
      toxicity_score: 0.01,
      hallucination_risk: 0.03,
      curation_verdict: 'accepted',
    },
  ],
};

export function DatasetSynthesisPage() {
  const [datasets, setDatasets] = useState<SyntheticDataset[]>([SAMPLE_DATASET]);
  const [selectedDataset, setSelectedDataset] = useState<SyntheticDataset>(SAMPLE_DATASET);
  const [metrics, setMetrics] = useState<DatasetSynthesisMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'samples' | 'export' | 'evolution'>('samples');

  // Modal State
  const [showSynthesizeModal, setShowSynthesizeModal] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState('');
  const [newTopic, setNewTopic] = useState('');
  const [newFormat, setNewFormat] = useState<DatasetFormat>('alpaca_sft');
  const [newSampleCount, setNewSampleCount] = useState(5);
  const [newTargetModel, setNewTargetModel] = useState('llama_3');

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/datasets');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setDatasets(data);
          // Fetch full detail of first
          const detailRes = await fetch(`/api/v1/datasets/${data[0].id}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            setSelectedDataset(detailData);
          }
        }
      }
    } catch {
      // Use fallback
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/v1/datasets/metrics');
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchDatasets();
    fetchMetrics();
  }, []);

  const handleSelectDataset = async (datasetId: string) => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/datasets/${datasetId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedDataset(data);
      }
    } catch {
      const found = datasets.find((d) => d.id === datasetId);
      if (found) setSelectedDataset(found);
    } finally {
      setLoading(false);
    }
  };

  const handleCuration = async (sampleId: string, verdict: 'accepted' | 'rejected') => {
    try {
      await fetch(`/api/v1/datasets/${selectedDataset.id}/samples/${sampleId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verdict }),
      });

      // Update local state
      setSelectedDataset((prev) => ({
        ...prev,
        samples: prev.samples?.map((s) => (s.id === sampleId ? { ...s, curation_verdict: verdict } : s)),
      }));
    } catch {
      // Local fallback
      setSelectedDataset((prev) => ({
        ...prev,
        samples: prev.samples?.map((s) => (s.id === sampleId ? { ...s, curation_verdict: verdict } : s)),
      }));
    }
  };

  const handleCreateDataset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDatasetName || !newTopic) return;

    try {
      setLoading(true);
      const res = await fetch('/api/v1/datasets/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newDatasetName,
          topic: newTopic,
          dataset_format: newFormat,
          sample_count: newSampleCount,
          target_model_family: newTargetModel,
        }),
      });
      if (res.ok) {
        setShowSynthesizeModal(false);
        setNewDatasetName('');
        setNewTopic('');
        await fetchDatasets();
      }
    } catch {
      setShowSynthesizeModal(false);
    } finally {
      setLoading(false);
    }
  };

  const exportPayloadPreview = useMemo(() => {
    if (!selectedDataset.samples) return '';
    const formatted = selectedDataset.samples
      .filter((s) => s.curation_verdict !== 'rejected')
      .map((s) => {
        if (selectedDataset.dataset_format === 'alpaca_sft') {
          return { instruction: s.instruction, input: s.input_context || '', output: s.chosen_response };
        } else if (selectedDataset.dataset_format === 'dpo_preference') {
          return { prompt: s.instruction, chosen: s.chosen_response, rejected: s.rejected_response || '' };
        } else if (selectedDataset.dataset_format === 'cot_reasoning') {
          return { instruction: s.instruction, thought: s.cot_reasoning_trace || '', solution: s.chosen_response };
        }
        return { instruction: s.instruction, response: s.chosen_response };
      });

    return formatted.map((item) => JSON.stringify(item)).join('\n');
  }, [selectedDataset]);

  const handleCopyExport = () => {
    navigator.clipboard.writeText(exportPayloadPreview);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSONL = () => {
    const blob = new Blob([exportPayloadPreview], { type: 'application/jsonl' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedDataset.name.toLowerCase().replace(/\s+/g, '_')}_${selectedDataset.dataset_format}.jsonl`;
    a.click();
    URL.revokeObjectURL(url);
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
            <Database size={28} color="var(--color-primary)" />
            Synthetic Instruction Dataset & Active Learning Engine
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
            Evol-Instruct Multi-Turn Synthesis, DPO Preference Pairs, Active Learning Curation, and Alignment Exports.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <button
            onClick={() => {
              fetchDatasets();
              fetchMetrics();
            }}
            className="button button-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
          <button
            onClick={() => setShowSynthesizeModal(true)}
            className="button button-primary"
            style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
          >
            <Plus size={16} />
            Synthesize Dataset
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
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Total Synthesized Datasets</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            {metrics?.total_synthetic_datasets ?? datasets.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Production Alignment Repositories
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Total Instruction Samples</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10b981' }}>
            {metrics?.total_instruction_samples ?? (selectedDataset.samples?.length || 0)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            High-Entropy Synthesized Prompts
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Average Quality Score</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#3b82f6' }}>
            {metrics?.average_quality_score ? (metrics.average_quality_score * 100).toFixed(1) + '%' : '95.2%'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Multi-Heuristic Quality Standard
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-md)' }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>Alignment Exports</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#8b5cf6' }}>
            {metrics?.total_alignment_exports ?? 3}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
            Standardized JSONL Artifacts
          </div>
        </div>
      </div>

      {/* Main Studio Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 'var(--spacing-lg)' }}>
        {/* Left Sidebar: Dataset Catalog */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Dataset Catalog</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
            {datasets.map((d) => {
              const isSelected = d.id === selectedDataset.id;
              return (
                <div
                  key={d.id}
                  onClick={() => handleSelectDataset(d.id)}
                  style={{
                    padding: 'var(--spacing-md)',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    background: isSelected ? 'var(--color-primary)' + '10' : 'var(--color-surface)',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{d.name}</div>
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
                      {d.dataset_format}
                    </span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        background: '#10b98120',
                        color: '#10b981',
                      }}
                    >
                      {d.total_samples} samples
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Stage: Inspector, Active Curation, and Alignment Exporter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {/* Active Dataset Header */}
          <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>{selectedDataset.name}</h2>
                <p style={{ color: 'var(--color-text-secondary)', marginTop: '4px', fontSize: '0.9rem' }}>
                  {selectedDataset.description}
                </p>
                <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-sm)' }}>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>Format:</strong> {selectedDataset.dataset_format}
                  </span>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>Target Model:</strong> {selectedDataset.target_model_family}
                  </span>
                  <span style={{ fontSize: '0.85rem' }}>
                    <strong>Domain:</strong> {selectedDataset.domain_field}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                <button
                  onClick={() => setActiveTab('samples')}
                  className={`button ${activeTab === 'samples' ? 'button-primary' : 'button-secondary'}`}
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  <Sliders size={16} />
                  Curation ({selectedDataset.samples?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('export')}
                  className={`button ${activeTab === 'export' ? 'button-primary' : 'button-secondary'}`}
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                  <FileCode size={16} />
                  Alignment Export
                </button>
              </div>
            </div>
          </div>

          {/* Tab 1: Instruction Samples & Active Learning Curation */}
          {activeTab === 'samples' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {selectedDataset.samples && selectedDataset.samples.length > 0 ? (
                selectedDataset.samples.map((sample) => (
                  <div
                    key={sample.id}
                    className="card"
                    style={{
                      padding: 'var(--spacing-lg)',
                      borderLeft: `4px solid ${sample.curation_verdict === 'accepted' ? '#10b981' : sample.curation_verdict === 'rejected' ? '#ef4444' : '#f59e0b'}`,
                    }}
                  >
                    {/* Sample Top Meta */}
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
                            fontWeight: 700,
                            fontSize: '0.85rem',
                            color: 'var(--color-primary)',
                          }}
                        >
                          Sample #{sample.sample_index}
                        </span>
                        <span
                          style={{
                            padding: '2px 8px',
                            borderRadius: '10px',
                            fontSize: '0.75rem',
                            background: '#8b5cf620',
                            color: '#8b5cf6',
                            fontWeight: 600,
                          }}
                        >
                          Strategy: {sample.evolution_strategy}
                        </span>
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
                          Quality: {(sample.quality_score * 100).toFixed(0)}%
                        </span>
                      </div>

                      {/* Active Learning Curation Controls */}
                      <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                        <button
                          onClick={() => handleCuration(sample.id, 'accepted')}
                          className="button"
                          style={{
                            padding: '4px 10px',
                            fontSize: '0.8rem',
                            background: sample.curation_verdict === 'accepted' ? '#10b981' : 'transparent',
                            color: sample.curation_verdict === 'accepted' ? '#fff' : 'var(--color-text)',
                            border: '1px solid #10b981',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          <CheckCircle2 size={14} /> Accept
                        </button>
                        <button
                          onClick={() => handleCuration(sample.id, 'rejected')}
                          className="button"
                          style={{
                            padding: '4px 10px',
                            fontSize: '0.8rem',
                            background: sample.curation_verdict === 'rejected' ? '#ef4444' : 'transparent',
                            color: sample.curation_verdict === 'rejected' ? '#fff' : 'var(--color-text)',
                            border: '1px solid #ef4444',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          <XCircle size={14} /> Reject
                        </button>
                      </div>
                    </div>

                    {/* Instruction */}
                    <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                      <div
                        style={{
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          color: 'var(--color-text-secondary)',
                          marginBottom: '4px',
                        }}
                      >
                        INSTRUCTION
                      </div>
                      <div
                        style={{
                          padding: 'var(--spacing-sm)',
                          background: 'var(--color-background)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.95rem',
                          fontWeight: 500,
                        }}
                      >
                        {sample.instruction}
                      </div>
                    </div>

                    {/* CoT Reasoning Trace (if present) */}
                    {sample.cot_reasoning_trace && (
                      <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                        <div
                          style={{
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            color: '#8b5cf6',
                            marginBottom: '4px',
                          }}
                        >
                          CHAIN-OF-THOUGHT REASONING TRACE
                        </div>
                        <pre
                          style={{
                            padding: 'var(--spacing-sm)',
                            background: '#8b5cf610',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.85rem',
                            fontFamily: 'monospace',
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {sample.cot_reasoning_trace}
                        </pre>
                      </div>
                    )}

                    {/* Chosen Response vs Rejected (DPO) */}
                    <div>
                      <div
                        style={{
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          color: '#10b981',
                          marginBottom: '4px',
                        }}
                      >
                        CHOSEN GROUND-TRUTH RESPONSE
                      </div>
                      <div
                        style={{
                          padding: 'var(--spacing-sm)',
                          background: 'var(--color-background)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.9rem',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {sample.chosen_response}
                      </div>
                    </div>

                    {sample.rejected_response && (
                      <div style={{ marginTop: 'var(--spacing-sm)' }}>
                        <div
                          style={{
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            color: '#ef4444',
                            marginBottom: '4px',
                          }}
                        >
                          REJECTED CANDIDATE (DPO PAIR)
                        </div>
                        <div
                          style={{
                            padding: 'var(--spacing-sm)',
                            background: '#ef444410',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.9rem',
                            color: 'var(--color-text-secondary)',
                          }}
                        >
                          {sample.rejected_response}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="card" style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--color-text-secondary)' }}>No instruction samples found for this dataset.</p>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Alignment Export */}
          {activeTab === 'export' && (
            <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 'var(--spacing-md)',
                }}
              >
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Standardized Alignment Export (JSONL)</h3>
                  <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem' }}>
                    Fine-tuning ready dataset formatted for HuggingFace, Unsloth, Axolotl, and LLaMA-Factory.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                  <button
                    onClick={handleCopyExport}
                    className="button button-secondary"
                    style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                  >
                    {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
                    {copied ? 'Copied!' : 'Copy JSONL'}
                  </button>
                  <button
                    onClick={handleDownloadJSONL}
                    className="button button-primary"
                    style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                  >
                    <Download size={16} />
                    Download .jsonl
                  </button>
                </div>
              </div>

              <pre
                style={{
                  padding: 'var(--spacing-md)',
                  background: 'var(--color-background)',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  maxHeight: '400px',
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  border: '1px solid var(--color-border)',
                }}
              >
                {exportPayloadPreview || 'No samples available to export.'}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Synthesize Dataset Modal */}
      {showSynthesizeModal && (
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
              width: '540px',
              padding: 'var(--spacing-xl)',
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
            }}
          >
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 'var(--spacing-md)' }}>
              Synthesize Instruction Tuning Dataset
            </h2>

            <form onSubmit={handleCreateDataset} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Dataset Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Quantum Circuit Instruction Corpus"
                  value={newDatasetName}
                  onChange={(e) => setNewDatasetName(e.target.value)}
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
                  Research Topic / Inquiry
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Quantum Error Mitigation & Super-polynomial sampling"
                  value={newTopic}
                  onChange={(e) => setNewTopic(e.target.value)}
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
                    Alignment Format
                  </label>
                  <select
                    value={newFormat}
                    onChange={(e) => setNewFormat(e.target.value as DatasetFormat)}
                    style={{
                      width: '100%',
                      padding: 'var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border)',
                      background: 'var(--color-background)',
                      color: 'var(--color-text)',
                    }}
                  >
                    <option value="alpaca_sft">Alpaca SFT</option>
                    <option value="sharegpt">ShareGPT Multi-Turn</option>
                    <option value="dpo_preference">DPO Preference Pairs</option>
                    <option value="cot_reasoning">Chain-of-Thought (CoT)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Target Model
                  </label>
                  <input
                    type="text"
                    value={newTargetModel}
                    onChange={(e) => setNewTargetModel(e.target.value)}
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
                    Sample Count
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={newSampleCount}
                    onChange={(e) => setNewSampleCount(parseInt(e.target.value, 10))}
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
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                <button
                  type="button"
                  onClick={() => setShowSynthesizeModal(false)}
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
                  Synthesize Dataset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
export default DatasetSynthesisPage;
