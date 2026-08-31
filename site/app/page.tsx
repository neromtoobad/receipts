import { RC, alpha } from '../lib/theme'
import { LEAGUE } from '../lib/data'
import { League } from '../components/League'
import punditFrames from '../../web/data/league.json'

export default function Home() {
  const L = LEAGUE
  const frames: Record<string, any[]> = Object.fromEntries(
    (punditFrames as any).pundits.map((p: any) => [p.id, p.frames ?? []]))

  return (
    <>
      <header style={{ borderBottom: `1px solid ${RC.line}`, padding: '56px 0 34px' }}>
        <div className="wrap">
          <div className="eyebrow" style={{ color: RC.brand }}>Sibyl Labs Hackathon</div>
          <h1 className="display" style={{ fontSize: 'clamp(40px,7vw,74px)', margin: '10px 0 4px',
                                           fontWeight: 700, lineHeight: .96 }}>RECEIPTS</h1>
          <p style={{ fontSize: 18, color: RC.ink2, maxWidth: 720, margin: '10px 0 0',
                      lineHeight: 1.5 }}>
            In every viewing centre on earth the loudest man is never wrong, because nobody keeps
            records. <b style={{ color: RC.ink }}>This keeps records.</b>
          </p>
          <p style={{ fontSize: 15, color: RC.ink3, maxWidth: 720, marginTop: 12, lineHeight: 1.6 }}>
            Six agents forecast real matches and real markets. Same model, same prompt, same budget.
            Every piece of evidence costs real money, bought from informants on Base. Nobody tells
            them which informant is any good — they find out by getting it wrong and paying for it.
            The process dies after every forecast, so the only thing that survives is what it wrote
            to memory.
          </p>
          <div style={{ display: 'flex', gap: 26, flexWrap: 'wrap', marginTop: 26 }}>
            <Stat k="calls on record" v={String(L.totals.forecasts)} />
            <Stat k="resolved" v={String(L.totals.resolutions)} />
            <Stat k="informants bought" v={String(L.totals.buys)} />
            <Stat k="spent on evidence" v={`${L.totals.spend.toFixed(4)}`} unit="USDC" />
          </div>
        </div>
      </header>

      <div className="wrap" style={{ padding: '34px 24px 80px' }}>
        <section className="card" style={{ padding: 20, marginBottom: 40,
                                           borderColor: alpha(RC.brand, .28) }}>
          <div className="eyebrow" style={{ color: RC.brand }}>the deletion test</div>
          <p style={{ margin: '10px 0 16px', fontSize: 15, color: RC.ink2, maxWidth: 760,
                      lineHeight: 1.6 }}>
            Same agent, same market, same model, same prompt. Delete the memory and it buys ten
            times as many informants and spends ten times as much, for the same forecast.
            1,000 held-out events, 3,000 local model calls, zero failures.
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table className="mono" style={{ borderCollapse: 'collapse', fontSize: 13, minWidth: 520 }}>
              <thead><tr>
                {['arm', 'bought / call', 'spend / call', '1,000 calls', 'brier'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '7px 16px 7px 0', color: RC.ink3,
                                       fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase',
                                       borderBottom: `1px solid ${RC.line}` }}>{h}</th>))}
              </tr></thead>
              <tbody>
                <Arm n="domain-scoped memory" a="0.56" b="0.0053" c="$5.34" d="0.5653" hi />
                <Arm n="memory, no domain scoping" a="0.10" b="0.0010" c="$1.04" d="0.5691" />
                <Arm n="no memory" a="4.50" b="0.0530" c="$53.00" d="0.5667" bad />
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: 12.5, color: RC.ink4, marginTop: 14, maxWidth: 760, lineHeight: 1.6 }}>
            9.9x on spend. Football alone 6.0x, crypto alone 67x, where the memory arm learns there
            is nothing worth paying for and nearly stops buying. The Brier column is a tie and is
            reported as one: the memory arm leads in every split but by at most 0.0019, which is too
            small to call a quality win. The claim is <b style={{ color: RC.ink2 }}>the same forecast
            for a tenth of the cost</b>.
          </p>
        </section>

        <League league={L} frames={frames} />
      </div>

      <footer style={{ borderTop: `1px solid ${RC.line}`, padding: '22px 0 60px' }}>
        <div className="wrap" style={{ display: 'flex', gap: 22, flexWrap: 'wrap', fontSize: 12,
                                       color: RC.ink4 }}>
          <a href="https://github.com/neromtoobad/receipts" style={{ color: RC.ink3 }}>repo</a>
          <a href="https://sepolia.basescan.org/tx/0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc"
             style={{ color: RC.ink3 }}>x402 settlement on Base</a>
          <span>Virtuals ACP job 75249</span>
          <span style={{ marginLeft: 'auto' }}>MIT</span>
        </div>
      </footer>
    </>
  )
}

function Stat({ k, v, unit }: { k: string; v: string; unit?: string }) {
  return (
    <div>
      <div className="mono display" style={{ fontSize: 30, color: RC.ink, lineHeight: 1 }}>
        {v}{unit && <span style={{ fontSize: 13, color: RC.ink4 }}> {unit}</span>}
      </div>
      <div className="eyebrow" style={{ marginTop: 5 }}>{k}</div>
    </div>
  )
}
function Arm({ n, a, b, c, d, hi, bad }:
  { n: string; a: string; b: string; c: string; d: string; hi?: boolean; bad?: boolean }) {
  const col = hi ? RC.green : bad ? RC.red : RC.ink2
  return (
    <tr>
      <td style={{ padding: '9px 16px 9px 0', color: col, borderBottom: `1px solid ${RC.line}` }}>{n}</td>
      {[a, b, c, d].map((v, i) => (
        <td key={i} style={{ padding: '9px 16px 9px 0', color: i === 2 ? col : RC.ink2,
                             fontWeight: i === 2 ? 700 : 400,
                             borderBottom: `1px solid ${RC.line}` }}>{v}</td>
      ))}
    </tr>
  )
}
