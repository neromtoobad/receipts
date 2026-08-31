/** RECEIPTS — "Viewing Centre", one theme, no toggle.
 *
 *  A dim room lit by a screen. Warm near-black, receipt-paper ink, and a ledger
 *  palette that has to survive being a heatmap: green where trust was earned,
 *  oxblood where it was burned, amber where it is still being paid for.
 *
 *  Heatmap colours are the product here, not decoration, so they are defined
 *  once and used everywhere. A cell you cannot read at a glance is a cell that
 *  tells the story wrong.
 */
export const RC = {
  bg: '#0A0908',
  surface: '#121010',
  surface2: '#1A1716',
  surface3: '#231F1D',
  ink: '#F4EDE2',
  ink2: '#D6CCBC',
  ink3: '#9C9184',
  ink4: '#665E55',
  line: '#262120',
  line2: '#38312E',

  green: '#35C47F',
  greenTint: '#0D2A1D',
  greenInk: '#A9EBC9',
  red: '#E05545',
  redTint: '#2C1310',
  redInk: '#FFC5BC',
  amber: '#E8A33D',
  amberTint: '#2A1F0E',
  amberInk: '#F7D9A4',

  brand: '#E8A33D',
  shadow: '0 1px 2px rgba(0,0,0,.55)',
  shadowPop: '0 18px 44px rgba(0,0,0,.7), 0 0 0 1px rgba(232,163,61,.10)',
} as const

export const alpha = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16)
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`
}

/** One place decides what a cell looks like, so the map and the legend can
 *  never disagree about what a colour means. */
export type CellState = 'established' | 'provisional' | 'archived' | 'none' | 'na'

export function cellStyle(
  c: { state?: string; trust?: number | null; skill?: number | null; n?: number } | null,
  covers: boolean,
) {
  if (!covers) return { bg: 'transparent', fg: RC.ink4, label: '', kind: 'na' as CellState }
  if (!c) return { bg: 'transparent', fg: RC.ink4, label: '', kind: 'none' as CellState }
  if (c.state === 'archived')
    return { bg: `repeating-linear-gradient(45deg,${RC.line2},${RC.line2} 4px,transparent 4px,transparent 9px)`,
             fg: RC.ink3, label: 'arch', kind: 'archived' as CellState }
  if (c.state === 'provisional')
    return { bg: alpha(RC.amber, .22), fg: RC.amberInk, label: `n${c.n ?? 0}`, kind: 'provisional' as CellState }
  const skill = c.skill ?? 0
  if (skill <= 0)
    return { bg: alpha(RC.red, .42), fg: RC.redInk, label: skill.toFixed(2), kind: 'established' as CellState }
  const t = c.trust ?? 0
  return { bg: alpha(RC.green, .14 + .66 * Math.min(t, 1)), fg: RC.greenInk,
           label: t.toFixed(2), kind: 'established' as CellState }
}
