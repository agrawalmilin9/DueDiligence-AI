import { ScanSearch } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn('flex items-center gap-2', className)}>
      <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <ScanSearch className="size-4.5" aria-hidden="true" />
      </span>
      <span className="text-base font-semibold tracking-tight text-primary">
        DueDiligence<span className="text-brand"> AI</span>
      </span>
    </span>
  )
}
