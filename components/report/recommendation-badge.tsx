import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'
import { recommendationLabel, recommendationStyles } from '@/lib/labels'
import type { Recommendation } from '@/lib/types'
import { cn } from '@/lib/utils'

const icons = {
  PROCEED: CheckCircle2,
  PROCEED_WITH_CAUTION: AlertTriangle,
  AVOID: XCircle,
} as const

export function RecommendationBadge({
  verdict,
  size = 'default',
}: {
  verdict: Recommendation
  size?: 'sm' | 'default' | 'lg'
}) {
  const Icon = icons[verdict]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border font-semibold tracking-wide whitespace-nowrap',
        recommendationStyles[verdict],
        size === 'sm' && 'px-2 py-0.5 text-[10px]',
        size === 'default' && 'px-2.5 py-1 text-xs',
        size === 'lg' && 'px-4 py-1.5 text-sm',
      )}
    >
      <Icon className={size === 'lg' ? 'size-4' : 'size-3'} aria-hidden="true" />
      {recommendationLabel[verdict]}
    </span>
  )
}
