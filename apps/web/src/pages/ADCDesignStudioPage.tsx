import React, { useState, useEffect } from 'react';
import { Pill, Activity, Sparkles, Shield, CheckCircle, Flame, Layers, Award } from 'lucide-react';

interface Construct {
  id: string;
  construct_code: string;
  payload_name: string;
  payload_class: string;
  linker_type: string;
  measured_dar: number;
  bystander_killing_score: number;
  plasma_half_life_hours: number;
  aggregation_propensity_pct: number;
  therapeutic_index_score: number;
  recommended_lead: boolean;
}

interface Campaign {
  id: string;
  antibody_name: string;
  target_antigen: string;
  conjugation_chemistry: string;
  target_dar: number;
  total_constructs_screened: number;
  created_at: string;
  constructs?: Construct[];
}

export const ADCDesignStudioPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCamp, setSelectedCamp] = useState<Campaign | null>(null);
  const [antibodyName, setAntibodyName] = useState('Trastuzumab');
  const [targetAntigen, setTargetAntigen] = useState('HER2');
  const [targetDar, setTargetDar] = useState(8.0);
  const [loading, setLoading] = useState(false);

  const fetchCampaigns = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/adc-design/campaigns');
      if (res.ok) {
        const data = await res.json();
        setCampaigns(data);
        if (data.length > 0 && !selectedCamp) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/adc-design/campaigns/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedCamp(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/adc-design/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          antibody_name: antibodyName,
          target_antigen: targetAntigen,
          conjugation_chemistry: 'Maleimide-Cysteine',
          target_dar: Number(targetDar),
        }),
      });
      if (res.ok) {
        await fetchCampaigns();
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
          <div className="p-3 bg-amber-950/60 border border-amber-500/40 rounded-xl text-amber-400">
            <Pill className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-amber-400 to-rose-300 bg-clip-text text-transparent">
              Antibody-Drug Conjugate (ADC) Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 59 • Payload-linker screening, drug-to-antibody ratio (DAR) optimization & therapeutic window simulation
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-amber-300">
            <Layers className="w-5 h-5" /> Launch ADC Campaign
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Antibody Backbone</label>
              <input
                type="text"
                value={antibodyName}
                onChange={(e) => setAntibodyName(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Target Antigen</label>
              <input
                type="text"
                value={targetAntigen}
                onChange={(e) => setTargetAntigen(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Target DAR (Ratio)</label>
              <input
                type="number"
                step="0.5"
                value={targetDar}
                onChange={(e) => setTargetDar(parseFloat(e.target.value))}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-500 hover:to-rose-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Optimizing ADCs...' : 'Screen Payload-Linkers'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">ADC Campaigns</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {campaigns.map((camp) => (
                <div
                  key={camp.id}
                  onClick={() => fetchDetail(camp.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedCamp?.id === camp.id
                      ? 'bg-amber-950/40 border-amber-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{camp.antibody_name}</span>
                    <span className="text-amber-400 font-mono">DAR {camp.target_dar}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">Target: {camp.target_antigen}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Constructs Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-amber-300">
              <Activity className="w-5 h-5" /> Screened ADC Candidate Constructs
            </h2>
            {selectedCamp && (
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                Chemistry: {selectedCamp.conjugation_chemistry}
              </span>
            )}
          </div>

          {selectedCamp?.constructs && selectedCamp.constructs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Construct</th>
                    <th className="p-3">Payload / Linker</th>
                    <th className="p-3">DAR</th>
                    <th className="p-3">Bystander Score</th>
                    <th className="p-3">Half-Life</th>
                    <th className="p-3">Therapeutic Index</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedCamp.constructs.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-mono font-semibold text-amber-300">{c.construct_code}</td>
                      <td className="p-3">
                        <div className="font-semibold text-slate-200">{c.payload_name}</div>
                        <div className="text-[10px] text-slate-400">{c.linker_type}</div>
                      </td>
                      <td className="p-3 font-mono font-bold text-slate-200">{c.measured_dar}</td>
                      <td className="p-3 font-mono text-emerald-400">{(c.bystander_killing_score * 100).toFixed(0)}%</td>
                      <td className="p-3 font-mono text-slate-400">{c.plasma_half_life_hours}h</td>
                      <td className="p-3 font-mono font-bold text-amber-400">{c.therapeutic_index_score}</td>
                      <td className="p-3">
                        {c.recommended_lead ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/50 border border-emerald-500/40 px-2 py-0.5 rounded text-[10px]">
                            <Award className="w-3 h-3" /> Lead ADC
                          </span>
                        ) : (
                          <span className="text-slate-500 text-[10px]">Candidate</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No constructs loaded. Screen a campaign above.</div>
          )}
        </div>
      </div>
    </div>
  );
};
