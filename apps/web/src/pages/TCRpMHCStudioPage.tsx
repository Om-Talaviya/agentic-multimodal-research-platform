import React, { useState } from 'react'

export const TCRpMHCStudioPage: React.FC = () => {
  const [tcrName, setTcrName] = useState('NY-ESO-1 1G4 TCR')
  const [cdr3a, setCdr3a] = useState('CAVRPTSGGSYIPTF')
  const [cdr3b, setCdr3b] = useState('CASSYVGNTGELFF')
  const [peptide, setPeptide] = useState('SLLMWITQC')
  const [hla, setHla] = useState('HLA-A*02:01')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/tcr-pmhc/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tcr_name: tcrName,
          cdr3_alpha_seq: cdr3a,
          cdr3_beta_seq: cdr3b,
          target_peptide: peptide,
          hla_allele: hla,
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
          TCR-pMHC Structural Binding & Off-Target Cross-Reactivity Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Predict engineered T-cell receptor binding affinity (Kd), on-target free energy ΔG, and human proteome off-target cross-reactivity risks.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">TCR & Epitope Complex</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">TCR Clone Name</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={tcrName}
              onChange={e => setTcrName(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">CDR3α Sequence</label>
              <input
                type="text"
                className="mt-1 w-full p-2 border rounded-md font-mono text-xs"
                value={cdr3a}
                onChange={e => setCdr3a(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">CDR3β Sequence</label>
              <input
                type="text"
                className="mt-1 w-full p-2 border rounded-md font-mono text-xs"
                value={cdr3b}
                onChange={e => setCdr3b(e.target.value)}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">Target Neoantigen / Epitope</label>
              <input
                type="text"
                className="mt-1 w-full p-2 border rounded-md font-mono text-xs"
                value={peptide}
                onChange={e => setPeptide(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">HLA Restriction</label>
              <input
                type="text"
                className="mt-1 w-full p-2 border rounded-md text-xs"
                value={hla}
                onChange={e => setHla(e.target.value)}
              />
            </div>
          </div>
          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 font-medium"
          >
            {loading ? 'Predicting TCR-pMHC Affinity...' : 'Run TCR-pMHC Interface Analysis'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Binding Energetics & Safety Sentinel</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="text-xs text-blue-700 font-medium">Binding Affinity (Kd)</div>
                  <div className="text-lg font-bold text-blue-900">{result.binding_kd_um} µM</div>
                  <div className="text-xs text-blue-600">ΔG: {result.on_target_energy_kcal_mol} kcal/mol</div>
                </div>
                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                  <div className="text-xs text-emerald-700 font-medium">Immunogenicity Score</div>
                  <div className="text-lg font-bold text-emerald-900">{(result.immunogenicity_score * 100).toFixed(1)}%</div>
                  <div className="text-xs text-emerald-600">HLA: {result.hla_allele}</div>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Cross-Reactivity Self-Peptide Scan
                </h3>
                <div className="mt-2 space-y-2">
                  {result.cross_reactivity_scan.map((ot: any, idx: number) => (
                    <div key={idx} className="p-2 border rounded text-xs">
                      <div className="flex justify-between font-semibold">
                        <span>{ot.self_peptide} (Kd: {ot.cross_kd_um} µM)</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          ot.risk_level === 'Low' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                        }`}>
                          {ot.risk_level} Risk
                        </span>
                      </div>
                      <div className="text-slate-500 mt-0.5 text-[11px]">{ot.tissue}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Enter TCR sequences to compute binding affinity and cross-reactivity.</p>
          )}
        </div>
      </div>
    </div>
  )
}
