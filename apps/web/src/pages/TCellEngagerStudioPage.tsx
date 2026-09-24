import React, { useState } from 'react';
import { Shield, ShieldCheck, Zap, Crosshair, Sparkles, Activity } from 'lucide-react';

export const TCellEngagerStudioPage: React.FC = () => {
  const [construct, setConstruct] = useState('EGFRvIII x HER2 x CD3e Trispecific T-Cell Engager');
  const [format, setFormat] = useState('TriTE (Trispecific T-Cell Engager)');
  const [antigen, setAntigen] = useState('EGFRvIII / HER2 Dual TAA');
  const [cd3Affinity, setCd3Affinity] = useState(12.5);
  const [modeling, setModeling] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleModel = async () => {
    setModeling(true);
    try {
      const res = await fetch('/api/v1/tcell-engager/model-geometry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          construct_name: construct,
          modality_format: format,
          primary_tumor_antigen: antigen,
          cd3_arm_affinity_nM: cd3Affinity,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setModeling(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Multi-Target Bispecific & Trispecific T-Cell Engager (BiTE/TriTE) Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 158: Immunological Synapse Geometry, CD3 Arm Optimization & Picomolar Cytolytic Pore Polarization
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-red-400" />
              <span>Engager Molecular Architecture</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Construct Designation</label>
                <input
                  type="text"
                  value={construct}
                  onChange={(e) => setConstruct(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Modality Format</label>
                <input
                  type="text"
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Dual Tumor Target Antigens</label>
                <input
                  type="text"
                  value={antigen}
                  onChange={(e) => setAntigen(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Anti-CD3 Arm Kd (nM)</label>
                <input
                  type="number"
                  value={cd3Affinity}
                  onChange={(e) => setCd3Affinity(parseFloat(e.target.value) || 10.0)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-red-500"
                />
              </div>

              <button
                onClick={handleModel}
                disabled={modeling}
                className="w-full py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-red-500/20 disabled:opacity-50"
              >
                {modeling ? 'Simulating Synapse Cleft...' : 'Model Immunological Synapse'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-red-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-red-400">Synapse Potency & CRS Safety</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Cytolytic EC50</p>
                      <p className="text-lg font-bold text-white mt-1">{result.cytolytic_potency_ec50_pm} pM</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Synaptic Distance</p>
                      <p className="text-lg font-bold text-red-400 mt-1">{result.synaptic_cleft_distance_a} Å</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">CRS Risk Index</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.crs_cytokine_risk_score} (Low)</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Lytic Polarization</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.perforin_granzyme_flux} AU/s</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Engineered Binding Arm Geometry</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Arm</th>
                          <th className="px-4 py-3">Target Epitope</th>
                          <th className="px-4 py-3">Kd (nM)</th>
                          <th className="px-4 py-3">Length (Å)</th>
                          <th className="px-4 py-3">Flexibility</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.binding_domains.map((b: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-bold text-red-400">{b.arm_designation}</td>
                            <td className="px-4 py-3.5 text-slate-300">{b.target_epitope}</td>
                            <td className="px-4 py-3.5 text-emerald-400 font-bold">{b.kd_affinity_nM} nM</td>
                            <td className="px-4 py-3.5 text-slate-400">{b.arm_length_angstrom} Å</td>
                            <td className="px-4 py-3.5 text-cyan-400">{b.rotational_flexibility_deg}°</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure trispecific engager parameters to calculate intermembrane synapse geometry.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TCellEngagerStudioPage;
