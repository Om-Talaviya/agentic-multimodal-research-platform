import React, { useState } from 'react';
import { 
  Activity, 
  Layers, 
  Cpu, 
  Sparkles, 
  Database, 
  Search, 
  Sliders, 
  CheckCircle2, 
  BarChart3, 
  Info,
  Disc,
  Play,
  Download,
  Flame
} from 'lucide-react';

interface MetalChannel {
  channel_name: string;
  metal_isotope: string;
  target_marker: string;
  category: string;
  mean_intensity: number;
  transformed_arcsinh: number;
  signal_to_noise: number;
}

interface SingleCellCluster {
  cluster_id: number;
  cluster_name: string;
  cell_frequency: number;
  marker_enrichment_profile: Record<string, number>;
  phenograph_k: number;
  center_x: number;
  center_y: number;
  tsne_coordinates_sample: Array<{ x: number; y: number }>;
}

export const CyTOFStudioPage: React.FC = () => {
  const [experimentName, setExperimentName] = useState('PBMC-Immune-Atlas-DeepProfile');
  const [tissueType, setTissueType] = useState('PBMC');
  const [cellCount, setCellCount] = useState(10000);
  const [cofactor, setCofactor] = useState(5.0);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'clusters' | 'channels' | 'tsne' | 'heatmap'>('clusters');
  const [selectedCluster, setSelectedCluster] = useState<SingleCellCluster | null>(null);

  const [channels, setChannels] = useState<MetalChannel[]>([
    { channel_name: "141Pr_CD3", metal_isotope: "141Pr", target_marker: "CD3", category: "Lineage", mean_intensity: 450.0, transformed_arcsinh: 5.19, signal_to_noise: 24.2 },
    { channel_name: "142Nd_CD4", metal_isotope: "142Nd", target_marker: "CD4", category: "T-Cell", mean_intensity: 320.0, transformed_arcsinh: 4.85, signal_to_noise: 21.8 },
    { channel_name: "144Nd_CD8a", metal_isotope: "144Nd", target_marker: "CD8a", category: "T-Cell", mean_intensity: 280.0, transformed_arcsinh: 4.72, signal_to_noise: 19.5 },
    { channel_name: "145Nd_CD19", metal_isotope: "145Nd", target_marker: "CD19", category: "B-Cell", mean_intensity: 190.0, transformed_arcsinh: 4.33, signal_to_noise: 18.2 },
    { channel_name: "146Nd_CD14", metal_isotope: "146Nd", target_marker: "CD14", category: "Monocyte", mean_intensity: 510.0, transformed_arcsinh: 5.32, signal_to_noise: 26.1 },
    { channel_name: "159Tb_FoxP3", metal_isotope: "159Tb", target_marker: "FoxP3", category: "Treg", mean_intensity: 95.0, transformed_arcsinh: 3.64, signal_to_noise: 14.5 },
    { channel_name: "165Ho_PD1", metal_isotope: "165Ho", target_marker: "PD-1", category: "Checkpoint", mean_intensity: 115.0, transformed_arcsinh: 3.83, signal_to_noise: 15.9 },
    { channel_name: "174Yb_GranzymeB", metal_isotope: "174Yb", target_marker: "GranzymeB", category: "Cytotoxic", mean_intensity: 260.0, transformed_arcsinh: 4.64, signal_to_noise: 22.0 },
  ]);

  const [clusters, setClusters] = useState<SingleCellCluster[]>([
    { cluster_id: 1, cluster_name: "CD4+ Central Memory T Cells", cell_frequency: 22.0, marker_enrichment_profile: { "CD3": 2.8, "CD4": 3.1, "CD45RO": 2.9, "CD27": 2.2, "CD8a": -1.2 }, phenograph_k: 30, center_x: 18.0, center_y: 0.0, tsne_coordinates_sample: [{ x: 17.5, y: 1.2 }, { x: 19.1, y: -0.8 }] },
    { cluster_id: 2, cluster_name: "CD4+ Effector Memory T Cells", cell_frequency: 14.0, marker_enrichment_profile: { "CD3": 2.7, "CD4": 2.9, "CD45RO": 3.0, "CD27": -0.8, "PD-1": 1.4 }, phenograph_k: 30, center_x: 13.8, center_y: 16.4, tsne_coordinates_sample: [{ x: 14.2, y: 15.8 }] },
    { cluster_id: 3, cluster_name: "CD4+ Regulatory T Cells (Tregs)", cell_frequency: 5.0, marker_enrichment_profile: { "CD3": 2.6, "CD4": 3.0, "FoxP3": 3.5, "HLA-DR": 1.8 }, phenograph_k: 30, center_x: -6.2, center_y: 29.3, tsne_coordinates_sample: [{ x: -5.8, y: 28.9 }] },
    { cluster_id: 4, cluster_name: "CD8+ Cytotoxic Effector T Cells", cell_frequency: 18.0, marker_enrichment_profile: { "CD3": 2.9, "CD8a": 3.4, "GranzymeB": 3.1, "Perforin": 2.8 }, phenograph_k: 30, center_x: -21.4, center_y: 17.9, tsne_coordinates_sample: [{ x: -20.8, y: 18.5 }] },
    { cluster_id: 5, cluster_name: "CD8+ Exhausted T Cells", cell_frequency: 7.0, marker_enrichment_profile: { "CD3": 2.8, "CD8a": 3.2, "PD-1": 3.3, "TIGIT": 3.0 }, phenograph_k: 30, center_x: -24.0, center_y: -0.0, tsne_coordinates_sample: [{ x: -23.5, y: -1.2 }] },
    { cluster_id: 6, cluster_name: "CD19+ B Cells", cell_frequency: 11.0, marker_enrichment_profile: { "CD19": 3.6, "HLA-DR": 2.9, "CD3": -1.8 }, phenograph_k: 30, center_x: -18.4, center_y: -21.9, tsne_coordinates_sample: [{ x: -17.9, y: -22.4 }] },
    { cluster_id: 7, cluster_name: "CD14+ Classical Monocytes", cell_frequency: 13.0, marker_enrichment_profile: { "CD14": 3.7, "HLA-DR": 2.5, "CD11c": 2.1 }, phenograph_k: 30, center_x: 6.2, center_y: -29.3, tsne_coordinates_sample: [{ x: 5.9, y: -28.8 }] },
  ]);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/cytof/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experiment_name: experimentName,
          tissue_type: tissueType,
          cell_count: cellCount,
          cofactor: cofactor,
        })
      });
      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setChannels(data.data.channels);
          setClusters(data.data.clusters);
        }
      }
    } catch (e) {
      console.error('CyTOF simulation failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
              <Disc className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
                Phase 109: High-Dimensional CyTOF Phenotyper
              </h1>
              <p className="text-sm text-slate-400">
                Mass cytometry single-cell phenotyping, Arcsinh transformations, and PhenoGraph cluster profiling
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handleSimulate}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium rounded-lg shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            {loading ? 'Analyzing CyTOF Panel...' : 'Run Mass Cytometry Phenotyper'}
          </button>
        </div>
      </div>

      {/* Control Configuration Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block">Experiment Name</label>
          <input 
            type="text" 
            value={experimentName} 
            onChange={(e) => setExperimentName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 px-3 py-1.5 rounded text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block">Tissue Source</label>
          <select 
            value={tissueType} 
            onChange={(e) => setTissueType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 px-3 py-1.5 rounded text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="PBMC">Human Peripheral Blood (PBMC)</option>
            <option value="TUMOR_INFILTRATING">Tumor-Infiltrating Lymphocytes (TIL)</option>
            <option value="BONE_MARROW">Bone Marrow Aspirate</option>
            <option value="SPLEEN">Splenocyte Dissociation</option>
          </select>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block">Single Cells Interrogated</label>
          <input 
            type="number" 
            value={cellCount} 
            onChange={(e) => setCellCount(Number(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 px-3 py-1.5 rounded text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Arcsinh Cofactor (c)</label>
            <span className="text-xs font-mono text-indigo-400">{cofactor}</span>
          </div>
          <input 
            type="range" 
            min="1" 
            max="15" 
            step="0.5"
            value={cofactor} 
            onChange={(e) => setCofactor(Number(e.target.value))}
            className="w-full accent-indigo-500 cursor-pointer"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-800 mt-8 mb-6 pb-2">
        <button 
          onClick={() => setActiveTab('clusters')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'clusters' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Layers className="w-4 h-4" />
          Phenotypic Subsets ({clusters.length})
        </button>
        <button 
          onClick={() => setActiveTab('tsne')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'tsne' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <BarChart3 className="w-4 h-4" />
          2D t-SNE / PhenoGraph Map
        </button>
        <button 
          onClick={() => setActiveTab('channels')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'channels' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Cpu className="w-4 h-4" />
          Heavy-Metal Isotopic Panel ({channels.length})
        </button>
      </div>

      {/* Content Area */}
      {activeTab === 'clusters' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            {clusters.map((cl) => (
              <div 
                key={cl.cluster_id}
                onClick={() => setSelectedCluster(cl)}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedCluster?.cluster_id === cl.cluster_id ? 'bg-indigo-950/40 border-indigo-500 shadow-lg shadow-indigo-500/10' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-400 flex items-center justify-center text-xs font-bold font-mono">
                      {cl.cluster_id}
                    </span>
                    <h3 className="font-semibold text-slate-100">{cl.cluster_name}</h3>
                  </div>
                  <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                    {cl.cell_frequency}% Frequency
                  </span>
                </div>
                
                <div className="flex flex-wrap gap-2 mt-3">
                  {Object.entries(cl.marker_enrichment_profile).map(([marker, zScore]) => (
                    <span 
                      key={marker}
                      className={`text-xs px-2 py-0.5 rounded border font-mono ${zScore > 0 ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : 'bg-rose-500/10 text-rose-300 border-rose-500/30'}`}
                    >
                      {marker}: {zScore > 0 ? `+${zScore}` : zScore}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-xl backdrop-blur-md h-fit">
            <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-indigo-400" />
              Immune Compartment Breakdown
            </h3>
            <div className="space-y-4 text-sm">
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Total Analyzed Cells</div>
                <div className="text-xl font-bold font-mono text-indigo-400">{cellCount.toLocaleString()} events</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">T-Cell Compartment (CD4+ / CD8+)</div>
                <div className="text-xl font-bold font-mono text-emerald-400">66.0%</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">B-Cell & Myeloid Compartment</div>
                <div className="text-xl font-bold font-mono text-purple-400">24.0%</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">PhenoGraph Resolution k</div>
                <div className="text-xl font-bold font-mono text-amber-400">k=30 neighbors</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tsne' && (
        <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-xl backdrop-blur-md">
          <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            2D t-SNE High-Dimensional Manifold Projection
          </h3>
          <div className="w-full h-96 bg-slate-950 rounded-xl border border-slate-800 relative flex items-center justify-center overflow-hidden">
            {/* 2D Cluster Centroids Visualization */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-80 h-80 rounded-full border border-dashed border-slate-800/80 absolute"></div>
              <div className="w-48 h-48 rounded-full border border-dashed border-slate-800/60 absolute"></div>
            </div>

            {clusters.map((cl) => {
              const leftPercent = 50 + (cl.center_x / 40) * 45;
              const topPercent = 50 + (cl.center_y / 40) * 45;
              return (
                <div 
                  key={cl.cluster_id}
                  style={{ left: `${leftPercent}%`, top: `${topPercent}%` }}
                  className="absolute -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
                  onClick={() => setSelectedCluster(cl)}
                >
                  <div className="w-5 h-5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/50 flex items-center justify-center text-[10px] font-bold text-white group-hover:scale-125 transition-transform">
                    {cl.cluster_id}
                  </div>
                  <div className="hidden group-hover:block absolute left-6 top-0 z-20 bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-lg shadow-xl text-xs whitespace-nowrap">
                    <div className="font-semibold text-indigo-300">{cl.cluster_name}</div>
                    <div className="text-slate-400">{cl.cell_frequency}% of cells</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {activeTab === 'channels' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-md">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="p-4">Metal Isotope</th>
                <th className="p-4">Target Marker</th>
                <th className="p-4">Category</th>
                <th className="p-4">Raw Intensity (Counts)</th>
                <th className="p-4">Arcsinh Transformed</th>
                <th className="p-4">Signal-to-Noise</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {channels.map((ch, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono text-indigo-300 font-semibold">{ch.metal_isotope}</td>
                  <td className="p-4 font-semibold text-slate-100">{ch.target_marker}</td>
                  <td className="p-4">
                    <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {ch.category}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-slate-300">{ch.mean_intensity}</td>
                  <td className="p-4 font-mono text-emerald-400">{ch.transformed_arcsinh}</td>
                  <td className="p-4 font-mono text-amber-400">{ch.signal_to_noise} dB</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default CyTOFStudioPage;
