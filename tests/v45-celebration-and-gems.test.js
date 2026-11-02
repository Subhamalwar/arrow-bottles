const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const src=fs.readFileSync('www/index.html','utf8');
test('gem ads do not have daily cap',()=>{assert.match(src,/mission_chest_double: 1 \};/);assert.match(src,/placement === 'gems' \|\| placement === 'bottle_double'/);});
test('shop presents unlimited optional gem ads',()=>{assert.match(src,/aria-label': 'Watch an optional ad for 2 gems'/);assert.match(src,/el\('span', \{ class: 'ab-gem-name' \}, 'Watch an ad'\)/);});
test('victory celebration tiers and reduced motion',()=>{assert.match(src,/function victoryCelebration\(g\)/);assert.match(src,/level % 10 === 0/);assert.match(src,/level % 5 === 0/);assert.match(src,/prefers-reduced-motion: reduce/);assert.match(src,/victoryCelebration\(g\);/);});
test('bottle reward video grants only after earned reward',()=>{assert.match(src,/AB\.ads\.rewarded\('bottle_double'/);assert.match(src,/if \(ok\) \{\s*AB\.economy\.addCoins\(reward\.n, 'bottle_double'\)/);});
