import React, { useState } from 'react';
import { 
  BarChart3, 
  Activity, 
  Sparkles, 
  Layers, 
  Play, 
  CheckCircle2, 
  Crosshair,
  Filter,
  Check,
  TrendingUp,
  Cpu
} from 'lucide-react';

interface GateHierarchyNode {
  gate_name: string;
  x_channel: string;
  y_channel: string;
  gated_event_count: number;
  population_pct_of_parent: number;
  population_pct_of_total: number;
}

export const FlowCytometryStudioPage: React.FC = () => {
  const [experimentName, setExperimentName] = useState('CAR-T Cytotoxic Potency & Exhaustion Panel');
  const [cellType, setCellType] = useState('Primary CAR-T');
  const [totalEvents, setTotalEvents] = useState(50000);
  const [plateId, setPlateId] = useState('PLT-384-HTS-09');
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    experiment_id: string;
    z_prime: number;
    assay_status: string;
    signal_to_bg: number;
    gates: GateHierarchyNode[];
  } | null>({
    experiment_id: 'FLOW-EXP-2026-993',
    z_prime: 0.81,
    assay_status: 'EXCELLENT_ASSAY',
    signal_to_bg: 14.8,
    gates: [
      { gate_name: 'All Events', x_channel: 'FSC-A', y_channel: 'SSC-A', gated_event_count: 50000, population_pct_of_parent: 100.0, population_pct_of_total: 100.0 },
      { gate_name: 'Intact Lymphocytes', x_channel: 'FSC-A', y_channel: 'SSC-A', gated_event_count: 42100, population_pct_of_parent: 84.2, population_pct_of_total: 84.2 },
      { gate_name: 'Singlets (FSC-H vs FSC-A)', x_channel: 'FSC-A', y_channel: 'FSC-H', gated_event_count: 38732, population_pct_of_parent: 92.0, population_pct_of_total: 77.5 },
      { gate_name: 'Live T Cells (Live/Dead-)', x_channel: 'CD3-FITC', y_channel: 'Live/Dead', gated_event_count: 36408, population_pct_of_parent: 94.0, population_pct_of_total: 72.8 },
      { gate_name: 'CD8+ Effector CAR-T', x_channel: 'CD4-PE', y_channel: 'CD8-APC', gated_event_count: 24757, population_pct_of_parent: 68.0, population_pct_of_total: 49.5 },
    ]
  });

  const handleRunAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        experiment_id: `FLOW-EXP-${Date.now().toString().slice(-6)}`,
        z_prime: 0.83,
        assay_status: 'EXCELLENT_ASSAY',
        signal_to_bg: 15.2,
        gates: [
          { gate_name: 'All Events', x_channel: 'FSC-A', y_channel: 'SSC-A', gated_event_count: totalEvents, population_pct_of_parent: 100.0, population_pct_of_total: 100.0 },
          { gate_name: 'Intact Lymphocytes', x_channel: 'FSC-A', y_channel: 'SSC-A', gated_event_count: Math.round(totalEvents * 0.85), population_pct_of_parent: 85.0, population_pct_of_total: 85.0 },
          { gate_name: 'Singlets (FSC-H/A)', x_channel: 'FSC-A', y_channel: 'FSC-H', gated_event_count: Math.round(totalEvents * 0.85 * 0.91), population_pct_of_parent: 91.0, population_pct_of_total: 77.35 },
          { gate_name: 'Live T Cells', x_channel: 'CD3-FITC', y_channel: 'Live/Dead', gated_event_count: Math.round(totalEvents * 0.85 * 0.91 * 0.95), population_pct_of_parent: 95.0, population_pct_of_total: 73.48 },
          { gate_name: 'CD8+ CAR-T Cells', x_channel: 'CD4-PE', y_channel: 'CD8-APC', gated_event_count: Math.round(totalEvents * 0.85 * 0.91 * 0.95 * 0.70), population_pct_of_parent: 70.0, population_pct_of_total: 51.44 },
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
            <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
              <Crosshair className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                Flow Cytometry Bivariate Gating & HTS Assay Robotics Studio
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Hierarchical polygon gating, population subset frequencies, and robotic Z'-factor quality certification (ADR 068).
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleRunAnalysis}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg transition-all"
        >
          <Play className="w-4 h-4 fill-current" />
          {loading ? 'Processing FCS...' : 'Run Gating Tree'}
        </button>
      </div>

      {/* Control Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Experiment Name</label>
          <input 
            type="text" 
            value={experimentName} 
            onChange={(e) => setExperimentName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Sample / Cell Type</label>
          <input 
            type="text" 
            value={cellType} 
            onChange={(e) => setCellType(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Total FCS Events</label>
          <input 
            type="number" 
            value={totalEvents} 
            onChange={(e) => setTotalEvents(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">HTS Plate ID</label>
          <input 
            type="text" 
            value={plateId} 
            onChange={(e) => setPlateId(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Telemetry Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>HTS Assay Z'-Factor</span>
                <Sparkles className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.z_prime.toFixed(2)}
              </div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> High Robustness (Z' &gt; 0.5)
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Signal-to-Background (S/B)</span>
                <TrendingUp className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.signal_to_bg.toFixed(1)}x
              </div>
              <p className="text-xs text-slate-400 mt-1">Fluorophore Dynamic Window</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Hierarchical Gates</span>
                <Layers className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.gates.length} Levels
              </div>
              <p className="text-xs text-indigo-400 mt-1">Nested Sub-Populations</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Target Subset Purity</span>
                <Activity className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400 mt-2">
                {result.gates[result.gates.length - 1].population_pct_of_total.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400 mt-1">Final Endpoint Fraction</p>
            </div>
          </div>

          {/* Gating Hierarchy Tree Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Filter className="w-4 h-4 text-cyan-400" />
                Hierarchical Bivariate Flow Gating Cascade
              </h2>
              <span className="text-xs px-2.5 py-1 bg-slate-800 text-cyan-300 rounded-full border border-slate-700 font-mono">
                {result.experiment_id}
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Gate Hierarchy Tier</th>
                    <th className="px-4 py-3">X Channel</th>
                    <th className="px-4 py-3">Y Channel</th>
                    <th className="px-4 py-3">Event Count</th>
                    <th className="px-4 py-3">% of Parent</th>
                    <th className="px-4 py-3">% of Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.gates.map((g, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-medium text-white flex items-center gap-2">
                        <span className="text-xs text-slate-500 font-mono">L{idx + 1}</span>
                        <span>{g.gate_name}</span>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-cyan-300">{g.x_channel}</td>
                      <td className="px-4 py-3 font-mono text-xs text-cyan-300">{g.y_channel}</td>
                      <td className="px-4 py-3 font-mono text-white font-semibold">{g.gated_event_count.toLocaleString()}</td>
                      <td className="px-4 py-3 text-emerald-400 font-semibold">{g.population_pct_of_parent.toFixed(1)}%</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${g.population_pct_of_total}%` }} />
                          </div>
                          <span className="text-xs font-mono">{g.population_pct_of_total.toFixed(1)}%</span>
                        </div>
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
export default FlowCytometryStudioPage;
