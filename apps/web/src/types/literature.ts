export interface SLRCriterion {
  id: string;
  criterion_type: 'inclusion' | 'exclusion';
  category: string;
  description: string;
  order_index: number;
  is_active: boolean;
}

export interface RiskOfBiasAssessment {
  overall_risk: 'low_risk' | 'some_concerns' | 'high_risk';
  selection_bias: 'low_risk' | 'some_concerns' | 'high_risk';
  confounding_bias: 'low_risk' | 'some_concerns' | 'high_risk';
  measurement_bias: 'low_risk' | 'some_concerns' | 'high_risk';
  reporting_bias: 'low_risk' | 'some_concerns' | 'high_risk';
}

export interface SLRStudyCandidate {
  id: string;
  title: string;
  authors: string[];
  publication_year?: number;
  venue?: string;
  doi?: string;
  url?: string;
  screening_status: 'identified' | 'title_abstract_screened' | 'full_text_screened' | 'included' | 'excluded';
  exclusion_reason?: string;
  relevance_score: number;
  methodology_type?: string;
  sample_size?: number;
  effect_size?: number;
  variance?: number;
  standard_error?: number;
  risk_of_bias?: RiskOfBiasAssessment;
}

export interface ForestPlotDataPoint {
  study_id: string;
  title: string;
  year?: number;
  sample_size?: number;
  effect_size: number;
  variance: number;
  standard_error: number;
  ci_lower: number;
  ci_upper: number;
  weight_percentage: number;
}

export interface MetaAnalysisReport {
  id: string;
  synthesis_name: string;
  effect_metric: string;
  model_type: string;
  total_studies_analyzed: number;
  pooled_effect_size: number;
  pooled_ci_lower: number;
  pooled_ci_upper: number;
  i_squared: number;
  q_statistic?: number;
  p_value: number;
  z_score?: number;
  forest_plot_data: ForestPlotDataPoint[];
  summary_markdown?: string;
  created_at: string;
}

export interface LiteratureReview {
  id: string;
  title: string;
  research_question: string;
  protocol_type: string;
  current_phase: string;
  pico_framework?: {
    population?: string;
    intervention?: string;
    comparator?: string;
    outcome?: string;
  };
  search_strategy?: {
    keywords?: string[];
    databases?: string[];
    date_range?: string;
  };
  total_identified: number;
  total_screened: number;
  total_eligible: number;
  total_included: number;
  total_excluded: number;
  criteria?: SLRCriterion[];
  candidates?: SLRStudyCandidate[];
  meta_analyses?: MetaAnalysisReport[];
  created_at: string;
}

export interface PRISMAFlowSummary {
  identification: {
    records_identified_databases: number;
    records_removed_before_screening: number;
  };
  screening: {
    records_screened: number;
    records_excluded_title_abstract: number;
  };
  eligibility: {
    reports_sought_for_retrieval: number;
    reports_not_retrieved: number;
    reports_assessed_for_eligibility: number;
    reports_excluded_with_reasons: Record<string, number>;
  };
  included: {
    studies_included_in_review: number;
    reports_included_in_meta_analysis: number;
  };
  attrition_rate: number;
}

export interface SLRMetrics {
  total_reviews: number;
  total_candidates: number;
  total_included_studies: number;
  total_meta_analyses: number;
  average_inclusion_rate: number;
}

export interface CreateReviewPayload {
  title: string;
  research_question: string;
  protocol_type: string;
  population?: string;
  intervention?: string;
  comparator?: string;
  outcome?: string;
  workspace_id?: string;
  project_id?: string;
}
