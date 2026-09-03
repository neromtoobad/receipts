import { RC, alpha } from '../../lib/theme'
import { LEAGUE } from '../../lib/data'
import { Nav } from '../../components/Nav'
import { Section } from '../../components/Section'
import { DeletionChart } from '../../components/DeletionChart'
import { Foot } from '../../components/Foot'

export const metadata = {
  title: 'The deletion test — RECEIPTS',
  description: 'Delete the memory and the same agent spends ten times as much for the same forecast. 1,000 held-out events.',
}

export default function Proof() {
  return (
    <>
      <Nav />
      <div className="wrap" style={{ paddingBottom: 80 }}>
        <Section eyebrow="the deletion test" title="Same agent, same market."
          accent="One tenth the cost."
          lede={<>An agent that pays for its own inputs has two jobs: decide what to believe, and
            decide what to buy. Take the memory away and the second becomes impossible — no basis to
            rank a source, no basis to stop, no way to learn that one has never beaten a coin flip.
            So it buys everything, every time, forever. That is the core function failing, not an
            optimisation being lost: an agent that cannot budget cannot be left running.</>}>
          <div className="card" style={{ padding: 22, borderColor: alpha(RC.brand, .26) }}>
            <DeletionChart />
          </div>
        </Section>

        <Section eyebrow="how to read it" title="The spend result is decisive."
          accent="The quality result is a tie.">
          <div style={{ display: 'grid', gap: 12,
                        gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))' }}>
            <Note title="Why spend is the function, not an optimisation"
              body="The amnesiac buys 4.50 informants for every call and never stops, because nothing in it can know the eighth opinion adds nothing to the first. At these prices it burns a month of funding in three days for the same forecasts. Autonomy is what memory is holding up here, and autonomy is what stops working without it." />
            <Note title="Why the number is trustworthy"
              body="An arm learns from what each SOURCE said against the outcome, never from its own forecast. Selection is settled entirely by memory, so the spend figures hold whatever forecaster runs on top — they are not an artefact of the model we happened to use." />
            <Note title="Why we do not claim a quality win"
              body="The memory arm leads on Brier in all three splits and the direction is consistent, but the largest margin is 0.0019 and accuracy favours the amnesiac by 0.3 points. That is noise in both directions. Inflating it would collapse under one question." />
            <Note title="Why the third arm exists"
              body="A flat log remembers, but cannot tell domains apart. One global number gets dragged toward zero by crypto, so it stops buying in football too and lands on the worst Brier of the three. Over-buying and under-buying are the same bug." />
            <Note title="Tuning discipline"
              body="Informants are calibrated on season 2023-24 and the earlier 60% of the crypto series. The selection and exploration rules were tuned on that same fit split, then run once on the held-out split. No rule was ever tuned against the numbers reported here." />
          </div>
        </Section>

        <Section eyebrow="onchain" title="Everything here is" accent="a hash or a measurement.">
          <div style={{ display: 'grid', gap: 12,
                        gridTemplateColumns: 'repeat(auto-fill,minmax(258px,1fr))' }}>
            <Proofcard k="Base · x402 settlement" v="0xb0cc50db…64eebc"
              sub="0.012 USDC, block 46195402. Gas paid by the facilitator, not the agent — EIP-3009 means the agent needs USDC and no ETH."
              href="https://sepolia.basescan.org/tx/0xb0cc50dbf1530884b0789f15b0498632bb50d6a74b74336b58659fefd864eebc" />
            <Proofcard k="Virtuals · ACP job 75249" v="completed"
              sub="pundit_5 hired pundit_1 on Base mainnet, funded escrow, received a forecast from the real runtime, released it."
              href="https://github.com/neromtoobad/receipts/blob/main/proof/VIRTUALS.md" />
            <Proofcard k="Informant reliability" v="6,462 matches"
              sub="6 leagues, 3 seasons. Regional desks score +0.10 to +0.12 inside their beat and +0.01 to +0.04 outside it."
              href="https://github.com/neromtoobad/receipts/blob/main/proof/DOMAINS.md" />
            <Proofcard k="Crypto has no signal" v="zero skill"
              sub="Every informant scores at or below zero on crypto direction. The correct spend there is nothing, and only domain-scoped memory gets there."
              href="https://github.com/neromtoobad/receipts/blob/main/proof/DOMAINS.md" />
            <Proofcard k="Memory, measured" v="42ms cold boot"
              sub="Boot to decision. 2,983 bytes per traced event, so 1,757 forecasts fit per pundit database."
              href="https://github.com/neromtoobad/receipts/blob/main/proof/PHASE0_FINDINGS.md" />
            <Proofcard k="The bench" v="3,000 calls"
              sub="qwen2.5:7b-instruct running locally, zero failed requests. Reproducible with ollama pull and one command, no API key."
              href="https://github.com/neromtoobad/receipts/blob/main/proof/BENCH.md" />
          </div>
        </Section>
      </div>
      <Foot generated={LEAGUE.generated} />
    </>
  )
}

function Note({ title, body }: { title: string; body: string }) {
  return (
    <div className="card" style={{ padding: '15px 16px' }}>
      <div style={{ fontSize: 14, color: RC.ink, fontWeight: 600, marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 12.5, color: RC.ink3, lineHeight: 1.65 }}>{body}</div>
    </div>
  )
}
function Proofcard({ k, v, sub, href }: { k: string; v: string; sub: string; href?: string }) {
  const inner = (
    <div className="card lift" style={{ padding: '15px 16px', height: '100%' }}>
      <div className="eyebrow">{k}</div>
      <div className="mono" style={{ fontSize: 15, color: RC.brand, margin: '7px 0 6px',
                                     wordBreak: 'break-all' }}>{v}</div>
      <div style={{ fontSize: 12, color: RC.ink3, lineHeight: 1.6 }}>{sub}</div>
    </div>
  )
  return href ? <a href={href}>{inner}</a> : inner
}
