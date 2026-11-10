#!/usr/bin/env python3
"""Threshold sensitivity of the factor->band rule table over all 3^14 factor vectors. Writes rules_sens.json."""
import json, numpy as np
nu=lambda x:1+4*(np.asarray(x,float)-1)/9
CUT=np.array([1.8,2.6,3.4,4.2]); lvl=lambda v:np.searchsorted(CUT,v,side="left")+1
IEF=["safety","scope","regulatory","cascading","recovery"]; LEF=["exposure","access","maturity","tools","automation"]
VEF=["documentation","interface","complexity","monitoring"]; names=IEF+LEF+VEF; col={n:i for i,n in enumerate(names)}
g=np.indices((3,)*14).reshape(14,-1).T+1; c=lambda n:g[:,col[n]]
nH=sum((c(k)==3).astype(int) for k in IEF); sl=sum(c(k) for k in LEF); sv=sum(c(k) for k in VEF)
def bands(P):
    bD=np.where(nH>=P["nh"],2,np.where(nH>=1,1,0))
    bA=np.minimum(c("scope"),c("cascading"))-1 if P["a"]=="min" else np.maximum(c("scope"),c("cascading"))-1
    bE=np.where((c("exposure")==3)&(c("tools")==3),2,np.where(sl>=P["lef"],1,0))
    bR=np.where((c("automation")==3)&(c("maturity")==3),2,np.where(sl>=P["lef"],1,0))
    bD2=np.where(c("interface")==3,2,np.where(sv>=P["vef"],1,0))
    return dict(D=bD,A=bA,E=bE,R=bR,D2=bD2)
def comp(b,E_):  # E_: edges (Mlo,Hlo) for the 4 ratings and (Mlo2,Hlo2) for D2; rating = band midpoint
    mid=lambda lo,hi:(lo+hi)/2
    def pts(code,Mlo,Hlo): return np.where(code==0,mid(1,Mlo-1),np.where(code==1,mid(Mlo,Hlo-1),mid(Hlo,10)))
    D=pts(b["D"],E_[0],E_[1]);A=pts(b["A"],E_[0],E_[1]);R=pts(b["R"],E_[0],E_[1]);E=pts(b["E"],E_[0],E_[1]);D2=pts(b["D2"],E_[2],E_[3])
    S=4;I=(nu(D)+nu(A)+S)/3;L=(nu(R)+nu(E)+nu(D2))/3;return (I+L)/2,lvl(I),lvl(L)
BASE=dict(nh=3,a="max",lef=8,vef=6); EDG=(5,8,4,7)
b0=bands(BASE); s0,i0,l0=comp(b0,EDG)
var={"D: High if >=2 High factors":dict(BASE,nh=2),"D: High if >=4 High factors":dict(BASE,nh=4),
"A: High only if scope and cascading both High":dict(BASE,a="min"),
"E,R: Medium cut-off 7":dict(BASE,lef=7),"E,R: Medium cut-off 9":dict(BASE,lef=9),
"D2: Medium cut-off 5":dict(BASE,vef=5),"D2: Medium cut-off 7":dict(BASE,vef=7)}
res=[]
f={"safety":3,"scope":3,"regulatory":2,"cascading":3,"recovery":2,"exposure":3,"access":2,"maturity":3,"tools":2,"automation":3,"documentation":2,"interface":2,"complexity":2,"monitoring":2}
ex=np.array([[f[n] for n in names]])
def exbands(P):
    global g,c,nH,sl,sv
    sg,sc_,snH,ssl,ssv=g,c,nH,sl,sv
    g=ex; c=lambda n:g[:,col[n]]; nH=sum((c(k)==3).astype(int) for k in IEF); sl=sum(c(k) for k in LEF); sv=sum(c(k) for k in VEF)
    b=bands(P); r=comp(b,EDG)
    g,c,nH,sl,sv=sg,sc_,snH,ssl,ssv
    return {k:int(v[0]) for k,v in b.items()},int(r[1][0]),int(r[2][0])
eb0=exbands(BASE)
for name,P in var.items():
    b=bands(P); s,i,l=comp(b,EDG)
    ch=np.zeros(len(g),bool)
    for k in b: ch|=b[k]!=b0[k]
    exb=exbands(P)
    res.append(dict(name=name,band_changed=float(ch.mean()),cell_changed=float(((i!=i0)|(l!=l0)).mean()),
        comp_changed=float((lvl(s)!=lvl(s0)).mean()),maxshift=int(np.abs(lvl(s)-lvl(s0)).max()),worst_dscore=float(np.abs(s-s0).max()),
        ex_bands_same=exb[0]==eb0[0],ex_cell_same=exb[1:]==eb0[1:]))
# rating-range edge shifts (rule thresholds fixed, band->rating mapping moves)
for name,E_ in {"High range starts at 7 (D2: 6)":(5,7,4,6),"High range starts at 9 (D2: 8)":(5,9,4,8),"Medium range starts at 4 (D2: 3)":(4,8,3,7),"Medium range starts at 6 (D2: 5)":(6,8,5,7)}.items():
    s,i,l=comp(b0,E_); res.append(dict(name=name,band_changed=0.0,cell_changed=float(((i!=i0)|(l!=l0)).mean()),comp_changed=float((lvl(s)!=lvl(s0)).mean()),maxshift=int(np.abs(lvl(s)-lvl(s0)).max()),worst_dscore=float(np.abs(s-s0).max()),ex_bands_same=True,ex_cell_same=None))
# composite-band distribution under baseline
dist={int(k):float((lvl(s0)==k).mean()) for k in range(1,6)}
# rank stability: Kendall tau of composite score across variants
from scipy.stats import kendalltau
rs=np.random.default_rng(1).choice(len(g),20000,replace=False)
for r,(name,P) in zip(res[:len(var)],var.items()):
    s,_,_=comp(bands(P),EDG); r["tau"]=float(kendalltau(s0[rs],s[rs])[0])
out=dict(res=res,base_dist=dist,n=len(g),ex_base=eb0[0])
json.dump(out,open("rules_sens.json","w"),indent=1)
for r in res: print({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
print(dist)
