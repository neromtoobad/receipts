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
import { AgentCards } from './AgentCards'
import { Calls } from './Calls'
import { identityOf } from '../lib/pundits'

type Frames = Record<string, any[]>

export function League({ league, frames }: { league: L; frames: Frames }) {
  const [sel, setSel] = useState(league.pundits[0]?.id ?? '')
  const [tab, setTab] = useState<'map' | 'calls'>('map')
  const p = league.pundits.find(x => x.id === sel) ?? league.pundits[0]
  const id = identityOf(p?.id ?? '')

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 372px', gap: 26,
                  alignItems: 'start' }} className="home-grid">
      <div>
        <AgentCards pundits={league.pundits} selected={sel} onSelect={setSel} />

        {p && (
          <div style={{ marginTop: 26 }}>
            <div style={{ display: 'flex', gap: 6, marginBottom: 14, alignItems: 'center' }}>
              {(['map', 'calls'] as const).map(t => (
                <button key={t} onClick={() => setTab(t)}
                  style={{ background: tab === t ? alpha(id.color, .16) : 'transparent',
                           border: `1px solid ${tab === t ? alpha(id.color, .45) : RC.line}`,
                           color: tab === t ? RC.ink : RC.ink3, borderRadius: 999,
                           padding: '5px 14px', fontSize: 12, cursor: 'pointer',
                           fontFamily: 'inherit' }}>
                  {t === 'map' ? 'trust map' : `calls (${p.forecasts})`}
                </button>
              ))}
              <span className="mono" style={{ marginLeft: 'auto', fontSize: 11, color: RC.ink4 }}>
                same model, same prompt as every other seat
              </span>
            </div>
            {tab === 'map'
              ? <PunditView p={p} domains={league.domains} catalogue={league.catalogue as any}
                            frames={frames[p.id] ?? []} />
              : <Calls items={(p as any).feed ?? []} color={id.color} />}
          </div>
        )}
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
