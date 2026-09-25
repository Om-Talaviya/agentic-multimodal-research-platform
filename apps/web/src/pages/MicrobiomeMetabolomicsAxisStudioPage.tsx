import React, { useState } from "react";
import { Trees, Activity, Cpu, Sparkles, PieChart, CheckCircle2, ShieldCheck } from "lucide-react";

export const MicrobiomeMetabolomicsAxisStudioPage: React.FC = () => {
  const [sampleId, setSampleId] = useState("SMP-MB-9012");
  const [fiberIntake, setFiberIntake] = useState(32);
  const [prebioticGrams, setPrebioticGrams] = useState(5);
  const [abxDays, setAbxDays] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    setTimeout(() => {
      setResult({
        totalSCFA: 96.4,
        butyrateConc: 55.9,
        barrierIntegrity: 0.93,
        shannonDiversity: 3.88,
        homeostasisIndex: 0.912,
        recommendation: `Optimal high-fiber co-metabolism profile for ${sampleId}. High lumen Butyrate (55.9 mM) promotes colonic mucosal barrier repair and GPR41/43 signaling.`,
      });
      setIsSimulating(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-emerald-400 to-lime-400 bg-clip-text text-transparent">
            <Trees className="w-8 h-8 text-emerald-400" />
            Gut Microbiome-Host Co-Metabolism & SCFA Dynamics Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 182: Microbiome taxonomic community structure, dietary fiber fermentation, and short-chain fatty acid flux simulator.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Activity className="w-5 h-5 text-emerald-400" /> Host Diet & Exposure Inputs
          </h2>
          <div>
            <label className="text-sm text-slate-400">Sample Cohort ID</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={sampleId}
              onChange={(e) => setSampleId(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Dietary Fiber ({fiberIntake} g/day)</label>
            <input
              type="range"
              min="10"
              max="60"
              step="2"
              className="w-full mt-1"
              value={fiberIntake}
              onChange={(e) => setFiberIntake(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Prebiotic Inulin Supplement ({prebioticGrams} g)</label>
            <input
              type="range"
              min="0"
              max="20"
              step="1"
              className="w-full mt-1"
              value={prebioticGrams}
              onChange={(e) => setPrebioticGrams(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Recent Antibiotic Exposure ({abxDays} days)</label>
            <input
              type="range"
              min="0"
              max="14"
              step="1"
              className="w-full mt-1"
              value={abxDays}
              onChange={(e) => setAbxDays(parseInt(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isSimulating}
            className="w-full bg-emerald-600 hover:bg-emerald-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isSimulating ? "Modeling Microbial Fermentation..." : "Simulate SCFA Metabolic Flux"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <PieChart className="w-5 h-5 text-lime-400" /> Metabolomic Flux & Mucosal Barrier Index
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Total SCFA Production</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.totalSCFA} mM</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Lumen Butyrate</div>
                  <div className="text-2xl font-bold text-lime-400">{result.butyrateConc} mM</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Barrier Integrity Score</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.barrierIntegrity}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Shannon Diversity</div>
                  <div className="text-2xl font-bold text-purple-400">{result.shannonDiversity}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Trees className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure dietary fiber and probiotic inputs to forecast SCFA flux</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MicrobiomeMetabolomicsAxisStudioPage;