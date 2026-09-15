import React, { useState, useEffect } from 'react';
import { 
  Award, Sparkles, RefreshCw, Activity, CheckCircle, Zap, Brain, BookOpen, Compass, Terminal
} from 'lucide-react';

interface Program {
  id: string;
  title: string;
  research_domain: string;
  goal_statement: string;
  exploration_mode: string;
  overall_novelty_score: number;
  status: string;
}

export const AIScientistStudioPage: React.FC = () => {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [selectedProgram, setSelectedProgram] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  
  const [title, setTitle] = useState('Autonomous Discovery of Pan-KRAS Resistance Bypass Modulators');
  const [domain, setDomain] = useState('Precision Oncology & Molecular Therapeutics');
  const [goal, setGoal] = useState('Autonomously formulate and in-silico validate novel macrocyclic modalities overcoming secondary point mutations.');

  const fetchPrograms = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/ai-scientist/programs', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPrograms(data);
        if (data.length > 0) {
          fetchProgramDetails(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgramDetails = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/ai-scientist/programs/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedProgram(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchPrograms();
  }, []);

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    setRunning(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/ai-scientist/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          research_domain: domain,
          goal_statement: goal,
          cycles_count: 3
        })
      });
      if (res.ok) {
        const created = await res.json();
        await fetchPrograms();
        await fetchProgramDetails(created.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-yellow-500 to-amber-700 rounded-xl shadow-lg shadow-amber-900/30">
              <Award className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Autonomous AI Scientist Discovery Studio
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 font-mono">
                  Phase 50
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Closed-Loop Self-Evolving Research Agent & Nobel-Turing Discovery Engine
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchPrograms}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Program Launch Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            Autonomous Program Directives
          </h2>
          <form onSubmit={handleRun} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Research Program Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-yellow-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Scientific Domain</label>
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-yellow-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Primary Objective & Challenge</label>
              <textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-yellow-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={running}
              className="w-full py-2.5 bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-600 hover:to-amber-700 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-amber-900/20 disabled:opacity-50"
            >
              {running ? 'Executing Self-Evolving Research Loop...' : 'Launch Autonomous AI Scientist'}
            </button>
          </form>

          {/* Programs List */}
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Discovery Programs</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {programs.map((p) => (
                <div
                  key={p.id}
                  onClick={() => fetchProgramDetails(p.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                    selectedProgram?.id === p.id
                      ? 'bg-yellow-950/40 border-yellow-500/40 text-yellow-200'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{p.title}</div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800">{p.research_domain.split(' ')[0]}</span>
                    <span className="text-yellow-400 font-bold">{(p.overall_novelty_score * 100).toFixed(0)}% Novelty</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Self-Evolving Cycles & Breakthrough Dossier */}
        <div className="lg:col-span-2 space-y-6">
          {selectedProgram ? (
            <>
              {/* Breakthrough Banner */}
              <div className="p-6 bg-gradient-to-r from-yellow-950/50 via-amber-950/30 to-slate-900 border border-yellow-500/30 rounded-2xl shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-yellow-400" />
                    <span className="text-xs font-bold font-mono uppercase tracking-widest text-yellow-400">
                      {selectedProgram.breakthroughs?.[0]?.class || 'NOBEL_TURING_CLASS'} DISCOVERY
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs font-mono">
                    <span className="text-slate-300">Novelty: <strong className="text-yellow-400">{(selectedProgram.breakthroughs?.[0]?.novelty * 100).toFixed(0)}%</strong></span>
                    <span className="text-slate-300">Validity: <strong className="text-emerald-400">{(selectedProgram.breakthroughs?.[0]?.validity * 100).toFixed(0)}%</strong></span>
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white leading-snug">
                  {selectedProgram.breakthroughs?.[0]?.title}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedProgram.breakthroughs?.[0]?.conclusion}
                </p>
              </div>

              {/* Research Iteration Cycle Timeline */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Brain className="w-4 h-4 text-yellow-400" />
                  Self-Evolving Research Program Cycles & Metacognitive Reflections
                </h3>
                <div className="space-y-4">
                  {selectedProgram.cycles?.map((c: any) => (
                    <div key={c.cycle} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-yellow-400 font-mono">Cycle #{c.cycle}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-yellow-500/10 text-yellow-300 border border-yellow-500/20">
                          +{(c.novelty_delta * 100).toFixed(0)}% Knowledge Delta
                        </span>
                      </div>
                      <div className="text-xs text-slate-200">
                        <strong>Hypothesis:</strong> {c.hypothesis}
                      </div>
                      <div className="text-xs text-slate-400">
                        <strong>In-Silico Protocol:</strong> {c.protocol}
                      </div>
                      <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800/80 text-[11px] text-amber-200/90 font-mono">
                        💡 <strong>Metacognitive Self-Reflection:</strong> {c.reflection}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500">
              <Award className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
              <p className="text-sm">Select or run an autonomous AI Scientist program to view the discovery timeline</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
