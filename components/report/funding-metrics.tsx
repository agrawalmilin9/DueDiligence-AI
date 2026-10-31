import { Landmark } from 'lucide-react'
import { SectionCard } from '@/components/report/section-card'
import type { CompanyMetrics } from '@/lib/types'
import { cn } from '@/lib/utils'

export function FundingMetrics({ metrics }: { metrics: CompanyMetrics }) {
  const isShrinking = metrics.employeeGrowth.startsWith('-')

  return (
    <SectionCard id="funding" title="Funding & team" icon={Landmark}>
      <dl className="grid grid-cols-2 gap-3">
        <div className="col-span-2 rounded-xl bg-secondary p-4">
          <dt className="text-xs text-muted-foreground">Total funding</dt>
          <dd className="font-mono text-2xl font-semibold text-primary">{metrics.totalFunding}</dd>
        </div>
        <div className="rounded-xl border p-3">
          <dt className="text-xs text-muted-foreground">Employees</dt>
          <dd className="font-mono text-lg font-semibold text-primary">{metrics.employees}</dd>
          <dd className={cn('text-xs font-medium', isShrinking ? 'text-destructive' : 'text-success')}>
            {metrics.employeeGrowth}
          </dd>
        </div>
        <div className="rounded-xl border p-3">
          <dt className="text-xs text-muted-foreground">Last round</dt>
          <dd className="text-sm font-semibold text-primary">{metrics.lastRound}</dd>
          <dd className="text-xs text-muted-foreground">{metrics.lastRoundDate}</dd>
        </div>
        <div className="col-span-2">
          <dt className="text-xs text-muted-foreground">Valuation</dt>
          <dd className="text-sm font-medium text-foreground">{metrics.valuation}</dd>
        </div>
        <div className="col-span-2">
          <dt className="mb-1.5 text-xs text-muted-foreground">Investors</dt>
          <dd className="flex flex-wrap gap-1.5">
            {metrics.investors.map((investor) => (
              <span key={investor} className="rounded-md bg-accent px-2 py-1 text-xs font-medium text-accent-foreground">
                {investor}
              </span>
            ))}
          </dd>
        </div>
      </dl>
    </SectionCard>
  )
}
