import React, { useState, useEffect } from 'react'
import {
  Sparkles,
  Activity,
  Layers,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Search,
  Filter,
  BarChart3,
  Dna,
  ShieldCheck,
  Zap,
  Users
} from 'lucide-react'
import { api } from '../services/api'

interface BiomarkerFeature {
  id: string
  feature_name: string
  omics_modality: string
  log2_fold_change: number
  adjusted_p_value: number
  feature_importance_weight: number
  correlation_direction: string
}

interface PatientStratification {
  id: string
  patient_cohort_id: string
  prognostic_risk_tier: string
  response_probability_score: number
  composite_signature_score: number
  expression_map: Record<string, number>
}

interface BiomarkerStudy {
  id: string
  study_title: string
  disease_indication: string
  cohort_sample_size: number
  omics_layers: string[]
  signature_stability_score: number
  auc_roc_score: number
  metadata?: Record<string, any>
  features: BiomarkerFeature[]
  stratifications: PatientStratification[]
}

export const BiomarkerDiscoveryStudioPage: React.FC = () => {
  const [studies, setStudies] = useState<BiomarkerStudy[]>([])
  const [selectedStudy, setSelectedStudy] = useState<BiomarkerStudy | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [modalityFilter, setModalityFilter] = useState<string>('ALL')

  // Form State
  const [title, setTitle] = useState('Anti-PD1 Immunotherapy Multi-Omics Signature')
  const [indication, setIndication] = useState('Non-Small Cell Lung Cancer (NSCLC)')
  const [cohortSize, setCohortSize] = useState(120)
  const [submitting, setSubmitting] = useState(false)

  const fetchStudies = async () => {
    try {
      setLoading(true)
      const res = await api.get('/biomarkers/studies')
      setStudies(res.data)
      if (res.data.length > 0) {
        fetchStudyDetails(res.data[0].id)
      } else {
        setLoading(false)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch biomarker studies')
      setLoading(false)
    }
  }

  const fetchStudyDetails = async (studyId: string) => {
    try {
      const res = await api.get(`/biomarkers/studies/${studyId}`)
      setSelectedStudy(res.data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch study details')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudies()
  }, [])

  const handleExtractSignature = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await api.post('/biomarkers/studies/extract', {
        study_title: title,
        disease_indication: indication,
        cohort_sample_size: cohortSize,
        omics_layers: ['TRANSCRIPTOMICS', 'PROTEOMICS', 'EPIGENOMICS', 'METABOLOMICS'],
      })
      setSelectedStudy(res.data)
      fetchStudies()
    } catch (err: any) {
      setError(err.message || 'Failed to extract signature')
    } finally {
      setSubmitting(false)
    }
  }

  const filteredFeatures = selectedStudy?.features?.filter(f => {
    if (modalityFilter === 'ALL') return true
    return f.omics_modality === modalityFilter
  }) || []

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px', color: '#10b981' }}>
            <Sparkles size={32} />
            Multi-Modal Biomarker Discovery Studio
          </h1>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)', marginTop: '4px' }}>
            Autonomous Multi-Omics Signature Extraction, Regularized ElasticNet Feature Weights & Patient Risk Stratification
          </p>
        </div>
        <button
          onClick={fetchStudies}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: '8px',
            backgroundColor: 'var(--color-surface, #1e293b)',
            border: '1px solid var(--color-border, #334155)',
            color: '#f8fafc',
            cursor: 'pointer'
          }}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', backgroundColor: '#ef444420', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px' }}>
        {/* Left Column: Extraction Form & Study History */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={20} color="#10b981" />
              Signature Extraction Pipeline
            </h3>
            <form onSubmit={handleExtractSignature} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Study Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Disease Indication</label>
                <input
                  type="text"
                  value={indication}
                  onChange={(e) => setIndication(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Cohort Sample Size (N)</label>
                <input
                  type="number"
                  value={cohortSize}
                  onChange={(e) => setCohortSize(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  min={10}
                  max={10000}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  marginTop: '8px',
                  padding: '10px',
                  borderRadius: '6px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#fff',
                  fontWeight: 600,
                  border: 'none',
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {submitting ? <RefreshCw className="animate-spin" size={18} /> : <Sparkles size={18} />}
                {submitting ? 'Extracting Signature...' : 'Extract Multi-Omics Signature'}
              </button>
            </form>
          </div>

          {/* Study History */}
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', maxHeight: '420px', overflowY: 'auto' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={18} color="#38bdf8" />
              Active Biomarker Studies
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {studies.map((s) => (
                <div
                  key={s.id}
                  onClick={() => fetchStudyDetails(s.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: selectedStudy?.id === s.id ? '#10b98120' : '#0f172a',
                    border: selectedStudy?.id === s.id ? '1px solid #10b981' : '1px solid #334155',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>{s.study_title}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{s.disease_indication}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '11px', color: '#38bdf8' }}>
                    <span>AUROC: {s.auc_roc_score}</span>
                    <span>Stability: {s.signature_stability_score}</span>
                  </div>
                </div>
              ))}
              {studies.length === 0 && !loading && (
                <div style={{ textAlign: 'center', color: '#64748b', padding: '20px' }}>No studies recorded</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Detailed Study Inspection */}
        {selectedStudy ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Top Overview Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Discrimination Power</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', marginTop: '4px' }}>
                  {selectedStudy.auc_roc_score} AUROC
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Cross-Validated AUC</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Signature Stability</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#38bdf8', marginTop: '4px' }}>
                  {(selectedStudy.signature_stability_score * 100).toFixed(0)}%
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Permutation Robustness</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Cohort Size (N)</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', marginTop: '4px' }}>
                  {selectedStudy.cohort_sample_size}
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Patients Analyzed</span>
              </div>

              <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '16px', borderRadius: '10px', border: '1px solid var(--color-border, #334155)' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Omics Modalities</span>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#a855f7', marginTop: '4px' }}>
                  {selectedStudy.omics_layers?.length || 4} Layers
                </div>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Integrated Layers</span>
              </div>
            </div>

            {/* Feature Rank & Filter Table */}
            <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Dna size={20} color="#10b981" />
                  Key Biomarker Signature Features
                </h3>
                {/* Modality Filter Pills */}
                <div style={{ display: 'flex', gap: '8px' }}>
                  {['ALL', 'TRANSCRIPTOMICS', 'PROTEOMICS', 'EPIGENOMICS', 'METABOLOMICS'].map((mod) => (
                    <button
                      key={mod}
                      onClick={() => setModalityFilter(mod)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        background: modalityFilter === mod ? '#10b981' : '#0f172a',
                        border: '1px solid #334155',
                        color: modalityFilter === mod ? '#fff' : '#94a3b8'
                      }}
                    >
                      {mod}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                      <th style={{ padding: '8px' }}>Feature Name</th>
                      <th style={{ padding: '8px' }}>Modality</th>
                      <th style={{ padding: '8px' }}>Log2 FC</th>
                      <th style={{ padding: '8px' }}>Adj. p-value</th>
                      <th style={{ padding: '8px' }}>ElasticNet Weight</th>
                      <th style={{ padding: '8px' }}>Direction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFeatures.map((f) => (
                      <tr key={f.id} style={{ borderBottom: '1px solid #1e293b', color: '#f8fafc' }}>
                        <td style={{ padding: '10px 8px', fontWeight: 600 }}>{f.feature_name}</td>
                        <td style={{ padding: '10px 8px' }}>
                          <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: '#38bdf820', color: '#38bdf8', border: '1px solid #38bdf840' }}>
                            {f.omics_modality}
                          </span>
                        </td>
                        <td style={{ padding: '10px 8px', color: f.log2_fold_change > 0 ? '#10b981' : '#ef4444' }}>
                          {f.log2_fold_change > 0 ? `+${f.log2_fold_change}` : f.log2_fold_change}
                        </td>
                        <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{f.adjusted_p_value}</td>
                        <td style={{ padding: '10px 8px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ flex: 1, height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{ width: `${f.feature_importance_weight * 100}%`, height: '100%', background: '#10b981' }} />
                            </div>
                            <span style={{ fontSize: '11px', color: '#10b981' }}>{f.feature_importance_weight}</span>
                          </div>
                        </td>
                        <td style={{ padding: '10px 8px' }}>
                          <span style={{ color: f.correlation_direction === 'POSITIVE' ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                            {f.correlation_direction}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Patient Risk Stratification Cards */}
            <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Users size={20} color="#f59e0b" />
                Patient Cohort Risk Stratification & Clinical Response
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                {selectedStudy.stratifications?.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      backgroundColor: '#0f172a',
                      padding: '16px',
                      borderRadius: '8px',
                      border: s.prognostic_risk_tier === 'LOW' ? '1px solid #10b981' : s.prognostic_risk_tier === 'HIGH' ? '1px solid #ef4444' : '1px solid #f59e0b'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontWeight: 600, color: '#fff' }}>{s.patient_cohort_id}</span>
                      <span
                        style={{
                          fontSize: '11px',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 600,
                          background: s.prognostic_risk_tier === 'LOW' ? '#10b98120' : s.prognostic_risk_tier === 'HIGH' ? '#ef444420' : '#f59e0b20',
                          color: s.prognostic_risk_tier === 'LOW' ? '#10b981' : s.prognostic_risk_tier === 'HIGH' ? '#ef4444' : '#f59e0b'
                        }}
                      >
                        {s.prognostic_risk_tier} RISK
                      </span>
                    </div>
                    <div style={{ marginTop: '12px', fontSize: '13px', color: '#94a3b8' }}>
                      <div>Response Probability: <strong style={{ color: '#38bdf8' }}>{(s.response_probability_score * 100).toFixed(0)}%</strong></div>
                      <div>Composite Signature Score: <strong style={{ color: '#f8fafc' }}>{s.composite_signature_score}</strong></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', backgroundColor: 'var(--color-surface, #1e293b)', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', color: '#64748b' }}>
            Select or extract a biomarker study to inspect multi-omics signatures
          </div>
        )}
      </div>
    </div>
  )
}

export default BiomarkerDiscoveryStudioPage
