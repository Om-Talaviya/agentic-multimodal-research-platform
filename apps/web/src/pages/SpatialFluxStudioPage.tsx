import React, { useState } from 'react';
import { Activity, Flame, ShieldCheck, Zap, Compass, RefreshCw } from 'lucide-react';

export const SpatialFluxStudioPage: React.FC = () => {
  const [sampleId, setSampleId] = useState('TME-PDAC-Resection-004');
  const [organContext, setOrganContext] = useState('Pancreatic Ductal Adenocarcinoma');
  const [cellsCount, setCellsCount] = useState(2500);
  const [radiusUm, setRadiusUm] = useState(300.0);
  const [solving, setSolving] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSolve = async () => {
    setSolving(true);
    try {
      const res = await fetch('/api/v1/spatial-flux/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tissue_sample_id: sampleId,
          organ_context: organContext,
          single_cells_count: cellsCount,
          perfusion_radius_um: radiusUm,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSolving(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Flame className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Single-Cell High-Resolution Spatial Flux Balance Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 150: Microenvironmental O2/Glucose Diffusion Constraints, Warburg Phenotyping & ATP Kinetic Optimization
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-amber-400" />
              <span>Spatial Microenvironment Model</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tissue Sample ID</label>
                <input
                  type="text"
                  value={sampleId}
                  onChange={(e) => setSampleId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Organ Context / Malignancy</label>
                <input
                  type="text"
                  value={organContext}
                  onChange={(e) => setOrganContext(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Simulated Single Cells</label>
                <input
                  type="number"
                  value={cellsCount}
                  onChange={(e) => setCellsCount(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Perfusion Gradient Radius (µm)</label>
                <input
                  type="number"
                  value={radiusUm}
                  onChange={(e) => setRadiusUm(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <button
                onClick={handleSolve}
                disabled={solving}
                className="w-full py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
              >
                {solving ? 'Solving Linear Program (FBA)...' : 'Compute Spatial Flux Balance'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-amber-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-amber-400">Metabolic Flux Steady-State Rates</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Glycolytic Flux</p>
                      <p className="text-lg font-bold text-white mt-1">{result.mean_glycolytic_flux} mmol/gDW/h</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">OXPHOS Flux</p>
                      <p className="text-lg font-bold text-amber-400 mt-1">{result.mean_oxphos_flux} mmol/gDW/h</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Lactate Secretion</p>
                      <p className="text-lg font-bold text-rose-400 mt-1">{result.lactate_secretion_rate} mmol/gDW/h</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">ATP Generation</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.atp_generation_rate} mmol/gDW/h</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Microenvironment Perfusion Zones</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Microdomain</th>
                          <th className="px-4 py-3">Distance (µm)</th>
                          <th className="px-4 py-3">O2 (µM)</th>
                          <th className="px-4 py-3">Glucose (mM)</th>
                          <th className="px-4 py-3">Warburg Score</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.microdomains.map((m: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-medium text-slate-200">{m.domain_name}</td>
                            <td className="px-4 py-3.5 text-slate-400">{m.radial_distance_um} µm</td>
                            <td className="px-4 py-3.5 text-cyan-400">{m.oxygen_concentration_uM} µM</td>
                            <td className="px-4 py-3.5 text-slate-300">{m.glucose_concentration_mM} mM</td>
                            <td className="px-4 py-3.5 font-bold text-amber-400">{(m.warburg_phenotype_score * 100).toFixed(0)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure tumor tissue perfusion parameters and solve spatial flux balance LP.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpatialFluxStudioPage;
