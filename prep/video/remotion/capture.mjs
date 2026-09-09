import puppeteer from 'puppeteer-core';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = 'https://neromtoobad.github.io/receipts';

const shots = [
  {name: 'home.png', path: '/', height: 1200},
  {name: 'agents.png', path: '/agents/', height: 1200},
  {name: 'proof.png', path: '/proof/', height: 1200},
];

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--hide-scrollbars', '--disable-gpu'],
});

for (const s of shots) {
  const page = await browser.newPage();
  await page.setViewport({width: 1500, height: s.height, deviceScaleFactor: 2});
  await page.goto(BASE + s.path, {waitUntil: 'networkidle2', timeout: 60000});
  // Scroll the whole page once so anything gated on intersection has fired.
  await page.evaluate(async () => {
    const step = window.innerHeight * 0.8;
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 120));
    }
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 900));
  });
  await page.screenshot({path: `public/${s.name}`, fullPage: true});
  const dims = await page.evaluate(() => [document.body.scrollWidth, document.body.scrollHeight]);
  console.log(s.name, 'css size', dims.join('x'));
  await page.close();
}

await browser.close();
