import React, { useState } from 'react'

export const AptamerEvolutionStudioPage: React.FC = () => {
  const [targetName, setTargetName] = useState('Human Thrombin')
  const [aptamerType, setAptamerType] = useState('ssDNA')
  const [targetPka, setTargetPka] = useState(8.5)
  const [rounds, setRounds] = useState(8)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleEvolve = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/aptamer-evolution/evolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_protein_name: targetName,
          aptamer_type: aptamerType,
          target_pka: Number(targetPka),
          selection_rounds: Number(rounds),
          random_region_length: 40,
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
          In-Silico SELEX Nucleic Acid Aptamer Evolution Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Simulate iterative in-silico SELEX selection, high-affinity RNA/ssDNA aptamer enrichment, and G-quadruplex folding.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">SELEX Campaign Setup</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Target Protein</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={targetName}
              onChange={e => setTargetName(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">Aptamer Type</label>
              <select
                className="mt-1 w-full p-2 border rounded-md"
                value={aptamerType}
                onChange={e => setAptamerType(e.target.value)}
              >
                <option value="ssDNA">ssDNA</option>
                <option value="RNA">RNA</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Target pKa</label>
              <input
                type="number"
                step="0.1"
                className="mt-1 w-full p-2 border rounded-md"
                value={targetPka}
                onChange={e => setTargetPka(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Rounds</label>
              <input
                type="number"
                className="mt-1 w-full p-2 border rounded-md"
                value={rounds}
                onChange={e => setRounds(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            onClick={handleEvolve}
            disabled={loading}
            className="w-full bg-teal-600 text-white py-2 rounded-md hover:bg-teal-700 font-medium"
          >
            {loading ? 'Simulating SELEX Rounds...' : 'Execute In-Silico SELEX Evolution'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Lead Candidate & Enrichment</h2>
          {result ? (
            <div className="space-y-4">
              <div className="p-3 bg-teal-50 rounded-lg border border-teal-100">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-teal-800">{result.top_lead.lead_id}</span>
                  <span className="text-xs font-bold text-teal-900">Kd: {result.top_lead.kd_nm} nM</span>
                </div>
                <div className="mt-1 font-mono text-xs text-teal-700 break-all">{result.top_lead.sequence}</div>
                <div className="mt-2 text-xs text-teal-600 flex justify-between">
                  <span>Motif: {result.consensus_motif}</span>
                  <span>Selectivity: {result.top_lead.specificity_ratio}x</span>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Enrichment Trajectory Across Rounds
                </h3>
                <div className="mt-2 space-y-1">
                  {result.evolution_trajectory.map((t: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs py-1 border-b">
                      <span>Round {t.round_num}</span>
                      <span className="font-mono text-slate-600">Kd: {t.predicted_kd_nm} nM</span>
                      <span className="font-semibold text-teal-700">+{t.fold_enrichment}x</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Configure target parameters to evolve high-affinity aptamer leads.</p>
          )}
        </div>
      </div>
    </div>
  )
}
