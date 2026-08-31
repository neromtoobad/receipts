'use client'

// What the league is doing, newest first. Purchases, calls, resolutions and
// promotions in one stream, because the story is the sequence: it bought this,
// it called that, reality disagreed, it changed its mind.

import { useState } from 'react'
import { RC, alpha } from '../lib/theme'
import type { FeedItem } from '../lib/data'
import { relTime } from '../lib/data'

const KINDS: Record<string, { c: string; label: string }> = {
  buy: { c: RC.amber, label: 'bought' },
  forecast: { c: RC.ink2, label: 'called' },
  resolved: { c: RC.green, label: 'resolved' },
  promotion: { c: RC.green, label: 'promoted' },
  archive: { c: RC.ink3, label: 'archived' },
}

export function Feed({ items }: { items: FeedItem[] }) {
  const [filter, setFilter] = useState<string>('all')
  const shown = items.filter(i => filter === 'all' || i.kind === filter).slice(0, 60)

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <div style={{ display: 'flex', gap: 6, padding: 10, borderBottom: `1px solid ${RC.line}`,
                    flexWrap: 'wrap' }}>
        {['all', 'buy', 'forecast', 'resolved', 'promotion'].map(k => (
          <button key={k} onClick={() => setFilter(k)}
            style={{ background: filter === k ? alpha(RC.brand, .16) : 'transparent',
                     color: filter === k ? RC.brand : RC.ink3,
                     border: `1px solid ${filter === k ? alpha(RC.brand, .4) : RC.line}`,
                     borderRadius: 999, padding: '4px 11px', fontSize: 11, cursor: 'pointer',
                     fontFamily: 'inherit' }}>
            {k === 'all' ? 'everything' : KINDS[k]?.label ?? k}
          </button>
        ))}
      </div>
      <div style={{ maxHeight: 460, overflowY: 'auto' }}>
        {shown.length === 0 && (
          <div style={{ padding: 18, color: RC.ink4, fontSize: 13 }}>nothing yet</div>
        )}
        {shown.map((it, n) => {
          const k = KINDS[it.kind] ?? { c: RC.ink3, label: it.kind }
          return (
            <div key={n} style={{ display: 'flex', gap: 10, padding: '9px 13px',
                                  borderBottom: `1px solid ${RC.line}`, fontSize: 12,
                                  alignItems: 'baseline' }}>
              <span className="mono" style={{ color: RC.ink4, width: 62, flex: '0 0 auto' }}>
                {relTime(it.ts)}
              </span>
              <span className="mono" style={{ color: RC.ink3, width: 66, flex: '0 0 auto' }}>
                {it.pundit}
              </span>
              <span style={{ color: k.c, width: 66, flex: '0 0 auto' }}>{k.label}</span>
              <span style={{ color: RC.ink2, minWidth: 0, overflow: 'hidden',
                             textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {it.kind === 'buy' && <>
                  <b style={{ color: RC.ink }}>{it.source}</b>
                  <span className="mono" style={{ color: RC.ink4 }}> {it.cost?.toFixed(4)} </span>
                  {it.trust != null
                    ? <span className="mono" style={{ color: RC.green }}>trust {it.trust.toFixed(2)}</span>
                    : <span style={{ color: RC.ink4 }}>unproven</span>}
                </>}
                {it.kind === 'forecast' && <>
                  {it.market} <span className="mono" style={{ color: RC.ink4 }}>
                    {it.probabilities && Object.entries(it.probabilities)
                      .map(([o, p]) => `${o} ${p.toFixed(2)}`).join('  ')}
                  </span>
                </>}
                {it.kind === 'resolved' && <>
                  {it.market} → <b className="mono" style={{ color: RC.green }}>{it.outcome}</b>
                  <span className="mono" style={{ color: RC.ink4 }}> brier {it.brier?.toFixed(3)}</span>
                </>}
                {it.kind === 'promotion' && <>
                  <b>{it.source}</b> on {it.domain}
                  <span className="mono" style={{ color: RC.green }}> skill {it.skill?.toFixed(3)}</span>
                </>}
                {it.kind === 'archive' && <><b>{it.source}</b> on {it.domain} went quiet</>}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
