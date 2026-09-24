import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Dna, Activity } from 'lucide-react';

export const RNAThermodynamicsStudioPage: React.FC = () => {
  const [rnaName, setRnaName] = useState('SAM-I_Riboswitch_Aptamer');
  const [sequence, setSequence] = useState('GGGAUCGCAGUCUCGAGAGUUGCCAAACCAGCAGCAGCGCUCCUUCUGCGAGAUCCC');
  const [temperature, setTemperature] = useState(37.0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleFold = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/rna-thermodynamics/fold', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          rna_name: rnaName,
          sequence: sequence,
          temperature_celsius: temperature
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
        <Dna size={32} color="#a855f7" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            RNA Secondary Structure & Thermodynamics Studio
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 163: Turner 2004 Nearest-Neighbor MFE Secondary Structure & Melting Kinetics Simulator
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>RNA Sequence Parameters</h2>
          <form onSubmit={handleFold} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Aptamer / RNA Name</label>
              <input
                type="text"
                value={rnaName}
                onChange={(e) => setRnaName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>RNA Sequence (5' to 3')</label>
              <textarea
                value={sequence}
                onChange={(e) => setSequence(e.target.value)}
                rows={3}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff', fontFamily: 'monospace' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Folding Temperature (°C)</label>
              <input
                type="number"
                step="0.5"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
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
                background: '#a855f7',
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
              Compute MFE & Thermodynamic Profile
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>MFE Free Energy ΔG</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#c084fc' }}>{result.mfe_delta_g_kcal_mol} kcal/mol</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Melting Temperature Tm</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.melting_temperature_tm_celsius}°C</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Ensemble Defect</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>{result.ensemble_defect}</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.5rem', fontSize: '1.1rem' }}>Dot-Bracket Structure</h3>
                <div style={{ fontFamily: 'monospace', background: '#0f172a', padding: '0.75rem', borderRadius: '6px', color: '#38bdf8', letterSpacing: '2px', wordBreak: 'break-all' }}>
                  {result.dot_bracket_structure}
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Recommendations & Stability Analysis</h3>
                <ul style={{ paddingLeft: '1.25rem', margin: 0, color: '#cbd5e1' }}>
                  {result.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '12px', textAlign: 'center', color: '#64748b' }}>
              <Dna size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Enter RNA sequence to calculate thermodynamic partition function and MFE secondary structure</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RNAThermodynamicsStudioPage;
