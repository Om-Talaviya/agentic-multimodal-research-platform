export type EntityType =
  | 'CONCEPT'
  | 'TECHNOLOGY'
  | 'MATERIAL'
  | 'PERSON'
  | 'ORGANIZATION'
  | 'METRIC'
  | 'DATASET'
  | 'PAPER'
  | 'LOCATION'
  | 'OTHER'

export type RelationType =
  | 'AUTHORED_BY'
  | 'USES_MATERIAL'
  | 'CONTRADICTS'
  | 'EVALUATED_ON'
  | 'DEVELOPED_BY'
  | 'CORRELATES_WITH'
  | 'DERIVED_FROM'
  | 'APPLIES_METHODOLOGY'
  | 'EXPOSED_TO'
  | 'HOSTS'
  | 'SECRETES'
  | 'ENHANCES'
  | 'SYNTHESIZED_VIA'
  | 'RELATES_TO'

export interface KnowledgeEntity {
  id: string
  user_id?: string | null
  project_id?: string | null
  name: string
  canonical_name: string
  entity_type: EntityType | string
  description?: string | null
  aliases: string[]
  properties: Record<string, any>
  confidence: number
  created_at?: string | null
  updated_at?: string | null
}

export interface KnowledgeRelation {
  id: string
  source_id: string
  target_id: string
  source_name?: string
  target_name?: string
  relation_type: RelationType | string
  user_id?: string | null
  project_id?: string | null
  job_id?: string | null
  description?: string | null
  weight: number
  confidence: number
  evidence_id?: string | null
  properties: Record<string, any>
  created_at?: string | null
}

export interface SubgraphData {
  nodes: KnowledgeEntity[]
  edges: KnowledgeRelation[]
  center_id?: string | null
  k_hops?: number
}

export interface GraphPathStep {
  from_id: string
  to_id: string
  relation_id: string
  relation_type: string
  description?: string | null
  direction: string
}

export interface GraphPathResult {
  source_entity: string
  target_entity: string
  path_found: boolean
  hop_count: number
  steps: GraphPathStep[]
  summary?: string | null
}

export interface GraphStats {
  total_entities: number
  total_relations: number
  entity_type_counts: Record<string, number>
}

export interface CreateEntityPayload {
  name: string
  canonical_name?: string
  entity_type?: EntityType | string
  description?: string
  aliases?: string[]
  properties?: Record<string, any>
  confidence?: number
}

export interface CreateRelationPayload {
  source_id: string
  target_id: string
  relation_type?: RelationType | string
  description?: string
  weight?: number
  confidence?: number
  evidence_id?: string
  properties?: Record<string, any>
}
