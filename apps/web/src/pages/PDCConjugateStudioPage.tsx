import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Activity, ShieldCheck } from 'lucide-react';

export const PDCConjugateStudioPage: React.FC = () => {
  const [pdcName, setPdcName] = useState('cRGD-ValCit-MMAE');
  const [peptide, setPeptide] = useState('cyclo(RGDfK)');
  const [linker, setLinker] = useState('Val-Cit-PABC');
  const [payload, setPayload] = useState('Monomethyl Auristatin E (MMAE)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/pdc-conjugate/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          pdc_name: pdcName,
          homing_peptide_sequence: peptide,
          linker_type: linker,
          cytotoxic_payload: payload
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
        <ShieldCheck size={32} color="#10b981" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            Peptide-Drug Conjugate (PDC) Linker Cleavability Studio
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 165: Cathepsin-B Cleavage Kinetics, Systemic Plasma Stability & Tumor Selectivity Forecaster
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>PDC Design Parameters</h2>
          <form onSubmit={handleEvaluate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>PDC Construct Name</label>
              <input
                type="text"
                value={pdcName}
                onChange={(e) => setPdcName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Homing Peptide Sequence</label>
              <input
                type="text"
                value={peptide}
                onChange={(e) => setPeptide(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Cleavable Linker Architecture</label>
              <select
                value={linker}
                onChange={(e) => setLinker(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              >
                <option value="Val-Cit-PABC">Val-Cit-PABC (Cathepsin-B Cleavable)</option>
                <option value="Val-Ala-PABC">Val-Ala-PABC (High Plasma Stability)</option>
                <option value="Phe-Lys-PABC">Phe-Lys-PABC (Rapid Release)</option>
                <option value="Disulfide-Hindered">Disulfide-Hindered (Glutathione Sensitive)</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Cytotoxic Payload</label>
              <input
                type="text"
                value={payload}
                onChange={(e) => setPayload(e.target.value)}
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
                background: '#10b981',
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
              Evaluate Cleavage & Stability
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Plasma t₁/₂ (Hours)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>
                    {result.plasma_stability_half_life_hours}h
                  </div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Therapeutic Index</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.therapeutic_index}:1</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Cleavage Rate (kcat/Km)</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#facc15' }}>{result.tumor_cleavage_rate_kcat_km.toLocaleString()} M⁻¹s⁻¹</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Enzymatic Cleavage Profiles</h3>
                {result.cleavage_profiles.map((cp: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < result.cleavage_profiles.length - 1 ? '1px solid #334155' : 'none' }}>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{cp.enzyme}</div>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      Efficiency: {cp.cleavage_efficiency_percent}% in {cp.incubation_time_min} min | Intact Remaining: {cp.intact_percent}%
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
              <ShieldCheck size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Configure peptide conjugate and cleavable linker to simulate lysosomal activation kinetics</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PDCConjugateStudioPage;
