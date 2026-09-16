import React, { useState, useEffect } from 'react';
import { BookOpen, Activity, Sparkles, CheckCircle2, ShieldAlert, Award, FileCheck, MessageSquare } from 'lucide-react';

interface RebuttalPoint {
  id: string;
  referee_claim: string;
  author_rebuttal: string;
  proposed_supplementary_experiment: string;
  is_conceded_and_fixed: boolean;
}

interface ReviewReport {
  id: string;
  referee_persona: string;
  score_out_of_10: number;
  statistical_rigor_score: number;
  novelty_score: number;
  reproducibility_score: number;
  critique_summary: string;
  recommendation: string;
  rebuttal_points?: RebuttalPoint[];
}

interface Manuscript {
  id: string;
  manuscript_title: string;
  research_domain: string;
  abstract_text: string;
  overall_score_out_of_10: number;
  editorial_recommendation: string;
  total_reviews: number;
  created_at: string;
  reviews?: ReviewReport[];
}

export const PeerReviewStudioPage: React.FC = () => {
  const [manuscripts, setManuscripts] = useState<Manuscript[]>([]);
  const [selectedManuscript, setSelectedManuscript] = useState<Manuscript | null>(null);
  const [title, setTitle] = useState('Autonomous Multi-Modal AI Scientist for Closed-Loop Therapeutic Discovery');
  const [domain, setDomain] = useState('Computational Immuno-Oncology');
  const [abstractText, setAbstractText] = useState('We present an autonomous multimodal platform uniting neoantigen prediction, ADC design, and clinical logistics.');
  const [loading, setLoading] = useState(false);

  const fetchManuscripts = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/peer-review/manuscripts');
      if (res.ok) {
        const data = await res.json();
        setManuscripts(data);
        if (data.length > 0 && !selectedManuscript) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/peer-review/manuscripts/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedManuscript(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchManuscripts();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/peer-review/manuscripts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manuscript_title: title,
          research_domain: domain,
          abstract_text: abstractText,
        }),
      });
      if (res.ok) {
        await fetchManuscripts();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-emerald-400">
            <BookOpen className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Autonomous Scientific Peer-Review Panel
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 64 • Adversarial multi-persona referee panel, statistical rigor audit & automated point-by-point rebuttal loop
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-emerald-300">
            <FileCheck className="w-5 h-5" /> Submit Manuscript
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Manuscript Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Research Domain</label>
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Abstract</label>
              <textarea
                value={abstractText}
                onChange={(e) => setAbstractText(e.target.value)}
                rows={3}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Convening Referee Panel...' : 'Convene Referee Panel'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Evaluated Manuscripts</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {manuscripts.map((m) => (
                <div
                  key={m.id}
                  onClick={() => fetchDetail(m.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedManuscript?.id === m.id
                      ? 'bg-emerald-950/40 border-emerald-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200 truncate max-w-[180px]">{m.manuscript_title}</span>
                    <span className="text-emerald-400 font-mono font-bold">{m.overall_score_out_of_10}/10</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{m.editorial_recommendation}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Referee Reports & Rebuttals */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-emerald-300">
              <Activity className="w-5 h-5" /> Adversarial Referee Scores & Decision
            </h2>
            {selectedManuscript && (
              <span className="text-xs bg-emerald-950 text-emerald-300 px-2.5 py-1 rounded border border-emerald-500/40 font-semibold">
                Decision: {selectedManuscript.editorial_recommendation} ({selectedManuscript.overall_score_out_of_10}/10)
              </span>
            )}
          </div>

          {selectedManuscript?.reviews && selectedManuscript.reviews.length > 0 ? (
            <div className="space-y-4">
              {selectedManuscript.reviews.map((rev) => (
                <div key={rev.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-emerald-300 text-sm">{rev.referee_persona}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                        Rigor: {rev.statistical_rigor_score}/10 | Novelty: {rev.novelty_score}/10
                      </span>
                      <span className="text-xs font-bold text-emerald-400 font-mono">{rev.score_out_of_10}/10</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 italic bg-slate-900/50 p-2.5 rounded border border-slate-800">
                    "{rev.critique_summary}"
                  </p>

                  {/* Rebuttal Point */}
                  {rev.rebuttal_points && rev.rebuttal_points.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80 space-y-2">
                      {rev.rebuttal_points.map((reb) => (
                        <div key={reb.id} className="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-lg text-xs space-y-1.5">
                          <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
                            <MessageSquare className="w-3.5 h-3.5" /> Point-by-Point Author Rebuttal
                          </div>
                          <div className="text-slate-300">{reb.author_rebuttal}</div>
                          {reb.proposed_supplementary_experiment && (
                            <div className="text-[11px] text-amber-300 flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Action: {reb.proposed_supplementary_experiment}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No reviews loaded. Submit a manuscript above.</div>
          )}
        </div>
      </div>
    </div>
  );
};
