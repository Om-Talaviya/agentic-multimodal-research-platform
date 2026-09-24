import React, { useState } from 'react'

export const MitochondrialBioenergeticsStudioPage: React.FC = () => {
  const [cellLine, setCellLine] = useState('Human iPSC Cardiomyocytes')
  const [substrate, setSubstrate] = useState('Pyruvate/Malate')
  const [fccp, setFccp] = useState(0.5)
  const [complexIInhib, setComplexIInhib] = useState(0)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/mitochondrial-bioenergetics/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cell_line: cellLine,
          substrate_type: substrate,
          uncoupler_fccp_concentration_um: Number(fccp),
          complex_i_inhibition_pct: Number(complexIInhib),
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
          Mitochondrial OXPHOS Bioenergetics & ROS Dynamics Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Simulate chemiosmotic mitochondrial respiration, Seahorse XF oxygen consumption rates (OCR), and superoxide emission dynamics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Mitochondrial Chamber Parameters</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Cell Line / Tissue</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={cellLine}
              onChange={e => setCellLine(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Metabolic Substrate</label>
            <select
              className="mt-1 w-full p-2 border rounded-md"
              value={substrate}
              onChange={e => setSubstrate(e.target.value)}
            >
              <option value="Pyruvate/Malate">Pyruvate/Malate (Complex I-driven)</option>
              <option value="Succinate">Succinate (Complex II-driven)</option>
              <option value="Palmitoyl-CoA">Palmitoyl-CoA (Fatty Acid β-Oxidation)</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">FCCP Uncoupler (µM)</label>
              <input
                type="number"
                step="0.1"
                className="mt-1 w-full p-2 border rounded-md"
                value={fccp}
                onChange={e => setFccp(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Complex I Inhibition (%)</label>
              <input
                type="number"
                className="mt-1 w-full p-2 border rounded-md"
                value={complexIInhib}
                onChange={e => setComplexIInhib(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-rose-600 text-white py-2 rounded-md hover:bg-rose-700 font-medium"
          >
            {loading ? 'Modeling Chemiosmotic Flux...' : 'Run Bioenergetics & ROS Simulation'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Respirometry & Chemiosmotic Flux</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-rose-50 rounded-lg border border-rose-100">
                  <div className="text-xs text-rose-700 font-medium">Basal OCR</div>
                  <div className="text-lg font-bold text-rose-900">{result.basal_ocr_pmol_min} pmol/min</div>
                  <div className="text-xs text-rose-600">ATP-linked: {result.atp_linked_respiration} pmol/min</div>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                  <div className="text-xs text-amber-700 font-medium">Maximal Capacity</div>
                  <div className="text-lg font-bold text-amber-900">{result.maximal_respiratory_capacity} pmol/min</div>
                  <div className="text-xs text-amber-600">Spare Reserve: {result.spare_respiratory_capacity}</div>
                </div>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between text-xs">
                <span>ΔΨm: <strong>{result.delta_psi_mv} mV</strong></span>
                <span>Superoxide Rate: <strong>{result.superoxide_emission_rate} µM/s</strong></span>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  ETC Complex Activity Matrix
                </h3>
                <div className="mt-2 space-y-1">
                  {result.etc_complexes.map((c: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs py-1 border-b">
                      <span>{c.complex_id}</span>
                      <span className="font-semibold text-rose-700">{c.activity_pct}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Configure respiration chamber to simulate OXPHOS and electron transport.</p>
          )}
        </div>
      </div>
    </div>
  )
}
