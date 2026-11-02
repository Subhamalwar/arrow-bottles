const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('www/index.html','utf8');
test('banner is eligible from Level 1 without Level 30 gate',()=>{
  assert.match(html,/bannerAllowed\(\) \{[\s\S]*?return !removeAds\(\) && !vip\(\) && consentGiven\(\);/);
  assert.doesNotMatch(html,/\(s\.maxCleared \|\| 0\) >= 30 && !removeAds/);
});
test('arrow path has only centered main stroke and no offset glossy highlight',()=>{
  const paint=html.slice(html.indexOf('    _paint(ctx, a, pts, t, o)'),html.indexOf('    _pattern(ctx, col, pts, sw)'));
  assert.match(paint,/line\(\[0, 0\], sw, main\)/);
  assert.doesNotMatch(paint,/line\(\[0, drop\]/);
  assert.doesNotMatch(paint,/line\(\[-sw \* 0\.1/);
});
test('rewarded video reports loading and failure states',()=>{
  assert.match(html,/Loading rewarded video/);
  assert.match(html,/Ad unavailable or not completed/);
});
