import React, { useState } from 'react';
import { Layers, Zap, Sparkles, Activity, Crosshair, Cpu } from 'lucide-react';

export const QuorumQuenchingLactonaseDispersionStudioPage: React.FC = () => {
  const [name, setName] = useState('Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster Investigation');
  const [specimen, setSpecimen] = useState('Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)');
  const [modality, setModality] = useState('quorum-quenching-lactonase');
  const [scale, setScale] = useState(1.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/quorum-quenching-lactonase-dispersion/analyze', {
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
              Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 485 (Milestone v4.7): Automated Analysis &amp; High-Throughput Quantitative Instrumentation
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
                  Input Perturbation Scale: {scale}x
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="10.0"
                  step="0.1"
                  value={scale}
                  onChange={(e) => setScale(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full mt-4 flex items-center justify-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium py-3 rounded-xl shadow-lg shadow-cyan-500/20 transition-all duration-200 disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Activity className="w-5 h-5 animate-spin" />
                    <span>Executing Simulation...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Run Autonomous Analysis</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
                    <span className="text-xs font-semibold text-slate-400 uppercase">ahl_hydrolysis_kcat_over_km_M_inv_s_inv</span>
                    <p className="text-2xl font-bold text-cyan-400 mt-2">{result.ahl_hydrolysis_kcat_over_km_M_inv_s_inv}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
                    <span className="text-xs font-semibold text-slate-400 uppercase">biofilm_extracellular_matrix_reduction_pct</span>
                    <p className="text-2xl font-bold text-blue-400 mt-2">{result.biofilm_extracellular_matrix_reduction_pct}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
                    <span className="text-xs font-semibold text-slate-400 uppercase">quorum_regulated_pyocyanin_suppression_pct</span>
                    <p className="text-2xl font-bold text-indigo-400 mt-2">{result.quorum_regulated_pyocyanin_suppression_pct}</p>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
                    <span className="text-xs font-semibold text-slate-400 uppercase">Confidence</span>
                    <p className="text-2xl font-bold text-emerald-400 mt-2">{(result.confidence_score * 100).toFixed(1)}%</p>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-md font-semibold text-white flex items-center space-x-2 mb-3">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    <span>Synthesis Telemetry &amp; Findings</span>
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed">{result.summary_report}</p>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-md font-semibold text-white mb-4">Item Profile Decomposition</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                          <th className="pb-3">Item Name</th>
                          <th className="pb-3">Category</th>
                          <th className="pb-3">Quantitative Value</th>
                          <th className="pb-3">Log2 FC</th>
                          <th className="pb-3">Significance</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.item_profiles?.map((item: any, i: number) => (
                          <tr key={i} className="hover:bg-slate-800/30">
                            <td className="py-2.5 font-medium text-slate-200">{item.item_name}</td>
                            <td className="py-2.5 text-slate-400">{item.profile_category}</td>
                            <td className="py-2.5 text-cyan-300">{item.quantitative_value}</td>
                            <td className="py-2.5 text-slate-400">{item.log2_fold_change}</td>
                            <td className="py-2.5 text-emerald-400">{item.significance_score}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-96 border border-dashed border-slate-800/80 rounded-2xl flex flex-col items-center justify-center text-slate-500 space-y-3">
                <Crosshair className="w-10 h-10 stroke-1" />
                <p className="text-sm">Configure parameters and launch the autonomous analysis engine.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
