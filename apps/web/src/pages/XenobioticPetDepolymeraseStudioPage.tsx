import React, { useState } from 'react';
import { Layers, Zap, Sparkles, Activity } from 'lucide-react';

export const XenobioticPetDepolymeraseStudioPage: React.FC = () => {
  const [name, setName] = useState("Autonomous Xenobiotic PET Plastic Enzymatic Depolymerase Engineering Investigation");
  const [enzyme, setEnzyme] = useState("Ideonella sakaiensis PETase Engineered Variant (Fast-PETase/LCC-ICCG)");
  const [substrate, setSubstrate] = useState("Post-Consumer Highly Crystalline Polyethylene Terephthalate (PET, 35% crystallinity)");
  const [scale, setScale] = useState(1.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/xenobiotic-pet-depolymerase/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          target_enzyme: enzyme,
          substrate_type: substrate,
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
              Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 578 (Milestone v5.1): Biocatalytic Depolymerization Kinetics &amp; Micro-Solvation Activation Barriers
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-cyan-400" />
              <span>Depolymerization Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Study Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Target Enzyme Construct
                </label>
                <input
                  type="text"
                  value={enzyme}
                  onChange={(e) => setEnzyme(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Substrate / Polymer Specimen
                </label>
                <input
                  type="text"
                  value={substrate}
                  onChange={(e) => setSubstrate(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Catalytic Scale Factor ({scale}x)
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="5.0"
                  step="0.1"
                  value={scale}
                  onChange={(e) => setScale(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>Executing Simulation...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Run Depolymerase Analysis</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-medium mb-1 truncate">kcat / Km (s^-1 mM^-1)</div>
                <div className="text-xl font-bold text-cyan-400">
                  {result ? result.catalytic_efficiency_kcat_km : '142.5'}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-medium mb-1 truncate">Melting Temp Tm (°C)</div>
                <div className="text-xl font-bold text-emerald-400">
                  {result ? result.melting_temperature_tm_celsius : '78.2'}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-medium mb-1 truncate">Barrier ΔG‡ (kcal/mol)</div>
                <div className="text-xl font-bold text-purple-400">
                  {result ? result.solvation_free_energy_barrier_kcal : '14.8'}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-medium mb-1 truncate">PET Yield (%)</div>
                <div className="text-xl font-bold text-amber-400">
                  {result ? `${result.depolymerization_yield_percent}%` : '94.6%'}
                </div>
              </div>
            </div>

            {result && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-2">
                    Executive Depolymerase Summary
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800">
                    {result.summary_report}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
                    Active Site Profiles &amp; Energetic Conformations
                  </h3>
                  <div className="space-y-2">
                    {result.item_profiles?.map((p: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg text-sm">
                        <span className="font-medium text-slate-200">{p.item_name}</span>
                        <div className="flex items-center space-x-4 text-xs">
                          <span className="text-slate-400">{p.profile_category}</span>
                          <span className="text-cyan-400 font-bold">Val: {p.quantitative_value}</span>
                          <span className="text-emerald-400 font-bold">Log2FC: {p.log2_fold_change}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
                    Biocatalytic Metric Traces
                  </h3>
                  <div className="space-y-2">
                    {result.metric_traces?.map((t: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg text-sm">
                        <span className="text-slate-300">{t.metric_dimension}</span>
                        <div className="flex items-center space-x-4 text-xs">
                          <span className="text-cyan-400 font-bold">Observed: {t.observed_value}</span>
                          <span className="text-purple-400 font-bold">Z: {t.z_score}</span>
                          <span className="text-slate-400">p: {t.p_value}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default XenobioticPetDepolymeraseStudioPage;
