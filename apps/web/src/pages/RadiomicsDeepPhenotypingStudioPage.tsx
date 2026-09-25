import React, { useState } from "react";
import { Scan, Eye, Cpu, Sparkles, Activity, CheckCircle2, ShieldCheck } from "lucide-react";

export const RadiomicsDeepPhenotypingStudioPage: React.FC = () => {
  const [modality, setModality] = useState("Multiparametric MRI (T1c, T2, FLAIR, DWI)");
  const [tumorType, setTumorType] = useState("Glioblastoma Multiforme");
  const [gtvCm3, setGtvCm3] = useState(48.5);
  const [heterogeneity, setHeterogeneity] = useState(0.89);
  const [isSegmenting, setIsSegmenting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setIsSegmenting(true);
    setTimeout(() => {
      setResult({
        activeRimVol: 22.3,
        necroticVol: 11.6,
        glcmEntropy: 6.12,
        hypoxiaSUV: 6.8,
        predictedOSMonths: 15.3,
        recommendation: `${tumorType} Habitat Segmentation: Resolved 3 functional subregions. High GLCM entropy (6.12) & hypoxia PET SUV (6.8) forecast overall survival of 15.3 months.`,
      });
      setIsSegmenting(false);
    }, 600);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            <Scan className="w-8 h-8 text-blue-400" />
            Oncology Radiomics & Tumor Habitat Imaging Studio
          </h1>
          <p className="text-slate-400 mt-2">
            Phase 186: Multi-parametric MRI/CT habitat deconstruction, IBSI-compliant GLCM texture extraction, and radiogenomic prognostic forecaster.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Cpu className="w-5 h-5 text-blue-400" /> Imaging Scan Parameters
          </h2>
          <div>
            <label className="text-sm text-slate-400">Scan Modality</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={modality}
              onChange={(e) => setModality(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Tumor Pathology</label>
            <input
              type="text"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 mt-1"
              value={tumorType}
              onChange={(e) => setTumorType(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Gross Tumor Volume ({gtvCm3} cm³)</label>
            <input
              type="range"
              min="5"
              max="150"
              step="5"
              className="w-full mt-1"
              value={gtvCm3}
              onChange={(e) => setGtvCm3(parseFloat(e.target.value))}
            />
          </div>
          <div>
            <label className="text-sm text-slate-400">Intratumoral Heterogeneity Index ({heterogeneity})</label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              className="w-full mt-1"
              value={heterogeneity}
              onChange={(e) => setHeterogeneity(parseFloat(e.target.value))}
            />
          </div>
          <button
            onClick={handleSimulate}
            disabled={isSegmenting}
            className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
          >
            <Sparkles className="w-5 h-5" />
            {isSegmenting ? "Extracting 3D Radiomics..." : "Extract Tumor Habitats"}
          </button>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
            <Activity className="w-5 h-5 text-indigo-400" /> Habitat Spatial Metrics & Radiogenomic Prognosis
          </h2>

          {result ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Active Rim Volume</div>
                  <div className="text-2xl font-bold text-blue-400">{result.activeRimVol} cm³</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Necrotic Core Volume</div>
                  <div className="text-2xl font-bold text-rose-400">{result.necroticVol} cm³</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">GLCM Texture Entropy</div>
                  <div className="text-2xl font-bold text-cyan-400">{result.glcmEntropy}</div>
                </div>
                <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                  <div className="text-xs text-slate-400">Predicted Survival</div>
                  <div className="text-2xl font-bold text-emerald-400">{result.predictedOSMonths} mo</div>
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <Scan className="w-10 h-10 mb-2 opacity-50" />
              <p>Configure volumetric imaging parameters and segment functional tumor habitats</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RadiomicsDeepPhenotypingStudioPage;