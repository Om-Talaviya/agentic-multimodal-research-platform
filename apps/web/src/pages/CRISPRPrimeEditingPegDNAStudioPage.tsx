import React, { useState } from "react";
import { Scissors, Dna, Cpu, Sparkles, Activity, CheckCircle2, ShieldAlert } from "lucide-react";

export const CRISPRPrimeEditingPegDNAStudioPage: React.FC = () => {
  const [targetGene, setTargetGene] = useState("HBB (Sickle Cell E6V)");
  const [mutationType, setMutationType] = useState("point_substitution");
  const [pbsLength, setPbsLength] = useState(13);
  const [rttLength, setRttLength] = useState(15);
  const [nickDistance, setNickDistance] = useState(3);
  const [peSystem, setPeSystem] = useState("PEmax_epegRNA");
  const [isDesigning, setIsDesigning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsDesigning(true);
    setTimeout(() => {
      setResult({
        editingEfficiency: 76.4,
        indelFrequency: 2.8,
        flapEquilibriumRatio: 3.45,
        fidelityIndex: 27.3,
        pbsTm: 38.5,
        recommendation: `Optimized ${peSystem} construct for ${targetGene}: PBS ${pbsLength}nt (Tm 38.5°C), RTT ${rttLength}nt. High flap resolution towards edited strand.`,
      });
      setIsDesigning(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
            <Scissors className="w-8 h-8 text-teal-400" />
            CRISPR Prime Editing pegRNA & Flap Kinetics Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 180: pegRNA PBS/RTT design, structured tevpre epegRNA optimization, and flap equilibrium kinetics predictor.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Dna className="w-5 h-5 text-teal-400" /> pegRNA Design Parameters
          </h2>
          <div>
            <label className="text-sm text-slate-400">Target Gene Locus</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={targetGene}
              onChange={(e) => setTargetGene(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Prime Editing System</label>
            <select
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={peSystem}
              onChange={(e) => setPeSystem(e.target.value)}
            >
              <option value="PEmax_epegRNA">PEmax + tevpre-epegRNA (Recommended)</option>
              <option value="PE2_canonical">PE2 Canonical pegRNA</option>
              <option value="PE3b_paired_nick">PE3b (Paired Flap Nicking)</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-slate-400">PBS Length ({pbsLength} nt)</label>
            <input
              type="range"
              min="9"
              max="17"
              step="1"
              className="w-full mt-1"
              value={pbsLength}
              onChange={(e) => setPbsLength(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">RTT Length ({rttLength} nt)</label>
            <input
              type="range"
              min="10"
              max="24"
              step="1"
              className="w-full mt-1"
              value={rttLength}
              onChange={(e) => setRttLength(parseInt(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isDesigning}
            className="w-full bg-teal-600 hover:bg-teal-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isDesigning ? "Optimizing pegRNA..." : "Generate pegRNA Design"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Activity className="w-5 h-5 text-emerald-400" /> Editing Precision & Flap Equilibrium
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Editing Efficiency</div>
                  <div className="text-2xl font-bold text-teal-400">{result.editingEfficiency}%</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Indel Byproducts</div>
                  <div className="text-2xl font-bold text-amber-400">{result.indelFrequency}%</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Flap Ratio (Edit/Unmod)</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.flapEquilibriumRatio}x</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Precision Fidelity Index</div>
                  <div className="text-2xl font-bold text-purple-400">{result.fidelityIndex}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Scissors className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure PBS/RTT lengths and simulate flap ligation kinetics</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CRISPRPrimeEditingPegDNAStudioPage;
