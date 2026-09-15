import React, { useState } from 'react';
import { 
  Pill, 
  Sparkles, 
  Flame, 
  ShieldCheck, 
  TrendingUp, 
  Download, 
  RefreshCw, 
  CheckCircle2, 
  Activity,
  Layers,
  Percent
} from 'lucide-react';

interface Candidate {
  id: string;
  name: string;
  original: string;
  mechanism: string;
  connectivity: number;
  ic50: number;
  pubs: number;
}

interface Synergy {
  drugA: string;
  drugB: string;
  zipScore: number;
  bliss: number;
  loewe: number;
  reduction: number;
  classification: string;
  risk: string;
}

export const DrugSynergyStudioPage: React.FC = () => {
  const [diseaseIndication, setDiseaseIndication] = useState('Sorafenib-Resistant Hepatocellular Carcinoma');
  const [activeCandidate, setActiveCandidate] = useState<Candidate | null>(null);

  const candidates: Candidate[] = [
    {
      id: 'c1',
      name: 'Niclosamide',
      original: 'Anthelmintic (FDA Approved)',
      mechanism: 'Mitochondrial oxidative phosphorylation uncoupling and STAT3 / Wnt transcriptional blockade.',
      connectivity: -0.925,
      ic50: 0.85,
      pubs: 48,
    },
    {
      id: 'c2',
      name: 'Disulfiram',
      original: 'Alcohol Deterrent (FDA Approved)',
      mechanism: 'ALDH1A1 copper-dependent carbamylation inducing proteasome inhibition in cancer stem cells.',
      connectivity: -0.874,
      ic50: 1.45,
      pubs: 62,
    },
    {
      id: 'c3',
      name: 'Metformin',
      original: 'Type 2 Diabetes (FDA Approved)',
      mechanism: 'Mitochondrial Complex I inhibition activating AMPK and repressing mTORC1 translation.',
      connectivity: -0.782,
      ic50: 3.20,
      pubs: 140,
    },
    {
      id: 'c4',
      name: 'Auranofin',
      original: 'Rheumatoid Arthritis (FDA Approved)',
      mechanism: 'Thioredoxin reductase (TrxR1) inhibition inducing catastrophic ROS accumulation.',
      connectivity: -0.841,
      ic50: 0.62,
      pubs: 35,
    },
  ];

  const synergy: Synergy = {
    drugA: 'Niclosamide',
    drugB: 'Sorafenib (Standard Care)',
    zipScore: 19.85,
    bliss: 16.4,
    loewe: 0.58,
    reduction: 4.2,
    classification: 'Highly Synergistic (ZIP δ > 10.0)',
    risk: 'Low (Non-Overlapping Toxicities)',
  };

  // 4x4 ZIP Synergy Matrix
  const matrix = [
    [0.0, 4.2, 8.5, 12.1],
    [3.8, 11.4, 18.2, 22.8],
    [7.2, 17.6, 24.5, 27.2],
    [10.5, 21.0, 26.8, 29.5],
  ];

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-400">
              <Pill className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Drug Repurposing & Combination Synergy Simulator
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Generation 17 • Phase 45
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Transcriptomic connectivity map inversion, ZIP synergy matrix modeling, and Loewe/Bliss combination index calculation.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={diseaseIndication}
            onChange={(e) => setDiseaseIndication(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option>Sorafenib-Resistant Hepatocellular Carcinoma</option>
            <option>Temozolomide-Refractory Glioblastoma</option>
            <option>Osimertinib-Resistant EGFR+ NSCLC</option>
            <option>Platinum-Resistant High-Grade Serous Ovarian Cancer</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-emerald-500/20">
            <RefreshCw className="w-4 h-4" />
            Screen 2,450 Compounds
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Repurposed Candidate List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                Top Connectivity Inversion Candidates
              </h2>
              <span className="text-xs text-slate-400">Library: 2,450 FDA-Approved & Clinical Drugs</span>
            </div>

            <div className="space-y-4">
              {candidates.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setActiveCandidate(c)}
                  className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 transition space-y-3 cursor-pointer"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                    <div>
                      <h3 className="text-base font-semibold text-white flex items-center gap-2">
                        {c.name}
                        <span className="text-xs font-normal text-slate-400">({c.original})</span>
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 font-mono text-xs font-semibold">
                        CMap Score {c.connectivity}
                      </span>
                      <span className="px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono text-xs">
                        IC50 = {c.ic50} µM
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{c.mechanism}</p>

                  <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1 text-emerald-400">
                      <ShieldCheck className="w-3.5 h-3.5" /> High Safety Tier (FDA Approved)
                    </span>
                    <span className="text-slate-500">{c.pubs} Peer-Reviewed Articles</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: 2D ZIP Synergy Heatmap & Combination Index */}
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-semibold text-white">ZIP Synergy Heatmap</h3>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/50">
                δ = {synergy.zipScore}
              </span>
            </div>

            <p className="text-xs text-slate-400">
              Combination: <span className="text-emerald-400 font-semibold">{synergy.drugA}</span> + <span className="text-cyan-400 font-semibold">{synergy.drugB}</span>
            </p>

            {/* 4x4 Heatmap Matrix */}
            <div className="space-y-1.5 p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] text-slate-500 text-center pb-1">Niclosamide Dose (µM) vs Sorafenib Dose (µM)</div>
              <div className="grid grid-cols-4 gap-1.5">
                {matrix.map((row, rIdx) => (
                  row.map((val, cIdx) => {
                    const intensity = Math.min(1, val / 30.0);

                    return (
                      <div
                        key={`${rIdx}-${cIdx}`}
                        className="h-10 rounded-lg flex items-center justify-center font-mono text-xs font-semibold transition hover:scale-105"
                        style={{
                          backgroundColor: val > 0 
                            ? `rgba(16, 185, 129, ${Math.max(0.15, intensity)})` 
                            : 'rgba(30, 41, 59, 0.5)',
                          color: val > 15 ? '#ffffff' : '#a7f3d0'
                        }}
                      >
                        +{val.toFixed(1)}
                      </div>
                    );
                  })
                ))}
              </div>
            </div>

            {/* Combination Telemetry */}
            <div className="space-y-2 text-xs">
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Loewe Combination Index (CI):</span>
                <span className="font-mono text-emerald-400 font-semibold">{synergy.loewe} (&lt; 1.0 Synergistic)</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Dose Reduction Index (DRI):</span>
                <span className="font-mono text-white font-semibold">{synergy.reduction}x Sparing</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-slate-400">Drug-Drug Interaction Risk:</span>
                <span className="font-mono text-emerald-400 font-semibold">{synergy.risk}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrugSynergyStudioPage;
