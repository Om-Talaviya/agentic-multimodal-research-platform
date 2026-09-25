import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, RefreshCw, BarChart2, Flame, Crosshair, AlertTriangle } from 'lucide-react';

interface Reaction {
  reaction_id: string;
  reaction_name: string;
  subsystem: string;
  lower_bound: number;
  upper_bound: number;
  computed_flux_mmol_gdw_hr: number;
  shadow_price: number;
}

interface Vulnerability {
  target_enzyme_gene: string;
  target_reaction: string;
  growth_inhibition_percent: number;
  synthetic_lethal_partner: string | null;
  druggability_verdict: string;
}

export const MetabolicFluxFBAStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Warburg Glycolysis & Glutaminolysis FBA Simulation');
  const [organismModel, setOrganismModel] = useState('Human Recon3D');
  const [phenotype, setPhenotype] = useState('Warburg Glycolytic Cancer');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/metabolic-flux-fba/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          organism_model: organismModel,
          cellular_phenotype: phenotype,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 text-amber-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Flame className="w-4 h-4" /> Systems Metabolism & Genome-Scale FBA
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Metabolic Flux Balance Analysis (FBA) Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Simulate stoichiometric reaction network fluxes, biomass maximization, and single-gene synthetic lethality vulnerabilities.
          </p>
        </div>
        <button
          onClick={handleRunSimulation}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Solve Flux Balance LP
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-amber-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Organism Reconstruction</label>
          <input
            type="text"
            value={organismModel}
            onChange={(e) => setOrganismModel(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-amber-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Cellular Phenotype</label>
          <input
            type="text"
            value={phenotype}
            onChange={(e) => setPhenotype(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-amber-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-amber-400" /> Linear Programming Optimization Principles
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Flux Balance Analysis solves $\max c^T v$ subject to the steady-state stoichiometric constraint $S \cdot v = 0$ and boundary conditions $v_{lb} \le v \le v_{ub}$. Shadow prices identify metabolic bottlenecks, while in-silico gene deletions uncover targetable vulnerabilities and synthetic lethal pairs.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Objective Target</div>
              <div className="text-xl font-bold text-white mt-1">Biomass Production</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Recon Model</div>
              <div className="text-xl font-bold text-amber-400 mt-1">Recon3D (13k rxns)</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Solver Backend</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">Simplex / GLPK LP</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Optimal Growth Rate</div>
              <div className="text-2xl font-black text-white mt-2">{result.optimal_growth_rate_hr} hr⁻¹</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Total Reaction Flux</div>
              <div className="text-2xl font-black text-amber-400 mt-2">{result.summary_metrics?.total_reaction_flux_mmol_gdw_hr} mmol/gDW/hr</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Glycolysis Fraction</div>
              <div className="text-2xl font-black text-orange-400 mt-2">{((result.summary_metrics?.glycolytic_flux_fraction || 0.65) * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Vulnerability Hits</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{result.vulnerabilities?.length || 3} Targets</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-amber-400" /> Solved Reaction Flux Constraints
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                      <th className="pb-3 font-semibold">Reaction ID</th>
                      <th className="pb-3 font-semibold">Subsystem</th>
                      <th className="pb-3 font-semibold">Flux (mmol/gDW/hr)</th>
                      <th className="pb-3 font-semibold">Shadow Price</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.reactions?.map((r: Reaction, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 font-mono text-amber-300 text-xs">{r.reaction_id}</td>
                        <td className="py-3 text-slate-400 text-xs">{r.subsystem}</td>
                        <td className="py-3 font-bold text-white">{r.computed_flux_mmol_gdw_hr}</td>
                        <td className="py-3 font-mono text-cyan-400 text-xs">{r.shadow_price}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Crosshair className="w-5 h-5 text-rose-400" /> Knockout Vulnerability Targets
              </h3>
              <div className="space-y-3">
                {result.vulnerabilities?.map((v: Vulnerability, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-amber-300 font-bold text-sm">{v.target_enzyme_gene} ({v.target_reaction})</span>
                      <span className="text-rose-400 font-mono font-bold text-xs">-{v.growth_inhibition_percent}% Growth</span>
                    </div>
                    {v.synthetic_lethal_partner && (
                      <p className="text-slate-400 text-xs">
                        Synthetic lethal with: <span className="text-cyan-300">{v.synthetic_lethal_partner}</span>
                      </p>
                    )}
                    <span className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {v.druggability_verdict}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetabolicFluxFBAStudioPage;
