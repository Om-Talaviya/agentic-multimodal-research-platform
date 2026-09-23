import React, { useState } from 'react';
import {
  Globe,
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
  Activity,
  GitBranch,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

interface ViralLineage {
  clade: string;
  pangolin: string;
  who: string;
  mutations: string[];
  growth_advantage: number;
  immune_evasion: number;
  prevalence: number;
}

interface TrajectoryStep {
  day: number;
  rt: number;
  cases: number;
  dominant_freq: number;
}

export const ViralPhylodynamicsStudioPage: React.FC = () => {
  const [pathogenName, setPathogenName] = useState('SARS-CoV-2');
  const [genomeType, setGenomeType] = useState('ssRNA(+)');
  const [horizonDays, setHorizonDays] = useState(90);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'lineages' | 'trajectories' | 'tree'>('lineages');

  const [lineages, setLineages] = useState<ViralLineage[]>([
    {
      clade: '24A (JN.1)',
      pangolin: 'JN.1.11.1',
      who: 'Variant of Interest',
      mutations: ['S:L455S', 'S:F456L', 'S:R346T'],
      growth_advantage: 0.115,
      immune_evasion: 0.94,
      prevalence: 68.4,
    },
    {
      clade: '24B (KP.3)',
      pangolin: 'KP.3.1.1',
      who: 'FLiRT Lineage',
      mutations: ['S:V1104L', 'S:Q493E', 'S:F456L'],
      growth_advantage: 0.142,
      immune_evasion: 0.97,
      prevalence: 24.2,
    },
    {
      clade: '23I (BA.2.86)',
      pangolin: 'BA.2.86.1',
      who: 'Pirola Ancestor',
      mutations: ['S:K356T', 'S:V483del'],
      growth_advantage: 0.04,
      immune_evasion: 0.81,
      prevalence: 7.4,
    },
  ]);

  const [trajectories, setTrajectories] = useState<TrajectoryStep[]>([
    { day: 0, rt: 1.15, cases: 18200, dominant_freq: 32.0 },
    { day: 15, rt: 1.28, cases: 24500, dominant_freq: 46.5 },
    { day: 30, rt: 1.39, cases: 36000, dominant_freq: 62.0 },
    { day: 45, rt: 1.48, cases: 51200, dominant_freq: 78.4 },
    { day: 60, rt: 1.42, cases: 59000, dominant_freq: 88.0 },
    { day: 75, rt: 1.30, cases: 48000, dominant_freq: 92.5 },
    { day: 90, rt: 1.12, cases: 34000, dominant_freq: 94.0 },
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
              <span className="px-3 py-1 bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-semibold rounded-full uppercase tracking-wider">
                Phase 132 Studio
              </span>
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Biosurveillance Network Synchronized
              </span>
            </div>
            <h1 className="text-3xl font-bold mt-2 bg-gradient-to-r from-white via-slate-200 to-violet-400 bg-clip-text text-transparent">
              Global Pandemic Biosurveillance & Viral Lineage Phylodynamics Engine
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Multi-strain renewal branching models, daily growth fitness advantage estimation, and clade displacement tracking.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSimulate}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-violet-900/20 transition-all disabled:opacity-50"
            >
              <Globe className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Modeling...' : 'Simulate Phylodynamics'}
            </button>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Effective Rt (Current)</span>
              <TrendingUp className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400 mt-2">1.48</div>
            <div className="text-xs text-rose-400 mt-1">Active transmission expansion</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Dominant Clade</span>
              <Award className="w-4 h-4 text-violet-400" />
            </div>
            <div className="text-2xl font-bold text-white mt-2">JN.1.11.1</div>
            <div className="text-xs text-violet-400 mt-1">68.4% Global Prevalence</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Peak Immune Evasion</span>
              <ShieldCheck className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 mt-2">0.97</div>
            <div className="text-xs text-slate-400 mt-1">16.8x Titer fold drop</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Total Genomes Sequenced</span>
              <Dna className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-cyan-400 mt-2">125,000</div>
            <div className="text-xs text-slate-400 mt-1">GISAID / Nextstrain ingested</div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          {/* Config Column */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 h-fit space-y-5">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-violet-400" /> Surveillance Parameters
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Pathogen Name</label>
              <input
                type="text"
                value={pathogenName}
                onChange={(e) => setPathogenName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Genome Architecture</label>
              <input
                type="text"
                value={genomeType}
                onChange={(e) => setGenomeType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Horizon Forecast (Days)</label>
              <input
                type="number"
                value={horizonDays}
                onChange={(e) => setHorizonDays(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-xl text-xs space-y-2 text-slate-300">
              <div className="font-semibold text-violet-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Epidemiological Alert
              </div>
              <p>
                Clade KP.3 exhibits a +14.2% daily growth advantage over JN.1, driven by epistatic mutations S:V1104L and S:Q493E.
              </p>
            </div>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
            <div className="flex items-center gap-4 border-b border-slate-800 pb-4 mb-6">
              <button
                onClick={() => setActiveTab('lineages')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'lineages'
                    ? 'border-violet-500 text-violet-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Tracked Clades & Mutations
              </button>
              <button
                onClick={() => setActiveTab('trajectories')}
                className={`text-sm font-medium pb-1 border-b-2 transition-all ${
                  activeTab === 'trajectories'
                    ? 'border-violet-500 text-violet-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Rt & Epidemiological Trajectories
              </button>
            </div>

            {activeTab === 'lineages' ? (
              <div className="space-y-4">
                {lineages.map((l, idx) => (
                  <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800/80 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-100">{l.pangolin}</span>
                        <span className="text-xs text-slate-400">({l.clade})</span>
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/40">
                        {l.prevalence}% Global
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Defining Mutations: <span className="text-slate-200 font-mono">{l.mutations.join(', ')}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs pt-2 border-t border-slate-800/60">
                      <div>
                        <span className="text-slate-500">Growth Advantage:</span> +{(l.growth_advantage * 100).toFixed(1)}%/day
                      </div>
                      <div>
                        <span className="text-slate-500">Immune Evasion:</span> {(l.immune_evasion * 100).toFixed(0)}%
                      </div>
                      <div>
                        <span className="text-slate-500">Classification:</span> {l.who}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-xs font-medium">
                        <th className="pb-3">Day</th>
                        <th className="pb-3">Effective Rt</th>
                        <th className="pb-3">Estimated Daily Cases</th>
                        <th className="pb-3">Dominant Lineage Freq</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {trajectories.map((t, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 font-medium text-slate-200">Day {t.day}</td>
                          <td className="py-3">
                            <span
                              className={`px-2 py-0.5 rounded text-xs font-mono font-semibold ${
                                t.rt > 1.2
                                  ? 'bg-rose-500/20 text-rose-300'
                                  : 'bg-emerald-500/20 text-emerald-300'
                              }`}
                            >
                              Rt {t.rt}
                            </span>
                          </td>
                          <td className="py-3 text-slate-300 font-mono text-xs">{t.cases.toLocaleString()}</td>
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-violet-500 h-full rounded-full"
                                  style={{ width: `${t.dominant_freq}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono">{t.dominant_freq}%</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default ViralPhylodynamicsStudioPage;
