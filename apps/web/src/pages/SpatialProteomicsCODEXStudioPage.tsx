import React, { useState } from 'react';
import { Layers, ShieldCheck, Zap, Crosshair, Sparkles, Activity } from 'lucide-react';

export const SpatialProteomicsCODEXStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('Metastatic Melanoma Lymph Node Biopsy');
  const [tissueType, setTissueType] = useState('Cutaneous / Lymphoid Tissue');
  const [plexLevel, setPlexLevel] = useState(40);
  const [cellsEstimate, setCellsEstimate] = useState(8500);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const res = await fetch('/api/v1/spatial-proteomics-codex/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tissue_sample_name: sampleName,
          organ_tissue_type: tissueType,
          panel_plex_level: plexLevel,
          single_cells_estimate: cellsEstimate,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-fuchsia-500/10 text-fuchsia-400 rounded-xl border border-fuchsia-500/20">
            <Crosshair className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Multi-Modal Spatial Proteomics & CODEX Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 155: Ultra High-Plex (40+) Iterative Fluorescence, Cellular Neighborhood Phenotyping & Infiltration Scoring
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-fuchsia-400" />
              <span>CODEX Assay Setup</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tissue Sample Name</label>
                <input
                  type="text"
                  value={sampleName}
                  onChange={(e) => setSampleName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-fuchsia-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tissue / Organ Origin</label>
                <input
                  type="text"
                  value={tissueType}
                  onChange={(e) => setTissueType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-fuchsia-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Plex Level</label>
                  <input
                    type="number"
                    value={plexLevel}
                    onChange={(e) => setPlexLevel(parseInt(e.target.value) || 40)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-fuchsia-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Segmented Cells</label>
                  <input
                    type="number"
                    value={cellsEstimate}
                    onChange={(e) => setCellsEstimate(parseInt(e.target.value) || 5000)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-fuchsia-500"
                  />
                </div>
              </div>

              <button
                onClick={handleProcess}
                disabled={processing}
                className="w-full py-3 bg-gradient-to-r from-fuchsia-600 to-pink-600 hover:from-fuchsia-500 hover:to-pink-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-fuchsia-500/20 disabled:opacity-50"
              >
                {processing ? 'Segmenting Multiplex Stacks...' : 'Process CODEX Imaging Panel'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-fuchsia-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-fuchsia-400">Multiplexing Quality & Infiltration</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Total Cells</p>
                      <p className="text-lg font-bold text-white mt-1">{result.single_cells_segmented.toLocaleString()}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mean SNR</p>
                      <p className="text-lg font-bold text-fuchsia-400 mt-1">{result.mean_signal_to_background}:1</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Neighborhoods</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.cellular_neighborhoods_count} Clusters</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Infiltration Score</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{(result.immune_infiltration_score * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">High-Plex Antibody Channels</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Marker</th>
                          <th className="px-4 py-3">Compartment</th>
                          <th className="px-4 py-3">Intensity (MFI)</th>
                          <th className="px-4 py-3">SNR</th>
                          <th className="px-4 py-3">Positive %</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.marker_expressions.map((m: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-fuchsia-400">{m.marker_name}</td>
                            <td className="px-4 py-3.5 text-slate-400">{m.cellular_compartment}</td>
                            <td className="px-4 py-3.5 text-slate-200">{m.mean_fluorescence_intensity.toLocaleString()}</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{m.signal_to_noise_ratio}x</td>
                            <td className="px-4 py-3.5 text-cyan-400">{m.positive_cells_percentage}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure tissue parameters and run CODEX spatial single-cell multiplex processing.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpatialProteomicsCODEXStudioPage;
