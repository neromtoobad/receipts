'use client'

// The cast, with the portraits at the size they deserve.
//
// They were 58px thumbnails, which wasted the only real imagery on the page.
// Full-bleed portrait, the agent's colour on the border and the accent, and its
// record underneath — the same shape a reader already understands from a squad
// list or a set of trading cards.

import { RC, alpha } from '../lib/theme'
import type { Pundit } from '../lib/data'
import { divergence, identityOf, readOf } from '../lib/pundits'

const BASE = process.env.NODE_ENV === 'production' ? '/receipts' : ''

export function AgentCards({ pundits, selected, onSelect }:
  { pundits: Pundit[]; selected: string; onSelect: (id: string) => void }) {

  const ranked = [...pundits].sort((a, b) => (a.brier ?? 99) - (b.brier ?? 99))
  const converged = pundits.every(p => divergence(p, pundits) === 0)

  return (
    <>
      {converged && (
        <div className="card" style={{ borderLeft: `3px solid ${RC.amber}`, padding: '11px 14px',
                                       marginBottom: 16, fontSize: 12.5, color: RC.ink3 }}>
          <b style={{ color: RC.ink2 }}>All six believe the same things right now.</b> They run the
          same model on the same prompt, so until they have paid for different informants and
          reality has answered, they are the same agent six times. Divergence is earned.
        </div>
      )}
      <div style={{ display: 'grid', gap: 14,
                    gridTemplateColumns: 'repeat(auto-fill,minmax(212px,1fr))' }}>
        {ranked.map((p, i) => {
          const id = identityOf(p.id)
          const on = p.id === selected
          const cells = Object.values(p.cells)
          const trusted = cells.filter(c => (c.skill ?? 0) > 0).length
          const burned = cells.filter(c => c.skill != null && c.skill <= 0).length
          const best = cells.filter(c => (c.skill ?? 0) > 0)
                            .sort((a, b) => (b.skill ?? 0) - (a.skill ?? 0))[0]
          return (
            <button key={p.id} onClick={() => onSelect(p.id)} className="lift"
              style={{ padding: 0, textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit',
                       background: RC.surface, borderRadius: 13, overflow: 'hidden',
                       border: `1px solid ${on ? alpha(id.color, .6) : RC.line}`,
                       boxShadow: on ? `0 0 0 1px ${alpha(id.color, .25)}, 0 20px 46px -26px ${id.color}`
                                     : undefined }}>
              <div style={{ position: 'relative', aspectRatio: '1/1', overflow: 'hidden' }}>
                <img src={`${BASE}${id.portrait}`} alt="" width={420} height={420}
                     style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                <div style={{ position: 'absolute', inset: 0,
                              background: `linear-gradient(180deg, transparent 42%, ${RC.surface} 97%)` }} />
                {i === 0 && p.brier != null && (
                  <span className="mono" style={{ position: 'absolute', top: 9, left: 9,
                          fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase',
                          background: alpha(RC.brand, .9), color: '#17120A',
                          padding: '3px 7px', borderRadius: 5, fontWeight: 700 }}>leading</span>
                )}
                <div style={{ position: 'absolute', left: 12, right: 12, bottom: 9 }}>
                  <div className="display" style={{ fontSize: 20, color: RC.ink,
                                                    letterSpacing: '.03em' }}>{id.name}</div>
                  <div className="mono" style={{ fontSize: 11, color: id.color }}>
                    {p.brier == null ? 'no record yet' : `brier ${p.brier.toFixed(4)}`}
                  </div>
                </div>
              </div>

              <div style={{ padding: '11px 13px 13px' }}>
                <p style={{ margin: 0, fontSize: 11.5, color: RC.ink3, lineHeight: 1.5,
                            minHeight: 52 }}>
                  {best
                    ? <>Rates <b style={{ color: RC.ink2 }}>{best.source}</b> on {best.domain} at{' '}
                        <span className="mono" style={{ color: RC.green }}>
                          {best.skill! > 0 ? '+' : ''}{best.skill!.toFixed(2)}</span>.
                        Spends {(p.forecasts ? p.spend / p.forecasts : 0).toFixed(4)} a call.</>
                    : readOf(p)}
                </p>
                <div style={{ display: 'flex', gap: 9, marginTop: 10, paddingTop: 9,
                              borderTop: `1px solid ${RC.line}`, fontSize: 10.5,
                              color: RC.ink4, alignItems: 'center' }}>
                  <span className="mono">{p.resolutions} resolved</span>
                  <span style={{ marginLeft: 'auto' }}>
                    {trusted > 0 && <b className="mono" style={{ color: RC.green }}>{trusted}✓ </b>}
                    {burned > 0 && <b className="mono" style={{ color: RC.red }}>{burned}✕</b>}
                  </span>
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </>
  )
}
