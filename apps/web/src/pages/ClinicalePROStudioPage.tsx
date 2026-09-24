import React, { useState } from 'react'

export const ClinicalePROStudioPage: React.FC = () => {
  const [protocolId, setProtocolId] = useState('PH3-ONC-MELANOMA-2026')
  const [therapeuticArea, setTherapeuticArea] = useState('Immuno-Oncology')
  const [cohortSize, setCohortSize] = useState(120)
  const [qolBaseline, setQolBaseline] = useState(0.74)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/v1/clinical-epro/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol_id: protocolId,
          therapeutic_area: therapeuticArea,
          patient_cohort_size: Number(cohortSize),
          baseline_qol_score: Number(qolBaseline),
          trial_duration_weeks: 24,
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
          Decentralized Clinical Trial ePRO Telemetry Studio
        </h1>
        <p className="text-slate-600 mt-1">
          Monitor real-world patient reported outcomes (PROs), EQ-5D quality-of-life trajectories, and automated CTCAE adverse event escalation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">ePRO Protocol Parameters</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700">Protocol ID</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={protocolId}
              onChange={e => setProtocolId(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Therapeutic Area</label>
            <input
              type="text"
              className="mt-1 w-full p-2 border rounded-md"
              value={therapeuticArea}
              onChange={e => setTherapeuticArea(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700">Patient Cohort</label>
              <input
                type="number"
                className="mt-1 w-full p-2 border rounded-md"
                value={cohortSize}
                onChange={e => setCohortSize(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700">Baseline QoL (0-1)</label>
              <input
                type="number"
                step="0.05"
                className="mt-1 w-full p-2 border rounded-md"
                value={qolBaseline}
                onChange={e => setQolBaseline(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-2 rounded-md hover:bg-emerald-700 font-medium"
          >
            {loading ? 'Simulating Patient Telemetry...' : 'Run ePRO Outcomes Simulation'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Study Telemetry & Safety Alerts</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                  <div className="text-xs text-emerald-700 font-medium">Compliance Rate</div>
                  <div className="text-lg font-bold text-emerald-900">
                    {(result.overall_compliance_rate * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="text-xs text-blue-700 font-medium">Mean QoL Shift</div>
                  <div className="text-lg font-bold text-blue-900">+{result.mean_qol_change_delta}</div>
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Active Adverse Event Sentinel Alerts ({result.active_alerts.length})
                </h3>
                <div className="mt-2 space-y-2">
                  {result.active_alerts.map((a: any, idx: number) => (
                    <div
                      key={idx}
                      className={`p-2 rounded border text-xs ${
                        a.site_escalation ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-slate-50 border-slate-200'
                      }`}
                    >
                      <div className="flex justify-between font-semibold">
                        <span>{a.patient_id} - Grade {a.ctcae_grade}</span>
                        {a.site_escalation && (
                          <span className="text-red-600 uppercase text-[10px] font-bold">Escalation Required</span>
                        )}
                      </div>
                      <div className="mt-0.5">{a.symptom}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Configure trial cohort to view ePRO engagement and safety alerts.</p>
          )}
        </div>
      </div>
    </div>
  )
}
