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
  ShieldAlert,
  Zap
} from 'lucide-react';

export const CARMacrophageStudioPage: React.FC = () => {
  const [constructName, setConstructName] = useState('CT-0508 Anti-HER2 CAR-M');
  const [targetAntigen, setTargetAntigen] = useState('HER2 / ERBB2');
  const [signalingDomain, setSignalingDomain] = useState('Megf10 / FcR-gamma');
  const [tumorType, setTumorType] = useState('SK-BR-3 Breast Cancer');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'phagocytosis' | 'mmp' | 'tme'>('phagocytosis');

  const handleRunDesign = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 700);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 p-6 rounded-2xl border border-emerald-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30 text-emerald-300">
              <Zap className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              CAR-Macrophage (CAR-M) Phagocytosis Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 137: Solid Tumor Phagocytic Engulfment, Trogocytosis Branching & TME Desmoplastic Matrix Degradation
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRunDesign}
            disabled={loading}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Modeling CAR-M...' : 'Model Phagocytosis'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Construct Name</label>
          <input
            type="text"
            value={constructName}
            onChange={(e) => setConstructName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Target Antigen</label>
          <input
            type="text"
            value={targetAntigen}
            onChange={(e) => setTargetAntigen(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Intracellular Signaling</label>
          <input
            type="text"
            value={signalingDomain}
            onChange={(e) => setSignalingDomain(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Tumor Cell Target</label>
          <input
            type="text"
            value={tumorType}
            onChange={(e) => setTumorType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-emerald-900/40">
          <div className="text-xs text-slate-400 font-medium">Target Phagocytosis Rate</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">78.1% Clearance</div>
          <div className="text-xs text-emerald-500 mt-1">✓ Complete cell engulfment</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-emerald-900/40">
          <div className="text-xs text-slate-400 font-medium">MMP-2/9 Matrix Clearance</div>
          <div className="text-2xl font-bold text-teal-400 mt-1">74.0% Digestion</div>
          <div className="text-xs text-teal-400 mt-1">Stroma penetration: 340 µm</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-emerald-900/40">
          <div className="text-xs text-slate-400 font-medium">M1 Repolarization Index</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">0.91 / 1.0</div>
          <div className="text-xs text-purple-400 mt-1">High TNF-α & IL-12 release</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-emerald-900/40">
          <div className="text-xs text-slate-400 font-medium">T-Cell Infiltration Boost</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">3.6x Increase</div>
          <div className="text-xs text-amber-500 mt-1">Overcomes cold tumor barrier</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('phagocytosis')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'phagocytosis'
              ? 'border-b-2 border-emerald-500 text-emerald-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Engulfment vs Trogocytosis Kinetics
        </button>
        <button
          onClick={() => setActiveTab('mmp')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'mmp'
              ? 'border-b-2 border-emerald-500 text-emerald-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Extracellular Matrix (ECM) Degradation
        </button>
      </div>

      {/* Content */}
      {activeTab === 'phagocytosis' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-lg font-bold text-white">Whole-Cell Engulfment Pathway</h3>
            <p className="text-sm text-slate-300">
              Synergistic activation of <span className="font-mono text-emerald-400">Megf10</span> (phagocytic cup formation) and <span className="font-mono text-teal-400">FcR-gamma</span> (ITAM phosphorylation) triggers actin polymerization and phagolysosomal maturation.
            </p>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Whole-Cell Engulfment:</span>
                <span className="font-bold text-emerald-400">72.5%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Trogocytosis (Gnathic Nibbling):</span>
                <span className="text-amber-400">11.2%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Antigen Cross-Presentation (MHC-I):</span>
                <span className="text-purple-400 font-bold">0.89 Index</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'mmp' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-slate-300">
          <h3 className="text-lg font-bold text-white mb-3">Matrix Metalloproteinase Digestion Profile</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">MMP-2 (Gelatinase A)</span>
              <div className="text-xl font-bold text-white mt-1">480 ng/mL</div>
            </div>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">MMP-9 (Gelatinase B)</span>
              <div className="text-xl font-bold text-white mt-1">820 ng/mL</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
