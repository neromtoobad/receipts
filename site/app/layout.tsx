import { RC } from '../lib/theme'

export const metadata = {
  title: 'RECEIPTS — everybody\'s calls are on record',
  description:
    'Six AI pundits forecast real matches and real markets. Same model, same prompt, same budget. ' +
    'Every piece of evidence costs real money. The only edge is a private map of which informants ' +
    'are worth paying for, and it lives entirely in memory.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* Bricolage Grotesque for display — it has the slightly printed,
            slightly off character a project called RECEIPTS should have.
            Inter for UI. JetBrains Mono for every number, because every number
            here is a measurement and should read like one. */}
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
        <style>{`
          :root, :root[data-theme] {
            --rc-bg:${RC.bg}; --rc-surface:${RC.surface}; --rc-surface-2:${RC.surface2};
            --rc-surface-3:${RC.surface3};
            --rc-ink:${RC.ink}; --rc-ink-2:${RC.ink2}; --rc-ink-3:${RC.ink3}; --rc-ink-4:${RC.ink4};
            --rc-line:${RC.line}; --rc-line-2:${RC.line2};
            --rc-green:${RC.green}; --rc-red:${RC.red}; --rc-amber:${RC.amber};
            --rc-brand:${RC.brand};
            color-scheme: dark;
          }
          * { box-sizing:border-box }
          html,body { margin:0; padding:0; background:var(--rc-bg); color:var(--rc-ink);
            font-family:Inter,system-ui,sans-serif; -webkit-font-smoothing:antialiased;
            text-rendering:optimizeLegibility }
          /* A viewing centre is a dim room with a lit screen. Two lights, not one:
             a warm wash from the screen and a cold spill from the side, so surfaces
             have somewhere to fall away to. */
          body::before { content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
            background:
              radial-gradient(110% 62% at 50% -6%, rgba(232,163,61,.10), transparent 58%),
              radial-gradient(70% 50% at 96% 8%, rgba(89,183,232,.055), transparent 62%),
              radial-gradient(90% 60% at 4% 42%, rgba(53,196,127,.035), transparent 60%) }
          /* Fine grain stops large dark fields banding and reads as film rather than flat. */
          body::after { content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
            opacity:.5; mix-blend-mode:overlay;
            background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.28'/%3E%3C/svg%3E") }
          a { color:inherit; text-decoration:none }
          ::selection { background:var(--rc-brand); color:var(--rc-bg) }
          .mono { font-family:'JetBrains Mono',ui-monospace,monospace; font-variant-numeric:tabular-nums }
          .display { font-family:'Bricolage Grotesque',Inter,sans-serif; letter-spacing:-.02em }
          /* Editorial serif for section headlines. A page of grotesque at one size
             is what "AI-generic" looks like; the serif gives the page a voice and
             a second tier in the type scale. */
          .serif { font-family:'Instrument Serif',Georgia,serif; font-weight:400;
            letter-spacing:-.015em; line-height:1.05 }
          .h-sect { font-size:clamp(28px,3.4vw,44px); margin:8px 0 10px }
          .lede { font-size:15px; color:var(--rc-ink-3); line-height:1.65; max-width:640px }
          .btn { display:inline-flex; align-items:center; gap:8px; border-radius:9px;
            padding:11px 18px; font-size:14px; font-weight:600; cursor:pointer;
            font-family:inherit; border:1px solid transparent;
            transition:transform 200ms cubic-bezier(.16,1,.3,1), background 200ms, border-color 200ms }
          .btn-primary { background:var(--rc-brand); color:#17120A }
          .btn-primary:hover { transform:translateY(-1px); background:#F2B457 }
          .btn-ghost { border-color:var(--rc-line-2); color:var(--rc-ink-2) }
          .btn-ghost:hover { border-color:var(--rc-brand); color:var(--rc-ink) }
          .sect { padding:56px 0 8px }
          nav a:hover { color:var(--rc-ink) }
          .wrap { max-width:1180px; margin:0 auto; padding:0 24px; position:relative; z-index:1 }
          .eyebrow { font-size:11px; letter-spacing:.18em; text-transform:uppercase;
            color:var(--rc-ink-3); font-weight:600 }
          .card { background:linear-gradient(180deg, rgba(255,255,255,.028), rgba(255,255,255,.008));
            border:1px solid var(--rc-line); border-radius:12px;
            box-shadow:0 1px 0 rgba(255,255,255,.03) inset, 0 12px 32px -18px rgba(0,0,0,.9) }
          /* One motion language across the page: the same spring, everywhere. */
          .lift { transition:transform 220ms cubic-bezier(.16,1,.3,1),
                             box-shadow 220ms cubic-bezier(.16,1,.3,1),
                             border-color 220ms }
          .lift:hover { transform:translateY(-2px);
            box-shadow:0 18px 44px -22px rgba(0,0,0,.95), 0 0 0 1px rgba(232,163,61,.10) }
          button:focus-visible, a:focus-visible, input:focus-visible {
            outline:2px solid var(--rc-brand); outline-offset:2px; border-radius:8px }
          input[type=range]{ height:22px }
          @media (max-width:820px){ .wrap{padding:0 16px} }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}
