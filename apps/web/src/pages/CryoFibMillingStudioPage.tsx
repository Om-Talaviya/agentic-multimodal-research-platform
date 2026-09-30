import React, { useState } from 'react';
import { Layers, ShieldCheck, Zap, Sparkles, Activity, Crosshair, Cpu, CheckCircle } from 'lucide-react';

export const CryoFibMillingStudioPage: React.FC = () => {
  const [name, setName] = useState('Vitreous Lamella Thinning for Nuclear Pore Cryo-ET');
  const [specimen, setSpecimen] = useState('Vitreous Cellular Cryo-Lamella (HeLa Nucleus)');
  const [modality, setModality] = useState('cryo-fib-milling');
  const [scale, setScale] = useState(1.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/cryo-fib-milling/analyze', {
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
              Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 414 (Milestone v4.4): Ion-Beam Current Profiling, Curtaining Suppression & In-Situ Vitreous Lamella Optimization (&lt;150 nm)
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-cyan-400" />
              <span>Cryo-FIB DualBeam Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold uppercase text-slate-400">Study / Lamella Designation</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase text-slate-400">Target Specimen</label>
                <input
                  type="text"
                  value={specimen}
                  onChange={(e) => setSpecimen(e.target.value)}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase text-slate-400">Milling Intensity Scale ({scale.toFixed(2)}x)</label>
                <input
                  type="range"
                  min="0.5"
                  max="3.0"
                  step="0.1"
                  value={scale}
                  onChange={(e) => setScale(parseFloat(e.target.value))}
                  className="w-full mt-2 accent-cyan-500"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full mt-4 bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2.5 px-4 rounded-xl transition duration-150 flex items-center justify-center space-x-2 shadow-lg shadow-cyan-600/20 disabled:opacity-50"
              >
                {analyzing ? (
                  <Activity className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Crosshair className="w-5 h-5" />
                    <span>Run Cryo-FIB Optimization</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
                    <p className="text-xs text-slate-400">Lamella Thickness</p>
                    <p className="text-2xl font-bold text-cyan-400 mt-1">{result.in_situ_lamella_thickness_nm} nm</p>
                    <span className="text-[10px] text-emerald-400 flex items-center mt-1">
                      <CheckCircle className="w-3 h-3 mr-1" /> Cryo-ET Optimal
                    </span>
                  </div>

                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
                    <p className="text-xs text-slate-400">Curtaining Suppression</p>
                    <p className="text-2xl font-bold text-sky-400 mt-1">{(result.curtaining_artifact_suppression_ratio * 100).toFixed(1)}%</p>
                    <span className="text-[10px] text-slate-400 mt-1">GIS Platinum Coated</span>
                  </div>

                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
                    <p className="text-xs text-slate-400">Polishing Current</p>
                    <p className="text-2xl font-bold text-emerald-400 mt-1">{result.gallium_ion_beam_current_pA} pA</p>
                    <span className="text-[10px] text-slate-400 mt-1">Ga+ Low-Damage Mode</span>
                  </div>

                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
                    <p className="text-xs text-slate-400">Vitreous Ice Score</p>
                    <p className="text-2xl font-bold text-indigo-400 mt-1">{result.vitreous_ice_preservation_score}</p>
                    <span className="text-[10px] text-slate-400 mt-1">Devitrification Free</span>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-white flex items-center space-x-2">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    <span>Milling Stage Profiles</span>
                  </h3>
                  <div className="divide-y divide-slate-800/60">
                    {result.item_profiles?.map((item: any, idx: number) => (
                      <div key={idx} className="py-3 flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-200">{item.item_name}</p>
                          <p className="text-xs text-slate-400">{item.profile_category}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-cyan-400">{item.quantitative_value}</p>
                          <p className="text-xs text-slate-500">Significance: {item.significance_score}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-2 flex items-center space-x-2">
                    <Sparkles className="w-5 h-5 text-cyan-400" />
                    <span>Autonomous Synthesis Report</span>
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800/60">
                    {result.summary_report}
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/30 border border-dashed border-slate-800 rounded-2xl p-12 text-center text-slate-500">
                <Layers className="w-12 h-12 mx-auto mb-3 opacity-40 text-cyan-400" />
                <p className="text-sm">Configure Cryo-FIB milling parameters and click "Run Cryo-FIB Optimization" to compute in-situ lamella thinning metrics.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
