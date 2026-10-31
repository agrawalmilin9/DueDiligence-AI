import Link from 'next/link'
import { Logo } from '@/components/logo'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md print:hidden">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" aria-label="DueDiligence AI home" className="rounded-md">
          <Logo />
        </Link>
        <nav aria-label="Main" className="flex items-center gap-1">
          <Link href="/" className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'hidden sm:inline-flex')}>
            Dashboard
          </Link>
          <Link href="/#recent" className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'hidden sm:inline-flex')}>
            Investigations
          </Link>
          <Link href="/#new" className={buttonVariants({ size: 'sm' })}>
            New investigation
          </Link>
        </nav>
      </div>
    </header>
  )
}
