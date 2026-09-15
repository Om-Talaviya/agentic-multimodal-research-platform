import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Atom,
  ChevronRight,
  Compass,
  Copy,
  Dna,
  Download,
  Eye,
  Microscope,
  Play,
  RefreshCw,
  RotateCcw,
  Scale,
  Sparkles,
  Zap,
} from 'lucide-react';
import { api } from '../services/api';

interface BindingPocket {
  id: string;
  pocket_index: number;
  druggability_score: number;
  volume_cubic_angstrom: number;
  surface_area_angstrom2: number;
  key_residues_json: string[];
  center_coordinates_json: { x?: number; y?: number; z?: number };
}

interface DockingPose {
  id: string;
  pocket_id: string;
  ligand_name: string;
  binding_affinity_kcal_mol: number;
  rmsd_angstrom: number;
  hydrogen_bonds_count: number;
  pi_stacking_interactions: number;
  pose_coordinates_json: any;
  created_at?: string;
}

interface MutationStability {
  id: string;
  wildtype_residue: string;
  position: number;
  mutant_residue: string;
  delta_delta_g_kcal_mol: number;
  stability_verdict: string;
  pathogenicity_score: number;
}

interface MolecularStructure {
  id: string;
  uniprot_id: string;
  gene_name: string;
  organism: string;
  sequence: string;
  mean_plddt_score: number;
  resolution_angstrom?: number;
  structure_source: string;
  pdb_coordinate_data?: string;
  secondary_structure_summary?: {
    alpha_helix_pct?: number;
    beta_sheet_pct?: number;
    random_coil_pct?: number;
    very_high_plddt_pct?: number;
    confident_plddt_pct?: number;
    low_plddt_pct?: number;
  };
  binding_pockets?: BindingPocket[];
  docking_poses?: DockingPose[];
  mutations?: MutationStability[];
  created_at?: string;
}

export const MolecularStructurePage: React.FC = () => {
  const [structures, setStructures] = useState<MolecularStructure[]>([]);
  const [selectedStructure, setSelectedStructure] = useState<MolecularStructure | null>(null);
  const [activeTab, setActiveTab] = useState<'3d' | 'pockets' | 'docking' | 'mutations' | 'pdb'>('3d');
  const [renderMode, setRenderMode] = useState<'cartoon' | 'ribbon' | 'backbone' | 'spacefill'>('cartoon');
  const [rotationAngle, setRotationAngle] = useState<number>(35);
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [loading, setLoading] = useState<boolean>(true);
  const [predicting, setPredicting] = useState<boolean>(false);
  const [docking, setDocking] = useState<boolean>(false);
  const [mutating, setMutating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Prediction Form State
  const [uniprotId, setUniprotId] = useState('Q9BYF1');
  const [geneName, setGeneName] = useState('PCSK9');
  const [structureSource, setStructureSource] = useState('AlphaFold3');

  // Docking Form State
  const [selectedPocketId, setSelectedPocketId] = useState<string>('');
  const [ligandName, setLigandName] = useState('Evolocumab Mimetic Small Molecule (EpiBlock-01)');

  // Mutation Form State
  const [wtResidue, setWtResidue] = useState('D');
  const [mutPosition, setMutPosition] = useState(374);
  const [mutResidue, setMutResidue] = useState('Y');

  const fetchStructures = async () => {
    try {
      setLoading(true);
      const res = await api.get('/molecular/structures');
      const list: MolecularStructure[] = res.data || [];
      setStructures(list);
      if (list.length > 0) {
        const fullRes = await api.get(`/molecular/structures/${list[0].id}`);
        setSelectedStructure(fullRes.data);
        if (fullRes.data.binding_pockets && fullRes.data.binding_pockets.length > 0) {
          setSelectedPocketId(fullRes.data.binding_pockets[0].id);
        }
      } else {
        setSelectedStructure(null);
      }
      setError(null);
    } catch (err: any) {
      setError('Failed to fetch molecular structures. Verify backend connectivity.');
    } finally {
      setLoading(false);
    }
  };

  const selectStructure = async (id: string) => {
    try {
      setLoading(true);
      const res = await api.get(`/molecular/structures/${id}`);
      setSelectedStructure(res.data);
      if (res.data.binding_pockets && res.data.binding_pockets.length > 0) {
        setSelectedPocketId(res.data.binding_pockets[0].id);
      }
      setError(null);
    } catch (err: any) {
      setError('Failed to load structure details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStructures();
  }, []);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setPredicting(true);
      setError(null);
      const res = await api.post('/molecular/predict', {
        uniprot_id: uniprotId,
        gene_name: geneName,
        structure_source: structureSource,
      });

      const fullRes = await api.get(`/molecular/structures/${res.data.id}`);
      setStructures((prev) => [fullRes.data, ...prev]);
      setSelectedStructure(fullRes.data);
      if (fullRes.data.binding_pockets && fullRes.data.binding_pockets.length > 0) {
        setSelectedPocketId(fullRes.data.binding_pockets[0].id);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Structure prediction failed.');
    } finally {
      setPredicting(false);
    }
  };

  const handleDock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStructure || !selectedPocketId) return;
    try {
      setDocking(true);
      setError(null);
      await api.post(`/molecular/structures/${selectedStructure.id}/dock`, {
        pocket_id: selectedPocketId,
        ligand_name: ligandName,
      });

      // Refresh structure details
      const fullRes = await api.get(`/molecular/structures/${selectedStructure.id}`);
      setSelectedStructure(fullRes.data);
      setActiveTab('docking');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Ligand docking simulation failed.');
    } finally {
      setDocking(false);
    }
  };

  const handleMutate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStructure) return;
    try {
      setMutating(true);
      setError(null);
      await api.post(`/molecular/structures/${selectedStructure.id}/mutate`, {
        wildtype_residue: wtResidue,
        position: Number(mutPosition),
        mutant_residue: mutResidue,
      });

      const fullRes = await api.get(`/molecular/structures/${selectedStructure.id}`);
      setSelectedStructure(fullRes.data);
      setActiveTab('mutations');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Mutational scan failed.');
    } finally {
      setMutating(false);
    }
  };

  const handleDownloadPdb = () => {
    if (!selectedStructure) return;
    const blob = new Blob([selectedStructure.pdb_coordinate_data || ''], { type: 'chemical/x-pdb' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedStructure.gene_name}_${selectedStructure.uniprot_id}.pdb`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopyPdb = () => {
    if (!selectedStructure?.pdb_coordinate_data) return;
    navigator.clipboard.writeText(selectedStructure.pdb_coordinate_data);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingBottom: '3rem' }}>
      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
          borderRadius: '1rem',
          padding: '1.75rem 2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.36)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div
            style={{
              width: '3.5rem',
              height: '3.5rem',
              borderRadius: '1rem',
              background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(16, 185, 129, 0.4)',
            }}
          >
            <Dna size={28} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                Bio-Molecular Structure & Protein Folding Studio
              </h1>
              <span
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                Generation 12 • Phase 38
              </span>
            </div>
            <p style={{ margin: '0.35rem 0 0 0', color: '#94a3b8', fontSize: '0.9rem', maxWidth: '750px' }}>
              AlphaFold3 / ESMFold 3D protein coordinate prediction, per-residue pLDDT confidence mapping, catalytic binding pocket detection, and in-silico ligand docking.
            </p>
          </div>
        </div>

        <button
          onClick={fetchStructures}
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.6rem 1rem',
            borderRadius: '0.5rem',
            backgroundColor: 'rgba(51, 65, 85, 0.8)',
            color: '#e2e8f0',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            cursor: 'pointer',
            fontWeight: 500,
            fontSize: '0.875rem',
          }}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Refresh Structures
        </button>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '0.75rem',
            padding: '1rem',
            color: '#fca5a5',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Left Sidebar: Controls & Catalog */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Prediction Synthesis Card */}
          <div
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.7)',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '1.25rem',
            }}
          >
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: 600, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={16} color="#34d399" />
              Predict 3D Protein Structure
            </h3>
            <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  UniProt ID
                </label>
                <input
                  type="text"
                  value={uniprotId}
                  onChange={(e) => setUniprotId(e.target.value)}
                  placeholder="e.g. Q9BYF1, Q99250, P02766"
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  Gene Symbol
                </label>
                <input
                  type="text"
                  value={geneName}
                  onChange={(e) => setGeneName(e.target.value)}
                  placeholder="e.g. PCSK9, Cas9, TTR"
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                  Folding Prediction Model
                </label>
                <select
                  value={structureSource}
                  onChange={(e) => setStructureSource(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '0.375rem',
                    padding: '0.5rem 0.75rem',
                    color: '#f8fafc',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="AlphaFold3">AlphaFold3 (DeepMind)</option>
                  <option value="ESMFold">ESMFold (Meta AI)</option>
                  <option value="PDB_Experimental">PDB Experimental (X-Ray / Cryo-EM)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={predicting}
                style={{
                  backgroundColor: '#10b981',
                  color: '#0f172a',
                  border: 'none',
                  borderRadius: '0.375rem',
                  padding: '0.65rem 1rem',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  marginTop: '0.5rem',
                }}
              >
                {predicting ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
                {predicting ? 'Predicting 3D Coordinates...' : 'Fold & Detect Pockets'}
              </button>
            </form>
          </div>

          {/* Structures Catalog */}
          <div
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.7)',
              borderRadius: '0.75rem',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '1.25rem',
              maxHeight: '380px',
              overflowY: 'auto',
            }}
          >
            <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
              Target Proteins ({structures.length})
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {structures.map((s) => {
                const isSelected = selectedStructure?.id === s.id;
                return (
                  <div
                    key={s.id}
                    onClick={() => selectStructure(s.id)}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(15, 23, 42, 0.5)',
                      border: isSelected ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(255, 255, 255, 0.05)',
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.9rem', color: isSelected ? '#34d399' : '#e2e8f0' }}>
                        {s.gene_name}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8', backgroundColor: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.4rem', borderRadius: '0.25rem' }}>
                        {s.uniprot_id}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                      <span>{s.structure_source}</span>
                      <span style={{ color: s.mean_plddt_score >= 85 ? '#34d399' : '#fbbf24', fontWeight: 600 }}>
                        {s.mean_plddt_score.toFixed(1)} pLDDT
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Main Structure Viewer */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {selectedStructure ? (
            <>
              {/* Telemetry Scorecards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                  gap: '1rem',
                }}
              >
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Activity size={24} color="#34d399" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Mean pLDDT</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedStructure.mean_plddt_score.toFixed(1)} / 100
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Scale size={24} color="#38bdf8" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Resolution / Model</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedStructure.resolution_angstrom?.toFixed(2)} Å ({selectedStructure.structure_source})
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Compass size={24} color="#f59e0b" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Binding Pockets</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedStructure.binding_pockets?.length || 0} Predicted Sites
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.6)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                  }}
                >
                  <Atom size={24} color="#a855f7" />
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Secondary Structure</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedStructure.secondary_structure_summary?.alpha_helix_pct || 42}% α / {selectedStructure.secondary_structure_summary?.beta_sheet_pct || 28}% β
                    </div>
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div style={{ display: 'flex', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', gap: '1rem' }}>
                <button
                  onClick={() => setActiveTab('3d')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === '3d' ? '2px solid #10b981' : '2px solid transparent',
                    color: activeTab === '3d' ? '#34d399' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Eye size={16} />
                  3D Molecular Explorer
                </button>

                <button
                  onClick={() => setActiveTab('pockets')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'pockets' ? '2px solid #10b981' : '2px solid transparent',
                    color: activeTab === 'pockets' ? '#34d399' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Compass size={16} />
                  Binding Pockets ({selectedStructure.binding_pockets?.length || 0})
                </button>

                <button
                  onClick={() => setActiveTab('docking')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'docking' ? '2px solid #10b981' : '2px solid transparent',
                    color: activeTab === 'docking' ? '#34d399' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Microscope size={16} />
                  Ligand Docking ({selectedStructure.docking_poses?.length || 0})
                </button>

                <button
                  onClick={() => setActiveTab('mutations')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'mutations' ? '2px solid #10b981' : '2px solid transparent',
                    color: activeTab === 'mutations' ? '#34d399' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Zap size={16} />
                  Mutational Stability ({selectedStructure.mutations?.length || 0})
                </button>

                <button
                  onClick={() => setActiveTab('pdb')}
                  style={{
                    padding: '0.65rem 1rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === 'pdb' ? '2px solid #10b981' : '2px solid transparent',
                    color: activeTab === 'pdb' ? '#34d399' : '#94a3b8',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <Download size={16} />
                  PDB Coordinates
                </button>
              </div>

              {/* Tab 1: 3D Molecular Canvas Visualizer */}
              {activeTab === '3d' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  {/* Canvas Toolbar */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {(['cartoon', 'ribbon', 'backbone', 'spacefill'] as const).map((mode) => (
                        <button
                          key={mode}
                          onClick={() => setRenderMode(mode)}
                          style={{
                            padding: '0.35rem 0.75rem',
                            borderRadius: '0.375rem',
                            backgroundColor: renderMode === mode ? '#10b981' : 'rgba(15, 23, 42, 0.6)',
                            color: renderMode === mode ? '#0f172a' : '#cbd5e1',
                            border: 'none',
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            textTransform: 'capitalize',
                            cursor: 'pointer',
                          }}
                        >
                          {mode}
                        </button>
                      ))}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <button
                        onClick={() => setRotationAngle((prev) => (prev + 45) % 360)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          padding: '0.35rem 0.75rem',
                          backgroundColor: 'rgba(51, 65, 85, 0.8)',
                          color: '#f8fafc',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.75rem',
                        }}
                      >
                        <RotateCcw size={13} />
                        Rotate ({rotationAngle}°)
                      </button>

                      <button
                        onClick={() => setZoomLevel((prev) => (prev >= 150 ? 100 : prev + 25))}
                        style={{
                          padding: '0.35rem 0.75rem',
                          backgroundColor: 'rgba(51, 65, 85, 0.8)',
                          color: '#f8fafc',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.75rem',
                        }}
                      >
                        Zoom: {zoomLevel}%
                      </button>
                    </div>
                  </div>

                  {/* 3D Visual Rendering Canvas Stage */}
                  <div
                    style={{
                      height: '420px',
                      backgroundColor: 'rgba(10, 15, 29, 0.95)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      position: 'relative',
                      overflow: 'hidden',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {/* SVG 3D Protein Helix/Ribbon Simulation */}
                    <svg
                      width="100%"
                      height="100%"
                      viewBox="0 0 600 400"
                      style={{
                        transform: `scale(${zoomLevel / 100}) rotate(${rotationAngle}deg)`,
                        transition: 'transform 0.4s ease-out',
                      }}
                    >
                      <defs>
                        <linearGradient id="plddtGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#0284c7" />
                          <stop offset="35%" stopColor="#38bdf8" />
                          <stop offset="70%" stopColor="#34d399" />
                          <stop offset="90%" stopColor="#fbbf24" />
                          <stop offset="100%" stopColor="#f87171" />
                        </linearGradient>
                        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                          <feGaussianBlur stdDeviation="3" result="blur" />
                          <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                      </defs>

                      {/* Main Helix 1 */}
                      <path
                        d="M 120 200 Q 180 80, 240 200 T 360 200 T 480 200"
                        fill="none"
                        stroke="url(#plddtGradient)"
                        strokeWidth={renderMode === 'cartoon' ? '12' : renderMode === 'spacefill' ? '24' : '4'}
                        strokeLinecap="round"
                        filter="url(#glow)"
                      />

                      {/* Secondary Beta Sheet Strand */}
                      <path
                        d="M 160 260 L 260 260 L 360 280 L 440 240"
                        fill="none"
                        stroke="#38bdf8"
                        strokeWidth={renderMode === 'cartoon' ? '10' : '4'}
                        strokeDasharray={renderMode === 'backbone' ? '5,5' : 'none'}
                        strokeLinecap="square"
                      />

                      {/* Catalytic Binding Pocket 1 Overlay */}
                      {selectedStructure.binding_pockets && selectedStructure.binding_pockets.length > 0 && (
                        <g>
                          <circle cx="280" cy="180" r="32" fill="rgba(245, 158, 11, 0.25)" stroke="#fbbf24" strokeWidth="2" strokeDasharray="4,4" />
                          <text x="280" y="185" fill="#fef08a" fontSize="11" textAnchor="middle" fontWeight="bold">
                            Pocket 1 (ASP374)
                          </text>
                        </g>
                      )}

                      {/* Simulated Atom Nodes for spacefill / backbone */}
                      {renderMode === 'spacefill' && (
                        <>
                          <circle cx="180" cy="120" r="14" fill="#38bdf8" opacity="0.8" />
                          <circle cx="240" cy="200" r="16" fill="#0284c7" opacity="0.8" />
                          <circle cx="300" cy="150" r="15" fill="#34d399" opacity="0.8" />
                          <circle cx="360" cy="200" r="14" fill="#fbbf24" opacity="0.8" />
                          <circle cx="420" cy="160" r="13" fill="#0284c7" opacity="0.8" />
                        </>
                      )}
                    </svg>

                    {/* pLDDT Confidence Color Spectrum Bar */}
                    <div
                      style={{
                        position: 'absolute',
                        bottom: '1rem',
                        left: '1rem',
                        backgroundColor: 'rgba(15, 23, 42, 0.85)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        padding: '0.6rem 1rem',
                        borderRadius: '0.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.35rem',
                      }}
                    >
                      <div style={{ fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600 }}>
                        AlphaFold pLDDT Model Confidence
                      </div>
                      <div style={{ display: 'flex', gap: '0.4rem', fontSize: '0.65rem' }}>
                        <span style={{ color: '#0284c7', fontWeight: 600 }}>■ &gt;90 (Very High)</span>
                        <span style={{ color: '#38bdf8', fontWeight: 600 }}>■ 70-90 (Confident)</span>
                        <span style={{ color: '#fbbf24', fontWeight: 600 }}>■ 50-70 (Low)</span>
                        <span style={{ color: '#f87171', fontWeight: 600 }}>■ &lt;50 (Disordered)</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Binding Pockets */}
              {activeTab === 'pockets' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#f8fafc' }}>
                    Predicted Active Site Cavities & Binding Pockets
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {selectedStructure.binding_pockets?.map((pocket) => (
                      <div
                        key={pocket.id}
                        style={{
                          backgroundColor: 'rgba(15, 23, 42, 0.6)',
                          borderRadius: '0.5rem',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          padding: '1.25rem',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '1rem',
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                            <span style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
                              Binding Pocket #{pocket.pocket_index}
                            </span>
                            <span
                              style={{
                                backgroundColor: pocket.druggability_score >= 0.8 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                color: pocket.druggability_score >= 0.8 ? '#34d399' : '#fbbf24',
                                padding: '0.15rem 0.5rem',
                                borderRadius: '0.25rem',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                              }}
                            >
                              Druggability: {pocket.druggability_score.toFixed(2)}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                            Volume: <strong>{pocket.volume_cubic_angstrom.toFixed(1)} Å³</strong> | Surface Area: <strong>{pocket.surface_area_angstrom2.toFixed(1)} Å²</strong>
                          </div>
                          <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                            {pocket.key_residues_json?.map((res, rIdx) => (
                              <span
                                key={rIdx}
                                style={{
                                  backgroundColor: 'rgba(56, 189, 248, 0.15)',
                                  color: '#38bdf8',
                                  fontSize: '0.7rem',
                                  padding: '0.15rem 0.4rem',
                                  borderRadius: '0.25rem',
                                  fontWeight: 600,
                                }}
                              >
                                {res}
                              </span>
                            ))}
                          </div>
                        </div>

                        <button
                          onClick={() => {
                            setSelectedPocketId(pocket.id);
                            setActiveTab('docking');
                          }}
                          style={{
                            padding: '0.5rem 1rem',
                            backgroundColor: '#10b981',
                            color: '#0f172a',
                            border: 'none',
                            borderRadius: '0.375rem',
                            fontWeight: 600,
                            fontSize: '0.8rem',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.4rem',
                          }}
                        >
                          Dock Inhibitor <ChevronRight size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Ligand Docking Studio */}
              {activeTab === 'docking' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Docking Form */}
                  <div
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '1.25rem',
                    }}
                  >
                    <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
                      Run In-Silico Ligand Docking Simulation
                    </h4>
                    <form onSubmit={handleDock} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                      <div style={{ flex: 1, minWidth: '220px' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                          Target Pocket
                        </label>
                        <select
                          value={selectedPocketId}
                          onChange={(e) => setSelectedPocketId(e.target.value)}
                          style={{
                            width: '100%',
                            backgroundColor: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '0.375rem',
                            padding: '0.5rem 0.75rem',
                            color: '#f8fafc',
                            fontSize: '0.85rem',
                          }}
                        >
                          {selectedStructure.binding_pockets?.map((p) => (
                            <option key={p.id} value={p.id}>
                              Pocket #{p.pocket_index} (Druggability: {p.druggability_score.toFixed(2)})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div style={{ flex: 2, minWidth: '280px' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                          Ligand / Small Molecule Name
                        </label>
                        <input
                          type="text"
                          value={ligandName}
                          onChange={(e) => setLigandName(e.target.value)}
                          style={{
                            width: '100%',
                            backgroundColor: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '0.375rem',
                            padding: '0.5rem 0.75rem',
                            color: '#f8fafc',
                            fontSize: '0.85rem',
                          }}
                          required
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={docking}
                        style={{
                          padding: '0.55rem 1.25rem',
                          backgroundColor: '#06b6d4',
                          color: '#0f172a',
                          border: 'none',
                          borderRadius: '0.375rem',
                          fontWeight: 600,
                          fontSize: '0.85rem',
                          cursor: 'pointer',
                        }}
                      >
                        {docking ? 'Simulating Docking...' : 'Calculate Affinity'}
                      </button>
                    </form>
                  </div>

                  {/* Docked Poses Table */}
                  <div
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '1.5rem',
                    }}
                  >
                    <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
                      Computed Ligand Docking Poses & Binding Thermodynamics
                    </h4>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8' }}>
                            <th style={{ padding: '0.6rem' }}>Ligand Name</th>
                            <th style={{ padding: '0.6rem' }}>Binding Affinity (ΔG)</th>
                            <th style={{ padding: '0.6rem' }}>RMSD</th>
                            <th style={{ padding: '0.6rem' }}>H-Bonds</th>
                            <th style={{ padding: '0.6rem' }}>π-Stacking</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedStructure.docking_poses?.map((dp) => (
                            <tr key={dp.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: '#e2e8f0' }}>
                              <td style={{ padding: '0.6rem', fontWeight: 600, color: '#38bdf8' }}>{dp.ligand_name}</td>
                              <td style={{ padding: '0.6rem', fontWeight: 700, color: '#34d399' }}>
                                {dp.binding_affinity_kcal_mol.toFixed(2)} kcal/mol
                              </td>
                              <td style={{ padding: '0.6rem' }}>{dp.rmsd_angstrom.toFixed(2)} Å</td>
                              <td style={{ padding: '0.6rem' }}>{dp.hydrogen_bonds_count} Bonds</td>
                              <td style={{ padding: '0.6rem' }}>{dp.pi_stacking_interactions} Interactions</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: Mutational Stability */}
              {activeTab === 'mutations' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Mutation Form */}
                  <div
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '1.25rem',
                    }}
                  >
                    <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
                      In-Silico Mutational Stability Scan (ΔΔG Free Energy)
                    </h4>
                    <form onSubmit={handleMutate} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                      <div style={{ width: '120px' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                          Wildtype AA
                        </label>
                        <input
                          type="text"
                          maxLength={1}
                          value={wtResidue}
                          onChange={(e) => setWtResidue(e.target.value.toUpperCase())}
                          style={{
                            width: '100%',
                            backgroundColor: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '0.375rem',
                            padding: '0.5rem 0.75rem',
                            color: '#f8fafc',
                            fontSize: '0.85rem',
                            textAlign: 'center',
                            fontWeight: 700,
                          }}
                          required
                        />
                      </div>

                      <div style={{ width: '140px' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                          Residue Position
                        </label>
                        <input
                          type="number"
                          value={mutPosition}
                          onChange={(e) => setMutPosition(Number(e.target.value))}
                          style={{
                            width: '100%',
                            backgroundColor: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '0.375rem',
                            padding: '0.5rem 0.75rem',
                            color: '#f8fafc',
                            fontSize: '0.85rem',
                          }}
                          required
                        />
                      </div>

                      <div style={{ width: '120px' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                          Mutant AA
                        </label>
                        <input
                          type="text"
                          maxLength={1}
                          value={mutResidue}
                          onChange={(e) => setMutResidue(e.target.value.toUpperCase())}
                          style={{
                            width: '100%',
                            backgroundColor: 'rgba(15, 23, 42, 0.8)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '0.375rem',
                            padding: '0.5rem 0.75rem',
                            color: '#f8fafc',
                            fontSize: '0.85rem',
                            textAlign: 'center',
                            fontWeight: 700,
                          }}
                          required
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={mutating}
                        style={{
                          padding: '0.55rem 1.25rem',
                          backgroundColor: '#a855f7',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '0.375rem',
                          fontWeight: 600,
                          fontSize: '0.85rem',
                          cursor: 'pointer',
                        }}
                      >
                        {mutating ? 'Scanning ΔΔG...' : 'Scan Mutation'}
                      </button>
                    </form>
                  </div>

                  {/* Mutation Results Table */}
                  <div
                    style={{
                      backgroundColor: 'rgba(30, 41, 59, 0.7)',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '1.5rem',
                    }}
                  >
                    <h4 style={{ margin: '0 0 1rem 0', color: '#f8fafc', fontSize: '1rem' }}>
                      Mutational Scanning Stability Matrix
                    </h4>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8' }}>
                            <th style={{ padding: '0.6rem' }}>Variant</th>
                            <th style={{ padding: '0.6rem' }}>Position</th>
                            <th style={{ padding: '0.6rem' }}>ΔΔG Stability</th>
                            <th style={{ padding: '0.6rem' }}>Verdict</th>
                            <th style={{ padding: '0.6rem' }}>Pathogenicity Score</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedStructure.mutations?.map((m) => (
                            <tr key={m.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: '#e2e8f0' }}>
                              <td style={{ padding: '0.6rem', fontWeight: 700, color: '#f8fafc' }}>
                                {m.wildtype_residue}{m.position}{m.mutant_residue}
                              </td>
                              <td style={{ padding: '0.6rem' }}>Residue #{m.position}</td>
                              <td
                                style={{
                                  padding: '0.6rem',
                                  fontWeight: 700,
                                  color: m.delta_delta_g_kcal_mol <= 0 ? '#34d399' : '#f87171',
                                }}
                              >
                                {m.delta_delta_g_kcal_mol > 0 ? '+' : ''}{m.delta_delta_g_kcal_mol.toFixed(2)} kcal/mol
                              </td>
                              <td style={{ padding: '0.6rem' }}>
                                <span
                                  style={{
                                    backgroundColor: m.stability_verdict === 'stabilizing' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                    color: m.stability_verdict === 'stabilizing' ? '#34d399' : '#f87171',
                                    padding: '0.15rem 0.5rem',
                                    borderRadius: '0.25rem',
                                    fontSize: '0.75rem',
                                    fontWeight: 600,
                                    textTransform: 'capitalize',
                                  }}
                                >
                                  {m.stability_verdict}
                                </span>
                              </td>
                              <td style={{ padding: '0.6rem' }}>
                                <span style={{ color: m.pathogenicity_score >= 0.7 ? '#f87171' : '#38bdf8', fontWeight: 600 }}>
                                  {m.pathogenicity_score.toFixed(2)}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: PDB Coordinates */}
              {activeTab === 'pdb' && (
                <div
                  style={{
                    backgroundColor: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '0.75rem',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    padding: '1.5rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h4 style={{ margin: 0, color: '#f8fafc', fontSize: '1rem' }}>
                      Standard PDB Coordinate Format Data
                    </h4>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={handleCopyPdb}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          padding: '0.4rem 0.75rem',
                          backgroundColor: 'rgba(51, 65, 85, 0.8)',
                          color: '#f8fafc',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                        }}
                      >
                        <Copy size={14} />
                        {copied ? 'Copied PDB!' : 'Copy PDB'}
                      </button>
                      <button
                        onClick={handleDownloadPdb}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          padding: '0.4rem 0.75rem',
                          backgroundColor: '#10b981',
                          color: '#0f172a',
                          border: 'none',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                        }}
                      >
                        <Download size={14} />
                        Download .PDB
                      </button>
                    </div>
                  </div>

                  <pre
                    style={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      padding: '1.25rem',
                      borderRadius: '0.5rem',
                      color: '#34d399',
                      fontFamily: 'monospace',
                      fontSize: '0.8rem',
                      lineHeight: 1.5,
                      overflowX: 'auto',
                      maxHeight: '450px',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                    }}
                  >
                    <code>{selectedStructure.pdb_coordinate_data || '# No PDB coordinates available'}</code>
                  </pre>
                </div>
              )}
            </>
          ) : (
            <div
              style={{
                backgroundColor: 'rgba(30, 41, 59, 0.7)',
                borderRadius: '0.75rem',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: '3rem',
                textAlign: 'center',
                color: '#94a3b8',
              }}
            >
              <Dna size={48} color="#10b981" style={{ margin: '0 auto 1rem auto', display: 'block' }} />
              <h3>No Protein Structure Selected</h3>
              <p>Predict a new 3D structure or select one from the catalog to inspect binding pockets and docking.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
