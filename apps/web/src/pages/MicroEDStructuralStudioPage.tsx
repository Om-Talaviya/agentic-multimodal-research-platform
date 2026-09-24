import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Eye, Sparkles } from 'lucide-react';

export const MicroEDStructuralStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('Bovine Trypsin');
  const [voltage, setVoltage] = useState(200.0);
  const [rotationRange, setRotationRange] = useState(120.0);
  const [framesCount, setFramesCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleRefine = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/microed-structural/refine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          sample_name: sampleName,
          voltage_kv: voltage,
          rotation_range_deg: rotationRange,
          frames_count: framesCount
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
        <Sparkles size={32} color="#06b6d4" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            MicroED Sub-Ångström Structural Refinement Studio
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 166: Continuous Rotation Electron Diffraction & Electrostatic Potential Map Refinement
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>Microcrystal Parameters</h2>
          <form onSubmit={handleRefine} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Protein / Peptide Sample</label>
              <input
                type="text"
                value={sampleName}
                onChange={(e) => setSampleName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Beam Voltage (kV)</label>
                <input
                  type="number"
                  value={voltage}
                  onChange={(e) => setVoltage(parseFloat(e.target.value))}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Rotation Arc (°)</label>
                <input
                  type="number"
                  value={rotationRange}
                  onChange={(e) => setRotationRange(parseFloat(e.target.value))}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                />
              </div>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Diffraction Frames Sampled</label>
              <input
                type="number"
                value={framesCount}
                onChange={(e) => setFramesCount(parseInt(e.target.value))}
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
                background: '#06b6d4',
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
              Simulate MicroED & Refine
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Resolution Limit</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.resolution_angstrom} Å</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Completeness</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>{result.completeness_percent}%</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>R-work / R-free</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#facc15' }}>{result.r_work} / {result.r_free}</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Diffraction Rotation Frames</h3>
                {result.frames.map((fr: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < result.frames.length - 1 ? '1px solid #334155' : 'none' }}>
                    <span style={{ fontWeight: 600, color: '#f8fafc' }}>Frame #{fr.frame_number} (Tilt {fr.tilt_angle_deg}°)</span>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      Reflections: {fr.reflections_count} | ⟨I/σ⟩: {fr.i_over_sigma}
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
              <Eye size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Configure rotation series and voltage to solve sub-micron protein crystal structures</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MicroEDStructuralStudioPage;
