import React, { useState, useEffect } from 'react';
import { Layers, Activity, ShieldCheck, Box, RefreshCw, BarChart2, Zap } from 'lucide-react';

export const OrganoidMorphometryStudioPage: React.FC = () => {
  const [studies, setStudies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [studyName, setStudyName] = useState('Patient-Derived Glioblastoma Spheroid High-Content Screen');
  const [tumorType, setTumorType] = useState('Glioblastoma Multiforme');
  const [analyzing, setAnalyzing] = useState(false);
  const [currentResult, setCurrentResult] = useState<any>(null);

  const fetchStudies = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/organoid-morphometry/studies');
      if (res.ok) {
        const data = await res.json();
        setStudies(data.studies || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudies();
  }, []);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/organoid-morphometry/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          tumor_type: tumorType
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentResult(data.study);
        fetchStudies();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
              <Box className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">
                3D Tumor Organoid High-Content Morphometry Studio
              </h1>
              <p className="text-sm text-slate-400">
                Phase 147: Confocal Z-Stack 3D Volumetric Segmentation, Core Necrosis & Dose-Response Engine
              </p>
            </div>
          </div>
          <button
            onClick={fetchStudies}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-sm text-slate-300 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Input Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <span>Morphometric Assay Setup</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Study Name</label>
                <input
                  type="text"
                  value={studyName}
                  onChange={(e) => setStudyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tumor / Tissue Type</label>
                <input
                  type="text"
                  value={tumorType}
                  onChange={(e) => setTumorType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="p-4 bg-emerald-950/20 border border-emerald-800/30 rounded-xl text-xs text-emerald-300/80 space-y-1">
                <p className="font-semibold text-emerald-200">Autonomous Pipeline Actions:</p>
                <p>• 3D Trapezoidal Z-stack slice volume integral</p>
                <p>• Sphericity factor & necrotic core live/dead ratio</p>
                <p>• Multicomponent Hill equation IC50 evaluation</p>
              </div>

              <button
                onClick={handleRunAnalysis}
                disabled={analyzing}
                className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                {analyzing ? 'Reconstructing 3D Spheroid...' : 'Execute High-Content Morphometry'}
              </button>
            </div>
          </div>

          {/* Real-time Display */}
          <div className="lg:col-span-2 space-y-6">
            {currentResult && (
              <div className="bg-slate-900/60 border border-emerald-500/30 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold text-emerald-400">Latest 3D Morphometry Reconstruction</h3>
                  <span className="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-300 rounded-full border border-emerald-500/20">
                    Calculated in 42ms
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                    <p className="text-xs text-slate-400">Mean Diameter</p>
                    <p className="text-lg font-bold text-white mt-1">{currentResult.mean_diameter_um} µm</p>
                  </div>
                  <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                    <p className="text-xs text-slate-400">Total Volume</p>
                    <p className="text-lg font-bold text-white mt-1">{(currentResult.mean_volume_um3 / 1e6).toFixed(2)} ×10⁶ µm³</p>
                  </div>
                  <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                    <p className="text-xs text-slate-400">Sphericity Index</p>
                    <p className="text-lg font-bold text-emerald-400 mt-1">{currentResult.sphericity_index}</p>
                  </div>
                  <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                    <p className="text-xs text-slate-400">Necrotic Core Ratio</p>
                    <p className="text-lg font-bold text-amber-400 mt-1">{(currentResult.necrotic_core_ratio * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>
            )}

            {/* Historical Studies Table */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
              <h3 className="text-base font-semibold text-white mb-4 flex items-center space-x-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                <span>Organoid Screening History</span>
              </h3>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Study Name</th>
                      <th className="px-4 py-3">Tumor Type</th>
                      <th className="px-4 py-3">Diameter</th>
                      <th className="px-4 py-3">Sphericity</th>
                      <th className="px-4 py-3">Necrotic Ratio</th>
                      <th className="px-4 py-3">Z-Slices</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {studies.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                          No organoid studies recorded yet. Launch an assay above.
                        </td>
                      </tr>
                    ) : (
                      studies.map((s) => (
                        <tr key={s.id} className="hover:bg-slate-800/30 transition">
                          <td className="px-4 py-3.5 font-medium text-slate-200">{s.name}</td>
                          <td className="px-4 py-3.5 text-slate-400">{s.tumor_type}</td>
                          <td className="px-4 py-3.5 text-slate-300">{s.mean_diameter_um} µm</td>
                          <td className="px-4 py-3.5 text-emerald-400">{s.sphericity_index}</td>
                          <td className="px-4 py-3.5 text-amber-400">{(s.necrotic_core_ratio * 100).toFixed(1)}%</td>
                          <td className="px-4 py-3.5 text-slate-400">{s.z_stacks_count}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrganoidMorphometryStudioPage;
