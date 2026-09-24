import React, { useState } from 'react';
import { Target, Layers, Sparkles, Activity, ShieldCheck, Zap } from 'lucide-react';

export const GlycanMicroarrayStudioPage: React.FC = () => {
  const [lectinName, setLectinName] = useState('Galectin-3');
  const [organism, setOrganism] = useState('Homo sapiens');
  const [conc, setConc] = useState(10.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleScreen = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/glycan-microarray/screen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_lectin_name: lectinName,
          organism_source: organism,
          concentration_ug_ml: conc,
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
          <div className="p-3 bg-pink-500/10 text-pink-400 rounded-xl border border-pink-500/20">
            <Target className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Glycomics Microarray & Lectin Specificity Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 148: High-Density Glycan Microarray, Motif Enrichment & Apparent Kd Dissociation Engine
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-pink-400" />
              <span>Microarray Configuration</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Lectin / Receptor</label>
                <input
                  type="text"
                  value={lectinName}
                  onChange={(e) => setLectinName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-pink-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Organism Source</label>
                <input
                  type="text"
                  value={organism}
                  onChange={(e) => setOrganism(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-pink-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Lectin Concentration (µg/mL)</label>
                <input
                  type="number"
                  value={conc}
                  onChange={(e) => setConc(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-pink-500"
                />
              </div>

              <button
                onClick={handleScreen}
                disabled={analyzing}
                className="w-full py-3 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-pink-500/20 disabled:opacity-50"
              >
                {analyzing ? 'Scanning Microarray...' : 'Execute Glycan Array Screen'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-pink-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-pink-400">Specificity & Kinetics Summary</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Primary Motif</p>
                      <p className="text-sm font-bold text-white mt-1">{result.primary_epitope_motif}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Apparent Kd</p>
                      <p className="text-lg font-bold text-pink-400 mt-1">{result.kd_apparent_nM} nM</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mean SNR</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.mean_signal_to_noise}:1</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Spots Tested</p>
                      <p className="text-lg font-bold text-white mt-1">{result.spots_evaluated}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Top Binding Glycan Epitopes</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Glycan IUPAC Structure</th>
                          <th className="px-4 py-3">RFU Signal</th>
                          <th className="px-4 py-3">Z-Score</th>
                          <th className="px-4 py-3">Relative Affinity</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.top_binding_spots.map((s: any) => (
                          <tr key={s.spot_index} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-mono text-xs text-pink-300">{s.glycan_iupac}</td>
                            <td className="px-4 py-3.5 text-slate-200">{s.fluorescence_rfu.toLocaleString()}</td>
                            <td className="px-4 py-3.5 text-emerald-400">+{s.z_score}σ</td>
                            <td className="px-4 py-3.5 text-slate-300">{s.relative_affinity}x</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure your target lectin and run screening to view carbohydrate epitope profiles.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlycanMicroarrayStudioPage;
