import React, { useState } from 'react';
import { Dna, ShieldCheck, Zap, Layers, Sparkles, Sliders } from 'lucide-react';

export const mRNACodonStudioPage: React.FC = () => {
  const [proteinName, setProteinName] = useState('Personalized Neoantigen / Spike mRNA');
  const [host, setHost] = useState('Homo sapiens (Human)');
  const [gcTarget, setGcTarget] = useState(58.0);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    try {
      const res = await fetch('/api/v1/mrna-codon/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_protein_name: proteinName,
          expression_host: host,
          amino_acid_sequence: 'MFVFLVLLPLVSSQCVNLTTRTQLPPAYTN',
          target_gc_percent: gcTarget,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl border border-teal-500/20">
            <Dna className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Multi-Objective mRNA Codon Optimization Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 153: CAI Harmonization, GC Content Balancing, Uridine Depletion & Minimum Free Energy Folding
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-teal-400" />
              <span>mRNA Optimization Objective</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Antigen / Protein</label>
                <input
                  type="text"
                  value={proteinName}
                  onChange={(e) => setProteinName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Host Expression System</label>
                <input
                  type="text"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target GC Content (%)</label>
                <input
                  type="number"
                  step="0.5"
                  value={gcTarget}
                  onChange={(e) => setGcTarget(parseFloat(e.target.value) || 55.0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <button
                onClick={handleOptimize}
                disabled={optimizing}
                className="w-full py-3 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-teal-500/20 disabled:opacity-50"
              >
                {optimizing ? 'Executing Genetic Algorithm...' : 'Optimize Codon Adaptation'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-teal-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-teal-400">Codon Adaptation & Translation Metrics</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Optimized CAI</p>
                      <p className="text-lg font-bold text-teal-400 mt-1">{result.optimized_cai} <span className="text-xs text-slate-500">(from {result.original_cai})</span></p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">GC Content</p>
                      <p className="text-lg font-bold text-white mt-1">{result.gc_content_percent}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Uridine Depletion</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">-{result.uridine_depletion_percent}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Secondary MFE</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.mfe_secondary_struct_kcal_mol} kcal</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Pareto-Optimal Candidate Transcripts</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Rank</th>
                          <th className="px-4 py-3">Sequence Preview (5' → 3')</th>
                          <th className="px-4 py-3">Pareto Fitness</th>
                          <th className="px-4 py-3">Dwell Time</th>
                          <th className="px-4 py-3">Immuno-Risk</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.candidate_variants.map((v: any) => (
                          <tr key={v.variant_rank} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-teal-400">#{v.variant_rank}</td>
                            <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{v.mrna_sequence_preview}</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{v.pareto_fitness_score}</td>
                            <td className="px-4 py-3.5 text-slate-300">{v.ribosome_dwell_time_ms} ms</td>
                            <td className="px-4 py-3.5 text-slate-400">{v.immunogenicity_risk_score}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure peptide antigen sequence to generate Pareto-optimal codon adaptation mRNA variants.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default mRNACodonStudioPage;
