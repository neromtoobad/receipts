'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { RC, alpha } from '../lib/theme'

/** Nav, logo and a way out to the code. The page had none of these, which is
 *  most of why it read as a document rather than a product. */
const LINKS = [
  { href: '/agents', label: 'Agents' },
  { href: '/proof', label: 'The deletion test' },
  { href: '/live', label: 'Live' },
]

export function Nav() {
  const path = usePathname() || '/'
  return (
    <nav style={{ position: 'sticky', top: 0, zIndex: 20,
                  background: 'rgba(10,9,8,.72)', backdropFilter: 'blur(14px)',
                  borderBottom: `1px solid ${RC.line}` }}>
      <div className="wrap nav-row">
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <Mark />
          <span className="mono" style={{ fontSize: 13.5, letterSpacing: '.16em',
                                          color: RC.ink, fontWeight: 700 }}>RECEIPTS</span>
        </Link>
        <div className="nav-links scroll-x">
          {LINKS.map(l => {
            const on = path.startsWith(l.href)
            return (
              <Link key={l.href} href={l.href}
                style={{ color: on ? RC.ink : RC.ink3,
                         background: on ? alpha(RC.brand, .12) : 'transparent' }}>{l.label}</Link>
            )
          })}
        </div>
        <a className="btn btn-ghost nav-code" href="https://github.com/neromtoobad/receipts">
          <span className="nav-code-long">View the code</span>
          <span className="nav-code-short">Code</span>
        </a>
      </div>
      {/* The links used to be hidden below 820px, which left a phone with a
          logo and no way through the site. They stay, and scroll if they must.
          Every rule that a breakpoint has to change lives here rather than
          inline, because an inline style beats a media query. */}
      <style>{`
        .nav-row{ display:flex; align-items:center; gap:22px; height:58px }
        .nav-links{ display:flex; gap:4px; margin-left:16px; min-width:0 }
        .nav-links a{ font-size:13.5px; padding:6px 11px; border-radius:7px; white-space:nowrap;
          transition:color 180ms, background 180ms }
        .nav-code{ margin-left:auto; padding:7px 14px; flex:0 0 auto }
        .nav-code-short{ display:none }
        @media (max-width:820px){
          .nav-row{ gap:10px; height:54px }
          .nav-links{ margin-left:4px; gap:2px }
          .nav-links a{ font-size:12.5px; padding:6px 8px }
          .nav-code{ padding:8px 12px; font-size:12.5px }
          .nav-code-long{ display:none }
          .nav-code-short{ display:inline }
        }
      `}</style>
    </nav>
  )
}

/** A torn receipt stub. Drawn inline: no asset to 404. */
function Mark() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden>
      <path d="M4 2h16v18l-2.7-1.6L14.6 20l-2.6-1.6L9.4 20l-2.7-1.6L4 20z"
            fill="none" stroke={RC.brand} strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M8 8h8M8 12h5" stroke={RC.brand} strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  )
}
