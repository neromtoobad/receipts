import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, F} from './theme';
import {ease} from './ui';

const KEYWORDS = /\b(def|if|else|elif|return|for|in|not|and|or|None|True|False|class|import|from|continue|raise)\b/g;
const BUILTINS = /\b(self|dict|list|float|str|int)\b/g;

/** Enough highlighting to read as code without pulling in a syntax library. */
const tokenize = (line: string): React.ReactNode => {
  const hash = line.indexOf('#');
  const code = hash >= 0 ? line.slice(0, hash) : line;
  const comment = hash >= 0 ? line.slice(hash) : '';

  const parts: React.ReactNode[] = [];
  const re = /("[^"]*"|'[^']*')/g;
  let last = 0;
  let m: RegExpExecArray | null;
  const pushPlain = (text: string, key: string) => {
    const nodes: React.ReactNode[] = [];
    let idx = 0;
    text.split(/(\b(?:def|if|else|elif|return|for|in|not|and|or|None|True|False|class|import|from|continue|raise|self)\b)/).forEach((chunk, i) => {
      if (!chunk) return;
      const isKw = KEYWORDS.test(chunk);
      KEYWORDS.lastIndex = 0;
      const isSelf = BUILTINS.test(chunk);
      BUILTINS.lastIndex = 0;
      nodes.push(
        <span
          key={`${key}-${i}-${idx++}`}
          style={{color: isKw ? C.amber : isSelf ? C.blue : C.ink2}}
        >
          {chunk}
        </span>
      );
    });
    return nodes;
  };

  while ((m = re.exec(code)) !== null) {
    if (m.index > last) parts.push(...(pushPlain(code.slice(last, m.index), `p${last}`) as any));
    parts.push(
      <span key={`s${m.index}`} style={{color: C.green}}>
        {m[0]}
      </span>
    );
    last = m.index + m[0].length;
  }
  if (last < code.length) parts.push(...(pushPlain(code.slice(last), `p${last}`) as any));
  if (comment) {
    parts.push(
      <span key="c" style={{color: C.ink4, fontStyle: 'italic'}}>
        {comment}
      </span>
    );
  }
  return parts;
};

export const CodeCard: React.FC<{
  file: string;
  lines: string[];
  /** zero-based indices that get the amber band */
  highlight?: number[];
  /** frame at which the highlight band sweeps in */
  highlightAt?: number;
  startAt?: number;
  perLine?: number;
  fontSize?: number;
  width?: number;
}> = ({file, lines, highlight = [], highlightAt = 999999, startAt = 0, perLine = 2.2, fontSize = 26, width = 1180}) => {
  const frame = useCurrentFrame();
  const bandW = interpolate(frame, [highlightAt, highlightAt + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        width,
        background: C.surface,
        border: `1px solid ${C.line2}`,
        borderRadius: 14,
        overflow: 'hidden',
        boxShadow: '0 40px 120px -50px rgba(0,0,0,.95)',
      }}
    >
      <div
        style={{
          padding: '13px 22px',
          background: C.surface2,
          borderBottom: `1px solid ${C.line}`,
          fontFamily: F.mono,
          fontSize: 19,
          color: C.ink3,
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <span>{file}</span>
        <span style={{color: C.ink4}}>python</span>
      </div>
      <div style={{padding: '20px 0 24px'}}>
        {lines.map((line, i) => {
          const at = startAt + i * perLine;
          const o = interpolate(frame, [at, at + 10], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const isHot = highlight.includes(i);
          return (
            <div
              key={i}
              style={{
                position: 'relative',
                display: 'flex',
                gap: 22,
                padding: '2px 26px',
                opacity: o,
              }}
            >
              {isHot ? (
                <div
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: `${bandW * 100}%`,
                    background: 'rgba(232,163,61,.13)',
                    borderLeft: `3px solid ${C.amber}`,
                  }}
                />
              ) : null}
              <span
                style={{
                  fontFamily: F.mono,
                  fontSize: fontSize - 4,
                  color: C.ink4,
                  width: 34,
                  textAlign: 'right',
                  zIndex: 1,
                }}
              >
                {i + 1}
              </span>
              <span
                style={{
                  fontFamily: F.mono,
                  fontSize,
                  lineHeight: 1.62,
                  whiteSpace: 'pre',
                  zIndex: 1,
                }}
              >
                {tokenize(line)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
