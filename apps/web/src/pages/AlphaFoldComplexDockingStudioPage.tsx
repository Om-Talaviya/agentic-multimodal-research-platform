import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, Layers, Sparkles, BarChart2, GitCommit, CheckCircle2 } from 'lucide-react';

interface Contact {
  chain_a_residue: string;
  chain_b_residue: string;
  inter_residue_distance_angstrom: number;
  predicted_aligned_error_angstrom: number;
  interaction_type: string;
  contact_plddt: number;
}

interface EnergyMetric {
  energy_component: string;
  value_kcal_mol: number;
  favorable_flag: string;
}

export const AlphaFoldComplexDockingStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('PD-1 / PD-L1 Complex Interface Simulation');
  const [complexName, setComplexName] = useState('PD-1 / PD-L1 Complex');
  const [chainA, setChainA] = useState('PDCD1_HUMAN (Chain A)');
  const [chainB, setChainB] = useState('CD274_HUMAN (Chain B)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunDocking = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/alphafold-complex-docking/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          target_complex_name: complexName,
          chain_a_name: chainA,
          chain_b_name: chainB,
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
          <div className="flex items-center gap-2 text-indigo-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Layers className="w-4 h-4" /> Structural Biology & Multimer Assembly
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">AlphaFold Complex Docking Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Predict multimeric protein-protein complex interfaces, cross-chain PAE matrices, and binding free energy.
          </p>
        </div>
        <button
          onClick={handleRunDocking}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Predict Multimer Complex
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Complex Name</label>
          <input
            type="text"
            value={complexName}
            onChange={(e) => setComplexName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Receptor Chain (A)</label>
          <input
            type="text"
            value={chainA}
            onChange={(e) => setChainA(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Ligand Chain (B)</label>
          <input
            type="text"
            value={chainB}
            onChange={(e) => setChainB(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" /> Interface Contact Principles (ipTM & PAE)
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              AlphaFold-Multimer evaluates the relative orientation and interaction quality between protein subunits via the interface predicted Template Modeling score (ipTM). Low Predicted Aligned Error (PAE &lt; 3.0 Å) across inter-chain residue pairs validates reliable quaternary assembly conformation.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Complex Type</div>
              <div className="text-xl font-bold text-white mt-1">Heterodimer</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Buried Surface Area</div>
              <div className="text-xl font-bold text-indigo-400 mt-1">~1,840 Å²</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Confidence Metric</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">ipTM + pLDDT</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">ipTM Score</div>
              <div className="text-2xl font-black text-indigo-400 mt-2">{result.mean_iptm_score}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Interface pLDDT</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{result.mean_plddt_interface}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Buried Area</div>
              <div className="text-2xl font-black text-white mt-2">{result.buried_surface_area_angstrom2} Å²</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Confidence Tier</div>
              <div className="text-2xl font-black text-cyan-400 mt-2">High Confidence</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <GitCommit className="w-5 h-5 text-indigo-400" /> Key Interface Contact Residues
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                      <th className="pb-3 font-semibold">Chain A</th>
                      <th className="pb-3 font-semibold">Chain B</th>
                      <th className="pb-3 font-semibold">Distance</th>
                      <th className="pb-3 font-semibold">PAE</th>
                      <th className="pb-3 font-semibold">Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.contacts?.map((c: Contact, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 font-mono text-cyan-300">{c.chain_a_residue}</td>
                        <td className="py-3 font-mono text-purple-300">{c.chain_b_residue}</td>
                        <td className="py-3 text-slate-300">{c.inter_residue_distance_angstrom} Å</td>
                        <td className="py-3 text-emerald-400 font-bold">{c.predicted_aligned_error_angstrom} Å</td>
                        <td className="py-3 text-slate-400 text-xs">{c.interaction_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" /> Binding Free Energy Decomposition
              </h3>
              <div className="space-y-3">
                {result.energy_metrics?.map((e: EnergyMetric, idx: number) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-300 text-sm">{e.energy_component}</span>
                    <span className={`font-mono font-bold ${e.value_kcal_mol < 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {e.value_kcal_mol} kcal/mol
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

export default AlphaFoldComplexDockingStudioPage;
