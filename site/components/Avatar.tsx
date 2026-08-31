'use client'

// A procedural sigil per pundit. Deterministic from the name, so it is stable
// across rebuilds, and drawn inline so the page stays self-contained — no
// external image can 404 during a demo.
//
// It is a ticket stub: this project is called RECEIPTS.

export function Avatar({ name, color, size = 46, portrait }:
  { name: string; color: string; size?: number; portrait?: string }) {
  if (portrait) {
    const base = process.env.NODE_ENV === 'production' ? '/receipts' : ''
    return (
      <img src={`${base}${portrait}`} alt="" width={size} height={size}
           style={{ borderRadius: 9, flex: '0 0 auto', objectFit: 'cover',
                    border: `1px solid ${color}55`,
                    boxShadow: `0 0 0 1px rgba(0,0,0,.5), 0 6px 18px rgba(0,0,0,.45)` }} />
    )
  }
  return <Sigil name={name} color={color} size={size} />
}

/** Fallback mark, drawn inline, so a missing portrait never blanks a card. */
function Sigil({ name, color, size }: { name: string; color: string; size: number }) {
  let h = 0
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  const rows = 5, cols = 5
  const cells: boolean[] = []
  for (let i = 0; i < rows * cols; i++) cells.push(((h >> (i % 30)) & 1) === 1)

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden
         style={{ borderRadius: 9, background: 'rgba(255,255,255,.035)', flex: '0 0 auto',
                  border: `1px solid ${color}44` }}>
      {/* perforated stub edge */}
      {Array.from({ length: 7 }).map((_, i) => (
        <circle key={i} cx={4} cy={10 + i * 13.5} r={2.2} fill="rgba(0,0,0,.5)" />
      ))}
      <g transform="translate(16,16)">
        {cells.map((on, i) => {
          const c = i % cols, r = Math.floor(i / cols)
          // mirror so the sigil reads as a face/mark rather than noise
          const mirrored = c > 2 ? cells[r * cols + (4 - c)] : on
          return mirrored ? (
            <rect key={i} x={c * 14} y={r * 14} width={12} height={12} rx={2.5}
                  fill={color} opacity={0.35 + ((h >> i) & 3) * 0.2} />
          ) : null
        })}
      </g>
    </svg>
  )
}
