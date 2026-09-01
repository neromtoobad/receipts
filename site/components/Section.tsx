import { RC } from '../lib/theme'

/** Eyebrow, serif headline, lede. The page had no section rhythm at all, which
 *  is why it scrolled like a document instead of reading like a product. */
export function Section({ id, eyebrow, title, accent, lede, children }: {
  id?: string; eyebrow: string; title: React.ReactNode; accent?: React.ReactNode
  lede?: React.ReactNode; children: React.ReactNode
}) {
  return (
    <section id={id} className="sect">
      <div className="eyebrow" style={{ color: RC.brand }}>{eyebrow}</div>
      <h2 className="serif h-sect">
        {title}{accent && <> <span style={{ color: RC.brand }}>{accent}</span></>}
      </h2>
      {lede && <p className="lede" style={{ margin: '0 0 22px' }}>{lede}</p>}
      {children}
    </section>
  )
}
