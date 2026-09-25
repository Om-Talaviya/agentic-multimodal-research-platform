import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, Compass, Dna, BarChart2, Layers, Crosshair } from 'lucide-react';

interface Spot {
  spot_barcode: string;
  x_coord: number;
  y_coord: number;
  target_mrna_symbol: string;
  mrna_normalized_count: number;
  target_protein_antibody: string;
  protein_adt_signal: number;
  colocalization_pearson_r: number;
  subcellular_niche: string;
}

interface Enrichment {
  marker_pair: string;
  enrichment_z_score: number;
  fdr_q_value: number;
  biological_relevance: string;
}

export const SpatialProteogenomicsStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Glioblastoma Spatial CITE-seq Subcellular Profiling');
  const [sampleId, setSampleId] = useState('GBM_TME_Slice_04');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/spatial-proteogenomics/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          tissue_sample_id: sampleId,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 text-rose-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Compass className="w-4 h-4" /> Spatial Multi-Omics & Subcellular CITE-seq
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Spatial Proteogenomics Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Simultaneously quantify RNA transcriptomes and surface/intracellular protein epitopes with subcellular co-localization.
          </p>
        </div>
        <button
          onClick={handleRunAnalysis}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-400 hover:to-pink-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-rose-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Run Spatial Co-Detection
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-rose-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Tissue Slice Sample ID</label>
          <input
            type="text"
            value={sampleId}
            onChange={(e) => setSampleId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-rose-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <Layers className="w-5 h-5 text-rose-400" /> Multi-Omics Co-Registration Methodology
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Spatial CITE-seq couples microfluidic deterministic barcoding with oligonucleotide-conjugated antibody tags (ADT). Simultaneous capture of whole transcriptome mRNA and surface protein markers enables detection of post-transcriptional discordance and immune niche microdomains.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Modality Dual-Plex</div>
              <div className="text-xl font-bold text-white mt-1">RNA + ADT Protein</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Resolution</div>
              <div className="text-xl font-bold text-rose-400 mt-1">10 µm Grid Spot</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Concordance Metric</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">Pearson r &gt; 0.85</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Total Spots Co-Mapped</div>
              <div className="text-2xl font-black text-white mt-2">{result.total_spots_analyzed}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Mean Pearson r</div>
              <div className="text-2xl font-black text-rose-400 mt-2">{result.mean_pearson_colocalization_r}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Subcellular Niches</div>
              <div className="text-2xl font-black text-pink-400 mt-2">{result.subcellular_niche_count} Niches</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Concordance Tier</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">Ultra-High</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Crosshair className="w-5 h-5 text-rose-400" /> Spatial Spot Co-Localization Map
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                      <th className="pb-3 font-semibold">Spot</th>
                      <th className="pb-3 font-semibold">mRNA (Counts)</th>
                      <th className="pb-3 font-semibold">Protein (ADT)</th>
                      <th className="pb-3 font-semibold">Pearson r</th>
                      <th className="pb-3 font-semibold">Niche</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.spots?.map((s: Spot, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 font-mono text-xs text-slate-300">{s.spot_barcode}</td>
                        <td className="py-3 font-mono text-cyan-300">{s.target_mrna_symbol} ({s.mrna_normalized_count})</td>
                        <td className="py-3 font-mono text-rose-300">{s.target_protein_antibody} ({s.protein_adt_signal})</td>
                        <td className="py-3 text-emerald-400 font-bold">{s.colocalization_pearson_r}</td>
                        <td className="py-3 text-slate-400 text-xs">{s.subcellular_niche}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" /> Marker Pair Enrichment in Niches
              </h3>
              <div className="space-y-3">
                {result.enrichment_metrics?.map((e: Enrichment, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-rose-300 font-semibold text-sm">{e.marker_pair}</span>
                      <span className="text-emerald-400 font-mono font-bold text-xs">z = +{e.enrichment_z_score} (q = {e.fdr_q_value})</span>
                    </div>
                    <p className="text-slate-400 text-xs">{e.biological_relevance}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpatialProteogenomicsStudioPage;
