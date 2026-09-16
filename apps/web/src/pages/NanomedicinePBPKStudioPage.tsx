import React, { useState, useEffect } from 'react';
import { Activity, Sparkles, Box, ShieldCheck, PieChart, BarChart2, Layers, Cpu } from 'lucide-react';

interface Compartment {
  id: string;
  organ_name: string;
  auc_ug_h_ml: number;
  cmax_ug_ml: number;
  tmax_hours: number;
  organ_to_plasma_ratio: number;
  fraction_of_dose_pct: number;
}

interface Clearance {
  id: string;
  pathway_name: string;
  clearance_fraction_pct: number;
  half_life_hours: number;
}

interface Simulation {
  id: string;
  formulation_name: string;
  carrier_type: string;
  hydrodynamic_diameter_nm: number;
  zeta_potential_mv: number;
  pegylation_density_pct: number;
  dose_mg_kg: number;
  tumor_epr_permeability_index: number;
  created_at: string;
  compartments?: Compartment[];
  clearance_pathways?: Clearance[];
}

export const NanomedicinePBPKStudioPage: React.FC = () => {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [selectedSim, setSelectedSim] = useState<Simulation | null>(null);
  const [formulationName, setFormulationName] = useState('LNP-mRNA-Oncology-01');
  const [diameterNm, setDiameterNm] = useState(85.0);
  const [zetaMv, setZetaMv] = useState(-3.5);
  const [pegPct, setPegPct] = useState(1.5);
  const [doseMgKg, setDoseMgKg] = useState(1.0);
  const [loading, setLoading] = useState(false);

  const fetchSimulations = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/pbpk-nanomedicine/simulations');
      if (res.ok) {
        const data = await res.json();
        setSimulations(data);
        if (data.length > 0 && !selectedSim) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/pbpk-nanomedicine/simulations/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedSim(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSimulations();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/pbpk-nanomedicine/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          formulation_name: formulationName,
          carrier_type: 'Lipid Nanoparticle (LNP)',
          hydrodynamic_diameter_nm: Number(diameterNm),
          zeta_potential_mv: Number(zetaMv),
          pegylation_density_pct: Number(pegPct),
          dose_mg_kg: Number(doseMgKg),
          tumor_epr_permeability_index: 0.85,
        }),
      });
      if (res.ok) {
        await fetchSimulations();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-950/60 border border-cyan-500/40 rounded-xl text-cyan-400">
            <Box className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-300 bg-clip-text text-transparent">
              Nanomedicine PBPK Biodistribution Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 60 • 7-compartment PBPK ODE simulation, EPR tumor vascular targeting & MPS hepatic clearance modeling
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-cyan-300">
            <Layers className="w-5 h-5" /> Run PBPK Simulation
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Formulation Name</label>
              <input
                type="text"
                value={formulationName}
                onChange={(e) => setFormulationName(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase">Diameter (nm)</label>
                <input
                  type="number"
                  value={diameterNm}
                  onChange={(e) => setDiameterNm(parseFloat(e.target.value))}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase">Zeta (mV)</label>
                <input
                  type="number"
                  step="0.5"
                  value={zetaMv}
                  onChange={(e) => setZetaMv(parseFloat(e.target.value))}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase">PEG Density (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={pegPct}
                  onChange={(e) => setPegPct(parseFloat(e.target.value))}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase">Dose (mg/kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={doseMgKg}
                  onChange={(e) => setDoseMgKg(parseFloat(e.target.value))}
                  className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Solving PBPK ODEs...' : 'Solve PBPK Biodistribution'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">PBPK Simulations</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {simulations.map((sim) => (
                <div
                  key={sim.id}
                  onClick={() => fetchDetail(sim.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedSim?.id === sim.id
                      ? 'bg-cyan-950/40 border-cyan-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{sim.formulation_name}</span>
                    <span className="text-cyan-400 font-mono">{sim.hydrodynamic_diameter_nm}nm</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">Dose: {sim.dose_mg_kg} mg/kg | PEG {sim.pegylation_density_pct}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Compartments Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-cyan-300">
              <Activity className="w-5 h-5" /> 7-Compartment Pharmacokinetic Biodistribution
            </h2>
            {selectedSim && (
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                Formulation: {selectedSim.carrier_type}
              </span>
            )}
          </div>

          {selectedSim?.compartments && selectedSim.compartments.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Organ Compartment</th>
                    <th className="p-3">AUC (μg·h/mL)</th>
                    <th className="p-3">Cmax (μg/mL)</th>
                    <th className="p-3">Tmax (h)</th>
                    <th className="p-3">Tissue/Plasma</th>
                    <th className="p-3">% Injected Dose</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedSim.compartments.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-semibold text-slate-200">
                        {c.organ_name.includes('Tumor') ? (
                          <span className="text-pink-300 font-bold">{c.organ_name}</span>
                        ) : c.organ_name.includes('Liver') ? (
                          <span className="text-amber-300">{c.organ_name}</span>
                        ) : (
                          c.organ_name
                        )}
                      </td>
                      <td className="p-3 font-mono text-cyan-300">{c.auc_ug_h_ml.toLocaleString()}</td>
                      <td className="p-3 font-mono text-slate-300">{c.cmax_ug_ml}</td>
                      <td className="p-3 font-mono text-slate-400">{c.tmax_hours}h</td>
                      <td className="p-3 font-mono font-bold text-slate-200">{c.organ_to_plasma_ratio}x</td>
                      <td className="p-3 font-mono text-emerald-400 font-bold">{c.fraction_of_dose_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No simulation loaded. Run a formulation above.</div>
          )}

          {/* Clearance Pathways */}
          {selectedSim?.clearance_pathways && selectedSim.clearance_pathways.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-cyan-300 uppercase tracking-wider flex items-center gap-2">
                <PieChart className="w-4 h-4 text-blue-400" /> Mononuclear Phagocyte Clearance Pathways
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedSim.clearance_pathways.map((cl) => (
                  <div key={cl.id} className="p-3 bg-slate-950/80 border border-cyan-500/30 rounded-xl flex justify-between items-center text-xs">
                    <div>
                      <div className="font-semibold text-slate-200">{cl.pathway_name}</div>
                      <div className="text-[11px] text-slate-400">Elimination t½: {cl.half_life_hours}h</div>
                    </div>
                    <div className="font-mono text-cyan-400 font-bold text-sm">{cl.clearance_fraction_pct}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
