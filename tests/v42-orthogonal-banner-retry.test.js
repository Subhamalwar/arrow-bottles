const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('www/index.html','utf8');
test('every woven board uses a perfectly orthogonal projection', () => {
  const projection = html.slice(html.indexOf('    worldPoint(x,y) {'), html.indexOf('    // Canvas-local CSS px'));
  assert.match(projection, /return \[x \+ 1\.15, y \+ 1\.15\]/);
  assert.doesNotMatch(projection.slice(projection.indexOf("// Orthogonal Woven Maze")), /Math\.sin/);
});
test('map banner retries when consent changes and screens change', () => {
  assert.match(html, /AB\.bus\.on\('screen:shown', refreshBanner\)/);
  assert.match(html, /AB\.bus\.on\('consent:changed', refreshBanner\)/);
  assert.match(html, /ads\.showBanner\(\)/);
});
test('native banner is not requested prematurely during map construction', () => {
  const banner = html.slice(html.indexOf('    banner() {'), html.indexOf('    session: () =>'));
  assert.doesNotMatch(banner, /showBanner\(/);
});
