import React, { useState } from 'react';

interface VariantScore {
  chromosome: string;
  position: number;
  reference_allele: string;
  alternate_allele: string;
  hgvs_c: string;
  raw_score: number;
  phred_score: number;
  gerp_score: number;
  phylop_score: number;
  pathogenicity_verdict: string;
}

interface EnsembleScore {
  algorithm_name: string;
  concordance_rate: number;
  high_impact_flag: string;
}

interface CADDStudy {
  id: string;
  study_name: string;
  genome_build: string;
  target_gene: string;
  variant_count: number;
  mean_phred_score: number;
  deleterious_variant_count: number;
  summary_metrics: Record<string, any>;
  variants: VariantScore[];
  ensemble_scores: EnsembleScore[];
}

export const CADDVariantPathogenicityStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('TP53_Somatic_Mutational_Hotspot_Screen');
  const [gene, setGene] = useState('TP53');
  const [build, setBuild] = useState('GRCh38');
  const [loading, setLoading] = useState(false);
  const [study, setStudy] = useState<CADDStudy | null>(null);

  const handleScore = async () => {
    setLoading(true);
    try {
      const resp = await fetch('/api/v1/cadd-variant-pathogenicity/score-variants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          genome_build: build,
          target_gene: gene,
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
        <h1 className="text-3xl font-bold text-rose-400">
          Combined Annotation Dependent Depletion (CADD) & Pathogenicity Studio
        </h1>
        <p className="text-gray-400 mt-2">
          Genome-wide in-silico variant effect prediction integrating CADD PHRED, GERP++ conservation, and AlphaMissense consensus.
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
          <label className="text-sm text-gray-400">Target Gene Locus</label>
          <input
            type="text"
            value={gene}
            onChange={(e) => setGene(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">Reference Genome</label>
          <select
            value={build}
            onChange={(e) => setBuild(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          >
            <option value="GRCh38">GRCh38 / hg38</option>
            <option value="GRCh37">GRCh37 / hg19</option>
          </select>
        </div>
        <div className="md:col-span-3">
          <button
            onClick={handleScore}
            disabled={loading}
            className="w-full bg-rose-600 hover:bg-rose-500 text-white font-semibold py-2.5 rounded-lg transition"
          >
            {loading ? 'Evaluating Epigenomic & Conservation Weights...' : 'Execute CADD & Multi-Algorithm Pathogenicity Scorer'}
          </button>
        </div>
      </div>

      {study && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Mean CADD PHRED</span>
              <p className="text-2xl font-bold text-rose-400">{study.mean_phred_score}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Deleterious Count</span>
              <p className="text-2xl font-bold text-red-400">{study.deleterious_variant_count} / {study.variant_count}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Deleterious Fraction</span>
              <p className="text-2xl font-bold text-yellow-400">
                {((study.summary_metrics?.deleterious_fraction || 0) * 100).toFixed(0)}%
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Top Driver Variant</span>
              <p className="text-sm font-mono font-bold text-cyan-300 mt-2 truncate">
                {study.summary_metrics?.top_deleterious_variant}
              </p>
            </div>
          </div>

          <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Annotated SNVs & Conservation Scores</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-300">
                <thead className="bg-gray-800 text-gray-400 uppercase text-xs">
                  <tr>
                    <th className="p-3">Position</th>
                    <th className="p-3">Alleles</th>
                    <th className="p-3">HGVS Mutation</th>
                    <th className="p-3">CADD PHRED</th>
                    <th className="p-3">GERP++</th>
                    <th className="p-3">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {study.variants.map((v, i) => (
                    <tr key={i} className="hover:bg-gray-800/50">
                      <td className="p-3 font-mono">{v.chromosome}:{v.position}</td>
                      <td className="p-3 font-semibold text-rose-300">{v.reference_allele} &gt; {v.alternate_allele}</td>
                      <td className="p-3 font-mono text-cyan-300">{v.hgvs_c}</td>
                      <td className="p-3 font-bold text-amber-400">{v.phred_score}</td>
                      <td className="p-3">{v.gerp_score}</td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded text-xs ${v.pathogenicity_verdict === 'pathogenic' ? 'bg-red-950 text-red-300' : v.pathogenicity_verdict === 'benign' ? 'bg-emerald-950 text-emerald-300' : 'bg-yellow-950 text-yellow-300'}`}>
                          {v.pathogenicity_verdict}
                        </span>
                      </td>
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

export default CADDVariantPathogenicityStudioPage;
