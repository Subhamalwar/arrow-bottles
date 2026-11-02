const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'www', 'index.html'), 'utf8');
const levels = vm.runInNewContext(html.match(/^AB\.LEVELS = (.*);$/m)[1], {});

// Reproduce the game's model guarantees with independent assertions.
test('the first twenty levels grow by exactly four arrows, starting at twelve', () => {
  for (let index = 0; index < 20; index++) {
    assert.equal(levels[index].arrows.length, 12+4*index, `level ${index+1}`);
  }
});
test('the full three hundred level campaign never becomes less populated', () => {
  assert.equal(levels.length, 300);
  for (let i = 1; i < levels.length; i++)
    assert.ok(levels[i].arrows.length >= levels[i-1].arrows.length, `arrows dropped at ${i+1}`);
});
test('puzzles have genuine bends and clean disjoint paths', () => {
  for (const [index, level] of levels.entries()) {
    const occupied = new Set();
    let turns = 0;
    for (const [arrowId, arrow] of level.arrows.entries()) {
      assert.ok(arrow.length>=5, `level ${index+1} arrow ${arrowId} too short`);
      if (arrow[1] >= 0) assert.ok(arrow[1] < level.arrows.length && arrow[1] !== arrowId, 'bad key lock');
      for (let j=3; j<arrow.length; j++) {
        const c=arrow[j];
        assert.ok(c>=0 && c<level.w*level.h, 'cell out of bounds');
        assert.ok(!occupied.has(c), `level ${index+1} has overlapping arrows at ${c}`);
        occupied.add(c);
        if (j>3) assert.equal(Math.abs(c%level.w - arrow[j-1]%level.w)+Math.abs(Math.floor(c/level.w)-Math.floor(arrow[j-1]/level.w)),1,'noncontiguous arrow');
        if (j>4 && c-arrow[j-1] !== arrow[j-1]-arrow[j-2]) turns++;
      }
    }
    assert.ok(turns >= level.arrows.length, `level ${index+1} not intertwined enough (${turns} turns)`);
  }
});
test('Puzzle IQ is a visible nondecreasing in-game challenge rating', () => {
  assert.match(html, /Puzzle IQ /);
  assert.match(html, /'g-puzzle-iq'/);
  assert.match(html, /'g-win-iq'/);
  for (let i=1;i<levels.length;i++)assert.ok(levels[i].puzzleIQ>=levels[i-1].puzzleIQ);
  assert.ok(levels.at(-1).puzzleIQ <= 220, 'rating should be a sensible game score');
});
test('thin arrow shafts, small tips, touch tolerance, and zoom controls exist', () => {
  assert.match(html, /0\.145/);
  assert.match(html, /TL = k \* 0\.29, TW = k \* 0\.19/);
  assert.match(html, /class: 'g-zoom'/);
  assert.match(html, /this\.zoomAt\(this\.VW \/ 2/);
});
test('resume snapshots from a different campaign layout are not blindly reused', () => {
  assert.match(html, /r\.layoutVersion === 4/);
  assert.match(html, /layoutVersion: 4/);
});
