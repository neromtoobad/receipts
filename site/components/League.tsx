'use client'

// The league, as one screen.
//
// Six stacked trust maps was a wall of scroll and made the pundits look
// identical, which is exactly the wrong impression: the whole point is that
// they diverge. Tabs put them in the same place so switching between two is a
// comparison rather than a scroll, and the divergence becomes visible.

import { useState } from 'react'
import { RC, alpha } from '../lib/theme'
import type { FeedItem, League as L, Pundit } from '../lib/data'
import { PunditView } from './PunditView'
import { Feed } from './Feed'

type Frames = Record<string, any[]>

export function League({ league, frames }: { league: L; frames: Frames }) {
  const [sel, setSel] = useState(league.pundits[0]?.id ?? '')
  const p = league.pundits.find(x => x.id === sel) ?? league.pundits[0]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 372px', gap: 26,
                  alignItems: 'start' }} className="home-grid">
      <div>
        <div className="eyebrow" style={{ marginBottom: 10 }}>Trust maps</div>
        <p style={{ fontSize: 13.5, color: RC.ink3, margin: '0 0 14px', maxWidth: 720,
                    lineHeight: 1.6 }}>
          What each pundit has worked out about each informant, in each domain, by paying for it.
          Nothing here was told to it: the catalogue it reads advertises prices and coverage and
          never a hit rate.
        </p>

        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
          {league.pundits.map(x => {
            const on = x.id === sel
            const trusted = Object.values(x.cells).filter(c => (c.skill ?? 0) > 0).length
            const burned = Object.values(x.cells).filter(c => c.skill != null && c.skill <= 0).length
            return (
              <button key={x.id} onClick={() => setSel(x.id)}
                style={{ background: on ? alpha(RC.brand, .14) : RC.surface,
                         border: `1px solid ${on ? alpha(RC.brand, .45) : RC.line}`,
                         color: on ? RC.ink : RC.ink3, borderRadius: 8, padding: '8px 12px',
                         cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left', lineHeight: 1.3 }}>
                <div className="mono" style={{ fontSize: 12.5 }}>{x.id}</div>
                <div className="mono" style={{ fontSize: 10.5, color: RC.ink4, marginTop: 2 }}>
                  {x.resolutions} resolved
                  {trusted > 0 && <span style={{ color: RC.green }}> · {trusted}✓</span>}
                  {burned > 0 && <span style={{ color: RC.red }}> · {burned}✕</span>}
                </div>
              </button>
            )
          })}
        </div>

        {p && <PunditView p={p} domains={league.domains} catalogue={league.catalogue as any}
                          frames={frames[p.id] ?? []} />}
      </div>

      <div style={{ position: 'sticky', top: 18 }}>
        <div className="eyebrow" style={{ marginBottom: 10 }}>Live</div>
        <Feed items={league.feed} />
        <p style={{ fontSize: 11.5, color: RC.ink4, marginTop: 12, lineHeight: 1.6 }}>
          Generated {league.generated.slice(0, 19).replace('T', ' ')}Z, read from the pundit SQLite
          stores through <span className="mono">agent/memory.py</span>. Reliability is measured from
          resolved outcomes, never declared.
        </p>
      </div>
      <style>{`@media (max-width:980px){ .home-grid{ grid-template-columns:1fr !important } }`}</style>
    </div>
  )
}
