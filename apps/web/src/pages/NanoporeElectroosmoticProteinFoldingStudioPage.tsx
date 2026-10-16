import React, { useState } from 'react';
import { Layers, Zap, Sparkles, Activity, Crosshair, Cpu } from 'lucide-react';

export const NanoporeElectroosmoticProteinFoldingStudioPage: React.FC = () => {
  const [name, setName] = useState('Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler Investigation');
  const [specimen, setSpecimen] = useState('Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias');
  const [modality, setModality] = useState('nanopore-electroosmotic-folding');
  const [scale, setScale] = useState(1.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/nanopore-electroosmotic-protein-folding/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          target_specimen: specimen,
          analytical_modality: modality,
          input_scale: scale,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Layers className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 553 (Milestone v5.0): Automated Analysis &amp; High-Throughput Quantitative Instrumentation
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-cyan-400" />
              <span>Experiment Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Study Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-800/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Target Specimen
                </label>
                <input
                  type="text"
                  value={specimen}
                  onChange={(e) => setSpecimen(e.target.value)}
                  className="w-full bg-slate-800/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Analytical Modality
                </label>
                <input
                  type="text"
                  value={modality}
                  onChange={(e) => setModality(e.target.value)}
                  className="w-full bg-slate-800/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Input Scaling Factor: {scale}x
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="5.0"
                  step="0.1"
                  value={scale}
                  onChange={(e) => setScale(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium rounded-xl shadow-lg shadow-cyan-500/20 transition duration-200 flex items-center justify-center space-x-2"
              >
                {analyzing ? (
                  <>
                    <Activity className="w-5 h-5 animate-spin" />
                    <span>Executing Analysis...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Execute Autonomous Study</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <p className="text-xs text-slate-400 uppercase font-medium">single_molecule_trap_dwell_time_s</p>
                    <p className="text-xl font-bold text-cyan-400 mt-1">{result.single_molecule_trap_dwell_time_s}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <p className="text-xs text-slate-400 uppercase font-medium">electroosmotic_holding_force_pn</p>
                    <p className="text-xl font-bold text-blue-400 mt-1">{result.electroosmotic_holding_force_pn}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <p className="text-xs text-slate-400 uppercase font-medium">unfolding_activation_free_energy_barrier_kt</p>
                    <p className="text-xl font-bold text-indigo-400 mt-1">{result.unfolding_activation_free_energy_barrier_kt}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <p className="text-xs text-slate-400 uppercase font-medium">Confidence</p>
                    <p className="text-xl font-bold text-emerald-400 mt-1">{(result.confidence_score * 100).toFixed(1)}%</p>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-md font-semibold text-white mb-3 flex items-center space-x-2">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    <span>Synthesis Report</span>
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                    {result.summary_report}
                  </p>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-md font-semibold text-white mb-4 flex items-center space-x-2">
                    <Crosshair className="w-5 h-5 text-cyan-400" />
                    <span>Biophysical Item Profiles</span>
                  </h3>
                  <div className="space-y-3">
                    {result.item_profiles?.map((item: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3.5 bg-slate-950/40 border border-slate-800/60 rounded-xl">
                        <div>
                          <p className="text-sm font-medium text-white">{item.item_name}</p>
                          <p className="text-xs text-slate-500">{item.profile_category}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-cyan-400">{item.quantitative_value}</p>
                          <p className="text-xs text-slate-400">log2FC: {item.log2_fold_change}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center bg-slate-900/30 border border-dashed border-slate-800 rounded-2xl p-8 text-center">
                <Layers className="w-12 h-12 text-slate-600 mb-3" />
                <h3 className="text-base font-medium text-slate-400">No Study Analysis Generated Yet</h3>
                <p className="text-xs text-slate-500 max-w-sm mt-1">
                  Adjust research specimen parameters on the left and trigger the scientific engine to generate biophysical telemetry.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
