import React, { useState } from 'react';
import { Activity, ShieldCheck, Zap, Box, Compass, BarChart2, Eye, Award } from 'lucide-react';

interface Particle {
  particle_id_str: string;
  x_vox: number;
  y_vox: number;
  z_vox: number;
  euler_rot_deg: number;
  euler_tilt_deg: number;
  euler_psi_deg: number;
  cross_correlation_score: number;
  conformational_state: string;
}

interface ResClass {
  class_number: number;
  class_name: string;
  particle_occupancy_pct: number;
  resolution_angstrom: number;
  fsc_cutoff_type: string;
}

export const CryoETSubtomogramTomographyStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('In-Situ Synaptic AMPAR-TARP Subtomogram Averaging');
  const [context, setContext] = useState('Intact Neuronal Synapse (In-Situ)');
  const [complexName, setComplexName] = useState('AMPAR-TARP Ion Channel Complex');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleRunReconstruction = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/cryoet-subtomogram-tomography/reconstruct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          cellular_context: context,
          target_complex_name: complexName,
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
          <div className="flex items-center gap-2 text-violet-400 font-semibold tracking-wider text-sm uppercase mb-1">
            <Box className="w-4 h-4" /> Cryo-ET & In-Situ Structural Biology
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Cryo-ET Subtomogram Averaging Studio</h1>
          <p className="text-slate-400 text-sm mt-1">
            Reconstruct macromolecular complexes directly inside native cellular contexts with 3D subtomogram averaging and Gold-Standard FSC.
          </p>
        </div>
        <button
          onClick={handleRunReconstruction}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-400 hover:to-indigo-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-violet-500/20 disabled:opacity-50"
        >
          {loading ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          Run 3D Subtomogram Refinement
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl space-y-4">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Cellular In-Situ Context</label>
          <input
            type="text"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500"
          />

          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Target Complex</label>
          <input
            type="text"
            value={complexName}
            onChange={(e) => setComplexName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500"
          />
        </div>

        <div className="md:col-span-2 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <Compass className="w-5 h-5 text-violet-400" /> In-Situ Subtomogram Refinement Workflow
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Cryo-electron tomography reconstructs tilt-series into 3D volumes (tomograms). Subtomogram averaging aligns thousands of sub-volumes through iterative Euler search $(\phi, \theta, \psi)$ with 3D CTF correction and missing-wedge compensation to achieve near-atomic in-situ resolution.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800/80">
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Tilt Range</div>
              <div className="text-xl font-bold text-white mt-1">-60° to +60° (2° step)</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Target Resolution</div>
              <div className="text-xl font-bold text-violet-400 mt-1">3.42 Å (FSC 0.143)</div>
            </div>
            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs text-slate-400 uppercase font-semibold">Classification</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">3D Multi-State</div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Subtomograms Averaged</div>
              <div className="text-2xl font-black text-white mt-2">{result.particles_picked_count}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Gold-Standard FSC</div>
              <div className="text-2xl font-black text-violet-400 mt-2">{result.final_fsc_resolution_angstrom} Å</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">Mean Cross-Corr</div>
              <div className="text-2xl font-black text-indigo-400 mt-2">{result.summary_metrics?.mean_cross_correlation}</div>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs text-slate-400 uppercase font-bold">In-Situ States</div>
              <div className="text-2xl font-black text-emerald-400 mt-2">{result.classes?.length || 3} Classes</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Eye className="w-5 h-5 text-violet-400" /> Extracted Subtomogram Orientations
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase">
                      <th className="pb-3 font-semibold">Particle ID</th>
                      <th className="pb-3 font-semibold">Coordinates (vox)</th>
                      <th className="pb-3 font-semibold">Euler (Rot/Tilt/Psi)</th>
                      <th className="pb-3 font-semibold">Cross-Corr</th>
                      <th className="pb-3 font-semibold">State</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {result.particles?.map((p: Particle, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 font-mono text-xs text-violet-300">{p.particle_id_str}</td>
                        <td className="py-3 text-slate-400 text-xs">{p.x_vox.toFixed(0)}, {p.y_vox.toFixed(0)}, {p.z_vox.toFixed(0)}</td>
                        <td className="py-3 font-mono text-xs text-slate-300">{p.euler_rot_deg}°, {p.euler_tilt_deg}°, {p.euler_psi_deg}°</td>
                        <td className="py-3 font-bold text-emerald-400">{p.cross_correlation_score}</td>
                        <td className="py-3 text-cyan-300 text-xs">{p.conformational_state}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-emerald-400" /> 3D Classification & FSC Resolutions
              </h3>
              <div className="space-y-3">
                {result.classes?.map((c: ResClass, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-violet-300 font-bold text-sm">{c.class_name}</span>
                      <span className="text-emerald-400 font-mono font-bold text-sm">{c.resolution_angstrom} Å</span>
                    </div>
                    <div className="flex justify-between items-center text-xs text-slate-400">
                      <span>Occupancy: {c.particle_occupancy_pct}%</span>
                      <span className="text-slate-500">{c.fsc_cutoff_type}</span>
                    </div>
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

export default CryoETSubtomogramTomographyStudioPage;
