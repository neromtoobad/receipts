import { RC } from '../../lib/theme'
import { LEAGUE } from '../../lib/data'
import { Nav } from '../../components/Nav'
import { Section } from '../../components/Section'
import { Feed } from '../../components/Feed'
import { Foot } from '../../components/Foot'

export const metadata = {
  title: 'Live — RECEIPTS',
  description: 'Every purchase, call, resolution and promotion in the league, newest first.',
}

export default function Live() {
  const L = LEAGUE
  const counts = L.feed.reduce<Record<string, number>>((a, f) => {
    a[f.kind] = (a[f.kind] ?? 0) + 1; return a
  }, {})
  return (
    <>
      <Nav />
      <div className="wrap" style={{ paddingBottom: 80 }}>
        <Section eyebrow="live" title="It bought this. It called that."
          accent="Reality disagreed."
          lede={<>The league ticks every twenty minutes. Each tick spawns six processes that
            forecast and die, then the resolver scores whatever has resolved since. This is that
            stream, newest first — the sequence is the story.</>}>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 18 }}>
            <Tile k="calls on record" v={L.totals.forecasts} />
            <Tile k="resolved" v={L.totals.resolutions} />
            <Tile k="informants bought" v={L.totals.buys} />
            <Tile k="promotions in view" v={counts.promotion ?? 0} />
          </div>
          <Feed items={L.feed} />
        </Section>
      </div>
      <Foot generated={L.generated} />
    </>
  )
}

function Tile({ k, v }: { k: string; v: number }) {
  return (
    <div className="card lift" style={{ padding: '12px 16px', minWidth: 124 }}>
      <div className="mono display" style={{ fontSize: 26, color: RC.ink, lineHeight: 1 }}>{v}</div>
      <div className="eyebrow" style={{ marginTop: 6 }}>{k}</div>
    </div>
  )
}
