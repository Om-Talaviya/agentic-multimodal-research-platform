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

export interface ResearchTask {
  id: string
  job_id: string
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

export interface Evidence {
  id: string
  source_id: string
  claim: string
  supporting_text: string
  confidence: number
  verification_status: string
  verification_notes: string | null
}

export interface Finding {
  id: string
  topic: string
  summary: string
  evidence_ids: string[]
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
  conclusions: string[]
  limitations: string[]
  generated_at: string
}