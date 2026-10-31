import { cn } from '@/lib/utils'

export function StatusPill({ className, children }: { className: string; children: React.ReactNode }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide whitespace-nowrap uppercase',
        className,
      )}
    >
      {children}
    </span>
  )
}
