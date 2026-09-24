import React, { useState } from 'react';
import { Cpu, ShieldCheck, Zap, Layers, Sparkles, CheckCircle2, Award } from 'lucide-react';

export const MilestoneV18StudioPage: React.FC = () => {
  const [pipelineName, setPipelineName] = useState('Centennial Multi-Modal Bio-System Integration');
  const [indication, setIndication] = useState('Metastatic Glioblastoma & Immuno-Oncology');
  const [phasesCount, setPhasesCount] = useState(154);
  const [synthesizing, setSynthesizing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSynthesize = async () => {
    setSynthesizing(true);
    try {
      const res = await fetch('/api/v1/milestone-v1-8/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          orchestration_name: pipelineName,
          target_indication: indication,
          active_phases_count: phasesCount,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSynthesizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Award className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Centennial Bio-System Synthesis & Milestone v1.8 Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 154: Unified Multi-Modal Orchestration, Cross-Domain Synthesis & 154 Active Phases Certification
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-amber-400" />
              <span>Synthesis Controller</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Orchestration Campaign</label>
                <input
                  type="text"
                  value={pipelineName}
                  onChange={(e) => setPipelineName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Therapeutic Indication</label>
                <input
                  type="text"
                  value={indication}
                  onChange={(e) => setIndication(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Active Phases Certified</label>
                <input
                  type="number"
                  value={phasesCount}
                  onChange={(e) => setPhasesCount(parseInt(e.target.value) || 154)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <button
                onClick={handleSynthesize}
                disabled={synthesizing}
                className="w-full py-3 bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
              >
                {synthesizing ? 'Executing Cross-Scale Synthesis...' : 'Execute Centennial Synthesis'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-amber-500/30 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold text-amber-400">Milestone v1.8 Platform Status</h3>
                    <span className="flex items-center space-x-1.5 text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-300 rounded-full border border-emerald-500/20">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{result.cross_domain_pipeline_status}</span>
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Total Phases</p>
                      <p className="text-xl font-extrabold text-white mt-1">{result.total_phases_integrated} Phases</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Milestone</p>
                      <p className="text-xl font-bold text-amber-400 mt-1">{result.milestone_version}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Confidence Score</p>
                      <p className="text-xl font-bold text-emerald-400 mt-1">{(result.orchestration_confidence_score * 100).toFixed(1)}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">System Entropy</p>
                      <p className="text-xl font-bold text-cyan-400 mt-1">{result.global_system_entropy}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-white">Cross-Domain Workflow Pipeline Nodes</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Workflow Node</th>
                          <th className="px-4 py-3">Domain</th>
                          <th className="px-4 py-3">Phase Ref</th>
                          <th className="px-4 py-3">Latency</th>
                          <th className="px-4 py-3">Fidelity</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.workflow_nodes.map((n: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-medium text-slate-200">{n.node_name}</td>
                            <td className="px-4 py-3.5 text-slate-400">{n.domain_category}</td>
                            <td className="px-4 py-3.5 font-mono text-xs text-amber-400">{n.phase_reference}</td>
                            <td className="px-4 py-3.5 text-slate-300">{n.execution_latency_ms} ms</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{(n.node_fidelity_score * 100).toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Trigger cross-scale synthesis to aggregate insights across all 154 platform research phases.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MilestoneV18StudioPage;
