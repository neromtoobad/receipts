'use client'

// The deletion test, as a picture.
//
// This is the argument the whole project rests on, and it was a monospace table.
// A 10x difference in spend should be obvious before you read a single number —
// so the bars carry it and the figures confirm it.

import { useEffect, useRef, useState } from 'react'
import { RC, alpha } from '../lib/theme'

type Arm = { name: string; note: string; spend: number; brier: number; bought: number; tone: string }

const ARMS: Arm[] = [
  { name: 'domain-scoped memory', note: 'knows who is worth paying for, and where',
    spend: 5.28, brier: 0.5658, bought: 0.55, tone: RC.green },
  { name: 'memory, no domain scoping', note: 'one global number cannot hold two lessons',
    spend: 0.89, brier: 0.5697, bought: 0.08, tone: RC.ink3 },
  { name: 'no memory', note: 'no basis to choose, no basis to stop',
    spend: 53.00, brier: 0.5664, bought: 4.50, tone: RC.red },
]
const MAX = 53

export function DeletionChart() {
  const [shown, setShown] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  // Grow the bars when they scroll into view: the 10x gap lands harder as a
  // movement than as a static length.
  //
  // But NEVER let the animation be the reason a number is invisible. On a short
  // viewport the chart may never clear the threshold, and a bar stuck at zero
  // width is a chart showing nothing. So a timer draws them regardless, and the
  // observer only ever makes it arrive earlier.
  useEffect(() => {
    const t = setTimeout(() => setShown(true), 700)
    const el = ref.current
    if (!el) return () => clearTimeout(t)
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { setShown(true); io.disconnect() }
    }, { threshold: .12 })
    io.observe(el)
    return () => { clearTimeout(t); io.disconnect() }
  }, [])

  return (
    <div ref={ref} style={{ display: 'grid', gap: 14 }}>
      {ARMS.map(a => {
        const pct = (a.spend / MAX) * 100
        return (
          <div key={a.name}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6,
                          flexWrap: 'wrap' }}>
              <span style={{ fontSize: 13.5, color: a.tone, fontWeight: 600 }}>{a.name}</span>
              <span style={{ fontSize: 12, color: RC.ink4 }}>{a.note}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ flex: 1, height: 34, background: alpha(RC.ink, .04),
                            borderRadius: 7, overflow: 'hidden', position: 'relative' }}>
                <div style={{
                  width: shown ? `${pct}%` : '0%', height: '100%',
                  background: `linear-gradient(90deg, ${alpha(a.tone, .30)}, ${alpha(a.tone, .72)})`,
                  boxShadow: `inset 0 0 0 1px ${alpha(a.tone, .45)}`,
                  borderRadius: 7,
                  transition: 'width 1100ms cubic-bezier(.16,1,.3,1)',
                }} />
                <span className="mono" style={{ position: 'absolute', left: 12, top: 0,
                        lineHeight: '34px', fontSize: 14, fontWeight: 700,
                        color: RC.ink, textShadow: '0 1px 3px rgba(0,0,0,.7)' }}>
                  ${a.spend.toFixed(2)}
                </span>
              </div>
              <div style={{ display: 'flex', gap: 16, flex: '0 0 auto' }}>
                <Metric k="bought / call" v={a.bought.toFixed(2)} />
                <Metric k="brier" v={a.brier.toFixed(4)} />
              </div>
            </div>
          </div>
        )
      })}
      <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', marginTop: 4,
                    flexWrap: 'wrap' }}>
        <span className="display" style={{ fontSize: 34, color: RC.brand, lineHeight: 1 }}>10.0×</span>
        <span style={{ fontSize: 13.5, color: RC.ink2 }}>
          the spend, for the same forecast. Football alone 6.0×, crypto alone <b>67×</b>.
        </span>
      </div>
    </div>
  )
}

function Metric({ k, v }: { k: string; v: string }) {
  return (
    <div style={{ minWidth: 74 }}>
      <div className="eyebrow" style={{ fontSize: 9 }}>{k}</div>
      <div className="mono" style={{ fontSize: 13, color: RC.ink2, marginTop: 1 }}>{v}</div>
    </div>
  )
}
