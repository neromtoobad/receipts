'use client'

// The trust map. Rows are informants, columns are domains, and a cell is what
// this pundit has learned about that pairing by paying for it.
//
// The hover panel matters as much as the grid: a colour tells you the verdict,
// but the evidence behind it — how many resolutions, how much money, how long
// since it last proved anything — is what makes the verdict believable.

import { useState } from 'react'
import { RC, alpha, cellStyle } from '../lib/theme'
import type { Cell } from '../lib/data'
import { shortDomain } from '../lib/data'

type Props = {
  cells: Record<string, Cell>
  domains: string[]
  catalogue: Record<string, { name: string; price: number; answers_on: string[] }>
}

export function TrustMap({ cells, domains, catalogue }: Props) {
  const [hover, setHover] = useState<{ key: string; src: string; dom: string } | null>(null)
  const sources = Object.keys(catalogue).sort((a, b) => catalogue[b].price - catalogue[a].price)
  const active = hover ? cells[hover.key] : null

  return (
    <div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: 0, width: '100%',
                        background: RC.surface, border: `1px solid ${RC.line}`, borderRadius: 10 }}>
          <thead>
            <tr>
              <th style={{ ...th, textAlign: 'left', width: 176, position: 'sticky', left: 0,
                           background: RC.surface2, zIndex: 1 }}>informant</th>
              {domains.map(d => (
                <th key={d} style={th} title={d}>{shortDomain(d)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sources.map(src => {
              const covers = new Set(catalogue[src].answers_on)
              return (
                <tr key={src}>
                  <th style={{ ...td, textAlign: 'left', fontWeight: 500, color: RC.ink,
                               position: 'sticky', left: 0, background: RC.surface2, zIndex: 1 }}>
                    {src}
                    <span className="mono" style={{ float: 'right', color: RC.ink4, fontSize: 11 }}>
                      {catalogue[src].price.toFixed(4)}
                    </span>
                  </th>
                  {domains.map(d => {
                    const key = `${src}|${d}`
                    const c = cells[key] ?? null
                    const s = cellStyle(c, covers.has(d))
                    const isHot = hover?.key === key
                    return (
                      <td key={d}
                          onMouseEnter={() => c && setHover({ key, src, dom: d })}
                          onMouseLeave={() => setHover(null)}
                          className="mono"
                          style={{ ...td, textAlign: 'center', background: s.bg, color: s.fg,
                                   cursor: c ? 'pointer' : 'default', fontSize: 11,
                                   outline: isHot ? `1px solid ${RC.brand}` : 'none',
                                   opacity: s.kind === 'na' ? .3 : 1 }}>
                        {s.label}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* The receipt sits under the map, not beside it. Beside it, the panel
          stole 250px from a grid that needs every pixel and the far columns
          clipped. */}
      <div style={{ background: RC.surface, border: `1px solid ${RC.line}`, borderRadius: 10,
                    padding: '12px 14px', marginTop: 10, minHeight: 88 }}>
        {!active && (
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'center',
                        color: RC.ink4, fontSize: 12 }}>
            <span className="eyebrow">the receipt</span>
            <span>Hover any cell to see what it was paid for and what it proved.</span>
            <span style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginLeft: 'auto' }}>
              <Key c={RC.green} t="trusted" />
              <Key c={RC.red} t="worse than the base rate" />
              <Key c={RC.amber} t="not yet promoted" />
              <Key c={RC.line2} t="archived" />
            </span>
          </div>
        )}
        {active && hover && (
          <div style={{ display: 'flex', gap: 26, flexWrap: 'wrap', alignItems: 'flex-start',
                        fontSize: 12 }}>
            <div style={{ minWidth: 168 }}>
              <div className="eyebrow">{hover.dom}</div>
              <div className="display" style={{ fontSize: 19, margin: '3px 0 1px' }}>{hover.src}</div>
              <div style={{ color: RC.ink4 }}>
                {catalogue[hover.src].price.toFixed(4)} USDC a call
              </div>
            </div>
            <div style={{ display: 'flex', gap: 22, flexWrap: 'wrap' }}>
              <Fact k="state" v={active.state} />
              <Fact k="resolutions" v={String(active.n)} />
              <Fact k="skill" v={active.skill == null ? '—' :
                                 `${active.skill > 0 ? '+' : ''}${active.skill.toFixed(3)}`}
                    c={active.skill == null ? RC.ink3 : active.skill > 0 ? RC.green : RC.red} />
              <Fact k="trust" v={active.trust == null ? 'unproven' : active.trust.toFixed(2)} />
              <Fact k="spent on it" v={active.spend.toFixed(4)} />
              {active.misses > 0 && <Fact k="paid, no data" v={String(active.misses)} c={RC.amber} />}
            </div>
            <p style={{ color: RC.ink4, margin: 0, lineHeight: 1.55, flex: '1 1 240px',
                        minWidth: 220 }}>
              {active.skill != null && active.skill <= 0
                ? 'Measured worse than simply knowing how often each outcome happens. It will not be bought here again.'
                : active.state === 'provisional'
                ? `Being explored. ${active.n} resolutions so far; three earns it a trust weight.`
                : 'Earned its weight by resolving better than the base rate, repeatedly.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

const th: React.CSSProperties = {
  padding: '9px 8px', fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase',
  color: RC.ink3, fontWeight: 600, borderBottom: `1px solid ${RC.line}`, background: RC.surface2,
}
const td: React.CSSProperties = {
  padding: '8px 9px', fontSize: 12, borderBottom: `1px solid ${RC.line}`, whiteSpace: 'nowrap',
}

function Fact({ k, v, c }: { k: string; v: string; c?: string }) {
  return (
    <div>
      <div className="eyebrow" style={{ fontSize: 9.5 }}>{k}</div>
      <div className="mono" style={{ color: c ?? RC.ink, fontSize: 14, marginTop: 2 }}>{v}</div>
    </div>
  )
}
function Key({ c, t }: { c: string; t: string }) {
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <i style={{ width: 11, height: 11, borderRadius: 3, background: alpha(c, .75), flex: '0 0 auto' }} />
      <span>{t}</span>
    </div>
  )
}
