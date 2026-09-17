import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Sparkles, 
  Layers, 
  Play, 
  CheckCircle2, 
  Thermometer,
  Boxes,
  Zap,
  TestTubes,
  Clock
} from 'lucide-react';

interface HydrophobicPatchItem {
  patch_identifier: string;
  surface_area_angstrom2: number;
  average_hydrophobicity_score: number;
  residue_span: string;
  aggregation_risk_level: string;
}

export const BiotherapeuticStabilityStudioPage: React.FC = () => {
  const [constructName, setConstructName] = useState('Trastuzumab-Bispecific-CD3-HER2');
  const [modality, setModality] = useState('Bispecific mAb');
  const [bufferType, setBufferType] = useState('Histidine (20mM)');
  const [ph, setPh] = useState(6.0);
  const [surfactant, setSurfactant] = useState('Polysorbate 80 (0.04%)');
  const [tonicity, setTonicity] = useState('Sucrose (240mM)');
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    construct_id: string;
    sap_score: number;
    tm1: number;
    tm2: number;
    shelf_life_months: number;
    monomer_retention: number;
    patches: HydrophobicPatchItem[];
  } | null>({
    construct_id: 'BIO-STAB-2026-884',
    sap_score: 0.16,
    tm1: 72.8,
    tm2: 83.2,
    shelf_life_months: 30.2,
    monomer_retention: 97.4,
    patches: [
      { patch_identifier: 'CDR-H3 Hydrophobic Core', surface_area_angstrom2: 245.2, average_hydrophobicity_score: 2.34, residue_span: 'HC: 98-106 (W-G-G-D-G-F-Y)', aggregation_risk_level: 'MODERATE' },
      { patch_identifier: 'CH2 Lower Hinge Patch', surface_area_angstrom2: 198.5, average_hydrophobicity_score: 1.88, residue_span: 'HC: 234-239 (L-L-G-G-P)', aggregation_risk_level: 'LOW' },
      { patch_identifier: 'CH3 Dimer Interface Loop', surface_area_angstrom2: 162.0, average_hydrophobicity_score: 1.65, residue_span: 'HC: 368-372 (L-V-K-G)', aggregation_risk_level: 'LOW' },
    ]
  });

  const handleRunForecast = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        construct_id: `BIO-STAB-${Date.now().toString().slice(-6)}`,
        sap_score: 0.14,
        tm1: 73.4,
        tm2: 83.8,
        shelf_life_months: 31.5,
        monomer_retention: 98.1,
        patches: [
          { patch_identifier: 'CDR-H3 Core Patch', surface_area_angstrom2: 232.0, average_hydrophobicity_score: 2.21, residue_span: 'HC: 98-106 (W-G-G-D-G-F-Y)', aggregation_risk_level: 'MODERATE' },
          { patch_identifier: 'CH2 Loop Patch', surface_area_angstrom2: 184.0, average_hydrophobicity_score: 1.72, residue_span: 'HC: 234-239 (L-L-G-G-P)', aggregation_risk_level: 'LOW' },
        ]
      });
      setLoading(false);
    }, 500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-400">
              <Boxes className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                Biotherapeutic Stability & Spatial Aggregation Propensity Forecaster
              </h1>
              <p className="text-slate-400 text-sm mt-0.5">
                Spatial Aggregation Propensity (SAP), hydrophobic surface patch mapping, and formulation excipient stability (ADR 069).
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={handleRunForecast}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg transition-all"
        >
          <Play className="w-4 h-4 fill-current" />
          {loading ? 'Forecasting...' : 'Compute Stability'}
        </button>
      </div>

      {/* Input Parameters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Construct Identifier</label>
          <input 
            type="text" 
            value={constructName} 
            onChange={(e) => setConstructName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-amber-500"
          />
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Modality</label>
          <select 
            value={modality} 
            onChange={(e) => setModality(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-amber-500"
          >
            <option value="mAb">Monoclonal Antibody (IgG1)</option>
            <option value="Bispecific mAb">Bispecific (T-Cell Engager)</option>
            <option value="ADC">Antibody-Drug Conjugate</option>
            <option value="Fusion Protein">Fc-Fusion Protein</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Buffer & pH</label>
          <select 
            value={bufferType} 
            onChange={(e) => setBufferType(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-amber-500"
          >
            <option value="Histidine (20mM)">Histidine (pH 6.0)</option>
            <option value="Acetate (20mM)">Acetate (pH 5.2)</option>
            <option value="Citrate (20mM)">Citrate (pH 6.5)</option>
            <option value="Phosphate (20mM)">Phosphate (pH 7.2)</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Surfactant</label>
          <select 
            value={surfactant} 
            onChange={(e) => setSurfactant(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-amber-500"
          >
            <option value="Polysorbate 80 (0.04%)">Polysorbate 80 (0.04%)</option>
            <option value="Polysorbate 20 (0.02%)">Polysorbate 20 (0.02%)</option>
            <option value="Poloxamer 188 (0.1%)">Poloxamer 188 (0.1%)</option>
          </select>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-1">Tonicity / Sugar</label>
          <select 
            value={tonicity} 
            onChange={(e) => setTonicity(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-amber-500"
          >
            <option value="Sucrose (240mM)">Sucrose (240mM)</option>
            <option value="Trehalose (240mM)">Trehalose (240mM)</option>
            <option value="Arginine-HCl (100mM)">Arginine-HCl (100mM)</option>
          </select>
        </div>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Key Metric Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>SAP Aggregation Score</span>
                <Sparkles className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.sap_score.toFixed(2)}
              </div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> High Developability (SAP &lt; 0.25)
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Thermal Unfolding (Tm1 / Tm2)</span>
                <Thermometer className="w-4 h-4 text-orange-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.tm1.toFixed(1)}°C / {result.tm2.toFixed(1)}°C
              </div>
              <p className="text-xs text-slate-400 mt-1">Fab / CH3 Unfolding Points</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Monomer Retention (40°C, 4wk)</span>
                <TestTubes className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400 mt-2">
                {result.monomer_retention.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400 mt-1">SEC Monomer Stability</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
              <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase">
                <span>Estimated 4°C Shelf Life</span>
                <Clock className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2">
                {result.shelf_life_months.toFixed(0)} Months
              </div>
              <p className="text-xs text-cyan-400 mt-1">&gt; 2 Years Commercial Target</p>
            </div>
          </div>

          {/* Hydrophobic Surface Patches */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Boxes className="w-4 h-4 text-amber-400" />
                Detected Spatial Hydrophobic Surface Patches
              </h2>
              <span className="text-xs px-2.5 py-1 bg-slate-800 text-amber-300 rounded-full border border-slate-700">
                Kyte-Doolittle Window = 7
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/60 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Patch Identifier</th>
                    <th className="px-4 py-3">Residue Sequence Span</th>
                    <th className="px-4 py-3">Surface Area</th>
                    <th className="px-4 py-3">Hydrophobicity Score</th>
                    <th className="px-4 py-3">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.patches.map((p, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-medium text-white">{p.patch_identifier}</td>
                      <td className="px-4 py-3 font-mono text-xs text-amber-300 font-semibold">{p.residue_span}</td>
                      <td className="px-4 py-3">{p.surface_area_angstrom2.toFixed(1)} Å²</td>
                      <td className="px-4 py-3 font-semibold text-white">{p.average_hydrophobicity_score.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 text-xs rounded font-medium ${
                          p.aggregation_risk_level === 'HIGH' 
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {p.aggregation_risk_level}
                        </span>
                      </td>
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
export default BiotherapeuticStabilityStudioPage;
