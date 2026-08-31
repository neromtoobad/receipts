/** Static export. GitHub Pages serves it from /receipts/, so every asset needs
 *  that prefix. No server anywhere in the demo path. */
const isProd = process.env.NODE_ENV === 'production'
export default {
  output: 'export',
  basePath: isProd ? '/receipts' : '',
  assetPrefix: isProd ? '/receipts/' : '',
  images: { unoptimized: true },
  trailingSlash: true,
}
