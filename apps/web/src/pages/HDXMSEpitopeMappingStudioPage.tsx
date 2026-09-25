import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, Waves, Microscope, BarChart2, CheckCircle2, Bookmark } from 'lucide-react';

interface Peptide {
  peptide_sequence: string;
  start_residue: number;
  end_residue: number;
  deuterium_uptake_apo_pct: number;
  deuterium_uptake_bound_pct: number;
  delta_deuterium_protection_pct: number;
  confidence_p_value: number;
}

interface Hotspot {
  residue_name: string;
  protection_factor_log2: number;
  solvent_accessibility_change: string;
}

export const HDXMSEpitopeMappingStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('SARS-CoV-2 Spike RBD Neutralizing mAb Epitope Mapping');
  const [proteinName, setProteinName] = useState('Spike RBD / Neutralizing mAb');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunMapping = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/hdx-ms-epitope-mapping/map-epitope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          target_protein_name: proteinName,
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
          <div className="flex items-center gap-2 text-teal-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Waves className="w-4 h-4" /> Biophysics & Conformational Mass Spectrometry
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">HDX-MS Epitope Mapping Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Map conformational antibody epitopes and allosteric dynamics via Hydrogen-Deuterium Exchange mass spectrometry.
          </p>
        </div>
        <button
          onClick={handleRunMapping}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-teal-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Map Epitope Footprint
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-teal-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Target Antigen-Antibody</label>
          <input
            type="text"
            value={proteinName}
            onChange={(e) => setProteinName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-teal-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <Microscope className="w-5 h-5 text-teal-400" /> HDX-MS Deuteration Protection Principles
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Hydrogen-Deuterium Exchange Mass Spectrometry measures the exchange rate of backbone amide hydrogens with deuterium oxide ($D_2O$). Epitope engagement or ligand-induced rigidification shields amides from solvent exchange, manifesting as a significant reduction in mass increase ($\Delta D \% &gt; 30\%$).
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Labeling Timepoints</div>
              <div className="text-xl font-bold text-white mt-1">10s – 4hr Kinetic</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Protease Digestion</div>
              <div className="text-xl font-bold text-teal-400 mt-1">Online Pepsin MS</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Protection Cutoff</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">ΔD &gt; 25% (p &lt; 0.01)</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Peptides Screened</div>
              <div className="text-2xl font-black text-white mt-2">{result.peptides_monitored_count}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Mean Protection ΔD</div>
              <div className="text-2xl font-black text-teal-400 mt-2">{result.mean_deuteration_protection_pct}%</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Hotspot Residues</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{result.hotspots?.length || 4} Residues</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Epitope Footprint</div>
              <div className="text-2xl font-black text-cyan-400 mt-2">RBD 464-506</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-teal-400" /> Peptic Fragment Differential Uptake (ΔD)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                      <th className="pb-3 font-semibold">Residues</th>
                      <th className="pb-3 font-semibold">Sequence</th>
                      <th className="pb-3 font-semibold">Apo Uptake</th>
                      <th className="pb-3 font-semibold">Bound</th>
                      <th className="pb-3 font-semibold">ΔD Protection</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.peptides?.map((p: Peptide, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 font-mono text-xs text-teal-300">{p.start_residue}–{p.end_residue}</td>
                        <td className="py-3 font-mono text-xs text-slate-300 max-w-[120px] truncate">{p.peptide_sequence}</td>
                        <td className="py-3 text-slate-400 text-xs">{p.deuterium_uptake_apo_pct}%</td>
                        <td className="py-3 text-slate-400 text-xs">{p.deuterium_uptake_bound_pct}%</td>
                        <td className="py-3 font-bold text-emerald-400">+{p.delta_deuterium_protection_pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Bookmark className="w-5 h-5 text-emerald-400" /> Key Epitope Hotspot Residues
              </h3>
              <div className="space-y-3">
                {result.hotspots?.map((h: Hotspot, idx: number) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <div>
                      <span className="text-teal-300 font-mono font-bold text-sm">{h.residue_name}</span>
                      <p className="text-slate-400 text-xs mt-0.5">{h.solvent_accessibility_change}</p>
                    </div>
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      log₂ PF = +{h.protection_factor_log2}
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

export default HDXMSEpitopeMappingStudioPage;
