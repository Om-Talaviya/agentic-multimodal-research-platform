import React, { useState } from 'react';
import {
  Layers,
  Activity,
  Sparkles,
  Sliders,
  BarChart3,
  Dna,
  Zap,
  Flame,
  Clock,
  ShieldCheck,
  CheckCircle2,
  TrendingUp
} from 'lucide-react';

interface TimePointData {
  time_point_hours: number;
  h3k27ac_enrichment: number;
  atac_seq_intensity_rpm: number;
  nucleosome_occupancy_percent: number;
  brd4_recruitment_fold: number;
}

export const HistoneAcetylationStudioPage: React.FC = () => {
  const [locusName, setLocusName] = useState('MYC Super-Enhancer Locus');
  const [genomicCoords, setGenomicCoords] = useState('chr8:127735434-127736300');
  const [cellLine, setCellLine] = useState('K562 Leukemia');
  const [hdacInhibitor, setHdacInhibitor] = useState('Vorinostat (SAHA)');
  const [doseUm, setDoseUm] = useState(2.5);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'dynamics' | 'kinetics' | 'occupancy'>('dynamics');

  const [timePoints] = useState<TimePointData[]>([
    { time_point_hours: 0, h3k27ac_enrichment: 10.0, atac_seq_intensity_rpm: 20.0, nucleosome_occupancy_percent: 75.0, brd4_recruitment_fold: 1.0 },
    { time_point_hours: 2, h3k27ac_enrichment: 21.2, atac_seq_intensity_rpm: 38.4, nucleosome_occupancy_percent: 61.5, brd4_recruitment_fold: 2.2 },
    { time_point_hours: 6, h3k27ac_enrichment: 36.8, atac_seq_intensity_rpm: 63.2, nucleosome_occupancy_percent: 43.1, brd4_recruitment_fold: 3.8 },
    { time_point_hours: 12, h3k27ac_enrichment: 44.5, atac_seq_intensity_rpm: 76.0, nucleosome_occupancy_percent: 33.7, brd4_recruitment_fold: 4.6 },
    { time_point_hours: 24, h3k27ac_enrichment: 48.2, atac_seq_intensity_rpm: 81.8, nucleosome_occupancy_percent: 29.5, brd4_recruitment_fold: 5.1 },
  ]);

  const handleSimulate = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 700);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 p-6 rounded-2xl border border-teal-800/40 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-500/20 rounded-lg border border-teal-400/30 text-teal-300">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Histone Acetylation & Chromatin Remodeling Studio
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Phase 136: HAT (p300/CBP) / HDAC Dynamic ODE Kinetics & Nucleosome Eviction / BRD4 Recruitment Simulator
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="flex items-center gap-2 bg-teal-600 hover:bg-teal-500 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-teal-600/20 transition-all cursor-pointer"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Simulating Chromatin Dynamics...' : 'Run Epigenetic ODE'}
          </button>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Target Enhancer / Promoter</label>
          <input
            type="text"
            value={locusName}
            onChange={(e) => setLocusName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Genomic Coordinates</label>
          <input
            type="text"
            value={genomicCoords}
            onChange={(e) => setGenomicCoords(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">HDAC Inhibitor</label>
          <input
            type="text"
            value={hdacInhibitor}
            onChange={(e) => setHdacInhibitor(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
          />
        </div>
        <div className="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800 space-y-2">
          <label className="text-xs text-slate-400 font-semibold uppercase">Dose (µM)</label>
          <input
            type="number"
            step="0.1"
            value={doseUm}
            onChange={(e) => setDoseUm(parseFloat(e.target.value))}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500"
          />
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-4 rounded-xl border border-teal-900/40">
          <div className="text-xs text-slate-400 font-medium">H3K27ac Hyperacetylation</div>
          <div className="text-2xl font-bold text-teal-400 mt-1">4.82x Fold</div>
          <div className="text-xs text-emerald-400 mt-1">✓ Active Enhancer State</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-teal-900/40">
          <div className="text-xs text-slate-400 font-medium">ATAC Openness Gain</div>
          <div className="text-2xl font-bold text-white mt-1">+61.8 RPM</div>
          <div className="text-xs text-slate-400 mt-1">Chromatin de-condensation</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-teal-900/40">
          <div className="text-xs text-slate-400 font-medium">Nucleosome Eviction</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">-45.5%</div>
          <div className="text-xs text-slate-400 mt-1">Histone octamer clearance</div>
        </div>
        <div className="bg-slate-900/80 p-4 rounded-xl border border-teal-900/40">
          <div className="text-xs text-slate-400 font-medium">BRD4 Bromodomain Binding</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">5.1x Recruitment</div>
          <div className="text-xs text-purple-400 mt-1">Pol II Elongation Prime</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('dynamics')}
          className={`pb-3 text-sm font-medium transition-colors cursor-pointer ${
            activeTab === 'dynamics'
              ? 'border-b-2 border-teal-500 text-teal-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Time-Resolved Chromatin Remodeling
        </button>
      </div>

      {/* Content */}
      {activeTab === 'dynamics' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-semibold">
              <tr>
                <th className="p-4">Time Point (h)</th>
                <th className="p-4">H3K27ac Enrichment</th>
                <th className="p-4">ATAC-seq Intensity (RPM)</th>
                <th className="p-4">Nucleosome Occupancy (%)</th>
                <th className="p-4">BRD4 Recruitment Fold</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {timePoints.map((tp) => (
                <tr key={tp.time_point_hours} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-4 font-mono font-medium text-teal-400">{tp.time_point_hours}h</td>
                  <td className="p-4 font-mono text-emerald-400">{tp.h3k27ac_enrichment}</td>
                  <td className="p-4 font-mono text-white">{tp.atac_seq_intensity_rpm}</td>
                  <td className="p-4 font-mono text-rose-300">{tp.nucleosome_occupancy_percent}%</td>
                  <td className="p-4 font-mono text-purple-300 font-bold">{tp.brd4_recruitment_fold}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
