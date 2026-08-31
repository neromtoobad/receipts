/** Who the pundits are.
 *
 *  IMPORTANT, and the copy on the page must keep saying it: all six run the
 *  same model with the same prompt on the same budget. These names and colours
 *  are labels, not personalities — nothing here makes one behave differently
 *  from another.
 *
 *  What actually differentiates them is derived from their own record: what
 *  they have paid for, what they came to trust, what burned them. They start
 *  identical and diverge because they bought different things and reality
 *  answered. That divergence is the product, so the page shows the derivation
 *  rather than asserting a character.
 *
 *  The names are drawn from forecasting and record-keeping, because that is the
 *  whole job: call it, write it down, and be held to it.
 */
import type { Cell, Pundit } from './data'

export type Identity = { id: string; name: string; color: string; seat: string; portrait: string }

export const PUNDITS: Identity[] = [
  { id: 'pundit_1', name: 'AUGUR',  color: '#E8A33D', seat: 'seat one',   portrait: '/pundits/augur.png' },
  { id: 'pundit_2', name: 'CIPHER', color: '#59B7E8', seat: 'seat two',   portrait: '/pundits/cipher.png' },
  { id: 'pundit_3', name: 'TALLY',  color: '#35C47F', seat: 'seat three', portrait: '/pundits/tally.png' },
  { id: 'pundit_4', name: 'QUORUM', color: '#C77DD8', seat: 'seat four',  portrait: '/pundits/quorum.png' },
  { id: 'pundit_5', name: 'VERTEX', color: '#E0645A', seat: 'seat five',  portrait: '/pundits/vertex.png' },
  { id: 'pundit_6', name: 'LEDGER', color: '#8FBF52', seat: 'seat six',   portrait: '/pundits/ledger.png' },
]

export const identityOf = (id: string): Identity =>
  PUNDITS.find(p => p.id === id) ??
  { id, name: id.toUpperCase(), color: '#9C9184', seat: '', portrait: '' }

/** How far this pundit has drifted from the rest, measured on what it believes.
 *  Early on the answer is zero, and saying so is more honest — and a better
 *  story — than dressing six identical records up as six characters. */
export function divergence(p: Pundit, all: Pundit[]): number {
  const sig = (x: Pundit) => Object.entries(x.cells)
    .map(([k, c]) => `${k}:${(c.skill ?? 0) > 0 ? 'T' : 'B'}`).sort().join(',')
  const mine = sig(p)
  return all.filter(o => o.id !== p.id && sig(o) !== mine).length
}

/** A one-line read of a pundit, computed from its record. Never invented. */
export function readOf(p: Pundit): string {
  const cells = Object.values(p.cells)
  if (!cells.length)
    return p.forecasts
      ? `${p.forecasts} calls placed, nothing resolved yet. It has opinions and no record.`
      : 'Has not called anything yet.'

  const trusted = cells.filter(c => (c.skill ?? 0) > 0)
      .sort((a, b) => (b.skill ?? 0) - (a.skill ?? 0))
  const burned = cells.filter(c => c.skill != null && c.skill <= 0)
  const perCall = p.forecasts ? p.spend / p.forecasts : 0

  // Lead with what actually differs between seats. Early in a league that is
  // spend and volume, not taste, because taste has not had time to form.
  const bits: string[] = [`${perCall.toFixed(4)} USDC a call across ${p.forecasts}`]
  if (trusted.length) bits.push(`rates ${trusted[0].source} on ${trusted[0].domain}`)
  if (burned.length) {
    bits.push(burned.length === 1
      ? `dropped ${burned[0].source}`
      : `dropped ${burned.length} informants`)
  }
  return bits.join(' · ') + '.'
}

/** Standing, by the metric that actually matters: forecast quality per dollar. */
export function rankOf(p: Pundit): number {
  if (p.brier == null) return Infinity
  return p.brier
}

export function initials(name: string): string {
  return name.slice(0, 2)
}
