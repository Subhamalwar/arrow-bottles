#!/usr/bin/env python3
"""Arrow Escape v3: generate 300 deterministic, checked braid puzzles.

Construction: Each 3-row braid traverses columns in one horizontal direction,
reversing vertical direction on each column. Cutting it only at forward horizontal
steps guarantees every horizontal exit ray sees only later pieces in its braid.
A final downward arrow may look into the next braid; lower braids have no upward
exit rays, so solving from the bottom braid upward always works. Optional key
locks similarly point only forward in this known winning order. No retry loops.
"""
import json, math, random, sys

def level_counts(level):
    return 12 + 4 * (level - 1) if level <= 20 else min(132, 88 + (level-20)//6)

def dims(level):
    target=level_counts(level)
    width=max(9,min(23,round(math.sqrt(target*3.85*.82))))
    if width%2==0:width+=1
    # guarantee slack for board variations: 3-row braids can contain <= width-1 arrows.
    bands=max(2,math.ceil(target/(width-2)*1.24))
    return width,3*bands,bands

def braid_path(w, yoff, direction, ending, rng):
    # Randomly alternate two Hamilton traversals of each 3x2 gadget:
    #  - vertical U-shaped braid (entry and exit at same edge row)
    #  - sideways S-shaped braid (flips top/bottom entry for next gadget).
    # This creates interleaving bends instead of identical U shapes.
    xs=list(range(w)) if direction==1 else list(range(w-1,-1,-1))
    path=[]
    edge=0  # next gadget entry top (0) or bottom (2)
    pair_limit=(w-1) if ending=='down' else (w-3)
    variants=[rng.choice([0,1]) for _ in range(pair_limit//2)]
    if ending=='down':
        # Last single column must enter from the top to exit down into
        # the lower band, giving a provably acyclic global ordering.
        variants[-1]=(sum(variants[:-1])%2)
    for k in range(0,pair_limit,2):
        a,b=xs[k:k+2]
        other=2-edge
        if variants[k//2]==0:  # vertical folded U
            path.extend([(a,edge),(a,1),(a,other),(b,other),(b,1),(b,edge)])
        else:  # interwoven sideways S
            path.extend([(a,edge),(b,edge),(b,1),(a,1),(a,other),(b,other)])
            edge=other
    if ending=='side':
        # First cover the odd singleton column; then finish with a 3x2
        # sideways gadget whose head points OUT of the board, leaving
        # multiple independent free arrows across the full board.
        a=xs[-3]
        other=2-edge
        path.extend([(a,edge),(a,1),(a,other)])
        edge=other
        a,b=xs[-2:]
        other=2-edge
        path.extend([(a,edge),(b,edge),(b,1),(a,1),(a,other),(b,other)])
    else:
        assert edge==0
        a=xs[-1]
        path.extend([(a,0),(a,1),(a,2)])
    path=[(x,yoff+y) for x,y in path]
    assert len(path)==w*3 and len(set(path))==len(path)
    for a,b in zip(path,path[1:]): assert abs(a[0]-b[0])+abs(a[1]-b[1])==1
    return path

def partition(path, count, direction, ending, rng):
    # Cut only at forward horizontal moves which have already reached the
    # furthest column seen. Such ray heads cannot see older placed pieces.
    visited_max=-10**9
    candidates=[]
    for i in range(1,len(path)):
        x0=path[i-1][0]*direction
        x1=path[i][0]*direction
        visited_max=max(visited_max,x0)
        if x1>x0 and x1>=visited_max and i>=1 and len(path)-i-1>=2:
            candidates.append(i)
        visited_max=max(visited_max,x1)
    # Exact count, minimum two cells per arrow; memoized feasibility checks.
    from functools import lru_cache
    @lru_cache(None)
    def feasible(j,last,remain):
        if remain==0:return (len(path)-1-last)>=2
        if j==len(candidates):return False
        if feasible(j+1,last,remain):return True
        return candidates[j]-last>=2 and feasible(j+1,candidates[j],remain-1)
    if not feasible(0,-1,count-1):raise ValueError(f'Cannot partition {len(path)} into {count} arrows; candidates={len(candidates)}')
    cuts=[];last=-1;need=count-1
    for j,pos in enumerate(candidates):
        if not need: break
        can_take=pos-last>=2 and feasible(j+1,pos,need-1)
        can_skip=feasible(j+1,last,need)
        take=can_take and (not can_skip or rng.random()<.77)
        if take:cuts.append(pos);last=pos;need-=1
    assert need==0
    parts=[];start=0
    for end in cuts+[len(path)-1]:
        chunk=path[start:end+1]
        assert len(chunk)>=2
        d=(chunk[-1][0]-chunk[-2][0],chunk[-1][1]-chunk[-2][1])
        if end!=len(path)-1:assert d==(direction,0)
        if end==len(path)-1:assert d==((direction,0) if ending=='side' else (0,1))
        parts.append(chunk);start=end+1
    assert len(parts)==count
    return parts

def solve(w,h,pieces):
    dx=(0,1,0,-1);dy=(-1,0,1,0)
    occ={c:i for i,a in enumerate(pieces) for c in a[3:]}
    if len(occ)!=sum(len(a)-3 for a in pieces):return False,0,0
    removed=set();maxwave=0;waves=0
    while len(removed)<len(pieces):
        free=[]
        for i,a in enumerate(pieces):
            if i in removed or (a[1]>=0 and a[1] not in removed): continue
            cc=a[3:]; px,py=cc[-2]%w,cc[-2]//w; x,y=cc[-1]%w,cc[-1]//w
            d=next((k for k in range(4) if (x-px,y-py)==(dx[k],dy[k])),None)
            if d is None:return False,0,0
            x+=dx[d];y+=dy[d]
            if all(occ.get(xx+w*yy,i)==i for xx,yy in walkray(x,y,dx[d],dy[d],w,h)):
                free.append(i)
        if not free: return False,maxwave,waves
        for i in free:
            for c in pieces[i][3:]:occ.pop(c,None)
            removed.add(i)
        maxwave=max(maxwave,len(free));waves+=1
    return True,maxwave,waves

def walkray(x,y,dx,dy,w,h):
    while 0<=x<w and 0<=y<h:
        yield x,y
        x+=dx;y+=dy

def generate(level,seed):
    rng=random.Random(seed)
    target=level_counts(level)
    w,h,bands=dims(level)
    endings=[('side' if rng.random()<.68 else 'down') for _ in range(bands)]
    capacities=[w-2 if e=='side' else w-1 for e in endings]
    if sum(capacities)<target:
        endings=['down']*bands
        capacities=[w-1]*bands
    allocated=[0]*bands
    for _ in range(target):
        opts=[i for i in range(bands) if allocated[i]<capacities[i]]
        # Balanced but non-uniform density to avoid every level looking identical.
        i=min(opts,key=lambda j:allocated[j]/capacities[j]+rng.random()*.24)
        allocated[i]+=1
    assert sum(allocated)==target
    all_pieces=[]
    records=[]
    for band in range(bands):
        direction=rng.choice([-1,1])
        ending=endings[band]
        path=braid_path(w,band*3,direction,ending,rng)
        parts=partition(path,allocated[band],direction,ending,rng)
        for chunk in parts:
            records.append((band,chunk))
            all_pieces.append([rng.randrange(5),-1,0,*[x+y*w for x,y in chunk]])
    # Distinct arrow colors; a handful of directional key locks for depth.
    # Every locked-by ID must be a later arrow in the global winning order,
    # so even cross-braid locks cannot form a deadlock.
    for i,p in enumerate(all_pieces):
        band=records[i][0]
        if level>=5 and i+1<len(all_pieces) and rng.random()<(0.04 if level<11 else .075):
            nxt=rng.randrange(i+1,min(len(all_pieces),i+12))
            p[1]=nxt
        if level>=11 and rng.random()<.018:p[2]=1
    # Rearrange to avoid leaking the solution order via click positions or indices.
    order=list(range(target));rng.shuffle(order)
    to_new={old:new for new,old in enumerate(order)}
    shuffled=[all_pieces[old][:] for old in order]
    for p in shuffled:
        if p[1]>=0:p[1]=to_new[p[1]]
    valid,max_free,waves=solve(w,h,shuffled)
    assert valid, f'Unsolvable level {level}'
    turns=sum(sum((p[j]-p[j-1])!=(p[j-1]-p[j-2]) for j in range(5,len(p))) for p in shuffled)
    tier='easy' if level<=4 else 'medium' if level<=10 else 'hard' if level<=20 else 'superhard'
    # Long enough to study paths, short enough to retain urgency; adaptive timer
    # can be calibrated to actual anonymized completion times later.
    limit=min(540, max(100, int(target*3.2 + 55))) * 1000
    # Progressive *in-game* Puzzle IQ, no claim to measure human intelligence.
    iq=85+round(95*math.log1p(level)/math.log1p(300))+min(7,round(turns/max(1,target)*2))
    return {'w':w,'h':h,'tier':tier,'moveLimit':target+max(5,target//6),
            'spare':max(5,target//6),'arrows':shuffled,'timeLimitMs':limit,
            'puzzleIQ':iq,'complexity':{'turns':turns,'solutionWaves':waves,'maxFreeWave':max_free}}

def main():
    levels=[]
    for i in range(1,301):
        v=generate(i,seed=0xB4A1D+i*989)
        levels.append(v)
        if i%50==0:print('generated',i,'arrows',len(v['arrows']),'board',v['w'],v['h'],flush=True)
    # Ensure displayed Puzzle IQ only increases when the complexity increases;
    # current level increase provides a guaranteed baseline, not a real IQ score.
    for i,v in enumerate(levels):
        if i and v['puzzleIQ']<=levels[i-1]['puzzleIQ']:
            v['puzzleIQ']=levels[i-1]['puzzleIQ']
    if len(sys.argv)>1:
        with open(sys.argv[1],'w') as f:json.dump(levels,f,separators=(',',':'))
    print('Complete:',len(levels),'levels')
if __name__=='__main__':main()
