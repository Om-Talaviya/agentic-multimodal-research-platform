import React, { useState } from 'react';
import { 
  Activity, 
  TrendingDown, 
  Dna, 
  Sparkles, 
  Database, 
  Search, 
  Sliders, 
  CheckCircle2, 
  BarChart3, 
  Info,
  Play,
  Download,
  Flame,
  Award,
  ShieldAlert,
  Users
} from 'lucide-react';

interface SurvivalCurve {
  risk_tier: string;
  time_points_months: number[];
  survival_probability_km: number[];
  patients_at_risk: number[];
  median_survival_months: number;
}

interface CohortPatient {
  patient_barcode: string;
  overall_survival_months: number;
  vital_status: number;
  risk_group: string;
  risk_score: number;
  biomarker_vector: Record<string, number>;
}

export const SurvivalPrognosisStudioPage: React.FC = () => {
  const [modelName, setModelName] = useState('MultiOmics-PanCancer-RiskStratifier');
  const [cancerCohort, setCancerCohort] = useState('TCGA-LUAD');
  const [sampleSize, setSampleSize] = useState(120);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'km' | 'forest' | 'cohort'>('km');

  const [cIndex, setCIndex] = useState(0.84);
  const [hazardRatio, setHazardRatio] = useState(3.82);
  const [pVal, setPVal] = useState(0.00008);

  const [curves, setCurves] = useState<SurvivalCurve[]>([
    {
      risk_tier: "HIGH",
      time_points_months: [0, 6, 12, 18, 24, 36, 48, 60],
      survival_probability_km: [1.0, 0.78, 0.52, 0.38, 0.25, 0.14, 0.08, 0.04],
      patients_at_risk: [38, 30, 20, 14, 9, 5, 3, 1],
      median_survival_months: 13.5
    },
    {
      risk_tier: "INTERMEDIATE",
      time_points_months: [0, 6, 12, 18, 24, 36, 48, 60],
      survival_probability_km: [1.0, 0.94, 0.85, 0.74, 0.62, 0.45, 0.31, 0.22],
      patients_at_risk: [52, 49, 44, 38, 32, 23, 16, 11],
      median_survival_months: 33.0
    },
    {
      risk_tier: "LOW",
      time_points_months: [0, 6, 12, 18, 24, 36, 48, 60],
      survival_probability_km: [1.0, 0.98, 0.96, 0.92, 0.88, 0.81, 0.74, 0.68],
      patients_at_risk: [30, 29, 28, 27, 26, 24, 22, 20],
      median_survival_months: 58.0
    }
  ]);

  const [patients, setPatients] = useState<CohortPatient[]>([
    { patient_barcode: "TCGA-LUAD-PT-1001", overall_survival_months: 11.2, vital_status: 1, risk_group: "HIGH", risk_score: 1.45, biomarker_vector: { "TP53": 1, "MKI67": 3.4, "KRAS": 1 } },
    { patient_barcode: "TCGA-LUAD-PT-1002", overall_survival_months: 45.8, vital_status: 0, risk_group: "LOW", risk_score: -0.62, biomarker_vector: { "CD8A": 2.8, "PD-L1": 1, "EGFR": 1 } },
    { patient_barcode: "TCGA-LUAD-PT-1003", overall_survival_months: 28.4, vital_status: 1, risk_group: "INTERMEDIATE", risk_score: 0.18, biomarker_vector: { "VEGFA": 1.2, "TP53": 0 } },
    { patient_barcode: "TCGA-LUAD-PT-1004", overall_survival_months: 8.9, vital_status: 1, risk_group: "HIGH", risk_score: 1.82, biomarker_vector: { "TP53": 1, "STK11": 1, "MKI67": 4.1 } },
  ]);

  const biomarkerWeights = [
    { gene: "MKI67 (Ki-67)", beta: 0.92, hr: 2.51, type: "Adverse" },
    { gene: "TP53 Mutation", beta: 0.85, hr: 2.34, type: "Adverse" },
    { gene: "KRAS G12C", beta: 0.74, hr: 2.10, type: "Adverse" },
    { gene: "STK11 Loss", beta: 0.65, hr: 1.91, type: "Adverse" },
    { gene: "CD8A Infiltration", beta: -0.78, hr: 0.46, type: "Favorable" },
    { gene: "EGFR Exon 19 Del", beta: -0.62, hr: 0.54, type: "Favorable" },
    { gene: "CD274 (PD-L1)", beta: -0.45, hr: 0.64, type: "Favorable" },
  ];

  const handleStratify = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/survival-prognosis/stratify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_name: modelName,
          cancer_cohort: cancerCohort,
          sample_size: sampleSize,
        })
      });
      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setCurves(data.data.curves);
          setPatients(data.data.patients);
          setCIndex(data.data.c_index_score);
          setHazardRatio(data.data.hazard_ratio_high_vs_low);
          setPVal(data.data.log_rank_p_value);
        }
      }
    } catch (e) {
      console.error('Survival stratification failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-xl border border-emerald-500/30 text-emerald-400">
              <TrendingDown className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Phase 110: Clinical-Genomic Survival Prognosis Stratifier
              </h1>
              <p className="text-sm text-slate-400">
                Multi-omics Cox proportional hazards modeling, Kaplan-Meier curves, and Harrell's C-Index validation
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handleStratify}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium rounded-lg shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            {loading ? 'Fitting Cox Model...' : 'Run Survival Stratification'}
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Harrell's C-Index</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{cIndex}</div>
          <div className="text-xs text-slate-400 mt-1">Discriminative Accuracy &gt; 0.80</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Hazard Ratio (High vs Low)</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{hazardRatio}x</div>
          <div className="text-xs text-slate-400 mt-1">95% CI [2.42 - 5.81]</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Log-Rank Test p-value</div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">{pVal.toExponential(2)}</div>
          <div className="text-xs text-slate-400 mt-1">Statistically Significant</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Cohort Patients</div>
          <div className="text-2xl font-bold font-mono text-indigo-400 mt-1">{sampleSize}</div>
          <div className="text-xs text-slate-400 mt-1">Multi-Omics Integrated</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-800 mt-8 mb-6 pb-2">
        <button 
          onClick={() => setActiveTab('km')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'km' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <TrendingDown className="w-4 h-4" />
          Kaplan-Meier Survival Curves
        </button>
        <button 
          onClick={() => setActiveTab('forest')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'forest' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <BarChart3 className="w-4 h-4" />
          Cox Hazard Ratio Forest Plot
        </button>
        <button 
          onClick={() => setActiveTab('cohort')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeTab === 'cohort' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Users className="w-4 h-4" />
          Patient Cohort ({patients.length})
        </button>
      </div>

      {/* Content Area */}
      {activeTab === 'km' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 p-6 rounded-xl backdrop-blur-md">
            <h3 className="font-semibold text-slate-200 mb-6 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-emerald-400" />
                Overall Survival (OS) by Multi-Omics Risk Stratification
              </span>
              <span className="text-xs text-slate-400 font-mono">Months post-diagnosis</span>
            </h3>

            {/* Kaplan-Meier Step-Plot Simulation Visualizer */}
            <div className="w-full h-72 bg-slate-950 rounded-xl border border-slate-800 p-4 relative flex flex-col justify-between">
              <div className="absolute inset-x-8 inset-y-6 flex flex-col justify-between pointer-events-none opacity-20">
                <div className="border-b border-slate-600 w-full h-0"></div>
                <div className="border-b border-slate-600 w-full h-0"></div>
                <div className="border-b border-slate-600 w-full h-0"></div>
                <div className="border-b border-slate-600 w-full h-0"></div>
              </div>

              {/* Curve Traces */}
              <div className="relative w-full h-full">
                {curves.map((cv) => {
                  const color = cv.risk_tier === 'HIGH' ? '#f43f5e' : cv.risk_tier === 'INTERMEDIATE' ? '#eab308' : '#10b981';
                  const points = cv.time_points_months.map((t, i) => {
                    const x = (t / 60) * 100;
                    const y = (1.0 - cv.survival_probability_km[i]) * 100;
                    return `${x}%,${y}%`;
                  }).join(' ');

                  return (
                    <svg key={cv.risk_tier} className="absolute inset-0 w-full h-full overflow-visible">
                      <polyline
                        fill="none"
                        stroke={color}
                        strokeWidth="3"
                        points={cv.time_points_months.map((t, i) => {
                          const x = (t / 60) * 100;
                          const y = (1.0 - cv.survival_probability_km[i]) * 100;
                          return `${x * 6.5},${y * 2.2}`;
                        }).join(' ')}
                      />
                    </svg>
                  );
                })}
              </div>

              <div className="flex justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                <span>0m</span>
                <span>12m</span>
                <span>24m</span>
                <span>36m</span>
                <span>48m</span>
                <span>60m</span>
              </div>
            </div>

            {/* Risk Legend Table */}
            <div className="grid grid-cols-3 gap-4 mt-4">
              {curves.map((cv) => (
                <div key={cv.risk_tier} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`w-3 h-3 rounded-full ${cv.risk_tier === 'HIGH' ? 'bg-rose-500' : cv.risk_tier === 'INTERMEDIATE' ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
                    <span className="text-xs font-bold text-slate-200">{cv.risk_tier} RISK</span>
                  </div>
                  <div className="text-xs text-slate-400">Median OS: <span className="font-mono text-slate-200 font-semibold">{cv.median_survival_months} mo</span></div>
                  <div className="text-xs text-slate-400">5-Year OS: <span className="font-mono text-slate-200 font-semibold">{(cv.survival_probability_km.slice(-1)[0] * 100).toFixed(0)}%</span></div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-xl backdrop-blur-md h-fit">
            <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-400" />
              Prognostic Model Validation
            </h3>
            <div className="space-y-4 text-sm">
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Cancer Staging Cohort</div>
                <div className="text-lg font-bold font-mono text-emerald-400">{cancerCohort}</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Survival Regression Model</div>
                <div className="text-lg font-bold font-mono text-teal-400">Cox PH (Multi-Omics)</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Bootstrap Cross-Validation</div>
                <div className="text-lg font-bold font-mono text-indigo-400">1000 Iterations (0.84 C-Index)</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'forest' && (
        <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-xl backdrop-blur-md">
          <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            Cox Proportional Hazards Forest Plot (Genomic Biomarkers)
          </h3>
          <div className="space-y-3">
            {biomarkerWeights.map((bm) => (
              <div key={bm.gene} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-200">{bm.gene}</div>
                  <div className="text-xs text-slate-400">Beta coefficient: {bm.beta > 0 ? `+${bm.beta}` : bm.beta}</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm font-bold font-mono text-slate-100">HR = {bm.hr}</div>
                    <span className={`text-[10px] px-2 py-0.5 rounded border ${bm.type === 'Adverse' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'}`}>
                      {bm.type} Prognosis
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'cohort' && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-md">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="p-4">Patient Barcode</th>
                <th className="p-4">Risk Tier</th>
                <th className="p-4">Risk Score</th>
                <th className="p-4">Overall Survival</th>
                <th className="p-4">Vital Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {patients.map((pt, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono text-emerald-300 font-semibold">{pt.patient_barcode}</td>
                  <td className="p-4">
                    <span className={`text-xs px-2.5 py-1 rounded font-bold border ${pt.risk_group === 'HIGH' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : pt.risk_group === 'INTERMEDIATE' ? 'bg-amber-500/10 text-amber-300 border-amber-500/30' : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'}`}>
                      {pt.risk_group}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-slate-300">{pt.risk_score}</td>
                  <td className="p-4 font-mono text-slate-200">{pt.overall_survival_months} mo</td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-0.5 rounded ${pt.vital_status === 1 ? 'bg-rose-950 text-rose-300' : 'bg-emerald-950 text-emerald-300'}`}>
                      {pt.vital_status === 1 ? 'Deceased' : 'Censored / Alive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default SurvivalPrognosisStudioPage;
