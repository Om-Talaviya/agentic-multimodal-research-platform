import React, { useState } from 'react';

interface OrganCompartment {
  organ_name: string;
  organ_volume_l_kg: number;
  blood_flow_rate_l_h_kg: number;
  tissue_plasma_partition_coefficient: number;
  permeability_surface_area_product: number;
  computed_cmax_ug_ml: number;
  computed_auc_ug_h_ml: number;
  computed_tmax_h: number;
}

interface ClearanceRate {
  elimination_pathway: string;
  organ_source: string;
  clearance_rate_ml_min: number;
  extraction_ratio: number;
  fraction_metabolized: number;
}

interface PBPKStudy {
  id: string;
  study_name: string;
  drug_candidate_name: string;
  molecular_weight_da: number;
  logp: number;
  plasma_protein_unbound_fraction: number;
  intrinsic_clearance_ml_min_kg: number;
  species: string;
  administration_route: string;
  dose_mg_kg: number;
  simulation_time_hours: number;
  summary_metrics: Record<string, any>;
  organ_compartments: OrganCompartment[];
  clearance_rates: ClearanceRate[];
}

export const WholeBodyPBPKStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('First-In-Human PBPK Profiling');
  const [drugCandidate, setDrugCandidate] = useState('MOL-7824-PBPK');
  const [mw, setMw] = useState<number>(448.5);
  const [logp, setLogp] = useState<number>(2.8);
  const [fu, setFu] = useState<number>(0.07);
  const [clInt, setClInt] = useState<number>(18.5);
  const [route, setRoute] = useState('oral');
  const [dose, setDose] = useState<number>(10.0);
  const [duration, setDuration] = useState<number>(24.0);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStudy, setCurrentStudy] = useState<PBPKStudy | null>(null);

  const handleSimulate = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/pbpk/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          drug_candidate_name: drugCandidate,
          molecular_weight_da: mw,
          logp: logp,
          plasma_protein_unbound_fraction: fu,
          intrinsic_clearance_ml_min_kg: clInt,
          species: 'human',
          administration_route: route,
          dose_mg_kg: dose,
          simulation_time_hours: duration,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentStudy(data);
      }
    } catch (err) {
      console.error('Failed to run PBPK simulation', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="pbpk-studio-page p-6 max-w-7xl mx-auto space-y-8">
      <header className="border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold text-emerald-400">
          Whole-Body PBPK Digital Twin & Trans-Organ Pharmacokinetics Studio
        </h1>
        <p className="text-gray-400 mt-2">
          Physiologically-based pharmacokinetics digital twin engine for multi-organ tissue distribution, hepatic clearance, and cross-species translation.
        </p>
      </header>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-900 p-6 rounded-xl border border-gray-800">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Physicochemical Properties</h3>
          <div>
            <label className="block text-sm text-gray-400">Study Name</label>
            <input
              type="text"
              value={studyName}
              onChange={(e) => setStudyName(e.target.value)}
              className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400">Drug Candidate Identifier</label>
            <input
              type="text"
              value={drugCandidate}
              onChange={(e) => setDrugCandidate(e.target.value)}
              className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400">MW (Da)</label>
              <input
                type="number"
                value={mw}
                onChange={(e) => setMw(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400">LogP</label>
              <input
                type="number"
                step="0.1"
                value={logp}
                onChange={(e) => setLogp(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Disposition & Clearance</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400">Fraction Unbound (fu)</label>
              <input
                type="number"
                step="0.01"
                value={fu}
                onChange={(e) => setFu(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400">CLint (mL/min/kg)</label>
              <input
                type="number"
                value={clInt}
                onChange={(e) => setClInt(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-400">Administration Route</label>
            <select
              value={route}
              onChange={(e) => setRoute(e.target.value)}
              className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
            >
              <option value="oral">Oral (PO)</option>
              <option value="iv_bolus">Intravenous Bolus (IV)</option>
              <option value="subcutaneous">Subcutaneous (SC)</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400">Dose (mg/kg)</label>
              <input
                type="number"
                value={dose}
                onChange={(e) => setDose(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400">Simulation Time (h)</label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col justify-between">
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-2">
            <h4 className="text-sm font-semibold text-emerald-300">PBPK Engine Model Specs</h4>
            <p className="text-xs text-gray-400">• Rodgers-Rowland tissue partition algorithm</p>
            <p className="text-xs text-gray-400">• 9-organ differential mass balance ODE</p>
            <p className="text-xs text-gray-400">• Hepatic CYP + Glomerular filtration clearance</p>
            <p className="text-xs text-gray-400">• Dynamic Blood-Brain Barrier (BBB) permeability</p>
          </div>
          <button
            onClick={handleSimulate}
            disabled={isLoading}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 px-4 rounded-lg transition mt-4"
          >
            {isLoading ? 'Simulating Whole-Body Kinetics...' : 'Run Whole-Body PBPK Digital Twin'}
          </button>
        </div>
      </div>

      {/* Results Overview */}
      {currentStudy && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Steady-State Vd</span>
              <p className="text-2xl font-bold text-emerald-400">
                {currentStudy.summary_metrics.steady_state_volume_of_distribution_l_kg} L/kg
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Systemic Clearance</span>
              <p className="text-2xl font-bold text-blue-400">
                {currentStudy.summary_metrics.total_systemic_clearance_ml_min} mL/min
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Terminal Half-Life</span>
              <p className="text-2xl font-bold text-yellow-400">
                {currentStudy.summary_metrics.elimination_half_life_hours} h
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Plasma Cmax / AUCinf</span>
              <p className="text-2xl font-bold text-purple-400">
                {currentStudy.summary_metrics.plasma_cmax_ug_ml} µg/mL
              </p>
            </div>
          </div>

          {/* Organ Compartments Breakdown */}
          <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Trans-Organ Tissue Distribution</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-300">
                <thead className="bg-gray-800 text-gray-400 uppercase text-xs">
                  <tr>
                    <th className="p-3">Organ</th>
                    <th className="p-3">Volume (L/kg)</th>
                    <th className="p-3">Flow (L/h/kg)</th>
                    <th className="p-3">Partition Kp</th>
                    <th className="p-3">Cmax (µg/mL)</th>
                    <th className="p-3">AUC (µg·h/mL)</th>
                    <th className="p-3">Tmax (h)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {currentStudy.organ_compartments.map((comp) => (
                    <tr key={comp.organ_name} className="hover:bg-gray-800/50">
                      <td className="p-3 font-semibold text-emerald-400 capitalize">{comp.organ_name.replace('_', ' ')}</td>
                      <td className="p-3">{comp.organ_volume_l_kg}</td>
                      <td className="p-3">{comp.blood_flow_rate_l_h_kg}</td>
                      <td className="p-3">{comp.tissue_plasma_partition_coefficient}</td>
                      <td className="p-3">{comp.computed_cmax_ug_ml}</td>
                      <td className="p-3">{comp.computed_auc_ug_h_ml}</td>
                      <td className="p-3">{comp.computed_tmax_h}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WholeBodyPBPKStudioPage;
