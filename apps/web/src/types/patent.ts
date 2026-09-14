export type PatentJurisdiction = 'USPTO' | 'EPO' | 'WIPO' | 'JPO' | 'CNIPA' | 'GLOBAL';
export type FTOVerdict = 'clear' | 'caution' | 'high_risk' | 'blocked';
export type PriorArtVerdict = 'anticipates_102' | 'obvious_103' | 'distinguishable' | 'non_infringing';

export interface PatentClaim {
  id: string;
  claim_number: number;
  claim_type: 'independent' | 'dependent';
  claim_text: string;
  parsed_elements?: Array<{
    element_id: string;
    element_text: string;
    keywords: string[];
  }>;
}

export interface PatentDocument {
  id: string;
  patent_number: string;
  title: string;
  abstract?: string;
  assignee: string;
  filing_date?: string;
  publication_date?: string;
  cpc_classes: string[];
  status: 'granted' | 'pending' | 'expired';
  claims_count: number;
  claims?: PatentClaim[];
}

export interface PriorArtEvaluation {
  id: string;
  target_invention_claim: string;
  novelty_score: number;
  obviousness_score: number;
  overlap_ratio: number;
  verdict: PriorArtVerdict;
  detailed_rationale: string;
  mitigation_strategy?: string;
  claim_chart?: Array<{
    element_id: string;
    target_limitation: string;
    status: 'anticipated' | 'obvious_variant' | 'novel_distinction';
    overlap_score: number;
    matched_terms: string[];
  }>;
  created_at: string;
}

export interface FreedomToOperateReport {
  id: string;
  total_examined_patents: number;
  high_risk_claims_count: number;
  medium_risk_claims_count: number;
  fto_clearance_percentage: number;
  summary_assessment: string;
  white_space_opportunities: Array<{
    domain_subfield: string;
    opportunity_description: string;
    patentability_index: number;
  }>;
  created_at: string;
}

export interface PatentCorpus {
  id: string;
  title: string;
  technology_domain: string;
  cpc_classification: string;
  jurisdiction: PatentJurisdiction;
  total_patents_indexed: number;
  freedom_to_operate_verdict: FTOVerdict;
  status: 'active' | 'analyzing' | 'completed' | 'archived';
  created_at: string;
  patents?: PatentDocument[];
  evaluations?: PriorArtEvaluation[];
  fto_reports?: FreedomToOperateReport[];
}

export interface PatentMetrics {
  total_patent_corpora: number;
  total_patents_indexed: number;
  total_prior_art_evaluations: number;
  total_fto_reports: number;
  jurisdiction_distribution: Record<string, number>;
  freedom_to_operate_distribution: Record<string, number>;
}
