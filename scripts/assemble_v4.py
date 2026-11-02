#!/usr/bin/env python3
"""V4 patch on a v3 HTML app. Does not rerun the original v2->v3 patches."""
import re,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
p=root/'www/index.html'
s=p.read_text()
levels=json.loads((root/'scripts/v4-campaign.json').read_text())
s,n=re.subn(r'(?m)^AB\.LEVELS = .*?;$','AB.LEVELS = '+json.dumps(levels,separators=(',',':'))+';',s,count=1)
assert n==1

def replace(old,new,n=1):
    global s
    assert s.count(old)>=n, f'missing source patch: {old[:110]}'
    s=s.replace(old,new,n)

replace('this.w = level.w; this.h = level.h; this.tier = level.tier;',
        "this.w = level.w; this.h = level.h; this.tier = level.tier;\n      this.boardStyle = level.boardStyle === 'orbit' ? 'orbit' : 'weave';")
replace('r.layoutVersion === 3','r.layoutVersion === 4')
replace('layoutVersion: 3','layoutVersion: 4')

# Board geometry: one continuous warped network or a circular polar projection.
replace('''      const pad = 14;
      // the board card extends 0.3 cell beyond the grid on each side
      this.cam.cell = Math.max(6, Math.min((this.VW - 2 * pad) / (s.w + 0.6), (this.VH - 2 * pad) / (s.h + 0.6)));
      this.cam.zoom = 1;
      this.cam.ox = (this.VW - this.cam.cell * s.w) / 2;
      this.cam.oy = (this.VH - this.cam.cell * s.h) / 2;''','''      const pad = 14;
      const [bw, bh] = this.boardDims();
      this.cam.cell = Math.max(5, Math.min((this.VW - 2 * pad) / bw, (this.VH - 2 * pad) / bh));
      this.cam.zoom = 1;
      this.cam.ox = (this.VW - this.cam.cell * bw) / 2;
      this.cam.oy = (this.VH - this.cam.cell * bh) / 2;''')
replace('''    // canvas-local CSS px of a cell centre
    scr(x, y) { const k = this.scale(); return [this.cam.ox + (x + 0.5) * k, this.cam.oy + (y + 0.5) * k]; }''','''    // Real x/y grid cells are connected across the entire puzzle. Projection is
    // purely visual, never alters collision, tapping order or solving legality.
    isOrbit() { return !!this.session && this.session.boardStyle === 'orbit'; }
    orbitGeom() {
      const s = this.session;
      const inner = Math.max(2.8, s.h / (Math.PI * 1.75) * 0.72);
      const outer = inner + (s.w + 0.6) * 0.84;
      const half = outer + 1.25;
      return {inner, outer, half, span:Math.PI * 1.75, start:-Math.PI*0.82};
    }
    boardDims() {
      if (this.isOrbit()) { const g=this.orbitGeom(); return [g.half*2,g.half*2]; }
      return [this.session.w+1.4,this.session.h+1.4];
    }
    worldPoint(x,y) {
      if (this.isOrbit()) {
        const g=this.orbitGeom();
        const r=g.inner + (x+0.5)*0.84;
        const a=g.start + (y+0.5)*g.span/this.session.h;
        return [g.half + r*Math.cos(a),g.half + r*Math.sin(a)];
      }
      // A bounded smooth distortion removes the look of isolated mini-grids.
      return [x+1.15+0.22*Math.sin(y*0.61)+0.12*Math.sin(x*0.51+y*0.29),
              y+1.15+0.29*Math.sin(x*0.48+y*0.13)];
    }
    // Canvas-local CSS px for any logical (possibly fractional) grid coordinate.
    scr(x, y) { const k = this.scale(), [wx,wy]=this.worldPoint(x,y);
      return [this.cam.ox+wx*k,this.cam.oy+wy*k]; }
    tangent(a, pts) {
      pts = pts || this.cellPts(a);
      const q=pts[pts.length-1], p=pts[pts.length-2];
      const d=Math.hypot(q[0]-p[0],q[1]-p[1]) || 1;
      return [(q[0]-p[0])/d,(q[1]-p[1])/d];
    }''')
replace('''    cellPts(a) { const w = this.session.w; return a.cells.map(c => this.scr(c % w, (c / w) | 0)); }''','''    cellPts(a) {
      const w=this.session.w, cells=a.cells, pts=[];
      for(let i=0;i<cells.length;i++) {
        const x=cells[i]%w,y=(cells[i]/w)|0;
        if (i && this.isOrbit()) {
          const prev=cells[i-1], px=prev%w, py=(prev/w)|0;
          for (let t=1;t<=4;t++) {
            const z=t/4;pts.push(this.scr(px+(x-px)*z,py+(y-py)*z));
          }
        } else pts.push(this.scr(x,y));
      }
      return pts;
    }''')
replace('''        pts.push([hd[0] + DX[a.dir] * k * 0.29, hd[1] + DY[a.dir] * k * 0.29]);''','''        const [tx,ty] = this.tangent(a,pts);
        pts.push([hd[0] + tx * k * 0.29, hd[1] + ty * k * 0.29]);''')
replace('''      const pad = Math.max(6, k * 0.3), bx = this.cam.ox - pad, by = this.cam.oy - pad;
      const bw = s.w * k + 2 * pad, bh = s.h * k + 2 * pad, rad = Math.min(22, k * 0.8);
      ctx.fillStyle = C.line; ctx.beginPath(); ctx.roundRect(bx, by + 5, bw, bh, rad); ctx.fill();
      ctx.fillStyle = C.card; ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, rad); ctx.fill();''','''      if (this.isOrbit()) {
        const g=this.orbitGeom();
        const cx=this.cam.ox+g.half*k,cy=this.cam.oy+g.half*k;
        const r=(g.outer+0.55)*k;
        ctx.fillStyle=C.line;ctx.beginPath();ctx.arc(cx,cy+4,r,0,Math.PI*2);ctx.fill();
        ctx.fillStyle=C.card;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.fill();
        ctx.fillStyle=C.lilac;ctx.beginPath();ctx.arc(cx,cy,Math.max(2,g.inner-0.8)*k,0,Math.PI*2);ctx.fill();
        ctx.strokeStyle=C.line;ctx.lineWidth=Math.max(1.1,k*0.06);
        ctx.beginPath();ctx.arc(cx,cy,g.inner*k,0,Math.PI*2);ctx.stroke();
      } else {
        const pad=Math.max(6,k*0.3),bx=this.cam.ox-pad,by=this.cam.oy-pad;
        const [ww,hh]=this.boardDims();
        const bw=ww*k+2*pad,bh=hh*k+2*pad,rad=Math.min(22,k*0.8);
        ctx.fillStyle=C.line;ctx.beginPath();ctx.roundRect(bx,by+5,bw,bh,rad);ctx.fill();
        ctx.fillStyle=C.card;ctx.beginPath();ctx.roundRect(bx,by,bw,bh,rad);ctx.fill();
      }''')
replace('''      const toEdge = [y, w - 1 - x, s.h - 1 - y, x][a.dir];
      const ex = sx + DX[a.dir] * (toEdge + 0.5) * k, ey = sy + DY[a.dir] * (toEdge + 0.5) * k;
      ctx.save();
      ctx.strokeStyle = this.C.grape; ctx.lineWidth = Math.max(2, k * 0.1); ctx.lineCap = 'round';
      ctx.setLineDash([0.1, Math.max(6, k * 0.32)]);
      ctx.beginPath(); ctx.moveTo(sx + DX[a.dir] * k * 0.6, sy + DY[a.dir] * k * 0.6); ctx.lineTo(ex, ey); ctx.stroke();
      ctx.restore();''','''      const toEdge=[y,w-1-x,s.h-1-y,x][a.dir];
      ctx.save();ctx.strokeStyle=this.C.grape;ctx.lineWidth=Math.max(2,k*0.1);
      ctx.lineCap='round';ctx.setLineDash([0.1,Math.max(6,k*0.32)]);
      ctx.beginPath();
      for(let i=1;i<=Math.max(2,Math.ceil((toEdge+0.6)*4));i++) {
        const z=Math.min(toEdge+0.6,i/4);
        const [qx,qy]=this.scr(x+DX[a.dir]*z,y+DY[a.dir]*z);
        if (i===1)ctx.moveTo(qx,qy);else ctx.lineTo(qx,qy);
      }
      ctx.stroke();ctx.restore();''')
replace('''      const k = this.scale(), dx = DX[a.dir], dy = DY[a.dir];
      const o = { glow: a.id === this.hint ? t : -1, selected: a.id === this.selected };''','''      const k = this.scale(), [dx,dy] = this.tangent(a,pts);
      const o = { glow: a.id === this.hint ? t : -1, selected: a.id === this.selected };''')
replace('''      const dx = DX[a.dir], dy = DY[a.dir], nx = -dy, ny = dx;''','''      const q=pts[pts.length-1], p=pts[pts.length-2], mag=Math.hypot(q[0]-p[0],q[1]-p[1])||1;
      const dx=(q[0]-p[0])/mag,dy=(q[1]-p[1])/mag,nx=-dy,ny=dx;''')
replace('''      const s = this.session, k = this.scale(), bw = s.w * k, bh = s.h * k, m = 40;''','''      const [ww,hh]=this.boardDims(),k=this.scale(),bw=ww*k,bh=hh*k,m=40;''')
# Circle mode should identify itself in a visible, accessible descriptor.
replace("'Puzzle IQ ' + g.level.puzzleIQ + ' · ' + g.level.arrows.length + ' arrows' : null;",
        "'Puzzle IQ ' + g.level.puzzleIQ + ' · ' + g.level.arrows.length + ' arrows' + (g.level.boardStyle === 'orbit' ? ' · Orbit Maze' : ' · Woven Maze') : null;")
styles='''
/* V4: a single cross-board dependency network, with circular orbit challenges. */
.g-puzzle-iq {max-width: 100%; text-align: center; font-size: 11px;}
'''
replace('</style>',styles+'</style>')
assert s.count('AB.LEVELS = ') == 1
p.write_text(s)
(root/'arrow-bottles-final-index.html').write_text(s)
print('v4 HTML',len(s),'levels',len(levels))
