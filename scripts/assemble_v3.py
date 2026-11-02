#!/usr/bin/env python3
"""Patch the existing v2 HTML app with v3 generator output and UI/UX changes."""
import json,re,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
p=root/'www/index.html';s=p.read_text()
levels=json.loads((root/'scripts/v3-campaign.json').read_text())
compact=json.dumps(levels,separators=(',',':'),ensure_ascii=False)
s,n=re.subn(r'(?m)^AB\.LEVELS = .*?;$','AB.LEVELS = '+compact+';',s,count=1)
assert n==1,'Campaign board array not found'
# Thin colored stick-shafts. Keep head small and visible, no giant filled triangles.
s=s.replace('strokeW() { return Math.max(4, this.scale() * 0.36); }',
            'strokeW() { return Math.max(2.1, this.scale() * (this.session && this.session.mode !== \'tutorial\' ? 0.145 : 0.29)); }')
s=s.replace('const head = pts[pts.length - 1], TL = k * 0.46, TW = k * 0.4, drop = Math.max(1.5, sw * 0.13);',
            'const head = pts[pts.length - 1], TL = k * 0.29, TW = k * 0.19, drop = Math.max(0.65, sw * 0.1);')
s=s.replace('Math.max(2.2, k * 0.12)', 'Math.max(1.2, k * 0.07)')
s=s.replace('const r = Math.max(5, sw * 0.62);','const r = Math.max(3.7, sw * 0.7);')
s=s.replace('hd[0] + DX[a.dir] * k * 0.46, hd[1] + DY[a.dir] * k * 0.46',
            'hd[0] + DX[a.dir] * k * 0.29, hd[1] + DY[a.dir] * k * 0.29')
s=s.replace('const k = this.scale(), tol = this.strokeW() / 2 + 14;',
            'const k = this.scale(), tol = this.strokeW() / 2 + Math.min(13, Math.max(6, k * 0.31));')
s=s.replace('if (second <= tol && second - bd < k * 0.08) return null;',
            'if (second <= tol && second - bd < Math.max(1, k * 0.085)) return null;')
# Dedicated tap zoom, in addition to pinch zoom and fit; important for small phones.
s=s.replace("this.fitBtn.hidden = true;\n      stage.appendChild(this.fitBtn);", """this.fitBtn.hidden = true;
      stage.appendChild(this.fitBtn);
      this.zoomBtn = AB.util.el('button', { class: 'g-zoom', type: 'button', 'aria-label': 'Zoom in to select thin arrows' }, '+');
      this.zoomBtn.addEventListener('click', () => this.zoomAt(this.VW / 2, this.VH / 2, this.cam.zoom * 1.55));
      this.zoomBtn.hidden = true;
      stage.appendChild(this.zoomBtn);""")
s=s.replace('this.fitBtn.hidden = !this.zoomable();', 'this.fitBtn.hidden = !this.zoomable();\n      this.zoomBtn.hidden = !this.zoomable();')
s=s.replace('this.canvas.remove(); this.fitBtn.remove();','this.canvas.remove(); this.fitBtn.remove(); this.zoomBtn.remove();')
# Show Puzzle IQ across campaign / replay and map; not asserted as a psychometric measure.
s=s.replace("const title = el('div', { class: 'g-title' }, el('h1', {}, g.title), badge);", """const iqValue = (g.mode === 'campaign' || g.mode === 'replay') && Number.isFinite(g.level.puzzleIQ)
      ? 'Puzzle IQ ' + g.level.puzzleIQ + ' · ' + g.level.arrows.length + ' arrows' : null;
    const iqTag = iqValue ? el('span', { class: 'g-puzzle-iq', 'aria-label': 'In-game puzzle difficulty rating' }, iqValue) : null;
    const title = el('div', { class: 'g-title' }, el('h1', {}, g.title), iqTag, badge);""")
s=s.replace("'aria-label': 'Level ' + id + (isCleared(id) ? ', ' + n + ' stars, replay' : ', play') },",
            "'aria-label': 'Level ' + id + ', Puzzle IQ ' + (L.puzzleIQ || 'unrated') + (isCleared(id) ? ', ' + n + ' stars, replay' : ', play') },")
s=s.replace("el('b', { class: 'ab-lv-n' }, String(id)),\n            el('span', { class: 'ab-lv-stars'",
            "el('b', { class: 'ab-lv-n' }, String(id)),\n            el('small', { class: 'ab-lv-iq' }, 'IQ ' + (L.puzzleIQ || '—')),\n            el('span', { class: 'ab-lv-stars'")
s=s.replace("const bits = [starRow(info.stars),", """const iqAnnouncement = (g.mode === 'campaign' || g.mode === 'replay') && Number.isFinite(g.level.puzzleIQ)
      ? el('p', { class: 'g-win-iq' }, 'Puzzle IQ ' + g.level.puzzleIQ + ' conquered · ' + g.level.arrows.length + ' arrows') : null;
    const bits = [starRow(info.stars), iqAnnouncement,""")
# Save compatibility: avoid applying a v2 move-index snapshot to a different board.
s=s.replace("if (r && r.mode === g.mode && Number(r.levelId) === Number(g.levelId) && r.snap) {",
            "if (r && r.mode === g.mode && Number(r.levelId) === Number(g.levelId) && r.snap &&\n        ((g.mode !== 'campaign' && g.mode !== 'replay') || r.layoutVersion === 3)) {")
s=s.replace('const rec = { mode: g.mode, levelId: g.levelId, snap: g.session.snapshot(),',
            'const rec = { mode: g.mode, levelId: g.levelId, layoutVersion: 3, snap: g.session.snapshot(),')
# UI styles added into the existing stylesheet, before the closing head.
styles='''
/* Arrow Escape v3: accessible dense puzzles and game-only Puzzle IQ. */
.g-puzzle-iq { font-size: 11px; font-weight: 900; color: var(--grape); white-space: nowrap; letter-spacing: .015em; }
.g-zoom { position: absolute; bottom: 58px; right: 6px; width: 49px; height: 45px; border: 0;
  border-radius: var(--r-pill); background: var(--card); color: var(--grape); font-weight: 900;
  font-size: 25px; box-shadow: var(--shadow-soft); opacity: .85; cursor: pointer; }
.g-zoom:active { transform: scale(.96); }
.ab-lv-iq { display: block; font-weight: 800; font-size: 10px; color: var(--grape); }
.g-win-iq { color: var(--grape); background: var(--lilac); border-radius: 16px; font-weight: 900;
  font-size: 14px; padding: 8px 12px; text-align: center; }
'''
assert '</style>' in s
s=s.replace('</style>',styles+'</style>',1)
# Clear previously generated metadata if ZIP reassembled multiple times
assert s.count('AB.LEVELS = ') == 1
p.write_text(s)
(root/'arrow-bottles-final-index.html').write_text(s)
print('Updated web game',len(s),'characters; levels',len(levels))
