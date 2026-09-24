import React, { useState } from 'react';
import { Eye, ShieldCheck, Zap, Sparkles, Activity } from 'lucide-react';

export const smFRETKineticsStudioPage: React.FC = () => {
  const [biomolecule, setBiomolecule] = useState('Hsp90 Molecular Chaperone Homodimer');
  const [donor, setDonor] = useState('Cy3 (Donor)');
  const [acceptor, setAcceptor] = useState('Cy5 (Acceptor)');
  const [laserMw, setLaserMw] = useState(15.0);
  const [samplingHz, setSamplingHz] = useState(100.0);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch('/api/v1/smfret-kinetics/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          biomolecule_name: biomolecule,
          donor_fluorophore: donor,
          acceptor_fluorophore: acceptor,
          laser_power_mw: laserMw,
          sampling_rate_hz: samplingHz,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
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
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-6">
          <div className="p-3 bg-sky-500/10 text-sky-400 rounded-xl border border-sky-500/20">
            <Eye className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Single-Molecule FRET (smFRET) Conformational Kinetics Studio
            </h1>
            <p className="text-sm text-slate-400">
              Phase 160: Hidden Markov Model (HMM) Dwell-Time Trajectories, Förster R0 Dynamics & Real-Time Transition Rates
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
            <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-sky-400" />
              <span>smFRET Instrument Setup</span>
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Biomolecule</label>
                <input
                  type="text"
                  value={biomolecule}
                  onChange={(e) => setBiomolecule(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Donor Dye</label>
                  <input
                    type="text"
                    value={donor}
                    onChange={(e) => setDonor(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Acceptor Dye</label>
                  <input
                    type="text"
                    value={acceptor}
                    onChange={(e) => setAcceptor(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Laser Power (mW)</label>
                  <input
                    type="number"
                    value={laserMw}
                    onChange={(e) => setLaserMw(parseFloat(e.target.value) || 15.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Sampling (Hz)</label>
                  <input
                    type="number"
                    value={samplingHz}
                    onChange={(e) => setSamplingHz(parseFloat(e.target.value) || 100.0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full py-3 bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-medium rounded-xl text-sm transition shadow-lg shadow-sky-500/20 disabled:opacity-50"
              >
                {analyzing ? 'Decoding HMM Trajectories...' : 'Analyze smFRET Kinetics'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <div className="space-y-6">
                <div className="bg-slate-900/60 border border-sky-500/30 rounded-2xl p-6 space-y-4">
                  <h3 className="text-base font-semibold text-sky-400">Conformational Dynamics & Kinetics</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Mean Efficiency (E)</p>
                      <p className="text-lg font-bold text-white mt-1">{result.mean_fret_efficiency}</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">Förster Distance</p>
                      <p className="text-lg font-bold text-sky-400 mt-1">{result.forster_distance_r0_nm} nm</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">k_open Rate</p>
                      <p className="text-lg font-bold text-emerald-400 mt-1">{result.transition_rate_k_open_s} s⁻¹</p>
                    </div>
                    <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
                      <p className="text-xs text-slate-400">k_close Rate</p>
                      <p className="text-lg font-bold text-cyan-400 mt-1">{result.transition_rate_k_close_s} s⁻¹</p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
                  <h3 className="text-base font-semibold text-white mb-4">Hidden Markov Model (HMM) FRET States</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3">Conformational State</th>
                          <th className="px-4 py-3">FRET Peak (E)</th>
                          <th className="px-4 py-3">Dwell Time</th>
                          <th className="px-4 py-3">Occupancy</th>
                          <th className="px-4 py-3">Apparent Distance</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        {result.conformational_states.map((s: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition">
                            <td className="px-4 py-3.5 font-medium text-slate-200">{s.state_label}</td>
                            <td className="px-4 py-3.5 font-bold text-sky-400">{s.fret_efficiency_peak}</td>
                            <td className="px-4 py-3.5 text-slate-300">{s.mean_dwell_time_ms} ms</td>
                            <td className="px-4 py-3.5 text-emerald-400">{s.state_occupancy_percentage}%</td>
                            <td className="px-4 py-3.5 text-slate-400">{s.apparent_distance_angstrom} Å</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500">
                Configure fluorophore parameters and run single-molecule FRET state decoding.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default smFRETKineticsStudioPage;
