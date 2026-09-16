import React, { useState, useEffect } from 'react';
import { Layers, Activity, Sparkles, Filter, Database, Dna, Compass, BarChart3 } from 'lucide-react';

interface Motif {
  id: string;
  motif_name: string;
  pwm_match_score: number;
  consensus_sequence: string;
}

interface Peak {
  id: string;
  chromosome: string;
  start_pos: number;
  end_pos: number;
  peak_score: number;
  fold_enrichment: number;
  p_value_neg_log10: number;
  genomic_annotation: string;
  nearest_gene: string;
  distance_to_tss: number;
  motifs: Motif[];
}

interface Experiment {
  id: string;
  sample_id: string;
  tissue_type: string;
  assay_type: string;
  sequencing_depth_millions: number;
  total_peaks_called: number;
  created_at: string;
  peaks?: Peak[];
}

export const EpigenomicsStudioPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);
  const [sampleId, setSampleId] = useState('SAM-ATAC-2026-01');
  const [tissueType, setTissueType] = useState('CD8+ T-cell Exhaustion');
  const [loading, setLoading] = useState(false);

  const fetchExperiments = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/epigenomics/experiments');
      if (res.ok) {
        const data = await res.json();
        setExperiments(data);
        if (data.length > 0 && !selectedExp) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/epigenomics/experiments/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedExp(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/epigenomics/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sample_id: sampleId,
          tissue_type: tissueType,
          assay_type: 'ATAC-seq',
          sequencing_depth_millions: 54.0,
        }),
      });
      if (res.ok) {
        await fetchExperiments();
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
          <div className="p-3 bg-violet-950/60 border border-violet-500/40 rounded-xl text-violet-400">
            <Compass className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-cyan-300 bg-clip-text text-transparent">
              Epigenomic Chromatin & ATAC-seq Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 56 • Open-chromatin peak calling, transcription factor motif scanning & regulatory landscape cartography
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-violet-300">
            <Layers className="w-5 h-5" /> Launch Epigenomic Run
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Sample ID</label>
              <input
                type="text"
                value={sampleId}
                onChange={(e) => setSampleId(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Tissue / Cell Type</label>
              <input
                type="text"
                value={tissueType}
                onChange={(e) => setTissueType(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Calling Peaks...' : 'Execute ATAC-seq Peak Calling'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Experiments</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {experiments.map((exp) => (
                <div
                  key={exp.id}
                  onClick={() => fetchDetail(exp.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedExp?.id === exp.id
                      ? 'bg-violet-950/40 border-violet-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{exp.sample_id}</span>
                    <span className="text-violet-400 font-mono">{exp.total_peaks_called} Peaks</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{exp.tissue_type} ({exp.assay_type})</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Peaks & TF Motifs Grid */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-violet-300">
              <Activity className="w-5 h-5" /> Chromatin Accessibility Peaks & Motifs
            </h2>
            {selectedExp && (
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                Depth: {selectedExp.sequencing_depth_millions}M Reads
              </span>
            )}
          </div>

          {selectedExp?.peaks && selectedExp.peaks.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Genomic Locus</th>
                    <th className="p-3">Nearest Gene</th>
                    <th className="p-3">Annotation</th>
                    <th className="p-3">Peak Score</th>
                    <th className="p-3">Fold Enrich</th>
                    <th className="p-3">Enriched TF Motifs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedExp.peaks.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-mono text-cyan-300">
                        {p.chromosome}:{p.start_pos.toLocaleString()}-{p.end_pos.toLocaleString()}
                      </td>
                      <td className="p-3 font-semibold text-violet-300">
                        {p.nearest_gene} <span className="text-[10px] text-slate-500">({p.distance_to_tss}bp)</span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] border ${
                          p.genomic_annotation === 'Promoter'
                            ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                            : p.genomic_annotation === 'Enhancer'
                            ? 'bg-amber-950/60 border-amber-500/40 text-amber-300'
                            : 'bg-slate-800 border-slate-700 text-slate-400'
                        }`}>
                          {p.genomic_annotation}
                        </span>
                      </td>
                      <td className="p-3 font-mono font-bold text-slate-200">{p.peak_score}</td>
                      <td className="p-3 font-mono text-violet-400">{p.fold_enrichment}x</td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-1">
                          {p.motifs.map((m) => (
                            <span key={m.id} className="bg-slate-800 text-cyan-300 px-1.5 py-0.5 rounded text-[10px] border border-slate-700">
                              {m.motif_name} ({m.pwm_match_score})
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No peaks loaded. Execute or select an experiment above.</div>
          )}
        </div>
      </div>
    </div>
  );
};
