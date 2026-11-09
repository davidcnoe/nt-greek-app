import json,re,random
exec(open("gen3.py").read().split("\nM={}\n")[0])
def cr(pts):
    d=f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts)-1):
        p0=pts[i-1] if i else pts[i]; p1=pts[i]; p2=pts[i+1]; p3=pts[i+2] if i+2<len(pts) else p2
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6); c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+=f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d
def hand(seed,ys,x1=133,x2=182,w=2.2,amp=3.2,loops=False,c=BU,lastfrac=.6,slant=1.2,step=2.6):
    r=random.Random(seed); out=""
    for li,y in enumerate(ys):
        end=x1+(x2-x1)*(lastfrac if li==len(ys)-1 else 1)
        x=x1+(0 if li else 5)
        while x<end-6:
            wl=min(r.uniform(9,22),end-x); pts=[(x,y)]; xx=x; up=True
            while xx<x+wl:
                xx+=step*r.uniform(.85,1.15)
                if up:
                    h=amp*r.uniform(.75,1.1)*(2.6 if loops and r.random()<.15 else 1)
                    pts.append((xx+slant,y-h))
                else: pts.append((xx,y))
                up=not up
            if up is False: pts.append((xx+step,y))
            out+=f'<path d="{cr(pts)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
            x=pts[-1][0]+r.uniform(4.5,6.5)
    return out
YS=(100,117,134,151,168)
SMALL=lambda c: lines(c,w=12,ys=(104,132,160))
M={}
M["C4a"]=("Cursive: fine","A finer pen: thin, joined strokes broken into words of different lengths, five lines, the last ending short. Gold Τ.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,G,700)+(hand(1,YS) if not sm else SMALL(BU)))
M["C4b"]=("Cursive: looped","The same hand with ascender loops, as in a Greek cursive with tall λ, δ, and θ.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,G,700)+(hand(2,YS,loops=True) if not sm else SMALL(BU)))
M["C4c"]=("Cursive: rubric","Fine hand, with the first line in gold to match the Τ.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,G,700)+(hand(1,YS[:1],c=G,lastfrac=1)+hand(5,YS[1:],lastfrac=.55) if not sm else lines(BU,w=12,ys=(104,132,160),first=G)))
M["C4d"]=("Cursive: dark","Fine hand on Dark Blue pages; the gold Τ stands out most here.",
 lambda u,sm: book(DB)+gutter(BU)+T(84,160,86,G,700)+(hand(1,YS) if not sm else SMALL(BU)))
M["C4e"]=("Cursive: on Bust","Fine hand, no shadow, on the Bust background.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/><path d="{BOOK}" fill="{B}"/>'+gutter(BU)+T(84,160,86,G,700)+(hand(1,YS) if not sm else SMALL(BU)))
M["C4f"]=("Cursive: four lines","Fewer, larger lines in the looped hand, which keep their shape down to 48 px.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,G,700)+(hand(3,(104,126,148,170),loops=True,w=3,amp=4.2,step=3.4) if not sm else SMALL(BU)))
src=open("gen3.py").read(); tailcode=src[src.index("def svg(k,size,i):"):]
tailcode=tailcode.replace("sm=size<=48","sm=size<=32").replace('Round 3: Codex Τ with script','Round 4: Codex Τ, cursive hand').replace("y=1460+3*800+60","y=1460+3*800+60+1600").replace('"round3"','"round4"').replace("sheet3","sheet4")
exec(tailcode)
