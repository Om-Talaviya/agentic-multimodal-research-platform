import React, { useState, useEffect } from 'react';
import { 
  Box, Eye, Layers, Sparkles, Activity, CheckCircle, RefreshCw, BarChart2, ShieldCheck, Zap
} from 'lucide-react';

interface DensityMap {
  id: string;
  title: string;
  emdb_id: string;
  nominal_resolution_angstrom: number;
  voxel_size_angstrom: number;
  box_dimensions: string;
  status: string;
}

export const CryoEMStudioPage: React.FC = () => {
  const [maps, setMaps] = useState<DensityMap[]>([]);
  const [selectedMap, setSelectedMap] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [fitting, setFitting] = useState(false);
  
  const [title, setTitle] = useState('2.4A Cryo-EM Structure of Human PCSK9-Antibody Complex');
  const [emdbId, setEmdbId] = useState('EMD-30452');
  const [pdbId, setPdbId] = useState('7KRR');
  const [resolution, setResolution] = useState(2.4);

  const fetchMaps = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/cryoem/maps', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMaps(data);
        if (data.length > 0) {
          fetchMapDetails(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchMapDetails = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/cryoem/maps/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedMap(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchMaps();
  }, []);

  const handleFitMap = async (e: React.FormEvent) => {
    e.preventDefault();
    setFitting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/cryoem/fit-map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          emdb_id: emdbId,
          pdb_model_id: pdbId,
          target_resolution: parseFloat(resolution.toString())
        })
      });
      if (res.ok) {
        const created = await res.json();
        await fetchMaps();
        await fetchMapDetails(created.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setFitting(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in text-slate-100">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-cyan-600 to-blue-700 rounded-xl shadow-lg shadow-cyan-900/30">
              <Box className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Autonomous Cryo-EM Structural Biology Studio
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  Phase 47
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-0.5">
                3D Volumetric Density Map Fitting, Fourier Shell Correlation (FSC) & Macromolecular Assembly
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchMaps}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Density Map Fitting Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            Cryo-EM Map Parameters
          </h2>
          <form onSubmit={handleFitMap} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Density Map Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">EMDB Accession</label>
                <input
                  type="text"
                  value={emdbId}
                  onChange={(e) => setEmdbId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">PDB Model ID</label>
                <input
                  type="text"
                  value={pdbId}
                  onChange={(e) => setPdbId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Target Resolution (Å)</label>
              <input
                type="number"
                step="0.1"
                value={resolution}
                onChange={(e) => setResolution(parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={fitting}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-cyan-900/20 disabled:opacity-50"
            >
              {fitting ? 'Refining Real-Space Coordinates...' : 'Fit 3D Density Map'}
            </button>
          </form>

          {/* Map List */}
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Fitted Cryo-EM Maps</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {maps.map((m) => (
                <div
                  key={m.id}
                  onClick={() => fetchMapDetails(m.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition text-xs ${
                    selectedMap?.id === m.id
                      ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-200'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{m.title}</div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800">{m.emdb_id}</span>
                    <span>{m.nominal_resolution_angstrom} Å</span>
                    <span>{m.box_dimensions}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Structural Telemetry & FSC Curve */}
        <div className="lg:col-span-2 space-y-6">
          {selectedMap ? (
            <>
              {/* Telemetry Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Box className="w-3.5 h-3.5 text-cyan-400"/> Resolution</div>
                  <div className="text-xl font-bold text-white mt-1">{selectedMap.resolution} Å</div>
                  <div className="text-[10px] text-cyan-400 mt-0.5">FSC @ 0.143 cutoff</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-blue-400"/> Map-Model CCC</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedMap.fittings?.[0]?.ccc || 0.885}
                  </div>
                  <div className="text-[10px] text-blue-400 mt-0.5">Real-space fit</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400"/> Ramachandran</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedMap.fittings?.[0]?.ramachandran_pct || 97.8}%
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-0.5">Favored backbone</div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-indigo-400"/> Binding ΔG</div>
                  <div className="text-xl font-bold text-white mt-1">
                    {selectedMap.complexes?.[0]?.delta_g || -16.4} kcal/mol
                  </div>
                  <div className="text-[10px] text-indigo-400 mt-0.5">Buried Area: {selectedMap.complexes?.[0]?.bsa || 3820} Å²</div>
                </div>
              </div>

              {/* Macromolecular Interface Hotspots */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Macromolecular Interface Hotspots & Stoichiometry ({selectedMap.complexes?.[0]?.stoichiometry || 'A2B2'})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedMap.complexes?.[0]?.hotspots?.map((h: any, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-cyan-300">{h.chain_a_residue} ↔ {h.chain_b_residue}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          {h.distance_angstrom} Å
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400">Interaction: <span className="text-slate-200">{h.interaction_type}</span></div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Fourier Shell Correlation (FSC) Curve */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-cyan-400" />
                  Fourier Shell Correlation (FSC) Spatial Frequency Spectrum
                </h3>
                <div className="grid grid-cols-5 sm:grid-cols-10 gap-2 text-center mt-3">
                  {selectedMap.fsc_curve?.slice(0, 10).map((pt: any, i: number) => (
                    <div key={i} className="p-2 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">{pt.resolution_angstrom} Å</div>
                      <div className="text-xs font-bold text-cyan-400 mt-1">{(pt.fsc_correlation).toFixed(2)}</div>
                      <div className="text-[9px] text-slate-500 mt-0.5">{pt.spatial_frequency_inv_angstrom} 1/Å</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500">
              <Box className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
              <p className="text-sm">Select or fit a Cryo-EM density map to inspect structural coordinates</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
