import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Network, GitPullRequest } from 'lucide-react';

export const SingleCellPerturbationStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('K562_CRISPRi_Kinome_Screen');
  const [modality, setModality] = useState('CRISPRi-PerturbSeq');
  const [targets, setTargets] = useState('MYC, TP53, STAT3, CDK4');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleScreen = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const targetList = targets.split(',').map(s => s.trim()).filter(Boolean);
      const res = await fetch('/api/v1/single-cell-perturbation/screen', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          study_name: studyName,
          modality: modality,
          target_genes: targetList
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data.result);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <Network size={32} color="#ec4899" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            Single-Cell Perturbation & Causal GRN Inversion Studio
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 167: Perturb-seq CRISPRi/a Single-Cell Transcriptomic State Bifurcation & Causal Gene Regulatory Network Inversion
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>Perturb-seq Configuration</h2>
          <form onSubmit={handleScreen} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Study Identifier</label>
              <input
                type="text"
                value={studyName}
                onChange={(e) => setStudyName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Perturbation Modality</label>
              <select
                value={modality}
                onChange={(e) => setModality(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              >
                <option value="CRISPRi-PerturbSeq">CRISPRi-PerturbSeq (Knockdown)</option>
                <option value="CRISPRa-PerturbSeq">CRISPRa-PerturbSeq (Activation)</option>
                <option value="BaseEditing-PerturbSeq">BaseEditing-PerturbSeq (Precise Point Variant)</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Target Genes (Comma-separated)</label>
              <input
                type="text"
                value={targets}
                onChange={(e) => setTargets(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                background: '#ec4899',
                color: '#fff',
                padding: '0.75rem',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: 600,
                marginTop: '0.5rem'
              }}
            >
              {loading ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
              Invert Causal GRN
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Profiled Single Cells</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f472b6' }}>{result.total_cells.toLocaleString()}</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Energy Distance Shift</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.e_distance}</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Network Density</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>{result.network_density}</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Inverted Causal Regulatory Edges</h3>
                {result.grn_edges.map((edge: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < result.grn_edges.length - 1 ? '1px solid #334155' : 'none' }}>
                    <span style={{ fontWeight: 600, color: '#f8fafc' }}>{edge.source} → {edge.target}</span> ({edge.sign})
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      Causal β: {edge.beta} | FDR: {edge.fdr.toExponential(2)}
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Recommendations</h3>
                <ul style={{ paddingLeft: '1.25rem', margin: 0, color: '#cbd5e1' }}>
                  {result.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '12px', textAlign: 'center', color: '#64748b' }}>
              <Network size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Configure single-cell perturbation targets to reconstruct causal gene regulatory circuits</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SingleCellPerturbationStudioPage;
