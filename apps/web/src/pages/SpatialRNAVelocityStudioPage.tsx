import React, { useState } from 'react'

export const SpatialRNAVelocityStudioPage: React.FC = () => {
  const [tissue, setTissue] = useState('Developing Mouse Neocortex')
  const [stage, setStage] = useState('E14.5')
  const [spots, setSpots] = useState(1500)
  const [gamma, setGamma] = useState(1.0)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/spatial-rna-velocity/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tissue_sample: tissue,
          developmental_stage: stage,
          spot_count: Number(spots),
          splicing_rate_gamma: Number(gamma),
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Spatial RNA Velocity & Morphogenesis Vector Field Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Model directional cell differentiation trajectories and spatial morphogenesis streamlines from spliced/unspliced RNA kinetics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Spatial Kinetics Setup</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Tissue Sample</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={tissue}
              onChange={e => setTissue(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">Stage</label>
              <input
                type="text"
                className="mt-1 w-full p-2 border rounded-md"
                value={stage}
                onChange={e => setStage(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Spots</label>
              <input
                type="number"
                className="mt-1 w-full p-2 border rounded-md"
                value={spots}
                onChange={e => setSpots(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Degradation γ</label>
              <input
                type="number"
                step="0.1"
                className="mt-1 w-full p-2 border rounded-md"
                value={gamma}
                onChange={e => setGamma(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-orange-600 text-white py-2 rounded-md hover:bg-orange-700 font-medium"
          >
            {loading ? 'Solving Velocity Vector Field...' : 'Simulate Spatial RNA Velocity'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Morphogenetic Streamlines</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-orange-50 rounded-lg border border-orange-100">
                  <div className="text-xs text-orange-700 font-medium">Mean Velocity Speed</div>
                  <div className="text-lg font-bold text-orange-900">{result.mean_speed} a.u./hr</div>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Spatial Coherence</div>
                  <div className="text-lg font-bold text-slate-900">{(result.directionality_coherence * 100).toFixed(1)}%</div>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Lineage Streamline Paths
                </h3>
                <div className="mt-2 space-y-2">
                  {result.streamlines.map((s: any, idx: number) => (
                    <div key={idx} className="p-2 border rounded text-xs">
                      <div className="font-semibold text-orange-900">{s.flow_id}</div>
                      <div className="text-slate-600 mt-0.5">
                        {s.source_state} → <strong>{s.dest_state}</strong> (Δt: {s.pseudotime})
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Configure spatial tissue parameters to compute RNA velocity vector fields.</p>
          )}
        </div>
      </div>
    </div>
  )
}
