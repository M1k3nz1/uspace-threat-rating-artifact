#!/usr/bin/env python3
"""Validation analyses for the paper. (1) exhaustive verification of Props 1-3 over the full rating domain,
(2) independent-rater check of the EWTS premise: is weaker evidence associated with more rater disagreement?"""
import csv, json, itertools
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
rng=np.random.default_rng(20270116)
CUT=np.array([1.8,2.6,3.4,4.2]); nu=lambda x:1+4*(np.asarray(x,float)-1)/9
lvl=lambda v: np.searchsorted(CUT,v,side="left")+1
out={}
# ---- (1) exhaustive verification: all 10^5 DREAD vectors x 5 S values
g=np.arange(1,11); G=np.array(np.meshgrid(g,g,g,g,g,indexing="ij")).reshape(5,-1).T   # D,R,E,A,D2
n=nu(G); N=G.shape[0]*5
bad_id=0; bad_mono=0; bad_wstar=0; bad_ord=0; total=0
Is=[];Ls=[];Rs=[]
for S in range(1,6):
    I=(n[:,0]+n[:,3]+S)/3; L=(n[:,1]+n[:,2]+n[:,4])/3
    R=(n.sum(1)+S)/6
    bad_id+=int((np.abs(R-(I+L)/2)>1e-12).sum())
    Is.append(I);Ls.append(L);Rs.append(R)
Rall=np.concatenate(Rs)
# monotonicity: raising any single rating by 1 strictly raises the score (check per dimension, S fixed 3)
for d in range(5):
    m=G[:,d]<10; G2=G[m].copy(); G2[:,d]+=1
    r1=(nu(G[m]).sum(1)+3)/6; r2=(nu(G2).sum(1)+3)/6
    bad_mono+=int((r2<=r1).sum())
for S in range(1,5):
    bad_mono+=int((((n.sum(1)+S+1)/6)<=((n.sum(1)+S)/6)).sum())
# band preservation threshold: for each score r>3 and each w on a grid, band kept iff w>w*
lowerEdge=np.array([0,1.8,2.6,3.4,4.2]); ws=np.linspace(.05,1,96)
Rsub=Rall[Rall>3]
for w in ws:
    adj=3+w*(Rsub-3); kept=lvl(adj)==lvl(Rsub)
    tau=lowerEdge[lvl(Rsub)-1]
    wstar=np.where(tau>3,(tau-3)/(Rsub-3),0.0)
    pred=np.where(tau>3,w>wstar,True)
    # the closed form claims preservation iff w>w*; check equality
    near=np.abs(w-wstar)<1e-9
    bad_wstar+=int(((kept!=pred)&~near).sum()); near_ct=globals().get('near_ct',0)+int(((kept!=pred)&near).sum()); globals()['near_ct']=near_ct
    bad_ord+=0
out["exh"]={"vectors":int(G.shape[0]*5),"identity_violations":bad_id,"monotonicity_violations":bad_mono,"wstar_checks":int(len(Rsub)*len(ws)),"wstar_violations":bad_wstar,"wstar_float_ties":int(globals().get("near_ct",0))}
# ---- (2) independent-rater check
cat={r["id"]:r for r in csv.DictReader(open("data/ratings.csv"))}
W={"Strong":1.0,"Moderate":.75,"Weak":.5,"None":.25}
rows=list(csv.DictReader(open("data/llm/ratings_all_runs.csv")))
ids=list(cat.keys()); models=sorted({r["model"] for r in rows})
def ds(r): return (sum(nu(int(r[k])) for k in("D","R","E","A","D2"))+int(r["S"]))/6
sc={i:{m:[] for m in models} for i in ids}
for r in rows: sc[r["id"]][r["model"]].append(ds(r))
mm=np.array([[np.mean(sc[i][m]) for m in models] for i in ids])          # asset x model mean
between=mm.std(axis=1,ddof=1)                                           # disagreement between models
within=np.array([np.mean([np.std(sc[i][m],ddof=1) for m in models]) for i in ids])
allsd=np.array([np.std(sum((sc[i][m] for m in models),[]),ddof=1) for i in ids])
pub=np.array([ds(cat[i]) for i in ids]); lmean=mm.mean(1)
w=np.array([W[cat[i]["evidence"]] for i in ids])
gap=np.abs(lmean-pub)
def perm(x,y,B=20000):
    obs=spearmanr(x,y)[0]; c=0
    for _ in range(B):
        if abs(spearmanr(x,rng.permutation(y))[0])>=abs(obs): c+=1
    return float(obs),(c+1)/(B+1)
res={}
for name,v in [("between_model_sd",between),("all_run_sd",allsd),("within_model_sd",within),("gap_to_catalogue",gap)]:
    rho,p=perm(w,v); res[name]={"rho":rho,"p":p,"mean":float(v.mean())}
hi=np.isin([cat[i]["evidence"] for i in ids],["Strong","Moderate"])
res["group"]={"strong_mod_n":int(hi.sum()),"weak_none_n":int((~hi).sum()),
 "between_med_strong_mod":float(np.median(between[hi])),"between_med_weak_none":float(np.median(between[~hi])),
 "gap_med_strong_mod":float(np.median(gap[hi])),"gap_med_weak_none":float(np.median(gap[~hi])),
 "mw_p_between":float(mannwhitneyu(between[hi],between[~hi],alternative="less")[1])}
# confound: score level vs dispersion
res["rho_score_vs_between"]=float(spearmanr(pub,between)[0])
# partial check: residual of between-sd after regressing on score level
A=np.c_[np.ones(len(pub)),pub]; beta=np.linalg.lstsq(A,between,rcond=None)[0]; resid=between-A@beta
res["partial_rho_between"]=float(spearmanr(w,resid)[0])
res["per_asset"]={i:{"between":float(b),"gap":float(g_),"w":float(x)} for i,b,g_,x in zip(ids,between,gap,w)}
out["rater"]=res; out["n_runs"]=len(rows); out["n_models"]=len(models)
json.dump(out,open("validation.json","w"),indent=1)
print(json.dumps({k:v for k,v in out.items()},indent=1)[:2600])
