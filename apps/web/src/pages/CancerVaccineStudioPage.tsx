import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Dna, 
  Activity, 
  Sparkles, 
  Layers, 
  Play, 
  CheckCircle2, 
  AlertCircle,
  FileCode,
  Syringe,
  Target
} from 'lucide-react';

interface NeoepitopeItem {
  mutated_gene: string;
  peptide_sequence: string;
  hla_restriction: string;
  mhc_affinity_ic50_nm: number;
  immunogenicity_rank_score: number;
}

export const CancerVaccineStudioPage: React.FC = () => {
  const [patientId, setPatientId] = useState('PT-MEL-9042');
  const [tumorType, setTumorType] = useState('Cutaneous Melanoma');
  const [hlaAllele, setHlaAllele] = useState('HLA-A*02:01');
  const [linker, setLinker] = useState('AAY');
  const [adjuvant, setAdjuvant] = useState('Poly-ICLC (Hiltonol)');
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    vaccine_id: string;
    cleavability_score: number;
    immunogenicity_index: number;
    mrna_sequence: string;
    selected_epitopes: NeoepitopeItem[];
  } | null>({
    vaccine_id: 'VAC-2026-8819',
    cleavability_score: 0.91,
    immunogenicity_index: 0.94,
    mrna_sequence: 'MKWVTFISLLFLFSSAYS_KLVVVGADGVAAYFLTETLTAAYYLFPDGKLIAAYVLDLKGYP_IVGIVAGLAVLAVVVIGAVVATVMCRRKSSGGKGGSYSQAASSDSAQGSDVSLTA',
    selected_epitopes: [
      { mutated_gene: 'BRAF (V600E)', peptide_sequence: 'EDLTVKIGDF', hla_restriction: 'HLA-A*02:01', mhc_affinity_ic50_nm: 18.4, immunogenicity_rank_score: 0.96 },
      { mutated_gene: 'KRAS (G12D)', peptide_sequence: 'KLVVVGADGV', hla_restriction: 'HLA-A*02:01', mhc_affinity_ic50_nm: 24.2, immunogenicity_rank_score: 0.93 },
      { mutated_gene: 'TP53 (R248Q)', peptide_sequence: 'SQHMTEVVRQ', hla_restriction: 'HLA-A*02:01', mhc_affinity_ic50_nm: 42.1, immunogenicity_rank_score: 0.89 },
      { mutated_gene: 'NRAS (Q61R)', peptide_sequence: 'ILDTAGREEY', hla_restriction: 'HLA-A*02:01', mhc_affinity_ic50_nm: 48.7, immunogenicity_rank_score: 0.87 },
      { mutated_gene: 'MUC16 (S1248L)', peptide_sequence: 'FLTETLTVVL', hla_restriction: 'HLA-A*02:01', mhc_affinity_ic50_nm: 31.6, immunogenicity_rank_score: 0.88 },
    ]
  });

  const handleDesign = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        vaccine_id: `VAC-${Date.now().toString().slice(-6)}`,
        cleavability_score: linker === 'AAY' ? 0.92 : 0.86,
        immunogenicity_index: 0.95,
        mrna_sequence: `MKWVTFISLLFLFSSAYS_EDLTVKIGDF${linker}KLVVVGADGV${linker}SQHMTEVVRQ_IVGIVAGLAVLAVVVIGAVVATVMCRRKSSGGKGGSYSQAASSDSAQGSDVSLTA`,
        selected_epitopes: [
          { mutated_gene: 'BRAF (V600E)', peptide_sequence: 'EDLTVKIGDF', hla_restriction: hlaAllele, mhc_affinity_ic50_nm: 18.4, immunogenicity_rank_score: 0.96 },
          { mutated_gene: 'KRAS (G12D)', peptide_sequence: 'KLVVVGADGV', hla_restriction: hlaAllele, mhc_affinity_ic50_nm: 24.2, immunogenicity_rank_score: 0.93 },
          { mutated_gene: 'TP53 (R248Q)', peptide_sequence: 'SQHMTEVVRQ', hla_restriction: hlaAllele, mhc_affinity_ic50_nm: 42.1, immunogenicity_rank_score: 0.89 },
        ]
      });
      setLoading(false);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
              <Syringe className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                Personalized Neoepitope & mRNA Cancer Vaccine Studio
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Proteogenomic mutation-to-neoantigen mapping, HLA presentation scoring, and cleavable poly-epitope assembly (ADR 067).
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleDesign}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg transition-all"
        >
          <Play className="w-4 h-4 fill-current" />
          {loading ? 'Synthesizing...' : 'Assemble Vaccine'}
        </button>
      </div>

      {/* Control Configuration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Patient Identifier</label>
          <input 
            type="text" 
            value={patientId} 
            onChange={(e) => setPatientId(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-rose-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Tumor Type</label>
          <input 
            type="text" 
            value={tumorType} 
            onChange={(e) => setTumorType(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-rose-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Primary HLA Allele</label>
          <select 
            value={hlaAllele} 
            onChange={(e) => setHlaAllele(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-rose-500"
          >
            <option value="HLA-A*02:01">HLA-A*02:01 (45% Cauc)</option>
            <option value="HLA-A*24:02">HLA-A*24:02 (60% Asian)</option>
            <option value="HLA-B*07:02">HLA-B*07:02</option>
            <option value="HLA-B*08:01">HLA-B*08:01</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Poly-Epitope Linker</label>
          <select 
            value={linker} 
            onChange={(e) => setLinker(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-rose-500"
          >
            <option value="AAY">AAY (Alanine-Alanine-Tyrosine)</option>
            <option value="GPGPG">GPGPG (Flexible Spacer)</option>
            <option value="HEYMAE">HEYMAE (Proteasomal Opt)</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Adjuvant Formulation</label>
          <select 
            value={adjuvant} 
            onChange={(e) => setAdjuvant(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-rose-500"
          >
            <option value="Poly-ICLC (Hiltonol)">Poly-ICLC (Hiltonol)</option>
            <option value="QS-21 Saponin">QS-21 Saponin</option>
            <option value="GM-CSF">GM-CSF Cytokine</option>
          </select>
        </div>
      </div>

      {/* Main Results and Construct Visualizer */}
      {result && (
        <div className="space-y-6">
          {/* Key Metric Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Predicted Immunogenicity</span>
                <Sparkles className="w-4 h-4 text-rose-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {(result.immunogenicity_index * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> High CD8+ Activation Potential
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Junction Cleavability</span>
                <Layers className="w-4 h-4 text-pink-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {(result.cleavability_score * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400 mt-1">TAP & Proteasome Efficiency</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Candidate Neoepitopes</span>
                <Target className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.selected_epitopes.length} Selected
              </div>
              <p className="text-xs text-indigo-400 mt-1">Top-Ranked Somatic Mutants</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Vaccine Design ID</span>
                <Dna className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-lg font-mono font-bold text-amber-300 mt-2 truncate">
                {result.vaccine_id}
              </div>
              <p className="text-xs text-slate-400 mt-1">Ready for GMP Synthesis</p>
            </div>
          </div>

          {/* Top Ranked Neoepitopes Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Target className="w-4 h-4 text-rose-400" />
                Ranked Neoepitopes in Poly-Epitope Cassette
              </h2>
              <span className="text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded-full border border-slate-700">
                IC50 &lt; 50nM Strong Binder
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Mutated Gene</th>
                    <th className="px-4 py-3">Peptide Sequence (MT)</th>
                    <th className="px-4 py-3">HLA Restriction</th>
                    <th className="px-4 py-3">MHC IC50 Affinity</th>
                    <th className="px-4 py-3">Rank Score</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.selected_epitopes.map((ep, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-medium text-white">{ep.mutated_gene}</td>
                      <td className="px-4 py-3 font-mono text-rose-300 tracking-wide font-semibold">{ep.peptide_sequence}</td>
                      <td className="px-4 py-3 text-slate-400">{ep.hla_restriction}</td>
                      <td className="px-4 py-3">
                        <span className="text-emerald-400 font-semibold">{ep.mhc_affinity_ic50_nm.toFixed(1)} nM</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-rose-500 h-full rounded-full" style={{ width: `${ep.immunogenicity_rank_score * 100}%` }} />
                          </div>
                          <span className="text-xs font-mono">{(ep.immunogenicity_rank_score * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 text-xs rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                          INCLUDED
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Full Engineered mRNA Construct CDS */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <FileCode className="w-4 h-4 text-pink-400" />
                Engineered Poly-Epitope mRNA Open Reading Frame (ORF)
              </h2>
              <span className="text-xs text-slate-400">Signal + Tandem Epitopes + MITD Domain</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-pink-300 break-all leading-relaxed">
              {result.mrna_sequence}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default CancerVaccineStudioPage;
