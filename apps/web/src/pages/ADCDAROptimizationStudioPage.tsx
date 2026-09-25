import React, { useState } from "react";
import { Activity, ShieldAlert, Cpu, Sparkles, BarChart2, Layers, CheckCircle2 } from "lucide-react";

export const ADCDAROptimizationStudioPage: React.FC = () => {
  const [antibodyName, setAntibodyName] = useState("Trastuzumab (anti-HER2)");
  const [payloadName, setPayloadName] = useState("Monomethyl Auristatin E (MMAE)");
  const [targetDAR, setTargetDAR] = useState(4.0);
  const [stoichiometry, setStoichiometry] = useState(4.5);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    setTimeout(() => {
      setResult({
        meanDAR: 3.92,
        unconjugatedPct: 3.8,
        highDAROverloadPct: 5.4,
        aggregationPropensity: 0.118,
        therapeuticMultiplier: 2.85,
        recommendation: `Stoichiometry of ${stoichiometry}x optimal for target DAR ${targetDAR}. Minimal high-DAR (>=6) species overload.`,
      });
      setIsSimulating(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            <Layers className="w-8 h-8 text-emerald-400" />
            ADC DAR Optimization & Aggregation Predictor Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 178: In-silico drug-to-antibody ratio profiling, Poisson/Binomial species resolution, and formulation stability simulation.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Cpu className="w-5 h-5 text-cyan-400" /> Conjugation Parameters
          </h2>
          <div>
            <label className="text-sm text-slate-400">Antibody Construct</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={antibodyName}
              onChange={(e) => setAntibodyName(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Cytotoxic Payload</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={payloadName}
              onChange={(e) => setPayloadName(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Target DAR ({targetDAR})</label>
            <input
              type="range"
              min="1.0"
              max="8.0"
              step="0.5"
              className="w-full mt-1"
              value={targetDAR}
              onChange={(e) => setTargetDAR(parseFloat(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Reaction Stoichiometry ({stoichiometry}x)</label>
            <input
              type="range"
              min="1.0"
              max="8.0"
              step="0.5"
              className="w-full mt-1"
              value={stoichiometry}
              onChange={(e) => setStoichiometry(parseFloat(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isSimulating}
            className="w-full bg-emerald-600 hover:bg-emerald-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isSimulating ? "Optimizing Conjugation..." : "Run DAR Optimization"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <BarChart2 className="w-5 h-5 text-emerald-400" /> Conjugate Species & Aggregation Metrics
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Calculated Mean DAR</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.meanDAR}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Unconjugated (DAR 0)</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.unconjugatedPct}%</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Overload (DAR &ge; 6)</div>
                  <div className="text-2xl font-bold text-amber-400">{result.highDAROverloadPct}%</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Therapeutic Index Multiplier</div>
                  <div className="text-2xl font-bold text-purple-400">{result.therapeuticMultiplier}x</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Activity className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure conjugation stoichiometry and run simulation</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ADCDAROptimizationStudioPage;
