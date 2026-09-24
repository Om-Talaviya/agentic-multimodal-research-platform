import React, { useState } from 'react';
import { Layers, Zap, RefreshCw, Grid, MapPin } from 'lucide-react';

export const SpatialMicrodissectionStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('VisiumHD_Glioblastoma_Section4');
  const [tissueType, setTissueType] = useState('Glioblastoma Multiforme');
  const [gridSize, setGridSize] = useState(4);
  const [resolutionNm, setResolutionNm] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleDeconvolve = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/spatial-microdissection/deconvolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          sample_name: sampleName,
          tissue_type: tissueType,
          spot_grid_size: gridSize,
          resolution_nm: resolutionNm
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
        <Grid size={32} color="#38bdf8" />
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
            Spatial Microdissection & Subcellular Spot Deconvolution
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Phase 162: Subcellular NMF-Bayesian Single-Cell Resolution Spot Deconvolution Studio
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#f8fafc' }}>Microdissection Setup</h2>
          <form onSubmit={handleDeconvolve} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Sample Identifier</label>
              <input
                type="text"
                value={sampleName}
                onChange={(e) => setSampleName(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Tissue Type</label>
              <input
                type="text"
                value={tissueType}
                onChange={(e) => setTissueType(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Grid Size (NxN)</label>
                <input
                  type="number"
                  value={gridSize}
                  onChange={(e) => setGridSize(parseInt(e.target.value))}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Resolution (nm)</label>
                <input
                  type="number"
                  value={resolutionNm}
                  onChange={(e) => setResolutionNm(parseFloat(e.target.value))}
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
                background: '#38bdf8',
                color: '#0f172a',
                padding: '0.75rem',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: 600,
                marginTop: '0.5rem'
              }}
            >
              {loading ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
              Deconvolve Spots
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Total Spots Analyzed</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{result.total_spots}</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Subcellular Resolution</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#4ade80' }}>{result.resolution_nm} nm</div>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Mean Shannon Entropy</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#facc15' }}>{result.mean_entropy} bits</div>
                </div>
              </div>

              <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h3 style={{ margin: 0, marginBottom: '0.75rem', fontSize: '1.1rem' }}>Identified Cellular Niches</h3>
                {result.niches.map((niche: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < result.niches.length - 1 ? '1px solid #334155' : 'none' }}>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{niche.niche_name}</div>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      Cellularity: {niche.cellularity_score} | Interface Distance: {niche.interface_distance_um} µm
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ background: '#1e293b', padding: '3rem', borderRadius: '12px', textAlign: 'center', color: '#64748b' }}>
              <Layers size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p>Configure spot parameters and execute Bayesian NMF subcellular deconvolution</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpatialMicrodissectionStudioPage;
