import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Scissors, ShieldAlert } from 'lucide-react';

export const CRISPRBaseEditorStudioPage: React.FC = () => {
  const [gene, setGene] = useState('PCSK9');
  const [protospacer, setProtospacer] = useState('GAACACCCAGAGCCCGGACG');
  const [editorType, setEditorType] = useState('ABE8e');
  const [pam, setPam] = useState('NGG');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/crispr-base-editor/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          target_gene: gene,
          protospacer_sequence: protospacer,
          editor_type: editorType,
          pam: pam
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
        <Scissors size={32} color="#f43f5e" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            CRISPR Base Editing & Bystander Mutation Predictor
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 164: Adenine & Cytosine Deaminase Editing Window, Transition Efficiency & Bystander Risk Forecaster
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>Guide & Editor Parameters</h2>
          <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Target Gene Symbol</label>
              <input
                type="text"
                value={gene}
                onChange={(e) => setGene(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Protospacer (20nt)</label>
              <input
                type="text"
                value={protospacer}
                onChange={(e) => setProtospacer(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff', fontFamily: 'monospace' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Editor Architecture</label>
                <select
                  value={editorType}
                  onChange={(e) => setEditorType(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                >
                  <option value="ABE8e">ABE8e (A-to-G)</option>
                  <option value="BE4max">BE4max (C-to-T)</option>
                  <option value="evoCDA-narrow">evoCDA-narrow</option>
                  <option value="Dual-ABE/CBE">Dual-ABE/CBE</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>PAM Motif</label>
                <input
                  type="text"
                  value={pam}
                  onChange={(e) => setPam(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                background: '#f43f5e',
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
              Predict Conversion & Bystander Risk
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>On-Target Efficiency</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>
                    {Math.round(result.on_target_efficiency * 100)}%
                  </div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Bystander Purity Score</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.bystander_purity_score}</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Indel Risk</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#facc15' }}>{result.indel_frequency_percent}%</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Predicted Base Transitions</h3>
                {result.transitions.map((t: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < result.transitions.length - 1 ? '1px solid #334155' : 'none' }}>
                    <span style={{ color: '#f43f5e', fontWeight: 700 }}>Position {t.position}: {t.initial_base} → {t.target_base}</span> ({Math.round(t.efficiency * 100)}% efficiency)
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>{t.consequence}</div>
                  </div>
                ))}
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Mitigation & Optimization Recommendations</h3>
                <ul style={{ paddingLeft: '1.25rem', margin: 0, color: '#cbd5e1' }}>
                  {result.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '12px', textAlign: 'center', color: '#64748b' }}>
              <Scissors size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Configure protospacer and deaminase architecture to predict single-nucleotide transition purity</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CRISPRBaseEditorStudioPage;
