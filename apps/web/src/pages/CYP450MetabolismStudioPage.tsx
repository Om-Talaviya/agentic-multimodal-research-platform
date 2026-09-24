import React, { useState } from 'react'

export const CYP450MetabolismStudioPage: React.FC = () => {
  const [compoundName, setCompoundName] = useState('Ketoconazole')
  const [smiles, setSmiles] = useState('CC(=O)N1CCN(CC1)C2=CC=C(C=C2)OCC3COC(O3)(CN4C=CN=C4)C5=C(C=C(C=C5)Cl)Cl')
  const [mw, setMw] = useState(531.43)
  const [logp, setLogp] = useState(4.35)
  const [aromaticRings, setAromaticRings] = useState(3)
  const [basicN, setBasicN] = useState(2)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/cyp450-metabolism/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          compound_name: compoundName,
          smiles,
          molecular_weight: Number(mw),
          logp: Number(logp),
          aromatic_ring_count: Number(aromaticRings),
          basic_nitrogen_count: Number(basicN),
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
          Cytochrome P450 Drug Metabolism & Inhibition Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Predict human hepatic CYP isoform inhibition (3A4, 2D6, 2C9), intrinsic clearance (Clint), and metabolic soft spots.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Compound Descriptors</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Compound Name</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={compoundName}
              onChange={e => setCompoundName(e.target.value)}
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
          <div className="grid grid-cols-2 gap-3">
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
          </div>
          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full bg-violet-600 text-white py-2 rounded-md hover:bg-violet-700 font-medium"
          >
            {loading ? 'Predicting CYP450 Profile...' : 'Run CYP450 Inhibition & Clearance Screen'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Metabolic Stability & DDI Risk</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-violet-50 rounded-lg border border-violet-100">
                  <div className="text-xs text-violet-700 font-medium">Intrinsic Clint</div>
                  <div className="text-lg font-bold text-violet-900">{result.clint_ml_min_kg} mL/min/kg</div>
                  <div className="text-xs text-violet-600">Hepatic Extraction: {result.hepatic_extraction}</div>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Primary Metabolic Site</div>
                  <div className="text-sm font-semibold text-slate-800 mt-1">{result.primary_metabolic_site}</div>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Isoform Inhibition Profile
                </h3>
                <div className="mt-2 space-y-2">
                  {result.isoform_predictions.map((iso: any, idx: number) => (
                    <div key={idx} className="p-2 border rounded flex justify-between items-center text-xs">
                      <div>
                        <strong>{iso.isoform}</strong> (IC50: {iso.ic50_um} µM)
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          iso.is_inhibitor ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {iso.is_inhibitor ? 'INHIBITOR' : 'NON-INHIBITOR'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Enter molecular descriptors to simulate CYP450 metabolism.</p>
          )}
        </div>
      </div>
    </div>
  )
}
