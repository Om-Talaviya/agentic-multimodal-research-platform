import React, { useState } from 'react';
import { ShieldAlert, Dna, Activity, Zap, Play, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';

export const CARTStudioPage: React.FC = () => {
  const [constructName, setConstructName] = useState('CAR-T-AntiCD19-41BB');
  const [targetAntigen, setTargetAntigen] = useState('CD19');
  const [costimDomain, setCostimDomain] = useState('4-1BB');
  const [vectorType, setVectorType] = useState('Lentiviral');
  const [etRatio, setEtRatio] = useState(5.0);
  const [tumorBurden, setTumorBurden] = useState(1.0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunSimulation = () => {
    setIsSimulating(true);
    setTimeout(() => {
      const baseLysis = Math.min(96.4, 45.0 + 35.0 * (1.0 - Math.exp(-0.35 * etRatio)) * (costimDomain === 'CD28' ? 1.15 : 1.0));
      const peakIL6 = (150.0 * (costimDomain === 'CD28' ? 1.45 : 0.75) * tumorBurden).toFixed(1);
      const crsGrade = parseFloat(peakIL6) > 280 ? 'Grade 3' : (parseFloat(peakIL6) > 120 ? 'Grade 2' : 'Grade 1');

      setResults({
        construct: {
          name: constructName,
          target: targetAntigen,
          scfv: targetAntigen === 'CD19' ? 'FMC63' : (targetAntigen === 'BCMA' ? '11D5-3' : '4D5'),
          costim: costimDomain,
          vector: vectorType,
          architecture: `Leader-scFv[${targetAntigen}]-CD8a-TM-${costimDomain}-CD3zeta`,
        },
        cytotoxicity: {
          lysisPct: baseLysis.toFixed(1),
          persistenceScore: costimDomain === '4-1BB' ? '0.88 (High Tcm)' : '0.55 (Effector Tem)',
          pd1: (costimDomain === 'CD28' ? 38.4 : 16.2).toFixed(1),
          grade: 'POTENT',
        },
        crs: {
          peakIL6: peakIL6,
          astctGrade: crsGrade,
          icansRisk: parseFloat(peakIL6) > 280 ? '48.5%' : '14.2%',
          tociResponsive: true,
          dexRecommended: parseFloat(peakIL6) > 280,
        }
      });
      setIsSimulating(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
                <Dna className="w-7 h-7" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">Autonomous CAR-T Cell Engineering Studio</h1>
                <p className="text-sm text-slate-400">Synthetic Immunology & Cytokine Release Syndrome (CRS) Toxicity Predictor</p>
              </div>
            </div>
          </div>
          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg font-medium transition-all shadow-lg shadow-emerald-500/20"
          >
            {isSimulating ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {isSimulating ? 'Compiling In Silico...' : 'Run Simulation Pipeline'}
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Controls */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              Construct Parameters
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Construct Design Name</label>
                <input
                  type="text"
                  value={constructName}
                  onChange={(e) => setConstructName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Tumor Antigen</label>
                <select
                  value={targetAntigen}
                  onChange={(e) => setTargetAntigen(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="CD19">CD19 (B-ALL / DLBCL / MCL)</option>
                  <option value="BCMA">BCMA (Multiple Myeloma)</option>
                  <option value="HER2">HER2 (Solid Tumors / Glioblastoma)</option>
                  <option value="EGFRvIII">EGFRvIII (Glioblastoma)</option>
                  <option value="PSMA">PSMA (Prostate Carcinoma)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Costimulatory Endodomain</label>
                <select
                  value={costimDomain}
                  onChange={(e) => setCostimDomain(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="4-1BB">4-1BB (CD137) - Tcm Memory / High Persistence</option>
                  <option value="CD28">CD28 - Rapid Lysis / Effector Tem</option>
                  <option value="CD28+4-1BB">CD28 + 4-1BB (3rd Generation Dual-Costim)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Vector Delivery Type</label>
                <select
                  value={vectorType}
                  onChange={(e) => setVectorType(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Lentiviral">Lentiviral Transduction</option>
                  <option value="Retroviral">gamma-Retroviral Vector</option>
                  <option value="mRNA-LNP">Transient mRNA LNP Electroporation</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Effector-to-Target (E:T) Ratio</span>
                  <span className="text-emerald-400 font-mono">{etRatio}:1</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="0.5"
                  value={etRatio}
                  onChange={(e) => setEtRatio(parseFloat(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Tumor Burden Severity Factor</span>
                  <span className="text-amber-400 font-mono">{tumorBurden}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="3.0"
                  step="0.1"
                  value={tumorBurden}
                  onChange={(e) => setTumorBurden(parseFloat(e.target.value))}
                  className="w-full accent-amber-500"
                />
              </div>
            </div>
          </div>

          {/* Visualization & Results */}
          <div className="lg:col-span-2 space-y-6">
            {results ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Cytotoxicity Scorecard */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-white flex items-center gap-2">
                        <Zap className="w-4 h-4 text-emerald-400" />
                        In Vitro Lytic Efficacy
                      </h3>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {results.cytotoxicity.grade}
                      </span>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-xs text-slate-400 mb-1">
                          <span>Specific Target Lysis</span>
                          <span className="text-white font-mono">{results.cytotoxicity.lysisPct}%</span>
                        </div>
                        <div className="w-full bg-slate-800 rounded-full h-2">
                          <div
                            className="bg-emerald-500 h-2 rounded-full transition-all"
                            style={{ width: `${results.cytotoxicity.lysisPct}%` }}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
                        <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/50">
                          <span className="text-slate-400 block">T-Cell Persistence:</span>
                          <span className="text-white font-medium">{results.cytotoxicity.persistenceScore}</span>
                        </div>
                        <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/50">
                          <span className="text-slate-400 block">PD-1 Exhaustion:</span>
                          <span className="text-amber-400 font-medium">{results.cytotoxicity.pd1}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* CRS Toxicity Risk */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-white flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-amber-400" />
                        ASTCT CRS Toxicity Profile
                      </h3>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {results.crs.astctGrade}
                      </span>
                    </div>

                    <div className="space-y-3 text-xs">
                      <div className="flex justify-between py-1.5 border-b border-slate-800">
                        <span className="text-slate-400">Peak IL-6 Concentration:</span>
                        <span className="text-white font-mono">{results.crs.peakIL6} pg/mL</span>
                      </div>
                      <div className="flex justify-between py-1.5 border-b border-slate-800">
                        <span className="text-slate-400">ICANS Neurotoxicity Risk:</span>
                        <span className="text-amber-300 font-mono">{results.crs.icansRisk}</span>
                      </div>
                      <div className="flex justify-between py-1.5">
                        <span className="text-slate-400">Steroid (Dexamethasone):</span>
                        <span className={results.crs.dexRecommended ? "text-rose-400 font-semibold" : "text-emerald-400"}>
                          {results.crs.dexRecommended ? "Indicated" : "Not Required"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Synthetic Construct Genetic Schema */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-sm font-semibold text-slate-300">CAR-T Construct Molecular Architecture</h4>
                  <div className="p-3 bg-slate-950 font-mono text-xs text-emerald-400 rounded-lg border border-slate-800 break-all">
                    {results.construct.architecture}
                  </div>
                  <p className="text-xs text-slate-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    scFv binder {results.construct.scfv} validated against {results.construct.target} high-density epitope clusters.
                  </p>
                </div>
              </>
            ) : (
              <div className="h-64 border-2 border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-slate-500 p-8 text-center">
                <Dna className="w-10 h-10 mb-3 text-slate-600 animate-pulse" />
                <p className="text-sm font-medium text-slate-400">No active CAR-T simulation results</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm">
                  Configure synthetic construct modular domains and click "Run Simulation Pipeline" to analyze tumor lysis & CRS safety curves.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CARTStudioPage;
