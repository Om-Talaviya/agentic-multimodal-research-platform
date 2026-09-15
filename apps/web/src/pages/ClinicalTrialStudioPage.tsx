import React, { useState, useEffect } from 'react';
import { 
  FileText, Activity, Users, ShieldAlert, Sparkles, TrendingUp, CheckCircle, Search, RefreshCw, BarChart2, Layers
} from 'lucide-react';

interface Protocol {
  id: string;
  title: string;
  phase: string;
  target_indication: string;
  investigational_agent: string;
  sample_size_target: number;
  statistical_power: number;
  estimated_duration_months: number;
  status: string;
}

export const ClinicalTrialStudioPage: React.FC = () => {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  
  const [title, setTitle] = useState('Phase II Adaptive Trial of AGY-801 in Refractory NSCLC');
  const [indication, setIndication] = useState('Non-Small Cell Lung Cancer');
  const [agent, setAgent] = useState('AGY-801');
  const [phase, setPhase] = useState('Phase II');

  const fetchProtocols = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/clinical-trials/protocols', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProtocols(data);
        if (data.length > 0) {
          fetchProtocolDetails(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchProtocolDetails = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/clinical-trials/protocols/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedProtocol(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchProtocols();
  }, []);

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    setOptimizing(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/clinical-trials/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          indication,
          investigational_agent: agent,
          phase,
          target_power: 0.85
        })
      });
      if (res.ok) {
        const created = await res.json();
        await fetchProtocols();
        await fetchProtocolDetails(created.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-teal-600 to-emerald-700 rounded-xl shadow-lg shadow-teal-900/30">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Autonomous Clinical Trial Optimizer
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20 font-mono">
                  Phase 46
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                AI Protocol Optimization, EHR Cohort Stratification & Synthetic Control Arm Simulation
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchProtocols}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Optimizer Input Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            Protocol Optimization Parameters
          </h2>
          <form onSubmit={handleOptimize} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Protocol Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-teal-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Indication</label>
                <input
                  type="text"
                  value={indication}
                  onChange={(e) => setIndication(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-teal-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Investigational Agent</label>
                <input
                  type="text"
                  value={agent}
                  onChange={(e) => setAgent(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-teal-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Clinical Phase</label>
              <select
                value={phase}
                onChange={(e) => setPhase(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-teal-500"
              >
                <option value="Phase I">Phase I (Dose Escalation)</option>
                <option value="Phase II">Phase II (Adaptive Expansion)</option>
                <option value="Phase III">Phase III (Pivotal Confirmatory)</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={optimizing}
              className="w-full py-2.5 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-600 hover:to-emerald-700 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-teal-900/20 disabled:opacity-50"
            >
              {optimizing ? 'Simulating Bayesian Protocol...' : 'Optimize Clinical Protocol'}
            </button>
          </form>

          {/* Protocols List */}
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Saved Trial Protocols</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {protocols.map((p) => (
                <div
                  key={p.id}
                  onClick={() => fetchProtocolDetails(p.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                    selectedProtocol?.id === p.id
                      ? 'bg-teal-950/40 border-teal-500/40 text-teal-200'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{p.title}</div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800">{p.phase}</span>
                    <span>{p.sample_size_target} pts</span>
                    <span>Power: {(p.statistical_power * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Protocol Telemetry & Synthetic Arm Visualizer */}
        <div className="lg:col-span-2 space-y-6">
          {selectedProtocol ? (
            <>
              {/* Telemetry Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-teal-400"/> Sample Size</div>
                  <div className="text-xl font-bold text-white mt-1">{selectedProtocol.sample_size_target} pts</div>
                  <div className="text-[10px] text-teal-400 mt-0.5">Statistical Power: {(selectedProtocol.statistical_power * 100).toFixed(0)}%</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><TrendingUp className="w-3.5 h-3.5 text-emerald-400"/> Duration</div>
                  <div className="text-xl font-bold text-white mt-1">{selectedProtocol.estimated_duration_months} mo</div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">Adaptive enrollment</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-sky-400"/> Synthetic HR</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedProtocol.synthetic_arms?.[0]?.hazard_ratio || 0.62}
                  </div>
                  <div className="text-[10px] text-sky-400 mt-0.5">p = {selectedProtocol.synthetic_arms?.[0]?.p_value || 0.0008}</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-indigo-400"/> Median OS Gain</div>
                  <div className="text-xl font-bold text-white mt-1">
                    +{( (selectedProtocol.synthetic_arms?.[0]?.median_os_interventional || 18.6) - (selectedProtocol.synthetic_arms?.[0]?.median_os_control || 10.4) ).toFixed(1)} mo
                  </div>
                  <div className="text-[10px] text-indigo-400 mt-0.5">vs Standard of Care</div>
                </div>
              </div>

              {/* Eligibility Criteria breakdown */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-teal-400" />
                  Optimized Eligibility Rules & Enrollment Impact
                </h3>
                <div className="space-y-2">
                  {selectedProtocol.criteria?.map((c: any) => (
                    <div key={c.id} className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg flex items-center justify-between text-xs">
                      <div>
                        <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-semibold mr-2 ${
                          c.type === 'INCLUSION' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {c.type}
                        </span>
                        <span className="text-slate-200">{c.description}</span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">
                        {c.impact < 0 ? `${(c.impact * 100).toFixed(0)}% screen rate` : 'Baseline'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Synthetic Control Arm Kaplan-Meier */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-teal-400" />
                  Synthetic Control Arm Survival Probability (Kaplan-Meier Simulation)
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  RWE Baseline: {selectedProtocol.synthetic_arms?.[0]?.rwe_source || 'EHR Oncology Cohort'} (Matched N={selectedProtocol.sample_size_target})
                </p>
                <div className="grid grid-cols-6 sm:grid-cols-12 gap-2 text-center">
                  {selectedProtocol.synthetic_arms?.[0]?.curve?.slice(0, 12).map((pt: any) => (
                    <div key={pt.month} className="p-2 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">M{pt.month}</div>
                      <div className="text-xs font-bold text-emerald-400 mt-1">{(pt.interventional_survival * 100).toFixed(0)}%</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">{(pt.control_survival * 100).toFixed(0)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500">
              <FileText className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
              <p className="text-sm">Select or optimize a clinical trial protocol to inspect stratification</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
