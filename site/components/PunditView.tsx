'use client'

// One pundit, with a scrubber through everything it has ever learned.
//
// A snapshot of a trust map is a table. The map CHANGING is the argument: you
// drag the handle and watch an agent work out, at real cost, which informants
// are worth listening to. That is the thing the pitch promises and it needs to
// be watchable, not described.

import { useMemo, useState } from 'react'
import { RC } from '../lib/theme'
import type { Cell, Pundit } from '../lib/data'
import { TrustMap } from './TrustMap'

type Frame = {
  ts: string; market: string; domain: string; outcome: string
  changed: Record<string, Cell & { state: string }>
}

export function PunditView({ p, domains, catalogue, frames }:
  { p: Pundit; domains: string[]
    catalogue: Record<string, { name: string; price: number; answers_on: string[] }>
    frames: Frame[] }) {

  const [i, setI] = useState(frames.length)   // default: now
  const live = i >= frames.length

  // Replay the belief state up to the chosen point. Cheap: one pass per move.
  const cells = useMemo(() => {
    if (live) return p.cells
    const acc: Record<string, Cell> = {}
    for (const f of frames.slice(0, i)) {
      for (const [k, c] of Object.entries(f.changed)) acc[k] = { ...(acc[k] ?? {}), ...c } as Cell
    }
    return acc
  }, [i, live, frames, p.cells])

  const at = live ? null : frames[Math.max(0, i - 1)]
  const learned = Object.values(cells).filter(c => (c.skill ?? 0) > 0).length
  const burned = Object.values(cells).filter(c => c.skill != null && c.skill <= 0).length

  return (
    <section style={{ marginBottom: 44 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, flexWrap: 'wrap',
                    marginBottom: 10 }}>
        <h2 className="display" style={{ fontSize: 26, margin: 0 }}>{p.id}</h2>
        <span className="mono" style={{ color: RC.ink3, fontSize: 12 }}>
          {p.forecasts} calls · {p.resolutions} resolved · {p.spend.toFixed(4)} USDC ·{' '}
          {p.brier == null ? 'no brier yet' : `brier ${p.brier.toFixed(4)}`}
        </span>
        <span style={{ marginLeft: 'auto', fontSize: 12 }}>
          <b className="mono" style={{ color: RC.green }}>{learned}</b>
          <span style={{ color: RC.ink4 }}> trusted · </span>
          <b className="mono" style={{ color: RC.red }}>{burned}</b>
          <span style={{ color: RC.ink4 }}> burned</span>
        </span>
      </div>

      {frames.length > 0 && (
        <div className="card" style={{ padding: '12px 14px', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span className="eyebrow">what it knew</span>
            <span className="mono" style={{ fontSize: 12, color: live ? RC.brand : RC.ink2 }}>
              {live ? 'now' : `${at?.ts.slice(0, 19).replace('T', ' ')}Z`}
            </span>
            <span className="mono" style={{ marginLeft: 'auto', fontSize: 11, color: RC.ink4 }}>
              {i} / {frames.length} belief updates
            </span>
          </div>
          <input type="range" min={0} max={frames.length} value={i}
                 onChange={e => setI(Number(e.target.value))}
                 style={{ width: '100%', accentColor: RC.brand }} />
          <div style={{ fontSize: 12, color: RC.ink4, marginTop: 8, minHeight: 18 }}>
            {live
              ? 'Drag back to watch it learn. Every step is one resolved market that changed its mind.'
              : at && <>Learned from <b style={{ color: RC.ink2 }}>{at.market}</b> resolving{' '}
                  <b className="mono" style={{ color: RC.brand }}>{at.outcome}</b>
                  {' — '}{Object.values(at.changed).map(c => c.source).join(', ')} scored.</>}
          </div>
        </div>
      )}

      <TrustMap cells={cells} domains={domains} catalogue={catalogue} />
    </section>
  )
}
