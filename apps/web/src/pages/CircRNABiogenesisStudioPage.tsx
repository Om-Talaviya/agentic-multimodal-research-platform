import React, { useState } from "react";
import { Disc, Dna, Cpu, Sparkles, Network, CheckCircle2, ShieldCheck } from "lucide-react";

export const CircRNABiogenesisStudioPage: React.FC = () => {
  const [hostGene, setHostGene] = useState("CDR1as (ciRS-7)");
  const [genomicLocus, setGenomicLocus] = useState("chrX:139865339-139866824");
  const [exonCount, setExonCount] = useState(3);
  const [aluElements, setAluElements] = useState(2);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setResult({
        backspliceEfficiency: 0.895,
        halfLifeHours: 49.5,
        totalMiRNASites: 14,
        qkiAffinity: 0.94,
        spongeEfficiencyIndex: 25.8,
        summary: `Host gene ${hostGene} forms highly stable covalently closed circRNA with 14 functional miR-7-5p sponge motifs. High resistance to exonuclease degradation.`,
      });
      setIsAnalyzing(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
            <Disc className="w-8 h-8 text-cyan-400" />
            circRNA Back-Splicing Biogenesis & miRNA Sponge Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 179: Non-canonical exon circularization, inverted Alu repeat pairing, and transcript miRNA sponge capacity predictor.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Dna className="w-5 h-5 text-cyan-400" /> Biogenesis Parameters
          </h2>
          <div>
            <label className="text-sm text-slate-400">Host Gene Symbol</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={hostGene}
              onChange={(e) => setHostGene(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Genomic Locus Coordinates</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={genomicLocus}
              onChange={(e) => setGenomicLocus(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Circularized Exon Count ({exonCount})</label>
            <input
              type="range"
              min="1"
              max="8"
              step="1"
              className="w-full mt-1"
              value={exonCount}
              onChange={(e) => setExonCount(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Flanking Inverted Alu Pairs ({aluElements})</label>
            <input
              type="range"
              min="0"
              max="5"
              step="1"
              className="w-full mt-1"
              value={aluElements}
              onChange={(e) => setAluElements(parseInt(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isAnalyzing}
            className="w-full bg-cyan-600 hover:bg-cyan-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isAnalyzing ? "Predicting Biogenesis..." : "Simulate circRNA Splicing"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Network className="w-5 h-5 text-indigo-400" /> Circular Stability & Sponge Potential
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Back-Splicing Efficiency</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.backspliceEfficiency}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">RNase R Half-Life</div>
                  <div className="text-2xl font-bold text-indigo-400">{result.halfLifeHours} hrs</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">miRNA Sponge Sites</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.totalMiRNASites}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">QKI RBP Affinity</div>
                  <div className="text-2xl font-bold text-amber-400">{result.qkiAffinity}</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.summary}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Disc className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure locus parameters and predict circular biogenesis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CircRNABiogenesisStudioPage;
