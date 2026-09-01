import { RC } from '../lib/theme'

/** Nav, logo and a way out to the code. The page had none of these, which is
 *  most of why it read as a document rather than a product. */
export function Nav() {
  const link = { color: RC.ink3, fontSize: 13.5, transition: 'color 180ms' } as const
  return (
    <nav style={{ position: 'sticky', top: 0, zIndex: 20,
                  background: 'rgba(10,9,8,.72)', backdropFilter: 'blur(14px)',
                  borderBottom: `1px solid ${RC.line}` }}>
      <div className="wrap" style={{ display: 'flex', alignItems: 'center', gap: 22,
                                     height: 58 }}>
        <a href="#top" style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <Mark />
          <span className="mono" style={{ fontSize: 13.5, letterSpacing: '.16em',
                                          color: RC.ink, fontWeight: 700 }}>RECEIPTS</span>
        </a>
        <div style={{ display: 'flex', gap: 20, marginLeft: 18 }} className="nav-links">
          <a href="#agents" style={link}>Agents</a>
          <a href="#proof" style={link}>The deletion test</a>
          <a href="#maps" style={link}>Trust maps</a>
          <a href="#how" style={link}>How it works</a>
        </div>
        <a className="btn btn-ghost" style={{ marginLeft: 'auto', padding: '7px 14px' }}
           href="https://github.com/neromtoobad/receipts">View the code</a>
      </div>
      <style>{`@media (max-width:820px){ .nav-links{display:none} }`}</style>
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
