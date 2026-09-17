import React, { useState } from 'react'
import {
  Activity,
  Flame,
  Zap,
  TrendingUp,
  Layers,
  Sparkles,
  Search,
  Dna,
  Sliders,
  RotateCw,
  Clock,
  ArrowRight
} from 'lucide-react'

interface FRETPoint {
  frame: number
  time_sec: number
  donor_int: number
  acceptor_int: number
  fret_eff: number
  hmm_state: string
  distance_angstrom: number
}

interface ConformationalState {
  state_index: number
  state_name: string
  mean_efficiency: number
  occupancy_fraction: number
  mean_dwell_time_ms: number
  transition_rates: Record<string, number>
}

export const SmFRETStudioPage: React.FC = () => {
  const [experimentTitle, setExperimentTitle] = useState('Single-Molecule Conformational Dynamics of SAM-I Riboswitch')
  const [macromolecule, setMacromolecule] = useState('SAM-I Riboswitch')
  const [donorFluorophore, setDonorFluorophore] = useState('Cy3 (550nm)')
  const [acceptorFluorophore, setAcceptorFluorophore] = useState('Cy5 (650nm)')
  const [forsterRadius, setForsterRadius] = useState(54.0)
  const [acquisitionRate, setAcquisitionRate] = useState(100)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const [states, setStates] = useState<ConformationalState[]>([
    {
      state_index: 0,
      state_name: 'OPEN',
      mean_efficiency: 0.18,
      occupancy_fraction: 0.35,
      mean_dwell_time_ms: 120.0,
      transition_rates: { 'INTERMEDIATE': 6.2, 'CLOSED': 1.8 }
    },
    {
      state_index: 1,
      state_name: 'INTERMEDIATE',
      mean_efficiency: 0.52,
      occupancy_fraction: 0.40,
      mean_dwell_time_ms: 85.0,
      transition_rates: { 'OPEN': 5.0, 'CLOSED': 6.8 }
    },
    {
      state_index: 2,
      state_name: 'CLOSED (Ligand-Bound)',
      mean_efficiency: 0.84,
      occupancy_fraction: 0.25,
      mean_dwell_time_ms: 160.0,
      transition_rates: { 'OPEN': 1.2, 'INTERMEDIATE': 5.1 }
    }
  ])

  const [tracePoints, setTracePoints] = useState<FRETPoint[]>([
    { frame: 0, time_sec: 0.00, donor_int: 320, acceptor_int: 60, fret_eff: 0.16, hmm_state: 'OPEN', distance_angstrom: 68.5 },
    { frame: 1, time_sec: 0.01, donor_int: 310, acceptor_int: 75, fret_eff: 0.19, hmm_state: 'OPEN', distance_angstrom: 66.2 },
    { frame: 2, time_sec: 0.02, donor_int: 190, acceptor_int: 210, fret_eff: 0.52, hmm_state: 'INTERMEDIATE', distance_angstrom: 53.5 },
    { frame: 3, time_sec: 0.03, donor_int: 185, acceptor_int: 220, fret_eff: 0.54, hmm_state: 'INTERMEDIATE', distance_angstrom: 52.8 },
    { frame: 4, time_sec: 0.04, donor_int: 65, acceptor_int: 340, fret_eff: 0.84, hmm_state: 'CLOSED', distance_angstrom: 42.1 },
    { frame: 5, time_sec: 0.05, donor_int: 60, acceptor_int: 345, fret_eff: 0.85, hmm_state: 'CLOSED', distance_angstrom: 41.5 },
    { frame: 6, time_sec: 0.06, donor_int: 180, acceptor_int: 225, fret_eff: 0.55, hmm_state: 'INTERMEDIATE', distance_angstrom: 52.4 },
    { frame: 7, time_sec: 0.07, donor_int: 315, acceptor_int: 70, fret_eff: 0.18, hmm_state: 'OPEN', distance_angstrom: 67.0 },
  ])

  const handleAnalyze = () => {
    setIsAnalyzing(true)
    setTimeout(() => {
      setIsAnalyzing(false)
    }, 500)
  }

  const loadPreset = (preset: 'RIBOSWITCH' | 'HOLLIDAY' | 'CRISPR') => {
    if (preset === 'RIBOSWITCH') {
      setMacromolecule('SAM-I Riboswitch')
      setExperimentTitle('SAM-I Riboswitch Conformational Switching')
      setForsterRadius(54.0)
    } else if (preset === 'HOLLIDAY') {
      setMacromolecule('Holliday Junction (HJ-4way)')
      setExperimentTitle('Holliday Junction Isoform I vs II Conformational Dynamics')
      setForsterRadius(51.0)
    } else if (preset === 'CRISPR') {
      setMacromolecule('SpCas9-gRNA-DNA Complex')
      setExperimentTitle('SpCas9 HNH Nuclease Domain Activation Trajectory')
      setForsterRadius(56.0)
    }
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Zap size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Single-Molecule FRET (smFRET) Kinetics & Transition Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#34d399',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 79 • ADR 079
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              Time-resolved single-molecule photon intensity traces, Förster inter-dye distance modeling ($r$), and Hidden Markov Model (HMM) conformational transitions.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => loadPreset('RIBOSWITCH')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              SAM-I Riboswitch
            </button>
            <button
              onClick={() => loadPreset('HOLLIDAY')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Holliday Junction
            </button>
            <button
              onClick={() => loadPreset('CRISPR')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Cas9 HNH Gating
            </button>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 600,
                cursor: isAnalyzing ? 'not-allowed' : 'pointer'
              }}
            >
              <Sparkles size={16} />
              {isAnalyzing ? 'Fitting HMM...' : 'Run HMM Idealization'}
            </button>
          </div>
        </div>
      </div>

      {/* Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Förster Radius (R₀)</span>
            <Activity size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#34d399', marginTop: '0.5rem' }}>
            {forsterRadius} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Å</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            FRET Pair: {donorFluorophore} / {acceptorFluorophore}
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Conformational States</span>
            <Layers size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {states.length} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>HMM tiers</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Open (0.18) ⇄ Inter (0.52) ⇄ Closed (0.84)
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Camera Frame Rate</span>
            <Clock size={18} color="#fbbf24" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {acquisitionRate} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Hz</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Time resolution: 10.0 ms per frame
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Target Molecule</span>
            <Dna size={18} color="#c084fc" />
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {macromolecule}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Single-Molecule TIRF Microscope
          </div>
        </div>
      </div>

      {/* Main Grid: Dual Channel Intensity & HMM FRET Trajectory */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
        {/* Photon Intensity Trace */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Dual-Channel Fluorescence Photon Stream
            </h2>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem' }}>
              <span style={{ color: '#34d399', fontWeight: 600 }}>● Donor (Cy3)</span>
              <span style={{ color: '#f87171', fontWeight: 600 }}>● Acceptor (Cy5)</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {tracePoints.map((pt, idx) => (
              <div key={idx} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.6rem 0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                <div>
                  <span style={{ color: '#94a3b8' }}>t = {pt.time_sec}s:</span>
                  <span style={{ color: '#34d399', marginLeft: '0.5rem', fontWeight: 600 }}>I_D: {pt.donor_int}</span>
                  <span style={{ color: '#f87171', marginLeft: '0.5rem', fontWeight: 600 }}>I_A: {pt.acceptor_int}</span>
                </div>
                <div>
                  <span style={{ fontWeight: 700, color: '#60a5fa' }}>FRET E: {pt.fret_eff}</span>
                  <span style={{ color: '#cbd5e1', marginLeft: '0.5rem' }}>({pt.distance_angstrom} Å)</span>
                  <span style={{
                    marginLeft: '0.5rem',
                    fontSize: '0.7rem',
                    padding: '0.1rem 0.4rem',
                    borderRadius: '4px',
                    background: pt.hmm_state === 'CLOSED' ? 'rgba(52, 211, 153, 0.2)' : pt.hmm_state === 'INTERMEDIATE' ? 'rgba(96, 165, 250, 0.2)' : 'rgba(251, 191, 36, 0.2)',
                    color: pt.hmm_state === 'CLOSED' ? '#34d399' : pt.hmm_state === 'INTERMEDIATE' ? '#60a5fa' : '#fbbf24',
                    fontWeight: 600
                  }}>
                    {pt.hmm_state}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* HMM Conformational States */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              HMM Conformational State Dynamics
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Occupancy & Transition Kinetics</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {states.map((st, i) => (
              <div key={i} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <span style={{ fontWeight: 700, color: '#34d399', fontSize: '0.9rem' }}>{st.state_name}</span>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Mean E: <strong>{st.mean_efficiency}</strong></span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.4rem' }}>
                  Occupancy: {(st.occupancy_fraction * 100).toFixed(0)}% • Dwell Time (τ): {st.mean_dwell_time_ms} ms
                </div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  Transition Rates: {Object.entries(st.transition_rates).map(([k, v]) => `k(${st.state_name}→${k}) = ${v} s⁻¹`).join(' • ')}
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '0.75rem', marginTop: 'auto' }}>
            <div style={{ fontSize: '0.8rem', color: '#a7f3d0' }}>
              ⚡️ <strong>Kinetic Equilibrium:</strong> High-frequency transitions between Open and Intermediate state ($k_{01} = 6.2\text{ s}^{-1}$) demonstrate thermal breathing prior to ligand capture into Closed state.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SmFRETStudioPage
