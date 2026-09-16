import React, { useState, useEffect } from 'react';
import { Layers, Activity, Sparkles, Zap, Flame, BarChart2, Radio, Microscope } from 'lucide-react';

interface MetaboliteProfile {
  id: string;
  metabolite_name: string;
  kegg_id: string;
  mz_ratio: number;
  spatial_zone: string;
  mean_intensity_au: number;
  fold_change_vs_normal: number;
  spatial_heterogeneity_score: number;
}

interface FluxRoute {
  id: string;
  pathway_name: string;
  estimated_flux_rate: number;
  pathway_activity_score: number;
  limiting_enzyme: string;
}

interface Experiment {
  id: string;
  tissue_sample_id: string;
  organ_type: string;
  matrix_compound: string;
  spatial_resolution_um: number;
  total_metabolites_identified: number;
  created_at: string;
  metabolites?: MetaboliteProfile[];
  flux_routes?: FluxRoute[];
}

export const SpatialMetabolomicsStudioPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null);
  const [sampleId, setSampleId] = useState('SAM-MALDI-2026-07');
  const [organType, setOrganType] = useState('Glioblastoma Microenvironment');
  const [loading, setLoading] = useState(false);

  const fetchExperiments = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/spatial-metabolomics/experiments');
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
      const res = await fetch(`http://127.0.0.1:8000/api/v1/spatial-metabolomics/experiments/${id}`);
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
      const res = await fetch('http://127.0.0.1:8000/api/v1/spatial-metabolomics/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tissue_sample_id: sampleId,
          organ_type: organType,
          matrix_compound: 'DHB',
          spatial_resolution_um: 20.0,
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
          <div className="p-3 bg-teal-950/60 border border-teal-500/40 rounded-xl text-teal-400">
            <Microscope className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-teal-400 to-emerald-300 bg-clip-text text-transparent">
              Spatial Metabolomics & MALDI Flux Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 57 • MALDI imaging mass spectrometry, tissue microdomain metabolic profiling & FBA flux balance simulation
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-teal-300">
            <Radio className="w-5 h-5" /> Launch MALDI Run
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Tissue Sample ID</label>
              <input
                type="text"
                value={sampleId}
                onChange={(e) => setSampleId(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Organ / Tissue Model</label>
              <input
                type="text"
                value={organType}
                onChange={(e) => setOrganType(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Acquiring Spectra...' : 'Run Spatial MALDI Flux'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">MALDI Experiments</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {experiments.map((exp) => (
                <div
                  key={exp.id}
                  onClick={() => fetchDetail(exp.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedExp?.id === exp.id
                      ? 'bg-teal-950/40 border-teal-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{exp.tissue_sample_id}</span>
                    <span className="text-teal-400 font-mono">{exp.total_metabolites_identified} Metabolites</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{exp.organ_type} ({exp.spatial_resolution_um}μm)</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Spatial Profiles & Flux Grid */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-teal-300">
              <Activity className="w-5 h-5" /> Metabolite Spatial Distributions
            </h2>
            {selectedExp && (
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                Matrix: {selectedExp.matrix_compound} @ {selectedExp.spatial_resolution_um}μm
              </span>
            )}
          </div>

          {selectedExp?.metabolites && selectedExp.metabolites.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Metabolite</th>
                    <th className="p-3">m/z (Da)</th>
                    <th className="p-3">Spatial Domain</th>
                    <th className="p-3">Mean Intensity (AU)</th>
                    <th className="p-3">Fold Change</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedExp.metabolites.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-semibold text-teal-300">
                        {m.metabolite_name} <span className="text-[10px] text-slate-500 font-mono">({m.kegg_id})</span>
                      </td>
                      <td className="p-3 font-mono text-emerald-300">{m.mz_ratio.toFixed(3)}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] border ${
                          m.spatial_zone === 'Tumor Core'
                            ? 'bg-rose-950/60 border-rose-500/40 text-rose-300'
                            : m.spatial_zone === 'Invasive Margin'
                            ? 'bg-amber-950/60 border-amber-500/40 text-amber-300'
                            : 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                        }`}>
                          {m.spatial_zone}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-slate-200">{m.mean_intensity_au.toLocaleString()} AU</td>
                      <td className="p-3 font-mono font-bold text-teal-400">
                        {m.fold_change_vs_normal > 1 ? `+${m.fold_change_vs_normal}x` : `${m.fold_change_vs_normal}x`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No profiles loaded. Execute or select an experiment above.</div>
          )}

          {/* Metabolic Flux Routes */}
          {selectedExp?.flux_routes && selectedExp.flux_routes.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-teal-300 uppercase tracking-wider flex items-center gap-2">
                <Flame className="w-4 h-4 text-emerald-400" /> Flux Balance Analysis (FBA) Pathways
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedExp.flux_routes.map((f) => (
                  <div key={f.id} className="p-4 bg-slate-950/80 border border-teal-500/30 rounded-xl space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-200 text-sm">{f.pathway_name}</span>
                      <span className="text-[10px] bg-teal-950 text-teal-400 px-2 py-0.5 rounded border border-teal-500/30 font-mono">
                        Enzyme: {f.limiting_enzyme}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 flex justify-between font-mono">
                      <span>Flux: {f.estimated_flux_rate} mmol/gDW/h</span>
                      <span className="text-emerald-400">Score: {(f.pathway_activity_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
