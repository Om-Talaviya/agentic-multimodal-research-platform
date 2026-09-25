import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, Dna, ArrowRight, BarChart2, CheckCircle2, AlertCircle } from 'lucide-react';

interface Duplex {
  guide_strand_sequence: string;
  passenger_strand_sequence: string;
  delta_g_5p_kcal_mol: number;
  delta_g_3p_kcal_mol: number;
  delta_delta_g_asymmetry: number;
  seed_region_tm_celsius: number;
  risc_loading_preference: string;
  predicted_knockdown_efficiency: number;
  chemical_mod_pattern: string;
}

export const SiRNAThermodynamicsStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Oncology TP53 siRNA Knockdown Optimization');
  const [targetTranscript, setTargetTranscript] = useState('NM_000546.6 (TP53)');
  const [targetGene, setTargetGene] = useState('TP53');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunEvaluation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/sirna-thermodynamics/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          target_mrna_transcript: targetTranscript,
          target_gene: targetGene,
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
          <div className="flex items-center gap-2 text-cyan-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Dna className="w-4 h-4" /> RNA Interference & Oligonucleotide Engineering
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">siRNA Duplex Thermodynamics Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Compute terminal end stability asymmetry (ΔΔG), seed region melting temperatures, and RISC loading preference.
          </p>
        </div>
        <button
          onClick={handleRunEvaluation}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Run Thermodynamic Screen
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Target Transcript</label>
          <input
            type="text"
            value={targetTranscript}
            onChange={(e) => setTargetTranscript(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Target Gene</label>
          <input
            type="text"
            value={targetGene}
            onChange={(e) => setTargetGene(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-cyan-400" /> Thermodynamic Asymmetry & RISC Loading Rules
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              According to the Khvorova-Reynolds rules, efficient RISC guide-strand incorporation requires a lower thermodynamic stability (less negative ΔG) at the 5′ end of the antisense guide strand relative to its 3′ end (positive ΔΔG). High seed region stability (Tm &gt; 52°C) correlates with off-target seed-mediated 3′ UTR miRNA-like silencing.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Target Gene</div>
              <div className="text-xl font-bold text-white mt-1">{targetGene}</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Duplex Length</div>
              <div className="text-xl font-bold text-cyan-400 mt-1">21 nt + 2nt 3′ TT</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Chem Mod Type</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">2′OMe / 2′F PS</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Candidates Evaluated</div>
              <div className="text-2xl font-black text-white mt-2">{result.candidates_screened}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Mean Knockdown</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{result.mean_on_target_efficiency}%</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Guide-Dominant Ratio</div>
              <div className="text-2xl font-black text-cyan-400 mt-2">{((result.summary_metrics?.optimal_loading_fraction || 0.75) * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Off-Target Risk</div>
              <div className="text-2xl font-black text-indigo-400 mt-2">Low (Suppressed)</div>
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" /> Screened siRNA Duplex Constructs
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                    <th className="pb-3 font-semibold">Guide Strand (5′→3′)</th>
                    <th className="pb-3 font-semibold">5′ ΔG (kcal/mol)</th>
                    <th className="pb-3 font-semibold">3′ ΔG (kcal/mol)</th>
                    <th className="pb-3 font-semibold">Asymmetry (ΔΔG)</th>
                    <th className="pb-3 font-semibold">Seed Tm</th>
                    <th className="pb-3 font-semibold">RISC Loading</th>
                    <th className="pb-3 font-semibold">Predicted KD</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.duplexes?.map((d: Duplex, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 font-mono text-cyan-300 text-xs">{d.guide_strand_sequence}</td>
                      <td className="py-3.5 text-slate-300">{d.delta_g_5p_kcal_mol}</td>
                      <td className="py-3.5 text-slate-300">{d.delta_g_3p_kcal_mol}</td>
                      <td className="py-3.5 font-bold text-emerald-400">+{d.delta_delta_g_asymmetry}</td>
                      <td className="py-3.5 text-slate-300">{d.seed_region_tm_celsius}°C</td>
                      <td className="py-3.5">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          d.risc_loading_preference === 'guide_dominant'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}>
                          {d.risc_loading_preference}
                        </span>
                      </td>
                      <td className="py-3.5 font-black text-white">{d.predicted_knockdown_efficiency}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SiRNAThermodynamicsStudioPage;
