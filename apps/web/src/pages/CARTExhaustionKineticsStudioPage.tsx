import React, { useState } from "react";
import { Shield, Flame, Cpu, Sparkles, Activity, CheckCircle2, ShieldAlert } from "lucide-react";

export const CARTExhaustionKineticsStudioPage: React.FC = () => {
  const [constructName, setConstructName] = useState("anti-CD19-41BBz");
  const [costimDomain, setCostimDomain] = useState("4-1BB");
  const [tonicSignaling, setTonicSignaling] = useState("low");
  const [antigenDensity, setAntigenDensity] = useState(15000);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    setTimeout(() => {
      setResult({
        tscmPct: 42.5,
        toxScore: 0.18,
        halfLifeDays: 215.0,
        efficacyScore: 0.92,
        memoryFitness: 0.895,
        recommendation: `Construct ${constructName} (${costimDomain}) maintains high Tscm memory reserve (42.5%) and suppressed TOX chromatin remodeling. Long-term persistence forecast: 215 days.`,
      });
      setIsSimulating(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-red-400 to-amber-400 bg-clip-text text-transparent">
            <Shield className="w-8 h-8 text-red-400" />
            CAR-T Cell Exhaustion & Persistence Kinetics Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 183: Epigenetic Tscm stem memory preservation, TOX/NR4A exhaustion trajectory modeling, and clinical persistence predictor.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Flame className="w-5 h-5 text-red-400" /> CAR-T Engineering Inputs
          </h2>
          <div>
            <label className="text-sm text-slate-400">CAR Construct Name</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={constructName}
              onChange={(e) => setConstructName(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Costimulatory Domain</label>
            <select
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={costimDomain}
              onChange={(e) => setCostimDomain(e.target.value)}
            >
              <option value="4-1BB">4-1BB (CD137 - Oxidative/Memory)</option>
              <option value="CD28">CD28 (Glycolytic/Effector)</option>
              <option value="CD28_41BB_dual">Dual CD28 + 4-1BB Third Gen</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-slate-400">Tonic Signaling Level</label>
            <select
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={tonicSignaling}
              onChange={(e) => setTonicSignaling(e.target.value)}
            >
              <option value="low">Low (Favorable Non-Clustering)</option>
              <option value="medium">Medium (Moderate Antigen-Independent)</option>
              <option value="high">High (Clustering Driven Exhaustion)</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-slate-400">Tumor Target Antigen Density ({antigenDensity} molecules/cell)</label>
            <input
              type="range"
              min="1000"
              max="50000"
              step="1000"
              className="w-full mt-1"
              value={antigenDensity}
              onChange={(e) => setAntigenDensity(parseInt(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isSimulating}
            className="w-full bg-red-600 hover:bg-red-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isSimulating ? "Simulating Epigenetic Transitions..." : "Run Exhaustion Simulation"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Activity className="w-5 h-5 text-amber-400" /> T-Cell Memory Phenotype & TOX Status
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Tscm Stem Memory</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.tscmPct}%</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">TOX Exhaustion Score</div>
                  <div className="text-2xl font-bold text-amber-400">{result.toxScore}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">In-Vivo Persistence</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.halfLifeDays} days</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Efficacy Score</div>
                  <div className="text-2xl font-bold text-purple-400">{result.efficacyScore}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Shield className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure CAR domain structure and run persistence forecasting</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CARTExhaustionKineticsStudioPage;