import React, { useState } from 'react';
import { Beaker, ShieldCheck, Zap, TrendingUp, Clock, Activity } from 'lucide-react';

export const CFPSTXTLStudioPage: React.FC = () => {
  const [proteinName, setProteinName] = useState('De-Novo Designed Neutralizing Nanobody');
  const [extractType, setExtractType] = useState('E. coli BL21 Star (DE3) Lysate');
  const [mode, setMode] = useState('Continuous Exchange Cell-Free (CECF)');
  const [dnaConc, setDnaConc] = useState(10.0);
  const [temp, setTemp] = useState(30.0);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await fetch('/api/v1/cfps-txtl/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_protein_name: proteinName,
          extract_system_type: extractType,
          reaction_mode: mode,
          dna_template_concentration_nM: dnaConc,
          reaction_temperature_celsius: temp,
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
          <div className="p-3 bg-lime-500/10 text-lime-400 rounded-xl border border-lime-500/20">
            <Beaker className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Cell-Free Protein Synthesis (CFPS) TX-TL Kinetics Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 157: In-Vitro Transcription-Translation, Energy Substrate Regrowth & Continuous Exchange Bioreactor Yield
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-lime-400" />
              <span>Cell-Free Reaction Setup</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Protein Designation</label>
                <input
                  type="text"
                  value={proteinName}
                  onChange={(e) => setProteinName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-lime-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Extract System</label>
                <input
                  type="text"
                  value={extractType}
                  onChange={(e) => setExtractType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-lime-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Reaction Operating Mode</label>
                <input
                  type="text"
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-lime-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">DNA Conc (nM)</label>
                  <input
                    type="number"
                    value={dnaConc}
                    onChange={(e) => setDnaConc(parseFloat(e.target.value) || 10.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-lime-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Temp (°C)</label>
                  <input
                    type="number"
                    value={temp}
                    onChange={(e) => setTemp(parseFloat(e.target.value) || 30.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-lime-500"
                  />
                </div>
              </div>

              <button
                onClick={handleSimulate}
                disabled={simulating}
                className="w-full py-3 bg-gradient-to-r from-lime-600 to-green-600 hover:from-lime-500 hover:to-green-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-lime-500/20 disabled:opacity-50"
              >
                {simulating ? 'Integrating TX-TL ODEs...' : 'Simulate Cell-Free Synthesis'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-lime-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-lime-400">Protein Yield & Elongation Velocity</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Final Yield</p>
                      <p className="text-xl font-bold text-white mt-1">{result.final_protein_yield_mg_ml} mg/mL</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">TX Elongation</p>
                      <p className="text-lg font-bold text-lime-400 mt-1">{result.transcription_rate_nt_s} nt/s</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">TL Translation</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.translation_rate_aa_s} aa/s</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Energy Efficiency</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{(result.energy_regeneration_efficiency * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Protein Accumulation Kinetics</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Time (Hours)</th>
                          <th className="px-4 py-3">mRNA Pool (µM)</th>
                          <th className="px-4 py-3">Protein Yield (mg/mL)</th>
                          <th className="px-4 py-3">Active Ribosomes</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.yield_trajectories.map((y: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-lime-400">{y.time_elapsed_hours}h</td>
                            <td className="px-4 py-3.5 text-slate-300">{y.mrna_concentration_uM} µM</td>
                            <td className="px-4 py-3.5 font-bold text-white">{y.protein_concentration_mg_ml} mg/mL</td>
                            <td className="px-4 py-3.5 text-emerald-400">{(y.ribosome_active_fraction * 100).toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure cell-free extract conditions to compute transcription-translation kinetics.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CFPSTXTLStudioPage;
