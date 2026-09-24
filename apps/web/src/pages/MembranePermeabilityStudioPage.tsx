import React, { useState } from 'react'

export const MembranePermeabilityStudioPage: React.FC = () => {
  const [moleculeName, setMoleculeName] = useState('Propranolol')
  const [smiles, setSmiles] = useState('CC(C)NCC(O)COC1=CC=CC2=CC=CC=C12')
  const [mw, setMw] = useState(259.34)
  const [logp, setLogp] = useState(2.6)
  const [tpsa, setTpsa] = useState(41.49)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleEvaluate = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/membrane-permeability/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          molecule_name: moleculeName,
          smiles,
          molecular_weight: Number(mw),
          logp: Number(logp),
          tpsa: Number(tpsa),
          h_bond_donors: 2,
          h_bond_acceptors: 3,
          rotatable_bonds: 6,
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
          In-Silico Membrane Permeability (PAMPA) Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Predict artificial membrane permeability (Papp), BBB penetration, and lipid bilayer depth-dependent diffusivity.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Physicochemical Descriptors</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Molecule Name</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={moleculeName}
              onChange={e => setMoleculeName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">SMILES</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md font-mono text-sm"
              value={smiles}
              onChange={e => setSmiles(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">MW (g/mol)</label>
              <input
                type="number"
                className="mt-1 w-full p-2 border rounded-md"
                value={mw}
                onChange={e => setMw(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">cLogP</label>
              <input
                type="number"
                step="0.1"
                className="mt-1 w-full p-2 border rounded-md"
                value={logp}
                onChange={e => setLogp(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">TPSA (Å²)</label>
              <input
                type="number"
                step="0.1"
                className="mt-1 w-full p-2 border rounded-md"
                value={tpsa}
                onChange={e => setTpsa(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            onClick={handleEvaluate}
            disabled={loading}
            className="w-full bg-cyan-600 text-white py-2 rounded-md hover:bg-cyan-700 font-medium"
          >
            {loading ? 'Evaluating PAMPA Permeability...' : 'Run In-Silico PAMPA Simulation'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Permeability & BBB Summary</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-cyan-50 rounded-lg border border-cyan-100">
                  <div className="text-xs text-cyan-700 font-medium">Estimated Papp</div>
                  <div className="text-lg font-bold text-cyan-900">{result.papp_cm_per_s} cm/s</div>
                  <span className="text-xs bg-cyan-200 text-cyan-800 px-2 py-0.5 rounded-full font-semibold">
                    {result.permeability_class}
                  </span>
                </div>
                <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                  <div className="text-xs text-indigo-700 font-medium">BBB Permeability</div>
                  <div className="text-lg font-bold text-indigo-900">
                    {result.bbb_permeable ? 'Permeable (BBB+)' : 'Non-Permeable (BBB-)'}
                  </div>
                  <div className="text-xs text-indigo-600">QSAR Score: {result.qsar_score}</div>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Bilayer Energy Landscape Profile
                </h3>
                <div className="mt-2 space-y-1">
                  {result.diffusivity_profile.map((p: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs py-1 border-b">
                      <span>Depth: {p.depth_angstrom} Å</span>
                      <span className="font-mono">ΔG: {p.free_energy_barrier_kcal_mol} kcal/mol</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Enter molecular descriptors to calculate permeability profile.</p>
          )}
        </div>
      </div>
    </div>
  )
}
