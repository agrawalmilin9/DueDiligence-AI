import type { ClaimStatus, Recommendation, RiskLevel } from './types'

export const recommendationLabel: Record<Recommendation, string> = {
  PROCEED: 'PROCEED',
  PROCEED_WITH_CAUTION: 'PROCEED WITH CAUTION',
  AVOID: 'AVOID',
}

export const recommendationStyles: Record<Recommendation, string> = {
  PROCEED: 'bg-success/10 text-success border-success/25',
  PROCEED_WITH_CAUTION: 'bg-warning/15 text-[oklch(0.5_0.13_60)] border-warning/30',
  AVOID: 'bg-destructive/10 text-destructive border-destructive/25',
}

export const claimStatusStyles: Record<ClaimStatus, string> = {
  VERIFIED: 'bg-success/10 text-success border-success/25',
  CONTRADICTED: 'bg-destructive/10 text-destructive border-destructive/25',
  UNVERIFIED: 'bg-muted text-muted-foreground border-border',
  CONFLICTING: 'bg-warning/15 text-[oklch(0.5_0.13_60)] border-warning/30',
}

export const riskLevelStyles: Record<RiskLevel, string> = {
  low: 'bg-success/10 text-success border-success/25',
  medium: 'bg-warning/15 text-[oklch(0.5_0.13_60)] border-warning/30',
  high: 'bg-destructive/10 text-destructive border-destructive/25',
}

export function formatDate(iso: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(iso))
}
