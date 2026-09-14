export interface GrantSpecificAim {
  id: string;
  proposal_id: string;
  aim_number: number;
  title: string;
  hypothesis: string;
  experimental_design: string;
  expected_outcomes: string;
  potential_pitfalls_and_alternatives?: string;
  milestones: Array<{ quarter: string; milestone: string; deliverable: string }>;
  allocated_effort_percent: number;
  created_at: string;
}

export interface GrantBudgetItem {
  id: string;
  proposal_id: string;
  year_number: number;
  category: string;
  item_name: string;
  cost_usd: number;
  justification: string;
  is_direct_cost: boolean;
  created_at: string;
}

export interface GrantReviewScorecard {
  id: string;
  proposal_id: string;
  reviewer_persona: string;
  significance_score: number;
  investigators_score: number;
  innovation_score: number;
  approach_score: number;
  environment_score: number;
  overall_impact_score: number;
  recommendation: string;
  critique_strengths: string[];
  critique_weaknesses: string[];
  summary_statement: string;
  created_at: string;
}

export interface GrantProposal {
  id: string;
  user_id?: string;
  workspace_id?: string;
  project_id?: string;
  research_job_id?: string;
  title: string;
  funding_agency: string;
  grant_mechanism: string;
  target_call_number?: string;
  project_duration_years: number;
  total_requested_budget_usd: number;
  indirect_cost_rate_percent: number;
  status: string;
  executive_abstract?: string;
  significance_narrative?: string;
  innovation_narrative?: string;
  approach_narrative?: string;
  preliminary_data_summary?: string;
  mock_panel_overall_score: number;
  percentile_estimate: number;
  metadata?: Record<string, any>;
  aims?: GrantSpecificAim[];
  budget_items?: GrantBudgetItem[];
  review_scorecards?: GrantReviewScorecard[];
  created_at: string;
  updated_at?: string;
}
