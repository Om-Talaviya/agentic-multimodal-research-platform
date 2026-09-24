import React, { useState } from 'react';
import { ShieldCheck, Zap, Disc, Activity, Layers } from 'lucide-react';

export const CapsidAssemblyStudioPage: React.FC = () => {
  const [serotype, setSerotype] = useState('AAV9 Engineered (CNS-Tropic)');
  const [ph, setPh] = useState(7.4);
  const [temp, setTemp] = useState(37.0);
  const [vpRatio, setVpRatio] = useState('1:1:10');
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await fetch('/api/v1/capsid-assembly/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          serotype_name: serotype,
          ph_condition: ph,
          temperature_celsius: temp,
          vp1_vp2_vp3_ratio: vpRatio,
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
          <div className="p-3 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/20">
            <Disc className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              AAV Viral Capsid Thermodynamic Self-Assembly Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 151: 60-mer Icosahedral Capsomer Interfaces, Nucleation Thermodynamics & Packaging Kinetics
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-violet-400" />
              <span>Biophysical Assembly Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Capsid Serotype</label>
                <input
                  type="text"
                  value={serotype}
                  onChange={(e) => setSerotype(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Stoichiometry (VP1:VP2:VP3)</label>
                <input
                  type="text"
                  value={vpRatio}
                  onChange={(e) => setVpRatio(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Buffer pH</label>
                  <input
                    type="number"
                    step="0.1"
                    value={ph}
                    onChange={(e) => setPh(parseFloat(e.target.value) || 7.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Temp (°C)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={temp}
                    onChange={(e) => setTemp(parseFloat(e.target.value) || 37.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
                  />
                </div>
              </div>

              <button
                onClick={handleSimulate}
                disabled={simulating}
                className="w-full py-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-violet-500/20 disabled:opacity-50"
              >
                {simulating ? 'Computing Nucleation Free Energy...' : 'Simulate Capsid Assembly'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-violet-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-violet-400">Thermodynamic Free Energy & Packaging Yield</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Assembly Yield</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.assembly_yield_percent}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Total ΔG Assembly</p>
                      <p className="text-lg font-bold text-violet-400 mt-1">{result.gibbs_free_energy_kcal_mol} kcal/mol</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Full/Empty Ratio</p>
                      <p className="text-lg font-bold text-white mt-1">{result.full_empty_capsid_ratio}:1</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Symmetry Mode</p>
                      <p className="text-sm font-bold text-slate-300 mt-1">{result.triangulation_number}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Capsomer Interface Stability</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Symmetry Axis</th>
                          <th className="px-4 py-3">ΔG (kcal/mol)</th>
                          <th className="px-4 py-3">Buried Area (Å²)</th>
                          <th className="px-4 py-3">H-Bonds</th>
                          <th className="px-4 py-3">Salt Bridges</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.interfaces.map((intf: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-medium text-slate-200">{intf.symmetry_axis}</td>
                            <td className="px-4 py-3.5 text-violet-400 font-bold">{intf.delta_g_binding_kcal_mol}</td>
                            <td className="px-4 py-3.5 text-slate-300">{intf.buried_surface_area_a2} Å²</td>
                            <td className="px-4 py-3.5 text-emerald-400">{intf.hydrogen_bonds_count}</td>
                            <td className="px-4 py-3.5 text-cyan-400">{intf.salt_bridges_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure capsid serotype parameters and run self-assembly thermodynamics simulation.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CapsidAssemblyStudioPage;
