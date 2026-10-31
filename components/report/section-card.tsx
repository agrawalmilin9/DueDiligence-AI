import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

export function SectionCard({
  id,
  title,
  description,
  icon: Icon,
  action,
  className,
  children,
}: {
  id: string
  title: string
  description?: string
  icon: LucideIcon
  action?: React.ReactNode
  className?: string
  children: React.ReactNode
}) {
  return (
    <section
      id={id}
      aria-labelledby={`${id}-heading`}
      className={cn(
        'scroll-mt-24 rounded-2xl border bg-card p-5 shadow-sm animate-in fade-in slide-in-from-bottom-2 fill-mode-both duration-500 sm:p-6 print:break-inside-avoid print:shadow-none',
        className,
      )}
    >
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent text-brand">
            <Icon className="size-4.5" aria-hidden="true" />
          </span>
          <div>
            <h2 id={`${id}-heading`} className="font-semibold text-primary">
              {title}
            </h2>
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
        </div>
        {action}
      </div>
      {children}
    </section>
  )
}
