import React, { useState } from 'react';
import { Target, ShieldCheck, Zap, Scissors, Activity, BarChart2 } from 'lucide-react';

export const PROTACKineticsStudioPage: React.FC = () => {
  const [protacName, setProtacName] = useState('ARV-110 (Bavdegalutamide Analogue)');
  const [targetName, setTargetName] = useState('Androgen Receptor (AR / AR-T878A)');
  const [e3Ligase, setE3Ligase] = useState('VHL (Von Hippel-Lindau)');
  const [linker, setLinker] = useState('PEG3-Triazole Linker');
  const [targetKd, setTargetKd] = useState(18.5);
  const [e3Kd, setE3Kd] = useState(35.0);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await fetch('/api/v1/protac-kinetics/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protac_compound_name: protacName,
          target_protein_name: targetName,
          e3_ligase_name: e3Ligase,
          linker_type: linker,
          target_kd_binary_nM: targetKd,
          e3_kd_binary_nM: e3Kd,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl border border-rose-500/20">
            <Scissors className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              PROTAC Ternary Complex & Degradation Kinetics Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 156: Target-PROTAC-E3 Ternary Equilibrium, Cooperativity Factor (α) & Hook Effect Degradation Dynamics
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-rose-400" />
              <span>Targeted Degrader Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">PROTAC Compound Name</label>
                <input
                  type="text"
                  value={protacName}
                  onChange={(e) => setProtacName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Protein (POI)</label>
                <input
                  type="text"
                  value={targetName}
                  onChange={(e) => setTargetName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Recruited E3 Ligase</label>
                <input
                  type="text"
                  value={e3Ligase}
                  onChange={(e) => setE3Ligase(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">POI Kd (nM)</label>
                  <input
                    type="number"
                    value={targetKd}
                    onChange={(e) => setTargetKd(parseFloat(e.target.value) || 10.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">E3 Kd (nM)</label>
                  <input
                    type="number"
                    value={e3Kd}
                    onChange={(e) => setE3Kd(parseFloat(e.target.value) || 20.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                  />
                </div>
              </div>

              <button
                onClick={handleSimulate}
                disabled={simulating}
                className="w-full py-3 bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-rose-500/20 disabled:opacity-50"
              >
                {simulating ? 'Computing Ternary Thermodynamics...' : 'Simulate Degradation Kinetics'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-rose-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-rose-400">Degradation Potency & Cooperativity</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">DC50 Potency</p>
                      <p className="text-lg font-bold text-white mt-1">{result.dc50_nM} nM</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Dmax Efficacy</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.dmax_percent}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Cooperativity (α)</p>
                      <p className="text-lg font-bold text-rose-400 mt-1">{result.cooperativity_alpha}x</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Hook Threshold</p>
                      <p className="text-lg font-bold text-amber-400 mt-1">{result.hook_effect_threshold_uM} µM</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Dose-Response Bell Curve (Hook Effect)</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Dose (nM)</th>
                          <th className="px-4 py-3">Ternary Fraction</th>
                          <th className="px-4 py-3">Degradation %</th>
                          <th className="px-4 py-3">Ubiquitination Flux</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.dose_response_curve.map((d: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-rose-400">{d.protac_dose_nM} nM</td>
                            <td className="px-4 py-3.5 text-slate-300">{(d.ternary_fraction * 100).toFixed(1)}%</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{d.degradation_rate_pct}%</td>
                            <td className="px-4 py-3.5 text-cyan-400">{d.ubiquitination_flux} AU/s</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure binary Kd affinities and linker architecture to simulate PROTAC ternary degradation.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PROTACKineticsStudioPage;
