#!/usr/bin/env python3
"""Evidence->DREAD rule engine, worked example, SecRAM cell mapping checks. Writes framework.json."""
import json, itertools
import numpy as np
nu=lambda x:1+4*(np.asarray(x,float)-1)/9
CUT=[1.8,2.6,3.4,4.2]
def lvl(v): return int(np.searchsorted(np.array(CUT),v,side="left")+1)
# ---- rule table (High band as stated in the thesis slide; Medium/Low are this paper's completion) ----
# factor scores: 1=Low, 2=Medium, 3=High ; High always means "increases the rating"
IEF=["safety","scope","regulatory","cascading","recovery"]
LEF=["exposure","access","maturity","tools","automation"]
VEF=["documentation","interface","complexity","monitoring"]
RANGE={"D":{"H":(8,10),"M":(5,7),"L":(1,4)},"A":{"H":(8,10),"M":(5,7),"L":(1,4)},
       "E":{"H":(8,10),"M":(5,7),"L":(1,4)},"R":{"H":(8,10),"M":(5,7),"L":(1,4)},
       "D2":{"H":(7,10),"M":(4,6),"L":(1,3)}}
def band_D(f):   # >=3 High impact factors -> High (thesis); 1-2 High -> Medium; none -> Low
    n=sum(f[k]==3 for k in IEF); return "H" if n>=3 else ("M" if n>=1 else "L")
def band_A(f):   # fleet / cross-layer (thesis): either scope or cascading High
    m=max(f["scope"],f["cascading"]); return {3:"H",2:"M",1:"L"}[m]
def band_E(f):   # public + known tools (thesis): both High; else Medium if the five LEF scores sum to >=8
    if f["exposure"]==3 and f["tools"]==3: return "H"
    return "M" if sum(f[k] for k in LEF)>=8 else "L"
def band_R(f):   # automated & stable (thesis): both High; else Medium if the five LEF scores sum to >=8
    if f["automation"]==3 and f["maturity"]==3: return "H"
    return "M" if sum(f[k] for k in LEF)>=8 else "L"
def band_D2(f):  # public interfaces (thesis): interface transparency High; else sum>=6 Medium
    if f["interface"]==3: return "H"
    return "M" if sum(f[k] for k in VEF)>=6 else "L"
FUN={"D":(band_D,IEF),"A":(band_A,["scope","cascading"]),"E":(band_E,LEF),"R":(band_R,LEF),"D2":(band_D2,VEF)}
def bands(f): return {k:FUN[k][0](f) for k in FUN}
def comps(D,R,E,A,D2,S):
    I=(nu(D)+nu(A)+S)/3; L=(nu(R)+nu(E)+nu(D2))/3; return float(I),float(L),float((I+L)/2)
out={}
# ---- worked example (slide 9): Geo-awareness database tampering ----
f=dict(safety=3,scope=3,regulatory=2,cascading=3,recovery=2, exposure=3,access=2,maturity=3,tools=2,automation=3, documentation=2,interface=2,complexity=2,monitoring=2)
b=bands(f); pt=dict(D=8,A=8,R=8,E=7,D2=6); S=4
for k in pt: assert RANGE[k][b[k]][0]<=pt[k]<=RANGE[k][b[k]][1],(k,b[k],pt[k])
I,L,R=comps(pt["D"],pt["R"],pt["E"],pt["A"],pt["D2"],S)
I0=float((nu(pt["D"])+nu(pt["A"]))/2)
ex={"factors":f,"bands":b,"points":pt,"S":S,"sum":sum(pt.values()),"I":I,"L":L,"dreads":R,"I0":I0,"lvlI":lvl(I),"lvlL":lvl(L),"lvlR":lvl(R),"lvlI0":lvl(I0)}
ex["adj"]={str(w):float(3+w*(R-3)) for w in (1.0,0.75,0.5)}
ex["adj_lvl"]={str(w):lvl(3+w*(R-3)) for w in (1.0,0.75,0.5)}
ex["wstar"]=float((3.4-3)/(R-3))
# adjusted I,L separately (shrink toward 3)
ex["cell_adj"]={str(w):[lvl(3+w*(L-3)),lvl(3+w*(I-3))] for w in (1.0,0.75,0.5)}
# rule-admissible box: every rating anywhere in its band range
lo={k:RANGE[k][b[k]][0] for k in pt}; hi={k:RANGE[k][b[k]][1] for k in pt}
Imin,Lmin,_=comps(lo["D"],lo["R"],lo["E"],lo["A"],lo["D2"],S); Imax,Lmax,_=comps(hi["D"],hi["R"],hi["E"],hi["A"],hi["D2"],S)
ex["box"]={"Imin":Imin,"Imax":Imax,"Lmin":Lmin,"Lmax":Lmax,"lvlI":[lvl(Imin),lvl(Imax)],"lvlL":[lvl(Lmin),lvl(Lmax)]}
# fraction of the admissible integer grid that lands in the same cell
cnt=0;same=0
for D,A,R_,E,D2 in itertools.product(range(lo["D"],hi["D"]+1),range(lo["A"],hi["A"]+1),range(lo["R"],hi["R"]+1),range(lo["E"],hi["E"]+1),range(lo["D2"],hi["D2"]+1)):
    i,l,_=comps(D,R_,E,A,D2,S); cnt+=1; same+=(lvl(i)==ex["lvlI"] and lvl(l)==ex["lvlL"])
ex["box"]["n"]=cnt; ex["box"]["same_cell"]=same
from collections import Counter
cc=Counter(); bc=Counter()
for D,A,R_,E,D2 in itertools.product(range(lo["D"],hi["D"]+1),range(lo["A"],hi["A"]+1),range(lo["R"],hi["R"]+1),range(lo["E"],hi["E"]+1),range(lo["D2"],hi["D2"]+1)):
    i,l,r=comps(D,R_,E,A,D2,S); cc[f"{lvl(l)}{lvl(i)}"]+=1; bc[lvl(r)]+=1
ex["box"]["cells"]=dict(cc); ex["box"]["bands"]={str(k):v for k,v in bc.items()}
out["example"]=ex
# ---- exhaustive checks of the rule engine ----
def exhaustive():
    res={}
    # monotonicity per rating over its own factor subset (3^n combos, raise any factor by one step)
    allf=IEF+LEF+VEF; order={"L":0,"M":1,"H":2}; viol=0; checked=0
    for k,(fn,keys) in FUN.items():
        for vals in itertools.product((1,2,3),repeat=len(keys)):
            base=dict(zip(keys,vals)); 
            full={x:2 for x in allf}; full.update(base)
            b0=order[fn(full)]
            for j,key in enumerate(keys):
                if base[key]<3:
                    up=dict(full); up[key]+=1; checked+=1
                    if order[fn(up)]<b0: viol+=1
    res["rule_checked"]=checked; res["rule_viol"]=viol
    # rule bands -> rating ranges consistent and non-overlapping, contiguous 1..10
    ok=True
    for k,r in RANGE.items():
        ok&= r["L"][0]==1 and r["L"][1]+1==r["M"][0] and r["M"][1]+1==r["H"][0] and r["H"][1]==10
    res["ranges_partition_1_10"]=bool(ok)
    # full factor space 3^14: does every vector give a valid DREAD-S in [1,5] and monotone in band? (representative points)
    return res
out["exh"]=exhaustive()
# end-to-end monotonicity over the full 3^14 factor space using band lower/upper edges
import numpy as np
n14=3**14
grid=np.indices((3,)*14).reshape(14,-1).T+1   # all 4,782,969 vectors
names=IEF+LEF+VEF; col={n:i for i,n in enumerate(names)}
def bandcodes(g):
    c=lambda n:g[:,col[n]]
    nH=sum((c(k)==3).astype(int) for k in IEF); bD=np.where(nH>=3,2,np.where(nH>=1,1,0))
    bA=np.max(np.stack([c("scope"),c("cascading")]),0)-1
    sl=sum(c(k) for k in LEF)
    bE=np.where((c("exposure")==3)&(c("tools")==3),2,np.where(sl>=8,1,0))
    bR=np.where((c("automation")==3)&(c("maturity")==3),2,np.where(sl>=8,1,0))
    sv=sum(c(k) for k in VEF); bD2=np.where(c("interface")==3,2,np.where(sv>=6,1,0))
    return bD,bA,bE,bR,bD2
codes=bandcodes(grid)
# rating = lower edge of band range (conservative reading) -> I,L,DREAD-S ; check monotone when any factor raised
lowD={0:1,1:5,2:8}; lowD2={0:1,1:4,2:7}
def val(codes,S=4):
    bD,bA,bE,bR,bD2=codes
    m=lambda d,x:np.vectorize(d.get)(x)
    D=m(lowD,bD);A=m(lowD,bA);E=m(lowD,bE);R=m(lowD,bR);D2=m(lowD2,bD2)
    I=(nu(D)+nu(A)+S)/3;L=(nu(R)+nu(E)+nu(D2))/3;return (I+L)/2,I,L
sc,Iv,Lv=val(codes)
viol=0
strides=3**np.arange(13,-1,-1)
idx=((grid-1)*strides).sum(1)
for j in range(14):
    mask=grid[:,j]<3
    up=idx[mask]+strides[j]
    viol+=int((sc[up]<sc[idx[mask]]-1e-12).sum())
out["exh"]["factor_vectors"]=n14; out["exh"]["factor_monotone_viol"]=viol
out["exh"]["distinct_cells"]=len(set(zip(np.searchsorted(CUT,Lv,side="left"),np.searchsorted(CUT,Iv,side="left"))))
out["exh"]["dreads_min"]=float(sc.min()); out["exh"]["dreads_max"]=float(sc.max())
# ---- catalogue: slide variant I0=mean(nu(D),nu(A)); adjusted cells; multiplicative variant ----
import csv
rows=list(csv.DictReader(open("data/ratings.csv")))
W={"Strong":1.0,"Moderate":0.75,"Weak":0.5,"None":0.25}
cat=[]
for r in rows:
    D,R_,E,A,D2,Sx=[float(r[k]) for k in ("D","R","E","A","D2","S")]
    I,L,Rv=comps(D,R_,E,A,D2,Sx); I0=float((nu(D)+nu(A))/2); w=W[r["evidence"]]
    ra=3+w*(Rv-3); Ia=3+w*(I-3); La=3+w*(L-3); rm=w*Rv
    cat.append({"id":r["id"],"I":I,"L":L,"R":Rv,"I0":I0,"lI":lvl(I),"lL":lvl(L),"lI0":lvl(I0),"lR":lvl(Rv),"w":w,"ev":r["evidence"],
      "adj":ra,"lIa":lvl(Ia),"lLa":lvl(La),"lRa":lvl(ra),"Ia":Ia,"La":La,"mult":rm,"lRm":lvl(rm)})
out["cat"]=cat
out["slide_variant_cell_changes"]=[c["id"] for c in cat if c["lI0"]!=c["lI"]]
out["slide_variant_band_changes"]=int(sum(lvl((c["I0"]+c["L"])/2)!=c["lR"] for c in cat))
out["ewts_cell_moves"]=[{"id":c["id"],"from":[c["lL"],c["lI"]],"to":[c["lLa"],c["lIa"]],"ev":c["ev"]} for c in cat if (c["lL"],c["lI"])!=(c["lLa"],c["lIa"])]
out["mult_reclass"]=int(sum(c["lRm"]!=c["lR"] for c in cat))
out["mult_bands"]={k:int(sum(c["lRm"]==k for c in cat)) for k in range(1,6)}
json.dump(out,open("framework.json","w"),indent=1)
if __name__=="__main__":
    print(json.dumps({k:v for k,v in out.items() if k!="cat"},indent=1))
