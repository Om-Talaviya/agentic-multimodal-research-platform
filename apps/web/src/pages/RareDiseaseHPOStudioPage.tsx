import React, { useState, useEffect } from 'react';
import { GitMerge, Activity, Sparkles, Dna, FileText, CheckCircle, Award, Stethoscope } from 'lucide-react';

interface HPOTerm {
  id: string;
  hpo_id: string;
  term_name: string;
  severity_weight: number;
  information_content: number;
}

interface CandidateGene {
  id: string;
  gene_symbol: string;
  disease_name: string;
  omim_id: string;
  semantic_similarity_score: number;
  inheritance_mode: string;
  pathogenicity_evidence: string;
  is_top_match: boolean;
}

interface DiagnosticCase {
  id: string;
  case_number: string;
  patient_id: string;
  clinical_summary: string;
  age_of_onset: string;
  top_predicted_disease: string;
  total_phenotypes_mapped: number;
  created_at: string;
  phenotypes?: HPOTerm[];
  candidate_genes?: CandidateGene[];
}

export const RareDiseaseHPOStudioPage: React.FC = () => {
  const [cases, setCases] = useState<DiagnosticCase[]>([]);
  const [selectedCase, setSelectedCase] = useState<DiagnosticCase | null>(null);
  const [caseNumber, setCaseNumber] = useState('CASE-RD-2026-101');
  const [patientId, setPatientId] = useState('PT-PEDIATRIC-088');
  const [clinicalSummary, setClinicalSummary] = useState('14-month-old infant with refractory febrile seizures and global developmental delay.');
  const [loading, setLoading] = useState(false);

  const fetchCases = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/rare-disease/cases');
      if (res.ok) {
        const data = await res.json();
        setCases(data);
        if (data.length > 0 && !selectedCase) {
          fetchDetail(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDetail = async (id: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/rare-disease/cases/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedCase(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/rare-disease/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_number: caseNumber,
          patient_id: patientId,
          clinical_summary: clinicalSummary,
          age_of_onset: 'Infantile',
          phenotypes: [
            { hpo_id: 'HP:0001250', term_name: 'Seizures' },
            { hpo_id: 'HP:0001263', term_name: 'Global developmental delay' },
            { hpo_id: 'HP:0002069', term_name: 'Bilateral tonic-clonic seizures' },
            { hpo_id: 'HP:0010818', term_name: 'Febrile seizures' },
          ],
        }),
      });
      if (res.ok) {
        await fetchCases();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-fuchsia-950/60 border border-fuchsia-500/40 rounded-xl text-fuchsia-400">
            <Stethoscope className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-fuchsia-400 to-amber-300 bg-clip-text text-transparent">
              Rare Disease Phenotype-to-Genotype Studio
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Phase 61 • Human Phenotype Ontology (HPO) semantic DAG matching, orphan disease similarity & causal gene ranking
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-fuchsia-300">
            <FileText className="w-5 h-5" /> Diagnostic Intake
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Case Number</label>
              <input
                type="text"
                value={caseNumber}
                onChange={(e) => setCaseNumber(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Patient ID</label>
              <input
                type="text"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase">Clinical Summary</label>
              <textarea
                value={clinicalSummary}
                onChange={(e) => setClinicalSummary(e.target.value)}
                rows={3}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
              />
            </div>
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-fuchsia-600 to-amber-600 hover:from-fuchsia-500 hover:to-amber-500 font-semibold rounded-lg text-white shadow-lg transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" /> {loading ? 'Matching HPO DAGs...' : 'Execute Diagnostic Matching'}
            </button>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">Diagnostic Cases</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => fetchDetail(c.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedCase?.id === c.id
                      ? 'bg-fuchsia-950/40 border-fuchsia-500/50'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{c.case_number}</span>
                    <span className="text-fuchsia-400 font-mono">{c.total_phenotypes_mapped} HPO Terms</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{c.top_predicted_disease || 'Pending'}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Candidate Genes & HPO Badges */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-fuchsia-300">
              <Activity className="w-5 h-5" /> Prioritized Rare Disease Causal Genes
            </h2>
            {selectedCase?.top_predicted_disease && (
              <span className="text-xs bg-fuchsia-950 text-fuchsia-300 px-2.5 py-1 rounded border border-fuchsia-500/40 font-semibold">
                Diagnosis: {selectedCase.top_predicted_disease}
              </span>
            )}
          </div>

          {selectedCase?.candidate_genes && selectedCase.candidate_genes.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono">
                  <tr>
                    <th className="p-3">Candidate Gene</th>
                    <th className="p-3">Orphan Disease</th>
                    <th className="p-3">OMIM</th>
                    <th className="p-3">Semantic Match</th>
                    <th className="p-3">Inheritance</th>
                    <th className="p-3">Diagnostic Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {selectedCase.candidate_genes.map((g) => (
                    <tr key={g.id} className="hover:bg-slate-950/40">
                      <td className="p-3 font-bold font-mono text-fuchsia-300 text-sm">{g.gene_symbol}</td>
                      <td className="p-3 font-semibold text-slate-200">{g.disease_name}</td>
                      <td className="p-3 font-mono text-slate-400">{g.omim_id}</td>
                      <td className="p-3 font-mono text-emerald-400 font-bold">
                        {(g.semantic_similarity_score * 100).toFixed(1)}%
                      </td>
                      <td className="p-3 text-slate-400 text-[11px]">{g.inheritance_mode}</td>
                      <td className="p-3">
                        {g.is_top_match ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/50 border border-emerald-500/40 px-2 py-0.5 rounded text-[10px]">
                            <Award className="w-3 h-3" /> Causal Gene
                          </span>
                        ) : (
                          <span className="text-slate-500 text-[10px]">Candidate</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-sm">No cases loaded. Ingest a case above.</div>
          )}

          {/* Mapped HPO Phenotype Tags */}
          {selectedCase?.phenotypes && selectedCase.phenotypes.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-800 space-y-3">
              <h3 className="text-sm font-semibold text-fuchsia-300 uppercase tracking-wider flex items-center gap-2">
                <Dna className="w-4 h-4 text-amber-400" /> Extracted Clinical HPO Phenotypes
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedCase.phenotypes.map((p) => (
                  <span key={p.id} className="bg-slate-900 border border-fuchsia-500/30 text-slate-200 px-3 py-1 rounded-lg text-xs flex items-center gap-2">
                    <span className="font-mono text-fuchsia-400 font-bold">{p.hpo_id}</span>
                    <span>{p.term_name}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
