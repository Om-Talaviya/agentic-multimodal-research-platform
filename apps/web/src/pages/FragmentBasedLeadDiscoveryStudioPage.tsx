import React, { useState } from "react";
import { Magnet, Dna, Cpu, Sparkles, Box, CheckCircle2, ShieldAlert } from "lucide-react";

export const FragmentBasedLeadDiscoveryStudioPage: React.FC = () => {
  const [targetPocket, setTargetPocket] = useState("KRAS-G12D Switch-II Pocket");
  const [librarySize, setLibrarySize] = useState(1500);
  const [strategy, setStrategy] = useState("fragment_linking_rigid");
  const [isScreening, setIsScreening] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsScreening(true);
    setTimeout(() => {
      setResult({
        meanLE: 0.41,
        topLeadPotencyNM: 18.4,
        pic50: 8.74,
        deltaG: -10.6,
        saScore: 2.35,
        recommendation: `Target ${targetPocket}: Rigid alkyne-linked candidate achieves 18.4 nM binding affinity (pIC50 8.74, delta G -10.6 kcal/mol) with superior ligand efficiency (LE 0.41).`,
      });
      setIsScreening(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            <Magnet className="w-8 h-8 text-violet-400" />
            Fragment-Based Drug Discovery & Linker Growth Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 184: Biophysical fragment hit deconstruction, ligand efficiency (LE/LLE) optimization, and linker growth modeling.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Box className="w-5 h-5 text-violet-400" /> Fragment Campaign Inputs
          </h2>
          <div>
            <label className="text-sm text-slate-400">Target Binding Pocket</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={targetPocket}
              onChange={(e) => setTargetPocket(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Screening Library Size ({librarySize} fragments)</label>
            <input
              type="range"
              min="500"
              max="5000"
              step="250"
              className="w-full mt-1"
              value={librarySize}
              onChange={(e) => setLibrarySize(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Elaboration Strategy</label>
            <select
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
            >
              <option value="fragment_linking_rigid">Fragment Linking (Rigid Alkyne/Aromatic)</option>
              <option value="fragment_growing_vector">Fragment Growing (Vector SBDD)</option>
              <option value="fragment_merging_hybrid">Fragment Merging (Pharmacophore Overlap)</option>
            </select>
          </div>
          <button
            onClick={handleSimulate}
            disabled={isScreening}
            className="w-full bg-violet-600 hover:bg-violet-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isScreening ? "Linking Fragments..." : "Run FBDD Campaign"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Cpu className="w-5 h-5 text-fuchsia-400" /> Ligand Efficiency & Optimized Lead Potency
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Mean Ligand Efficiency</div>
                  <div className="text-2xl font-bold text-violet-400">{result.meanLE}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Lead Affinity (Kd)</div>
                  <div className="text-2xl font-bold text-fuchsia-400">{result.topLeadPotencyNM} nM</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Predicted pIC50</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.pic50}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Synthetic Accessibility</div>
                  <div className="text-2xl font-bold text-amber-400">{result.saScore}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Magnet className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure fragment screening parameters and perform linker growth synthesis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FragmentBasedLeadDiscoveryStudioPage;