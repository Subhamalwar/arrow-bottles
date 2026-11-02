#!/usr/bin/env python3
"""One-time phone-first usability improvements on assembled v4 game HTML."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'www/index.html';s=p.read_text()
def rep(old,new):
 global s
 assert s.count(old)==1,(old[:120],s.count(old))
 s=s.replace(old,new,1)
rep("      this.zoomBtn.hidden = true;\n      stage.appendChild(this.zoomBtn);", """      this.zoomBtn.hidden = true;
      stage.appendChild(this.zoomBtn);
      // Phones are the main platform. Provide a 44px+ zoom-out target as well
      // as the existing zoom-in, pinch-zoom, drag-to-pan and Fit controls.
      this.zoomOutBtn = AB.util.el('button', { class: 'g-zoom g-zoom-out', type: 'button', 'aria-label': 'Zoom out' }, '\u2212');
      this.zoomOutBtn.addEventListener('click', () => this.zoomAt(this.VW / 2, this.VH / 2, this.cam.zoom / 1.55));
      this.zoomOutBtn.hidden = true;
      stage.appendChild(this.zoomOutBtn);""")
rep("      this.zoomBtn.hidden = !this.zoomable();\n      this.fit();", """      this.zoomBtn.hidden = !this.zoomable();
      this.zoomOutBtn.hidden = !this.zoomable();
      this.fit();""")
rep("      this.canvas.remove(); this.fitBtn.remove(); this.zoomBtn.remove();", "      this.canvas.remove(); this.fitBtn.remove(); this.zoomBtn.remove(); this.zoomOutBtn.remove();")
rep("      this.fitBtn.classList.remove('on');\n      this.refresh();", """      this.fitBtn.classList.remove('on');
      this.zoomOutBtn.disabled = true;
      this.zoomBtn.disabled = !this.zoomable();
      this.refresh();""")
rep("      this.fitBtn.classList.toggle('on', this.cam.zoom > 1.001);\n      this.refresh();", """      this.fitBtn.classList.toggle('on', this.cam.zoom > 1.001);
      this.zoomOutBtn.disabled = this.cam.zoom <= 1.001;
      this.zoomBtn.disabled = this.cam.zoom >= ZOOM_MAX - 0.001;
      this.refresh();""")
rep("""            if (g && !g.moved && !g.multi && now() - g.t0 < TAP_MS) {
              const id = this.pick(p.x, p.y);
              if (this.opts.onArrowTap) this.opts.onArrowTap(id);
            }""", """            if (g && !g.moved && !g.multi) {
              const duration = now() - g.t0;
              if (duration < TAP_MS) {
                const id = this.pick(p.x, p.y);
                if (this.opts.onArrowTap) this.opts.onArrowTap(id);
              } else if (duration >= 430 && this.zoomable() && this.cam.zoom < ZOOM_MAX - 0.001) {
                // Holding your finger anywhere on a busy mobile board zooms
                // towards that exact spot without mistakenly firing an arrow.
                this.zoomAt(p.x, p.y, this.cam.zoom * 1.65);
              }
            }""")
rep('''/* V4: a single cross-board dependency network, with circular orbit challenges. */
.g-puzzle-iq {max-width: 100%; text-align: center; font-size: 11px;}''','''/* V4: one connected field, curved polar puzzles and phone-first controls. */
.g-puzzle-iq {max-width: 100%; text-align: center; font-size: 11px;}
.g-zoom-out { bottom: 110px; }
.g-zoom:disabled {opacity:.4; cursor:default;}
/* Smartphones are the primary aspect ratio, tablets use the base styles. */
@media (max-width: 480px) {
  .g-root { gap: 5px; padding-right: 8px; padding-left: 8px; }
  .g-top { grid-template-columns: 46px minmax(0, 1fr) auto; gap: 5px; }
  .g-pause {width: 46px; height: 46px;}
  .g-title h1 {font-size: clamp(20px, 6.3vw, 26px);}
  .g-puzzle-iq {font-size: 10px; letter-spacing: 0; white-space: normal; line-height: 1.2;}
  .g-moves {padding: 7px 10px; font-size: 14px;}
  .g-stage {isolation: isolate;}
  .g-zoom, .g-fit {right: 4px; z-index: 3; min-width: 45px; min-height: 45px;}
  .g-zoom {width: 45px; height: 45px;}
  .g-zoom-out {bottom: 114px;}
  .g-zoom:not(.g-zoom-out) {bottom: 62px;}
  .g-fit {bottom: 10px;}
  .g-tray {border-radius: 16px;}
  .g-pw {min-width: 52px;}
}
@media (max-width: 360px) {
  .g-bottle svg {width: 28px; height: 50px;}
  .g-bottle-n {font-size: 10px;}
  .g-top {grid-template-columns: 44px minmax(0, 1fr) auto;}
  .g-pause {width: 44px; height: 44px;}
}''')
p.write_text(s)
(root/'arrow-bottles-final-index.html').write_text(s)
print('Patched mobile UX',len(s))
