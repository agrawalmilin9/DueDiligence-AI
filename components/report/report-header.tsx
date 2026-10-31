import Link from 'next/link'
import { ArrowLeft, CalendarDays } from 'lucide-react'
import { DownloadReportButton } from '@/components/report/download-report-button'
import { buttonVariants } from '@/components/ui/button'
import { formatDate } from '@/lib/labels'
import type { InvestigationReport } from '@/lib/types'
import { cn } from '@/lib/utils'

const sectionLinks = [
  { href: '#overview', label: 'Overview' },
  { href: '#founders', label: 'Founders' },
  { href: '#findings', label: 'Findings' },
  { href: '#risks', label: 'Risks' },
  { href: '#claims', label: 'Claims' },
  { href: '#competitors', label: 'Competitors' },
  { href: '#memo', label: 'Memo' },
]

export function ReportHeader({ report }: { report: InvestigationReport }) {
  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/"
        className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), '-ml-2 w-fit text-muted-foreground print:hidden')}
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to dashboard
      </Link>

      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="flex items-center gap-4">
          <span
            aria-hidden="true"
            className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary text-lg font-semibold text-primary-foreground"
          >
            {report.company.name.slice(0, 2).toUpperCase()}
          </span>
          <div>
            <p className="text-sm font-medium text-brand">Due diligence report</p>
            <h1 className="text-balance text-3xl font-semibold tracking-tight text-primary">{report.company.name}</h1>
            <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
              <CalendarDays className="size-3.5" aria-hidden="true" />
              Generated <time dateTime={report.generatedAt}>{formatDate(report.generatedAt)}</time> ·{' '}
              {report.company.sector}
            </p>
          </div>
        </div>
        <div className="print:hidden">
          <DownloadReportButton report={report} />
        </div>
      </div>

      <nav aria-label="Report sections" className="-mx-4 overflow-x-auto px-4 print:hidden">
        <ul className="flex gap-1 border-b">
          {sectionLinks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="block border-b-2 border-transparent px-3 py-2 text-sm whitespace-nowrap text-muted-foreground transition-colors hover:border-brand hover:text-foreground"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}
