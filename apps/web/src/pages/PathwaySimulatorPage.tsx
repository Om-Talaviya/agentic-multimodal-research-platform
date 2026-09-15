import React, { useState, useEffect } from 'react';
import { 
  GitFork, Activity, TrendingDown, Sparkles, RefreshCw, BarChart2, ShieldAlert, Cpu, Layers
} from 'lucide-react';

interface Experiment {
  id: string;
  title: string;
  cell_line: string;
  perturbation_type: string;
  omics_layers: string[];
  status: string;
}

export const PathwaySimulatorPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  
  const [title, setTitle] = useState('Dynamic ODE Simulation of KRAS-G12C Knockdown in A549 Cells');
  const [targetNode, setTargetNode] = useState('KRAS_G12C');
  const [cellLine, setCellLine] = useState('A549 (Lung Adenocarcinoma)');
  const [perturbationType, setPerturbationType] = useState('CRISPR_KO');

  const fetchExperiments = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/pathways/experiments', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setExperiments(data);
        if (data.length > 0) {
          fetchExpDetails(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchExpDetails = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/pathways/experiments/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedExp(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/pathways/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          target_node: targetNode,
          cell_line: cellLine,
          perturbation_type: perturbationType,
          time_course_hours: 48
        })
      });
      if (res.ok) {
        const created = await res.json();
        await fetchExperiments();
        await fetchExpDetails(created.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-violet-600 to-fuchsia-700 rounded-xl shadow-lg shadow-violet-900/30">
              <GitFork className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Autonomous Multi-Omics Pathway Simulator
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20 font-mono">
                  Phase 48
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Dynamic ODE Signaling Cascades, Phospho-Proteomics & Bypass Resistance Prediction
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchExperiments}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Simulation Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-violet-400" />
            Perturbation Parameters
          </h2>
          <form onSubmit={handleSimulate} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Experiment Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Node / Gene</label>
                <input
                  type="text"
                  value={targetNode}
                  onChange={(e) => setTargetNode(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Cell Model</label>
                <input
                  type="text"
                  value={cellLine}
                  onChange={(e) => setCellLine(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Perturbation Mechanism</label>
              <select
                value={perturbationType}
                onChange={(e) => setPerturbationType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-violet-500"
              >
                <option value="CRISPR_KO">CRISPR-Cas9 Gene Knockout</option>
                <option value="SMALL_MOLECULE">Targeted Small Molecule Allosteric Inhibitor</option>
                <option value="SIRNA">siRNA Transcript Degradation</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={simulating}
              className="w-full py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-600 hover:from-violet-600 hover:to-fuchsia-700 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-violet-900/20 disabled:opacity-50"
            >
              {simulating ? 'Solving Differential Equations...' : 'Simulate Signaling Cascade'}
            </button>
          </form>

          {/* Experiments List */}
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Saved Perturbations</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {experiments.map((e) => (
                <div
                  key={e.id}
                  onClick={() => fetchExpDetails(e.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                    selectedExp?.id === e.id
                      ? 'bg-violet-950/40 border-violet-500/40 text-violet-200'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{e.title}</div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800">{e.cell_line.split(' ')[0]}</span>
                    <span>{e.perturbation_type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Simulation Telemetry & Trajectories */}
        <div className="lg:col-span-2 space-y-6">
          {selectedExp ? (
            <>
              {/* Telemetry Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><TrendingDown className="w-3.5 h-3.5 text-rose-400"/> Knockdown</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedExp.simulations?.[0]?.inhibition_pct || 94.2}%
                  </div>
                  <div className="text-[10px] text-rose-400 mt-0.5">Target: {selectedExp.simulations?.[0]?.target_node || 'KRAS'}</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-violet-400"/> Phospho-ERK</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedExp.simulations?.[0]?.phospho_delta || -82.6}%
                  </div>
                  <div className="text-[10px] text-violet-400 mt-0.5">Downstream effector</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-fuchsia-400"/> Metabolic Flux</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedExp.simulations?.[0]?.flux_shift || -51.3}%
                  </div>
                  <div className="text-[10px] text-fuchsia-400 mt-0.5">Glycolysis reduction</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-emerald-400"/> Cascade Nodes</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedExp.cascades?.[0]?.node_count || 22}
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">{selectedExp.cascades?.[0]?.feedback_loops || 4} feedback loops</div>
                </div>
              </div>

              {/* Bypass Resistance Cards */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  Compensatory Bypass Resistance Mechanisms & Synthetic Lethal Pairs
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedExp.simulations?.[0]?.bypass_mechanisms?.map((b: any, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-amber-300">{b.bypass_pathway}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          +{b.activation_delta_pct}% rebound
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{b.mechanism}</p>
                      <div className="text-[10px] text-emerald-400 font-mono">
                        Rx Synergy: {b.recommended_combination}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ODE Time Series Grid */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-violet-400" />
                  Dynamic ODE Kinetic Concentration Profile (0 - 48 Hours)
                </h3>
                <div className="grid grid-cols-4 sm:grid-cols-7 gap-2 text-center mt-3">
                  {selectedExp.simulations?.[0]?.trajectories?.slice(0, 7).map((pt: any) => (
                    <div key={pt.time_hours} className="p-2 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">{pt.time_hours}h</div>
                      <div className="text-xs font-bold text-rose-400 mt-1">{(pt.target_activity * 100).toFixed(0)}%</div>
                      <div className="text-[9px] text-violet-400 mt-0.5">ERK: {(pt.phospho_erk * 100).toFixed(0)}%</div>
                      <div className="text-[9px] text-amber-400 mt-0.5">AKT: {(pt.phospho_akt_bypass * 100).toFixed(0)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500">
              <GitFork className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
              <p className="text-sm">Select or simulate a multi-omics pathway perturbation to inspect kinetic trajectories</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
