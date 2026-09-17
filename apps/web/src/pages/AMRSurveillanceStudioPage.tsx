import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  Bug,
  Dna,
  RefreshCw,
  AlertCircle,
  Activity,
  Biohazard,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Radio
} from 'lucide-react'
import { api } from '../services/api'

interface PathogenAbundance {
  id: string
  taxon_name: string
  ncbi_taxid: number
  relative_abundance_pct: number
  read_depth: number
  pathogenicity_grade: string
  is_priority_pathogen: boolean
}

interface AMRGene {
  id: string
  gene_symbol: string
  resistance_mechanism: string
  drug_class: string
  identity_pct: number
  coverage_pct: number
  plasmid_mediated: boolean
}

interface MetagenomicSample {
  id: string
  sample_name: string
  sample_type: string
  collection_location: string
  total_reads_sequenced: number
  outbreak_risk_level: string
  metadata?: Record<string, any>
  pathogens: PathogenAbundance[]
  amr_genes: AMRGene[]
}

export const AMRSurveillanceStudioPage: React.FC = () => {
  const [samples, setSamples] = useState<MetagenomicSample[]>([])
  const [selectedSample, setSelectedSample] = useState<MetagenomicSample | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Form parameters
  const [sampleName, setSampleName] = useState('Municipal Wastewater Inflow Surveillance')
  const [sampleType, setSampleType] = useState('WASTEWATER')
  const [location, setLocation] = useState('Metro Treatment Basin #3')
  const [reads, setReads] = useState(10000000)
  const [submitting, setSubmitting] = useState(false)

  const fetchSamples = async () => {
    try {
      setLoading(true)
      const res = await api.get('/amr/samples')
      setSamples(res.data)
      if (res.data.length > 0) {
        fetchSampleDetails(res.data[0].id)
      } else {
        setLoading(false)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch AMR surveillance samples')
      setLoading(false)
    }
  }

  const fetchSampleDetails = async (id: string) => {
    try {
      const res = await api.get(`/amr/samples/${id}`)
      setSelectedSample(res.data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sample details')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSamples()
  }, [])

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await api.post('/amr/samples/analyze', {
        sample_name: sampleName,
        sample_type: sampleType,
        collection_location: location,
        total_reads_sequenced: reads,
      })
      setSelectedSample(res.data)
      fetchSamples()
    } catch (err: any) {
      setError(err.message || 'Metagenomic analysis failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px', color: '#f43f5e' }}>
            <ShieldAlert size={32} />
            Metagenomic Pathogen Surveillance & AMR Engine
          </h1>
          <p style={{ color: 'var(--color-text-secondary, #94a3b8)', marginTop: '4px' }}>
            Taxonomic Metagenomic Profiling, CARD Resistome Alignment, WHO Priority Pathogen Outbreak Warning & Plasmid Mobility Tracking
          </p>
        </div>
        <button
          onClick={fetchSamples}
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
        {/* Left Column: Form & History */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Radio size={20} color="#f43f5e" />
              Metagenomic Sample Profiler
            </h3>
            <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Sample Name</label>
                <input
                  type="text"
                  value={sampleName}
                  onChange={(e) => setSampleName(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Sample Source</label>
                  <select
                    value={sampleType}
                    onChange={(e) => setSampleType(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                  >
                    <option value="WASTEWATER">Wastewater</option>
                    <option value="CLINICAL_ISOLATE">Clinical Isolate</option>
                    <option value="AIR_BIOAEROSOL">Air Bioaerosol</option>
                    <option value="HOSPITAL_SURFACE">Hospital Surface</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Sequenced Reads</label>
                  <input
                    type="number"
                    value={reads}
                    onChange={(e) => setReads(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                    min={10000}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Location / Facility</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#fff' }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  marginTop: '8px',
                  padding: '10px',
                  borderRadius: '6px',
                  background: 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)',
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
                {submitting ? <RefreshCw className="animate-spin" size={18} /> : <Biohazard size={18} />}
                {submitting ? 'Profiling Resistome...' : 'Profile Metagenomic Resistome'}
              </button>
            </form>
          </div>

          {/* Sample History */}
          <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', maxHeight: '380px', overflowY: 'auto' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="#38bdf8" />
              Surveillance Stream
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {samples.map((s) => (
                <div
                  key={s.id}
                  onClick={() => fetchSampleDetails(s.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: selectedSample?.id === s.id ? '#f43f5e20' : '#0f172a',
                    border: selectedSample?.id === s.id ? '1px solid #f43f5e' : '1px solid #334155',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>{s.sample_name}</div>
                    <span
                      style={{
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontWeight: 600,
                        background: s.outbreak_risk_level === 'CRITICAL' ? '#ef4444' : s.outbreak_risk_level === 'ELEVATED' ? '#f59e0b' : '#10b981',
                        color: '#fff'
                      }}
                    >
                      {s.outbreak_risk_level}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{s.sample_type} • {s.collection_location}</div>
                </div>
              ))}
              {samples.length === 0 && !loading && (
                <div style={{ textAlign: 'center', color: '#64748b', padding: '20px' }}>No surveillance records found</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Detailed Metagenomic Inspection */}
        {selectedSample ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Outbreak Alert Banner */}
            <div
              style={{
                padding: '16px 20px',
                borderRadius: '12px',
                border: selectedSample.outbreak_risk_level === 'CRITICAL' ? '1px solid #ef4444' : '1px solid #f59e0b',
                backgroundColor: selectedSample.outbreak_risk_level === 'CRITICAL' ? '#ef444415' : '#f59e0b15',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <Biohazard size={32} color={selectedSample.outbreak_risk_level === 'CRITICAL' ? '#ef4444' : '#f59e0b'} />
                <div>
                  <h4 style={{ fontSize: '16px', fontWeight: 'bold', color: selectedSample.outbreak_risk_level === 'CRITICAL' ? '#f87171' : '#fbbf24' }}>
                    OUTBREAK RISK LEVEL: {selectedSample.outbreak_risk_level}
                  </h4>
                  <p style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '2px' }}>
                    {selectedSample.sample_name} • {selectedSample.collection_location} ({(selectedSample.total_reads_sequenced / 1e6).toFixed(1)}M reads)
                  </p>
                </div>
              </div>
            </div>

            {/* Pathogens Taxonomic Abundance Table */}
            <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Bug size={20} color="#f43f5e" />
                Pathogen Identification & Taxonomic Abundance
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Species / Taxon</th>
                    <th style={{ padding: '8px' }}>NCBI TaxID</th>
                    <th style={{ padding: '8px' }}>Relative Abundance</th>
                    <th style={{ padding: '8px' }}>Read Depth</th>
                    <th style={{ padding: '8px' }}>Pathogenicity</th>
                    <th style={{ padding: '8px' }}>WHO Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedSample.pathogens?.map((p) => (
                    <tr key={p.id} style={{ borderBottom: '1px solid #1e293b', color: '#f8fafc' }}>
                      <td style={{ padding: '10px 8px', fontWeight: 600 }}>{p.taxon_name}</td>
                      <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{p.ncbi_taxid}</td>
                      <td style={{ padding: '10px 8px', color: '#38bdf8', fontWeight: 600 }}>{p.relative_abundance_pct}%</td>
                      <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{p.read_depth.toLocaleString()}</td>
                      <td style={{ padding: '10px 8px' }}>
                        <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: p.pathogenicity_grade === 'HIGH_CONSEQUENCE' ? '#ef444420' : '#f59e0b20', color: p.pathogenicity_grade === 'HIGH_CONSEQUENCE' ? '#ef4444' : '#f59e0b' }}>
                          {p.pathogenicity_grade}
                        </span>
                      </td>
                      <td style={{ padding: '10px 8px' }}>
                        {p.is_priority_pathogen ? (
                          <span style={{ color: '#ef4444', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <AlertTriangle size={14} /> Critical
                          </span>
                        ) : (
                          <span style={{ color: '#64748b' }}>Standard</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* CARD Resistome & AMR Gene Breakdown */}
            <div style={{ backgroundColor: 'var(--color-surface, #1e293b)', padding: '20px', borderRadius: '12px', border: '1px solid var(--color-border, #334155)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Dna size={20} color="#38bdf8" />
                CARD Antimicrobial Resistance (AMR) Resistome
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>AMR Gene</th>
                    <th style={{ padding: '8px' }}>Mechanism</th>
                    <th style={{ padding: '8px' }}>Target Drug Class</th>
                    <th style={{ padding: '8px' }}>Identity / Coverage</th>
                    <th style={{ padding: '8px' }}>Plasmid Mobility</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedSample.amr_genes?.map((a) => (
                    <tr key={a.id} style={{ borderBottom: '1px solid #1e293b', color: '#f8fafc' }}>
                      <td style={{ padding: '10px 8px', fontWeight: 600, color: '#f43f5e' }}>{a.gene_symbol}</td>
                      <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{a.resistance_mechanism}</td>
                      <td style={{ padding: '10px 8px', fontWeight: 600, color: '#f59e0b' }}>{a.drug_class}</td>
                      <td style={{ padding: '10px 8px', color: '#38bdf8' }}>{a.identity_pct}% / {a.coverage_pct}%</td>
                      <td style={{ padding: '10px 8px' }}>
                        {a.plasmid_mediated ? (
                          <span style={{ color: '#ef4444', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Flame size={14} /> Plasmid-Borne (High Spread)
                          </span>
                        ) : (
                          <span style={{ color: '#64748b' }}>Chromosomal</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', backgroundColor: 'var(--color-surface, #1e293b)', borderRadius: '12px', border: '1px solid var(--color-border, #334155)', color: '#64748b' }}>
            Select or profile a metagenomic sample to inspect pathogens and AMR resistome
          </div>
        )}
      </div>
    </div>
  )
}

export default AMRSurveillanceStudioPage
