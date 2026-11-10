#!/usr/bin/env python3
"""Deterministic analysis for the VehicleSec paper. Input: data/ratings.csv. Output: results.json + results.tex macros."""
import csv, json, itertools
import numpy as np
from scipy.stats import kendalltau, spearmanr
rng = np.random.default_rng(20270115)
rows = list(csv.DictReader(open("data/ratings.csv")))
ids=[r["id"] for r in rows]; ev=[r["evidence"] for r in rows]
D=np.array([[r[k] for k in ("D","R","E","A","D2")] for r in rows],float); S=np.array([r["S"] for r in rows],float)
CUT=[1.8,2.6,3.4,4.2]; NAMES=["Minimal","Low","Medium","High","Critical"]
nu=lambda x:1+4*(np.asarray(x,float)-1)/9
def lvl(v): return np.searchsorted(np.array(CUT),v,side="left")+1   # 1..5 ; v<=1.8 ->1
def comps(D,S):
    n=nu(D); I=(n[...,0]+n[...,3]+S)/3; L=(n[...,1]+n[...,2]+n[...,4])/3
    return I,L,(I+L)/2
I,L,R=comps(D,S)
# identity with the published Eq.1
pub=(5/6)/5*nu(D).sum(-1)+S/6
res={"identity_maxdiff":float(np.abs(pub-R).max())}
li,ll,lr=lvl(I),lvl(L),lvl(R)
cells={}
for a,b in zip(ll,li): cells[f"{a}{b}"]=cells.get(f"{a}{b}",0)+1
res["cells"]=cells; res["n_cells"]=len(cells)
res["bands"]={NAMES[k-1]:int((lr==k).sum()) for k in range(1,6)}
res["I_levels"]={NAMES[k-1]:int((li==k).sum()) for k in range(1,6)}
res["L_levels"]={NAMES[k-1]:int((ll==k).sum()) for k in range(1,6)}
# aggregation sensitivity: product vs additive
P=I*L
res["tau_add_vs_prod"]=float(kendalltau(R,P)[0])
# plain DREAD baseline (unweighted mean of five raw ratings, no S)
dread=D.mean(1); res["tau_dread_vs_dreads"]=float(kendalltau(dread,R)[0])
top=lambda v,k: set(np.array(ids)[np.argsort(-v)[:k]])
res["top5_overlap"]=len(top(dread,5)&top(R,5)); res["top5_dread"]=sorted(top(dread,5)); res["top5_dreads"]=sorted(top(R,5))
res["dread_range"]=[float(dread.min()),float(dread.max())]; res["dreads_range"]=[float(R.min()),float(R.max())]
res["s_values"]=sorted(set(S.astype(int).tolist()))
# EWTS
W={"Strong":1.0,"Moderate":0.75,"Weak":0.5,"None":0.25}
def adj(R,w): return 3+w*(R-3)
def wv(vec): return np.array([vec[e] for e in ev])
w0=wv(W); Ra=adj(R,w0); la=lvl(Ra)
res["ewts_bands"]={NAMES[k-1]:int((la==k).sum()) for k in range(1,6)}
res["n_reclass"]=int((la!=lr).sum()); res["reclass_ids"]=[i for i,a,b in zip(ids,lr,la) if a!=b]
res["tau_ewts"]=float(kendalltau(R,Ra)[0])
# minimum weight preserving the band: 3+w(R-3) > lower cut of band
lower=np.array([0,1.8,2.6,3.4,4.2])
wmin=np.where(R>3,(lower[lr-1]-3)/(R-3),0.0); wmin=np.clip(np.where(lr==1,0,wmin),0,1)
alts={"default":W,"mild":{"Strong":1,"Moderate":.9,"Weak":.8,"None":.7},"steep":{"Strong":1,"Moderate":.6,"Weak":.3,"None":.1},"linear":{"Strong":1,"Moderate":.8,"Weak":.6,"None":.4},"thesis-tier":{"Strong":1,"Moderate":.75,"Weak":.5,"None":.5}}
res["alt_weights"]={}
for k,v in alts.items():
    a=adj(R,wv(v)); res["alt_weights"][k]={"n_reclass":int((lvl(a)!=lr).sum()),"tau":float(kendalltau(R,a)[0]),"bands":{NAMES[j-1]:int((lvl(a)==j).sum()) for j in range(1,6)}}
# quadrant: evidence-supported high risk
hi=lr>=4; strong=np.array([e in("Strong","Moderate") for e in ev])
quad=np.where(hi&strong,"Act",np.where(hi&~strong,"Verify",np.where(~hi&strong,"Monitor","Defer")))
res["quad"]={q:[i for i,x in zip(ids,quad) if x==q] for q in ["Act","Verify","Monitor","Defer"]}
# Monte Carlo +-1 on each of the six ratings
N=20000
Dp=np.clip(D[None]+rng.integers(-1,2,size=(N,)+D.shape),1,10); Sp=np.clip(S[None]+rng.integers(-1,2,size=(N,)+S.shape),1,5)
Ip,Lp,Rp=comps(Dp,Sp)
stab_band=(lvl(Rp)==lr[None]).mean(0); stab_cell=((lvl(Ip)==li[None])&(lvl(Lp)==ll[None])).mean(0)
res["mc"]={"N":N,"mean_band_stability":float(stab_band.mean()),"min_band_stability":float(stab_band.min()),"mean_cell_stability":float(stab_cell.mean()),"min_cell_stability":float(stab_cell.min())}
rk=np.argsort(np.argsort(-Rp,axis=1),axis=1)
res["mc"]["mean_tau_rank"]=float(np.mean([kendalltau(R,r)[0] for r in Rp[:500]]))
# ewts-adjusted stability: reclass under perturbation
Rap=adj(Rp,w0[None]); res["mc"]["mean_band_stability_ewts"]=float((lvl(Rap)==la[None]).mean())
res["flagged"]=[i for i,x in zip(ids,stab_band) if x<0.75]
res["mu_sens"]={}
for mu in (2.5,3.0,3.5):
    a=mu+w0*(R-mu); res["mu_sens"][str(mu)]=int((lvl(a)!=lr).sum())
res["n_ev"]={k:int(sum(e==k for e in ev)) for k in W}
# alternative split: affected scope A treated as likelihood
n_=nu(D); I2=(n_[:,0]+S)/2; L2=(n_[:,1]+n_[:,2]+n_[:,3]+n_[:,4])/4
res["altsplit_cell_changes"]=int(((lvl(I2)!=li)|(lvl(L2)!=ll)).sum())
# layer summary
lay={}
for k,r_ in enumerate(rows):
    d=lay.setdefault(r_["layer"],{"n":0,"score":0,"w":0,"Act":0,"Verify":0,"Monitor":0,"Defer":0})
    d["n"]+=1; d["score"]+=R[k]; d["w"]+=w0[k]; d[str(quad[k])]+=1
for d in lay.values(): d["score"]/=d["n"]; d["w"]/=d["n"]
res["layers"]=lay
per=[]
for k,i in enumerate(ids):
    per.append(dict(id=i,layer=rows[k]["layer"],asset=rows[k]["asset"],D=int(D[k,0]),R=int(D[k,1]),E=int(D[k,2]),A=int(D[k,3]),D2=int(D[k,4]),S=int(S[k]),ev=ev[k],I=float(I[k]),L=float(L[k]),score=float(R[k]),band=NAMES[lr[k]-1],w=float(w0[k]),adj=float(Ra[k]),adjband=NAMES[la[k]-1],Il=int(li[k]),Ll=int(ll[k]),quad=str(quad[k]),stab=float(stab_band[k]),wmin=float(wmin[k])))
res["per"]=per
json.dump(res,open("results.json","w"),indent=1)
if __name__=="__main__":
    for p in sorted(per,key=lambda x:-x["score"]): print(p["id"],f'I={p["I"]:.2f} L={p["L"]:.2f} R={p["score"]:.2f} {p["band"]} -> {p["adj"]:.2f} {p["adjband"]} {p["ev"]} {p["quad"]} stab={p["stab"]:.2f} wmin={p["wmin"]:.2f} cell=({p["Ll"]},{p["Il"]})')
    print({k:v for k,v in res.items() if k!="per"})
