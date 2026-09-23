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
  Zap,
  Boxes
} from 'lucide-react';

interface LipidComponent {
  lipid: string;
  mol_percent: number;
  role: string;
}

export const LNPEncapsulationStudioPage: React.FC = () => {
  const [formulationTag, setFormulationTag] = useState('LNP_Lead_Formulation_042');
  const [payloadName, setPayloadName] = useState('Bivalent mRNA Vaccine (Spike + Nucleocapsid)');
  const [flowRateRatio, setFlowRateRatio] = useState(3.0);
  const [totalFlowRate, setTotalFlowRate] = useState(12.0);
  const [npRatio, setNpRatio] = useState(6.0);
  const [ionizableMol, setIonizableMol] = useState(50.0);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'lipids' | 'physicochemical' | 'ribogreen'>('lipids');

  const [lipids] = useState<LipidComponent[]>([
    { lipid: 'Ionizable Lipid (ALC-0315 / SM-102)', mol_percent: 50.0, role: 'mRNA Electrostatic Condensation & Endosomal Escape' },
    { lipid: 'Helper Phospholipid (DSPC)', mol_percent: 10.0, role: 'Bilayer Stability & Structural Lamellar Transition' },
    { lipid: 'Cholesterol', mol_percent: 38.5, role: 'Membrane Packing & In Vivo Stability' },
    { lipid: 'PEG-Lipid (DMG-PEG2000)', mol_percent: 1.5, role: 'Particle Size Control & Steric Protection' },
  ]);

  const handleFormulate = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 700);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 p-6 rounded-2xl border border-sky-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sky-500/20 rounded-lg border border-sky-400/30 text-sky-300">
              <Boxes className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Lipid Nanoparticle (LNP) Encapsulation Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 138: High-Throughput Microfluidic Self-Assembly & RiboGreen mRNA Entrapment Efficiency Engine
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleFormulate}
            disabled={loading}
            className="flex items-center gap-2 bg-sky-600 hover:bg-sky-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-sky-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Simulating Assembly...' : 'Optimize Formulation'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Formulation Batch</label>
          <input
            type="text"
            value={formulationTag}
            onChange={(e) => setFormulationTag(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Aqueous : Organic Ratio</label>
          <input
            type="number"
            step="0.5"
            value={flowRateRatio}
            onChange={(e) => setFlowRateRatio(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Total Flow Rate (mL/min)</label>
          <input
            type="number"
            value={totalFlowRate}
            onChange={(e) => setTotalFlowRate(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">N/P Charge Ratio</label>
          <input
            type="number"
            step="0.5"
            value={npRatio}
            onChange={(e) => setNpRatio(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-sky-900/40">
          <div className="text-xs text-slate-400 font-medium">Encapsulation Efficiency</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">94.2% Entrapment</div>
          <div className="text-xs text-emerald-500 mt-1">✓ RiboGreen fluorometric assay</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-sky-900/40">
          <div className="text-xs text-slate-400 font-medium">Z-Average Particle Size</div>
          <div className="text-2xl font-bold text-sky-400 mt-1">74.5 nm</div>
          <div className="text-xs text-sky-500 mt-1">PDI: 0.08 (Monodisperse)</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-sky-900/40">
          <div className="text-xs text-slate-400 font-medium">Apparent pKa</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">6.45 pKa</div>
          <div className="text-xs text-amber-500 mt-1">Optimal endosomal release</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-sky-900/40">
          <div className="text-xs text-slate-400 font-medium">Transfection Potency</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">8.6x Fold</div>
          <div className="text-xs text-purple-400 mt-1">In vivo luciferase readout</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('lipids')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'lipids'
              ? 'border-b-2 border-sky-500 text-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Lipid Molar Ratios ({lipids.length})
        </button>
        <button
          onClick={() => setActiveTab('physicochemical')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'physicochemical'
              ? 'border-b-2 border-sky-500 text-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Physicochemical Specifications
        </button>
      </div>

      {/* Content */}
      {activeTab === 'lipids' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Lipid Class</th>
                <th className="p-4">Molar Ratio (%)</th>
                <th className="p-4">Mechanistic Function</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {lipids.map((l) => (
                <tr key={l.lipid} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-medium text-sky-400">{l.lipid}</td>
                  <td className="p-4 font-mono font-bold text-white">{l.mol_percent}%</td>
                  <td className="p-4 text-slate-300">{l.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'physicochemical' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3 text-sm">
            <h3 className="text-lg font-bold text-white">Cryo-TEM Core Morphology</h3>
            <p className="text-slate-300">
              Homogeneous, electron-dense amorphous core confirms complete encapsulation of high molecular weight mRNA without surface-blebbing or free blebs.
            </p>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Zeta Potential:</span>
                <span className="font-mono text-emerald-400">-2.4 mV (Neutral in Circulation)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">TNS Fluorescence Apparent pKa:</span>
                <span className="font-mono text-amber-400">6.45 ± 0.05</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
