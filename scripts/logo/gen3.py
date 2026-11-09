import json,re
src=open("gen.py").read()
exec(src[:src.index("M={}")])  # constants, T, ring
P="/mnt/user-data/outputs/artifacts/7fdfce12/project/"
BOOK="M48 76 Q84 62 120 76 Q156 62 192 76 V184 Q156 172 120 186 Q84 172 48 184 Z"
def book(fill,shadow=GR,bg="#FBF9F5"):
    return f'<rect width="240" height="240" rx="54" fill="{bg}"/><path d="{BOOK}" fill="{shadow}" transform="translate(8 9)"/><path d="{BOOK}" fill="{fill}"/>'
def gutter(c): return f'<path d="M120 78 V184" stroke="{c}" stroke-width="2" opacity=".55"/>'
def lines(c,ys=(100,118,136,154,172),x1=134,x2=180,w=6,last=164,first=None):
    out=""
    for i,y in enumerate(ys):
        x=last if i==len(ys)-1 else x2
        col=first if (first and i==0) else c
        out+=f'<path d="M{x1} {y} H{x}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
    return out
def greek(c,rows,size=14,x=157,y0=104,dy=17,first=None):
    out=""
    for i,r in enumerate(rows):
        col=first if (first and i==0) else c
        out+=f'<text x="{x}" y="{y0+i*dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="{size}" textLength="42" lengthAdjust="spacingAndGlyphs" fill="{col}">{r}</text>'
    return out
JOHN=["ΕΝΑΡΧΗ","ΗΝΟΛΟ","ΓΟΣΚΑΙ","ΟΛΟΓΟΣ","ΗΝΠΡΟΣ"]
M={}
M["C3a"]=("Codex Τ: ruled lines","The round-1 codex with the Τ moved to the left page and five lines of writing on the right; the last line runs short, like the end of a paragraph.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,BU,700)+lines(BU,w=7 if not sm else 12,ys=(100,118,136,154,172) if not sm else (104,132,160)))
M["C3b"]=("Codex Τ: uncial script","The right page carries real uncial capitals, written continuously as in the manuscripts: ΕΝ ΑΡΧΗ ΗΝ Ο ΛΟΓΟΣ (John 1:1). At 48 px and below the letters become lines.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,BU,700)+(greek(BU,JOHN) if not sm else lines(BU,w=12,ys=(104,132,160))))
M["C3c"]=("Codex Τ: rubric","As a scribe would rubricate it: the first line of the right page and the Τ in LPD Gold, the rest in Bust.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,G,700)+(greek(BU,JOHN,first=G) if not sm else lines(BU,w=12,ys=(104,132,160),first=G)))
M["C3d"]=("Codex Τ: dark","Dark Blue pages, gold Τ, script in Bust; the strongest contrast of the set.",
 lambda u,sm: book(DB)+gutter(BU)+T(84,160,86,G,700)+(greek(BU,JOHN) if not sm else lines(BU,w=12,ys=(104,132,160))))
M["C3e"]=("Codex Τ: cursive hand","The right page as flowing handwriting: wavy strokes in place of letters, so the Τ stays the only letterform.",
 lambda u,sm: book(B)+gutter(BU)+T(84,160,86,BU,700)+"".join(
   f'<path d="M134 {y} q5 -6 10 0 t10 0 t10 0 t10 0{"" if i==3 else " t6 0"}" fill="none" stroke="{BU}" stroke-width="{5 if not sm else 10}" stroke-linecap="round" stroke-linejoin="round"/>'
   for i,y in enumerate((102,124,146,168) if not sm else (106,138,170)))) 
M["C3f"]=("Codex Τ: on Bust","The uncial version without the tile shadow, on the Bust background used across the Moss materials.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/><path d="{BOOK}" fill="{B}"/>'+gutter(BU)+T(84,160,86,BU,700)+(greek(BU,JOHN) if not sm else lines(BU,w=12,ys=(104,132,160))))
def svg(k,size,i):
    sm=size<=48
    return f'<svg width="{size}" height="{size}" viewBox="0 0 240 240" role="img" aria-label="Tertius logo, {M[k][0]}" style="display: block">{M[k][2](f"{k}{i}",sm)}</svg>'
tpl=open(P+"SealB.dc.html").read()
head=tpl[:tpl.index('<div style="width: 480px')]; tail=tpl[tpl.index('</x-dc>'):]
body0=tpl[tpl.index('<div style="width: 480px'):tpl.index('</x-dc>')]
for k,(title,note,_) in M.items():
    # rebuild body from SealB structure, swapping svgs and note
    b=body0
    svgs=re.findall(r'<svg width="(\d+)".*?</svg>',b,re.S)
    for i,m in enumerate(re.finditer(r'<svg width="(\d+)".*?</svg>',body0,re.S)):
        b=b.replace(m.group(0),svg(k,int(m.group(1)),i),1)
    b=re.sub(r'(<p style="margin: 0;[^>]*>).*?</p>',lambda m:m.group(1)+note+'</p>',b,flags=re.S)
    open(P+f"{k}.dc.html","w").write(head.replace("Seal: bigger ring text",title)+b+tail)
c=json.load(open(P+"canvas.json"))
y=1460+3*800+60
c["notes"]["round3"]={"x":0,"y":y-200,"text":"Round 3: Codex Τ with script","kind":"title1","maxW":1600}
for i,k in enumerate(M):
    f=f"{k}.dc.html"; c["boards"][f]={"x":(i%3)*560,"y":y+(i//3)*700,"w":480,"h":620,"title":M[k][0]}
    if f not in c["order"]: c["order"].append(f)
json.dump(c,open(P+"canvas.json","w"),indent=1)
# preview sheet
out=[]
for i,k in enumerate(M):
    x,yy=(i%3)*260,(i//3)*300
    out.append(f'<g transform="translate({x},{yy})">{svg(k,220,9)}<g transform="translate(0,230)">{svg(k,48,8)}</g><g transform="translate(60,230)">{svg(k,32,7)}</g></g>')
open("sheet3.svg","w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="780" height="600" style="background:#fff">{"".join(out)}</svg>')
