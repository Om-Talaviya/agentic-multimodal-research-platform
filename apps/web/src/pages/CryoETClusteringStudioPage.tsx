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
  Eye,
  Box
} from 'lucide-react';

interface ClusterInfo {
  cluster_label: string;
  macromolecule_identity: string;
  particle_count: number;
  fsc_resolution_angstrom: number;
  b_factor_sharpening: number;
  conformational_state: string;
}

interface SubtomoVolume {
  volume_tag: string;
  tomogram_id: string;
  coord_x: number;
  coord_y: number;
  coord_z: number;
  signal_to_noise_ratio: number;
  cross_correlation_score: number;
  assigned_cluster: string;
}

export const CryoETClusteringStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('HeLa Cell Lamella In-Situ Cryo-ET');
  const [cellularOrganism, setCellularOrganism] = useState('Homo sapiens');
  const [voxelSize, setVoxelSize] = useState(1.35);
  const [clusterCount, setClusterCount] = useState(3);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'clusters' | 'volumes' | 'fsc'>('clusters');

  const [clusters, setClusters] = useState<ClusterInfo[]>([
    {
      cluster_label: 'Cluster_01_80S_Ribosome',
      macromolecule_identity: 'Eukaryotic 80S Ribosome',
      particle_count: 1800,
      fsc_resolution_angstrom: 3.15,
      b_factor_sharpening: -82.0,
      conformational_state: 'Pre-Translocation Active State',
    },
    {
      cluster_label: 'Cluster_02_26S_Proteasome',
      macromolecule_identity: '26S Proteasome Holoenzyme',
      particle_count: 720,
      fsc_resolution_angstrom: 3.85,
      b_factor_sharpening: -95.0,
      conformational_state: 'Doubly Capped 19S-20S Complex',
    },
    {
      cluster_label: 'Cluster_03_ATP_Synthase',
      macromolecule_identity: 'Mitochondrial F1Fo-ATP Synthase Dimer',
      particle_count: 480,
      fsc_resolution_angstrom: 4.20,
      b_factor_sharpening: -110.0,
      conformational_state: 'Membrane Curvature Oligomer',
    },
  ]);

  const [volumes, setVolumes] = useState<SubtomoVolume[]>([
    {
      volume_tag: 'Box_001',
      tomogram_id: 'Tomo_01_Lamella',
      coord_x: 120.0,
      coord_y: 340.0,
      coord_z: 50.0,
      signal_to_noise_ratio: 2.1,
      cross_correlation_score: 0.88,
      assigned_cluster: 'Cluster_01_80S_Ribosome',
    },
    {
      volume_tag: 'Box_002',
      tomogram_id: 'Tomo_01_Lamella',
      coord_x: 450.0,
      coord_y: 890.0,
      coord_z: 75.0,
      signal_to_noise_ratio: 1.9,
      cross_correlation_score: 0.84,
      assigned_cluster: 'Cluster_02_26S_Proteasome',
    },
    {
      volume_tag: 'Box_003',
      tomogram_id: 'Tomo_02_Lamella',
      coord_x: 890.0,
      coord_y: 120.0,
      coord_z: 110.0,
      signal_to_noise_ratio: 2.4,
      cross_correlation_score: 0.91,
      assigned_cluster: 'Cluster_03_ATP_Synthase',
    },
  ]);

  const handleRunClustering = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 800);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-2xl border border-indigo-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 rounded-lg border border-indigo-400/30 text-indigo-300">
              <Box className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Cryo-ET Subtomogram Deep Clustering Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 133: 3D Contrastive Convolutional Representation Learning & In-Situ Macromolecular Structure Solver
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRunClustering}
            disabled={loading}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Clustering Tomograms...' : 'Run Deep Clustering'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Cellular Organism</label>
          <input
            type="text"
            value={cellularOrganism}
            onChange={(e) => setCellularOrganism(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Voxel Size (Å/px)</label>
          <input
            type="number"
            step="0.01"
            value={voxelSize}
            onChange={(e) => setVoxelSize(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Target Clusters</label>
          <input
            type="number"
            value={clusterCount}
            onChange={(e) => setClusterCount(parseInt(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-indigo-900/40">
          <div className="text-xs text-slate-400 font-medium">Mean In-Situ Resolution</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">3.40 Å</div>
          <div className="text-xs text-emerald-400 mt-1">✓ Near-atomic cryo-ET threshold</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-indigo-900/40">
          <div className="text-xs text-slate-400 font-medium">Total In-Situ Particles</div>
          <div className="text-2xl font-bold text-white mt-1">3,000</div>
          <div className="text-xs text-slate-400 mt-1">Across 2 FIB lamellae</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-indigo-900/40">
          <div className="text-xs text-slate-400 font-medium">3D Embedding Silhouette</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">0.84</div>
          <div className="text-xs text-emerald-500 mt-1">High conformational separation</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-indigo-900/40">
          <div className="text-xs text-slate-400 font-medium">Distinct Macromolecules</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">3 Species</div>
          <div className="text-xs text-purple-400 mt-1">Ribosome, Proteasome, Synthase</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('clusters')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'clusters'
              ? 'border-b-2 border-indigo-500 text-indigo-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Discovered Macromolecular Clusters ({clusters.length})
        </button>
        <button
          onClick={() => setActiveTab('volumes')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'volumes'
              ? 'border-b-2 border-indigo-500 text-indigo-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Subtomogram Volumes ({volumes.length})
        </button>
        <button
          onClick={() => setActiveTab('fsc')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'fsc'
              ? 'border-b-2 border-indigo-500 text-indigo-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Fourier Shell Correlation (FSC) Curves
        </button>
      </div>

      {/* Content */}
      {activeTab === 'clusters' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {clusters.map((c) => (
            <div key={c.cluster_label} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-mono text-indigo-400 bg-indigo-950/60 px-2 py-1 rounded">
                    {c.cluster_label}
                  </span>
                  <h3 className="text-lg font-bold text-white mt-2">{c.macromolecule_identity}</h3>
                </div>
              </div>
              <div className="space-y-2 text-sm text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Resolution:</span>
                  <span className="font-semibold text-emerald-400">{c.fsc_resolution_angstrom} Å (FSC 0.143)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Particles:</span>
                  <span className="font-semibold text-white">{c.particle_count.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">B-factor:</span>
                  <span className="font-mono text-amber-400">{c.b_factor_sharpening} Å²</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Conformation:</span>
                  <span className="text-indigo-300 text-right">{c.conformational_state}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'volumes' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Volume Tag</th>
                <th className="p-4">Tomogram ID</th>
                <th className="p-4">Coordinates (X, Y, Z)</th>
                <th className="p-4">SNR</th>
                <th className="p-4">Cross-Correlation</th>
                <th className="p-4">Assigned Cluster</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {volumes.map((v) => (
                <tr key={v.volume_tag} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-medium text-white">{v.volume_tag}</td>
                  <td className="p-4 text-slate-400">{v.tomogram_id}</td>
                  <td className="p-4 font-mono text-xs text-slate-300">({v.coord_x}, {v.coord_y}, {v.coord_z})</td>
                  <td className="p-4 text-indigo-400 font-semibold">{v.signal_to_noise_ratio}</td>
                  <td className="p-4 text-emerald-400 font-semibold">{v.cross_correlation_score}</td>
                  <td className="p-4">
                    <span className="bg-indigo-950 text-indigo-300 text-xs px-2.5 py-1 rounded font-mono">
                      {v.assigned_cluster}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'fsc' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-slate-300">
          <h3 className="text-lg font-bold text-white mb-4">Fourier Shell Correlation & Nyquist Limits</h3>
          <div className="h-48 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center text-slate-500 font-mono text-sm">
            [FSC 0.143 Gold-Standard Half-Map Curve Visualizer: Nyquist limit at 2.70 Å | Mean Cutoff at 3.40 Å]
          </div>
        </div>
      )}
    </div>
  );
};
