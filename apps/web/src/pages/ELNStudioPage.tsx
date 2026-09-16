import React, { useState } from 'react';
import {
  BookOpen,
  Plus,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Clock,
  User,
  Tag,
  Atom,
  Table,
  LineChart,
  Lock,
  History,
  Check,
  Edit3,
  Sparkles,
  ChevronRight
} from 'lucide-react';

interface Notebook {
  id: string;
  title: string;
  author_id: string;
  status: 'DRAFT' | 'UNDER_REVIEW' | 'WITNESSED';
  tags: string[];
  cfr_part11_signed: boolean;
  witness_signature?: any;
  created_at: string;
  blocks_count: number;
}

export const ELNStudioPage: React.FC = () => {
  const [notebooks, setNotebooks] = useState<Notebook[]>([
    {
      id: 'nb-1',
      title: 'CRISPR-Cas9 Exon 20 Knock-in Protocol & In-Vitro Validation',
      author_id: 'dr_jane_doe',
      status: 'WITNESSED',
      tags: ['CRISPR', 'GeneEditing', 'Exon20', 'HEK293T'],
      cfr_part11_signed: true,
      witness_signature: {
        witness_id: 'dr_marcus_vance (Principal Investigator)',
        timestamp: '2026-09-16T14:30:00Z',
        sha256_hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
        compliance_standard: 'FDA 21 CFR Part 11 / ALCOA+'
      },
      created_at: '2026-09-16T10:00:00Z',
      blocks_count: 4
    },
    {
      id: 'nb-2',
      title: 'Small Molecule EGFR Kinase Inhibitor Binding Assay & IC50 Profiling',
      author_id: 'dr_alex_chen',
      status: 'UNDER_REVIEW',
      tags: ['Kinase', 'SMILES', 'DoseResponse', 'Biochemistry'],
      cfr_part11_signed: false,
      created_at: '2026-09-15T16:20:00Z',
      blocks_count: 3
    }
  ]);

  const [selectedNotebook, setSelectedNotebook] = useState<Notebook>(notebooks[0]);

  const [blocks, setBlocks] = useState<any[]>([
    {
      id: 'blk-1',
      block_type: 'PROTOCOL_STEP',
      content_json: {
        step_number: 1,
        title: 'Cell Seeding & Ribonucleoprotein Transfection',
        instructions: 'Seed HEK293T cells at 2.5e5 cells/well in a 24-well plate. Deliver 50pmol Cas9-RNP complex via electroporation.',
        parameters: { temperature_c: 37.0, co2_percent: 5.0, electroporation_voltage: 1150, pulse_width_ms: 20 },
        status: 'COMPLETED'
      }
    },
    {
      id: 'blk-2',
      block_type: 'MOLECULAR_SMILES',
      content_json: {
        smiles: 'CC(C)N1CCN(CC1)C(=O)c2cc3ccccc3[nH]2',
        formula_hint: 'C17H22N4O',
        molecular_weight: 298.38,
        visualizer_mode: '2D_DEPICTION'
      }
    },
    {
      id: 'blk-3',
      block_type: 'CHART_WIDGET',
      content_json: {
        chart_type: 'DOSE_RESPONSE_CURVE',
        title: 'In-Vitro Knock-in Efficiency vs HDR Donor Concentration',
        x_axis_label: 'HDR Donor Oligo (pmol)',
        y_axis_label: 'Target Integration Efficiency (%)',
        data_points: [
          { x: 10, y: 12.4 },
          { x: 25, y: 28.6 },
          { x: 50, y: 54.2 },
          { x: 100, y: 78.9 }
        ]
      }
    },
    {
      id: 'blk-4',
      block_type: 'MARKDOWN',
      content_json: {
        text: 'Observational Note: High cellular viability (>92%) retained post-electroporation with minimal off-target cleavage at validated surrogate loci.'
      }
    }
  ]);

  const [auditTrails, setAuditTrails] = useState<any[]>([
    {
      id: 'aud-4',
      actor_id: 'dr_marcus_vance',
      action: 'WITNESS_SIGN',
      diff_payload: { compliance: 'FDA 21 CFR Part 11 Witness Signature Applied' },
      cryptographic_hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
      timestamp: '2026-09-16T14:30:00Z'
    },
    {
      id: 'aud-3',
      actor_id: 'dr_jane_doe',
      action: 'BLOCK_INSERT',
      diff_payload: { type: 'CHART_WIDGET', title: 'In-Vitro Knock-in Efficiency' },
      cryptographic_hash: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
      timestamp: '2026-09-16T12:15:00Z'
    },
    {
      id: 'aud-2',
      actor_id: 'dr_jane_doe',
      action: 'BLOCK_INSERT',
      diff_payload: { type: 'MOLECULAR_SMILES', smiles: 'CC(C)N1CCN...' },
      cryptographic_hash: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
      timestamp: '2026-09-16T10:45:00Z'
    },
    {
      id: 'aud-1',
      actor_id: 'dr_jane_doe',
      action: 'NOTEBOOK_CREATE',
      diff_payload: { title: 'CRISPR-Cas9 Exon 20 Knock-in Protocol' },
      cryptographic_hash: 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d',
      timestamp: '2026-09-16T10:00:00Z'
    }
  ]);

  const [isSigning, setIsSigning] = useState(false);
  const [witnessStatement, setWitnessStatement] = useState('I certify that I have reviewed the experimental procedure and raw data recorded in this electronic notebook.');

  const handleSign = () => {
    setIsSigning(true);
    setTimeout(() => {
      setSelectedNotebook({
        ...selectedNotebook,
        status: 'WITNESSED',
        cfr_part11_signed: true,
        witness_signature: {
          witness_id: 'dr_current_user (Witness)',
          timestamp: new Date().toISOString(),
          sha256_hash: 'a8b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4c5d6e7f8091',
          compliance_standard: 'FDA 21 CFR Part 11 / ALCOA+'
        }
      });
      setIsSigning(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-teal-500/20 to-emerald-500/20 rounded-xl border border-teal-500/30 text-teal-400">
            <BookOpen className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-emerald-300 to-cyan-400">
                Electronic Lab Notebook (ELN)
              </h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Generation 23: FDA 21 CFR Part 11 Compliant
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Immutable ALCOA+ audit trails, modular protocol blocks, molecular structures, and cryptographic digital witness signatures.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {!selectedNotebook.cfr_part11_signed ? (
            <button
              onClick={handleSign}
              disabled={isSigning}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-teal-500/20"
            >
              <ShieldCheck className="w-4 h-4" />
              Apply Witness Signature
            </button>
          ) : (
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm font-mono">
              <CheckCircle2 className="w-4 h-4" />
              21 CFR Part 11 Witnessed
            </div>
          )}
        </div>
      </div>

      {/* Grid: Notebooks list Left (4 cols), Main Canvas & Blocks Center (5 cols), Audit Trail Right (3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Notebooks (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <FileText className="w-4 h-4 text-teal-400" />
              Notebook Experiments
            </h2>
            <button className="p-1 text-slate-400 hover:text-white rounded bg-slate-900 border border-slate-800">
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3">
            {notebooks.map((nb) => (
              <div
                key={nb.id}
                onClick={() => setSelectedNotebook(nb)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  selectedNotebook?.id === nb.id
                    ? 'bg-slate-900/90 border-teal-500/50 shadow-lg shadow-teal-500/5 ring-1 ring-teal-500/20'
                    : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold text-slate-200 line-clamp-2">
                    {nb.title}
                  </h3>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full font-mono ${
                    nb.status === 'WITNESSED'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {nb.status}
                  </span>
                </div>

                <div className="flex items-center gap-2 mt-3 text-xs text-slate-400">
                  <User className="w-3.5 h-3.5 text-slate-500" />
                  <span>{nb.author_id}</span>
                </div>

                <div className="flex flex-wrap gap-1 mt-2.5">
                  {nb.tags.map((t) => (
                    <span key={t} className="px-1.5 py-0.5 bg-slate-950 text-[10px] text-teal-300/80 rounded border border-slate-800">
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Column: Modular Notebook Blocks (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-xl font-bold text-slate-100">
                {selectedNotebook.title}
              </h2>
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-400 font-mono">
                <span className="flex items-center gap-1">
                  <User className="w-3.5 h-3.5 text-teal-400" />
                  Author: {selectedNotebook.author_id}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  {new Date(selectedNotebook.created_at).toLocaleDateString()}
                </span>
                {selectedNotebook.cfr_part11_signed && (
                  <span className="flex items-center gap-1 text-emerald-400">
                    <Lock className="w-3.5 h-3.5" />
                    Immutable Sealed
                  </span>
                )}
              </div>
            </div>

            {/* Block Items */}
            <div className="space-y-4">
              {blocks.map((b, idx) => (
                <div
                  key={b.id}
                  className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg space-y-3"
                >
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                    <span className="flex items-center gap-1.5 font-semibold text-teal-400">
                      {b.block_type === 'PROTOCOL_STEP' && <CheckCircle2 className="w-3.5 h-3.5" />}
                      {b.block_type === 'MOLECULAR_SMILES' && <Atom className="w-3.5 h-3.5" />}
                      {b.block_type === 'CHART_WIDGET' && <LineChart className="w-3.5 h-3.5" />}
                      {b.block_type === 'MARKDOWN' && <FileText className="w-3.5 h-3.5" />}
                      Block #{idx + 1}: {b.block_type}
                    </span>
                  </div>

                  {b.block_type === 'PROTOCOL_STEP' && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold text-slate-200">
                        {b.content_json.title}
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {b.content_json.instructions}
                      </p>
                      <div className="flex flex-wrap gap-2 pt-2">
                        {Object.entries(b.content_json.parameters).map(([k, v]) => (
                          <span key={k} className="px-2 py-0.5 bg-slate-900 border border-slate-800 rounded text-[11px] font-mono text-teal-300">
                            {k}: {String(v)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {b.block_type === 'MOLECULAR_SMILES' && (
                    <div className="p-3 bg-slate-900/60 rounded border border-slate-800 space-y-1 font-mono text-xs">
                      <div className="text-slate-400">SMILES String:</div>
                      <div className="text-cyan-300 font-bold break-all">{b.content_json.smiles}</div>
                      <div className="text-[11px] text-slate-500 pt-1">MW: {b.content_json.molecular_weight} g/mol | Formula: {b.content_json.formula_hint}</div>
                    </div>
                  )}

                  {b.block_type === 'CHART_WIDGET' && (
                    <div className="space-y-2">
                      <div className="text-xs font-semibold text-slate-300">{b.content_json.title}</div>
                      <div className="grid grid-cols-4 gap-2 pt-1 font-mono text-xs">
                        {b.content_json.data_points.map((pt: any, pidx: number) => (
                          <div key={pidx} className="p-2 bg-slate-900 rounded border border-slate-800 text-center">
                            <div className="text-slate-500 text-[10px]">{pt.x} pmol</div>
                            <div className="text-emerald-400 font-bold">{pt.y}%</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {b.block_type === 'MARKDOWN' && (
                    <div className="text-xs text-slate-300 italic bg-slate-900/40 p-3 rounded border border-slate-800/60">
                      {b.content_json.text}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Witness Stamp */}
            {selectedNotebook.witness_signature && (
              <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-xl space-y-2 font-mono text-xs">
                <div className="flex items-center gap-2 text-emerald-400 font-bold">
                  <ShieldCheck className="w-4 h-4" />
                  21 CFR PART 11 DIGITAL WITNESS SIGNATURE
                </div>
                <div className="text-slate-300 text-[11px]">
                  Signer: {selectedNotebook.witness_signature.witness_id}
                </div>
                <div className="text-slate-400 text-[11px] truncate">
                  SHA-256 Digest: {selectedNotebook.witness_signature.sha256_hash}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: ALCOA+ Audit Trail (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <History className="w-4 h-4 text-emerald-400" />
              Audit Trail (Part 11)
            </h2>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Tamper-Evident
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            {auditTrails.map((a) => (
              <div key={a.id} className="p-3 bg-slate-900/50 border border-slate-800 rounded-lg space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-teal-400">{a.action}</span>
                  <span className="text-slate-500">{new Date(a.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-slate-300 text-[11px]">Actor: {a.actor_id}</div>
                <div className="text-[10px] text-slate-500 truncate" title={a.cryptographic_hash}>
                  Hash: {a.cryptographic_hash.substring(0, 16)}...
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ELNStudioPage;
