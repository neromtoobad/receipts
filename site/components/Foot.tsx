import { RC } from '../lib/theme'

export function Foot({ generated }: { generated: string }) {
  return (
    <footer style={{ borderTop: `1px solid ${RC.line}`, padding: '24px 0 64px' }}>
      <div className="wrap" style={{ display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 12,
                                     color: RC.ink4 }}>
        <a href="https://github.com/neromtoobad/receipts" style={{ color: RC.ink3 }}>repo</a>
        <span>Generated {generated.slice(0, 16).replace('T', ' ')}Z from the pundit SQLite stores</span>
        <span style={{ marginLeft: 'auto' }}>MIT</span>
      </div>
    </footer>
  )
}
