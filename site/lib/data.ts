import league from '../../web/data/league.json'

export type Cell = {
  source: string; domain: string; n: number
  skill: number | null; trust: number | null
  spend: number; misses: number; state: string; last_seen: string | null
}
export type FeedItem = {
  ts: string; kind: string; pundit: string
  source?: string; domain?: string; cost?: number; trust?: number | null
  market?: string; probabilities?: Record<string, number>; confidence?: number
  reasoning?: string; leaned_on?: string[]; spend?: number
  outcome?: string; brier?: number; sources?: string[]; skill?: number
}
export type Pundit = {
  id: string; forecasts: number; resolutions: number; spend: number; buys: number
  brier: number | null; cells: Record<string, Cell>; memory_pct: number
}
export type League = {
  generated: string
  domains: string[]
  catalogue: Record<string, { name: string; blurb: string; price: number; answers_on: string[] }>
  constants: { promote_n: number; skill_full_trust: number; trust_shrink: number }
  pundits: Pundit[]
  feed: FeedItem[]
  totals: { forecasts: number; resolutions: number; spend: number; buys: number }
}

export const LEAGUE = league as unknown as League

export const shortDomain = (d: string) =>
  d.replace('crypto_', '').replace('championship', 'champ').replace('bundesliga', 'bundes')

export const relTime = (iso: string) => {
  const s = (Date.now() - new Date(iso).getTime()) / 1000
  if (s < 60) return `${Math.floor(s)}s ago`
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`
  return `${Math.floor(s / 86400)}d ago`
}
