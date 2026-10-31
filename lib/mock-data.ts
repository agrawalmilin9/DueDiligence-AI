import type {
  CompanyMetrics,
  InvestigationReport,
  InvestigationSummary,
  Recommendation,
} from './types'

interface CompanyProfile {
  id: string
  name: string
  sector: string
  stage: string
  founded: string
  headquarters: string
  tagline: string
  verdict: Recommendation
  score: number
  confidence: number
  metrics: CompanyMetrics
}

export const companyProfiles: CompanyProfile[] = [
  {
    id: 'lumora-health',
    name: 'Lumora Health',
    sector: 'HealthTech · AI Diagnostics',
    stage: 'Series A',
    founded: '2021',
    headquarters: 'Boston, MA',
    tagline: 'AI-assisted early detection for chronic kidney disease.',
    verdict: 'PROCEED_WITH_CAUTION',
    score: 68,
    confidence: 82,
    metrics: {
      totalFunding: '$18.4M',
      lastRound: 'Series A · $14M',
      lastRoundDate: 'Mar 2026',
      valuation: '$72M (post-money, reported)',
      employees: 64,
      employeeGrowth: '+38% YoY',
      investors: ['Northbridge Ventures', 'Halcyon Health Fund', 'Atlas Seed'],
    },
  },
  {
    id: 'vectrix-robotics',
    name: 'Vectrix Robotics',
    sector: 'Industrial Automation',
    stage: 'Series B',
    founded: '2019',
    headquarters: 'Pittsburgh, PA',
    tagline: 'Autonomous inspection robots for energy infrastructure.',
    verdict: 'PROCEED',
    score: 84,
    confidence: 88,
    metrics: {
      totalFunding: '$46M',
      lastRound: 'Series B · $30M',
      lastRoundDate: 'Jan 2026',
      valuation: '$210M (post-money, reported)',
      employees: 142,
      employeeGrowth: '+52% YoY',
      investors: ['Forgepoint Capital', 'Steelhead Partners', 'Ironwood VC'],
    },
  },
  {
    id: 'quillpay',
    name: 'Quillpay',
    sector: 'FinTech · B2B Payments',
    stage: 'Seed',
    founded: '2023',
    headquarters: 'Austin, TX',
    tagline: 'Embedded invoicing and payouts for creator agencies.',
    verdict: 'AVOID',
    score: 34,
    confidence: 76,
    metrics: {
      totalFunding: '$3.2M',
      lastRound: 'Seed · $2.5M',
      lastRoundDate: 'Jun 2025',
      valuation: '$14M (post-money, reported)',
      employees: 11,
      employeeGrowth: '-15% YoY',
      investors: ['Lonestar Angels', 'Pinecrest Seed'],
    },
  },
]

const defaultProfile = (id: string, name: string): CompanyProfile => ({
  id,
  name,
  sector: 'B2B SaaS · Applied AI',
  stage: 'Series A',
  founded: '2022',
  headquarters: 'San Francisco, CA',
  tagline: `${name} builds AI-native workflow software for mid-market operations teams.`,
  verdict: 'PROCEED_WITH_CAUTION',
  score: 66,
  confidence: 79,
  metrics: {
    totalFunding: '$12.5M',
    lastRound: 'Series A · $10M',
    lastRoundDate: 'Feb 2026',
    valuation: '$55M (post-money, reported)',
    employees: 48,
    employeeGrowth: '+41% YoY',
    investors: ['Granite Peak Ventures', 'Bluewater Capital', 'Founders Syndicate'],
  },
})

const verdictSummaries: Record<Recommendation, string> = {
  PROCEED:
    'Strong founder-market fit, verifiable traction, and defensible technology. Remaining risks are typical for the stage and can be addressed in standard deal terms.',
  PROCEED_WITH_CAUTION:
    'The core thesis is credible and the team is capable, but several headline claims are unverified or conflicting. Proceed only after confirmatory diligence on revenue and customer concentration.',
  AVOID:
    'Material discrepancies between stated and observed metrics, declining headcount, and a crowded market with well-funded incumbents make this investment unattractive at the proposed terms.',
}

export function buildReport(
  id: string,
  name: string,
  request: string,
): InvestigationReport {
  const profile = companyProfiles.find((p) => p.id === id) ?? defaultProfile(id, name)
  const company = profile.name
  const domain = `${profile.id.replace(/-/g, '')}.com`

  return {
    id: profile.id,
    request,
    generatedAt: new Date('2026-10-31T09:30:00Z').toISOString(),
    company: {
      name: company,
      tagline: profile.tagline,
      description: `${company} is a ${profile.stage} company headquartered in ${profile.headquarters}. The company sells a subscription platform to enterprise customers and has expanded from a single pilot program into a multi-product offering over the past 18 months. Its go-to-market relies on a direct sales team supplemented by channel partnerships.`,
      sector: profile.sector,
      stage: profile.stage,
      founded: profile.founded,
      headquarters: profile.headquarters,
      website: `https://www.${domain}`,
      businessModel: 'Annual SaaS subscriptions with usage-based expansion',
    },
    metrics: profile.metrics,
    founders: [
      {
        name: 'Maya Chen',
        role: 'Co-founder & CEO',
        background:
          'Former product lead who scaled an enterprise analytics product from $2M to $40M ARR. MBA, Wharton.',
        previousCompanies: ['Datacore', 'McKinsey & Company'],
        profileUrl: 'https://www.linkedin.com/in/maya-chen-example',
      },
      {
        name: 'Daniel Okafor',
        role: 'Co-founder & CTO',
        background:
          'Machine learning researcher with 12 peer-reviewed publications. Led ML infrastructure for a 200-person engineering org.',
        previousCompanies: ['Google Research', 'Stripe'],
        profileUrl: 'https://www.linkedin.com/in/daniel-okafor-example',
      },
      {
        name: 'Priya Raman',
        role: 'Co-founder & COO',
        background:
          'Operator with experience building go-to-market teams in regulated industries. Previously VP Operations.',
        previousCompanies: ['Flatiron Health', 'Deloitte'],
        profileUrl: 'https://www.linkedin.com/in/priya-raman-example',
      },
    ],
    competitors: [
      {
        name: 'Corvana',
        description: 'Category incumbent with broad enterprise distribution and legacy contracts.',
        funding: '$310M',
        positioning: 'Leader',
        threat: 'high',
      },
      {
        name: 'Helix Labs',
        description: 'Fast-growing challenger competing aggressively on price in the mid-market.',
        funding: '$88M',
        positioning: 'Challenger',
        threat: 'medium',
      },
      {
        name: 'Signalwise',
        description: 'Vertical specialist focused on a single customer segment with deep integrations.',
        funding: '$24M',
        positioning: 'Niche',
        threat: 'low',
      },
      {
        name: 'Openframe',
        description: 'Open-source alternative gaining developer mindshare; limited enterprise support.',
        funding: '$15M',
        positioning: 'Niche',
        threat: 'medium',
      },
    ],
    findings: [
      {
        title: 'Experienced, complementary founding team',
        detail:
          'All three founders have prior operating experience at scale-stage companies, and their skill sets cover product, technology, and go-to-market.',
        sentiment: 'positive',
      },
      {
        title: 'Hiring momentum signals real demand',
        detail: `Headcount grew ${profile.metrics.employeeGrowth} with most hires in sales and customer success, consistent with expanding customer adoption.`,
        sentiment: profile.metrics.employeeGrowth.startsWith('-') ? 'negative' : 'positive',
      },
      {
        title: 'Revenue figures are inconsistent across sources',
        detail:
          'ARR cited in the pitch deck differs from figures quoted in press interviews by roughly 30%, suggesting a mix of contracted and recognized revenue.',
        sentiment: 'negative',
      },
      {
        title: 'Customer concentration is high',
        detail:
          'Public case studies and job postings suggest the top two customers may represent more than 40% of revenue.',
        sentiment: 'negative',
      },
      {
        title: 'Regulatory pathway is partially de-risked',
        detail:
          'The company has completed one compliance certification and has a second in progress, ahead of most early-stage peers.',
        sentiment: 'neutral',
      },
    ],
    risks: [
      {
        category: 'Financial',
        title: 'Unverified revenue claims',
        description: 'Reported ARR cannot be reconciled with public signals and press statements.',
        level: 'high',
        mitigation: 'Request audited financials and a customer-level revenue breakdown.',
      },
      {
        category: 'Market',
        title: 'Well-funded incumbent competition',
        description: 'The market leader has 15x more capital and existing enterprise relationships.',
        level: 'medium',
        mitigation: 'Validate win/loss rates against the incumbent with reference customers.',
      },
      {
        category: 'Customer',
        title: 'Revenue concentration',
        description: 'Loss of a single top customer could materially impact growth.',
        level: 'high',
        mitigation: 'Review contract terms, renewal dates, and expansion clauses for top accounts.',
      },
      {
        category: 'Team',
        title: 'Key-person dependency',
        description: 'Core IP and model architecture are closely tied to the CTO.',
        level: 'medium',
        mitigation: 'Confirm IP assignment agreements and engineering leadership depth.',
      },
      {
        category: 'Legal',
        title: 'Data privacy exposure',
        description: 'Processing of sensitive customer data creates compliance obligations.',
        level: 'low',
        mitigation: 'Review SOC 2 report and data processing agreements.',
      },
    ],
    claims: [
      {
        id: 'c1',
        claim: `${company} was founded in ${profile.founded} by Maya Chen, Daniel Okafor, and Priya Raman.`,
        status: 'VERIFIED',
        evidence: 'State incorporation records and founder profiles consistently confirm the founding date and team.',
        source: {
          title: 'OpenCorporates — company registration',
          url: `https://opencorporates.com/companies/us_de/${profile.id}`,
        },
      },
      {
        id: 'c2',
        claim: `Raised ${profile.metrics.totalFunding} in total funding to date.`,
        status: 'VERIFIED',
        evidence: 'Funding total matches SEC Form D filings and the lead investor announcement.',
        source: {
          title: 'SEC EDGAR — Form D filing',
          url: `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(company)}`,
        },
      },
      {
        id: 'c3',
        claim: 'Reached $4.2M in annual recurring revenue.',
        status: 'CONFLICTING',
        evidence: 'Pitch deck states $4.2M ARR, while a TechCrunch interview from the same quarter cites "nearly $3M".',
        source: {
          title: 'TechCrunch — founder interview',
          url: `https://techcrunch.com/2026/04/12/${profile.id}-raises-series-a`,
        },
      },
      {
        id: 'c4',
        claim: 'Serves more than 120 enterprise customers.',
        status: 'CONTRADICTED',
        evidence: 'The company website lists 34 customer logos, and a recent press release references "over 40 customers".',
        source: {
          title: `${company} — press release`,
          url: `https://www.${domain}/press/series-a-announcement`,
        },
      },
      {
        id: 'c5',
        claim: 'Net revenue retention above 140%.',
        status: 'UNVERIFIED',
        evidence: 'No independent source confirms this metric. Only referenced in the company pitch deck.',
        source: {
          title: 'Company pitch deck (provided)',
          url: `https://www.${domain}/investors`,
        },
      },
      {
        id: 'c6',
        claim: `Team of ${profile.metrics.employees} employees across engineering, sales, and operations.`,
        status: 'VERIFIED',
        evidence: 'LinkedIn employee count and open job listings align with the stated headcount.',
        source: {
          title: 'LinkedIn — company page',
          url: `https://www.linkedin.com/company/${profile.id}`,
        },
      },
      {
        id: 'c7',
        claim: 'Proprietary model outperforms competitors by 35% on accuracy benchmarks.',
        status: 'UNVERIFIED',
        evidence: 'The benchmark is self-reported and has not been published or independently reproduced.',
        source: {
          title: `${company} — engineering blog`,
          url: `https://www.${domain}/blog/benchmark-results`,
        },
      },
    ],
    recommendation: {
      verdict: profile.verdict,
      score: profile.score,
      confidence: profile.confidence,
      summary: verdictSummaries[profile.verdict],
      conditions: [
        'Obtain audited financial statements for the last 24 months',
        'Conduct reference calls with at least 5 customers, including the top 2 accounts',
        'Reconcile customer count discrepancy before signing the term sheet',
        'Include information rights and a board observer seat in deal terms',
      ],
    },
    memo: {
      thesis: `${company} is positioned to capture a meaningful share of a growing market through a technically differentiated product and an experienced founding team. The investment case depends on validating revenue quality and reducing customer concentration over the next 12–18 months.`,
      sections: [
        {
          heading: 'Opportunity',
          body: `The target market is estimated at $8.5B and growing at 22% annually, driven by enterprise demand for automation and regulatory pressure. ${company} addresses a clear pain point with a product that shortens time-to-value from months to weeks.`,
        },
        {
          heading: 'Team',
          body: 'The founding team combines deep technical expertise with operational experience in regulated industries. Prior exits are absent, but each founder has led teams through hypergrowth at well-known companies.',
        },
        {
          heading: 'Traction',
          body: 'Headcount growth and public customer announcements indicate real momentum. However, the gap between claimed and verifiable customer counts is the single largest diligence concern.',
        },
        {
          heading: 'Deal Considerations',
          body: 'At the reported valuation, the proposed investment would represent a minority stake. We recommend structuring with milestone-based tranches tied to verified ARR and customer diversification targets.',
        },
      ],
    },
  }
}

export const recentInvestigations: InvestigationSummary[] = [
  {
    id: 'vectrix-robotics',
    companyName: 'Vectrix Robotics',
    sector: 'Industrial Automation',
    request: 'Evaluate for a $5M participation in the Series B extension.',
    createdAt: '2026-10-30T15:20:00Z',
    verdict: 'PROCEED',
    score: 84,
  },
  {
    id: 'lumora-health',
    companyName: 'Lumora Health',
    sector: 'HealthTech · AI Diagnostics',
    request: 'Analyze this startup for a potential investment of $2M.',
    createdAt: '2026-10-28T11:05:00Z',
    verdict: 'PROCEED_WITH_CAUTION',
    score: 68,
  },
  {
    id: 'quillpay',
    companyName: 'Quillpay',
    sector: 'FinTech · B2B Payments',
    request: 'Verify traction claims before a $500K angel check.',
    createdAt: '2026-10-24T09:45:00Z',
    verdict: 'AVOID',
    score: 34,
  },
]
