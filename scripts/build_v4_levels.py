#!/usr/bin/env python3
"""Deterministic unified Arrow Escape campaign.

A continuous Hamiltonian braid visits *every* row band in alternating directions.
Cuts are made only at frontier-facing heads (or a downward bridge). The exiting
ray therefore intersects only cells later in the same master path. Reversing
that path gives a valid solution, even when arrows cross former band boundaries.

The same logical grid supports both a warped 'weave' canvas and a concentric
'orbit' presentation. Orbit maps rows to angle and columns to radius; paths are
actual curved arcs in the viewer, with the exact same blocking semantics.
"""
import sys, json, random, math
from pathlib import Path
from build_v3_levels import braid_path, solve, level_counts, dims


def unified(level, seed):
    rng = random.Random(seed)
    target=level_counts(level)
    w,h,bands=dims(level)
    sign=rng.choice((-1,1))
    path=[]; candidates=[]; band_of=[]; bridges=[]
    for b in range(bands):
        d=sign if b%2==0 else -sign
        start=len(path)
        part=braid_path(w,b*3,d,'down',rng)
        if path:
            assert abs(path[-1][0]-part[0][0])+abs(path[-1][1]-part[0][1])==1
            # A cut at the bridging cell gives a downward-exiting long-range arrow.
            bridges.append(start)
        path.extend(part)
        band_of.extend([b]*len(part))
        xmax=-10**9
        for i in range(start+1,len(path)):
            prev=path[i-1][0]*d; current=path[i][0]*d
            xmax=max(xmax,prev)
            if current>prev and current>=xmax:
                # Avoid boundaries to create pieces that physically span adjoining bands.
                if i-start>=3 and len(path)-1-i>=3:
                    candidates.append(i)
            xmax=max(xmax,current)
    assert len(set(path))==len(path)==w*h
    # All cuts must be after at least two cells and leave at least two for the final piece.
    candidates=sorted(set(candidates+bridges))
    need=target-1
    from functools import lru_cache
    @lru_cache(None)
    def feasible(j,last,remain):
        if remain==0:return len(path)-1-last>=2
        if j>=len(candidates) or len(candidates)-j<remain:return False
        p=candidates[j]
        if p-last>=2 and feasible(j+1,p,remain-1):return True
        return feasible(j+1,last,remain)
    if not feasible(0,-1,need):
        raise ValueError(f'level {level}: target {target}, candidates {len(candidates)}, bands {bands}, size {w}x{h}')
    cuts=[];last=-1
    for j,p in enumerate(candidates):
        if not need:break
        take=p-last>=2 and feasible(j+1,p,need-1)
        skip=feasible(j+1,last,need)
        # Around one in three boundaries should become vertical exit shafts.
        select=take and (not skip or rng.random() < (0.66 if p in bridges else 0.81))
        if select:
            cuts.append(p);last=p;need-=1
    assert not need
    parts=[];a=0
    for z in cuts+[len(path)-1]:
        chunk=path[a:z+1]
        assert len(chunk)>=2
        parts.append(chunk);a=z+1
    assert len(parts)==target
    crossing=sum(any(p[1]//3 != c[0][1]//3 for p in c) for c in parts)
    # Prepare source pieces, then shuffle IDs (in-game does not reveal removal order).
    pieces=[[rng.randrange(5),-1,0,*[x+y*w for x,y in p]] for p in parts]
    for i,p in enumerate(pieces):
        if level>=5 and i+1<len(pieces) and rng.random() < (0.12 if level<15 else 0.19):
            # Prefer a distant key: a move from a lower/later section unlocks an earlier one.
            options=[j for j in range(i+1,len(pieces))
                     if abs((parts[j][0][1]//3)-(parts[i][-1][1]//3))>=2]
            if options:p[1]=rng.choice(options)
        if level>=11 and rng.random()<.016:p[2]=1
    idx=list(range(target));rng.shuffle(idx)
    to_new={old:new for new,old in enumerate(idx)}
    out=[pieces[old][:] for old in idx]
    for p in out:
        if p[1]>=0:p[1]=to_new[p[1]]
    valid,max_free,waves=solve(w,h,out)
    if not valid:raise ValueError(f'unsolvable v4 level {level}')
    # Count actual cross-row-band dependencies (locks and vertical rays).
    long_locks=sum(1 for i,p in enumerate(pieces) if p[1]>=0 and
                   abs(parts[p[1]][0][1]-parts[i][-1][1])>=6)
    angle_cut_count=sum(1 for z in cuts if z in bridges)
    mode='orbit' if (level>=10 and (level%5 in (0,1))) or (level>=30 and level%3==0) else 'weave'
    turns=sum(sum((p[j]-p[j-1])!=(p[j-1]-p[j-2]) for j in range(5,len(p))) for p in out)
    iq=85+round(95*math.log1p(level)/math.log1p(300))+min(7,round(turns/max(1,target)*2))
    limit=min(540,max(100,int(target*3.2+55)))*1000
    return {'w':w,'h':h,'tier':'easy' if level<=4 else 'medium' if level<=10 else 'hard' if level<=20 else 'superhard',
            'moveLimit':target+max(5,target//6),'spare':max(5,target//6),
            'arrows':out,'timeLimitMs':limit,'puzzleIQ':iq,'boardStyle':mode,
            'complexity':{'turns':turns,'solutionWaves':waves,'maxFreeWave':max_free,
                          'crossBandArrows':crossing,'crossBandLocks':long_locks,
                          'verticalBridgeExits':angle_cut_count,'connectedPath':True}}

def main():
    levels=[]
    for i in range(1,301):
        l=unified(i,0xB4A1D+i*989)
        levels.append(l)
        if i%30==0:print('done',i,'arrows',len(l['arrows']),'style',l['boardStyle'], 'cross', l['complexity']['crossBandArrows'],flush=True)
    for i,v in enumerate(levels):
        if i and v['puzzleIQ']<levels[i-1]['puzzleIQ']:
            v['puzzleIQ']=levels[i-1]['puzzleIQ']
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('v4-campaign.json')
    dest.write_text(json.dumps(levels,separators=(',',':')))
    print('Complete:',len(levels), 'unified layouts',sum(x['boardStyle']=='orbit' for x in levels),'orbits',dest)
if __name__=='__main__':main()
