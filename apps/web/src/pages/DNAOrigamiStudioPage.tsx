import React, { useState } from 'react';
import { Cpu, ShieldCheck, Zap, Box, Compass, Sparkles } from 'lucide-react';

export const DNAOrigamiStudioPage: React.FC = () => {
  const [robotName, setRobotName] = useState('Autonomous Thrombin Delivery Nanorobot');
  const [geometry, setGeometry] = useState('Hexagonal Barrel Capsule');
  const [biomarker, setBiomarker] = useState('Nucleolin / AS1411');
  const [cargoDia, setCargoDia] = useState(8.5);
  const [designing, setDesigning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDesign = async () => {
    setDesigning(true);
    try {
      const res = await fetch('/api/v1/dna-origami/design', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nanorobot_name: robotName,
          geometry_type: geometry,
          target_biomarker: biomarker,
          target_cargo_diameter_nm: cargoDia,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDesigning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Cpu className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              3D DNA Origami Nanorobot Design Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 149: M13mp18 Scaffold Routing, Staple Crossover Assembly & Aptamer Latch Triggering Engine
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-cyan-400" />
              <span>Nanorobot Architecture</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nanorobot Designation</label>
                <input
                  type="text"
                  value={robotName}
                  onChange={(e) => setRobotName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Capsule 3D Geometry</label>
                <input
                  type="text"
                  value={geometry}
                  onChange={(e) => setGeometry(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Receptor / Biomarker</label>
                <input
                  type="text"
                  value={biomarker}
                  onChange={(e) => setBiomarker(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Cargo Cavity Target Diameter (nm)</label>
                <input
                  type="number"
                  value={cargoDia}
                  onChange={(e) => setCargoDia(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                onClick={handleDesign}
                disabled={designing}
                className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-cyan-500/20 disabled:opacity-50"
              >
                {designing ? 'Synthesizing Crossover Map...' : 'Generate 3D DNA Nanorobot'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-cyan-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-cyan-400">Origami Thermodynamics & Payload Capacity</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Folding Yield</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.folding_yield_percent}%</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Melting Point (Tm)</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.predicted_melting_temp_c}°C</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Cavity Volume</p>
                      <p className="text-lg font-bold text-white mt-1">{result.cargo_cavity_volume_nm3} nm³</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Staple Strands</p>
                      <p className="text-lg font-bold text-white mt-1">{result.staple_strands_count}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Sample Staple Strand Crossovers</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Strand Index</th>
                          <th className="px-4 py-3">Sequence (5' → 3')</th>
                          <th className="px-4 py-3">Length</th>
                          <th className="px-4 py-3">Tm (°C)</th>
                          <th className="px-4 py-3">Crossovers</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.staple_strands.map((s: any) => (
                          <tr key={s.strand_index} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-cyan-400">#{s.strand_index}</td>
                            <td className="px-4 py-3.5 font-mono text-xs text-slate-300">{s.sequence_5to3}</td>
                            <td className="px-4 py-3.5 text-slate-400">{s.length_nt} nt</td>
                            <td className="px-4 py-3.5 text-slate-200">{s.tm_celsius}°C</td>
                            <td className="px-4 py-3.5 text-emerald-400">{s.crossover_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Specify nanorobot dimensions and triggering biomarker to compute full staple routes.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DNAOrigamiStudioPage;
