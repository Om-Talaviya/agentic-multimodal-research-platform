import React, { useState } from 'react'
import {
  Building2,
  Users,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Globe2,
  Clock,
  ShieldAlert,
  Play,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react'

interface CandidateSite {
  id?: string
  site_name: string
  country: string
  city: string
  principal_investigator: string
  historical_recruitment_rate: number
  ethics_approval_timeline_days: number
  patient_pool_density: number
  feasibility_score: number
  risk_tier: 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK'
  selected_for_trial: boolean
  metrics?: {
    velocity_score?: number
    reg_score?: number
    density_score?: number
    pi_factor?: number
    competing_trials?: number
  }
}

interface SimulationData {
  simulation_name: string
  target_timeline_months: number
  p10_completion_months: number
  p50_completion_months: number
  p90_completion_months: number
  dropout_rate: number
  enrollment_curve: Array<{
    month: number
    projected_enrolled: number
    target_enrolled: number
  }>
  bottleneck_risks: Array<{
    risk_type: string
    severity: string
    description: string
    recommendation: string
  }>
}

export const ClinicalSiteSelectionStudioPage: React.FC = () => {
  const [protocolCode, setProtocolCode] = useState('ONC-2026-NSCLC3')
  const [studyTitle, setStudyTitle] = useState('Global Phase 3 Study of Multi-Target Bispecific vs SOC in Advanced NSCLC')
  const [indication, setIndication] = useState('Non-Small Cell Lung Cancer')
  const [phase, setPhase] = useState('Phase 3')
  const [targetEnrollment, setTargetEnrollment] = useState(450)
  const [recruitmentDuration, setRecruitmentDuration] = useState(14)
  const [dropoutRate, setDropoutRate] = useState(0.12)
  const [isEvaluating, setIsEvaluating] = useState(false)

  const [sites, setSites] = useState<CandidateSite[]>([
    {
      site_name: 'Memorial Sloan Kettering Cancer Center',
      country: 'United States',
      city: 'New York, NY',
      principal_investigator: 'Dr. Sarah Lin, MD, PhD',
      historical_recruitment_rate: 3.8,
      ethics_approval_timeline_days: 35,
      patient_pool_density: 4800,
      feasibility_score: 0.92,
      risk_tier: 'LOW_RISK',
      selected_for_trial: true,
      metrics: { velocity_score: 1.0, reg_score: 0.92, density_score: 0.96, pi_factor: 1.0, competing_trials: 2 }
    },
    {
      site_name: 'Institut Gustave Roussy',
      country: 'France',
      city: 'Villejuif, Paris',
      principal_investigator: 'Prof. Jean-Marc Dupont',
      historical_recruitment_rate: 3.2,
      ethics_approval_timeline_days: 42,
      patient_pool_density: 4100,
      feasibility_score: 0.88,
      risk_tier: 'LOW_RISK',
      selected_for_trial: true,
      metrics: { velocity_score: 1.0, reg_score: 0.80, density_score: 0.82, pi_factor: 0.9, competing_trials: 1 }
    },
    {
      site_name: 'National Cancer Center Hospital East',
      country: 'Japan',
      city: 'Kashiwa, Chiba',
      principal_investigator: 'Dr. Kenji Takahashi, MD',
      historical_recruitment_rate: 2.9,
      ethics_approval_timeline_days: 30,
      patient_pool_density: 3900,
      feasibility_score: 0.86,
      risk_tier: 'LOW_RISK',
      selected_for_trial: true,
      metrics: { velocity_score: 0.97, reg_score: 1.0, density_score: 0.78, pi_factor: 0.85, competing_trials: 1 }
    },
    {
      site_name: 'Charité – Universitätsmedizin Berlin',
      country: 'Germany',
      city: 'Berlin',
      principal_investigator: 'Prof. Dr. Elena Richter',
      historical_recruitment_rate: 2.1,
      ethics_approval_timeline_days: 58,
      patient_pool_density: 2800,
      feasibility_score: 0.71,
      risk_tier: 'MODERATE_RISK',
      selected_for_trial: true,
      metrics: { velocity_score: 0.70, reg_score: 0.53, density_score: 0.56, pi_factor: 0.8, competing_trials: 3 }
    },
    {
      site_name: 'Royal Marsden NHS Foundation Trust',
      country: 'United Kingdom',
      city: 'London',
      principal_investigator: 'Dr. Alistair Vance, FRCP',
      historical_recruitment_rate: 1.8,
      ethics_approval_timeline_days: 65,
      patient_pool_density: 2200,
      feasibility_score: 0.63,
      risk_tier: 'MODERATE_RISK',
      selected_for_trial: true,
      metrics: { velocity_score: 0.60, reg_score: 0.42, density_score: 0.44, pi_factor: 0.85, competing_trials: 4 }
    },
    {
      site_name: 'Metropolitan General Oncology Ward',
      country: 'Greece',
      city: 'Athens',
      principal_investigator: 'Dr. Nikos Karagiannis',
      historical_recruitment_rate: 0.7,
      ethics_approval_timeline_days: 85,
      patient_pool_density: 850,
      feasibility_score: 0.41,
      risk_tier: 'HIGH_RISK',
      selected_for_trial: false,
      metrics: { velocity_score: 0.23, reg_score: 0.10, density_score: 0.17, pi_factor: 0.5, competing_trials: 0 }
    }
  ])

  const [simulation, setSimulation] = useState<SimulationData>({
    simulation_name: 'Monte Carlo Stochastic Enrollment v1',
    target_timeline_months: 14.0,
    p10_completion_months: 11.5,
    p50_completion_months: 13.2,
    p90_completion_months: 15.8,
    dropout_rate: 0.12,
    enrollment_curve: [
      { month: 1, projected_enrolled: 8, target_enrolled: 32 },
      { month: 2, projected_enrolled: 25, target_enrolled: 64 },
      { month: 4, projected_enrolled: 85, target_enrolled: 128 },
      { month: 6, projected_enrolled: 170, target_enrolled: 192 },
      { month: 8, projected_enrolled: 265, target_enrolled: 256 },
      { month: 10, projected_enrolled: 350, target_enrolled: 320 },
      { month: 12, projected_enrolled: 420, target_enrolled: 384 },
      { month: 14, projected_enrolled: 450, target_enrolled: 450 },
    ],
    bottleneck_risks: [
      {
        risk_type: 'TIMELINE_OVERRUN',
        severity: 'HIGH',
        description: 'P90 completion timeline (15.8 mo) exceeds study target (14.0 mo).',
        recommendation: 'Activate 1-2 additional high-velocity sites in APAC or North America.'
      },
      {
        risk_type: 'ETHICS_APPROVAL_LATENCY',
        severity: 'MODERATE',
        description: 'European sites average 55+ days for ethics approval.',
        recommendation: 'Pre-submit regulatory dossiers 60 days prior to site initiation visit (SIV).'
      }
    ]
  })

  const handleToggleSite = (index: number) => {
    const updated = [...sites]
    updated[index].selected_for_trial = !updated[index].selected_for_trial
    setSites(updated)
  }

  const handleRunEvaluation = () => {
    setIsEvaluating(true)
    setTimeout(() => {
      const activeSites = sites.filter(s => s.selected_for_trial)
      const aggRate = activeSites.reduce((acc, s) => acc + s.historical_recruitment_rate, 0) || 1.0
      const monthsNeeded = Math.round((targetEnrollment / (aggRate * (1 - dropoutRate))) * 10) / 10
      
      setSimulation({
        simulation_name: 'Dynamic Monte Carlo Run',
        target_timeline_months: recruitmentDuration,
        p10_completion_months: Math.round(monthsNeeded * 0.85 * 10) / 10,
        p50_completion_months: monthsNeeded,
        p90_completion_months: Math.round(monthsNeeded * 1.22 * 10) / 10,
        dropout_rate: dropoutRate,
        enrollment_curve: Array.from({ length: Math.min(16, Math.ceil(monthsNeeded * 1.1)) }).map((_, i) => ({
          month: i + 1,
          projected_enrolled: Math.min(targetEnrollment, Math.round(aggRate * (i + 1) * (1 - dropoutRate) * 0.9)),
          target_enrolled: Math.min(targetEnrollment, Math.round(targetEnrollment * ((i + 1) / recruitmentDuration)))
        })),
        bottleneck_risks: monthsNeeded > recruitmentDuration ? [
          {
            risk_type: 'TIMELINE_OVERRUN',
            severity: 'HIGH',
            description: `Projected P50 timeline (${monthsNeeded} mo) exceeds target (${recruitmentDuration} mo).`,
            recommendation: 'Enable additional trial sites or adjust eligibility criteria.'
          }
        ] : [
          {
            risk_type: 'FEASIBILITY_CLEAR',
            severity: 'LOW',
            description: 'Recruitment trajectory is within protocol timeline confidence intervals.',
            recommendation: 'Proceed with site contracting and central IRB filings.'
          }
        ]
      })
      setIsEvaluating(false)
    }, 600)
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Building2 size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Clinical Trial Site Selection & Feasibility Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#60a5fa',
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 73 • ADR 073
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              Autonomous multi-site recruitment forecasting, IRB turnaround modeling, and Poisson-gamma stochastic enrollment simulations.
            </p>
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={isEvaluating}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '0.6rem 1.25rem',
              fontWeight: 600,
              cursor: isEvaluating ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)',
              transition: 'all 0.2s'
            }}
          >
            <Play size={16} />
            {isEvaluating ? 'Simulating...' : 'Run Monte Carlo Feasibility'}
          </button>
        </div>
      </div>

      {/* Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Target Enrollment</span>
            <Users size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {targetEnrollment} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>pts</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Duration: {recruitmentDuration} months
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>P50 Completion</span>
            <Clock size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#34d399', marginTop: '0.5rem' }}>
            {simulation.p50_completion_months} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>mo</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            P10: {simulation.p10_completion_months} mo • P90: {simulation.p90_completion_months} mo
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Active Trial Sites</span>
            <Globe2 size={18} color="#a78bfa" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {sites.filter(s => s.selected_for_trial).length} / {sites.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Across 5 countries
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Protocol Risk Status</span>
            <ShieldAlert size={18} color={simulation.p90_completion_months > recruitmentDuration ? '#f59e0b' : '#10b981'} />
          </div>
          <div style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            color: simulation.p90_completion_months > recruitmentDuration ? '#fbbf24' : '#34d399',
            marginTop: '0.5rem'
          }}>
            {simulation.p90_completion_months > recruitmentDuration ? 'TIMELINE RISK' : 'ON TRACK'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Dropout buffer: {Math.round(dropoutRate * 100)}%
          </div>
        </div>
      </div>

      {/* Main Grid: Sites Table & Monte Carlo Simulation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
        {/* Sites Leaderboard */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Candidate Investigative Sites
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Ranked by Feasibility Index</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '0.5rem' }}>Select</th>
                  <th style={{ padding: '0.5rem' }}>Site / Location</th>
                  <th style={{ padding: '0.5rem' }}>PI</th>
                  <th style={{ padding: '0.5rem' }}>Rate (pts/mo)</th>
                  <th style={{ padding: '0.5rem' }}>IRB Days</th>
                  <th style={{ padding: '0.5rem' }}>Score</th>
                  <th style={{ padding: '0.5rem' }}>Tier</th>
                </tr>
              </thead>
              <tbody>
                {sites.map((s, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #334155', color: s.selected_for_trial ? '#f8fafc' : '#64748b' }}>
                    <td style={{ padding: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={s.selected_for_trial}
                        onChange={() => handleToggleSite(idx)}
                        style={{ cursor: 'pointer' }}
                      />
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      <div style={{ fontWeight: 600 }}>{s.site_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{s.city}, {s.country}</div>
                    </td>
                    <td style={{ padding: '0.5rem', fontSize: '0.8rem' }}>{s.principal_investigator}</td>
                    <td style={{ padding: '0.5rem', fontWeight: 600, color: '#60a5fa' }}>{s.historical_recruitment_rate}</td>
                    <td style={{ padding: '0.5rem' }}>{s.ethics_approval_timeline_days} d</td>
                    <td style={{ padding: '0.5rem', fontWeight: 600 }}>
                      <span style={{
                        color: s.feasibility_score >= 0.75 ? '#34d399' : s.feasibility_score >= 0.50 ? '#fbbf24' : '#f87171'
                      }}>
                        {(s.feasibility_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      <span style={{
                        fontSize: '0.7rem',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontWeight: 600,
                        background: s.risk_tier === 'LOW_RISK' ? 'rgba(52, 211, 153, 0.15)' : s.risk_tier === 'MODERATE_RISK' ? 'rgba(251, 191, 36, 0.15)' : 'rgba(248, 113, 113, 0.15)',
                        color: s.risk_tier === 'LOW_RISK' ? '#34d399' : s.risk_tier === 'MODERATE_RISK' ? '#fbbf24' : '#f87171',
                      }}>
                        {s.risk_tier.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Monte Carlo Enrollment Curve */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Recruitment Trajectory (P50 vs Target)
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Cumulative Patients Enrolled Over Time</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {simulation.enrollment_curve.map((pt, i) => {
              const projPct = Math.min(100, Math.round((pt.projected_enrolled / targetEnrollment) * 100))
              const targetPct = Math.min(100, Math.round((pt.target_enrolled / targetEnrollment) * 100))
              return (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                    <span>Month {pt.month}</span>
                    <span>
                      <strong style={{ color: '#60a5fa' }}>{pt.projected_enrolled}</strong> / {pt.target_enrolled} pts ({projPct}%)
                    </span>
                  </div>
                  <div style={{ display: 'flex', height: '8px', width: '100%', background: '#0f172a', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${projPct}%`, background: '#3b82f6', transition: 'width 0.3s' }} />
                  </div>
                </div>
              )
            })}
          </div>

          {/* Bottleneck Risk Alerts */}
          <div style={{ marginTop: '0.5rem', borderTop: '1px solid #334155', paddingTop: '0.75rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.5rem' }}>
              Bottleneck & Risk Analysis
            </h3>
            {simulation.bottleneck_risks.map((risk, idx) => (
              <div key={idx} style={{
                background: 'rgba(15, 23, 42, 0.6)',
                borderLeft: `3px solid ${risk.severity === 'HIGH' ? '#f87171' : risk.severity === 'MODERATE' ? '#fbbf24' : '#34d399'}`,
                padding: '0.6rem 0.8rem',
                borderRadius: '0 6px 6px 0',
                marginBottom: '0.5rem',
                fontSize: '0.8rem'
              }}>
                <div style={{ fontWeight: 600, color: '#f8fafc' }}>{risk.description}</div>
                <div style={{ color: '#94a3b8', marginTop: '0.2rem' }}>💡 {risk.recommendation}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClinicalSiteSelectionStudioPage
