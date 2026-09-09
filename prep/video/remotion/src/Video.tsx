import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {C, F} from './theme';
import {BrowserPan, Caption, Crop, Eyebrow, Ground, Headline, Lede, Mono, Scene, ease} from './ui';
import {CodeCard} from './CodeCard';

const S = {
  title: 209,
  site: 466,
  loop: 487,
  tiers: 388,
  code: 511,
  map: 420,
  bench: 420,
  proof: 377,
};
const AT = {
  title: 0,
  site: 209,
  loop: 675,
  tiers: 1162,
  code: 1550,
  map: 2061,
  bench: 2481,
  proof: 2901,
};
/** The read is slow by default; 1.2 lands it at a documentary pace. */
const VO_RATE = 1.12;

const Vo: React.FC<{n: number; at?: number}> = ({n, at = 8}) => (
  <Sequence from={at}>
    <Audio src={staticFile(`vo/${n}.wav`)} playbackRate={VO_RATE} volume={0.92} />
  </Sequence>
);

export const TOTAL = AT.proof + S.proof;

const prog = (frame: number, a: number, b: number) =>
  interpolate(frame, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/* ------------------------------------------------------------------ 1. title */

const Title: React.FC = () => {
  const frame = useCurrentFrame();
  const rule = interpolate(frame, [18, 50], [0, 560], {extrapolateRight: 'clamp', easing: ease});
  return (
    <Scene durationInFrames={S.title}>
      <Vo n={1} />
      <Ground>
        <AbsoluteFill style={{justifyContent: 'center', paddingLeft: 150}}>
          <Eyebrow delay={4}>Sibyl Labs Hackathon · live league</Eyebrow>
          <div style={{height: 26}} />
          <Headline delay={10} size={104}>
            Six AI pundits keep receipts.
          </Headline>
          <div style={{height: 22}} />
          <div style={{height: 3, width: rule, background: C.amber, borderRadius: 3}} />
          <div style={{height: 30}} />
          <Lede delay={34} width={1000}>
            One model, one prompt, one budget. Every piece of evidence costs real money. The
            process dies after every forecast — and the only thing that survives is what it wrote
            to Sibyl Memory.
          </Lede>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------------- 2. site */

const Site: React.FC = () => {
  const frame = useCurrentFrame();
  const p = prog(frame, 20, S.site - 30);
  return (
    <Scene durationInFrames={S.site}>
      <Vo n={2} />
      <Ground>
        <AbsoluteFill style={{flexDirection: 'row', alignItems: 'center'}}>
          <div style={{width: 560, paddingLeft: 96}}>
            <Eyebrow delay={6}>the board, live</Eyebrow>
            <div style={{height: 20}} />
            <Headline delay={12} size={62}>
              Everything they did is on the record.
            </Headline>
            <div style={{height: 34}} />
            <Caption delay={70}>
              <Mono color={C.amber} size={34}>1,166</Mono> calls ·{' '}
              <Mono color={C.amber} size={34}>805</Mono> resolved
            </Caption>
            <div style={{height: 18}} />
            <Caption delay={100}>
              <Mono color={C.amber} size={34}>2,010</Mono> informants bought ·{' '}
              <Mono color={C.amber} size={34}>18.50</Mono> USDC spent
            </Caption>
            <div style={{height: 18}} />
            <Caption delay={150}>About 1.6 cents a forecast, all of it real.</Caption>
          </div>
          <div style={{flex: 1, display: 'flex', justifyContent: 'center'}}>
            <BrowserPan
              src={staticFile('home.png')}
              url="neromtoobad.github.io/receipts"
              from={0}
              to={-740}
              progress={p}
              width={1180}
              height={880}
            />
          </div>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------- 3. the loop */

const Node: React.FC<{
  label: string;
  sub?: string;
  delay: number;
  accent?: string;
  dead?: boolean;
}> = ({label, sub, delay, accent = C.line2, dead = false}) => {
  const frame = useCurrentFrame();
  const o = prog(frame, delay, delay + 16);
  const y = interpolate(frame, [delay, delay + 22], [16, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  return (
    <div
      style={{
        opacity: o,
        transform: `translateY(${y}px)`,
        background: C.surface,
        border: `1px solid ${accent}`,
        borderRadius: 12,
        padding: '22px 26px',
        minWidth: 250,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontFamily: F.ui,
          fontSize: 28,
          color: dead ? C.red : C.ink,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      {sub ? (
        <div style={{fontFamily: F.mono, fontSize: 18, color: C.ink4, marginTop: 8}}>{sub}</div>
      ) : null}
    </div>
  );
};

const Chevron: React.FC<{delay: number}> = ({delay}) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        opacity: prog(frame, delay, delay + 12) * 0.55,
        color: C.ink4,
        fontFamily: F.ui,
        fontSize: 30,
      }}
    >
      →
    </div>
  );
};

const Loop: React.FC = () => {
  const frame = useCurrentFrame();
  const dash = interpolate(frame, [150, 220], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const labelO = prog(frame, 200, 226);
  return (
    <Scene durationInFrames={S.loop}>
      <Vo n={3} />
      <Ground>
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
          <Eyebrow delay={4}>how it works</Eyebrow>
          <div style={{height: 18}} />
          <Headline delay={8} size={64}>
            Buy, call, die, remember.
          </Headline>
          <div style={{height: 66}} />
          <div style={{display: 'flex', gap: 14, alignItems: 'center'}}>
            <Node label="boots" sub="empty context" delay={30} />
            <Chevron delay={42} />
            <Node label="reads the map" sub="42ms off disk" delay={48} accent={C.amber} />
            <Chevron delay={60} />
            <Node label="buys" sub="x402 USDC on Base" delay={66} />
            <Chevron delay={78} />
            <Node label="forecasts" sub="one call" delay={84} />
            <Chevron delay={96} />
            <Node label="exit(0)" sub="process gone" delay={102} accent={C.red} dead />
          </div>
          <svg width={1560} height={200} style={{marginTop: -6}}>
            <path
              d="M 1400 24 C 1400 168, 430 168, 430 24"
              fill="none"
              stroke={C.amber}
              strokeWidth={3}
              strokeDasharray={2400}
              strokeDashoffset={dash * 2400}
            />
            <circle cx={430} cy={26} r={7} fill={C.amber} opacity={labelO} />
          </svg>
          <div
            style={{
              marginTop: -96,
              opacity: labelO,
              fontFamily: F.ui,
              fontSize: 30,
              color: C.ink2,
              background: C.bg,
              padding: '6px 20px',
            }}
          >
            <span style={{color: C.amber, fontWeight: 600}}>Sibyl Memory</span> is the only thing
            that crosses the boundary.
          </div>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------------ 4. tiers */

const TIERS: [string, string, string, string][] = [
  ['HOT', 'set_state', "this turn's working set; sources paid for but not yet proven", C.ink3],
  ['WARM', 'set_entity', 'source_reliability per (informant, domain) — the map', C.green],
  ['COLD', 'write_event', 'every purchase and every forecast, with its reasoning', C.ink3],
  ['REFERENCE', 'set_reference', 'the informant catalogue and its prices', C.ink3],
  ['ARCHIVE', 'archive_entity', 'informants that went quiet. recoverable, not deleted', C.ink3],
];

const Tiers: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Scene durationInFrames={S.tiers}>
      <Vo n={4} />
      <Ground>
        <AbsoluteFill style={{justifyContent: 'center', paddingLeft: 130, paddingRight: 130}}>
          <Eyebrow delay={4}>where the memory lives</Eyebrow>
          <div style={{height: 18}} />
          <Headline delay={8} size={64}>
            Five tiers, one file.
          </Headline>
          <div style={{height: 14}} />
          <Lede delay={22} width={1180}>
            <Mono color={C.ink2} size={26}>agent/memory.py</Mono> is the only file in the project
            that imports the Sibyl SDK. A judge should need one file and fifteen seconds.
          </Lede>
          <div style={{height: 40}} />
          {TIERS.map(([tier, call, what, colour], i) => {
            const delay = 46 + i * 22;
            const o = prog(frame, delay, delay + 18);
            const x = interpolate(frame, [delay, delay + 24], [-26, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: ease,
            });
            const isWarm = tier === 'WARM';
            const glow = isWarm ? prog(frame, 190, 220) : 0;
            return (
              <div
                key={tier}
                style={{
                  opacity: o,
                  transform: `translateX(${x}px)`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 32,
                  padding: '17px 26px',
                  marginBottom: 10,
                  borderRadius: 10,
                  background: isWarm ? `rgba(53,196,127,${0.05 + glow * 0.08})` : C.surface,
                  border: `1px solid ${isWarm ? `rgba(53,196,127,${0.25 + glow * 0.5})` : C.line}`,
                }}
              >
                <div
                  style={{
                    fontFamily: F.ui,
                    fontSize: 22,
                    letterSpacing: '0.16em',
                    color: isWarm ? C.green : C.ink4,
                    width: 190,
                    fontWeight: 700,
                  }}
                >
                  {tier}
                </div>
                <div style={{fontFamily: F.mono, fontSize: 27, color: C.ink, width: 290}}>
                  {call}
                </div>
                <div style={{fontFamily: F.ui, fontSize: 25, color: C.ink3, flex: 1}}>{what}</div>
              </div>
            );
          })}
          <div style={{height: 26}} />
          <Caption delay={230} accent={C.green}>
            A source is not trusted the moment it is bought. Three resolved observations promote it
            to WARM; three silent days archive it.
          </Caption>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------------- 5. code */

const MEMORY_LINES = [
  'if body["n"] >= PROMOTE_N:                 # three resolved observations',
  '    body["status"] = "established"',
  '    self.c.set_entity(CAT_SOURCE, key, body)',
  '    self.log_event(acted=[f"promoted {key} to an entity"])',
  'else:',
  '    self.c.set_state(self._provisional_key(source, domain), body)',
];

const SOURCES_LINES = [
  'if arm == "amnesiac":',
  '    # No memory, so no ranking and no stopping rule. Spend until it cannot.',
  '    for src in sorted(candidates):',
  '        chosen.append(Choice(src, price, None, None, "no basis to choose"))',
  '',
  'if arm == "sibyl":',
  '    known = {s: mem.get_reliability(s, domain) for s in candidates}',
  '    if skill < MIN_SKILL:',
  '        continue                 # measured noise. not worth any price.',
];

const CodeBeat: React.FC<{
  file: string;
  lines: string[];
  highlight: number[];
  highlightAt: number;
  startAt: number;
  caption: React.ReactNode;
  captionAt: number;
  accent?: string;
  fadeIn: number;
  fadeOut?: number;
}> = ({file, lines, highlight, highlightAt, startAt, caption, captionAt, accent, fadeIn, fadeOut}) => {
  const frame = useCurrentFrame();
  const inO = prog(frame, fadeIn, fadeIn + 18);
  const outO = fadeOut === undefined ? 1 : 1 - prog(frame, fadeOut, fadeOut + 18);
  return (
    <AbsoluteFill
      style={{justifyContent: 'center', alignItems: 'center', opacity: inO * outO}}
    >
      <CodeCard
        file={file}
        lines={lines}
        highlight={highlight}
        highlightAt={highlightAt}
        startAt={startAt}
        width={1400}
        fontSize={25}
      />
      <div style={{height: 40}} />
      <div style={{width: 1400}}>
        <Caption delay={captionAt} accent={accent}>
          {caption}
        </Caption>
      </div>
    </AbsoluteFill>
  );
};

const Code: React.FC = () => {
  const frame = useCurrentFrame();
  const headO = 1 - prog(frame, 400, 440);
  return (
    <Scene durationInFrames={S.code}>
      <Vo n={5} />
      <Ground>
        <AbsoluteFill style={{alignItems: 'center', paddingTop: 84, opacity: headO}}>
          <Eyebrow delay={2}>the two files that matter</Eyebrow>
          <div style={{height: 14}} />
          <Headline delay={6} size={52}>
            Written once. Read by a process that never met the writer.
          </Headline>
        </AbsoluteFill>
        <AbsoluteFill style={{paddingTop: 90}}>
          <CodeBeat
            file="agent/memory.py"
            lines={MEMORY_LINES}
            highlight={[2]}
            highlightAt={104}
            startAt={26}
            captionAt={124}
            fadeIn={14}
            fadeOut={236}
            accent={C.green}
            caption={
              <>
                One <Mono color={C.green} size={28}>set_entity</Mono> call is the whole edge: a
                source that has proved itself three times becomes part of the map.
              </>
            }
          />
          <CodeBeat
            file="agent/sources.py"
            lines={SOURCES_LINES}
            highlight={[6]}
            highlightAt={352}
            startAt={268}
            captionAt={372}
            fadeIn={252}
            accent={C.red}
            caption={
              <>
                The same code with the memory deleted has{' '}
                <span style={{color: C.red}}>no basis to choose</span> — so it buys everything, and
                never stops.
              </>
            }
          />
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* --------------------------------------------------------------- 6. the map */

const TrustMap: React.FC = () => {
  const frame = useCurrentFrame();
  const p = prog(frame, 30, S.map - 40);
  return (
    <Scene durationInFrames={S.map}>
      <Vo n={6} />
      <Ground>
        <AbsoluteFill style={{flexDirection: 'row', alignItems: 'center'}}>
          <div style={{width: 620, paddingLeft: 96}}>
            <Eyebrow delay={4}>what memory holds</Eyebrow>
            <div style={{height: 18}} />
            <Headline delay={8} size={58}>
              Trust, per source and per domain.
            </Headline>
            <div style={{height: 30}} />
            <Caption delay={40} accent={C.green}>
              Green is trust earned. Red is a source measured worse than the base rate.
            </Caption>
            <div style={{height: 18}} />
            <Caption delay={90} accent={C.red}>
              Nobody declared any of it. It is the residue of 2,010 purchases and 805 resolved
              markets.
            </Caption>
            <div style={{height: 18}} />
            <Caption delay={150}>
              One global score per source would carry football skill into crypto and pay for noise
              forever.
            </Caption>
          </div>
          <div style={{flex: 1, display: 'flex', justifyContent: 'center'}}>
            <Crop
              src={staticFile('agents.png')}
              cssWidth={1500}
              rect={{x: 160, y: 1215, w: 810, h: 476}}
              rectEnd={{x: 168, y: 1240, w: 750, h: 441}}
              progress={p}
              outW={1080}
              outH={634}
            />
          </div>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------ 7. the bench */

const Bar: React.FC<{
  label: string;
  sub: string;
  value: number;
  max: number;
  colour: string;
  delay: number;
  bought: string;
}> = ({label, sub, value, max, colour, delay, bought}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 44], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const shown = (value * p).toFixed(2);
  return (
    <div style={{marginBottom: 26, opacity: prog(frame, delay - 8, delay + 8)}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
        <div style={{fontFamily: F.ui, fontSize: 27, color: C.ink2}}>
          {label} <span style={{color: C.ink4, fontSize: 23}}>{sub}</span>
        </div>
        <div style={{fontFamily: F.mono, fontSize: 23, color: C.ink4}}>{bought} bought / call</div>
      </div>
      <div style={{height: 12}} />
      <div
        style={{
          height: 62,
          width: `${(value / max) * p * 100}%`,
          background: colour,
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          paddingLeft: 20,
          minWidth: 150,
        }}
      >
        <span style={{fontFamily: F.mono, fontSize: 32, color: '#0E0D0B', fontWeight: 700}}>
          ${shown}
        </span>
      </div>
    </div>
  );
};

const Bench: React.FC = () => {
  const frame = useCurrentFrame();
  const multO = prog(frame, 326, 356);
  return (
    <Scene durationInFrames={S.bench}>
      <Vo n={7} />
      <Ground>
        <AbsoluteFill style={{justifyContent: 'center', paddingLeft: 130, paddingRight: 130}}>
          <Eyebrow delay={4}>the deletion test</Eyebrow>
          <div style={{height: 18}} />
          <Headline delay={8} size={62}>
            Delete the memory and it spends ten times as much.
          </Headline>
          <div style={{height: 16}} />
          <Lede delay={24} width={1200}>
            1,000 held-out events. Same model, same prompt, same budget, same informants at the
            same prices. The only difference is what each arm is allowed to remember.
          </Lede>
          <div style={{height: 44}} />
          <Bar label="domain-scoped memory" sub="knows who is worth paying for, and where" value={5.28} max={53} colour={C.green} delay={96} bought="0.55" />
          <Bar label="memory, no domain scoping" sub="one global number cannot hold two lessons" value={0.89} max={53} colour={C.ink4} delay={168} bought="0.08" />
          <Bar label="no memory" sub="no basis to choose, no basis to stop" value={53.0} max={53} colour={C.red} delay={232} bought="4.50" />
          <div style={{height: 14}} />
          <div style={{display: 'flex', alignItems: 'baseline', gap: 26, opacity: multO}}>
            <span style={{fontFamily: F.display, fontSize: 76, color: C.amber}}>10.0×</span>
            <span style={{fontFamily: F.ui, fontSize: 28, color: C.ink3, maxWidth: 900}}>
              the spend, for a forecast that scores the same — Brier{' '}
              <Mono color={C.ink} size={26}>0.5658</Mono> vs{' '}
              <Mono color={C.ink} size={26}>0.5664</Mono>. A tie, and reported as one.
            </span>
          </div>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ------------------------------------------------------------ 8. the proof */

const PROOF: [string, string, string][] = [
  ['BASE · x402 settlement', '0xb0cc50db…64eebc', '0.012 USDC, block 46195402. EIP-3009, so the agent never holds ETH.'],
  ['VIRTUALS · ACP job 75820', 'completed', 'One pundit hired another on Base mainnet, and the deliverable named its sources.'],
  ['THE BENCH', '3,000 calls', 'qwen2.5:7b-instruct, locally. Zero failures, no API key, one command.'],
];

const Proof: React.FC = () => {
  const frame = useCurrentFrame();
  const outro = prog(frame, 300, 330);
  return (
    <Scene durationInFrames={S.proof}>
      <Vo n={8} />
      <Ground>
        <AbsoluteFill style={{justifyContent: 'center', paddingLeft: 130, paddingRight: 130}}>
          <div style={{opacity: 1 - outro, position: 'absolute', left: 130, right: 130}}>
            <Eyebrow delay={2}>onchain</Eyebrow>
            <div style={{height: 18}} />
            <Headline delay={6} size={62}>
              Everything here is a hash or a measurement.
            </Headline>
            <div style={{height: 42}} />
            <div style={{display: 'flex', gap: 24}}>
              {PROOF.map(([head, value, body], i) => {
                const delay = 34 + i * 20;
                const o = prog(frame, delay, delay + 18);
                const y = interpolate(frame, [delay, delay + 26], [18, 0], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                  easing: ease,
                });
                return (
                  <div
                    key={head}
                    style={{
                      flex: 1,
                      opacity: o,
                      transform: `translateY(${y}px)`,
                      background: C.surface,
                      border: `1px solid ${C.line}`,
                      borderRadius: 12,
                      padding: '26px 28px',
                    }}
                  >
                    <div
                      style={{
                        fontFamily: F.ui,
                        fontSize: 18,
                        letterSpacing: '0.14em',
                        textTransform: 'uppercase',
                        color: C.ink4,
                      }}
                    >
                      {head}
                    </div>
                    <div style={{height: 14}} />
                    <div style={{fontFamily: F.mono, fontSize: 30, color: C.amber}}>{value}</div>
                    <div style={{height: 14}} />
                    <div style={{fontFamily: F.ui, fontSize: 22, color: C.ink3, lineHeight: 1.5}}>
                      {body}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <AbsoluteFill
            style={{
              opacity: outro,
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            <div style={{fontFamily: F.display, fontSize: 108, color: C.ink}}>RECEIPTS</div>
            <div style={{height: 18}} />
            <div style={{fontFamily: F.ui, fontSize: 30, color: C.ink3, maxWidth: 1100}}>
              Six agents, one model, and a map of who to trust that only exists because something
              wrote it down before it died.
            </div>
            <div style={{height: 34}} />
            <div style={{fontFamily: F.mono, fontSize: 30, color: C.amber}}>
              neromtoobad.github.io/receipts
            </div>
            <div style={{height: 16}} />
            <div style={{fontFamily: F.ui, fontSize: 24, color: C.ink4}}>
              Built on Sibyl Memory · evidence paid for over x402 on Base
            </div>
          </AbsoluteFill>
        </AbsoluteFill>
      </Ground>
    </Scene>
  );
};

/* ---------------------------------------------------------------- assembly */

export const Receipts: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: C.bg}}>
    <Sequence from={AT.title} durationInFrames={S.title}><Title /></Sequence>
    <Sequence from={AT.site} durationInFrames={S.site}><Site /></Sequence>
    <Sequence from={AT.loop} durationInFrames={S.loop}><Loop /></Sequence>
    <Sequence from={AT.tiers} durationInFrames={S.tiers}><Tiers /></Sequence>
    <Sequence from={AT.code} durationInFrames={S.code}><Code /></Sequence>
    <Sequence from={AT.map} durationInFrames={S.map}><TrustMap /></Sequence>
    <Sequence from={AT.bench} durationInFrames={S.bench}><Bench /></Sequence>
    <Sequence from={AT.proof} durationInFrames={S.proof}><Proof /></Sequence>
  </AbsoluteFill>
);
