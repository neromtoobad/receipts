import { RC, alpha } from '../lib/theme'

const STEPS = [
  { k: 'It boots knowing nothing', v: 'Fresh process, empty context. Everything it knows it reads back from disk in 42 milliseconds.' },
  { k: 'It decides what to buy', v: 'Evidence costs real money over x402 on Base. It spends only where its own record says a source earns its price.' },
  { k: 'It calls, then it dies', v: 'One forecast, then exit(0). No state survives the process boundary, which is what makes this a memory test rather than a context-window test.' },
  { k: 'Reality answers', v: 'The resolver scores the outcome and writes it back to every informant consulted, scoped to that domain.' },
  { k: 'The map changes', v: 'Three resolutions promote a source. Silence archives it. What it believes is only ever what it paid to learn.' },
  { k: 'It hires its rivals', v: 'Once the league rates a peer, its take goes on the shelf beside the informants — bought through the same 402.' },
]

export function HowItWorks() {
  return (
    <div style={{ display: 'grid', gap: 12,
                  gridTemplateColumns: 'repeat(auto-fill,minmax(268px,1fr))' }}>
      {STEPS.map((s, i) => (
        <div key={s.k} className="card lift" style={{ padding: '15px 16px' }}>
          <div className="mono" style={{ fontSize: 11, color: RC.brand, marginBottom: 7 }}>
            {String(i + 1).padStart(2, '0')}
          </div>
          <div style={{ fontSize: 14.5, color: RC.ink, fontWeight: 600, marginBottom: 5 }}>{s.k}</div>
          <div style={{ fontSize: 12.5, color: RC.ink3, lineHeight: 1.6 }}>{s.v}</div>
        </div>
      ))}
    </div>
  )
}
