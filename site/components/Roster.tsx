'use client'

// The roster. Six cards, one per pundit, each showing what it has actually
// done rather than a personality it was handed.
//
// The subtitle on every card is computed from its own record — which informant
// it rates, what it has written off, what it spends. Two pundits with the same
// record read the same, which is the honest outcome: they are the same agent
// until experience separates them.

import { RC, alpha } from '../lib/theme'
import type { Pundit } from '../lib/data'
import { divergence, identityOf, readOf } from '../lib/pundits'
import { Avatar } from './Avatar'

export function Roster({ pundits, selected, onSelect }:
  { pundits: Pundit[]; selected: string; onSelect: (id: string) => void }) {

  const ranked = [...pundits].sort((a, b) =>
    (a.brier ?? 99) - (b.brier ?? 99) || a.spend - b.spend)
  const converged = pundits.every(p => divergence(p, pundits) === 0)

  return (
    <>
    {converged && (
      <div style={{ background: RC.surface, border: `1px solid ${RC.line}`,
                    borderLeft: `3px solid ${RC.amber}`, borderRadius: 8,
                    padding: '11px 14px', marginBottom: 12, fontSize: 12.5,
                    color: RC.ink3, lineHeight: 1.6 }}>
        <b style={{ color: RC.ink2 }}>All six believe exactly the same things right now.</b>{' '}
        That is not a bug and it is the whole point: they run the same model on the same
        prompt, so until they have paid for different informants and reality has answered,
        they are the same agent six times. Divergence is earned, and it shows up here first.
      </div>
    )}
    <div style={{ display: 'grid', gap: 10,
                  gridTemplateColumns: 'repeat(auto-fill,minmax(272px,1fr))' }}>
      {ranked.map((p, i) => {
        const id = identityOf(p.id)
        const on = p.id === selected
        const cells = Object.values(p.cells)
        const trusted = cells.filter(c => (c.skill ?? 0) > 0).length
        const burned = cells.filter(c => c.skill != null && c.skill <= 0).length
        return (
          <button key={p.id} onClick={() => onSelect(p.id)}
            style={{ textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit',
                     background: on ? alpha(id.color, .07) : RC.surface,
                     border: `1px solid ${on ? alpha(id.color, .5) : RC.line}`,
                     borderRadius: 11, padding: 13, display: 'grid', gap: 10,
                     boxShadow: on ? `0 0 0 1px ${alpha(id.color, .18)}` : 'none' }}>
            <div style={{ display: 'flex', gap: 11, alignItems: 'center' }}>
              <Avatar name={id.name} color={id.color} portrait={id.portrait} size={58} />
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 7 }}>
                  <span className="display" style={{ fontSize: 17, color: RC.ink,
                                                     letterSpacing: '.02em' }}>{id.name}</span>
                  <span className="mono" style={{ fontSize: 10, color: RC.ink4 }}>{p.id}</span>
                </div>
                <div className="mono" style={{ fontSize: 11, color: id.color, marginTop: 2 }}>
                  {p.brier == null ? 'no record yet' : `brier ${p.brier.toFixed(4)}`}
                  {i === 0 && p.brier != null && (
                    <span style={{ color: RC.ink4 }}> · leading</span>
                  )}
                </div>
              </div>
            </div>

            <p style={{ margin: 0, fontSize: 12, color: RC.ink3, lineHeight: 1.5,
                        minHeight: 36 }}>
              {readOf(p)}
            </p>

            <div style={{ display: 'flex', gap: 12, fontSize: 11, color: RC.ink4,
                          borderTop: `1px solid ${RC.line}`, paddingTop: 9 }}>
              <span className="mono">{p.forecasts} calls</span>
              <span className="mono">{p.resolutions} resolved</span>
              <span className="mono">{p.spend.toFixed(3)} USDC</span>
              <span style={{ marginLeft: 'auto' }}>
                {trusted > 0 && <b className="mono" style={{ color: RC.green }}>{trusted}✓ </b>}
                {burned > 0 && <b className="mono" style={{ color: RC.red }}>{burned}✕</b>}
              </span>
            </div>
          </button>
        )
      })}
    </div>
    </>
  )
}
