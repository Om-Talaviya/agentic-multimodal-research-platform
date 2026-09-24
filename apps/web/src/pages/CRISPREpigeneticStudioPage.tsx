import React, { useState } from 'react';
import { BookmarkCheck, ShieldCheck, Zap, Dna, Activity, Lock } from 'lucide-react';

export const CRISPREpigeneticStudioPage: React.FC = () => {
  const [locusName, setLocusName] = useState('B2M Promoter CpG Island (Immune Evasion Silencing)');
  const [effector, setEffector] = useState('dCas9-DNMT3A-DNMT3L Methyltransferase');
  const [gRNA, setGRNA] = useState('GGCUAGCGUAGCUAGCUAGCGUU');
  const [cpgCount, setCpgCount] = useState(10);
  const [editing, setEditing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleEdit = async () => {
    setEditing(true);
    try {
      const res = await fetch('/api/v1/crispr-epigenetic/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_locus_name: locusName,
          catalytic_effector: effector,
          guide_rna_sequence: gRNA,
          target_cpg_count: cpgCount,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setEditing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <Lock className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Epigenetic CRISPR Base & Prime Editing DNA Methylation Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 159: Targeted dCas9-DNMT3A/TET1 CpG Methylation, Mitotic Memory Retention & Off-Target Epimutation Safeguards
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <span>Epigenetic Editing Design</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Genomic Locus / Gene</label>
                <input
                  type="text"
                  value={locusName}
                  onChange={(e) => setLocusName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Catalytic Effector Domain</label>
                <input
                  type="text"
                  value={effector}
                  onChange={(e) => setEffector(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Guide RNA (20nt protospacer)</label>
                <input
                  type="text"
                  value={gRNA}
                  onChange={(e) => setGRNA(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm font-mono text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Targeted CpG Dinucleotides</label>
                <input
                  type="number"
                  value={cpgCount}
                  onChange={(e) => setCpgCount(parseInt(e.target.value) || 10)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <button
                onClick={handleEdit}
                disabled={editing}
                className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                {editing ? 'Simulating Methylation Maintenance...' : 'Execute Epigenetic CRISPR Edit'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-emerald-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-emerald-400">Epigenetic Silencing & Stability</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Methylation Gain</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">+{result.target_methylation_change_pct}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Transcript Repression</p>
                      <p className="text-lg font-bold text-white mt-1">{result.transcriptional_repression_log2fc} log2FC</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mitotic Memory</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.mitotic_memory_retention_days} Days</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Off-Target Drift</p>
                      <p className="text-lg font-bold text-slate-300 mt-1">{result.off_target_epimutation_rate_pct}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">CpG Methylation Profile Status</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Genomic Pos (bp)</th>
                          <th className="px-4 py-3">Baseline</th>
                          <th className="px-4 py-3">Post-Edit</th>
                          <th className="px-4 py-3">Bisulfite Depth</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.cpg_profiles.map((c: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-mono text-xs text-emerald-400">{c.genomic_coordinate_bp}</td>
                            <td className="px-4 py-3.5 text-slate-400">{c.baseline_methylation_pct}%</td>
                            <td className="px-4 py-3.5 font-bold text-emerald-300">{c.post_edit_methylation_pct}%</td>
                            <td className="px-4 py-3.5 text-slate-300">{c.bisulfite_read_depth}x</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure epigenetic effector and gRNA to model targeted DNA methylation remodeling.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CRISPREpigeneticStudioPage;
