import json, os
P="/mnt/user-data/outputs/artifacts/7fdfce12/project/"
B,DB,G,R,GR,DG,BU,SK="#245B8F","#103166","#D58936","#701811","#939598","#474448","#F3EDE2","#C1E1E5"
SERIF="Vollkorn, Georgia, serif"
def T(x,y,s,fill,w=800): return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{SERIF}" font-weight="{w}" font-size="{s}" fill="{fill}">Τ</text>'
def ring(uid,r,txt,size,fill):
    import math
    L=round(2*math.pi*r*0.985)
    return (f'<path id="{uid}" d="M120,120 m-{r},0 a{r},{r} 0 1,1 {2*r},0 a{r},{r} 0 1,1 -{2*r},0" fill="none"/>'
            f'<text font-family="{SERIF}" font-weight="700" font-size="{size}" fill="{fill}"><textPath href="#{uid}" textLength="{L}" lengthAdjust="spacing">{txt}</textPath></text>')
# each mark: function(uid, small) -> inner svg
M={}
M["SealB"]=("Seal: bigger ring text", "Ring text cut to ΕΓΩ ΤΕΡΤΙΟΣ twice, set larger so it reads at app-icon size; at 32 px and below the ring drops out.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/><circle cx="120" cy="120" r="104" fill="{DB}"/>'
   + (f'<circle cx="120" cy="120" r="62" fill="none" stroke="{G}" stroke-width="3"/>'+ring(u,78,"ΕΓΩ ΤΕΡΤΙΟΣ · ΕΓΩ ΤΕΡΤΙΟΣ · ",24,BU)+T(120,150,86,BU) if not sm else T(120,160,120,BU)))
M["SealW"]=("Seal: wax", "A pressed wax seal in LPD Red with a gold Τ, the way a scribe closed a letter. No lettering, so it holds at every size.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/>'
   '<path d="M120 22 C150 20 160 34 184 44 C206 54 214 74 216 98 C220 124 212 142 206 160 C196 190 172 208 146 214 C120 222 98 216 76 206 C50 194 32 174 26 146 C20 118 24 90 38 68 C54 42 88 24 120 22 Z" fill="'+R+'"/>'
   f'<circle cx="120" cy="120" r="70" fill="none" stroke="#5a120d" stroke-width="6"/>'+T(120,153,96,G))
M["SealR"]=("Seal: reference", "Τ inside a double ring, with the verse reference ΡΩΜ ΙϚ΄ ΚΒ΄ (Rom 16:22) as a short arc at the foot; the arc drops out at small sizes.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{B}"/><circle cx="120" cy="120" r="92" fill="none" stroke="{BU}" stroke-width="5"/>'
   f'<circle cx="120" cy="120" r="80" fill="none" stroke="{G}" stroke-width="2"/>'
   + (T(120,146,96,BU) + f'<path id="{u}" d="M56,132 A64,64 0 0,0 184,132" fill="none"/><text font-family="{SERIF}" font-weight="700" font-size="17" letter-spacing="2" fill="{G}" text-anchor="middle"><textPath href="#{u}" startOffset="50%">ΡΩΜ ΙϚ΄ ΚΒ΄</textPath></text>' if not sm else T(120,156,120,BU)))
M["CodexO"]=("Codex: open book", "An open codex seen from above; the gutter and the top edge of the pages make the Τ.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/>'
   f'<path d="M30 74 Q76 58 116 72 V192 Q76 178 30 192 Z" fill="{B}"/><path d="M210 74 Q164 58 124 72 V192 Q164 178 210 192 Z" fill="{B}"/>'
   f'<rect x="54" y="78" width="132" height="18" rx="3" fill="{BU}"/><rect x="111" y="78" width="18" height="114" fill="{BU}"/>')
M["CodexD"]=("Codex: ribbon", "The original codex, in Dark Blue with a gold Τ and an LPD Red bookmark ribbon.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/>'
   f'<path d="M48 76 Q84 62 120 76 Q156 62 192 76 V184 Q156 172 120 186 Q84 172 48 184 Z" fill="{DB}"/>'
   f'<path d="M150 70 V210 L161 198 L172 210 V68 Z" fill="{R}"/>'+T(108,164,100,G,700))
M["CodexL"]=("Codex: line", "Drawn in a single weight of line on Sky, closer to the MossMethod illustrations; lightest of the three.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{SK}"/>'
   f'<path d="M44 78 Q82 62 120 78 Q158 62 196 78 V186 Q158 172 120 188 Q82 172 44 186 Z M120 78 V188" fill="none" stroke="{DB}" stroke-width="{14 if sm else 8}" stroke-linejoin="round"/>'
   +T(82,160,72,B,700)+f'<path d="M140 104 H178 M140 124 H178 M140 144 H170" stroke="{B}" stroke-width="6" stroke-linecap="round"/>' * (0 if sm else 1))
M["InkP"]=("Inkwell: pen Τ", "The reed pen stands upright in the well and its crosspiece makes the Τ: the letter is the tool.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/>'
   f'<rect x="62" y="36" width="116" height="18" rx="4" fill="{DB}"/><path d="M111 54 H129 V150 L120 166 L111 150 Z" fill="{G}"/>'
   f'<path d="M58 210 Q58 162 92 152 H148 Q182 162 182 210 Z" fill="{DB}"/><rect x="98" y="140" width="44" height="16" rx="3" fill="{B}"/>')
M["InkC"]=("Inkwell: roundel", "The original inkwell simplified to two shapes in a Dark Blue circle, with a gold pen; made to survive 20 px.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/><circle cx="120" cy="120" r="100" fill="{DB}"/>'
   f'<path d="M122 128 L170 46 L182 53 L134 135 Z" fill="{G}"/>'
   f'<path d="M70 190 Q70 148 98 140 H142 Q170 148 170 190 Z" fill="{BU}"/><rect x="100" y="124" width="40" height="18" rx="3" fill="{BU}"/>'
   + ('' if sm else T(120,182,40,DB,700)))
M["InkD"]=("Inkwell: ink drop", "A single drop of ink, with a gold Τ in the drop.",
 lambda u,sm: f'<rect width="240" height="240" rx="54" fill="{BU}"/>'
   f'<path d="M120 34 C120 34 186 112 186 150 C186 188 156 212 120 212 C84 212 54 188 54 150 C54 112 120 34 120 34 Z" fill="{DB}"/>'
   +T(120,190,{True:110,False:96}[sm],G))
def svg(k,size,i):
    sm=size<=32
    return f'<svg width="{size}" height="{size}" viewBox="0 0 240 240" role="img" aria-label="Tertius logo, {M[k][0]}" style="display: block">{M[k][2](f"{k}{i}",sm)}</svg>'
tpl=open(P+"Codex.dc.html").read()
head=tpl[:tpl.index('<div style="width: 480px')]
tail=tpl[tpl.index('</x-dc>'):]
for k,(title,note,_) in M.items():
    body=f'''<div style="width: 480px; height: 620px; box-sizing: border-box; padding: 40px 40px 32px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; background: #FFFFFF; font-family: Inter, system-ui, sans-serif">
{svg(k,220,0)}
<div style="display: flex; align-items: center; gap: 20px; align-self: stretch; padding: 18px 24px; background: #FBF9F5; border-radius: 16px">
{svg(k,72,1)}
<div style="display: flex; flex-direction: column; gap: 2px">
<div style="font-family: {SERIF}; font-weight: 800; font-size: 40px; line-height: 1.05; color: {DB}">Tertius</div>
<div style="font-size: 14px; color: {DG}">NT Greek Vocab Trainer</div>
</div>
</div>
<div style="display: flex; align-items: flex-end; gap: 18px">{svg(k,48,2)}{svg(k,32,3)}{svg(k,20,4)}</div>
<p style="margin: 0; font-size: 13px; line-height: 1.45; color: {DG}; text-align: center">{note}</p>
</div>
'''
    h=head.replace("Codex Τ",title)
    open(P+f"{k}.dc.html","w").write(h+body+tail.replace('"height":560','"height":620'))
c=json.load(open(P+"canvas.json"))
rows=[("Seal",["SealB","SealW","SealR"]),("Codex",["CodexD","CodexO","CodexL"]),("Inkwell",["InkC","InkP","InkD"])]
y0=1460
for r,(name,ks) in enumerate(rows):
    y=y0+r*800
    c["notes"][f"row{name}"]={"x":0,"y":y-90,"text":f"{name}: three more","kind":"title2","maxW":1600}
    for i,k in enumerate(ks):
        f=f"{k}.dc.html"; c["boards"][f]={"x":i*560,"y":y,"w":480,"h":620,"title":M[k][0]}
        if f not in c["order"]: c["order"].append(f)
c["notes"]["round2"]={"x":0,"y":y0-200,"text":"Round 2: Seal, Codex, Inkwell","kind":"title1","maxW":1600}
c["notes"]["head"]["text"]="Tertius: six logo directions (round 1)"
json.dump(c,open(P+"canvas.json","w"),indent=1)
