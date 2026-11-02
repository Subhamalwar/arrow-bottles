const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('www/index.html', 'utf8');
const bridge = fs.readFileSync('src/native-ads-bridge.js', 'utf8');
test('abandon attempt does not refund a heart', () => {
 const part = html.slice(html.indexOf('function leaveAttempt(g)'), html.indexOf('function recordFailAttempt(g)'));
 assert.match(part, /AB\.hearts\.forfeit\(g\.levelId\)/);
 assert.doesNotMatch(part, /AB\.hearts\.refund/);
});
test('restart consumes existing attempt even without mistakes', () => {
 const part = html.slice(html.indexOf('function doRestart(g)'), html.indexOf('// ---------------- router screen',html.indexOf('function doRestart(g)')));
 assert.match(part, /AB\.hearts\.forfeit\(g\.levelId\)/);
 assert.doesNotMatch(part, /AB\.hearts\.refund/);
});
test('ad diagnostics exposes consent, SDK, banner, errors and retry', () => {
 assert.match(bridge, /const diagnostics =/);
 assert.match(bridge, /adStatus\.bannerError/);
 assert.match(bridge, /adStatus\.consent/);
 assert.match(html, /Ad diagnostics/);
 assert.match(html, /Retry banner/);
});
