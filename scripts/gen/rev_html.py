import json,html,sys,zlib
d=json.load(open(sys.argv[1]))
GMAP="https://www.google.com/maps?cid=1892105797985093642"
STAR='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>'
COLORS=["#2E4A32","#7FAF3A","#C98A1B","#3D6344","#B5654A","#5A7D8C","#8A6BB0","#1D3322"]
def short(n):
    p=n.split()
    return p[0] if len(p)==1 else f"{p[0]} {p[1][0]}."
withtext=[r for r in d if r[5].strip()]; star=[r for r in d if not r[5].strip()]
LOW={"Александър Трайков","Anna Gateva"}
withtext.sort(key=lambda r:(r[0] in LOW, r[1]!=5, -min(len(r[5]),420)))
out=[]
for i,(name,rating,when,av,pid,text) in enumerate(withtext+star):
    t=html.escape(text.strip().replace("​","")).replace("\n","<br>")
    nm=short(name.strip()); ini=html.escape(nm[0].upper()); col=COLORS[zlib.crc32(name.encode())%len(COLORS)]
    stars="".join(f'<i class="{"on" if k<rating else ""}">{STAR}</i>' for k in range(5))
    cls="rv"+("" if t else " rv--short")+(" is-extra" if i>=9 else "")
    out.append(f'''        <a class="{cls}" href="{GMAP}" target="_blank" rel="noopener">
          <div class="rv-head"><span class="rv-av" style="background:{col}">{ini}</span><div class="rv-who"><b>{html.escape(nm)}</b><span>{html.escape(when)}</span></div><span class="rv-g" aria-label="Google">G</span></div>
          <div class="rv-stars" aria-label="{rating} от 5 звезди">{stars}</div>
          {f'<p>{t}</p>' if t else ''}
        </a>''')
print("\n".join(out))
