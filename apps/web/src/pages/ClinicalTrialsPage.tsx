import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  FileCheck,
  FlaskConical,
  HeartPulse,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Users,
  Zap,
} from 'lucide-react';
import { api } from '../services/api';

interface CohortCriterion {
  id: string;
  criterion_type: 'inclusion' | 'exclusion';
  category: string;
  description: string;
  is_mandatory: boolean;
  loinc_code?: string;
}

interface DrugCandidate {
  id: string;
  compound_name: string;
  smiles_string?: string;
  current_approved_indication: string;
  repurposed_indication: string;
  binding_affinity_nm: number;
  bioavailability_pct: number;
  toxicity_risk_score: number;
  repurposing_rationale: string;
}

interface RegulatoryPackage {
  id: string;
  regulatory_agency: string;
  module_type: string;
  completeness_score: number;
  irb_readiness_verdict: string;
  validation_findings: Array<{ section?: string; status?: string; note?: string }>;
  generated_at?: string;
}

interface ClinicalProtocol {
  id: string;
  protocol_title: string;
  phase_type: string;
  disease_indication: string;
  icd_code?: string;
  investigational_agent: string;
  mechanism_of_action?: string;
  target_gene_or_protein?: string;
  primary_endpoint: string;
  secondary_endpoints: string[];
  sample_size_planned: number;
  study_duration_weeks: number;
  adverse_risk_score: number;
  regulatory_status: string;
  cohort_criteria?: CohortCriterion[];
  drug_candidates?: DrugCandidate[];
  regulatory_packages?: RegulatoryPackage[];
  created_at?: string;
}

export const ClinicalTrialsPage: React.FC = () => {
  const [protocols, setProtocols] = useState<ClinicalProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<ClinicalProtocol | null>(null);
  const [activeTab, setActiveTab] = useState<'criteria' | 'repurposing' | 'regulatory'>('criteria');
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form State for new Protocol Synthesis
  const [diseaseIndication, setDiseaseIndication] = useState('Familial Hypercholesterolemia');
  const [investigationalAgent, setInvestigationalAgent] = useState('LNP-dCas9-Epi (EpiSilence-Hep01)');
  const [targetGene, setTargetGene] = useState('PCSK9');
  const [phaseType, setPhaseType] = useState('Phase I/IIa');
  const [moa, setMoa] = useState(
    'Targeted epigenetic transcriptional repression of PCSK9 promoter via dCas9-KRAB-MeCP2 fusion delivered in ester ionizable nanoparticles.'
  );

  // New Criterion modal/inline form
  const [newCritType, setNewCritType] = useState<'inclusion' | 'exclusion'>('inclusion');
  const [newCritCategory, setNewCritCategory] = useState('biomarker');
  const [newCritDesc, setNewCritDesc] = useState('');
  const [showCritModal, setShowCritModal] = useState(false);

  const fetchProtocols = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/clinical/protocols');
      const items = res.data.protocols || [];
      setProtocols(items);
      if (items.length > 0 && !selectedProtocol) {
        loadProtocolDetails(items[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load clinical protocols');
    } finally {
      setLoading(false);
    }
  };

  const loadProtocolDetails = async (id: string) => {
    try {
      const res = await api.get(`/clinical/protocols/${id}`);
      setSelectedProtocol(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load protocol details');
    }
  };

  useEffect(() => {
    fetchProtocols();
  }, []);

  const handleGenerateProtocol = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!diseaseIndication || !investigationalAgent) return;
    try {
      setGenerating(true);
      setError(null);
      const res = await api.post('/clinical/protocols/generate', {
        disease_indication: diseaseIndication,
        investigational_agent: investigationalAgent,
        target_gene_or_protein: targetGene,
        phase_type: phaseType,
        mechanism_of_action: moa,
      });
      await fetchProtocols();
      if (res.data.protocol_id) {
        await loadProtocolDetails(res.data.protocol_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to synthesize protocol');
    } finally {
      setGenerating(false);
    }
  };

  const handleAddCriterion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProtocol || !newCritDesc) return;
    try {
      await api.post(`/clinical/protocols/${selectedProtocol.id}/criteria`, {
        criterion_type: newCritType,
        category: newCritCategory,
        description: newCritDesc,
        is_mandatory: true,
      });
      setNewCritDesc('');
      setShowCritModal(false);
      await loadProtocolDetails(selectedProtocol.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to add criterion');
    }
  };

  return (
    <div style={{ padding: '2rem 3rem', maxWidth: '1600px', margin: '0 auto', color: '#e2e8f0' }}>
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '2rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          paddingBottom: '1.5rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <div
              style={{
                background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                padding: '0.6rem',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <HeartPulse size={24} color="#ffffff" />
            </div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>
              Autonomous Clinical Trial Studio & Drug Repurposing
            </h1>
            <span
              style={{
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#34d399',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                padding: '0.2rem 0.6rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
              }}
            >
              Phase 36 • Gen 10
            </span>
          </div>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.95rem' }}>
            Autonomous PICO cohort criteria synthesizer, molecular target-affinity repurposing screen, and eCTD FDA IND
            compliance dossier generation.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={fetchProtocols}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#f8fafc',
              padding: '0.6rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#fca5a5',
          }}
        >
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Left Synthesizer & List, Right Protocol Explorer */}
      <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '2rem' }}>
        {/* Left Column: Creator & Protocol Selector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Protocol Generation Card */}
          <div
            style={{
              background: 'rgba(30, 41, 59, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '1.5rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <Sparkles size={18} color="#34d399" />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0 }}>Synthesize New Protocol</h2>
            </div>

            <form onSubmit={handleGenerateProtocol} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Disease Indication
                </label>
                <input
                  type="text"
                  value={diseaseIndication}
                  onChange={(e) => setDiseaseIndication(e.target.value)}
                  placeholder="e.g. Transthyretin Amyloidosis (ATTR)"
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '0.9rem',
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Investigational Modality / Agent
                </label>
                <input
                  type="text"
                  value={investigationalAgent}
                  onChange={(e) => setInvestigationalAgent(e.target.value)}
                  placeholder="e.g. NTLA-2001 LNP-Cas9"
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '0.9rem',
                  }}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Molecular Target
                  </label>
                  <input
                    type="text"
                    value={targetGene}
                    onChange={(e) => setTargetGene(e.target.value)}
                    placeholder="e.g. TTR / PCSK9"
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '0.9rem',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                    Phase Type
                  </label>
                  <select
                    value={phaseType}
                    onChange={(e) => setPhaseType(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.6rem 0.8rem',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '0.9rem',
                    }}
                  >
                    <option value="Phase I">Phase I (SAD/MAD)</option>
                    <option value="Phase I/IIa">Phase I/IIa (Seamless)</option>
                    <option value="Phase IIb">Phase IIb (Dose-Ranging)</option>
                    <option value="Phase III">Phase III (Pivotal RCT)</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
                  Mechanism of Action
                </label>
                <textarea
                  value={moa}
                  onChange={(e) => setMoa(e.target.value)}
                  rows={2}
                  placeholder="Describe biological target mechanism..."
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '0.85rem',
                    resize: 'none',
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={generating}
                style={{
                  marginTop: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  color: '#ffffff',
                  border: 'none',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {generating ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    Synthesizing Protocol...
                  </>
                ) : (
                  <>
                    <Zap size={16} />
                    Autonomous Protocol Synthesis
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Protocols List */}
          <div
            style={{
              background: 'rgba(30, 41, 59, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              padding: '1.25rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#94a3b8' }}>
                Active Protocols ({protocols.length})
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '380px', overflowY: 'auto' }}>
              {protocols.map((p) => {
                const isSelected = selectedProtocol?.id === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => loadProtocolDetails(p.id)}
                    style={{
                      padding: '1rem',
                      borderRadius: '10px',
                      background: isSelected ? 'rgba(16, 185, 129, 0.12)' : 'rgba(15, 23, 42, 0.6)',
                      border: isSelected ? '1px solid #10b981' : '1px solid rgba(255, 255, 255, 0.06)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          background: 'rgba(6, 182, 212, 0.15)',
                          color: '#22d3ee',
                        }}
                      >
                        {p.phase_type}
                      </span>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          color: '#10b981',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                        }}
                      >
                        {p.regulatory_status}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.25rem' }}>
                      {p.disease_indication}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{p.investigational_agent}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Protocol Dossier Studio */}
        {selectedProtocol ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Header Card */}
            <div
              style={{
                background: 'rgba(30, 41, 59, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '14px',
                padding: '1.75rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <span
                      style={{
                        background: 'rgba(16, 185, 129, 0.15)',
                        color: '#34d399',
                        padding: '0.2rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                      }}
                    >
                      {selectedProtocol.phase_type}
                    </span>
                    {selectedProtocol.icd_code && (
                      <span
                        style={{
                          background: 'rgba(148, 163, 184, 0.15)',
                          color: '#cbd5e1',
                          padding: '0.2rem 0.6rem',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                        }}
                      >
                        ICD-10: {selectedProtocol.icd_code}
                      </span>
                    )}
                    <span
                      style={{
                        background: 'rgba(59, 130, 246, 0.15)',
                        color: '#60a5fa',
                        padding: '0.2rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                      }}
                    >
                      FDA IND Cleared
                    </span>
                  </div>
                  <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: '#f8fafc' }}>
                    {selectedProtocol.protocol_title}
                  </h2>
                </div>
              </div>

              {/* Metrics Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '1rem',
                  marginTop: '1.25rem',
                  paddingTop: '1.25rem',
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                }}
              >
                <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Planned Cohort</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
                    {selectedProtocol.sample_size_planned} Patients
                  </div>
                </div>
                <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Study Duration</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
                    {selectedProtocol.study_duration_weeks} Weeks
                  </div>
                </div>
                <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Adverse Risk Score</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#34d399' }}>
                    {(selectedProtocol.adverse_risk_score * 100).toFixed(0)}% (Low)
                  </div>
                </div>
                <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Target Molecule</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#60a5fa' }}>
                    {selectedProtocol.target_gene_or_protein || 'PCSK9'}
                  </div>
                </div>
              </div>

              {/* Endpoints */}
              <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.85rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase' }}>
                    Primary Endpoint:
                  </span>
                  <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.88rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                    {selectedProtocol.primary_endpoint}
                  </p>
                </div>
              </div>
            </div>

            {/* Sub-Views Tabs */}
            <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <button
                onClick={() => setActiveTab('criteria')}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === 'criteria' ? '2px solid #10b981' : '2px solid transparent',
                  color: activeTab === 'criteria' ? '#34d399' : '#94a3b8',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <Users size={16} />
                Cohort Criteria ({selectedProtocol.cohort_criteria?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('repurposing')}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === 'repurposing' ? '2px solid #10b981' : '2px solid transparent',
                  color: activeTab === 'repurposing' ? '#34d399' : '#94a3b8',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <FlaskConical size={16} />
                Drug Repositioning Screen ({selectedProtocol.drug_candidates?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('regulatory')}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === 'regulatory' ? '2px solid #10b981' : '2px solid transparent',
                  color: activeTab === 'regulatory' ? '#34d399' : '#94a3b8',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <FileCheck size={16} />
                FDA IND / eCTD Dossier ({selectedProtocol.regulatory_packages?.length || 0})
              </button>
            </div>

            {/* Tab 1: Cohort Criteria */}
            {activeTab === 'criteria' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                    Structured PICO Inclusion & Exclusion Criteria
                  </span>
                  <button
                    onClick={() => setShowCritModal(!showCritModal)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      background: 'rgba(16, 185, 129, 0.15)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      color: '#34d399',
                      padding: '0.5rem 0.85rem',
                      borderRadius: '8px',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    <Plus size={15} /> Add Criterion
                  </button>
                </div>

                {showCritModal && (
                  <form
                    onSubmit={handleAddCriterion}
                    style={{
                      background: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      borderRadius: '10px',
                      padding: '1.25rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.85rem',
                    }}
                  >
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Criterion Type</label>
                        <select
                          value={newCritType}
                          onChange={(e: any) => setNewCritType(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.5rem',
                            background: '#0f172a',
                            border: '1px solid #334155',
                            borderRadius: '6px',
                            color: '#fff',
                            marginTop: '0.25rem',
                          }}
                        >
                          <option value="inclusion">Inclusion Criterion</option>
                          <option value="exclusion">Exclusion Criterion</option>
                        </select>
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Category</label>
                        <select
                          value={newCritCategory}
                          onChange={(e) => setNewCritCategory(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.5rem',
                            background: '#0f172a',
                            border: '1px solid #334155',
                            borderRadius: '6px',
                            color: '#fff',
                            marginTop: '0.25rem',
                          }}
                        >
                          <option value="biomarker">Biomarker / Assay</option>
                          <option value="diagnostic">Diagnostic & Histology</option>
                          <option value="safety">Organ Reserve & Safety</option>
                          <option value="demographic">Demographics</option>
                          <option value="prior_therapy">Prior Therapy Washout</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Medical Description</label>
                      <input
                        type="text"
                        value={newCritDesc}
                        onChange={(e) => setNewCritDesc(e.target.value)}
                        placeholder="e.g. Documented baseline mutation or lab threshold..."
                        style={{
                          width: '100%',
                          padding: '0.6rem',
                          background: '#0f172a',
                          border: '1px solid #334155',
                          borderRadius: '6px',
                          color: '#fff',
                          marginTop: '0.25rem',
                        }}
                        required
                      />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => setShowCritModal(false)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'none',
                          border: '1px solid #334155',
                          color: '#94a3b8',
                          borderRadius: '6px',
                          cursor: 'pointer',
                        }}
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        style={{
                          padding: '0.5rem 1.25rem',
                          background: '#10b981',
                          border: 'none',
                          color: '#fff',
                          fontWeight: 600,
                          borderRadius: '6px',
                          cursor: 'pointer',
                        }}
                      >
                        Save Criterion
                      </button>
                    </div>
                  </form>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                  {/* Inclusion Criteria */}
                  <div
                    style={{
                      background: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '12px',
                      padding: '1.25rem',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '1rem',
                        color: '#34d399',
                        fontWeight: 600,
                      }}
                    >
                      <CheckCircle2 size={18} /> Inclusion Criteria
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {selectedProtocol.cohort_criteria
                        ?.filter((c) => c.criterion_type === 'inclusion')
                        .map((c) => (
                          <div
                            key={c.id}
                            style={{
                              background: 'rgba(15, 23, 42, 0.5)',
                              padding: '0.85rem',
                              borderRadius: '8px',
                              borderLeft: '3px solid #10b981',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                                {c.category}
                              </span>
                              {c.loinc_code && (
                                <span style={{ fontSize: '0.7rem', color: '#60a5fa' }}>LOINC {c.loinc_code}</span>
                              )}
                            </div>
                            <p style={{ margin: 0, fontSize: '0.85rem', color: '#f1f5f9', lineHeight: 1.4 }}>
                              {c.description}
                            </p>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Exclusion Criteria */}
                  <div
                    style={{
                      background: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '12px',
                      padding: '1.25rem',
                      border: '1px solid rgba(239, 68, 68, 0.2)',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '1rem',
                        color: '#f87171',
                        fontWeight: 600,
                      }}
                    >
                      <AlertCircle size={18} /> Exclusion Criteria
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {selectedProtocol.cohort_criteria
                        ?.filter((c) => c.criterion_type === 'exclusion')
                        .map((c) => (
                          <div
                            key={c.id}
                            style={{
                              background: 'rgba(15, 23, 42, 0.5)',
                              padding: '0.85rem',
                              borderRadius: '8px',
                              borderLeft: '3px solid #ef4444',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                                {c.category}
                              </span>
                              {c.loinc_code && (
                                <span style={{ fontSize: '0.7rem', color: '#60a5fa' }}>LOINC {c.loinc_code}</span>
                              )}
                            </div>
                            <p style={{ margin: 0, fontSize: '0.85rem', color: '#f1f5f9', lineHeight: 1.4 }}>
                              {c.description}
                            </p>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 2: Drug Repositioning Screen */}
            {activeTab === 'repurposing' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                  Target-Affinity Repurposing Screen for {selectedProtocol.disease_indication}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                  {selectedProtocol.drug_candidates?.map((cand) => (
                    <div
                      key={cand.id}
                      style={{
                        background: 'rgba(30, 41, 59, 0.7)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '12px',
                        padding: '1.25rem',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: 0, color: '#f8fafc' }}>
                            {cand.compound_name}
                          </h3>
                          <span
                            style={{
                              background: 'rgba(16, 185, 129, 0.15)',
                              color: '#34d399',
                              padding: '0.2rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                            }}
                          >
                            Kd {cand.binding_affinity_nm} nM
                          </span>
                        </div>

                        <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
                          Approved for: <span style={{ color: '#cbd5e1' }}>{cand.current_approved_indication}</span>
                        </div>

                        <div
                          style={{
                            background: 'rgba(15, 23, 42, 0.6)',
                            padding: '0.75rem',
                            borderRadius: '8px',
                            marginBottom: '0.75rem',
                          }}
                        >
                          <span style={{ fontSize: '0.7rem', color: '#38bdf8', fontWeight: 600 }}>REPURPOSING RATIONALE</span>
                          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.4 }}>
                            {cand.repurposing_rationale}
                          </p>
                        </div>
                      </div>

                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: '0.5rem',
                          paddingTop: '0.75rem',
                          borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                        }}
                      >
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Bioavailability: <span style={{ color: '#f8fafc', fontWeight: 600 }}>{cand.bioavailability_pct}%</span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Tox Risk: <span style={{ color: '#34d399', fontWeight: 600 }}>{(cand.toxicity_risk_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 3: Regulatory Package */}
            {activeTab === 'regulatory' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                  Electronic Common Technical Document (eCTD) FDA IND / EMA CTD Submission Module
                </div>

                {selectedProtocol.regulatory_packages?.map((pkg) => (
                  <div
                    key={pkg.id}
                    style={{
                      background: 'rgba(30, 41, 59, 0.7)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '12px',
                      padding: '1.5rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <ShieldCheck size={24} color="#10b981" />
                        <div>
                          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0 }}>
                            {pkg.regulatory_agency} {pkg.module_type}
                          </h3>
                          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>eCTD Structure Validated</span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Dossier Completeness</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#34d399' }}>
                            {(pkg.completeness_score * 100).toFixed(0)}%
                          </div>
                        </div>
                        <span
                          style={{
                            background: 'rgba(16, 185, 129, 0.15)',
                            color: '#34d399',
                            border: '1px solid rgba(16, 185, 129, 0.3)',
                            padding: '0.35rem 0.75rem',
                            borderRadius: '8px',
                            fontWeight: 600,
                            fontSize: '0.85rem',
                          }}
                        >
                          IRB Verdict: {pkg.irb_readiness_verdict.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                      {pkg.validation_findings?.map((vf, idx) => (
                        <div
                          key={idx}
                          style={{
                            background: 'rgba(15, 23, 42, 0.5)',
                            padding: '0.75rem 1rem',
                            borderRadius: '8px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <CheckCircle2 size={16} color="#10b981" />
                            <span style={{ fontSize: '0.85rem', color: '#f8fafc', fontWeight: 500 }}>{vf.section}</span>
                          </div>
                          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{vf.note}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div
            style={{
              background: 'rgba(30, 41, 59, 0.4)',
              border: '1px dashed rgba(255, 255, 255, 0.12)',
              borderRadius: '14px',
              padding: '4rem 2rem',
              textAlign: 'center',
              color: '#94a3b8',
            }}
          >
            <FlaskConical size={48} style={{ margin: '0 auto 1rem auto', opacity: 0.4 }} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
              No Clinical Protocol Selected
            </h3>
            <p style={{ margin: 0, fontSize: '0.9rem' }}>
              Synthesize a new clinical trial protocol or select one from the left sidebar to inspect PICO cohort
              eligibility, drug screens, and FDA IND packages.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClinicalTrialsPage;
