'use client'

// What the league is doing, newest first. Purchases, calls, resolutions and
// promotions in one stream, because the story is the sequence: it bought this,
// it called that, reality disagreed, it changed its mind.

import { useState } from 'react'
import { RC, alpha } from '../lib/theme'
import { identityOf } from '../lib/pundits'
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
      {/* Four columns of market ids do not fit a phone. Below 560 the row
          becomes two lines: who and what kind, then the market itself. */}
      <style>{`
        .feed-when{ width:62px } .feed-who{ width:66px } .feed-kind{ width:66px }
        .feed-what{ min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
        @media (max-width:560px){
          .feed-row{ flex-wrap:wrap; gap:8px }
          .feed-kind{ width:auto }
          .feed-what{ flex:1 0 100%; white-space:normal; overflow:visible;
            text-overflow:clip; word-break:break-word }
        }
      `}</style>
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
            <div key={n} className="feed-row" style={{ display: 'flex', gap: 10, padding: '9px 13px',
                                  borderBottom: `1px solid ${RC.line}`, fontSize: 12,
                                  alignItems: 'baseline' }}>
              <span className="mono feed-when" style={{ color: RC.ink4, flex: '0 0 auto' }}>
                {relTime(it.ts)}
              </span>
              <span className="mono feed-who" style={{ color: RC.ink3, flex: '0 0 auto' }}>
                {identityOf(it.pundit).name}
              </span>
              <span className="feed-kind" style={{ color: k.c, flex: '0 0 auto' }}>{k.label}</span>
              <span className="feed-what" style={{ color: RC.ink2 }}>
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
