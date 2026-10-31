import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { RecommendationBadge } from '@/components/report/recommendation-badge'
import { formatDate } from '@/lib/labels'
import type { InvestigationSummary } from '@/lib/types'

export function RecentInvestigations({ items }: { items: InvestigationSummary[] }) {
  return (
    <section id="recent" aria-labelledby="recent-heading" className="scroll-mt-24">
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <h2 id="recent-heading" className="text-lg font-semibold text-primary">
            Recent investigations
          </h2>
          <p className="text-sm text-muted-foreground">Pick up where you left off.</p>
        </div>
        <span className="text-sm text-muted-foreground">{items.length} reports</span>
      </div>

      <ul className="grid gap-3 md:grid-cols-3">
        {items.map((item, index) => (
          <li
            key={item.id}
            className="animate-in fade-in slide-in-from-bottom-2 fill-mode-both duration-500"
            style={{ animationDelay: `${index * 80}ms` }}
          >
            <Link
              href={`/report/${item.id}`}
              className="group flex h-full flex-col gap-4 rounded-xl border bg-card p-5 transition-all hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-lg hover:shadow-brand/5"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span
                    className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-accent text-sm font-semibold text-accent-foreground"
                    aria-hidden="true"
                  >
                    {item.companyName.slice(0, 2).toUpperCase()}
                  </span>
                  <div>
                    <p className="font-medium text-foreground">{item.companyName}</p>
                    <p className="text-xs text-muted-foreground">{item.sector}</p>
                  </div>
                </div>
                <ChevronRight
                  className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-brand"
                  aria-hidden="true"
                />
              </div>
              <p className="line-clamp-2 text-sm text-muted-foreground">{item.request}</p>
              <div className="mt-auto flex items-center justify-between gap-2">
                <RecommendationBadge verdict={item.verdict} size="sm" />
                <span className="text-xs text-muted-foreground">
                  <span className="font-mono font-medium text-foreground">{item.score}</span>/100 ·{' '}
                  <time dateTime={item.createdAt}>{formatDate(item.createdAt)}</time>
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
