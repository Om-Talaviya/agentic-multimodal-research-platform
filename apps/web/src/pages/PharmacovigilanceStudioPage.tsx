import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Activity, AlertTriangle, Sparkles, RefreshCw, BarChart2, CheckCircle, Database, TrendingUp
} from 'lucide-react';

interface Corpus {
  id: string;
  title: string;
  data_sources: string[];
  total_adverse_reports: number;
  status: string;
}

export const PharmacovigilanceStudioPage: React.FC = () => {
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [selectedCorpus, setSelectedCorpus] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [mining, setMining] = useState(false);
  
  const [drugName, setDrugName] = useState('Trastuzumab Deruxtecan');

  const fetchCorpora = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/pharmacovigilance/corpora', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCorpora(data);
        if (data.length > 0) {
          fetchCorpusDetails(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchCorpusDetails = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/pharmacovigilance/corpora/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedCorpus(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCorpora();
  }, []);

  const handleDetect = async (e: React.FormEvent) => {
    e.preventDefault();
    setMining(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/pharmacovigilance/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          drug_name: drugName,
          corpus_size: 1250000
        })
      });
      if (res.ok) {
        const created = await res.json();
        await fetchCorpora();
        await fetchCorpusDetails(created.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setMining(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-amber-600 to-rose-700 rounded-xl shadow-lg shadow-amber-900/30">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Autonomous Pharmacovigilance & Safety Signal Studio
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
                  Phase 49
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                Real-World Evidence (RWE) Disproportionality Mining, PRR/ROR & WHO-UMC Causality
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchCorpora}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Signal Mining Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            Pharmacovigilance Mining Query
          </h2>
          <form onSubmit={handleDetect} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Target Pharmaceutical Compound</label>
              <input
                type="text"
                value={drugName}
                onChange={(e) => setDrugName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-amber-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">RWE Surveillance Sources</label>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300 space-y-1">
                <div>• FDA FAERS (Adverse Event Reporting System)</div>
                <div>• WHO VigiBase Global Safety Database</div>
                <div>• EudraVigilance European Signal Repository</div>
              </div>
            </div>
            <button
              type="submit"
              disabled={mining}
              className="w-full py-2.5 bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-600 hover:to-rose-700 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-amber-900/20 disabled:opacity-50"
            >
              {mining ? 'Scanning Disproportionality...' : 'Detect Post-Market Safety Signals'}
            </button>
          </form>

          {/* Corpora List */}
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Surveillance Reports</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {corpora.map((c) => (
                <div
                  key={c.id}
                  onClick={() => fetchCorpusDetails(c.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                    selectedCorpus?.id === c.id
                      ? 'bg-amber-950/40 border-amber-500/40 text-amber-200'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{c.title}</div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800">{(c.total_adverse_reports / 1000000).toFixed(1)}M reports</span>
                    <span>{c.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Disproportionality Signals & Causality Cards */}
        <div className="lg:col-span-2 space-y-6">
          {selectedCorpus ? (
            <>
              {/* Telemetry Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5 text-rose-400"/> Max PRR</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedCorpus.signals?.[0]?.metrics?.[0]?.prr || 3.45}x
                  </div>
                  <div className="text-[10px] text-rose-400 mt-0.5">Threshold $\ge 2.0$</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-amber-400"/> Reporting Odds (ROR)</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedCorpus.signals?.[0]?.metrics?.[0]?.ror || 3.62}
                  </div>
                  <div className="text-[10px] text-amber-400 mt-0.5">95% CI: {selectedCorpus.signals?.[0]?.metrics?.[0]?.ror_ci || '[2.85-4.55]'}</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><TrendingUp className="w-3.5 h-3.5 text-sky-400"/> BCPNN IC025</div>
                  <div className="text-xl font-bold text-white mt-1">
                    +{selectedCorpus.signals?.[0]?.metrics?.[0]?.ic025 || 1.65}
                  </div>
                  <div className="text-[10px] text-sky-400 mt-0.5">Signal positive (&gt;0)</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-emerald-400"/> Adverse Cases</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedCorpus.signals?.[0]?.case_count || 142} pts
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">Chi-Square: {selectedCorpus.signals?.[0]?.metrics?.[0]?.chi_square || 48.6}</div>
                </div>
              </div>

              {/* Detected Safety Signals List */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  Prioritized MedDRA Safety Signals & WHO-UMC Causality Assessment
                </h3>
                <div className="space-y-3">
                  {selectedCorpus.signals?.map((s: any) => (
                    <div key={s.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-semibold text-rose-300 text-sm">{s.reaction}</span>
                          <span className="text-xs text-slate-400 ml-2">({s.soc})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            s.priority === 'URGENT' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>
                            {s.priority}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            WHO-UMC: {s.causality}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-slate-300">{s.summary}</p>
                      <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-900">
                        <span>PRR: <strong className="text-amber-400">{s.metrics?.[0]?.prr}</strong></span>
                        <span>ROR: <strong className="text-amber-400">{s.metrics?.[0]?.ror}</strong></span>
                        <span>IC₀₂₅: <strong className="text-sky-400">{s.metrics?.[0]?.ic025}</strong></span>
                        <span>EBGM: <strong className="text-emerald-400">{s.metrics?.[0]?.ebgm05}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500">
              <ShieldAlert className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
              <p className="text-sm">Select or run pharmacovigilance disproportionality detection to view safety signals</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
