import React, { useState } from 'react'
import {
  Boxes,
  Eye,
  Activity,
  Layers,
  Sparkles,
  Search,
  Maximize2,
  Atom,
  RotateCw,
  Compass,
  Cpu,
  BarChart2
} from 'lucide-react'

interface FSCCurvePoint {
  spatial_frequency: number
  fsc_correlation: number
  resolution_angstrom: number
}

interface ParticleSnapshot {
  particle_index: number
  coord_x: number
  coord_y: number
  coord_z: number
  euler_phi: number
  euler_theta: number
  euler_psi: number
  cross_correlation_score: number
  class_assignment: string
}

export const CryoETStudioPage: React.FC = () => {
  const [sampleName, setSampleName] = useState('In-Situ Eukaryotic 80S Ribosome')
  const [specimenOrganism, setSpecimenOrganism] = useState('Saccharomyces cerevisiae')
  const [cellularCompartment, setCellularCompartment] = useState('CYTOSOL')
  const [tiltMin, setTiltMin] = useState(-60.0)
  const [tiltMax, setTiltMax] = useState(60.0)
  const [pixelSize, setPixelSize] = useState(1.35)
  const [defocus, setDefocus] = useState(-2.5)
  const [estimatedRes, setEstimatedRes] = useState(3.85)
  const [particleCount, setParticleCount] = useState(480)
  const [isReconstructing, setIsReconstructing] = useState(false)

  const [fscCurve, setFscCurve] = useState<FSCCurvePoint[]>([
    { spatial_frequency: 0.05, fsc_correlation: 0.99, resolution_angstrom: 20.0 },
    { spatial_frequency: 0.10, fsc_correlation: 0.97, resolution_angstrom: 10.0 },
    { spatial_frequency: 0.15, fsc_correlation: 0.91, resolution_angstrom: 6.67 },
    { spatial_frequency: 0.20, fsc_correlation: 0.74, resolution_angstrom: 5.0 },
    { spatial_frequency: 0.23, fsc_correlation: 0.45, resolution_angstrom: 4.35 },
    { spatial_frequency: 0.26, fsc_correlation: 0.143, resolution_angstrom: 3.85 }, // 0.143 cutoff
    { spatial_frequency: 0.30, fsc_correlation: 0.03, resolution_angstrom: 3.33 },
  ])

  const [particles, setParticles] = useState<ParticleSnapshot[]>([
    { particle_index: 1, coord_x: 1240.5, coord_y: 1540.2, coord_z: 320.4, euler_phi: 45.2, euler_theta: 32.1, euler_psi: 112.5, cross_correlation_score: 0.84, class_assignment: 'CLASS_1' },
    { particle_index: 2, coord_x: 1840.1, coord_y: 2100.8, coord_z: 410.2, euler_phi: 120.4, euler_theta: 65.4, euler_psi: 88.0, cross_correlation_score: 0.81, class_assignment: 'CLASS_1' },
    { particle_index: 3, coord_x: 950.8, coord_y: 890.3, coord_z: 215.8, euler_phi: 210.1, euler_theta: 15.8, euler_psi: 304.2, cross_correlation_score: 0.79, class_assignment: 'CLASS_1' },
    { particle_index: 4, coord_x: 2310.4, coord_y: 1140.0, coord_z: 512.0, euler_phi: 315.0, euler_theta: 82.0, euler_psi: 195.4, cross_correlation_score: 0.76, class_assignment: 'CLASS_2' },
  ])

  const handleReconstruct = () => {
    setIsReconstructing(true)
    setTimeout(() => {
      const res = Math.round((pixelSize * 2.0 * 1.42) * 100) / 100
      setEstimatedRes(res)
      setFscCurve([
        { spatial_frequency: 0.05, fsc_correlation: 0.99, resolution_angstrom: 20.0 },
        { spatial_frequency: 0.15, fsc_correlation: 0.92, resolution_angstrom: 6.67 },
        { spatial_frequency: 0.22, fsc_correlation: 0.52, resolution_angstrom: 4.54 },
        { spatial_frequency: 0.26, fsc_correlation: 0.143, resolution_angstrom: res },
        { spatial_frequency: 0.32, fsc_correlation: 0.02, resolution_angstrom: 3.12 },
      ])
      setIsReconstructing(false)
    }, 600)
  }

  const loadPreset = (preset: 'RIBOSOME' | 'NPC' | 'ATP_SYNTHASE') => {
    if (preset === 'RIBOSOME') {
      setSampleName('In-Situ 80S Ribosome Complex')
      setSpecimenOrganism('Saccharomyces cerevisiae')
      setCellularCompartment('CYTOSOL')
      setPixelSize(1.35)
      setEstimatedRes(3.85)
      setParticleCount(480)
    } else if (preset === 'NPC') {
      setSampleName('Nuclear Pore Complex (NPC) Cytoplasmic Ring')
      setSpecimenOrganism('Homo sapiens HeLa cells')
      setCellularCompartment('NUCLEAR_PORE')
      setPixelSize(2.10)
      setEstimatedRes(6.40)
      setParticleCount(120)
    } else if (preset === 'ATP_SYNTHASE') {
      setSampleName('Mitochondrial ATP Synthase Dimer Row')
      setSpecimenOrganism('Bos taurus Heart Mitochondria')
      setCellularCompartment('MITOCHONDRIA')
      setPixelSize(1.50)
      setEstimatedRes(4.20)
      setParticleCount(320)
    }
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(14, 165, 233, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Boxes size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Cryo-ET Subtomogram Averaging (STA) & In-Situ Biology Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#38bdf8',
                background: 'rgba(14, 165, 233, 0.15)',
                border: '1px solid rgba(14, 165, 233, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 77 • ADR 077
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              In-situ 3D cryo-electron tomogram reconstruction, missing wedge compensation, Euler angular alignment, and gold-standard FSC 0.143 resolution refinement.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => loadPreset('RIBOSOME')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              80S Ribosome
            </button>
            <button
              onClick={() => loadPreset('NPC')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Nuclear Pore Complex
            </button>
            <button
              onClick={() => loadPreset('ATP_SYNTHASE')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              ATP Synthase
            </button>
            <button
              onClick={handleReconstruct}
              disabled={isReconstructing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 600,
                cursor: isReconstructing ? 'not-allowed' : 'pointer'
              }}
            >
              <Sparkles size={16} />
              {isReconstructing ? 'Refining...' : 'Run 3D STA Refinement'}
            </button>
          </div>
        </div>
      </div>

      {/* Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>FSC 0.143 Resolution</span>
            <Atom size={18} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#38bdf8', marginTop: '0.5rem' }}>
            {estimatedRes} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Å</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Nyquist: {(pixelSize * 2.0).toFixed(2)} Å • Pixel: {pixelSize} Å
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Particles Averaged</span>
            <Layers size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {particleCount} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>subvolumes</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Class 1 Consensus (92% homogeneous)
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Tilt Angle Range</span>
            <RotateCw size={18} color="#a78bfa" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {tiltMin}° to +{tiltMax}°
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Missing Wedge: {180 - (Math.abs(tiltMin) + Math.abs(tiltMax))}°
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Compartment & Organism</span>
            <Compass size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {cellularCompartment}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            {specimenOrganism}
          </div>
        </div>
      </div>

      {/* Main Grid: FSC Curve & Subtomogram Particle Coordinates */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.3fr', gap: '1.5rem' }}>
        {/* FSC Curve */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              Gold-Standard FSC Curve
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Fourier Shell Correlation vs Spatial Frequency (1/Å)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {fscCurve.map((pt, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                  <span>{pt.spatial_frequency} 1/Å ({pt.resolution_angstrom} Å)</span>
                  <span style={{ fontWeight: 600, color: pt.fsc_correlation <= 0.15 ? '#38bdf8' : '#f8fafc' }}>
                    FSC = {pt.fsc_correlation} {pt.fsc_correlation === 0.143 ? '🎯 Cutoff' : ''}
                  </span>
                </div>
                <div style={{ height: '8px', background: '#0f172a', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.max(2, pt.fsc_correlation * 100)}%`,
                    background: pt.fsc_correlation >= 0.143 ? '#0ea5e9' : '#64748b',
                    height: '100%',
                    transition: 'width 0.3s'
                  }} />
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: 'rgba(14, 165, 233, 0.1)', border: '1px solid rgba(14, 165, 233, 0.3)', borderRadius: '8px', padding: '0.75rem', marginTop: 'auto' }}>
            <div style={{ fontSize: '0.8rem', color: '#bae6fd' }}>
              🔬 <strong>Rosenthal-Henderson Standard:</strong> Resolution reported at FSC = 0.143 intersection ({estimatedRes} Å). B-factor sharpening applied: -115.0 Å².
            </div>
          </div>
        </div>

        {/* Subtomogram Particles */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              In-Situ Subtomogram Particles
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>3D Coordinates & Euler Orientations</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {particles.map((p, i) => (
              <div key={i} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.75rem', fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontWeight: 700, color: '#38bdf8' }}>Particle #{p.particle_index} ({p.class_assignment})</span>
                  <span style={{ color: '#34d399', fontWeight: 600 }}>CC: {p.cross_correlation_score}</span>
                </div>
                <div style={{ color: '#cbd5e1' }}>
                  Coordinates: X={p.coord_x}, Y={p.coord_y}, Z={p.coord_z} px
                </div>
                <div style={{ color: '#94a3b8', marginTop: '0.2rem' }}>
                  Euler (φ, θ, ψ): ({p.euler_phi}°, {p.euler_theta}°, {p.euler_psi}°)
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CryoETStudioPage
