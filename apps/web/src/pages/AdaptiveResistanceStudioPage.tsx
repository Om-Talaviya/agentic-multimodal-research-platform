import React, { useState } from 'react';
import {
  Activity,
  Sparkles,
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
  TrendingDown,
  RefreshCw,
  FlaskConical,
  Zap
} from 'lucide-react';

interface ClonalLineage {
  clone_name: string;
  driver_mutations: string[];
  initial_frequency: number;
  final_frequency: number;
  intrinsic_fitness: number;
  phenotype: string;
}

interface TrajectoryPoint {
  day: number;
  cycle: number;
  drug_concentration: number;
  tumor_burden: number;
  resistance_index: number;
  adaptive_recommendation: string;
}

export const AdaptiveResistanceStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('TNBC Cisplatin Adaptive Response Simulation');
  const [cancerType, setCancerType] = useState('Triple-Negative Breast Cancer');
  const [patientId, setPatientId] = useState('PT-TNBC-904');
  const [cycles, setCycles] = useState(6);
  const [adaptiveThreshold, setAdaptiveThreshold] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'trajectories' | 'clones' | 'regimen'>('trajectories');

  const [clones, setClones] = useState<ClonalLineage[]>([
    {
      clone_name: 'Clone_1_TP53_WT',
      driver_mutations: ['TP53_R273H'],
      initial_frequency: 0.75,
      final_frequency: 0.12,
      intrinsic_fitness: 1.0,
      phenotype: 'SENSITIVE',
    },
    {
      clone_name: 'Clone_2_BRCA1_Revertant',
      driver_mutations: ['TP53_R273H', 'BRCA1_C61G_Rev'],
      initial_frequency: 0.18,
      final_frequency: 0.58,
      intrinsic_fitness: 1.25,
      phenotype: 'MULTI_DRUG_RESISTANT',
    },
    {
      clone_name: 'Clone_3_ABCB1_Overexpressed',
      driver_mutations: ['ABCB1_HighAmp'],
      initial_frequency: 0.07,
      final_frequency: 0.30,
      intrinsic_fitness: 1.10,
      phenotype: 'TOLERANT',
    },
  ]);

  const [trajectories, setTrajectories] = useState<TrajectoryPoint[]>([
    { day: 21, cycle: 1, drug_concentration: 75.0, tumor_burden: 0.82, resistance_index: 0.25, adaptive_recommendation: 'CONTINUE' },
    { day: 42, cycle: 2, drug_concentration: 75.0, tumor_burden: 0.54, resistance_index: 0.40, adaptive_recommendation: 'CONTINUE' },
    { day: 63, cycle: 3, drug_concentration: 37.5, tumor_burden: 0.46, resistance_index: 0.48, adaptive_recommendation: 'DOSE_MODULATE' },
    { day: 84, cycle: 4, drug_concentration: 37.5, tumor_burden: 0.49, resistance_index: 0.59, adaptive_recommendation: 'DOSE_MODULATE' },
    { day: 105, cycle: 5, drug_concentration: 37.5, tumor_burden: 0.52, resistance_index: 0.72, adaptive_recommendation: 'SWITCH_REGIMEN' },
    { day: 126, cycle: 6, drug_concentration: 20.0, tumor_burden: 0.58, resistance_index: 0.88, adaptive_recommendation: 'DRUG_HOLIDAY' },
  ]);

  const [summary, setSummary] = useState({
    final_burden: 0.58,
    max_resistance_index: 0.88,
    tumor_controlled: true,
    total_days: 126,
  });

  const handleRunSimulation = () => {
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
              <span className="px-3 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold rounded-full uppercase tracking-wider">
                Phase 130 Studio
              </span>
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Evolutionary Oncology Engine Active
              </span>
            </div>
            <h1 className="text-3xl font-bold mt-2 bg-gradient-to-r from-white via-slate-200 to-rose-400 bg-clip-text text-transparent">
              Precision Oncology Adaptive Chemotherapy Resistance Simulator
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Lotka-Volterra subclonal competition modeling, dynamic IC50 shifts, and adaptive dose-skipping algorithms.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleRunSimulation}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white font-medium rounded-xl shadow-lg shadow-rose-900/20 transition-all disabled:opacity-50"
            >
              <Zap className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Simulating...' : 'Run Adaptive Simulation'}
            </button>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Final Tumor Burden</span>
              <TrendingDown className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">{(summary.final_burden * 100).toFixed(1)}%</div>
            <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
              <span>Controlled vs baseline</span>
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Peak Resistance Index</span>
              <Flame className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 mt-2">{(summary.max_resistance_index * 100).toFixed(1)}%</div>
            <div className="text-xs text-slate-400 mt-1">BRCA1 Rev / ABCB1 selection</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Subclonal Lineages</span>
              <Dna className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400 mt-2">{clones.length} Active</div>
            <div className="text-xs text-slate-400 mt-1">1 Sensitive / 2 Resistant</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Adaptive Strategy</span>
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-cyan-400 mt-2">Dose-Modulation</div>
            <div className="text-xs text-slate-400 mt-1">Maintains competitive suppressors</div>
          </div>
        </div>

        {/* Main Content Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          {/* Controls Config Column */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 h-fit space-y-5">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-rose-400" /> Study Parameters
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Study Name</label>
              <input
                type="text"
                value={studyName}
                onChange={(e) => setStudyName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Cancer Type</label>
              <input
                type="text"
                value={cancerType}
                onChange={(e) => setCancerType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Cycles</label>
                <input
                  type="number"
                  value={cycles}
                  onChange={(e) => setCycles(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Threshold</label>
                <input
                  type="number"
                  step="0.05"
                  value={adaptiveThreshold}
                  onChange={(e) => setAdaptiveThreshold(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                />
              </div>
            </div>

            <div className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-xl text-xs space-y-2 text-slate-300">
              <div className="font-semibold text-rose-400">Adaptive Rationale</div>
              <p>
                Continuous maximum-tolerated dose (MTD) rapidly eradicates sensitive cells, releasing competitive suppression on resistant subclones. Adaptive dosing maintains a sensitive population to restrain resistant expansion.
              </p>
            </div>
          </div>

          {/* Results Display Column */}
          <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
            <div className="flex items-center gap-4 border-b border-slate-800 pb-4 mb-6">
              <button
                onClick={() => setActiveTab('trajectories')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'trajectories'
                    ? 'border-rose-500 text-rose-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Longitudinal Trajectories
              </button>
              <button
                onClick={() => setActiveTab('clones')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'clones'
                    ? 'border-rose-500 text-rose-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Clonal Fitness Lineages
              </button>
            </div>

            {activeTab === 'trajectories' ? (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-xs font-medium">
                        <th className="pb-3">Day / Cycle</th>
                        <th className="pb-3">Dose (mg/m²)</th>
                        <th className="pb-3">Tumor Burden</th>
                        <th className="pb-3">Resistance</th>
                        <th className="pb-3">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {trajectories.map((t, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 font-medium text-slate-200">
                            Day {t.day} <span className="text-xs text-slate-500">(C{t.cycle})</span>
                          </td>
                          <td className="py-3 text-slate-300">{t.drug_concentration}</td>
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-emerald-500 h-full rounded-full"
                                  style={{ width: `${Math.min(100, t.tumor_burden * 100)}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono">{(t.tumor_burden * 100).toFixed(0)}%</span>
                            </div>
                          </td>
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-amber-500 h-full rounded-full"
                                  style={{ width: `${Math.min(100, t.resistance_index * 100)}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono">{(t.resistance_index * 100).toFixed(0)}%</span>
                            </div>
                          </td>
                          <td className="py-3">
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-rose-300 border border-rose-500/20">
                              {t.adaptive_recommendation}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {clones.map((c, idx) => (
                  <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{c.clone_name}</span>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                          c.phenotype === 'SENSITIVE'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {c.phenotype}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Driver Mutations: <span className="text-slate-200 font-mono">{c.driver_mutations.join(', ')}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs pt-1">
                      <div>
                        <span className="text-slate-500">Initial Freq:</span> {(c.initial_frequency * 100).toFixed(1)}%
                      </div>
                      <div>
                        <span className="text-slate-500">Final Freq:</span> {(c.final_frequency * 100).toFixed(1)}%
                      </div>
                      <div>
                        <span className="text-slate-500">Fitness:</span> {c.intrinsic_fitness}x
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
export default AdaptiveResistanceStudioPage;
