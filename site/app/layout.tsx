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
          href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap"
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
          /* A viewing centre is a dim room with a lit screen. */
          body::before { content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
            background:radial-gradient(120% 80% at 50% -10%, rgba(232,163,61,.055), transparent 60%) }
          a { color:inherit; text-decoration:none }
          ::selection { background:var(--rc-brand); color:var(--rc-bg) }
          .mono { font-family:'JetBrains Mono',ui-monospace,monospace; font-variant-numeric:tabular-nums }
          .display { font-family:'Bricolage Grotesque',Inter,sans-serif; letter-spacing:-.02em }
          .wrap { max-width:1180px; margin:0 auto; padding:0 24px; position:relative; z-index:1 }
          .eyebrow { font-size:11px; letter-spacing:.18em; text-transform:uppercase;
            color:var(--rc-ink-3); font-weight:600 }
          .card { background:var(--rc-surface); border:1px solid var(--rc-line); border-radius:10px }
          @media (max-width:820px){ .wrap{padding:0 16px} }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}
