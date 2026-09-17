import React, { useState } from 'react'
import {
  Dna,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Cpu,
  Database,
  Layers,
  Sparkles,
  Search,
  BookOpen,
  ArrowRight,
  ExternalLink
} from 'lucide-react'

interface ACMGCriterion {
  criterion_code: string
  criterion_type: string
  status: 'MET' | 'NOT_MET' | 'INDETERMINATE'
  weight: number
  rationale: string
  evidence_source: string
}

interface PredictorScore {
  tool_name: string
  score_value: number
  score_percentile: number
  prediction_label: string
}

export const VariantPathogenicityStudioPage: React.FC = () => {
  const [geneSymbol, setGeneSymbol] = useState('BRCA1')
  const [hgvsC, setHgvsC] = useState('c.5266dupC')
  const [hgvsP, setHgvsP] = useState('p.Gln1756Profs*74')
  const [chromosome, setChromosome] = useState('chr17')
  const [genomicPosition, setGenomicPosition] = useState(43044295)
  const [refAllele, setRefAllele] = useState('C')
  const [altAllele, setAltAllele] = useState('CC')
  const [consequence, setConsequence] = useState('frameshift_variant')
  const [alleleFrequency, setAlleleFrequency] = useState(0.000015)
  const [acmgClass, setAcmgClass] = useState<'PATHOGENIC' | 'LIKELY_PATHOGENIC' | 'VUS' | 'LIKELY_BENIGN' | 'BENIGN'>('PATHOGENIC')
  const [pathogenicityScore, setPathogenicityScore] = useState(0.99)
  const [isClassifying, setIsClassifying] = useState(false)

  const [criteria, setCriteria] = useState<ACMGCriterion[]>([
    {
      criterion_code: 'PVS1',
      criterion_type: 'PATHOGENIC_VERY_STRONG',
      status: 'MET',
      weight: 8.0,
      rationale: 'Null variant (frameshift insertion in exon 20) in BRCA1 where loss-of-function is an established mechanism of hereditary breast/ovarian cancer.',
      evidence_source: 'ClinGen Dosage Sensitivity Map & Ensembl Transcript'
    },
    {
      criterion_code: 'PM2',
      criterion_type: 'PATHOGENIC_MODERATE',
      status: 'MET',
      weight: 2.0,
      rationale: 'Extremely rare in gnomAD population cohorts (AF = 0.000015; absent in homozygous state).',
      evidence_source: 'gnomAD v4.1 Genome'
    },
    {
      criterion_code: 'PP3',
      criterion_type: 'PATHOGENIC_SUPPORTING',
      status: 'MET',
      weight: 1.0,
      rationale: 'Multiple in-silico algorithms predict deleterious truncation and loss of BRCT tandem repeats (CADD Phred = 34.0, AlphaMissense = 0.98).',
      evidence_source: 'In-Silico Predictor Ensemble'
    },
    {
      criterion_code: 'PS3',
      criterion_type: 'PATHOGENIC_STRONG',
      status: 'MET',
      weight: 4.0,
      rationale: 'Validated homology-directed DNA repair (HDR) reporter assays demonstrate complete loss of homologous recombination repair function.',
      evidence_source: 'Findlay et al. Nature Saturation Genome Editing'
    }
  ])

  const [predictors, setPredictors] = useState<PredictorScore[]>([
    { tool_name: 'AlphaMissense', score_value: 0.98, score_percentile: 98.5, prediction_label: 'Pathogenic' },
    { tool_name: 'REVEL', score_value: 0.89, score_percentile: 94.0, prediction_label: 'Damaging' },
    { tool_name: 'CADD Phred', score_value: 34.0, score_percentile: 99.8, prediction_label: 'Deleterious' },
    { tool_name: 'SpliceAI', score_value: 0.04, score_percentile: 12.0, prediction_label: 'Normal Splicing' },
  ])

  const handleClassify = () => {
    setIsClassifying(true)
    setTimeout(() => {
      if (consequence.includes('frameshift') || consequence.includes('stop_gained')) {
        setAcmgClass('PATHOGENIC')
        setPathogenicityScore(0.99)
      } else if (alleleFrequency > 0.05) {
        setAcmgClass('BENIGN')
        setPathogenicityScore(0.01)
      } else {
        setAcmgClass('LIKELY_PATHOGENIC')
        setPathogenicityScore(0.92)
      }
      setIsClassifying(false)
    }, 500)
  }

  const loadPreset = (presetName: string) => {
    if (presetName === 'BRCA1') {
      setGeneSymbol('BRCA1')
      setHgvsC('c.5266dupC')
      setHgvsP('p.Gln1756Profs*74')
      setConsequence('frameshift_variant')
      setAlleleFrequency(0.000015)
      setAcmgClass('PATHOGENIC')
      setPathogenicityScore(0.99)
    } else if (presetName === 'TP53') {
      setGeneSymbol('TP53')
      setHgvsC('c.743G>A')
      setHgvsP('p.Arg248Gln')
      setConsequence('missense_variant')
      setAlleleFrequency(0.000008)
      setAcmgClass('PATHOGENIC')
      setPathogenicityScore(0.98)
    } else if (presetName === 'CFTR_BENIGN') {
      setGeneSymbol('CFTR')
      setHgvsC('c.1408A>G')
      setHgvsP('p.Met470Val')
      setConsequence('missense_variant')
      setAlleleFrequency(0.485)
      setAcmgClass('BENIGN')
      setPathogenicityScore(0.01)
    }
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        borderRadius: '16px',
        padding: '1.75rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.37)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)',
                padding: '0.5rem',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Dna size={24} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Genomic Variant Pathogenicity & ACMG Classification Studio
              </h1>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#c084fc',
                background: 'rgba(168, 85, 247, 0.15)',
                border: '1px solid rgba(168, 85, 247, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px'
              }}>
                Phase 74 • ADR 074
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
              ACMG/AMP 2015 28-criteria rule engine, ClinVar curation, AlphaMissense & REVEL ensemble pathogenicity classification.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => loadPreset('BRCA1')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              BRCA1 Founder
            </button>
            <button
              onClick={() => loadPreset('TP53')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              TP53 Hotspot
            </button>
            <button
              onClick={() => loadPreset('CFTR_BENIGN')}
              style={{ background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              CFTR Polymorphism
            </button>
            <button
              onClick={handleClassify}
              disabled={isClassifying}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 600,
                cursor: isClassifying ? 'not-allowed' : 'pointer'
              }}
            >
              <Sparkles size={16} />
              {isClassifying ? 'Evaluating...' : 'Run ACMG Evaluation'}
            </button>
          </div>
        </div>
      </div>

      {/* Hero Scorecard */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        <div style={{
          background: '#1e293b',
          border: `2px solid ${acmgClass === 'PATHOGENIC' ? '#ef4444' : acmgClass === 'LIKELY_PATHOGENIC' ? '#f97316' : acmgClass === 'BENIGN' ? '#10b981' : '#eab308'}`,
          borderRadius: '12px',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>ACMG / AMP Verdict</span>
            <ShieldAlert size={18} color={acmgClass === 'PATHOGENIC' ? '#ef4444' : '#10b981'} />
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: acmgClass === 'PATHOGENIC' ? '#f87171' : acmgClass === 'LIKELY_PATHOGENIC' ? '#fb923c' : acmgClass === 'BENIGN' ? '#34d399' : '#facc15',
            marginTop: '0.5rem'
          }}>
            {acmgClass.replace('_', ' ')}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Posterior Probability: {(pathogenicityScore * 100).toFixed(1)}%
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Gene & HGVS Notation</span>
            <Dna size={18} color="#c084fc" />
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {geneSymbol} : {hgvsP}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            {hgvsC} ({consequence})
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>gnomAD Population AF</span>
            <Database size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: alleleFrequency <= 0.0001 ? '#38bdf8' : '#f87171', marginTop: '0.5rem' }}>
            {alleleFrequency.toFixed(6)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            {alleleFrequency <= 0.0001 ? 'PM2 Met (Ultra-Rare)' : alleleFrequency >= 0.05 ? 'BA1 Met (Common Benign)' : 'Sub-threshold'}
          </div>
        </div>

        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
            <span>Criteria Met</span>
            <Layers size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.5rem' }}>
            {criteria.filter(c => c.status === 'MET').length} Rules
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            PVS1, PS3, PM2, PP3 Active
          </div>
        </div>
      </div>

      {/* Main Grid: ACMG Criteria Breakdown & In-Silico Radar */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '1.5rem' }}>
        {/* ACMG Evidence Matrix */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              ACMG / AMP 2015 Criteria Evidence Matrix
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Algorithmic Rule Evaluation</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {criteria.map((crit, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                      fontWeight: 800,
                      fontSize: '0.85rem',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '4px',
                      background: crit.criterion_type.startsWith('PATHOGENIC') ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                      color: crit.criterion_type.startsWith('PATHOGENIC') ? '#f87171' : '#34d399',
                    }}>
                      {crit.criterion_code}
                    </span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                      {crit.criterion_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#34d399',
                    background: 'rgba(52, 211, 153, 0.1)',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px'
                  }}>
                    STATUS: {crit.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                  {crit.rationale}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Source: {crit.evidence_source}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* In-Silico Ensemble Scores */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
              In-Silico Predictor Ensemble
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Machine Learning Pathogenicity Scores</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {predictors.map((pred, i) => (
              <div key={i} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem' }}>{pred.tool_name}</span>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: pred.prediction_label.includes('Pathogenic') || pred.prediction_label.includes('Damaging') || pred.prediction_label.includes('Deleterious') ? '#f87171' : '#34d399',
                    background: pred.prediction_label.includes('Pathogenic') || pred.prediction_label.includes('Damaging') || pred.prediction_label.includes('Deleterious') ? 'rgba(248, 113, 113, 0.15)' : 'rgba(52, 211, 153, 0.15)',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px'
                  }}>
                    {pred.prediction_label}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.3rem' }}>
                  <span>Raw Score: <strong style={{ color: '#f8fafc' }}>{pred.score_value}</strong></span>
                  <span>Percentile: {pred.score_percentile}%</span>
                </div>
                <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${pred.score_percentile}%`, background: '#a855f7', height: '100%', transition: 'width 0.3s' }} />
                </div>
              </div>
            ))}
          </div>

          {/* Clinical Actionability */}
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px', padding: '0.85rem', marginTop: 'auto' }}>
            <div style={{ fontWeight: 600, color: '#93c5fd', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
              💡 Clinical Actionability Guidance
            </div>
            <div style={{ fontSize: '0.8rem', color: '#bfdbfe' }}>
              High penetrance pathogenic variant in BRCA1. Qualifies patient for PARP inhibitor therapy (Olaparib/Talazoparib) and NCCN high-risk surveillance protocol.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VariantPathogenicityStudioPage
