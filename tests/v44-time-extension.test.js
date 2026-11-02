const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(require('node:path').join(__dirname,'../www/index.html'),'utf8');
test('time extension rewarded offer is not gated behind level 5',()=>{assert.doesNotMatch(html,/levelNum\s*>=\s*5\s*&&\s*AB\.ads/);assert.match(html,/if \(AB\.ads && AB\.ads\.rewarded\)/);});
test('time extension remains capped at two per attempt',()=>{assert.match(html,/MAX_EXTENSIONS\s*=\s*2/);assert.match(html,/g\.rescueCount \|\| 0\) < MAX_EXTENSIONS/);});
test('continue only after earned ad reward',()=>{assert.match(html,/if \(ok\) rescue\(g\); else failPanel\(g\)/);});
