import React, { useState } from 'react';
import {
  Activity,
  Layers,
  Zap,
  Sparkles,
  Database,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface ItemProfile {
  item_name: string;
  profile_category: string;
  quantitative_value: number;
  log2_fold_change: number;
  significance_score: number;
}

interface MetricTrace {
  metric_dimension: string;
  observed_value: number;
  z_score: number;
  p_value: number;
}

export const MrnaCapPolyADecayStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Autonomous Synthetic mRNA 5-Prime Cap Structure & Poly(A) Tail Deadenylation Decay Kinetics Simulator Engine Protocol 01');
  const [specimen, setSpecimen] = useState('Human Patient Cohort Sample');
  const [inputScale, setInputScale] = useState(1.0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch('/api/v1/mrna-cap-poly-a-decay/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: studyName,
          target_specimen: specimen,
          input_scale: inputScale,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-400 bg-clip-text text-transparent">
              Autonomous Synthetic mRNA 5-Prime Cap Structure & Poly(A) Tail Deadenylation Decay Kinetics Simulator Engine Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 219: Autonomous Models synthetic mRNA translation initiation efficiency and half-life dynamics as a function of Cap-1/Cap-2 enzymatic structures and poly(A) deadenylation rate kinetics.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <span className="px-3 py-1 bg-cyan-950 border border-cyan-700 text-cyan-300 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> High-Fidelity Engine
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" /> Assay Parameters
          </h2>
          <div>
            <label className="text-xs text-slate-400 font-medium">Study Name</label>
            <input
              type="text"
              value={studyName}
              onChange={(e) => setStudyName(e.target.value)}
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Target Specimen</label>
            <input
              type="text"
              value={specimen}
              onChange={(e) => setSpecimen(e.target.value)}
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Input Perturbation / Scale ({inputScale}x)</label>
            <input
              type="range"
              min="0.5"
              max="2.5"
              step="0.1"
              value={inputScale}
              onChange={(e) => setInputScale(parseFloat(e.target.value))}
              className="w-full mt-2 accent-cyan-500"
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium rounded-lg text-sm flex items-center justify-center gap-2 transition"
          >
            {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            Run Analysis & Simulation
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" /> Autonomous Results & Profiles
          </h2>
          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">mrna_half_life_hours</p>
                  <p className="text-2xl font-bold text-cyan-400 mt-1">{result.mrna_half_life_hours}</p>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">initiation_complex_affinity_kd_nM</p>
                  <p className="text-2xl font-bold text-sky-300 mt-1">{result.initiation_complex_affinity_kd_nM}</p>
                </div>
              </div>

              <div className="p-4 bg-cyan-950/30 border border-cyan-900/50 rounded-lg text-sm text-cyan-200">
                <p className="font-semibold text-cyan-300 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Synthesis Report:
                </p>
                {result.summary_report}
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-300 mb-2">Identified Signatures & Profiles</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {result.item_profiles.map((item: ItemProfile, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="flex justify-between font-semibold text-slate-200">
                        <span>{item.item_name}</span>
                        <span className="text-cyan-400 font-mono">{item.quantitative_value}</span>
                      </div>
                      <div className="text-slate-400 flex justify-between">
                        <span>{item.profile_category}</span>
                        <span>Log2FC: +{item.log2_fold_change}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500 space-y-2">
              <Activity className="w-12 h-12 text-slate-700 animate-pulse" />
              <p className="text-sm">Initiate run to view real-time computational simulation telemetry.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
