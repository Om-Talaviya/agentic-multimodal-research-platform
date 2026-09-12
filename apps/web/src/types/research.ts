export interface ResearchJob {
  id: string
  request_id: string
  question: string
  objective: string
  domain: string | null
  scope: string | null
  constraints: string[]
  expected_output: string
  status: string
  created_at: string
  updated_at: string
  completed_at: string | null
  error_message: string | null
}

export interface QueryTreeNode {
  id: string
  parent_id?: string | null
  question: string
  rationale?: string
  domain_focus?: string
  depth?: number
  assigned_agent?: string
  subqueries?: QueryTreeNode[]
  status?: string
}

export interface InferredScope {
  domain?: string
  time_horizon?: string | null
  geography?: string | null
  key_entities?: string[]
  constraints?: string[]
}

export interface ResearchStep {
  id: string
  name: string
  description: string
  agent: string
  inputs?: Record<string, any>
  depends_on?: string[]
  priority?: number
  parent_id?: string | null
  depth?: number
  is_dynamic?: boolean
}

export interface ResearchPlan {
  objective: string
  steps: ResearchStep[]
  expected_outputs: string[]
  query_tree?: QueryTreeNode | null
  ambiguity_score?: number
  inferred_scope?: InferredScope | null
  replan_count?: number
  plan_explanation?: string
}

export interface ResearchTask {
  id: string
  job_id: string
  parent_task_id?: string | null
  is_dynamic?: boolean
  depth?: number
  type: string
  objective: string
  agent: string
  status: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  result: Record<string, any> | null
}

export interface Source {
  id: string
  type: string
  url: string | null
  title: string
  metadata: Record<string, any>
  retrieved_at: string
}

export interface CitationCoordinates {
  page_number?: number | null
  paragraph_index?: number | null
  table_row?: number | null
  table_col?: number | null
  char_start?: number | null
  char_end?: number | null
}

export interface Citation {
  id: string
  claim: string
  source_id?: string | null
  document_id?: string | null
  citation_text: string
  quote: string
  coordinates?: CitationCoordinates | null
  confidence: number
  source_reliability?: number
}

export interface Contradiction {
  id: string
  topic: string
  claim_a: string
  source_a: string
  claim_b: string
  source_b: string
  conflict_type: string
  explanation: string
  severity: string
}

export interface Evidence {
  id: string
  source_id: string
  claim: string
  supporting_text: string
  confidence: number
  source_reliability?: number
  verification_status: string
  verification_notes: string | null
  citation_coordinates?: CitationCoordinates | null
  citations?: Citation[]
}

export interface Finding {
  id: string
  topic: string
  summary: string
  evidence_ids: string[]
  citations?: Citation[]
  confidence: number
  uncertainty: string | null
  assumptions: string[]
}

export interface ResearchReport {
  id: string
  job_id: string
  title: string
  executive_summary: string
  methodology: string
  findings: Finding[]
  evidence: Evidence[]
  sources: Source[]
  contradictions?: Contradiction[]
  confidence_score?: number
  conclusions: string[]
  limitations: string[]
  generated_at: string
}

export interface DocumentItem {
  id: string
  filename: string
  mime_type: string
  file_size: number
  file_path: string
  status: string
  created_at: string
}