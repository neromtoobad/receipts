'use client'

// Every call a pundit has made, with what it bought to make it and what it
// leaned on. The reasoning is the receipt: you can see whether the evidence it
// paid for actually moved the answer, or whether it shrugged and returned the
// base rate.

import { RC, alpha } from '../lib/theme'
import type { FeedItem } from '../lib/data'
import { relTime } from '../lib/data'

export function Calls({ items, color }: { items: FeedItem[]; color: string }) {
  const calls = items.filter(i => i.kind === 'forecast').slice(0, 14)
  if (!calls.length)
    return <p style={{ color: RC.ink4, fontSize: 12.5 }}>No calls on record yet.</p>

  return (
    <div style={{ display: 'grid', gap: 8 }}>
      {calls.map((c, i) => {
        const probs = Object.entries(c.probabilities ?? {})
        const top = probs.sort((a, b) => b[1] - a[1])[0]
        const leaned = c.leaned_on ?? []
        return (
          <div key={i} className="card" style={{ padding: '11px 13px' }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap' }}>
              <span className="mono" style={{ fontSize: 12, color: RC.ink2 }}>{c.market}</span>
              <span className="mono" style={{ fontSize: 11, color: RC.ink4, marginLeft: 'auto' }}>
                {relTime(c.ts)}
              </span>
            </div>
            <div style={{ display: 'flex', gap: 14, marginTop: 8, flexWrap: 'wrap',
                          alignItems: 'center' }}>
              {probs.map(([o, p]) => (
                <span key={o} className="mono" style={{ fontSize: 12,
                        color: o === top?.[0] ? color : RC.ink3 }}>
                  {o} <b>{p.toFixed(3)}</b>
                </span>
              ))}
              <span className="mono" style={{ fontSize: 11, color: RC.ink4 }}>
                confidence {c.confidence?.toFixed(2)}
              </span>
              <span className="mono" style={{ fontSize: 11, color: RC.amber, marginLeft: 'auto' }}>
                spent {c.spend?.toFixed(4)}
              </span>
            </div>
            {c.reasoning && (
              <p style={{ margin: '9px 0 0', fontSize: 12, color: RC.ink3, lineHeight: 1.55 }}>
                {c.reasoning}
              </p>
            )}
            <div style={{ marginTop: 8, fontSize: 11, color: RC.ink4 }}>
              {leaned.length
                ? <>leaned on {leaned.map(s => (
                    <span key={s} className="mono" style={{ color: RC.ink2,
                            background: alpha(color, .12), padding: '2px 6px',
                            borderRadius: 5, marginRight: 5 }}>{s}</span>))}</>
                : <span>leaned on nothing — the evidence it bought did not move it</span>}
            </div>
          </div>
        )
      })}
    </div>
  )
}
