import Link from 'next/link'
import { RC, alpha } from '../lib/theme'
import { LEAGUE } from '../lib/data'
import { identityOf } from '../lib/pundits'
import { Nav } from '../components/Nav'
import { Section } from '../components/Section'
import { HowItWorks } from '../components/HowItWorks'
import { Foot } from '../components/Foot'

const BASE = process.env.NODE_ENV === 'production' ? '/receipts' : ''

export default function Home() {
  const L = LEAGUE
  const ranked = [...L.pundits].sort((a, b) => (a.brier ?? 99) - (b.brier ?? 99))
  const lead = ranked[0]

  return (
    <>
      <Nav />

      <header style={{ position: 'relative', overflow: 'hidden',
                       borderBottom: `1px solid ${RC.line}` }}>
        <img src={`${BASE}/pundits/augur.png`} alt="" aria-hidden
             style={{ position: 'absolute', right: '-4%', top: '-14%', width: 620, maxWidth: '58vw',
                      opacity: .5,
                      maskImage: 'radial-gradient(58% 58% at 52% 46%, #000 42%, transparent 76%)',
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
            <Link className="btn btn-primary" href="/agents">See what they learned →</Link>
            <Link className="btn btn-ghost" href="/proof">Delete the memory</Link>
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 34 }}>
            <Stat k="calls on record" v={String(L.totals.forecasts)} />
            <Stat k="resolved" v={String(L.totals.resolutions)} />
            <Stat k="informants bought" v={String(L.totals.buys)} />
            <Stat k="spent on evidence" v={L.totals.spend.toFixed(2)} unit="USDC" />
          </div>
        </div>
      </header>

      <div className="wrap" style={{ paddingBottom: 70 }}>
        <Section eyebrow="the deletion test" title="Delete the memory and it spends"
          accent="ten times as much."
          lede={<>The gate for this hackathon is whether the project still works without its memory.
            So we removed it, a thousand times, and measured. Same budget, same informants, same
            prompt, same model — the only difference is what each arm is allowed to remember.</>}>
          <div className="card" style={{ padding: 22, borderColor: alpha(RC.brand, .26) }}>
            <div style={{ display: 'flex', gap: 30, flexWrap: 'wrap', alignItems: 'center' }}>
              <div>
                <div className="serif" style={{ fontSize: 62, color: RC.brand, lineHeight: 1 }}>9.9×</div>
                <div className="eyebrow" style={{ marginTop: 6 }}>the spend, same forecast</div>
              </div>
              <div style={{ display: 'flex', gap: 26, flexWrap: 'wrap' }}>
                <Mini k="with memory" v="$5.34" c={RC.green} sub="0.56 informants a call" />
                <Mini k="without" v="$53.00" c={RC.red} sub="4.50 informants a call" />
                <Mini k="brier" v="0.5653 vs 0.5667" c={RC.ink2} sub="a tie, and reported as one" />
              </div>
              <Link className="btn btn-ghost" href="/proof"
                    style={{ marginLeft: 'auto' }}>See the method →</Link>
            </div>
          </div>
        </Section>

        <Section eyebrow="the league" title="Six seats." accent="One of them is ahead."
          lede={<>They are the same agent six times over. Everything that separates them was paid
            for.{lead?.brier != null && <> <b style={{ color: RC.ink2 }}>{identityOf(lead.id).name}
            </b> leads on Brier right now.</>}</>}>
          <Link href="/agents" style={{ display: 'block' }}>
            <div style={{ display: 'grid', gap: 12,
                          gridTemplateColumns: 'repeat(auto-fill,minmax(150px,1fr))' }}>
              {ranked.map((p, i) => {
                const id = identityOf(p.id)
                return (
                  <div key={p.id} className="lift" style={{ background: RC.surface, borderRadius: 12,
                        overflow: 'hidden', border: `1px solid ${i === 0 ? alpha(id.color, .5) : RC.line}` }}>
                    <div style={{ position: 'relative', aspectRatio: '1/1' }}>
                      <img src={`${BASE}${id.portrait}`} alt="" width={300} height={300}
                           style={{ width: '100%', height: '100%', objectFit: 'cover',
                                    display: 'block' }} />
                      <div style={{ position: 'absolute', inset: 0,
                                    background: `linear-gradient(180deg,transparent 46%,${RC.surface} 98%)` }} />
                      <div style={{ position: 'absolute', left: 11, bottom: 8 }}>
                        <div className="display" style={{ fontSize: 16, color: RC.ink }}>{id.name}</div>
                        <div className="mono" style={{ fontSize: 10.5, color: id.color }}>
                          {p.brier == null ? '—' : p.brier.toFixed(4)}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </Link>
        </Section>

        <Section eyebrow="how it works" title="Buy, call, die," accent="remember.">
          <HowItWorks />
        </Section>
      </div>
      <Foot generated={L.generated} />
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
function Mini({ k, v, c, sub }: { k: string; v: string; c: string; sub: string }) {
  return (
    <div>
      <div className="eyebrow" style={{ fontSize: 9.5 }}>{k}</div>
      <div className="mono" style={{ fontSize: 21, color: c, margin: '3px 0 2px' }}>{v}</div>
      <div style={{ fontSize: 11.5, color: RC.ink4 }}>{sub}</div>
    </div>
  )
}
