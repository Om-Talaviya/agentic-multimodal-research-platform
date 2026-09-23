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
  ShieldCheck
} from 'lucide-react';

interface FragmentHit {
  hit_id: string;
  smiles: string;
  site: string;
  b_factor: number;
  occupancy: number;
  z_peak: number;
  le: number;
}

interface DensityMap {
  map_id: string;
  resolution: number;
  sigma: number;
  mean_density: number;
}

export const PanDDACrystallographyStudioPage: React.FC = () => {
  const [campaignName, setCampaignName] = useState('SARS_CoV_2_Mpro_XChem_PanDDA');
  const [targetProtein, setTargetProtein] = useState('Main Protease (Mpro)');
  const [totalCrystals, setTotalCrystals] = useState(380);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'hits' | 'maps' | 'density'>('hits');

  const [hits, setHits] = useState<FragmentHit[]>([
    {
      hit_id: 'XChem_Mpro_Hit_042',
      smiles: 'CC(=O)Nc1ccc(S(=O)(=O)N)cc1',
      site: 'Catalytic Cys145-His41 Dyad',
      b_factor: 22.4,
      occupancy: 0.82,
      z_peak: 7.12,
      le: 0.52,
    },
    {
      hit_id: 'XChem_Mpro_Hit_089',
      smiles: 'c1ccc2c(c1)nc([nH]2)c3ccncc3',
      site: 'Dimerization Interface',
      b_factor: 28.5,
      occupancy: 0.65,
      z_peak: 5.84,
      le: 0.44,
    },
    {
      hit_id: 'XChem_Mpro_Hit_114',
      smiles: 'Cc1c(c(no1)c2ccccc2)C(=O)N',
      site: 'Cryptic S2 Subpocket',
      b_factor: 19.8,
      occupancy: 0.88,
      z_peak: 7.65,
      le: 0.58,
    },
  ]);

  const [maps, setMaps] = useState<DensityMap[]>([
    {
      map_id: 'PanDDA_Ground_State_Model_01',
      resolution: 1.35,
      sigma: 0.08,
      mean_density: 1.02,
    },
    {
      map_id: 'PanDDA_Ensemble_Difference_Map_02',
      resolution: 1.35,
      sigma: 0.12,
      mean_density: 0.98,
    },
  ]);

  const handleRunPanDDA = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Phase 129
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Structural Biology & XChem
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2 flex items-center gap-2">
            <Layers className="w-7 h-7 text-emerald-400" />
            Autonomous High-Throughput Crystallography PanDDA Fragment Screening Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Pan-Dataset Density Analysis (PanDDA) ground-state statistical subtraction, low-occupancy fragment event detection, and ligand efficiency optimization.
          </p>
        </div>

        <button
          onClick={handleRunPanDDA}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-5 py-2.5 rounded-lg font-medium transition shadow-lg shadow-emerald-900/30 disabled:opacity-50"
        >
          {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {loading ? 'Analyzing Crystallography Maps...' : 'Run PanDDA Screen'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Target className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">PanDDA Events Detected</div>
            <div className="text-xl font-bold text-white">{hits.length} Validated Hits</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">Mean Z-Peak: 6.87σ</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Mean Ligand Efficiency</div>
            <div className="text-xl font-bold text-white">0.51 kcal/mol/HA</div>
            <div className="text-[11px] text-blue-400 mt-0.5">Highly Tractable Starting Points</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Crystals Soaked & Shot</div>
            <div className="text-xl font-bold text-white">{totalCrystals} Datasets</div>
            <div className="text-[11px] text-purple-400 mt-0.5">High-Res: 1.35 Å Cutoff</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Background Noise (σ)</div>
            <div className="text-xl font-bold text-white">0.08 σ_bg</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Statistical Ground State Converged</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 mb-6">
        <button
          onClick={() => setActiveTab('hits')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'hits'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Resolved Fragment Hits ({hits.length})
        </button>
        <button
          onClick={() => setActiveTab('maps')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'maps'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Statistical Background Density Maps ({maps.length})
        </button>
        <button
          onClick={() => setActiveTab('density')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition ${
            activeTab === 'density'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          PanDDA Z-Map Visualizer
        </button>
      </div>

      {/* Content */}
      {activeTab === 'hits' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">XChem / PanDDA Fragment Hits</h2>
            <span className="text-xs text-slate-400">Low-occupancy binding events detected via statistical subtraction</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Hit ID</th>
                <th className="px-4 py-3">Binding Subsite</th>
                <th className="px-4 py-3">Fragment SMILES</th>
                <th className="px-4 py-3">Z-Peak Score</th>
                <th className="px-4 py-3">Occupancy</th>
                <th className="px-4 py-3">Ligand Efficiency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {hits.map((h, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400 font-medium">{h.hit_id}</td>
                  <td className="px-4 py-3 text-white font-bold font-sans">{h.site}</td>
                  <td className="px-4 py-3 text-slate-300 font-mono text-[11px]">{h.smiles}</td>
                  <td className="px-4 py-3 text-cyan-400 font-bold">+{h.z_peak} σ</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{(h.occupancy * 100).toFixed(0)}%</td>
                  <td className="px-4 py-3 text-purple-400 font-bold">{h.le} LE</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'maps' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-white">Statistical Electron Density Background Models</h2>
            <span className="text-xs text-slate-400">Averaged across 380 crystallographic datasets</span>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Map Model ID</th>
                <th className="px-4 py-3">Resolution</th>
                <th className="px-4 py-3">Statistical Outlier Sigma</th>
                <th className="px-4 py-3">Mean Density</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {maps.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-3 text-emerald-400">{m.map_id}</td>
                  <td className="px-4 py-3 text-white font-bold">{m.resolution} Å</td>
                  <td className="px-4 py-3 text-amber-400 font-bold">{m.sigma} σ</td>
                  <td className="px-4 py-3 text-slate-300">{m.mean_density} e/Å³</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'density' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
          <div className="max-w-md mx-auto py-8">
            <Layers className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-80" />
            <h3 className="text-base font-semibold text-white">PanDDA Event Electron Density Viewer</h3>
            <p className="text-slate-400 text-xs mt-1">
              Interactive 3D difference electron density isocontour rendering at 2.0σ revealing subtle fragment binding modes in cryptic allosteric pockets.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PanDDACrystallographyStudioPage;
