import React, { useState } from 'react'
import {
  TestTube2,
  Activity,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  BarChart2,
  Layers,
  Sparkles,
  Search,
  Clock,
  ShieldCheck,
  ShieldAlert,
  ArrowRight
} from 'lucide-react'

interface FragmentBin {
  bin_start_bp: number
  bin_end_bp: number
  fragment_count: number
  fragment_frequency_pct: number
}

interface EndMotif {
  motif_sequence_4mer: string
  observed_frequency: number
  reference_frequency: number
  motif_diversity_score: number
}

export const LiquidBiopsyStudioPage: React.FC = () => {
  const [patientId, setPatientId] = useState('PT-CRC-882')
  const [sampleBarcode, setSampleBarcode] = useState('LB-2026-0941')
  const [cancerType, setCancerType] = useState('Colorectal Adenocarcinoma (Stage III)')
  const [samplingTimepoint, setSamplingTimepoint] = useState('POST_SURGERY')
  const [totalCfdna, setTotalCfdna] = useState(14.8)
  const [shortFragments, setShortFragments] = useState(42000)
  const [longFragments, setLongFragments] = useState(98000)
  const [mrdStatus, setMrdStatus] = useState<'MRD_POSITIVE' | 'MRD_NEGATIVE' | 'INDETERMINATE'>('MRD_POSITIVE')
  const [tumorFraction, setTumorFraction] = useState(2.1)
  const [relapseRisk, setRelapseRisk] = useState(0.82)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const [sizeBins, setSizeBins] = useState<FragmentBin[]>([
    { bin_start_bp: 50, bin_end_bp: 99, fragment_count: 5600, fragment_frequency_pct: 4.0 },
    { bin_start_bp: 100, bin_end_bp: 130, fragment_count: 16800, fragment_frequency_pct: 12.0 },
    { bin_start_bp: 131, bin_end_bp: 150, fragment_count: 25200, fragment_frequency_pct: 18.0 },
    { bin_start_bp: 151, bin_end_bp: 175, fragment_count: 63700, fragment_frequency_pct: 45.5 }, // Peak at 167 bp
    { bin_start_bp: 176, bin_end_bp: 220, fragment_count: 34300, fragment_frequency_pct: 24.5 },
    { bin_start_bp: 221, bin_end_bp: 350, fragment_count: 11200, fragment_frequency_pct: 8.0 },
  ])

  const [endMotifs, setEndMotifs] = useState<EndMotif[]>([
    { motif_sequence_4mer: 'CCCA', observed_frequency: 0.088, reference_frequency: 0.0625, motif_diversity_score: 1.41 },
    { motif_sequence_4mer: 'CCAG', observed_frequency: 0.082, reference_frequency: 0.0625, motif_diversity_score: 1.31 },
    { motif_sequence_4mer: 'CCTG', observed_frequency: 0.070, reference_frequency: 0.0625, motif_diversity_score: 1.12 },
    { motif_sequence_4mer: 'AAAA', observed_frequency: 0.049, reference_frequency: 0.0625, motif_diversity_score: 0.78 },
    { motif_sequence_4mer: 'TTTT', observed_frequency: 0.046, reference_frequency: 0.0625, motif_diversity_score: 0.74 },
  ])

  const handleAnalyze = () => {
    setIsAnalyzing(true)
    setTimeout(() => {
      const ratio = shortFragments / Math.max(1, longFragments)
      if (ratio >= 0.30) {
        setMrdStatus('MRD_POSITIVE')
        setTumorFraction(Math.round((ratio - 0.18) * 8.5 * 10) / 10)
        setRelapseRisk(0.85)
      } else if (ratio <= 0.22) {
        setMrdStatus('MRD_NEGATIVE')
        setTumorFraction(0.02)
        setRelapseRisk(0.06)
      } else {
        setMrdStatus('INDETERMINATE')
        setTumorFraction(0.08)
        setRelapseRisk(0.35)
      }
      setIsAnalyzing(false)
    }, 500)
  }

  const loadPreset = (preset: 'CRC_POS' | 'NSCLC_CLEAR' | 'SURVEILLANCE') => {
    if (preset === 'CRC_POS') {
      setPatientId('PT-CRC-882')
      setCancerType('Colorectal Adenocarcinoma (Stage III)')
      setSamplingTimepoint('POST_SURGERY')
      setTotalCfdna(14.8)
      setShortFragments(42000)
      setLongFragments(98000)
      setMrdStatus('MRD_POSITIVE')
      setTumorFraction(2.1)
      setRelapseRisk(0.82)
    } else if (preset === 'NSCLC_CLEAR') {
      setPatientId('PT-LUNG-104')
      setCancerType('NSCLC Adenocarcinoma (Stage IIA)')
      setSamplingTimepoint('CYCLE_3_ADJUVANT')
      setTotalCfdna(8.2)
      setShortFragments(16000)
      setLongFragments(110000)
      setMrdStatus('MRD_NEGATIVE')
      setTumorFraction(0.01)
      setRelapseRisk(0.04)
    }
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(236, 72, 153, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <TestTube2 size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Liquid Biopsy ctDNA Fragmentomics & MRD Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#f472b6',
                background: 'rgba(236, 72, 153, 0.15)',
                border: '1px solid rgba(236, 72, 153, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 75 • ADR 075
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              Autonomous cell-free DNA (cfDNA) short fragment enrichment profiling, 4-mer end-motif diversity, and Minimal Residual Disease relapse forecasting.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => loadPreset('CRC_POS')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              CRC Post-Op ctDNA+
            </button>
            <button
              onClick={() => loadPreset('NSCLC_CLEAR')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              NSCLC Cycle 3 MRD-
            </button>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 600,
                cursor: isAnalyzing ? 'not-allowed' : 'pointer'
              }}
            >
              <Sparkles size={16} />
              {isAnalyzing ? 'Profiling...' : 'Run Fragmentomics MRD'}
            </button>
          </div>
        </div>
      </div>

      {/* Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{
          background: '#1e293b',
          border: `2px solid ${mrdStatus === 'MRD_POSITIVE' ? '#f43f5e' : '#10b981'}`,
          borderRadius: '12px',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>MRD Relapse Call</span>
            {mrdStatus === 'MRD_POSITIVE' ? <ShieldAlert size={18} color="#f43f5e" /> : <ShieldCheck size={18} color="#10b981 Prim" />}
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: mrdStatus === 'MRD_POSITIVE' ? '#fb7185' : '#34d399',
            marginTop: '0.5rem'
          }}>
            {mrdStatus.replace('_', ' ')}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Relapse Probability: {(relapseRisk * 100).toFixed(0)}%
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Inferred Tumor Fraction</span>
            <TrendingUp size={18} color="#f472b6" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: tumorFraction >= 0.10 ? '#fb7185' : '#34d399', marginTop: '0.5rem' }}>
            {tumorFraction.toFixed(2)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Short Frags: {((shortFragments / longFragments) * 100).toFixed(1)}% vs 18% baseline
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Total cfDNA Shed</span>
            <Activity size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {totalCfdna} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>ng/mL</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Timepoint: {samplingTimepoint}
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Clinical Action</span>
            <Sparkles size={18} color="#a78bfa" />
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {mrdStatus === 'MRD_POSITIVE' ? 'Adjuvant Escalation' : 'Standard Surveillance'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Next draw in 3 months
          </div>
        </div>
      </div>

      {/* Main Grid: Fragment Size Histogram & End-Motifs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
        {/* Fragment Length Distribution */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              cfDNA Fragment Size Distribution Profile
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Mono-nucleosomal peak (167 bp) & Tumor-derived Shortening</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {sizeBins.map((bin, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8' }}>
                  <span>{bin.bin_start_bp} – {bin.bin_end_bp} bp {bin.bin_start_bp === 151 ? '⭐️ (Canonical Peak)' : bin.bin_start_bp >= 100 && bin.bin_end_bp <= 150 ? '🔥 (Tumor Enriched)' : ''}</span>
                  <span style={{ fontWeight: 600, color: bin.bin_start_bp >= 100 && bin.bin_end_bp <= 150 ? '#f472b6' : '#f8fafc' }}>
                    {bin.fragment_frequency_pct}% ({bin.fragment_count.toLocaleString()} reads)
                  </span>
                </div>
                <div style={{ height: '10px', background: '#0f172a', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${bin.fragment_frequency_pct * 2}%`,
                    background: bin.bin_start_bp >= 100 && bin.bin_end_bp <= 150 ? '#ec4899' : '#3b82f6',
                    height: '100%',
                    transition: 'width 0.3s'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4-mer End Motifs */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              4-mer End-Motif Signatures
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Nuclease Cleavage Fingerprint</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {endMotifs.map((motif, i) => (
              <div key={i} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, color: '#f472b6', fontSize: '0.95rem' }}>{motif.motif_sequence_4mer}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Ref: {(motif.reference_frequency * 100).toFixed(1)}%</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem' }}>{(motif.observed_frequency * 100).toFixed(1)}%</div>
                  <div style={{ fontSize: '0.75rem', color: motif.motif_diversity_score > 1.2 ? '#fb7185' : '#94a3b8' }}>
                    {motif.motif_diversity_score > 1.2 ? 'Elevated in Cancer' : 'Baseline'}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: 'rgba(236, 72, 153, 0.1)', border: '1px solid rgba(236, 72, 153, 0.3)', borderRadius: '8px', padding: '0.75rem', marginTop: 'auto' }}>
            <div style={{ fontWeight: 600, color: '#f472b6', fontSize: '0.85rem' }}>
              🔬 Fragmentomics Summary
            </div>
            <div style={{ fontSize: '0.75rem', color: '#fbcfe8', marginTop: '0.2rem' }}>
              Short fragment ratio ({((shortFragments / longFragments) * 100).toFixed(1)}%) coupled with high CCCA end-motif frequencies confirms presence of persistent ctDNA.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiquidBiopsyStudioPage
