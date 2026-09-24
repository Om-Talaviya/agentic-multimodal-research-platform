import React, { useState } from 'react';
import { Award, ShieldCheck, Zap, Layers, Sparkles, CheckCircle2, TrendingUp } from 'lucide-react';

export const MilestoneV19StudioPage: React.FC = () => {
  const [cohortName, setCohortName] = useState('Pan-Cancer 10,000-Patient Multi-Omics Precision Atlas');
  const [cohortSize, setCohortSize] = useState(10000);
  const [phasesCount, setPhasesCount] = useState(161);
  const [stratifying, setStratifying] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleStratify = async () => {
    setStratifying(true);
    try {
      const res = await fetch('/api/v1/milestone-v1-9/stratify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cohort_study_name: cohortName,
          patient_cohort_size: cohortSize,
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
      setStratifying(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <Award className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Pan-Cancer Multi-Omics Precision Stratification & Milestone v1.9 Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 161: 161 Active Phases Integration, Pan-Cancer Cluster Subtyping & Cross-Modal Therapeutic Synergy Matrix
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-purple-400" />
              <span>Cohort Stratification Parameters</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Study Atlas Name</label>
                <input
                  type="text"
                  value={cohortName}
                  onChange={(e) => setCohortName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Patient Cohort Size</label>
                <input
                  type="number"
                  value={cohortSize}
                  onChange={(e) => setCohortSize(parseInt(e.target.value) || 10000)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Active Phases Certified</label>
                <input
                  type="number"
                  value={phasesCount}
                  onChange={(e) => setPhasesCount(parseInt(e.target.value) || 161)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <button
                onClick={handleStratify}
                disabled={stratifying}
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-purple-500/20 disabled:opacity-50"
              >
                {stratifying ? 'Stratifying Multi-Omics Cohort...' : 'Execute Pan-Cancer Stratification'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-purple-500/30 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold text-purple-400">Milestone v1.9 Platform Certification</h3>
                    <span className="flex items-center space-x-1.5 text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-300 rounded-full border border-emerald-500/20">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>SYNCHRONIZED</span>
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Total Phases</p>
                      <p className="text-xl font-extrabold text-white mt-1">{result.total_phases_integrated} Phases</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Milestone</p>
                      <p className="text-xl font-bold text-purple-400 mt-1">{result.milestone_version}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">HR Separation</p>
                      <p className="text-xl font-bold text-emerald-400 mt-1">{result.mean_hazard_ratio_separation}x</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Concordance</p>
                      <p className="text-xl font-bold text-cyan-400 mt-1">{(result.global_cross_modal_concordance * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Stratified Pan-Cancer Patient Clusters</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Cluster</th>
                          <th className="px-4 py-3">Subtype Designation</th>
                          <th className="px-4 py-3">Cohort %</th>
                          <th className="px-4 py-3">mPFS (Mo)</th>
                          <th className="px-4 py-3">Recommended Regimen</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.clusters.map((c: any) => (
                          <tr key={c.cluster_index} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-purple-400">#{c.cluster_index}</td>
                            <td className="px-4 py-3.5 font-medium text-slate-200">{c.subtype_designation}</td>
                            <td className="px-4 py-3.5 text-cyan-400">{c.patient_percentage}%</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{c.median_progression_free_survival_months}m</td>
                            <td className="px-4 py-3.5 text-xs text-slate-300">{c.recommended_therapy}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Trigger pan-cancer stratification to cluster patients across 161 multi-scale platform dimensions.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MilestoneV19StudioPage;
