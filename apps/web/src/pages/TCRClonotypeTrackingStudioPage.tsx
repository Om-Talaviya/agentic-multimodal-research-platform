import React, { useState } from 'react';

interface ClonotypeNode {
  id?: string;
  cdr3_amino_acid: string;
  v_gene: string;
  j_gene: string;
  clone_frequency: number;
  expansion_status: string;
  antigen_specificity?: string;
}

interface DiversityMetric {
  metric_name: string;
  metric_value: number;
  metric_category: string;
}

interface TCRStudy {
  id: string;
  study_name: string;
  sample_source: string;
  repertoire_type: string;
  cell_count: number;
  shannon_entropy: number;
  gini_simpson_index: number;
  clonality_score: number;
  summary_metrics: Record<string, any>;
  clonotypes: ClonotypeNode[];
  diversity_metrics: DiversityMetric[];
}

export const TCRClonotypeTrackingStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Melanoma_TIL_Checkpoint_Response');
  const [sampleSource, setSampleSource] = useState('TIL');
  const [repertoireType, setRepertoireType] = useState('TCR_alpha_beta');
  const [loading, setLoading] = useState(false);
  const [study, setStudy] = useState<TCRStudy | null>(null);

  const handleRunAnalysis = async () => {
    setLoading(true);
    try {
      const resp = await fetch('/api/v1/tcr-clonotype-tracking/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          sample_source: sampleSource,
          repertoire_type: repertoireType,
        }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setStudy(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-cyan-400">
          Single-Cell TCR/BCR Clonotype Expansion & Immune Repertoire Studio
        </h1>
        <p className="text-gray-400 mt-2">
          Autonomous Shannon-Wiener entropy calculation, V(D)J somatic recombination tracking, and lineage convergence analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-900 p-6 rounded-xl border border-gray-800">
        <div>
          <label className="text-sm text-gray-400">Study Identifier</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">Sample Origin</label>
          <select
            value={sampleSource}
            onChange={(e) => setSampleSource(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          >
            <option value="TIL">Tumor Infiltrating Lymphocytes (TIL)</option>
            <option value="PBMC">Peripheral Blood (PBMC)</option>
            <option value="BoneMarrow">Bone Marrow Aspirate</option>
            <option value="LymphNode">Draining Lymph Node</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-gray-400">Receptor Modality</label>
          <select
            value={repertoireType}
            onChange={(e) => setRepertoireType(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          >
            <option value="TCR_alpha_beta">TCR αβ (CD4+/CD8+)</option>
            <option value="TCR_gamma_delta">TCR γδ (Innate-like)</option>
            <option value="BCR_heavy_light">BCR / Heavy & Light Chain</option>
          </select>
        </div>
        <div className="md:col-span-3">
          <button
            onClick={handleRunAnalysis}
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 rounded-lg transition"
          >
            {loading ? 'Quantifying Lineage Trajectories...' : 'Execute Clonal Expansion & Diversity Profiler'}
          </button>
        </div>
      </div>

      {study && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Shannon Entropy</span>
              <p className="text-2xl font-bold text-cyan-400">{study.shannon_entropy}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Gini-Simpson Index</span>
              <p className="text-2xl font-bold text-emerald-400">{study.gini_simpson_index}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Clonality Score</span>
              <p className="text-2xl font-bold text-yellow-400">{study.clonality_score}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Hyperexpanded Ratio</span>
              <p className="text-2xl font-bold text-purple-400">
                {((study.summary_metrics?.hyperexpanded_clone_ratio || 0) * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Expanded Clonotypes & Specificity Targets</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-300">
                <thead className="bg-gray-800 text-gray-400 uppercase text-xs">
                  <tr>
                    <th className="p-3">CDR3 Sequence</th>
                    <th className="p-3">V Gene</th>
                    <th className="p-3">J Gene</th>
                    <th className="p-3">Frequency</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Target Antigen</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {study.clonotypes.map((c, i) => (
                    <tr key={i} className="hover:bg-gray-800/50">
                      <td className="p-3 font-mono text-cyan-300">{c.cdr3_amino_acid}</td>
                      <td className="p-3">{c.v_gene}</td>
                      <td className="p-3">{c.j_gene}</td>
                      <td className="p-3 font-semibold">{(c.clone_frequency * 100).toFixed(1)}%</td>
                      <td className="p-3">
                        <span className="px-2 py-1 bg-cyan-950 text-cyan-300 rounded text-xs">
                          {c.expansion_status}
                        </span>
                      </td>
                      <td className="p-3 text-emerald-400">{c.antigen_specificity}</td>
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

export default TCRClonotypeTrackingStudioPage;
