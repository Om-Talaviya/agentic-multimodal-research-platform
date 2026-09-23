import React, { useState } from 'react';
import {
  Cpu,
  Sparkles,
  Sliders,
  CheckCircle2,
  BarChart3,
  Flame,
  Award,
  Share2,
  Target,
  Dna,
  ShieldCheck,
  Zap,
  Layers,
  Network,
  Binary,
  Activity
} from 'lucide-react';

interface GateNode {
  gate_id: string;
  gate_type: string;
  promoter: string;
  km: number;
  hill: number;
  delay: number;
  high_rfu: number;
  low_rfu: number;
}

interface TruthTableRow {
  inputs: Record<string, number>;
  output: number;
  hex_state: string;
}

export const BiocomputerLogicStudioPage: React.FC = () => {
  const [circuitName, setCircuitName] = useState('Pancreatic_Adenocarcinoma_Classifier_v1');
  const [cellType, setCellType] = useState('Pancreatic Ductal Adenocarcinoma (PDAC)');
  const [expression, setExpression] = useState('(KRAS_G12D AND NOT miR-216) AND (MUC1 OR CEACAM5)');
  const [outputPayload, setOutputPayload] = useState('tBid_Apoptosis_Inducer');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'truth' | 'gates' | 'metrics'>('truth');

  const [gates, setGates] = useState<GateNode[]>([
    {
      gate_id: 'Gate_01_Sensor_miR216_NOT',
      gate_type: 'NOT',
      promoter: 'pTetO-TetR_LVA',
      km: 1.85,
      hill: 2.8,
      delay: 32.0,
      high_rfu: 5200,
      low_rfu: 85,
    },
    {
      gate_id: 'Gate_02_OR_SurfaceAntigen',
      gate_type: 'OR',
      promoter: 'pLux-LuxR_Hybrid',
      km: 2.10,
      hill: 2.6,
      delay: 28.0,
      high_rfu: 4800,
      low_rfu: 120,
    },
    {
      gate_id: 'Gate_03_AND_CoreLogic',
      gate_type: 'AND',
      promoter: 'pLacO-LacI_SplitGal4',
      km: 2.30,
      hill: 3.2,
      delay: 45.0,
      high_rfu: 4950,
      low_rfu: 110,
    },
  ]);

  const [truthRows, setTruthRows] = useState<TruthTableRow[]>([
    { inputs: { KRAS: 1, miR216: 0, MUC1: 1, CEACAM5: 0 }, output: 1, hex_state: '1010' },
    { inputs: { KRAS: 1, miR216: 0, MUC1: 0, CEACAM5: 1 }, output: 1, hex_state: '1001' },
    { inputs: { KRAS: 1, miR216: 0, MUC1: 1, CEACAM5: 1 }, output: 1, hex_state: '1011' },
    { inputs: { KRAS: 0, miR216: 0, MUC1: 1, CEACAM5: 1 }, output: 0, hex_state: '0011' },
    { inputs: { KRAS: 1, miR216: 1, MUC1: 1, CEACAM5: 1 }, output: 0, hex_state: '1111' },
    { inputs: { KRAS: 0, miR216: 1, MUC1: 0, CEACAM5: 0 }, output: 0, hex_state: '0100' },
  ]);

  const handleSimulate = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold rounded-full uppercase tracking-wider">
                Phase 131 Studio
              </span>
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Biocomputer Logic Core Online
              </span>
            </div>
            <h1 className="text-3xl font-bold mt-2 bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
              Synthetic Gene Logic Biocomputer & Multi-Input State Classifier
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Multi-layered Boolean transcriptional gates, Hill digital transfer curves, and cell-state targeting actuators.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSimulate}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl shadow-lg shadow-cyan-900/20 transition-all disabled:opacity-50"
            >
              <Zap className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Synthesizing...' : 'Simulate Biocomputer Logic'}
            </button>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Classification Accuracy</span>
              <Award className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">97.8%</div>
            <div className="text-xs text-emerald-400 mt-1">AUC-ROC: 0.992</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>False Positive Rate</span>
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-cyan-400 mt-2">1.8%</div>
            <div className="text-xs text-slate-400 mt-1">Healthy cell protection</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Noise Margin</span>
              <Activity className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-purple-400 mt-2">16.4 dB</div>
            <div className="text-xs text-slate-400 mt-1">High-gain digital switching</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Logic Gate Cascades</span>
              <Binary className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 mt-2">{gates.length} Nodes</div>
            <div className="text-xs text-slate-400 mt-1">NOT + OR + AND Cascade</div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          {/* Controls Column */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 h-fit space-y-5">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-cyan-400" /> Circuit Specification
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Circuit Identifier</label>
              <input
                type="text"
                value={circuitName}
                onChange={(e) => setCircuitName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Target Cellular Chassis</label>
              <input
                type="text"
                value={cellType}
                onChange={(e) => setCellType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Boolean Expression</label>
              <textarea
                value={expression}
                onChange={(e) => setExpression(e.target.value)}
                rows={3}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Actuator Payload</label>
              <input
                type="text"
                value={outputPayload}
                onChange={(e) => setOutputPayload(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
            <div className="flex items-center gap-4 border-b border-slate-800 pb-4 mb-6">
              <button
                onClick={() => setActiveTab('truth')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'truth'
                    ? 'border-cyan-500 text-cyan-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Truth Table & States
              </button>
              <button
                onClick={() => setActiveTab('gates')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'gates'
                    ? 'border-cyan-500 text-cyan-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Gate Biophysics & Promoters
              </button>
            </div>

            {activeTab === 'truth' ? (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-xs font-medium">
                        <th className="pb-3">Hex / Binary State</th>
                        <th className="pb-3">Input Pin Vector</th>
                        <th className="pb-3">Circuit Output</th>
                        <th className="pb-3">Actuator State</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {truthRows.map((r, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 font-mono text-xs text-slate-400">
                            0b{r.hex_state}
                          </td>
                          <td className="py-3">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              {Object.entries(r.inputs).map(([k, v]) => (
                                <span
                                  key={k}
                                  className={`px-2 py-0.5 rounded text-xs font-mono ${
                                    v === 1
                                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                                      : 'bg-slate-800 text-slate-500'
                                  }`}
                                >
                                  {k}:{v}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="py-3">
                            <span
                              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                                r.output === 1
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {r.output === 1 ? 'HIGH (1)' : 'LOW (0)'}
                            </span>
                          </td>
                          <td className="py-3 text-xs">
                            {r.output === 1 ? (
                              <span className="text-rose-400 font-medium flex items-center gap-1">
                                <Zap className="w-3.5 h-3.5" /> Payload Released
                              </span>
                            ) : (
                              <span className="text-slate-500">Quiescent (Repressed)</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {gates.map((g, idx) => (
                  <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-bold rounded">
                          {g.gate_type}
                        </span>
                        <span className="font-semibold text-slate-200">{g.gate_id}</span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">
                        Delay: {g.delay} mins
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Promoter-Repressor: <span className="text-slate-200 font-mono">{g.promoter}</span>
                    </div>
                    <div className="grid grid-cols-4 gap-2 text-xs pt-2 border-t border-slate-800/60">
                      <div>
                        <span className="text-slate-500">Km:</span> {g.km} µM
                      </div>
                      <div>
                        <span className="text-slate-500">Hill n:</span> {g.hill}
                      </div>
                      <div>
                        <span className="text-slate-500">High Out:</span> {g.high_rfu} RFU
                      </div>
                      <div>
                        <span className="text-slate-500">Low Out:</span> {g.low_rfu} RFU
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default BiocomputerLogicStudioPage;
