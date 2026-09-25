import React, { useState } from "react";
import { Crosshair, ShieldAlert, Cpu, Sparkles, Activity, CheckCircle2, ShieldCheck } from "lucide-react";

export const NeoantigenHLAPresentationStudioPage: React.FC = () => {
  const [patientId, setPatientId] = useState("TUMOR-MEL-402");
  const [hlaAlleles, setHlaAlleles] = useState("HLA-A*02:01, HLA-A*24:02, HLA-B*07:02");
  const [mutationsCount, setMutationsCount] = useState(45);
  const [isScreening, setIsScreening] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsScreening(true);
    setTimeout(() => {
      setResult({
        strongBinders: 3,
        meanIC50: 14.5,
        cleavageEfficiency: 0.93,
        tapTransport: 0.89,
        immunogenicityScore: 0.88,
        recommendation: `Patient ${patientId}: Identified 3 Tier-1 neoepitopes (Top: BRAF p.V600E 'EDLTEKIGD' -> HLA-A*02:01 IC50 14.5 nM). High proteasome cleavage and TAP transport rate.`,
      });
      setIsScreening(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-orange-400 to-rose-400 bg-clip-text text-transparent">
            <Crosshair className="w-8 h-8 text-orange-400" />
            Tumor Neoantigen Proteasomal Cleavage & HLA Presentation Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 185: Somatic mutation proteasomal processing, TAP transport dynamics, and HLA-I/II presentation affinity forecaster.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Cpu className="w-5 h-5 text-orange-400" /> Patient Genomic & HLA Profile
          </h2>
          <div>
            <label className="text-sm text-slate-400">Patient / Tumor ID</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Patient HLA Genotype</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={hlaAlleles}
              onChange={(e) => setHlaAlleles(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Somatic Mutations Analyzed ({mutationsCount})</label>
            <input
              type="range"
              min="10"
              max="200"
              step="5"
              className="w-full mt-1"
              value={mutationsCount}
              onChange={(e) => setMutationsCount(parseInt(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isScreening}
            className="w-full bg-orange-600 hover:bg-orange-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isScreening ? "Predicting HLA Presentation..." : "Screen Neoepitopes"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Activity className="w-5 h-5 text-rose-400" /> Neoepitope Presentation & Immunogenicity Ranking
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Tier-1 Neoepitopes</div>
                  <div className="text-2xl font-bold text-orange-400">{result.strongBinders}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Top Binder IC50</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.meanIC50} nM</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Cleavage Efficiency</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.cleavageEfficiency}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">TAP Translocation</div>
                  <div className="text-2xl font-bold text-purple-400">{result.tapTransport}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Crosshair className="w-10 h-10 mb-2 opacity-50" />
              <p>Enter patient tumor somatic mutations and HLA alleles for presentation ranking</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NeoantigenHLAPresentationStudioPage;