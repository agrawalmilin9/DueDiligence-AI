import { CheckCircle2 } from 'lucide-react'
import { RecommendationBadge } from '@/components/report/recommendation-badge'
import type { RecommendationSummary } from '@/lib/types'

function ScoreRing({ score }: { score: number }) {
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - score / 100)
  return (
    <div className="relative size-28 shrink-0">
      <svg viewBox="0 0 100 100" className="size-full -rotate-90" aria-hidden="true">
        <circle cx="50" cy="50" r={radius} fill="none" strokeWidth="8" className="stroke-white/15" />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="stroke-[oklch(0.75_0.13_250)] transition-[stroke-dashoffset] duration-1000"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-3xl font-semibold">{score}</span>
        <span className="text-[10px] tracking-wider text-white/60 uppercase">Score</span>
      </div>
    </div>
  )
}

export function RecommendationCard({ recommendation }: { recommendation: RecommendationSummary }) {
  return (
    <section
      id="recommendation"
      aria-labelledby="recommendation-heading"
      className="scroll-mt-24 overflow-hidden rounded-2xl bg-primary text-primary-foreground shadow-xl shadow-primary/10 animate-in fade-in slide-in-from-bottom-2 duration-500 print:break-inside-avoid"
    >
      <div className="grid gap-6 p-6 sm:p-8 lg:grid-cols-[auto_1fr_minmax(0,320px)] lg:items-center">
        <ScoreRing score={recommendation.score} />
        <div className="flex flex-col gap-3">
          <h2 id="recommendation-heading" className="text-sm font-medium text-white/70">
            Final recommendation
          </h2>
          <div className="rounded-full bg-white w-fit">
            <RecommendationBadge verdict={recommendation.verdict} size="lg" />
          </div>
          <p className="max-w-xl text-pretty leading-relaxed text-white/85">{recommendation.summary}</p>
          <p className="text-xs text-white/60">
            Model confidence: <span className="font-mono text-white">{recommendation.confidence}%</span>
          </p>
        </div>
        <div className="rounded-xl bg-white/5 p-4 ring-1 ring-white/10">
          <h3 className="mb-3 text-xs font-semibold tracking-wider text-white/60 uppercase">
            Conditions before investing
          </h3>
          <ul className="flex flex-col gap-2.5">
            {recommendation.conditions.map((condition) => (
              <li key={condition} className="flex gap-2 text-sm text-white/85">
                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[oklch(0.75_0.13_250)]" aria-hidden="true" />
                {condition}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
