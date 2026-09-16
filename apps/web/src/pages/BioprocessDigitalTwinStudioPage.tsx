import React, { useState, useEffect } from 'react';
import { Gauge, Activity, Sparkles, Sliders, TrendingUp, Zap, Thermometer, Droplets } from 'lucide-react';

interface TelemetryPoint {
  id: string;
  time_hours: number;
  viable_cell_density_10e6_ml: number;
  cell_viability_pct: number;
  glucose_concentration_g_l: number;
  lactate_concentration_g_l: number;
  product_titer_g_l: number;
}

interface ControlAction {
  id: string;
  time_hours: number;
  feed_rate_ml_h: number;
  agitation_rpm: number;
  temperature_c: number;
  policy_action_name: string;
}

interface BioreactorRun {
  id: string;
  run_name: string;
  cell_line: string;
  bioreactor_type: string;
  working_volume_liters: number;
  final_titer_g_l: number;
  final_viability_pct: number;
  created_at: string;
  telemetry_points?: TelemetryPoint[];
  control_actions?: ControlAction[];
}

export const BioprocessDigitalTwinStudioPage: React.FC = () => {
  const [runs, setRuns] = useState<BioreactorRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<BioreactorRun | null>(null);
  const [runName, setRunName] = useState('Bioreactor-mAb-Batch-2026-09');
  const [cellLine, setCellLine] = useState('CHO-K1 (mAb Producer)');
  const [volumeL, setVolumeL] = useState(50.0);
  const [loading, setLoading] = useState(false);

  const fetchRuns = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/bioprocess/runs');
      if (res.ok) {
        const data = await res.json();
        setRuns(data);
        if (data.length > 0 && !selectedRun) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/bioprocess/runs/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedRun(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/bioprocess/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_name: runName,
          cell_line: cellLine,
          bioreactor_type: 'Fed-Batch Stirred Tank',
          working_volume_liters: Number(volumeL),
        }),
      });
      if (res.ok) {
        await fetchRuns();
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
          <div className="p-3 bg-lime-950/60 border border-lime-500/40 rounded-xl text-lime-400">
            <Gauge className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-lime-400 to-emerald-300 bg-clip-text text-transparent">
              Bioprocess Bioreactor Digital Twin
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 62 • Monod-Luedeking-Piret kinetic simulation, automated MPC nutrient feed & fed-batch titer optimization
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-lime-300">
            <Sliders className="w-5 h-5" /> Start Bioreactor Batch
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Run / Batch Name</label>
              <input
                type="text"
                value={runName}
                onChange={(e) => setRunName(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Cell Line Host</label>
              <input
                type="text"
                value={cellLine}
                onChange={(e) => setCellLine(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Working Volume (Liters)</label>
              <input
                type="number"
                value={volumeL}
                onChange={(e) => setVolumeL(parseFloat(e.target.value))}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-lime-600 to-emerald-600 hover:from-lime-500 hover:to-emerald-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Running Twin...' : 'Simulate 14-Day Fermentation'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Bioreactor Batches</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {runs.map((r) => (
                <div
                  key={r.id}
                  onClick={() => fetchDetail(r.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedRun?.id === r.id
                      ? 'bg-lime-950/40 border-lime-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{r.run_name}</span>
                    <span className="text-lime-400 font-mono font-bold">{r.final_titer_g_l} g/L Titer</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{r.cell_line} ({r.working_volume_liters}L)</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Telemetry & Yield Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-lime-300">
              <Activity className="w-5 h-5" /> Fermentation Kinetic Telemetry
            </h2>
            {selectedRun && (
              <div className="flex gap-2 text-xs">
                <span className="bg-lime-950 text-lime-300 px-2.5 py-1 rounded border border-lime-500/40 font-semibold">
                  Titer: {selectedRun.final_titer_g_l} g/L
                </span>
                <span className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700">
                  Viability: {selectedRun.final_viability_pct}%
                </span>
              </div>
            )}
          </div>

          {selectedRun?.telemetry_points && selectedRun.telemetry_points.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Time</th>
                    <th className="p-3">VCD (10⁶/mL)</th>
                    <th className="p-3">Viability</th>
                    <th className="p-3">Glucose (g/L)</th>
                    <th className="p-3">Lactate (g/L)</th>
                    <th className="p-3">Product Titer</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedRun.telemetry_points.map((pt) => (
                    <tr key={pt.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-mono font-semibold text-slate-400">Day {(pt.time_hours / 24).toFixed(0)} ({pt.time_hours}h)</td>
                      <td className="p-3 font-mono text-lime-300 font-bold">{pt.viable_cell_density_10e6_ml}</td>
                      <td className="p-3 font-mono text-emerald-400">{pt.cell_viability_pct}%</td>
                      <td className="p-3 font-mono text-amber-300">{pt.glucose_concentration_g_l} g/L</td>
                      <td className="p-3 font-mono text-rose-300">{pt.lactate_concentration_g_l} g/L</td>
                      <td className="p-3 font-mono font-bold text-lime-400">{pt.product_titer_g_l} g/L</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No batches loaded. Run a fermentation above.</div>
          )}

          {/* Autonomous MPC Control Schedule */}
          {selectedRun?.control_actions && selectedRun.control_actions.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-lime-300 uppercase tracking-wider flex items-center gap-2">
                <Zap className="w-4 h-4 text-emerald-400" /> MPC Automated Feed Actions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedRun.control_actions.map((act) => (
                  <div key={act.id} className="p-3 bg-slate-950/80 border border-lime-500/30 rounded-xl space-y-1 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-200">{act.policy_action_name}</span>
                      <span className="font-mono text-[11px] text-lime-400 font-bold">{act.feed_rate_ml_h} mL/h</span>
                    </div>
                    <div className="text-[11px] text-slate-400 flex justify-between">
                      <span>Agitation: {act.agitation_rpm} RPM</span>
                      <span>Temp: {act.temperature_c}°C</span>
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
