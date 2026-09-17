import React, { useState } from 'react'
import {
  Pill,
  Target,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Activity,
  Layers,
  Sparkles,
  Search,
  Dna,
  Zap
} from 'lucide-react'

interface TargetAffinity {
  target_gene: string
  uniprot_id: string
  protein_family: string
  affinity_type: string
  affinity_value_nm: number
  is_primary_target: boolean
  is_off_target_liability: boolean
}

interface ToxicityAlert {
  target_gene: string
  risk_type: string
  binding_potency_nm: number
  severity: 'HIGH' | 'MODERATE' | 'LOW'
  recommendation: string
}

export const ChemogenomicsStudioPage: React.FC = () => {
  const [compoundName, setCompoundName] = useState('Imatinib (Gleevec)')
  const [smiles, setSmiles] = useState('CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5')
  const [primaryTarget, setPrimaryTarget] = useState('ABL1')
  const [giniIndex, setGiniIndex] = useState(0.68)
  const [selectivityTier, setSelectivityTier] = useState<'HIGHLY_SELECTIVE' | 'FAMILY_SELECTIVE' | 'PAN_INHIBITOR'>('FAMILY_SELECTIVE')
  const [isScreening, setIsScreening] = useState(false)

  const [affinities, setAffinities] = useState<TargetAffinity[]>([
    { target_gene: 'ABL1', uniprot_id: 'P00519', protein_family: 'KINASE (Tyrosine)', affinity_type: 'IC50', affinity_value_nm: 38.0, is_primary_target: true, is_off_target_liability: false },
    { target_gene: 'DDR1', uniprot_id: 'Q08345', protein_family: 'KINASE (RTK)', affinity_type: 'IC50', affinity_value_nm: 95.0, is_primary_target: false, is_off_target_liability: false },
    { target_gene: 'KIT', uniprot_id: 'P10721', protein_family: 'KINASE (RTK)', affinity_type: 'IC50', affinity_value_nm: 110.0, is_primary_target: false, is_off_target_liability: false },
    { target_gene: 'PDGFRA', uniprot_id: 'P16234', protein_family: 'KINASE (RTK)', affinity_type: 'IC50', affinity_value_nm: 140.0, is_primary_target: false, is_off_target_liability: false },
    { target_gene: 'KCNH2 (hERG)', uniprot_id: 'Q12809', protein_family: 'ION_CHANNEL', affinity_type: 'IC50', affinity_value_nm: 4200.0, is_primary_target: false, is_off_target_liability: false },
    { target_gene: 'EGFR', uniprot_id: 'P00533', protein_family: 'KINASE (ErbB)', affinity_type: 'IC50', affinity_value_nm: 8500.0, is_primary_target: false, is_off_target_liability: false },
    { target_gene: 'SRC', uniprot_id: 'P12931', protein_family: 'KINASE (Non-RTK)', affinity_type: 'IC50', affinity_value_nm: 12000.0, is_primary_target: false, is_off_target_liability: false },
  ])

  const [alerts, setAlerts] = useState<ToxicityAlert[]>([
    {
      target_gene: 'KCNH2 (hERG)',
      risk_type: 'CARDIOTOXICITY_HERG',
      binding_potency_nm: 4200.0,
      severity: 'LOW',
      recommendation: 'Low risk at therapeutic plasma Cmax (~2.5 µM). Ensure ECG monitoring during co-administration with CYP3A4 inhibitors.'
    }
  ])

  const handleScreen = () => {
    setIsScreening(true)
    setTimeout(() => {
      setIsScreening(false)
    }, 500)
  }

  const loadPreset = (preset: 'IMATINIB' | 'SUNITINIB' | 'OSIMERTINIB') => {
    if (preset === 'IMATINIB') {
      setCompoundName('Imatinib')
      setPrimaryTarget('ABL1')
      setGiniIndex(0.68)
      setSelectivityTier('FAMILY_SELECTIVE')
      setAffinities([
        { target_gene: 'ABL1', uniprot_id: 'P00519', protein_family: 'KINASE (Tyrosine)', affinity_type: 'IC50', affinity_value_nm: 38.0, is_primary_target: true, is_off_target_liability: false },
        { target_gene: 'KIT', uniprot_id: 'P10721', protein_family: 'KINASE (RTK)', affinity_type: 'IC50', affinity_value_nm: 110.0, is_primary_target: false, is_off_target_liability: false },
        { target_gene: 'PDGFRA', uniprot_id: 'P16234', protein_family: 'KINASE (RTK)', affinity_type: 'IC50', affinity_value_nm: 140.0, is_primary_target: false, is_off_target_liability: false },
      ])
    } else if (preset === 'SUNITINIB') {
      setCompoundName('Sunitinib')
      setPrimaryTarget('VEGFR2 (KDR)')
      setGiniIndex(0.32)
      setSelectivityTier('PAN_INHIBITOR')
      setAffinities([
        { target_gene: 'KDR (VEGFR2)', uniprot_id: 'P35968', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 9.0, is_primary_target: true, is_off_target_liability: false },
        { target_gene: 'FLT3', uniprot_id: 'P36888', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 25.0, is_primary_target: false, is_off_target_liability: false },
        { target_gene: 'KIT', uniprot_id: 'P10721', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 15.0, is_primary_target: false, is_off_target_liability: false },
        { target_gene: 'RET', uniprot_id: 'P07949', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 45.0, is_primary_target: false, is_off_target_liability: false },
        { target_gene: 'KCNH2 (hERG)', uniprot_id: 'Q12809', protein_family: 'ION_CHANNEL', affinity_type: 'IC50', affinity_value_nm: 850.0, is_primary_target: false, is_off_target_liability: true },
      ])
    } else if (preset === 'OSIMERTINIB') {
      setCompoundName('Osimertinib (Tagrisso)')
      setPrimaryTarget('EGFR (T790M/L858R)')
      setGiniIndex(0.88)
      setSelectivityTier('HIGHLY_SELECTIVE')
      setAffinities([
        { target_gene: 'EGFR (T790M)', uniprot_id: 'P00533', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 1.2, is_primary_target: true, is_off_target_liability: false },
        { target_gene: 'EGFR (WT)', uniprot_id: 'P00533', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 180.0, is_primary_target: false, is_off_target_liability: false },
        { target_gene: 'ERBB2 (HER2)', uniprot_id: 'P04626', protein_family: 'KINASE', affinity_type: 'IC50', affinity_value_nm: 42.0, is_primary_target: false, is_off_target_liability: false },
      ])
    }
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Pill size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Chemogenomics Polypharmacology & Kinome Interactome Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#a78bfa',
                background: 'rgba(139, 92, 246, 0.15)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 78 • ADR 078
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              Multi-target chemical profiling, Gini Selectivity Index quantification, kinome tree mapping, and antitarget safety liabilities (hERG, 5-HT2B, BSEP).
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => loadPreset('IMATINIB')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Imatinib (Family-Selective)
            </button>
            <button
              onClick={() => loadPreset('SUNITINIB')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Sunitinib (Pan-Kinase)
            </button>
            <button
              onClick={() => loadPreset('OSIMERTINIB')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Osimertinib (Specific)
            </button>
            <button
              onClick={handleScreen}
              disabled={isScreening}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 600,
                cursor: isScreening ? 'not-allowed' : 'pointer'
              }}
            >
              <Sparkles size={16} />
              {isScreening ? 'Screening...' : 'Run Kinome Screen'}
            </button>
          </div>
        </div>
      </div>

      {/* Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Gini Selectivity Index</span>
            <Target size={18} color="#a78bfa" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: giniIndex >= 0.75 ? '#34d399' : giniIndex >= 0.45 ? '#a78bfa' : '#fbbf24', marginTop: '0.5rem' }}>
            {giniIndex.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Scale: 0.0 (Promiscuous) → 1.0 (Clean)
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Selectivity Tier</span>
            <Zap size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {selectivityTier.replace('_', ' ')}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Primary Target: {primaryTarget}
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Antitarget Safety Alerts</span>
            <ShieldAlert size={18} color={alerts.length > 0 ? '#f59e0b' : '#34d399'} />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: alerts.length > 0 ? '#fbbf24' : '#34d399', marginTop: '0.5rem' }}>
            {alerts.length} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>flags</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            hERG / 5-HT2B / BSEP Panel
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Screened Kinome/GPCRs</span>
            <Layers size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {affinities.length} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>proteins</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Potent hits (IC50 &lt; 200 nM): {affinities.filter(a => a.affinity_value_nm < 200).length}
          </div>
        </div>
      </div>

      {/* Main Grid: Target Affinities & Antitarget Alerts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
        {/* Target Affinities Table */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Target Binding Potency Profile
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Ranked by Affinities (nM)</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '0.5rem' }}>Target Gene</th>
                  <th style={{ padding: '0.5rem' }}>Family</th>
                  <th style={{ padding: '0.5rem' }}>Type</th>
                  <th style={{ padding: '0.5rem' }}>Affinity (nM)</th>
                  <th style={{ padding: '0.5rem' }}>Classification</th>
                </tr>
              </thead>
              <tbody>
                {affinities.map((a, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '0.5rem' }}>
                      <div style={{ fontWeight: 700, color: a.is_primary_target ? '#38bdf8' : '#f8fafc' }}>
                        {a.target_gene} {a.is_primary_target && '🎯'}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{a.uniprot_id}</div>
                    </td>
                    <td style={{ padding: '0.5rem', fontSize: '0.8rem', color: '#cbd5e1' }}>{a.protein_family}</td>
                    <td style={{ padding: '0.5rem', fontSize: '0.8rem' }}>{a.affinity_type}</td>
                    <td style={{ padding: '0.5rem', fontWeight: 700, color: a.affinity_value_nm < 100 ? '#34d399' : a.affinity_value_nm < 1000 ? '#fbbf24' : '#94a3b8' }}>
                      {a.affinity_value_nm} nM
                    </td>
                    <td style={{ padding: '0.5rem' }}>
                      <span style={{
                        fontSize: '0.7rem',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontWeight: 600,
                        background: a.is_primary_target ? 'rgba(56, 189, 248, 0.15)' : a.is_off_target_liability ? 'rgba(239, 68, 68, 0.15)' : 'rgba(51, 65, 85, 0.5)',
                        color: a.is_primary_target ? '#38bdf8' : a.is_off_target_liability ? '#f87171' : '#94a3b8'
                      }}>
                        {a.is_primary_target ? 'PRIMARY' : a.is_off_target_liability ? 'OFF-TARGET ALERT' : 'SECONDARY HIT'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Antitarget Toxicity Alerts */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Antitarget Safety & Liabilities
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>hERG, 5-HT2B & Hepatobiliary Filters</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {alerts.map((al, idx) => (
              <div key={idx} style={{
                background: 'rgba(15, 23, 42, 0.7)',
                borderLeft: `3px solid ${al.severity === 'HIGH' ? '#f87171' : al.severity === 'MODERATE' ? '#fbbf24' : '#34d399'}`,
                padding: '0.85rem',
                borderRadius: '0 8px 8px 0',
                fontSize: '0.85rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <span style={{ fontWeight: 700, color: '#f8fafc' }}>{al.target_gene}</span>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    padding: '0.1rem 0.4rem',
                    borderRadius: '4px',
                    background: al.severity === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(52, 211, 153, 0.2)',
                    color: al.severity === 'HIGH' ? '#f87171' : '#34d399'
                  }}>
                    {al.severity} RISK
                  </span>
                </div>
                <div style={{ color: '#cbd5e1', marginBottom: '0.4rem' }}>
                  {al.risk_type.replace(/_/g, ' ')} • Potency: {al.binding_potency_nm} nM
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
                  💡 {al.recommendation}
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px', padding: '0.75rem', marginTop: 'auto' }}>
            <div style={{ fontSize: '0.8rem', color: '#ddd6fe' }}>
              🧬 <strong>Polypharmacology Insight:</strong> Multi-target inhibition of ABL1/KIT/PDGFRA confers synergistic efficacy against Gastrointestinal Stromal Tumors (GIST) and CML.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChemogenomicsStudioPage
