#!/usr/bin/env python3
"""Apply the official SecRAM 2.0 risk matrix to the catalogue, before and after EWTS, under three level mappings. Writes secram.json."""
import json, csv, numpy as np
from collections import Counter
from secram import risk, CLS
nu=lambda x:1+4*(np.asarray(x,float)-1)/9
CUT=np.array([1.8,2.6,3.4,4.2]); lam=lambda v:int(np.searchsorted(CUT,v,side="left")+1)
rnd=lambda v:int(min(5,max(1,np.floor(v+.5))))
W={"Strong":1.0,"Moderate":.75,"Weak":.5,"None":.25}
rows=list(csv.DictReader(open("data/ratings.csv")))
def lv(I,L,kind,D=None,A=None,S=None):
    if kind=="default": return lam(L),lam(I)
    if kind=="round": return rnd(L),rnd(I)
    if kind=="maximpact": return lam(L),rnd(max(nu(D),nu(A),S))
out={"assets":[],"variants":{}}
for r in rows:
    D,R,E,A,D2,S=[float(r[k]) for k in ("D","R","E","A","D2","S")]
    I=(nu(D)+nu(A)+S)/3; L=(nu(R)+nu(E)+nu(D2))/3; w=W[r["evidence"]]
    Ia=3+w*(I-3); La=3+w*(L-3)
    rec={"id":r["id"],"ev":r["evidence"],"w":w}
    for kind in ("default","round","maximpact"):
        l,i=lv(I,L,kind,D,A,S); rec[kind]={"cell":[l,i],"risk":risk(l,i)}
        if kind=="maximpact":
            # EWTS shrinkage applied to the max-impact level and L
            ima=3+w*(max(nu(D),nu(A),S)-3); la_,ia_=lam(La),rnd(ima)
        elif kind=="default": la_,ia_=lam(La),lam(Ia)
        else: la_,ia_=rnd(La),rnd(Ia)
        rec[kind]["adj_cell"]=[la_,ia_]; rec[kind]["adj_risk"]=risk(la_,ia_)
    out["assets"].append(rec)
for kind in ("default","round","maximpact"):
    b=Counter(a[kind]["risk"] for a in out["assets"]); c=Counter(a[kind]["adj_risk"] for a in out["assets"])
    out["variants"][kind]={"before":dict(b),"after":dict(c),
      "risk_changes":sum(a[kind]["risk"]!=a[kind]["adj_risk"] for a in out["assets"]),
      "cell_changes":sum(a[kind]["cell"]!=a[kind]["adj_cell"] for a in out["assets"]),
      "changed_ids":[a["id"] for a in out["assets"] if a[kind]["risk"]!=a[kind]["adj_risk"]],
      "occupied":len({tuple(a[kind]["cell"]) for a in out["assets"]})}
out["agree_default_vs_round"]=sum(a["default"]["risk"]==a["round"]["risk"] for a in out["assets"])
out["agree_default_vs_max"]=sum(a["default"]["risk"]==a["maximpact"]["risk"] for a in out["assets"])
# worked example
ex=json.load(open("framework.json"))["example"]
out["example"]={"cell":[ex["lvlL"],ex["lvlI"]],"risk":risk(ex["lvlL"],ex["lvlI"]),"adj_cell_half":ex["cell_adj"]["0.5"],"adj_risk_half":risk(*ex["cell_adj"]["0.5"])}
# box of reachable cells (rule-admissible) -> risk levels
bc=ex["box"]["cells"]; rk=Counter()
for k,n in bc.items(): rk[risk(int(k[0]),int(k[1]))]+=n
out["example"]["box_risk"]=dict(rk)
# LLM raters: official risk level per model run (condition A)
import sys, os, glob, re
sys.path.insert(0,"rater_study"); import analyze_raters as ar
runs=ar.load("rater_study/responses"); IDS=ar.IDS
lvl3=[];names=[]
for k in sorted(runs):
    if k[1]!="A": continue
    sc=ar.scores_from(runs[k],"A"); lvl3.append([CLS[risk(lam(sc[i][1]),lam(sc[i][0]))] for i in IDS]); names.append(k)
M=np.array(lvl3); out["raters"]={"alpha_risk_level":ar.alpha_ordinal(M),"all_runs_same":float(np.mean([len(set(M[:,j]))==1 for j in range(M.shape[1])]))}
mods=sorted({k[0] for k in names}); mm=[]
for m in mods:
    idx=[n for n,k in enumerate(names) if k[0]==m]; mm.append([int(np.round(np.median(M[idx,j]))) for j in range(M.shape[1])])
mm=np.array(mm); out["raters"]["models_same"]=float(np.mean([len(set(mm[:,j]))==1 for j in range(mm.shape[1])]))
out["raters"]["alpha_models"]=ar.alpha_ordinal(mm)
cat=[CLS[a["default"]["risk"]] for a in out["assets"]]
out["raters"]["model_vs_catalogue_same"]={m:float(np.mean(mm[n]==np.array(cat))) for n,m in enumerate(mods)}
out["raters"]["dist"]={m:dict(Counter(["Low","Medium","High"][x] for x in mm[n])) for n,m in enumerate(mods)}
json.dump(out,open("secram.json","w"),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="assets"},indent=1))
