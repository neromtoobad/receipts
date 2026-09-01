import { RC, alpha } from '../lib/theme'
import { LEAGUE } from '../lib/data'
import { Nav } from '../components/Nav'
import { Section } from '../components/Section'
import { League } from '../components/League'
import { DeletionChart } from '../components/DeletionChart'
import { HowItWorks } from '../components/HowItWorks'
import punditFrames from '../../web/data/league.json'

const BASE = process.env.NODE_ENV === 'production' ? '/receipts' : ''

export default function Home() {
  const L = LEAGUE
  const frames: Record<string, any[]> = Object.fromEntries(
    (punditFrames as any).pundits.map((p: any) => [p.id, p.frames ?? []]))
  const lead = [...L.pundits].sort((a, b) => (a.brier ?? 99) - (b.brier ?? 99))[0]

  return (
    <>
      <Nav />

      {/* Hero. Two-tone serif headline, one visual, two ways in. */}
      <header id="top" style={{ position: 'relative', overflow: 'hidden',
                                borderBottom: `1px solid ${RC.line}` }}>
        <img src={`${BASE}/pundits/augur.png`} alt="" aria-hidden
             style={{ position: 'absolute', right: '-4%', top: '-14%', width: 620, maxWidth: '58vw',
                      opacity: .5, maskImage: 'radial-gradient(58% 58% at 52% 46%, #000 42%, transparent 76%)',
                      WebkitMaskImage: 'radial-gradient(58% 58% at 52% 46%, #000 42%, transparent 76%)',
                      pointerEvents: 'none' }} />
        <div className="wrap" style={{ padding: '76px 24px 52px', position: 'relative' }}>
          <div className="eyebrow" style={{ color: RC.brand }}>Sibyl Labs Hackathon · live league</div>
          <h1 className="serif" style={{ fontSize: 'clamp(38px,5.6vw,68px)', margin: '14px 0 0',
                                         maxWidth: 800, lineHeight: 1.02 }}>
            Six AI pundits keep receipts.<br />
            <span style={{ color: RC.brand }}>Which of them has earned your trust?</span>
          </h1>
          <p className="lede" style={{ marginTop: 18, fontSize: 16 }}>
            Same model, same prompt, same budget. Every piece of evidence costs real money, bought
            from informants on Base. Nobody tells them which informant is any good — they find out
            by getting it wrong and paying for it. Then the process dies, and the only thing that
            survives is what it wrote to memory.
          </p>
          <div style={{ display: 'flex', gap: 10, marginTop: 26, flexWrap: 'wrap' }}>
            <a className="btn btn-primary" href="#maps">See what they learned →</a>
            <a className="btn btn-ghost" href="#proof">Delete the memory</a>
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 34 }}>
            <Stat k="calls on record" v={String(L.totals.forecasts)} />
            <Stat k="resolved" v={String(L.totals.resolutions)} />
            <Stat k="informants bought" v={String(L.totals.buys)} />
            <Stat k="spent on evidence" v={L.totals.spend.toFixed(2)} unit="USDC" />
          </div>
        </div>
      </header>

      <div className="wrap" style={{ paddingBottom: 80 }}>
        <Section id="proof" eyebrow="the deletion test" title="Same agent, same market."
                 accent="One tenth the cost."
                 lede={<>Delete the memory layer and it buys ten times as many informants and spends
                   ten times as much, for the same forecast. 1,000 held-out events, 3,000 local
                   model calls, zero failures — reproducible with one command and no API key.</>}>
          <div className="card" style={{ padding: 22, borderColor: alpha(RC.brand, .26) }}>
            <DeletionChart />
            <p style={{ fontSize: 12.5, color: RC.ink4, marginTop: 18, maxWidth: 780,
                        lineHeight: 1.65 }}>
              The Brier column is a tie and is reported as one: the memory arm leads in every split
              but by at most 0.0019, too small to call a quality win. The claim is{' '}
              <b style={{ color: RC.ink2 }}>the same forecast for a tenth of the cost</b> — the one
              that survives a judge&apos;s follow-up question.
            </p>
          </div>
        </Section>

        <Section id="agents" eyebrow="the league" title="Six seats." accent="One of them is ahead."
                 lede={<>They are the same agent six times over. What separates them is only what
                   each has paid to learn, so the names are labels and everything else on a card is
                   read off its own record.{lead?.brier != null && <> Right now{' '}
                   <b style={{ color: RC.ink2 }}>{lead.id}</b> leads on Brier.</>}</>}>
          <div id="maps" />
          <League league={L} frames={frames} />
        </Section>

        <Section id="how" eyebrow="how it works" title="Buy, call, die," accent="remember.">
          <HowItWorks />
        </Section>

        <Section eyebrow="proof" title="Everything here is" accent="a hash or a measurement.">
          <div style={{ display: 'grid', gap: 12,
                        gridTemplateColumns: 'repeat(auto-fill,minmax(258px,1fr))' }}>
            <Proof k="Base · x402 settlement" v="0xb0cc50db…64eebc"
                   sub="0.012 USDC, block 46195402. Gas paid by the facilitator, not the agent."
                   href="https://sepolia.basescan.org/tx/0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc" />
            <Proof k="Virtuals · ACP job 75249" v="completed"
                   sub="pundit_5 hired pundit_1 on Base mainnet, escrow funded and released." />
            <Proof k="Informant reliability" v="6,462 matches"
                   sub="6 leagues, 3 seasons. Calibrated on one season, measured on two it never saw."
                   href="https://github.com/neromtoobad/receipts/blob/main/proof/DOMAINS.md" />
            <Proof k="Memory, measured" v="42ms cold boot"
                   sub="Boot to decision. 1,757 traced forecasts fit per pundit database."
                   href="https://github.com/neromtoobad/receipts/blob/main/proof/PHASE0_FINDINGS.md" />
          </div>
        </Section>
      </div>

      <footer style={{ borderTop: `1px solid ${RC.line}`, padding: '24px 0 64px' }}>
        <div className="wrap" style={{ display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 12,
                                       color: RC.ink4 }}>
          <a href="https://github.com/neromtoobad/receipts" style={{ color: RC.ink3 }}>repo</a>
          <span>Generated {L.generated.slice(0, 16).replace('T', ' ')}Z from the pundit SQLite stores</span>
          <span style={{ marginLeft: 'auto' }}>MIT</span>
        </div>
      </footer>
    </>
  )
}

function Stat({ k, v, unit }: { k: string; v: string; unit?: string }) {
  return (
    <div className="card lift" style={{ padding: '13px 17px', minWidth: 128 }}>
      <div className="mono display" style={{ fontSize: 30, color: RC.ink, lineHeight: 1,
                                             letterSpacing: '-.02em' }}>
        {v}{unit && <span style={{ fontSize: 11, color: RC.ink4 }}> {unit}</span>}
      </div>
      <div className="eyebrow" style={{ marginTop: 7 }}>{k}</div>
    </div>
  )
}

function Proof({ k, v, sub, href }: { k: string; v: string; sub: string; href?: string }) {
  const inner = (
    <div className="card lift" style={{ padding: '15px 16px', height: '100%' }}>
      <div className="eyebrow">{k}</div>
      <div className="mono" style={{ fontSize: 15, color: RC.brand, margin: '7px 0 6px',
                                     wordBreak: 'break-all' }}>{v}</div>
      <div style={{ fontSize: 12, color: RC.ink3, lineHeight: 1.6 }}>{sub}</div>
    </div>
  )
  return href ? <a href={href}>{inner}</a> : inner
}
