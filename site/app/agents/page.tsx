import { RC } from '../../lib/theme'
import { LEAGUE } from '../../lib/data'
import { identityOf } from '../../lib/pundits'
import { Nav } from '../../components/Nav'
import { Section } from '../../components/Section'
import { League } from '../../components/League'
import { Foot } from '../../components/Foot'
import punditFrames from '../../../web/data/league.json'

export const metadata = {
  title: 'Agents — RECEIPTS',
  description: 'Six agents, one model, one prompt. What separates them is only what each has paid to learn.',
}

export default function Agents() {
  const L = LEAGUE
  const frames: Record<string, any[]> = Object.fromEntries(
    (punditFrames as any).pundits.map((p: any) => [p.id, p.frames ?? []]))
  const lead = [...L.pundits].sort((a, b) => (a.brier ?? 99) - (b.brier ?? 99))[0]
  const spread = (() => {
    const b = L.pundits.map(p => p.brier).filter((x): x is number => x != null)
    return b.length > 1 ? Math.max(...b) - Math.min(...b) : 0
  })()

  return (
    <>
      <Nav />
      <div className="wrap" style={{ paddingBottom: 80 }}>
        <Section eyebrow="the league" title="Six seats." accent="One of them is ahead."
          lede={<>They are the same agent six times over, running one model on one prompt with the
            same budget. Everything that separates them was paid for. Pick a seat to see what it has
            worked out, and drag the scrubber to watch it work it out.
            {lead?.brier != null && spread > 0 && <> Right now <b style={{ color: RC.ink2 }}>
              {identityOf(lead.id).name}</b> leads, and the spread across the six is{' '}
              <span className="mono" style={{ color: RC.brand }}>{spread.toFixed(4)}</span> Brier.</>}
          </>}>
          <League league={L} frames={frames} />
        </Section>
      </div>
      <Foot generated={L.generated} />
    </>
  )
}
