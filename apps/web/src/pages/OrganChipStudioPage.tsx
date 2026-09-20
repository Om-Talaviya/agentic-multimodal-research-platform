import React, { useState, useEffect } from 'react';
import { Cpu, Wind, Activity, Layers, ShieldCheck, Plus, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface MicroChannel {
  channel_name: string;
  width_um: number;
  height_um: number;
  length_mm: number;
  flow_velocity_mm_s: number;
  reynolds_number: number;
}

interface ShearProfile {
  axial_position_mm: number;
  wall_shear_stress: number;
  drug_permeation_pct: number;
  tight_junction_expression: number;
}

interface OrganChipSimulation {
  id: string;
  chip_name: string;
  organ_type: string;
  fluid_viscosity_cp: number;
  perfusion_flow_rate_ul_min: number;
  shear_stress_dyn_cm2: number;
  endothelial_barrier_integrity_teer: number;
  status: string;
  channels?: MicroChannel[];
  shear_profiles?: ShearProfile[];
}

export const OrganChipStudioPage: React.FC = () => {
  const [simulations, setSimulations] = useState<OrganChipSimulation[]>([]);
  const [selectedSim, setSelectedSim] = useState<OrganChipSimulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [chipName, setChipName] = useState('BBB-Microfluidic-Vascular-CoCulture');
  const [organType, setOrganType] = useState('BLOOD_BRAIN_BARRIER');

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/organ-chip/simulations');
      setSimulations(res.data);
      if (res.data.length > 0) {
        fetchSimulationDetail(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load organ-chip simulations', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSimulationDetail = async (id: string) => {
    try {
      const res = await axios.get(`/api/v1/organ-chip/simulations/${id}`);
      setSelectedSim(res.data);
    } catch (err) {
      console.error('Failed to fetch simulation details', err);
    }
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const payload = {
        chip_name: chipName,
        organ_type: organType,
        flow_rate_ul_min: 35.0,
        viscosity_cp: 1.0,
        channel_length_mm: 20.0
      };
      const res = await axios.post('/api/v1/organ-chip/simulate', payload);
      setSimulations([res.data, ...simulations]);
      setSelectedSim(res.data);
    } catch (err) {
      console.error('Failed to run organ chip simulation', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-500/10 border border-teal-500/20 rounded-lg text-teal-400">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Autonomous Organ-on-a-Chip Microphysiological Studio</h1>
              <p className="text-sm text-slate-400">
                Phase 108 • Navier-Stokes Laminar Flow, Wall Shear Stress (dyn/cm²), TEER Barrier & Drug Permeation
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white font-medium rounded-lg transition disabled:opacity-50"
          >
            {isSimulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Simulate Microfluidic Perfusion
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      {selectedSim && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Wall Shear Stress (τ)</div>
            <div className="text-2xl font-bold text-teal-400 mt-1">{selectedSim.shear_stress_dyn_cm2} dyn/cm²</div>
            <div className="text-xs text-slate-500 mt-1">Laminar Endothelial Perfusion</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Barrier Integrity (TEER)</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{selectedSim.endothelial_barrier_integrity_teer} Ω·cm²</div>
            <div className="text-xs text-slate-500 mt-1">Tight Junction Maturation</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Perfusion Flow Rate</div>
            <div className="text-2xl font-bold text-white mt-1">{selectedSim.perfusion_flow_rate_ul_min} µL/min</div>
            <div className="text-xs text-slate-500 mt-1">Viscosity: {selectedSim.fluid_viscosity_cp} cP</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-xs font-semibold text-slate-400 uppercase">Organ Microenvironment</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{selectedSim.organ_type}</div>
            <div className="text-xs text-slate-500 mt-1">Dual-Chamber Co-Culture Biochip</div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Biochips Catalog */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-teal-400" />
            Organ Biochips
          </h2>
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading simulations...</div>
          ) : simulations.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No simulations found. Run perfusion above.</div>
          ) : (
            <div className="space-y-3">
              {simulations.map((s) => (
                <div
                  key={s.id}
                  onClick={() => fetchSimulationDetail(s.id)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition ${
                    selectedSim?.id === s.id
                      ? 'bg-teal-950/40 border-teal-500/60'
                      : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-semibold text-white text-sm truncate">{s.chip_name}</div>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-teal-300 font-mono">
                      {s.organ_type}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>{s.shear_stress_dyn_cm2} dyn/cm²</span>
                    <span>TEER: {s.endothelial_barrier_integrity_teer} Ω·cm²</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Microfluidic Channels & Shear Profiles */}
        <div className="lg:col-span-2 space-y-6">
          {selectedSim ? (
            <>
              {/* Dual Channels Cards */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Wind className="w-5 h-5 text-teal-400" />
                  Dual-Chamber Microfluidic Channels
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedSim.channels && selectedSim.channels.length > 0 ? (
                    selectedSim.channels.map((ch, idx) => (
                      <div key={idx} className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-teal-300 text-sm">{ch.channel_name}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                            Re: {ch.reynolds_number}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                          <div>
                            <span className="text-slate-500">Cross-Section:</span> {ch.width_um} × {ch.height_um} µm
                          </div>
                          <div>
                            <span className="text-slate-500">Length:</span> {ch.length_mm} mm
                          </div>
                          <div>
                            <span className="text-slate-500">Mean Velocity:</span> {ch.flow_velocity_mm_s} mm/s
                          </div>
                          <div>
                            <span className="text-slate-500">Flow Regime:</span> Laminar (Re &lt; 1)
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-slate-500 col-span-2 text-center py-4">No channels configured.</div>
                  )}
                </div>
              </div>

              {/* Axial Shear Stress & Permeation Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-teal-400" />
                  Axial Shear Stress & Barrier Permeability Profile
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/80 text-xs uppercase text-slate-400 font-semibold">
                      <tr>
                        <th className="py-2.5 px-3">Axial Position (mm)</th>
                        <th className="py-2.5 px-3">Wall Shear Stress</th>
                        <th className="py-2.5 px-3">Drug Permeation %</th>
                        <th className="py-2.5 px-3">Tight Junction Expression</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {selectedSim.shear_profiles && selectedSim.shear_profiles.length > 0 ? (
                        selectedSim.shear_profiles.map((p, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-mono text-teal-300">{p.axial_position_mm} mm</td>
                            <td className="py-2.5 px-3 font-mono">{p.wall_shear_stress} dyn/cm²</td>
                            <td className="py-2.5 px-3 font-mono text-indigo-400 font-semibold">{p.drug_permeation_pct}%</td>
                            <td className="py-2.5 px-3 font-mono text-emerald-400 font-bold">{p.tight_junction_expression}%</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="py-4 text-center text-slate-500">
                            No profiles calculated.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
              Select or simulate an organ biochip to inspect microfluidic laminar flow dynamics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
