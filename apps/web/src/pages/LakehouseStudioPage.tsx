import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  Layers,
  HardDrive,
  FileCode,
  Zap,
  Activity,
  Plus,
  Play,
  CheckCircle,
  Clock,
  Filter,
  RefreshCw,
  Table as TableIcon,
  ChevronRight,
  Code,
  Sparkles
} from 'lucide-react';

interface LakeTable {
  id: string;
  name: string;
  description: string;
  modality: 'GENOMIC' | 'PROTEOMIC' | 'IMAGING' | 'TABULAR' | 'LITERATURE';
  storage_format: string;
  schema_definition: any;
  total_records: number;
  size_bytes: number;
  created_at: string;
  partitions?: any[];
}

interface LakeMetrics {
  total_tables: number;
  total_partitions: number;
  total_records: number;
  total_bytes: number;
  total_queries: number;
}

export const LakehouseStudioPage: React.FC = () => {
  const [metrics, setMetrics] = useState<LakeMetrics>({
    total_tables: 4,
    total_partitions: 18,
    total_records: 485000,
    total_bytes: 5368709120,
    total_queries: 42,
  });

  const [tables, setTables] = useState<LakeTable[]>([
    {
      id: 'tbl-1',
      name: 'pan_cancer_tcga_rnaseq',
      description: 'TCGA Pan-Cancer single-cell and bulk RNA-seq count matrices with 1536d vector embeddings',
      modality: 'GENOMIC',
      storage_format: 'PARQUET',
      total_records: 245000,
      size_bytes: 2684354560,
      created_at: '2026-09-16T12:00:00Z',
      schema_definition: {
        columns: [
          { name: 'gene_id', type: 'VARCHAR(64)', index: 'primary' },
          { name: 'chromosome', type: 'VARCHAR(16)', index: 'btree' },
          { name: 'expression_tpm', type: 'FLOAT' },
          { name: 'embedding', type: 'VECTOR(1536)', index: 'hnsw' }
        ],
        compression: 'ZSTD'
      }
    },
    {
      id: 'tbl-2',
      name: 'alphafold_kinase_pdb_structures',
      description: 'PDB & mmCIF structural coordinates and pocket binding affinities for human kinases',
      modality: 'PROTEOMIC',
      storage_format: 'PDB',
      total_records: 65000,
      size_bytes: 1073741824,
      created_at: '2026-09-15T09:30:00Z',
      schema_definition: {
        columns: [
          { name: 'uniprot_id', type: 'VARCHAR(32)', index: 'primary' },
          { name: 'residue_count', type: 'INTEGER' },
          { name: 'binding_kd_nm', type: 'FLOAT' },
          { name: 'structure_vector', type: 'VECTOR(1536)', index: 'hnsw' }
        ]
      }
    },
    {
      id: 'tbl-3',
      name: 'nih_chest_xray_dicom_vault',
      description: 'Multi-modal volumetric DICOM scans with CLIP multimodal visual embeddings',
      modality: 'IMAGING',
      storage_format: 'DICOM',
      total_records: 125000,
      size_bytes: 1476395008,
      created_at: '2026-09-14T14:15:00Z',
      schema_definition: {
        columns: [
          { name: 'scan_id', type: 'VARCHAR(64)', index: 'primary' },
          { name: 'pathology_finding', type: 'VARCHAR(128)' },
          { name: 'multimodal_clip_vector', type: 'VECTOR(512)', index: 'hnsw' }
        ]
      }
    },
    {
      id: 'tbl-4',
      name: 'pubmed_oncology_literature_lake',
      description: 'Structured bio-entity extracted PubMed oncology papers and trial preprints',
      modality: 'LITERATURE',
      storage_format: 'JSONL',
      total_records: 50000,
      size_bytes: 134217728,
      created_at: '2026-09-13T10:00:00Z',
      schema_definition: {
        columns: [
          { name: 'pmid', type: 'VARCHAR(32)', index: 'primary' },
          { name: 'mesh_terms', type: 'ARRAY(VARCHAR)' },
          { name: 'abstract_embedding', type: 'VECTOR(1536)', index: 'hnsw' }
        ]
      }
    }
  ]);

  const [selectedTable, setSelectedTable] = useState<LakeTable | null>(tables[0]);
  const [filterModality, setFilterModality] = useState<string>('ALL');

  // Query State
  const [queryPrompt, setQueryPrompt] = useState('Identify kinase inhibitor resistance mutations in EGFR exon 20 insertions with high structural binding affinity');
  const [sqlPredicate, setSqlPredicate] = useState('significance_pvalue < 0.001 AND fold_change > 2.0');
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.75);
  const [isQuerying, setIsQuerying] = useState<boolean>(false);
  const [queryResults, setQueryResults] = useState<any | null>(null);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleRunQuery = () => {
    setIsQuerying(true);
    setTimeout(() => {
      setQueryResults({
        query_id: 'qry-' + Math.random().toString(36).substring(7),
        query_text: queryPrompt,
        matched_records_count: 6,
        execution_time_ms: 24.8,
        results: [
          {
            record_id: 'rec-panc-1011',
            table_name: 'pan_cancer_tcga_rnaseq',
            vector_similarity: 0.942,
            matched_partition: 'partition_year=2026/cohort_group=A',
            entity_attributes: {
              primary_target: 'EGFR exon 20 ins NPG',
              significance_pvalue: 0.0001,
              fold_change: 3.82,
              ic50_shift: '8.4-fold resistance',
              predicate_matched: true,
            },
            citation_uri: 's3://lakehouse-data/scientific_vault/pan_cancer_tcga_rnaseq/part-0001.parquet',
          },
          {
            record_id: 'rec-alph-1012',
            table_name: 'alphafold_kinase_pdb_structures',
            vector_similarity: 0.918,
            matched_partition: 'partition_year=2026/cohort_group=B',
            entity_attributes: {
              primary_target: 'EGFR T790M / C797S',
              binding_affinity_kd: '1.2 nM',
              rmsd_angstrom: 0.42,
              predicate_matched: true,
            },
            citation_uri: 's3://lakehouse-data/scientific_vault/alphafold_kinase_pdb_structures/part-0002.parquet',
          },
          {
            record_id: 'rec-pubm-1013',
            table_name: 'pubmed_oncology_literature_lake',
            vector_similarity: 0.885,
            matched_partition: 'partition_year=2026/cohort_group=C',
            entity_attributes: {
              primary_target: 'Mobocertinib / Osimertinib Combination',
              clinical_phase: 'Phase III Trial Cohort',
              predicate_matched: true,
            },
            citation_uri: 's3://lakehouse-data/scientific_vault/pubmed_oncology_literature_lake/part-0003.parquet',
          }
        ]
      });
      setIsQuerying(false);
    }, 600);
  };

  const getModalityColor = (modality: string) => {
    switch (modality) {
      case 'GENOMIC':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'PROTEOMIC':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'IMAGING':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'TABULAR':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    }
  };

  const filteredTables = filterModality === 'ALL'
    ? tables
    : tables.filter(t => t.modality === filterModality);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
              <Database className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-cyan-400">
                  Scientific Multimodal Data Lakehouse
                </h1>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Generation 22: Unified Lake & Hybrid Vector-SQL
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-1">
                Unified petabyte-scale storage, automated biological partitioning, and hybrid Vector + Structured SQL Semantic query execution.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => handleRunQuery()}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-indigo-500/20"
          >
            <Play className="w-4 h-4 fill-current" />
            Run Semantic Query
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Registered Tables</span>
            <TableIcon className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{metrics.total_tables}</div>
          <div className="text-xs text-indigo-400/80 mt-1">5 Scientific Modalities</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Storage Partitions</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{metrics.total_partitions}</div>
          <div className="text-xs text-cyan-400/80 mt-1">ZSTD Compressed</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Indexed Records</span>
            <HardDrive className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{(metrics.total_records / 1000).toFixed(0)}k</div>
          <div className="text-xs text-emerald-400/80 mt-1">100% Vector Indexed</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Storage Volume</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{formatBytes(metrics.total_bytes)}</div>
          <div className="text-xs text-purple-400/80 mt-1">Distributed Parquet / PDB</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Semantic Queries</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{metrics.total_queries}</div>
          <div className="text-xs text-amber-400/80 mt-1">&lt; 30ms Avg Latency</div>
        </div>
      </div>

      {/* Main Grid: Catalog Left, Hybrid Query Center/Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Multimodal Catalog (4 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Multimodal Dataset Catalog
            </h2>
            <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
              {['ALL', 'GENOMIC', 'PROTEOMIC', 'IMAGING', 'LITERATURE'].map((mod) => (
                <button
                  key={mod}
                  onClick={() => setFilterModality(mod)}
                  className={`px-2 py-1 rounded transition ${
                    filterModality === mod
                      ? 'bg-indigo-600 text-white font-medium'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {mod === 'ALL' ? 'All' : mod.substring(0, 3)}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {filteredTables.map((table) => (
              <div
                key={table.id}
                onClick={() => setSelectedTable(table)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  selectedTable?.id === table.id
                    ? 'bg-slate-900/90 border-indigo-500/50 shadow-lg shadow-indigo-500/5 ring-1 ring-indigo-500/20'
                    : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold text-slate-200">
                        {table.name}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                      {table.description}
                    </p>
                  </div>
                  <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${getModalityColor(table.modality)}`}>
                    {table.modality}
                  </span>
                </div>

                <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/60 text-xs text-slate-400">
                  <span className="flex items-center gap-1 font-mono">
                    <FileCode className="w-3.5 h-3.5 text-slate-500" />
                    {table.storage_format}
                  </span>
                  <span>{table.total_records.toLocaleString()} rows</span>
                  <span>{formatBytes(table.size_bytes)}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Schema Preview for Selected Table */}
          {selectedTable && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 mt-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Code className="w-4 h-4 text-cyan-400" />
                  Schema: {selectedTable.name}
                </span>
                <span className="text-xs text-cyan-400 font-mono">HNSW Vector Indexed</span>
              </div>
              <div className="space-y-1.5 font-mono text-xs max-h-48 overflow-y-auto">
                {selectedTable.schema_definition?.columns?.map((col: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-1.5 bg-slate-950/60 rounded border border-slate-800/50">
                    <span className="text-slate-300">{col.name}</span>
                    <span className="text-indigo-400">{col.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Hybrid Semantic Vector + SQL Query Console (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2 text-slate-100">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                Hybrid Semantic Vector + Structured SQL Engine
              </h2>
              <span className="px-2 py-0.5 text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full font-mono">
                Predicate Pushdown AST
              </span>
            </div>

            {/* Prompt Input */}
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
                  Natural Language Semantic Query (Dense Embeddings)
                </label>
                <div className="relative">
                  <textarea
                    value={queryPrompt}
                    onChange={(e) => setQueryPrompt(e.target.value)}
                    rows={2}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-sans resize-none"
                    placeholder="Describe scientific search intent across genomic, structural, or literature assets..."
                  />
                  <Search className="w-4 h-4 text-slate-500 absolute right-3 bottom-3" />
                </div>
              </div>

              {/* SQL Predicate Pushdown */}
              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Filter className="w-3.5 h-3.5 text-indigo-400" />
                  SQL WHERE Predicate Filter Pushdown (Optional)
                </label>
                <input
                  type="text"
                  value={sqlPredicate}
                  onChange={(e) => setSqlPredicate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-cyan-300 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
                  placeholder="e.g. significance_pvalue < 0.001 AND fold_change > 2.0"
                />
              </div>

              {/* Vector Threshold Slider */}
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-medium text-slate-400">Cosine Threshold:</span>
                  <input
                    type="range"
                    min="0.5"
                    max="0.99"
                    step="0.01"
                    value={similarityThreshold}
                    onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                    className="w-32 accent-indigo-500 cursor-pointer"
                  />
                  <span className="text-xs font-mono text-indigo-400 font-semibold">
                    {similarityThreshold.toFixed(2)}
                  </span>
                </div>

                <button
                  onClick={handleRunQuery}
                  disabled={isQuerying}
                  className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                >
                  {isQuerying ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Evaluating AST...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      Execute Query
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results Console */}
          {queryResults && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-base font-semibold text-slate-200">
                    Execution Results: {queryResults.matched_records_count} Records Matched
                  </h3>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{queryResults.execution_time_ms} ms</span>
                </div>
              </div>

              <div className="space-y-3">
                {queryResults.results.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 bg-slate-950/70 border border-slate-800/80 rounded-lg hover:border-slate-700 transition space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-indigo-400">
                          {item.record_id}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          [{item.table_name}]
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded text-xs font-mono">
                        <span>Cosine:</span>
                        <span className="font-bold">{(item.vector_similarity * 100).toFixed(1)}%</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-900/50 p-2.5 rounded border border-slate-800/50 text-slate-300">
                      <div>
                        <span className="text-slate-500">Target / Entity: </span>
                        <span className="text-cyan-300 font-medium">{item.entity_attributes?.primary_target}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Partition: </span>
                        <span className="text-purple-300">{item.matched_partition}</span>
                      </div>
                    </div>

                    <div className="text-[11px] text-slate-500 font-mono truncate">
                      Storage URI: {item.citation_uri}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LakehouseStudioPage;
