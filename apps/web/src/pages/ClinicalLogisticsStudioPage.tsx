import React, { useState, useEffect } from 'react';
import { Truck, Activity, Sparkles, Globe, ShieldAlert, CheckCircle, Package, Clock } from 'lucide-react';

interface SiteNode {
  id: string;
  site_name: string;
  country_code: string;
  active_enrolled_patients: number;
  current_inventory_vials: number;
  inventory_runway_days: number;
  cold_chain_compliance_pct: number;
  stockout_risk_score: number;
}

interface SupplyRoute {
  id: string;
  origin_depot: string;
  destination_site: string;
  transport_mode: string;
  transit_time_hours: number;
  temperature_excursion_risk_pct: number;
  customs_clearance_delay_risk_pct: number;
  contingency_action: string;
}

interface TrialNetwork {
  id: string;
  trial_protocol_number: string;
  trial_title: string;
  phase: string;
  product_storage_regime: string;
  total_sites: number;
  global_supply_risk_index: number;
  created_at: string;
  sites?: SiteNode[];
  routes?: SupplyRoute[];
}

export const ClinicalLogisticsStudioPage: React.FC = () => {
  const [trials, setTrials] = useState<TrialNetwork[]>([]);
  const [selectedTrial, setSelectedTrial] = useState<TrialNetwork | null>(null);
  const [protocolNo, setProtocolNo] = useState('PROTO-IMM-2026-03');
  const [trialTitle, setTrialTitle] = useState('Global Phase III mRNA Neoantigen Combination Trial');
  const [storageRegime, setStorageRegime] = useState('Ultra-Cold Chain (-80°C)');
  const [loading, setLoading] = useState(false);

  const fetchTrials = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/clinical-logistics/trials');
      if (res.ok) {
        const data = await res.json();
        setTrials(data);
        if (data.length > 0 && !selectedTrial) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/clinical-logistics/trials/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedTrial(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchTrials();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/clinical-logistics/trials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trial_protocol_number: protocolNo,
          trial_title: trialTitle,
          phase: 'Phase III',
          product_storage_regime: storageRegime,
        }),
      });
      if (res.ok) {
        await fetchTrials();
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
          <div className="p-3 bg-blue-950/60 border border-blue-500/40 rounded-xl text-blue-400">
            <Globe className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-sky-300 bg-clip-text text-transparent">
              Clinical Trial Logistics & Cold-Chain Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 63 • Global multi-site clinical supply forecasting, temperature excursion risk modeling & stockout prevention
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-blue-300">
            <Truck className="w-5 h-5" /> Launch Trial Network
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Protocol Number</label>
              <input
                type="text"
                value={protocolNo}
                onChange={(e) => setProtocolNo(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Trial Title</label>
              <input
                type="text"
                value={trialTitle}
                onChange={(e) => setTrialTitle(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Storage Regime</label>
              <input
                type="text"
                value={storageRegime}
                onChange={(e) => setStorageRegime(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Simulating Routes...' : 'Simulate Logistics Network'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Active Trial Networks</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {trials.map((t) => (
                <div
                  key={t.id}
                  onClick={() => fetchDetail(t.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedTrial?.id === t.id
                      ? 'bg-blue-950/40 border-blue-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{t.trial_protocol_number}</span>
                    <span className="text-blue-400 font-mono">{t.total_sites} Sites</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{t.trial_title}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sites & Routes Table */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-blue-300">
              <Activity className="w-5 h-5" /> Investigative Site Inventory & Compliance
            </h2>
            {selectedTrial && (
              <span className="text-xs bg-blue-950 text-blue-300 px-2.5 py-1 rounded border border-blue-500/40 font-semibold">
                Network Risk: {(selectedTrial.global_supply_risk_index * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {selectedTrial?.sites && selectedTrial.sites.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Hospital Site</th>
                    <th className="p-3">Country</th>
                    <th className="p-3">Enrolled Patients</th>
                    <th className="p-3">Inventory Vials</th>
                    <th className="p-3">Runway (Days)</th>
                    <th className="p-3">Cold Compliance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedTrial.sites.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-semibold text-slate-200">{s.site_name}</td>
                      <td className="p-3 font-mono text-blue-400">{s.country_code}</td>
                      <td className="p-3 font-mono text-slate-300">{s.active_enrolled_patients} pts</td>
                      <td className="p-3 font-mono font-bold text-sky-300">{s.current_inventory_vials}</td>
                      <td className="p-3 font-mono font-bold text-emerald-400">{s.inventory_runway_days}d</td>
                      <td className="p-3 font-mono text-slate-200">{s.cold_chain_compliance_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No trial network loaded. Run a simulation above.</div>
          )}

          {/* Supply Shipping Lanes */}
          {selectedTrial?.routes && selectedTrial.routes.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-blue-300 uppercase tracking-wider flex items-center gap-2">
                <Package className="w-4 h-4 text-sky-400" /> Cold-Chain Transit Lanes & Risk
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedTrial.routes.map((r) => (
                  <div key={r.id} className="p-3 bg-slate-950/80 border border-blue-500/30 rounded-xl space-y-1.5 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-200">{r.destination_site}</span>
                      <span className="text-[10px] font-mono bg-blue-950 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30">
                        {r.transit_time_hours}h Transit
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 flex justify-between">
                      <span>Excursion Risk: {r.temperature_excursion_risk_pct}%</span>
                      <span>Customs Risk: {r.customs_clearance_delay_risk_pct}%</span>
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
