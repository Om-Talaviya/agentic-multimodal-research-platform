import React, { useState, useEffect } from 'react';
import { Activity, Layers, Dna, BarChart3, TrendingDown, Plus, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface UptakeCurve {
  peptide_sequence: string;
  start_res: number;
  end_res: number;
  timepoint_seconds: number;
  deuterium_uptake_da: number;
  fractional_uptake_pct: number;
  protection_factor_ln_p: number;
}

interface ProtectionMap {
  residue_number: number;
  amino_acid: string;
  protection_factor: number;
  solvent_accessibility_level: string;
  delta_uptake_apo_vs_bound: number;
}

interface HDXExperiment {
  id: string;
  protein_name: string;
  uniprot_id?: string;
  state_condition: string;
  total_peptides: number;
  sequence_coverage_pct: number;
  redundancy_score: number;
  status: string;
  uptake_curves?: UptakeCurve[];
  protection_maps?: ProtectionMap[];
}

export const HDXMSStudioPage: React.FC = () => {
  const [experiments, setExperiments] = useState<HDXExperiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<HDXExperiment | null>(null);
  const [loading, setLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [proteinName, setProteinName] = useState('PCSK9-Catalytic-Domain');
  const [stateCondition, setStateCondition] = useState('LIGAND_BOUND');

  useEffect(() => {
    fetchExperiments();
  }, []);

  const fetchExperiments = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/hdx-ms/experiments');
      setExperiments(res.data);
      if (res.data.length > 0) {
        fetchExperimentDetail(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load HDX experiments', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchExperimentDetail = async (id: string) => {
    try {
      const res = await axios.get(`/api/v1/hdx-ms/experiments/${id}`);
      setSelectedExp(res.data);
    } catch (err) {
      console.error('Failed to fetch HDX details', err);
    }
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const payload = {
        protein_name: proteinName,
        uniprot_id: 'P07550',
        state_condition: stateCondition,
        peptides: [
          { peptide_sequence: 'MGTVSSRRA', start_res: 1, end_res: 9, is_binding_site: false },
          { peptide_sequence: 'APGATNEKLFFL', start_res: 10, end_res: 21, is_binding_site: true },
          { peptide_sequence: 'CASSLIGVSSYN', start_res: 22, end_res: 33, is_binding_site: true },
          { peptide_sequence: 'EQFFGPGTRLTV', start_res: 34, end_res: 45, is_binding_site: false },
          { peptide_sequence: 'LGQGTKVEIKR', start_res: 46, end_res: 56, is_binding_site: false }
        ],
        timepoints: [10, 60, 300, 1800, 7200]
      };
      const res = await axios.post('/api/v1/hdx-ms/simulate', payload);
      setExperiments([res.data, ...experiments]);
      setSelectedExp(res.data);
    } catch (err) {
      console.error('Failed to run HDX simulation', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Autonomous Proteome-Wide HDX-MS Conformational Studio</h1>
              <p className="text-sm text-slate-400">
                Phase 105 • Deuterium Exchange Kinetics (%D), Woods Plots, Protection Factors & Epitope Footprinting
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-lg transition disabled:opacity-50"
          >
            {isSimulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Simulate HDX Timecourse
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      {selectedExp && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Sequence Coverage</div>
            <div className="text-2xl font-bold text-cyan-400 mt-1">{selectedExp.sequence_coverage_pct}%</div>
            <div className="text-xs text-slate-500 mt-1">Peptide Map Completeness</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Peptides Analyzed</div>
            <div className="text-2xl font-bold text-white mt-1">{selectedExp.total_peptides}</div>
            <div className="text-xs text-slate-500 mt-1">Redundancy: {selectedExp.redundancy_score}x</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">State / Conformation</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{selectedExp.state_condition}</div>
            <div className="text-xs text-slate-500 mt-1">Ligand / Binding Condition</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Exchange Timepoints</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">5 (10s – 7200s)</div>
            <div className="text-xs text-slate-500 mt-1">Deuteration Kinetic Span</div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Experiments List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Dna className="w-5 h-5 text-cyan-400" />
            HDX Experiments
          </h2>
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading experiments...</div>
          ) : experiments.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No experiments available. Run simulation above.</div>
          ) : (
            <div className="space-y-3">
              {experiments.map((exp) => (
                <div
                  key={exp.id}
                  onClick={() => fetchExperimentDetail(exp.id)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition ${
                    selectedExp?.id === exp.id
                      ? 'bg-cyan-950/40 border-cyan-500/50'
                      : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-semibold text-white text-sm truncate">{exp.protein_name}</div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-cyan-300 font-mono">
                      {exp.state_condition}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>{exp.total_peptides} peptides</span>
                    <span>Coverage: {exp.sequence_coverage_pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Woods Plot & Uptake Curves */}
        <div className="lg:col-span-2 space-y-6">
          {selectedExp ? (
            <>
              {/* Residue Protection Map (Woods Plot representation) */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingDown className="w-5 h-5 text-cyan-400" />
                  Woods Plot: Differential Deuterium Uptake (Δ%D Footprint)
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                  {selectedExp.protection_maps && selectedExp.protection_maps.length > 0 ? (
                    selectedExp.protection_maps.map((m, idx) => (
                      <div
                        key={idx}
                        className={`p-2.5 rounded-lg border text-center ${
                          m.delta_uptake_apo_vs_bound > 15
                            ? 'bg-cyan-950/60 border-cyan-500/80 text-cyan-300'
                            : m.delta_uptake_apo_vs_bound > 5
                            ? 'bg-slate-800 border-indigo-500/40 text-indigo-300'
                            : 'bg-slate-800/40 border-slate-700/40 text-slate-400'
                        }`}
                      >
                        <div className="text-xs font-mono font-bold">Res {m.residue_number}</div>
                        <div className="text-xs text-slate-400 mt-1">Δ {m.delta_uptake_apo_vs_bound}%</div>
                        <div className="text-[10px] uppercase mt-1 tracking-wider font-semibold opacity-80">
                          {m.solvent_accessibility_level}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-slate-500 col-span-6 text-center py-4">No protection maps found.</div>
                  )}
                </div>
              </div>

              {/* Deuterium Uptake Kinetic Curves Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-cyan-400" />
                  Peptide Exchange Kinetics (%D across Timepoints)
                </h2>
                <div className="overflow-x-auto max-h-72">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 font-semibold sticky top-0">
                      <tr>
                        <th className="py-2 px-3">Peptide Sequence</th>
                        <th className="py-2 px-3">Span</th>
                        <th className="py-2 px-3">Time (s)</th>
                        <th className="py-2 px-3">Uptake (Da)</th>
                        <th className="py-2 px-3">% Deuteration</th>
                        <th className="py-2 px-3">Protection ln(P)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {selectedExp.uptake_curves && selectedExp.uptake_curves.length > 0 ? (
                        selectedExp.uptake_curves.map((c, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2 px-3 font-mono text-cyan-300">{c.peptide_sequence}</td>
                            <td className="py-2 px-3 text-xs font-mono">{c.start_res}–{c.end_res}</td>
                            <td className="py-2 px-3 font-mono">{c.timepoint_seconds}s</td>
                            <td className="py-2 px-3 font-mono">{c.deuterium_uptake_da} Da</td>
                            <td className="py-2 px-3 font-mono text-emerald-400 font-semibold">{c.fractional_uptake_pct}%</td>
                            <td className="py-2 px-3 font-mono">{c.protection_factor_ln_p}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="py-4 text-center text-slate-500">
                            No kinetic curves recorded.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Select or simulate an HDX-MS experiment to inspect deuterium uptake curves and protection factor maps.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
