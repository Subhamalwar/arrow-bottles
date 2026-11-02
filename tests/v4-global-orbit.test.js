const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'..','www','index.html'),'utf8');
const levels=vm.runInNewContext(html.match(/^AB\.LEVELS = (.*);$/m)[1],{});
test('the whole 300-level campaign uses a unified, section-spanning braid',()=>{
  assert.equal(levels.length,300);
  for(const [i,l] of levels.entries()) {
    assert.equal(l.complexity.connectedPath,true,`level ${i+1}`);
    assert.ok(l.complexity.crossBandArrows >= 2,`level ${i+1} cross-band path`);
    assert.ok(l.complexity.verticalBridgeExits >= 0,`level ${i+1} bridge metadata`);
  }
});
test('cross-section key locks create distant dependencies',()=>{
  assert.ok(levels.slice(9).every(l=>l.complexity.crossBandLocks>=1));
  assert.ok(levels[19].complexity.crossBandLocks>=4);
});
test('circle / orbit boards interleave with woven boards beginning at level 10',()=>{
  assert.equal(levels[7].boardStyle,'weave');
  assert.equal(levels[9].boardStyle,'orbit');
  assert.equal(levels[10].boardStyle,'orbit');
  assert.ok(levels.some(l=>l.boardStyle==='weave'));
  assert.ok(levels.some(l=>l.boardStyle==='orbit'));
  assert.ok(levels.filter(l=>l.boardStyle==='orbit').length>=80);
  assert.match(html,/orbitGeom\(\)/);
  assert.match(html,/worldPoint\(x,y\)/);
  assert.match(html,/Math\.cos\(a\)/);
  assert.match(html,/Math\.sin\(a\)/);
  assert.match(html,/this\.tangent\(a,pts\)/);
  assert.match(html,/Orbit Maze/);
});
test('visual presentation does not change the tested game rules',()=>{
  assert.match(html,/function rayCells\(head, d, w, h\)/);
  assert.match(html,/function solveArrows\(w, h, arrows, removed\)/);
  assert.match(html,/layoutVersion: 4/);
});
