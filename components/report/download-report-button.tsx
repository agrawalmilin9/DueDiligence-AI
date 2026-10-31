'use client'

import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { reportToMarkdown } from '@/lib/report-export'
import type { InvestigationReport } from '@/lib/types'

export function DownloadReportButton({ report }: { report: InvestigationReport }) {
  function handleDownload() {
    const blob = new Blob([reportToMarkdown(report)], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.id}-due-diligence-report.md`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Button onClick={handleDownload} size="lg">
      <Download className="size-4" aria-hidden="true" />
      Download report
    </Button>
  )
}
