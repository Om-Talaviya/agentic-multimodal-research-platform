import React, { useState } from 'react';
import {
  Layers,
  Activity,
  Sparkles,
  Search,
  Sliders,
  CheckCircle2,
  BarChart3,
  Flame,
  Award,
  Share2,
  Cpu,
  Target,
  Dna,
  ShieldCheck,
  Network,
  GitFork,
  Boxes
} from 'lucide-react';

interface CoOccurrenceEdge {
  source: string;
  target: string;
  interaction_count: number;
  z_score: number;
  enrichment_status: string;
  lr_pair: string;
}

interface SpatialNiche {
  niche_id: string;
  composition: string;
  mean_distance_vasculature_um: number;
  hypoxia_signature: number;
}

export const SpatialGNNStudioPage: React.FC = () => {
  const [datasetName, setDatasetName] = useState('10x_Xenium_Breast_InSitu');
  const [tissueType, setTissueType] = useState('Triple Negative Breast Cancer');
  const [radiusUm, setRadiusUm] = useState(50.0);
  const [embeddingDim, setEmbeddingDim] = useState(128);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'edges' | 'niches' | 'signaling'>('edges');

  const [edges] = useState<CoOccurrenceEdge[]>([
    {
      source: 'CD8+ T Effector',
      target: 'M2-Polarized Macrophage',
      interaction_count: 2840,
      z_score: -3.2,
      enrichment_status: 'Spatial Exclusion',
      lr_pair: 'PD-L1 : PD-1',
    },
    {
      source: 'Cancer-Associated Fibroblast (CAF)',
      target: 'Malignant Epithelial Cell',
      interaction_count: 8920,
      z_score: 5.84,
      enrichment_status: 'Desmoplastic Niche',
      lr_pair: 'CXCL12 : CXCR4',
    },
    {
      source: 'CD8+ T Effector',
      target: 'Malignant Epithelial Cell',
      interaction_count: 1450,
      z_score: 2.15,
      enrichment_status: 'Direct Contact Interface',
      lr_pair: 'FASL : FAS',
    },
  ]);

  const [niches] = useState<SpatialNiche[]>([
    {
      niche_id: 'Niche_01_Invasive_Front',
      composition: '52% CAF, 38% Tumor, 10% Macrophage',
      mean_distance_vasculature_um: 42.0,
      hypoxia_signature: 2.4,
    },
    {
      niche_id: 'Niche_02_Tertiary_Lymphoid_Structure',
      composition: '60% B-cell, 30% T-cell, 10% Dendritic Cell',
      mean_distance_vasculature_um: 18.5,
      hypoxia_signature: 0.4,
    },
    {
      niche_id: 'Niche_03_Hypoxic_Necrotic_Core',
      composition: '80% Tumor Epithelium, 20% Necrotic Macrophage',
      mean_distance_vasculature_um: 120.0,
      hypoxia_signature: 4.8,
    },
  ]);

  const handleBuildMatrix = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 700);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-violet-950 to-slate-900 p-6 rounded-2xl border border-violet-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-500/20 rounded-lg border border-violet-400/30 text-violet-300">
              <Network className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Spatial Multi-Omics Cell-Cell GNN Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 139: Delaunay / k-NN Graph Neural Network Neighborhood Co-Occurrence & Microdomain Niche Solver
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleBuildMatrix}
            disabled={loading}
            className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-violet-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Executing GNN Message Passing...' : 'Compute Spatial Graph'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Dataset Tag</label>
          <input
            type="text"
            value={datasetName}
            onChange={(e) => setDatasetName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Tissue Origin</label>
          <input
            type="text"
            value={tissueType}
            onChange={(e) => setTissueType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Radius Cutoff (µm)</label>
          <input
            type="number"
            value={radiusUm}
            onChange={(e) => setRadiusUm(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">GNN Embedding Dim</label>
          <input
            type="number"
            value={embeddingDim}
            onChange={(e) => setEmbeddingDim(parseInt(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-violet-900/40">
          <div className="text-xs text-slate-400 font-medium">Indexed Single Cells</div>
          <div className="text-2xl font-bold text-violet-400 mt-1">48,000 Cells</div>
          <div className="text-xs text-slate-400 mt-1">Delaunay Voronoi Tessellation</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-violet-900/40">
          <div className="text-xs text-slate-400 font-medium">Spatial Homophily Ratio</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">0.71 / 1.0</div>
          <div className="text-xs text-emerald-500 mt-1">Structured cell clustering</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-violet-900/40">
          <div className="text-xs text-slate-400 font-medium">Distinct Microdomain Niches</div>
          <div className="text-2xl font-bold text-white mt-1">3 Identified</div>
          <div className="text-xs text-slate-400 mt-1">TLS, Invasive Front, Hypoxic Core</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-violet-900/40">
          <div className="text-xs text-slate-400 font-medium">Top Signaling Axis</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">CXCL12-CXCR4</div>
          <div className="text-xs text-amber-500 mt-1">CAF Stroma Barrier</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('edges')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'edges'
              ? 'border-b-2 border-violet-500 text-violet-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Co-Occurrence Graph Edges ({edges.length})
        </button>
        <button
          onClick={() => setActiveTab('niches')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'niches'
              ? 'border-b-2 border-violet-500 text-violet-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Microdomain Niches ({niches.length})
        </button>
      </div>

      {/* Content */}
      {activeTab === 'edges' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Source Cell</th>
                <th className="p-4">Target Cell</th>
                <th className="p-4">Interactions</th>
                <th className="p-4">Z-Score</th>
                <th className="p-4">Enrichment State</th>
                <th className="p-4">Ligand-Receptor Axis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {edges.map((e) => (
                <tr key={e.source + e.target} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-medium text-violet-300">{e.source}</td>
                  <td className="p-4 font-mono text-white">{e.target}</td>
                  <td className="p-4 font-mono">{e.interaction_count}</td>
                  <td className={`p-4 font-mono font-bold ${e.z_score > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {e.z_score > 0 ? `+${e.z_score}` : e.z_score}
                  </td>
                  <td className="p-4">
                    <span className="bg-violet-950 text-violet-300 text-xs px-2.5 py-1 rounded">
                      {e.enrichment_status}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-xs text-amber-300">{e.lr_pair}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'niches' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {niches.map((n) => (
            <div key={n.niche_id} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3">
              <span className="text-xs font-mono text-violet-400 bg-violet-950 px-2 py-1 rounded">
                {n.niche_id}
              </span>
              <p className="text-sm text-white font-medium">{n.composition}</p>
              <div className="text-xs text-slate-400 space-y-1 pt-2">
                <div>Distance to Vasculature: <span className="text-slate-200">{n.mean_distance_vasculature_um} µm</span></div>
                <div>Hypoxia Score: <span className="text-rose-400 font-bold">{n.hypoxia_signature}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
