const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'www', 'index.html'), 'utf8');
function getModule(relativePath, nextModule) {
  const start = html.indexOf('// ---- js/' + relativePath);
  const end = nextModule ? html.indexOf('// ---- js/' + nextModule, start + 1) : html.indexOf('</script>', start);
  assert.ok(start > -1 && end > start, relativePath + ' exists');
  return html.slice(start, end);
}
const context = vm.createContext({window: {AB: {}}, console, Int16Array, Set, Map});
context.AB = context.window.AB;
vm.runInContext(getModule('data/levels.js', 'core/store.js'), context);
vm.runInContext(getModule('game/session.js', 'game/board.js'), context);
const {LEVELS, DAILY, TUTORIAL, Session} = context.AB;

// Puzzle engine and level design invariants (real executable logic, no browser mocks).
test('all 300 campaign layouts have monotonic increasing complexity', () => {
  assert.equal(LEVELS.length, 300);
  const stats = LEVELS.map(x => x.arrows.length);
  for (let i=1; i<stats.length; i++) assert.ok(stats[i]>=stats[i-1], `Level ${i+1} reverted to an easier board`);
  assert.ok(stats[299]>stats[4], 'late-game puzzles must be harder than early game');
  for (const x of LEVELS) assert.ok(x.timeLimitMs >= 80000, 'level timer is positive and playable');
});
test('all 300 campaign levels remain solvable', () => {
  const unsolvable = LEVELS.map((x,i) => !Session.solve(x).solvable ? i+1 : 0).filter(Boolean);
  assert.equal(unsolvable.length, 0, `Unsolvable boards: ${unsolvable.join(", ")}`);
});
test('daily puzzles and tutorial data remain available', () => {
  assert.equal(DAILY.length, 366);
  assert.equal(TUTORIAL.length, 4);
});
test('timer causes failure at zero, not the old move counter', () => {
  const session = new Session(LEVELS[0], {mode:'campaign',levelId:1});
  session.used = session.moveLimit + 20;
  session._settle();
  assert.equal(session.status, 'playing');
  session.elapse(session.timeLimitMs - 1000);
  assert.equal(session.status,'playing');
  session.elapse(1000);
  assert.equal(session.status,'failed');
  assert.equal(session.remainingTime(),0);
});
test('reward extension restores timed level and does not grant twice accidentally', () => {
  const s = new Session(LEVELS[8],{mode:'campaign',levelId:9});
  s.elapse(s.timeLimitMs);
  assert.equal(s.status,'failed');
  assert.equal(s.addTime(20000),true);
  assert.equal(s.status,'playing');
  assert.equal(s.remainingTime(),20000);
  const snap=s.snapshot();
  const resumed=Session.restore(snap, LEVELS[8]);
  assert.equal(resumed.remainingTime(),20000);
  resumed.elapse(19999);
  assert.equal(resumed.status,'playing');
  resumed.elapse(1);
  assert.equal(resumed.status,'failed');
});
test('legacy move-based saves load with an active timer', () => {
  const s=new Session(LEVELS[0], {mode:'campaign',levelId:1});
  const old=s.snapshot(); delete old.timeRemainingMs; old.status='failed';
  old.used=999; const restored=Session.restore(old, LEVELS[0]);
  assert.equal(restored.status,'playing');
  assert.ok(restored.remainingTime()>0);
});
test('tutorial is not timed', () => {
  const s = new Session(TUTORIAL[0],{mode:'tutorial',levelId:0});
  assert.equal(s.timed,false);
  s.elapse(10**9);
  assert.equal(s.status,'playing');
});
test('two time extensions are enforced and saved', () => {
  assert.match(html, /const offer = \(g\.rescueCount \|\| 0\) < MAX_EXTENSIONS/);
  assert.match(html, /const MAX_EXTENSIONS = 2;/);
  assert.match(html, /const CONTINUE_SECONDS = 20;/);
  assert.match(html, /rescueCount: g\.rescueCount \|\| 0/);
  assert.match(html, /g\.session\.addTime\(CONTINUE_SECONDS \* 1000\)/);
});
test('Android rewards require real AdMob completion and fake purchases are blocked', () => {
  assert.match(html, /nativeAds\(\)\.rewarded\(\)/);
  assert.match(html, /if \(paymentsDisabled\(\)\) \{ AB\.ui\.toast/);
  assert.match(html, /'Browser demo banner \(no revenue\)'/);
});
