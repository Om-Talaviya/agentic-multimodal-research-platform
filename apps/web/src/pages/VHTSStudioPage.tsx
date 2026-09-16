import React, { useState } from 'react';
import {
  Flame,
  Search,
  Dna,
  Zap,
  Target,
  Play,
  Layers,
  Activity,
  CheckCircle2,
  Atom,
  Clock,
  Sparkles,
  BarChart2,
  ShieldAlert
} from 'lucide-react';

interface VHTSScreen {
  id: string;
  target_protein_name: string;
  pdb_id: string;
  library_source: string;
  total_screened_compounds: number;
  top_hits_count: number;
  best_affinity_kcal_mol: number;
  status: string;
  created_at: string;
}

export const VHTSStudioPage: React.FC = () => {
  const [screens, setScreens] = useState<VHTSScreen[]>([
    {
      id: 'scr-1',
      target_protein_name: 'EGFR T790M / C797S Kinase Domain',
      pdb_id: '7L11',
      library_source: 'Enamine REAL (10M Compounds)',
      total_screened_compounds: 10000000,
      top_hits_count: 48,
      best_affinity_kcal_mol: -11.84,
      status: 'COMPLETED',
      created_at: '2026-09-16T11:00:00Z'
    },
    {
      id: 'scr-2',
      target_protein_name: 'SARS-CoV-2 Main Protease (Mpro)',
      pdb_id: '7BQY',
      library_source: 'ZINC20 Lead-Like (5M Compounds)',
      total_screened_compounds: 5000000,
      top_hits_count: 32,
      best_affinity_kcal_mol: -10.42,
      status: 'COMPLETED',
      created_at: '2026-09-15T15:30:00Z'
    }
  ]);

  const [selectedScreen, setSelectedScreen] = useState<VHTSScreen>(screens[0]);

  const [hits, setHits] = useState<any[]>([
    {
      compound_id: 'REAL-CMP-1001',
      smiles: 'CC(C)N1CCN(CC1)c2cc3ncccc3nc2Nc4ccc(F)cc4',
      docking_score_kcal_mol: -11.84,
      estimated_kd_nm: 2.1,
      pains_filter_passed: true,
      rmsd: 0.54,
      scaffold_cluster: 'Quinazoline Kinase-Hinge Binders'
    },
    {
      compound_id: 'REAL-CMP-1002',
      smiles: 'O=C(Nc1ccc(F)cc1)c2cc3ccccc3[nH]2',
      docking_score_kcal_mol: -10.92,
      estimated_kd_nm: 10.4,
      pains_filter_passed: true,
      rmsd: 0.72,
      scaffold_cluster: 'Indole-Pyridine Cavity Fillers'
    },
    {
      compound_id: 'REAL-CMP-1003',
      smiles: 'NS(=O)(=O)c1ccc(Nc2ncccn2)cc1',
      docking_score_kcal_mol: -9.85,
      estimated_kd_nm: 58.2,
      pains_filter_passed: true,
      rmsd: 0.88,
      scaffold_cluster: 'Sulfonamide Pocket Anchors'
    }
  ]);

  const [clusters, setClusters] = useState<any[]>([
    { label: 'Quinazoline Kinase-Hinge Binders', count: 18, mean_affinity: -11.2 },
    { label: 'Indole-Pyridine Cavity Fillers', count: 16, mean_affinity: -10.4 },
    { label: 'Sulfonamide Pocket Anchors', count: 14, mean_affinity: -9.8 }
  ]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-orange-500/20 to-amber-500/20 rounded-xl border border-orange-500/30 text-orange-400">
            <Flame className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-orange-400 via-amber-300 to-yellow-400">
                Virtual High-Throughput Screening (vHTS)
              </h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">
                Generation 24: Billion-Molecule Docking Grid
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              GPU-accelerated AutoDock Vina / GNINA scoring, PAINS substructure filtering, and Murcko scaffold structural clustering.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-orange-500/20">
            <Play className="w-4 h-4 fill-current" />
            Launch Virtual Screen
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Screened Compounds</span>
            <Atom className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">15.0M+</div>
          <div className="text-xs text-orange-400/80 mt-1">Enamine REAL + ZINC20</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Top Binding Affinity</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{selectedScreen.best_affinity_kcal_mol} kcal/mol</div>
          <div className="text-xs text-amber-400/80 mt-1">Estimated Kd: 2.1 nM</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Active Target</span>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-slate-100 truncate">{selectedScreen.pdb_id}</div>
          <div className="text-xs text-emerald-400/80 mt-1">{selectedScreen.target_protein_name}</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Scaffold Clusters</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{clusters.length} Families</div>
          <div className="text-xs text-purple-400/80 mt-1">100% PAINS Filtered</div>
        </div>
      </div>

      {/* Main Grid: Hits Table & Clusters */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Top Chemical Hits (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-orange-400" />
                Top-Ranked Docking Hits ({selectedScreen.target_protein_name})
              </h2>
              <span className="text-xs font-mono text-slate-400">Ordered by Vina ΔG</span>
            </div>

            <div className="space-y-3">
              {hits.map((h, idx) => (
                <div
                  key={h.compound_id}
                  className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg hover:border-slate-700 transition space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-orange-500/10 border border-orange-500/20 text-orange-400 rounded font-mono text-xs font-bold">
                        #{idx + 1}
                      </span>
                      <span className="font-mono text-sm font-semibold text-slate-200">
                        {h.compound_id}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">
                        [{h.scaffold_cluster}]
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right font-mono">
                        <div className="text-sm font-bold text-emerald-400">
                          {h.docking_score_kcal_mol} kcal/mol
                        </div>
                        <div className="text-[10px] text-slate-400">Kd: {h.estimated_kd_nm} nM</div>
                      </div>
                    </div>
                  </div>

                  <div className="p-2.5 bg-slate-900/60 rounded border border-slate-800 font-mono text-xs text-cyan-300 break-all">
                    {h.smiles}
                  </div>

                  <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
                    <span className="flex items-center gap-1 text-emerald-400">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      PAINS: Clear
                    </span>
                    <span>Pocket RMSD: {h.rmsd} Å</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Scaffold Clusters (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
            <h2 className="text-base font-semibold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              Murcko Scaffold Clusters
            </h2>

            <div className="space-y-3">
              {clusters.map((c, idx) => (
                <div key={idx} className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200">{c.label}</span>
                    <span className="font-mono text-amber-400 font-bold">{c.mean_affinity} kcal/mol</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>{c.count} Member Compounds</span>
                    <span className="text-purple-400">Hinge Direct</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VHTSStudioPage;
