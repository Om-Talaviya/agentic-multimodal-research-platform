/**
 * TypeScript type definitions for Enterprise Security, KMS Secrets, and Audit Logs (Phase 23).
 */

export interface SecurityAuditLogRecord {
  id: string
  event_type: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  actor_id?: string | null
  workspace_id?: string | null
  resource_type?: string | null
  resource_id?: string | null
  action: string
  details: Record<string, unknown>
  ip_address?: string | null
  user_agent?: string | null
  previous_hash: string
  current_hash: string
  created_at: string
}

export interface EncryptedSecretRecord {
  id: string
  name: string
  secret_type: string
  provider: string
  key_version: string
  masked_preview: string
  workspace_id?: string | null
  created_by?: string | null
  is_revoked: boolean
  created_at: string
  updated_at: string
}

export interface SecurityPolicyRecord {
  id: string
  workspace_id: string
  retention_days: number
  enforce_mfa: boolean
  ip_whitelist: {
    allowed_cidrs?: string[]
  }
  allowed_providers: {
    providers?: string[]
  }
  gdpr_anonymize_on_delete: boolean
  data_classification: string
  updated_at: string
}

export interface ComplianceScorecard {
  soc2_compliance: {
    status: 'COMPLIANT' | 'NON_COMPLIANT'
    controls: {
      cc6_1_access_control: string
      cc6_6_encryption_at_rest: string
      cc7_2_immutable_audit_logging: string
      audit_chain_verified: boolean
    }
  }
  gdpr_compliance: {
    status: 'COMPLIANT' | 'NON_COMPLIANT'
    controls: {
      article_17_right_to_erasure: string
      article_25_data_protection_by_design: string
      article_32_security_of_processing: string
    }
  }
  policy?: SecurityPolicyRecord
  audit_summary?: {
    verified: boolean
    total_records_checked: number
    integrity_status: string
    error_detail?: string | null
    genesis_hash: string
    latest_verified_hash?: string | null
  }
}
