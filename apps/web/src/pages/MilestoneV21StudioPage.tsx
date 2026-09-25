import React, { useState } from 'react';
import {
  Globe,
  Cpu,
  Layers,
  Activity,
  Zap,
  Sparkles,
  Database,
  ArrowRight,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface TelemetryItem {
  subsystem_domain: string;
  subsystem_phase_code: string;
  throughput_ops_sec: number;
  cross_validation_accuracy: number;
  latency_ms: number;
}

interface PlanetaryRunItem {
  run_identifier: string;
  generated_hypotheses: number;
  validated_lead_targets: number;
  meta_synthesis_entropy: number;
}

export const MilestoneV21StudioPage: React.FC = () => {
  const [missionName, setMissionName] = useState('Global Autonomous Multimodal Milestone v2.1');
  const [activeSubsystems, setActiveSubsystems] = useState(187);
  const [crossCorrelation, setCrossCorrelation] = useState(0.982);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [synthesisResult, setSynthesisResult] = useState<any>(null);

  const handleSynthesize = async () => {
    setIsSynthesizing(true);
    try {
      const res = await fetch('/api/v1/milestone-v2-1/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: missionName,
          active_subsystems_count: activeSubsystems,
          global_cross_correlation_input: crossCorrelation,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSynthesisResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSynthesizing(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <Globe className="w-8 h-8 text-emerald-400" />
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              Milestone v2.1 Planetary Meta-Orchestrator
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 187: Autonomous Planetary Multi-Modal Synthesis Unifying All 187 Research Engines
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <span className="px-3 py-1 bg-emerald-950 border border-emerald-700 text-emerald-300 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> Planetary Tier v2.1
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" /> Synthesis Configuration
          </h2>
          <div>
            <label className="text-xs text-slate-400 font-medium">Mission Name</label>
            <input
              type="text"
              value={missionName}
              onChange={(e) => setMissionName(e.target.value)}
              className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Connected Subsystems ({activeSubsystems})</label>
            <input
              type="range"
              min="50"
              max="200"
              value={activeSubsystems}
              onChange={(e) => setActiveSubsystems(parseInt(e.target.value))}
              className="w-full mt-2 accent-emerald-500"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 font-medium">Global Cross-Correlation Index ({crossCorrelation})</label>
            <input
              type="range"
              min="0.5"
              max="1.0"
              step="0.001"
              value={crossCorrelation}
              onChange={(e) => setCrossCorrelation(parseFloat(e.target.value))}
              className="w-full mt-2 accent-emerald-500"
            />
          </div>
          <button
            onClick={handleSynthesize}
            disabled={isSynthesizing}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium rounded-lg text-sm flex items-center justify-center gap-2 transition"
          >
            {isSynthesizing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            Execute Planetary Meta-Synthesis
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" /> Planetary Telemetry & Synthesis Core
          </h2>
          {synthesisResult ? (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">Autonomous Throughput</p>
                  <p className="text-2xl font-bold text-emerald-400 mt-1">{synthesisResult.autonomous_discovery_throughput} <span className="text-xs text-slate-400 font-normal">hyp/hr</span></p>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">Synthesis Confidence</p>
                  <p className="text-2xl font-bold text-teal-300 mt-1">{(synthesisResult.synthesis_confidence_score * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <p className="text-xs text-slate-500">Subsystems Integrated</p>
                  <p className="text-2xl font-bold text-cyan-400 mt-1">{synthesisResult.active_subsystems_count} / 187</p>
                </div>
              </div>

              <div className="p-4 bg-emerald-950/30 border border-emerald-900/50 rounded-lg text-sm text-emerald-200">
                <p className="font-semibold text-emerald-300 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Executive Synthesis Summary:
                </p>
                {synthesisResult.executive_synthesis_report}
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-300 mb-2">Connected Research Domains</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {synthesisResult.telemetries.map((t: TelemetryItem, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="flex justify-between font-semibold text-slate-200">
                        <span>{t.subsystem_domain}</span>
                        <span className="text-emerald-400 font-mono">{(t.cross_validation_accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <div className="text-slate-500 flex justify-between">
                        <span>Code: {t.subsystem_phase_code}</span>
                        <span>{t.throughput_ops_sec} ops/s | {t.latency_ms} ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500 space-y-2">
              <Globe className="w-12 h-12 text-slate-700 animate-pulse" />
              <p className="text-sm">Initiate planetary synthesis to orchestrate all 187 research engines.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
