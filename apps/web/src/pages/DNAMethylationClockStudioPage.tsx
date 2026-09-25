import React, { useState } from 'react';

interface CpGMarker {
  cpg_probe_id: string;
  target_gene: string;
  chromosome: string;
  genomic_coordinate: number;
  beta_value: number;
  clock_weight: number;
}

interface AgeMetric {
  clock_algorithm: string;
  predicted_epigenetic_age: number;
  acceleration_residual: number;
  mortality_hazard_ratio: number;
}

interface MethylationStudy {
  id: string;
  study_name: string;
  sample_identifier: string;
  tissue_type: string;
  chronological_age: number;
  horvath_predicted_age: number;
  hannum_predicted_age: number;
  phenoage_predicted_age: number;
  grimage_mortality_risk_score: number;
  age_acceleration_delta: number;
  summary_metrics: Record<string, any>;
  cpg_markers: CpGMarker[];
  age_metrics: AgeMetric[];
}

export const DNAMethylationClockStudioPage: React.FC = () => {
  const [studyName, setStudyName] = useState('Longevity_Cohort_Epigenetic_Profiling');
  const [donorId, setDonorId] = useState('DONOR-7721-LONGEV');
  const [tissue, setTissue] = useState('whole_blood');
  const [chronoAge, setChronoAge] = useState<number>(52.0);
  const [loading, setLoading] = useState(false);
  const [study, setStudy] = useState<MethylationStudy | null>(null);

  const handleEstimate = async () => {
    setLoading(true);
    try {
      const resp = await fetch('/api/v1/dna-methylation-clock/estimate-age', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_name: studyName,
          sample_identifier: donorId,
          tissue_type: tissue,
          chronological_age: chronoAge,
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
        <h1 className="text-3xl font-bold text-amber-400">
          Multi-Tissue Epigenetic DNA Methylation Biological Clock Studio
        </h1>
        <p className="text-gray-400 mt-2">
          Automated Horvath, Hannum, PhenoAge, and GrimAge mortality risk projection from Infinium methylation arrays.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 bg-gray-900 p-6 rounded-xl border border-gray-800">
        <div>
          <label className="text-sm text-gray-400">Study Name</label>
          <input
            type="text"
            value={studyName}
            onChange={(e) => setStudyName(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">Donor/Subject ID</label>
          <input
            type="text"
            value={donorId}
            onChange={(e) => setDonorId(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">Tissue Modality</label>
          <select
            value={tissue}
            onChange={(e) => setTissue(e.target.value)}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          >
            <option value="whole_blood">Whole Blood (Infinium EPIC)</option>
            <option value="adipose">Adipose Tissue</option>
            <option value="skin_fibroblasts">Dermal Fibroblasts</option>
            <option value="brain_cortex">Prefrontal Cortex</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-gray-400">Chronological Age (Yrs)</label>
          <input
            type="number"
            value={chronoAge}
            onChange={(e) => setChronoAge(parseFloat(e.target.value))}
            className="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 mt-1"
          />
        </div>
        <div className="md:col-span-4">
          <button
            onClick={handleEstimate}
            disabled={loading}
            className="w-full bg-amber-600 hover:bg-amber-500 text-white font-semibold py-2.5 rounded-lg transition"
          >
            {loading ? 'Evaluating Multi-Locus Epigenetic Aging...' : 'Compute Biological Age & Mortality Projections'}
          </button>
        </div>
      </div>

      {study && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Horvath Epigenetic Age</span>
              <p className="text-2xl font-bold text-amber-400">{study.horvath_predicted_age} yrs</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Age Acceleration</span>
              <p className={`text-2xl font-bold ${study.age_acceleration_delta > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                {study.age_acceleration_delta > 0 ? `+${study.age_acceleration_delta}` : study.age_acceleration_delta} yrs
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">Consensus Bio-Age</span>
              <p className="text-2xl font-bold text-cyan-400">
                {study.summary_metrics?.biological_age_consensus} yrs
              </p>
            </div>
            <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
              <span className="text-xs text-gray-400">GrimAge Mortality Hazard</span>
              <p className="text-2xl font-bold text-purple-400">
                {study.summary_metrics?.grimage_all_cause_mortality_hazard}x
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
              <h3 className="text-xl font-bold text-gray-200 mb-4">Epigenetic Clock Ensembles</h3>
              <div className="space-y-3">
                {study.age_metrics.map((m, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-gray-800/60 rounded-lg">
                    <span className="text-sm text-gray-300 font-medium">{m.clock_algorithm}</span>
                    <span className="text-amber-400 font-bold">{m.predicted_epigenetic_age} yrs</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
              <h3 className="text-xl font-bold text-gray-200 mb-4">CpG Probes & Methylation Ratios</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-300">
                  <thead className="bg-gray-800 text-gray-400 uppercase text-xs">
                    <tr>
                      <th className="p-2">Probe ID</th>
                      <th className="p-2">Gene</th>
                      <th className="p-2">Beta (β)</th>
                      <th className="p-2">Weight</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {study.cpg_markers.map((c, i) => (
                      <tr key={i} className="hover:bg-gray-800/50">
                        <td className="p-2 font-mono text-amber-300">{c.cpg_probe_id}</td>
                        <td className="p-2">{c.target_gene}</td>
                        <td className="p-2 font-semibold">{(c.beta_value * 100).toFixed(1)}%</td>
                        <td className="p-2">{c.clock_weight}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DNAMethylationClockStudioPage;
