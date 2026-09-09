import React from 'react';
import {AbsoluteFill, Img, interpolate, useCurrentFrame, Easing} from 'remotion';
import {C, F} from './theme';

export const ease = Easing.bezier(0.16, 1, 0.3, 1);

/** Fade a scene in and out at its own edges, so cuts never snap. */
export const Scene: React.FC<{
  durationInFrames: number;
  children: React.ReactNode;
  fadeIn?: number;
  fadeOut?: number;
}> = ({durationInFrames, children, fadeIn = 14, fadeOut = 14}) => {
  const frame = useCurrentFrame();
  const opacity = Math.min(
    interpolate(frame, [0, fadeIn], [0, 1], {extrapolateRight: 'clamp'}),
    interpolate(frame, [durationInFrames - fadeOut, durationInFrames], [1, 0], {
      extrapolateLeft: 'clamp',
    })
  );
  // A very slow push, so a scene that holds under narration never goes dead.
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.02]);
  return (
    <AbsoluteFill style={{opacity}}>
      <AbsoluteFill style={{transform: `scale(${scale})`}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/** The page's two lights: a warm wash from the top, a cold spill from the side. */
export const Ground: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{backgroundColor: C.bg}}>
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(110% 62% at 50% -6%, rgba(232,163,61,.12), transparent 58%),' +
          'radial-gradient(70% 50% at 96% 8%, rgba(89,183,232,.06), transparent 62%),' +
          'radial-gradient(90% 60% at 4% 42%, rgba(53,196,127,.04), transparent 60%)',
      }}
    />
    {children}
  </AbsoluteFill>
);

export const Eyebrow: React.FC<{children: React.ReactNode; delay?: number}> = ({
  children,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 16], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        fontFamily: F.ui,
        fontSize: 20,
        letterSpacing: '0.22em',
        textTransform: 'uppercase',
        color: C.ink3,
        fontWeight: 600,
        opacity: o,
      }}
    >
      {children}
    </div>
  );
};

export const Headline: React.FC<{
  children: React.ReactNode;
  delay?: number;
  size?: number;
}> = ({children, delay = 0, size = 76}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const y = interpolate(frame, [delay, delay + 26], [18, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  return (
    <div
      style={{
        fontFamily: F.display,
        fontSize: size,
        lineHeight: 1.06,
        letterSpacing: '-0.015em',
        color: C.ink,
        opacity: o,
        transform: `translateY(${y}px)`,
      }}
    >
      {children}
    </div>
  );
};

export const Lede: React.FC<{children: React.ReactNode; delay?: number; width?: number}> = ({
  children,
  delay = 0,
  width = 820,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        fontFamily: F.ui,
        fontSize: 27,
        lineHeight: 1.55,
        color: C.ink3,
        maxWidth: width,
        opacity: o,
      }}
    >
      {children}
    </div>
  );
};

/** A screenshot of the real page, in a window, scrolling. */
export const BrowserPan: React.FC<{
  src: string;
  url: string;
  from: number;
  to: number;
  progress: number;
  width?: number;
  height?: number;
  scale?: number;
}> = ({src, url, from, to, progress, width = 1560, height = 800, scale = 1}) => {
  const y = interpolate(progress, [0, 1], [from, to]);
  return (
    <div
      style={{
        width,
        borderRadius: 14,
        overflow: 'hidden',
        border: `1px solid ${C.line2}`,
        boxShadow: '0 40px 120px -40px rgba(0,0,0,.95)',
        background: C.surface,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          height: 46,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '0 16px',
          background: C.surface2,
          borderBottom: `1px solid ${C.line}`,
        }}
      >
        {[C.red, C.amber, C.green].map((c) => (
          <div key={c} style={{width: 11, height: 11, borderRadius: 99, background: c, opacity: 0.75}} />
        ))}
        <div
          style={{
            marginLeft: 14,
            fontFamily: F.mono,
            fontSize: 15,
            color: C.ink4,
            background: C.surface3,
            padding: '5px 14px',
            borderRadius: 7,
          }}
        >
          {url}
        </div>
      </div>
      <div style={{height, overflow: 'hidden', position: 'relative'}}>
        <Img src={src} style={{width: '100%', display: 'block', transform: `translateY(${y}px)`}} />
      </div>
    </div>
  );
};

/** A lower third. Text I control, over a page I do not. */
export const Caption: React.FC<{
  children: React.ReactNode;
  delay?: number;
  accent?: string;
}> = ({children, delay = 0, accent = C.amber}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 16], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const w = interpolate(frame, [delay, delay + 26], [0, 6], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  return (
    <div style={{display: 'flex', gap: 20, alignItems: 'stretch', opacity: o}}>
      <div style={{width: w, background: accent, borderRadius: 4}} />
      <div
        style={{
          fontFamily: F.ui,
          fontSize: 30,
          lineHeight: 1.4,
          color: C.ink2,
          maxWidth: 1000,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Mono: React.FC<{children: React.ReactNode; color?: string; size?: number}> = ({
  children,
  color = C.ink,
  size = 28,
}) => (
  <span style={{fontFamily: F.mono, fontSize: size, color, fontVariantNumeric: 'tabular-nums'}}>
    {children}
  </span>
);

type Rect = {x: number; y: number; w: number; h: number};

/** A framed crop of a real screenshot, in CSS pixels of the captured page. */
export const Crop: React.FC<{
  src: string;
  cssWidth: number;
  rect: Rect;
  rectEnd?: Rect;
  progress?: number;
  outW: number;
  outH: number;
  radius?: number;
  border?: boolean;
}> = ({src, cssWidth, rect, rectEnd, progress = 0, outW, outH, radius = 14, border = true}) => {
  const r: Rect = rectEnd
    ? {
        x: rect.x + (rectEnd.x - rect.x) * progress,
        y: rect.y + (rectEnd.y - rect.y) * progress,
        w: rect.w + (rectEnd.w - rect.w) * progress,
        h: rect.h + (rectEnd.h - rect.h) * progress,
      }
    : rect;
  const scale = outW / r.w;
  return (
    <div
      style={{
        width: outW,
        height: outH,
        overflow: 'hidden',
        borderRadius: radius,
        border: border ? `1px solid ${C.line2}` : 'none',
        position: 'relative',
        background: C.bg,
        boxShadow: '0 40px 120px -50px rgba(0,0,0,.95)',
      }}
    >
      <Img
        src={src}
        style={{
          position: 'absolute',
          width: cssWidth * scale,
          left: -r.x * scale,
          top: -r.y * scale,
        }}
      />
    </div>
  );
};
