import React, { useState } from 'react';
import { 
  Zap, 
  Activity, 
  Sparkles, 
  Layers, 
  Play, 
  CheckCircle2, 
  Target,
  GitFork,
  Dna,
  Share2,
  TrendingDown
} from 'lucide-react';

interface SLPartnerNode {
  partner_gene: string;
  interaction_type: string;
  ceres_depmap_delta_score: number;
  synthetic_lethal_p_value: number;
  confidence_tier: string;
  is_validated_druggable: boolean;
}

export const SyntheticLethalityStudioPage: React.FC = () => {
  const [targetGene, setTargetGene] = useState('BRCA1');
  const [indication, setIndication] = useState('High-Grade Serous Ovarian Cancer');
  const [ceresCutoff, setCeresCutoff] = useState(-0.5);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    screen_id: string;
    target_gene: string;
    partners: SLPartnerNode[];
    cell_lines: { name: string; lineage: string; dep_pri: number; dep_part: number }[];
  } | null>({
    screen_id: 'SL-SCREEN-2026-441',
    target_gene: 'BRCA1',
    partners: [
      { partner_gene: 'PARP1', interaction_type: 'DNA Single-Strand Break Repair Trap', ceres_depmap_delta_score: -0.88, synthetic_lethal_p_value: 1.4e-12, confidence_tier: 'HIGH', is_validated_druggable: true },
      { partner_gene: 'POLQ (DNA Polymerase Theta)', interaction_type: 'Microhomology-Mediated End Joining (MMEJ)', ceres_depmap_delta_score: -0.76, synthetic_lethal_p_value: 3.8e-8, confidence_tier: 'HIGH', is_validated_druggable: true },
      { partner_gene: 'RAD52', interaction_type: 'Alternative Homologous Recombination', ceres_depmap_delta_score: -0.68, synthetic_lethal_p_value: 5.2e-6, confidence_tier: 'MODERATE', is_validated_druggable: false },
    ],
    cell_lines: [
      { name: 'MDA-MB-436', lineage: 'Breast', dep_pri: -0.92, dep_part: -0.88 },
      { name: 'OVCAR-8', lineage: 'Ovary', dep_pri: -0.85, dep_part: -0.79 },
      { name: 'HCT116', lineage: 'Colorectal', dep_pri: -0.78, dep_part: -0.82 },
      { name: 'PANC-1', lineage: 'Pancreas', dep_pri: -0.68, dep_part: -0.65 },
      { name: 'A549', lineage: 'Lung', dep_pri: -0.42, dep_part: -0.38 },
    ]
  });

  const handleRunScreen = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        screen_id: `SL-SCREEN-${Date.now().toString().slice(-6)}`,
        target_gene: targetGene,
        partners: [
          { partner_gene: 'PARP1', interaction_type: 'DNA Repair Synthetic Lethality', ceres_depmap_delta_score: -0.91, synthetic_lethal_p_value: 2.1e-13, confidence_tier: 'HIGH', is_validated_druggable: true },
          { partner_gene: 'POLQ', interaction_type: 'MMEJ Bypass Pathway', ceres_depmap_delta_score: -0.78, synthetic_lethal_p_value: 1.5e-8, confidence_tier: 'HIGH', is_validated_druggable: true },
          { partner_gene: 'CHEK1', interaction_type: 'G2/M Checkpoint Control', ceres_depmap_delta_score: -0.64, synthetic_lethal_p_value: 8.9e-6, confidence_tier: 'MODERATE', is_validated_druggable: true },
        ],
        cell_lines: [
          { name: 'OVCAR-8', lineage: 'Ovary', dep_pri: -0.89, dep_part: -0.84 },
          { name: 'MDA-MB-436', lineage: 'Breast', dep_pri: -0.94, dep_part: -0.90 },
        ]
      });
      setLoading(false);
    }, 500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                CRISPR Synthetic Lethality & Target Validation Studio
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                DepMap CERES co-dependency mapping, paralog compensation discovery, and target tractability screening (ADR 070).
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleRunScreen}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg transition-all"
        >
          <Play className="w-4 h-4 fill-current" />
          {loading ? 'Screening DepMap...' : 'Run SL Screen'}
        </button>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Target Loss-of-Function Gene</label>
          <select 
            value={targetGene} 
            onChange={(e) => setTargetGene(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-emerald-500"
          >
            <option value="BRCA1">BRCA1 (DNA Double-Strand Repair)</option>
            <option value="ARID1A">ARID1A (SWI/SNF Complex Subunit)</option>
            <option value="SMARCA4">SMARCA4 (Chromatin Remodeler)</option>
            <option value="MTAP">MTAP (9p21 Deletion / PRMT5 Lethality)</option>
            <option value="KRAS">KRAS (Oncogenic Addiction / SOS1/SHP2)</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Tumor Indication</label>
          <input 
            type="text" 
            value={indication} 
            onChange={(e) => setIndication(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">CERES Dependency Cutoff</label>
          <input 
            type="number" 
            step="0.05" 
            value={ceresCutoff} 
            onChange={(e) => setCeresCutoff(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Telemetry Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Top Vulnerability</span>
                <Target className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.partners[0].partner_gene}
              </div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> High Tractability Partner
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Max CERES Δ Score</span>
                <TrendingDown className="w-4 h-4 text-teal-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.partners[0].ceres_depmap_delta_score.toFixed(2)}
              </div>
              <p className="text-xs text-slate-400 mt-1">Selective Cancer Cell Killing</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Statistical Significance</span>
                <Sparkles className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2 font-mono">
                p &lt; 10⁻¹²
              </div>
              <p className="text-xs text-cyan-400 mt-1">FDR Benjamini-Hochberg</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Screen Identifier</span>
                <Dna className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-lg font-mono font-bold text-amber-300 mt-2 truncate">
                {result.screen_id}
              </div>
              <p className="text-xs text-slate-400 mt-1">DepMap 24Q2 Sync</p>
            </div>
          </div>

          {/* Synthetic Lethal Partners Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <GitFork className="w-4 h-4 text-emerald-400" />
                Ranked Synthetic Lethal Vulnerability Partners
              </h2>
              <span className="text-xs px-2.5 py-1 bg-slate-800 text-emerald-300 rounded-full border border-slate-700 font-mono">
                Target: {result.target_gene}
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Partner Gene</th>
                    <th className="px-4 py-3">Mechanistic SL Interaction</th>
                    <th className="px-4 py-3">CERES Δ Score</th>
                    <th className="px-4 py-3">FDR p-value</th>
                    <th className="px-4 py-3">Druggability</th>
                    <th className="px-4 py-3">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.partners.map((p, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-semibold text-white">{p.partner_gene}</td>
                      <td className="px-4 py-3 text-slate-300">{p.interaction_type}</td>
                      <td className="px-4 py-3 font-mono font-semibold text-teal-400">{p.ceres_depmap_delta_score.toFixed(2)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-400">{p.synthetic_lethal_p_value.toExponential(2)}</td>
                      <td className="px-4 py-3">
                        {p.is_validated_druggable ? (
                          <span className="px-2 py-0.5 text-xs rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                            DRUGGABLE
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs rounded bg-slate-800 text-slate-400 border border-slate-700">
                            NOVEL TARGET
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 text-xs rounded font-medium ${
                          p.confidence_tier === 'HIGH' 
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          {p.confidence_tier}
                        </span>
                      </td>
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
export default SyntheticLethalityStudioPage;
