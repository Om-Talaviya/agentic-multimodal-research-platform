import React, { useState } from 'react';
import { Layers, Zap, Sparkles, Activity, Crosshair, Cpu } from 'lucide-react';

export const CryoetActinMicrotubuleLatticeStudioPage: React.FC = () => {
  const [name, setName] = useState('Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine Investigation');
  const [specimen, setSpecimen] = useState('Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies');
  const [modality, setModality] = useState('cryoet-actin-microtubule-lattice');
  const [scale, setScale] = useState(1.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/cryoet-actin-microtubule-lattice/analyze', {
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
              Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 469 (Milestone v4.6): Automated Analysis &amp; High-Throughput Quantitative Instrumentation
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
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
                  Study Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
                  Target Specimen
                </label>
                <input
                  type="text"
                  value={specimen}
                  onChange={(e) => setSpecimen(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
                  Analytical Modality
                </label>
                <input
                  type="text"
                  value={modality}
                  onChange={(e) => setModality(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
                  Input Parameter Scale (1.0 - 5.0)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={scale}
                  onChange={(e) => setScale(parseFloat(e.target.value) || 1.0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium py-2.5 px-4 rounded-xl transition duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
              >
                {analyzing ? (
                  <span>Analyzing Telemetry...</span>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
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
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <div className="text-xs text-slate-400 mb-1">crosslinker_bridge_density_per_um</div>
                    <div className="text-xl font-bold text-cyan-400">{result.crosslinker_bridge_density_per_um}</div>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <div className="text-xs text-slate-400 mb-1">filament_intersection_angle_distribution_deg</div>
                    <div className="text-xl font-bold text-blue-400">{result.filament_intersection_angle_distribution_deg}</div>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <div className="text-xs text-slate-400 mb-1">subtomogram_correlation_resolution_angstrom</div>
                    <div className="text-xl font-bold text-indigo-400">{result.subtomogram_correlation_resolution_angstrom}</div>
                  </div>
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
                    <div className="text-xs text-slate-400 mb-1">Confidence Score</div>
                    <div className="text-xl font-bold text-emerald-400">
                      {(result.confidence_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3 flex items-center space-x-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <span>Summary Synthesis</span>
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-xl border border-slate-800/50">
                    {result.summary_report}
                  </p>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    <span>Item Profiles &amp; Step Telemetry</span>
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-xs text-slate-400">
                          <th className="pb-3 font-medium">Stage / Item</th>
                          <th className="pb-3 font-medium">Category</th>
                          <th className="pb-3 font-medium">Quant. Value</th>
                          <th className="pb-3 font-medium">Log2 FC</th>
                          <th className="pb-3 font-medium">Score</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
                        {result.item_profiles?.map((item: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30">
                            <td className="py-2.5 font-medium text-white">{item.item_name}</td>
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
