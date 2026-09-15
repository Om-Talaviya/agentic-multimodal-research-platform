import React, { useState, useEffect } from 'react';
import {
  Scissors,
  Dna,
  AlertCircle,
  CheckCircle2,
  Download,
  Copy,
  Plus,
  RefreshCw,
  Sparkles,
  Layers,
  ShieldAlert,
  FileCode,
} from 'lucide-react';
import { api } from '../services/api';

interface OffTargetSite {
  id: string;
  locus_name: string;
  chromosome: string;
  target_sequence: string;
  mismatches_count: number;
  cfd_off_target_score: number;
  is_exonic: boolean;
  annotation: string;
}

interface BaseEditingProfile {
  id: string;
  editor_type: string;
  target_nucleotide: string;
  edited_nucleotide: string;
  window_start: number;
  window_end: number;
  editing_efficiency: number;
  bystander_mutation_risk: boolean;
}

interface GuideRNA {
  id: string;
  guide_sequence: string;
  pam_sequence: string;
  strand: string;
  start_pos: number;
  end_pos: number;
  gc_content: number;
  on_target_score: number;
  off_target_cfd_score: number;
  composite_score: number;
  azimuth_efficiency: number;
  tier: string;
  golden_gate_top_oligo: string;
  golden_gate_bottom_oligo: string;
  off_targets?: OffTargetSite[];
  base_editing_profiles?: BaseEditingProfile[];
}

interface CRISPRDesign {
  id: string;
  target_gene: string;
  target_sequence: string;
  cas_type: string;
  pam_pattern: string;
  organism: string;
  total_guides_evaluated: number;
  top_guide_efficiency: number;
  metadata_json?: Record<string, any>;
  guides?: GuideRNA[];
  guides_count?: number;
  created_at?: string;
}

const SAMPLE_SEQUENCES: Record<string, { gene: string; desc: string; seq: string; cas: string }> = {
  PCSK9: {
    gene: 'PCSK9',
    desc: 'Human PCSK9 Exon 1 — Low-density lipoprotein receptor degradation target',
    cas: 'SpCas9',
    seq: 'ATGGGCACCGTCAGCTCCAGGCGGTCCTGGTGGCCGCTGCCACTGCTGCTGCTGCTGCTGCTGCTCCTGGGTCCCGCGGGCGCCCGTGCGCAGGAGGACGAGGACGGCGACTACGAGGAGCTGGTGCTAGCCTTGCGTTCCGAGGAGGACGGCCTGGCCGAAGCACCCGAGCACGGAACCACAGCCACCTTCCACCGCTGCGCCAAGGATCCGTGGCGGTTGCCCGGCACCTAC',
  },
  BCL11A: {
    gene: 'BCL11A',
    desc: 'Human BCL11A Erythroid Enhancer (+58 GATA1 site) — Fetal hemoglobin reactivation',
    cas: 'SpCas9',
    seq: 'CTAACAGGTTGCTTCTCCTCCCTCTGCCTCCCCACCTCCTCCTCTCCTCTCCCTTTTCTCTCTCTTTTCTCCCTCCCCTCTCTCCCTCTTTCTTTCCCTTTTTTCCCTCTTTCCTTTTTTTTTTCTTCCCTTTCTCTCCCTTTCTTTCCCTTTCCTTGATCAGTGAGTCACACACACACACACACACACACACACACACACACACACACTCACTCACTCACTCT',
  },
  VEGFA: {
    gene: 'VEGFA',
    desc: 'Human VEGFA Exon 3 — Angiogenesis and vascular permeability factor',
    cas: 'Cas12a_Cpf1',
    seq: 'ATGAACTTTCTGCTGTCTTGGGTGCATTGGAGCCTTGCCTTGCTGCTCTACCTCCACCATGCCAAGTGGTCCCAGGCTGCACCCATGGCAGAAGGAGGAGGGCAGAATCATCACGAAGTGGTGAAGTTCATGGATGTCTATCAGCGCAGCTACTGCCATCCAATCGAGACCCTGGTGGACATCTTCCAGGAGTACCCTGATGAGATCGAGTACATCTTCAAG',
  },
};

export const CRISPRStudioPage: React.FC = () => {
  const [designs, setDesigns] = useState<CRISPRDesign[]>([]);
  const [selectedDesign, setSelectedDesign] = useState<CRISPRDesign | null>(null);
  const [selectedGuide, setSelectedGuide] = useState<GuideRNA | null>(null);
  const [activeTab, setActiveTab] = useState<'guides' | 'sequence_map' | 'off_targets' | 'base_editing' | 'cloning'>('guides');
  const [loading, setLoading] = useState<boolean>(true);
  const [designing, setDesigning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showDesignModal, setShowDesignModal] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Design Form State
  const [targetGene, setTargetGene] = useState<string>('PCSK9');
  const [targetSequence, setTargetSequence] = useState<string>(SAMPLE_SEQUENCES.PCSK9.seq);
  const [casType, setCasType] = useState<string>('SpCas9');
  const [organism, setOrganism] = useState<string>('Homo sapiens');
  const [description, setDescription] = useState<string>('Targeted CRISPR-Cas9 knockout targeting Exon 1 for hypercholesterolemia');
  const [maxGuides, setMaxGuides] = useState<number>(15);

  const fetchDesigns = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/crispr/designs');
      const items: CRISPRDesign[] = res.data.items || [];
      setDesigns(items);
      if (items.length > 0 && (!selectedDesign || !items.find(d => d.id === selectedDesign.id))) {
        await loadDesignDetails(items[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch CRISPR designs');
    } finally {
      setLoading(false);
    }
  };

  const loadDesignDetails = async (id: string) => {
    try {
      const res = await api.get(`/crispr/designs/${id}`);
      setSelectedDesign(res.data);
      if (res.data.guides && res.data.guides.length > 0) {
        setSelectedGuide(res.data.guides[0]);
      } else {
        setSelectedGuide(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load design details');
    }
  };

  useEffect(() => {
    fetchDesigns();
  }, []);

  const handleCreateDesign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setDesigning(true);
      setError(null);
      const payload = {
        target_gene: targetGene.trim(),
        target_sequence: targetSequence.trim(),
        cas_type: casType,
        organism: organism.trim(),
        description: description.trim(),
        max_guides: maxGuides,
      };
      const res = await api.post('/crispr/design', payload);
      setShowDesignModal(false);
      await fetchDesigns();
      if (res.data.design_id) {
        await loadDesignDetails(res.data.design_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Guide RNA design failed');
    } finally {
      setDesigning(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const downloadGenBank = async () => {
    if (!selectedDesign) return;
    try {
      const res = await api.get(`/crispr/designs/${selectedDesign.id}/export-genbank`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedDesign.target_gene}_CRISPR_Guides.gb`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError('Failed to export GenBank file');
    }
  };

  const handleSampleSelect = (key: string) => {
    const s = SAMPLE_SEQUENCES[key];
    if (s) {
      setTargetGene(s.gene);
      setTargetSequence(s.seq);
      setCasType(s.cas);
      setDescription(s.desc);
    }
  };

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case 'TIER_1':
        return <span style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700, backgroundColor: 'rgba(234, 179, 8, 0.2)', color: '#eab308', border: '1px solid #eab308' }}>⭐ TIER 1 (Optimal)</span>;
      case 'TIER_2':
        return <span style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700, backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', border: '1px solid #3b82f6' }}>✨ TIER 2 (Viable)</span>;
      default:
        return <span style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700, backgroundColor: 'rgba(156, 163, 175, 0.2)', color: '#9ca3af', border: '1px solid #6b7280' }}>TIER 3</span>;
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ padding: '10px', borderRadius: '12px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
              <Scissors size={28} />
            </div>
            <div>
              <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0 }}>CRISPR & Synthetic Biology Studio</h1>
              <p style={{ margin: '4px 0 0', color: 'var(--text-secondary, #94a3b8)', fontSize: '14px' }}>
                PAM-directed candidate guide RNA scanner, Azimuth 2.0 on-target efficiency, genome-wide CFD off-target profiler, and precision base editing windows.
              </p>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setShowDesignModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#10b981',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 18px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
            }}
          >
            <Plus size={18} /> New CRISPR Campaign
          </button>
          <button
            onClick={fetchDesigns}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'var(--card-bg, #1e293b)',
              color: 'var(--text-primary, #f8fafc)',
              border: '1px solid var(--border-color, #334155)',
              borderRadius: '8px',
              padding: '10px 14px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Campaign Selector + Active Design Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px' }}>
        {/* Left Sidebar: Campaigns List */}
        <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '820px', overflowY: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color, #334155)', paddingBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              CRISPR Campaigns ({designs.length})
            </span>
          </div>

          {loading && designs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>Loading targeting campaigns...</div>
          ) : designs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8', fontSize: '13px' }}>
              No CRISPR campaigns yet. Launch one to evaluate target loci and gRNAs.
            </div>
          ) : (
            designs.map(d => {
              const isSelected = selectedDesign?.id === d.id;
              return (
                <div
                  key={d.id}
                  onClick={() => loadDesignDetails(d.id)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: isSelected ? '1px solid #10b981' : '1px solid var(--border-color, #334155)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>{d.target_gene}</span>
                    <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', backgroundColor: '#334155', color: '#38bdf8' }}>{d.cas_type}</span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>{d.organism}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#cbd5e1' }}>
                    <span>{d.guides_count ?? d.total_guides_evaluated} Guides</span>
                    <span style={{ color: '#10b981', fontWeight: 600 }}>Top Eff: {d.top_guide_efficiency.toFixed(1)}%</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Workspace: Selected Campaign Analysis */}
        {selectedDesign ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Target Overview Card */}
            <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2 style={{ fontSize: '22px', fontWeight: 700, margin: 0 }}>Target Locus: {selectedDesign.target_gene}</h2>
                    <span style={{ padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 600, backgroundColor: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', border: '1px solid #38bdf8' }}>
                      {selectedDesign.cas_type} (PAM: {selectedDesign.pam_pattern})
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>
                    Host: <strong>{selectedDesign.organism}</strong> &bull; Length: <strong>{selectedDesign.target_sequence.length} bp</strong> &bull; Total Candidates: <strong>{selectedDesign.total_guides_evaluated}</strong>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={downloadGenBank}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      color: '#f8fafc',
                      border: '1px solid var(--border-color, #334155)',
                      borderRadius: '8px',
                      padding: '8px 14px',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    <Download size={15} /> Export GenBank (.gb)
                  </button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color, #334155)', paddingBottom: '8px', flexWrap: 'wrap' }}>
                {[
                  { key: 'guides', label: `Candidate gRNAs (${selectedDesign.guides?.length || 0})`, icon: Layers },
                  { key: 'sequence_map', label: 'Protospacer Sequence Map', icon: Dna },
                  { key: 'off_targets', label: `Genome Off-Targets (${selectedGuide?.off_targets?.length || 0})`, icon: ShieldAlert },
                  { key: 'base_editing', label: 'Base Editing Windows (ABE/CBE)', icon: Sparkles },
                  { key: 'cloning', label: 'Golden Gate Oligo Specs', icon: FileCode },
                ].map(tab => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.key;
                  return (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: isActive ? '#10b981' : 'transparent',
                        color: isActive ? '#ffffff' : '#94a3b8',
                        fontWeight: isActive ? 600 : 500,
                        fontSize: '13px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <Icon size={16} />
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* TAB 1: Candidates Table */}
            {activeTab === 'guides' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Layers size={18} color="#10b981" /> Ranked Guide RNA Candidates (Azimuth 2.0 & CFD Scoring)
                </h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                        <th style={{ padding: '10px 8px' }}>Rank</th>
                        <th style={{ padding: '10px 8px' }}>Guide Sequence (5' &rarr; 3')</th>
                        <th style={{ padding: '10px 8px' }}>PAM</th>
                        <th style={{ padding: '10px 8px' }}>Strand</th>
                        <th style={{ padding: '10px 8px' }}>Locus</th>
                        <th style={{ padding: '10px 8px' }}>GC%</th>
                        <th style={{ padding: '10px 8px' }}>Azimuth Eff.</th>
                        <th style={{ padding: '10px 8px' }}>CFD Specificity</th>
                        <th style={{ padding: '10px 8px' }}>Tier</th>
                        <th style={{ padding: '10px 8px' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedDesign.guides?.map((g, idx) => {
                        const isSelected = selectedGuide?.id === g.id;
                        return (
                          <tr
                            key={g.id}
                            style={{
                              borderBottom: '1px solid #334155',
                              backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                            }}
                          >
                            <td style={{ padding: '10px 8px', fontWeight: 700, color: idx === 0 ? '#eab308' : '#cbd5e1' }}>#{idx + 1}</td>
                            <td style={{ padding: '10px 8px', fontFamily: 'monospace', fontWeight: 600, letterSpacing: '0.5px', color: '#38bdf8' }}>
                              {g.guide_sequence}
                            </td>
                            <td style={{ padding: '10px 8px', fontFamily: 'monospace', fontWeight: 700, color: '#f59e0b' }}>{g.pam_sequence}</td>
                            <td style={{ padding: '10px 8px', color: g.strand === '+' ? '#10b981' : '#ec4899', fontWeight: 700 }}>{g.strand}</td>
                            <td style={{ padding: '10px 8px', color: '#94a3b8' }}>{g.start_pos}..{g.end_pos}</td>
                            <td style={{ padding: '10px 8px', color: g.gc_content >= 40 && g.gc_content <= 60 ? '#10b981' : '#f59e0b' }}>{g.gc_content.toFixed(1)}%</td>
                            <td style={{ padding: '10px 8px', fontWeight: 700, color: g.azimuth_efficiency >= 70 ? '#10b981' : '#60a5fa' }}>
                              {g.azimuth_efficiency.toFixed(1)}%
                            </td>
                            <td style={{ padding: '10px 8px', fontWeight: 700, color: g.off_target_cfd_score >= 80 ? '#10b981' : '#f59e0b' }}>
                              {g.off_target_cfd_score.toFixed(1)}
                            </td>
                            <td style={{ padding: '10px 8px' }}>{getTierBadge(g.tier)}</td>
                            <td style={{ padding: '10px 8px' }}>
                              <button
                                onClick={() => setSelectedGuide(g)}
                                style={{
                                  padding: '4px 10px',
                                  fontSize: '11px',
                                  borderRadius: '6px',
                                  backgroundColor: isSelected ? '#10b981' : '#334155',
                                  color: '#ffffff',
                                  border: 'none',
                                  cursor: 'pointer',
                                  fontWeight: 600,
                                }}
                              >
                                {isSelected ? 'Inspecting' : 'Inspect'}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB 2: Protospacer Sequence Map */}
            {activeTab === 'sequence_map' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Dna size={18} color="#10b981" /> Target Sequence Protospacer Architecture
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
                  Target Sense Strand (5' &rarr; 3') with annotated PAM coordinates. Click on any guide in the candidate table to highlight its binding footprint.
                </p>

                {selectedGuide && (
                  <div style={{ backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px solid #38bdf8', borderRadius: '8px', padding: '12px 16px', marginBottom: '16px' }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#38bdf8', marginBottom: '4px' }}>
                      Active Guide Footprint: {selectedGuide.guide_sequence} (Strand {selectedGuide.strand}, Pos {selectedGuide.start_pos}..{selectedGuide.end_pos})
                    </div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
                      PAM: <strong>{selectedGuide.pam_sequence}</strong> &bull; Azimuth Efficiency: <strong>{selectedGuide.azimuth_efficiency.toFixed(1)}%</strong> &bull; CFD Specificity: <strong>{selectedGuide.off_target_cfd_score.toFixed(1)}</strong>
                    </div>
                  </div>
                )}

                <div style={{ backgroundColor: '#0f172a', borderRadius: '8px', padding: '16px', fontFamily: 'monospace', fontSize: '14px', lineHeight: '24px', letterSpacing: '1px', wordBreak: 'break-all' }}>
                  {selectedDesign.target_sequence.split('').map((char, index) => {
                    const pos = index + 1;
                    const inGuide = selectedGuide && pos >= selectedGuide.start_pos && pos <= selectedGuide.end_pos;
                    return (
                      <span
                        key={index}
                        style={{
                          backgroundColor: inGuide ? 'rgba(16, 185, 129, 0.4)' : 'transparent',
                          color: inGuide ? '#10b981' : '#f8fafc',
                          fontWeight: inGuide ? 700 : 400,
                          borderBottom: inGuide ? '2px solid #10b981' : 'none',
                          padding: '2px 1px',
                        }}
                        title={`Pos: ${pos}, Base: ${char}`}
                      >
                        {char}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 3: Genome-Wide Off-Targets */}
            {activeTab === 'off_targets' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ShieldAlert size={18} color="#ef4444" /> Off-Target Cleavage Profile for Selected Guide
                  </h3>
                  {selectedGuide && (
                    <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                      Guide: <code style={{ color: '#38bdf8' }}>{selectedGuide.guide_sequence}</code>
                    </span>
                  )}
                </div>

                {selectedGuide?.off_targets && selectedGuide.off_targets.length > 0 ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                          <th style={{ padding: '10px 8px' }}>Chromosome</th>
                          <th style={{ padding: '10px 8px' }}>Locus / Gene</th>
                          <th style={{ padding: '10px 8px' }}>Off-Target Sequence</th>
                          <th style={{ padding: '10px 8px' }}>Mismatches</th>
                          <th style={{ padding: '10px 8px' }}>CFD Cleavage Probability</th>
                          <th style={{ padding: '10px 8px' }}>Region Type</th>
                          <th style={{ padding: '10px 8px' }}>Annotation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedGuide.off_targets.map(ot => (
                          <tr key={ot.id} style={{ borderBottom: '1px solid #334155' }}>
                            <td style={{ padding: '10px 8px', fontWeight: 600, color: '#f8fafc' }}>{ot.chromosome}</td>
                            <td style={{ padding: '10px 8px', color: '#38bdf8' }}>{ot.locus_name}</td>
                            <td style={{ padding: '10px 8px', fontFamily: 'monospace', color: '#cbd5e1' }}>{ot.target_sequence}</td>
                            <td style={{ padding: '10px 8px', fontWeight: 700, color: ot.mismatches_count <= 1 ? '#ef4444' : '#f59e0b' }}>
                              {ot.mismatches_count} bp
                            </td>
                            <td style={{ padding: '10px 8px', fontWeight: 700, color: ot.cfd_off_target_score > 5.0 ? '#ef4444' : '#10b981' }}>
                              {ot.cfd_off_target_score.toFixed(2)}%
                            </td>
                            <td style={{ padding: '10px 8px' }}>
                              {ot.is_exonic ? (
                                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5', border: '1px solid #ef4444' }}>
                                  EXONIC (High Risk)
                                </span>
                              ) : (
                                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600, backgroundColor: 'rgba(100, 116, 139, 0.2)', color: '#94a3b8' }}>
                                  Intergenic / Intron
                                </span>
                              )}
                            </td>
                            <td style={{ padding: '10px 8px', color: '#94a3b8', fontSize: '12px' }}>{ot.annotation}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                    No significant predicted off-target loci (&le;3 mismatches) found across reference genome.
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: Precision Base Editing Windows */}
            {activeTab === 'base_editing' && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={18} color="#eab308" /> Precision Base Editing (ABE & CBE) Deamination Profiles
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
                  Evaluates Adenine Base Editors (ABE8e / ABE9: A &rarr; G) and Cytosine Base Editors (BE4max / evoAPOBEC: C &rarr; T) across the canonical editing window (positions 4–8 of the protospacer).
                </p>

                {selectedGuide?.base_editing_profiles && selectedGuide.base_editing_profiles.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
                    {selectedGuide.base_editing_profiles.map(be => (
                      <div
                        key={be.id}
                        style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.03)',
                          border: '1px solid var(--border-color, #334155)',
                          borderRadius: '10px',
                          padding: '16px',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <span style={{ fontWeight: 700, fontSize: '15px', color: '#f8fafc' }}>{be.editor_type}</span>
                          <span style={{ fontSize: '12px', fontWeight: 600, padding: '2px 8px', borderRadius: '4px', backgroundColor: '#334155', color: '#38bdf8' }}>
                            {be.target_nucleotide} &rarr; {be.edited_nucleotide}
                          </span>
                        </div>
                        <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '8px' }}>
                          Activity Window: Positions <strong>{be.window_start}–{be.window_end}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', marginBottom: '6px' }}>
                          <span style={{ color: '#94a3b8' }}>Deamination Efficiency:</span>
                          <span style={{ fontWeight: 700, color: '#10b981' }}>{be.editing_efficiency.toFixed(1)}%</span>
                        </div>
                        <div style={{ width: '100%', height: '6px', backgroundColor: '#334155', borderRadius: '3px', overflow: 'hidden', marginBottom: '10px' }}>
                          <div style={{ width: `${be.editing_efficiency}%`, height: '100%', backgroundColor: '#10b981' }} />
                        </div>
                        <div style={{ fontSize: '12px', color: be.bystander_mutation_risk ? '#f59e0b' : '#94a3b8' }}>
                          Bystander Risk: {be.bystander_mutation_risk ? '⚠️ Multiple target bases in window' : '✅ Single pure edit window'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                    No base editing target bases (A or C) present in canonical window (positions 4–8) for this guide.
                  </div>
                )}
              </div>
            )}

            {/* TAB 5: Cloning & Oligo Synthesis Sheet */}
            {activeTab === 'cloning' && selectedGuide && (
              <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileCode size={18} color="#38bdf8" /> Golden Gate BsmBI / BsaI Cloning Oligo Spec
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '16px' }}>
                  Ready-to-order DNA oligonucleotides with compatible sticky-end overhangs for seamless cloning into standard CRISPR Cas9 plasmids (e.g., PX459, lentiCRISPR v2).
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
                  {/* Top Oligo */}
                  <div style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8' }}>Top Strand Oligo (5' &rarr; 3')</span>
                      <button
                        onClick={() => copyToClipboard(selectedGuide.golden_gate_top_oligo, 'top')}
                        style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'none', border: 'none', color: copiedKey === 'top' ? '#10b981' : '#94a3b8', cursor: 'pointer', fontSize: '12px' }}
                      >
                        {copiedKey === 'top' ? <CheckCircle2 size={14} /> : <Copy size={14} />} {copiedKey === 'top' ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <div style={{ fontFamily: 'monospace', fontSize: '14px', color: '#f8fafc', wordBreak: 'break-all' }}>
                      <span style={{ color: '#ec4899', fontWeight: 700 }}>CACC</span>{selectedGuide.golden_gate_top_oligo.slice(4)}
                    </div>
                  </div>

                  {/* Bottom Oligo */}
                  <div style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8' }}>Bottom Strand Oligo (5' &rarr; 3')</span>
                      <button
                        onClick={() => copyToClipboard(selectedGuide.golden_gate_bottom_oligo, 'bottom')}
                        style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'none', border: 'none', color: copiedKey === 'bottom' ? '#10b981' : '#94a3b8', cursor: 'pointer', fontSize: '12px' }}
                      >
                        {copiedKey === 'bottom' ? <CheckCircle2 size={14} /> : <Copy size={14} />} {copiedKey === 'bottom' ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <div style={{ fontFamily: 'monospace', fontSize: '14px', color: '#f8fafc', wordBreak: 'break-all' }}>
                      <span style={{ color: '#ec4899', fontWeight: 700 }}>AAAC</span>{selectedGuide.golden_gate_bottom_oligo.slice(4)}
                    </div>
                  </div>
                </div>

                {/* Duplex Annealing Protocol */}
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.08)', border: '1px solid #10b981', borderRadius: '8px', padding: '16px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 700, color: '#10b981', margin: '0 0 10px' }}>Standard Duplex Annealing & Ligation Protocol</h4>
                  <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#cbd5e1', lineHeight: '22px' }}>
                    <li>Resuspend oligos to 100 &mu;M in sterile water or TE buffer.</li>
                    <li>Mix 10 &mu;L Top Oligo (100 &mu;M) + 10 &mu;L Bottom Oligo (100 &mu;M) + 80 &mu;L Water (Final concentration: 10 &mu;M duplex).</li>
                    <li>Heat to <strong>95&deg;C for 5 minutes</strong> in a thermocycler.</li>
                    <li>Ramp down from 95&deg;C to 25&deg;C at <strong>-5&deg;C / min</strong> (or cool slowly at room temperature for 45 min).</li>
                    <li>Dilute annealed duplex <strong>1:200</strong> in sterile water for Golden Gate ligation into BsmBI/BsaI digested backbone.</li>
                  </ol>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '12px', padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
            Select or launch a CRISPR campaign to begin guide RNA exploration.
          </div>
        )}
      </div>

      {/* Modal: New CRISPR Campaign */}
      {showDesignModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ backgroundColor: 'var(--card-bg, #1e293b)', border: '1px solid var(--border-color, #334155)', borderRadius: '14px', width: '100%', maxWidth: '680px', maxHeight: '90vh', overflowY: 'auto', padding: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Scissors size={22} color="#10b981" /> Launch CRISPR Guide RNA Targeting Campaign
            </h2>

            {/* Preloaded Sample Sequence Chips */}
            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Load Pre-configured Therapeutic Target:</span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {Object.keys(SAMPLE_SEQUENCES).map(key => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleSampleSelect(key)}
                    style={{
                      padding: '4px 10px',
                      fontSize: '12px',
                      borderRadius: '6px',
                      backgroundColor: targetGene === SAMPLE_SEQUENCES[key].gene ? '#10b981' : '#334155',
                      color: '#ffffff',
                      border: 'none',
                      cursor: 'pointer',
                      fontWeight: 600,
                    }}
                  >
                    {SAMPLE_SEQUENCES[key].gene} ({SAMPLE_SEQUENCES[key].cas})
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleCreateDesign} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Target Gene Symbol</label>
                  <input
                    type="text"
                    required
                    value={targetGene}
                    onChange={e => setTargetGene(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>CRISPR Nuclease Type</label>
                  <select
                    value={casType}
                    onChange={e => setCasType(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  >
                    <option value="SpCas9">SpCas9 (PAM: NGG, 20 nt spacer)</option>
                    <option value="Cas12a_Cpf1">Cas12a / Cpf1 (PAM: TTTV, 23 nt spacer)</option>
                    <option value="xCas9">xCas9 (PAM: NG, Broad PAM)</option>
                    <option value="SaCas9">SaCas9 (PAM: NNGRRT, Compact Cas)</option>
                    <option value="Cas9_HF1">Cas9-HF1 (High Fidelity SpCas9)</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Target DNA Sense Sequence (5' &rarr; 3')</label>
                <textarea
                  required
                  rows={4}
                  value={targetSequence}
                  onChange={e => setTargetSequence(e.target.value)}
                  placeholder="Paste DNA sequence (A, C, G, T)..."
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '12px', fontFamily: 'monospace' }}
                />
                <span style={{ fontSize: '11px', color: '#94a3b8' }}>Sequence Length: {targetSequence.trim().length} bp</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Host Organism</label>
                  <input
                    type="text"
                    value={organism}
                    onChange={e => setOrganism(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Max Candidate Guides</label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={maxGuides}
                    onChange={e => setMaxGuides(parseInt(e.target.value) || 15)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' }}>Campaign Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowDesignModal(false)}
                  style={{ padding: '8px 16px', borderRadius: '6px', border: '1px solid #334155', backgroundColor: 'transparent', color: '#94a3b8', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={designing}
                  style={{
                    padding: '8px 20px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: '#10b981',
                    color: '#ffffff',
                    fontWeight: 600,
                    cursor: designing ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {designing ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
                  {designing ? 'Analyzing Loci...' : 'Design Guides'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
