#!/usr/bin/env python3
"""Analysis of the 4-LLM rater study.
Usage:  python3 analyze_raters.py responses/            (real data)
        python3 analyze_raters.py --demo                (synthetic data, tests the pipeline)
File names: responses/<model>_<A|B>_run<k>.json   (model in e.g. gemini, claude, gpt, qwen; A = factor scoring, B = direct DREAD)
Needs: numpy, scipy.   Output: rater_results.json and rater_report.md"""
import sys, os, re, json, csv, glob, itertools, collections
import numpy as np
from scipy import stats
IEF=["safety","scope","regulatory","cascading","recovery"]; LEF=["exposure","access","maturity","tools","automation"]; VEF=["documentation","interface","complexity","monitoring"]
FACT=IEF+LEF+VEF
CUT=[1.8,2.6,3.4,4.2]; lvl=lambda v:int(np.searchsorted(CUT,v,side="left")+1)
nu=lambda x:1+4*(x-1)/9
W={"Strong":1.0,"Moderate":0.75,"Weak":0.5,"None":0.25}
CAT=list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"catalogue_ratings.csv"))))
IDS=[r["id"] for r in CAT]
def comps(D,R,E,A,D2,S):
    I=(nu(D)+nu(A)+S)/3; L=(nu(R)+nu(E)+nu(D2))/3; return I,L,(I+L)/2
cat={r["id"]:comps(*[float(r[k]) for k in ("D","R","E","A","D2","S")]) for r in CAT}
# ---- rule engine (Table 2 of the paper) ----
def bands(f):
    nH=sum(f[k]==3 for k in IEF); sl=sum(f[k] for k in LEF); sv=sum(f[k] for k in VEF)
    return dict(D=2 if nH>=3 else (1 if nH>=1 else 0), A=max(f["scope"],f["cascading"])-1,
      E=2 if (f["exposure"]==3 and f["tools"]==3) else (1 if sl>=8 else 0),
      R=2 if (f["automation"]==3 and f["maturity"]==3) else (1 if sl>=8 else 0),
      D2=2 if f["interface"]==3 else (1 if sv>=6 else 0))
MID={"D":(2.5,6,9),"A":(2.5,6,9),"E":(2.5,6,9),"R":(2.5,6,9),"D2":(2,5,8.5)}
def derived_ratings(f):
    b=bands(f); return {k:MID[k][b[k]] for k in b},b
# ---- Krippendorff alpha (ordinal) ----
def alpha_ordinal(M):
    """M: raters x units array of ordinal ints (no missing)."""
    M=np.asarray(M); m,n=M.shape; vals=np.unique(M); idx={v:i for i,v in enumerate(vals)}; k=len(vals)
    o=np.zeros((k,k))
    for u in range(n):
        col=M[:,u]
        for i in range(m):
            for j in range(m):
                if i!=j: o[idx[col[i]],idx[col[j]]]+=1/(m-1)
    nc=o.sum(1); N=nc.sum()
    if N<=1 or k==1: return float("nan")
    cum=np.cumsum(nc); d2=np.zeros((k,k))
    for c in range(k):
        for g in range(k):
            lo,hi=min(c,g),max(c,g); d2[c,g]=(nc[lo:hi+1].sum()-(nc[c]+nc[g])/2)**2
    Do=(o*d2).sum()/N; De=(np.outer(nc,nc)*d2).sum()/(N*(N-1))
    return float(1-Do/De) if De>0 else float("nan")
def kendall_w(S):
    """S: judges x items scores -> Kendall's W with tie correction, chi2 p-value."""
    S=np.asarray(S,float); m,n=S.shape; R=np.array([stats.rankdata(r) for r in S]); Rj=R.sum(0)
    T=sum((t**3-t) for r in S for t in collections.Counter(r).values())
    W=12*((Rj-Rj.mean())**2).sum()/(m**2*(n**3-n)-m*T)
    chi=m*(n-1)*W; p=1-stats.chi2.cdf(chi,n-1); return float(W),float(p)
def wkappa(a,b,k):
    a=np.asarray(a);b=np.asarray(b); O=np.zeros((k,k))
    for x,y in zip(a,b): O[x-1,y-1]+=1
    O/=O.sum(); E=np.outer(O.sum(1),O.sum(0)); Wt=np.array([[(i-j)**2 for j in range(k)] for i in range(k)])/((k-1)**2)
    return float(1-(Wt*O).sum()/(Wt*E).sum()) if (Wt*E).sum()>0 else float("nan")
# ---- loading ----
def load(dirn):
    runs={}
    for fn in sorted(glob.glob(os.path.join(dirn,"*.json"))):
        m=re.match(r"(.+)_([AB])_run(\d+)\.json$",os.path.basename(fn))
        if not m: print("skip (name):",fn); continue
        txt=open(fn).read().strip(); txt=re.sub(r"^```(?:json)?|```$","",txt,flags=re.M).strip()
        try: arr=json.loads(txt)
        except Exception as e: print("BAD JSON",fn,e); continue
        d={x["id"]:x for x in arr}
        miss=[i for i in IDS if i not in d]
        if miss: print("MISSING ids in",fn,miss); continue
        keys=FACT+["S"] if m.group(2)=="A" else ["D","R","E","A","D2","S"]
        rng={**{k:(1,3) for k in FACT},"S":(1,5),**{k:(1,10) for k in ("D","R","E","A","D2")}}
        ok=True
        for i in IDS:
            for k in keys:
                v=d[i].get(k)
                if not isinstance(v,int) or isinstance(v,bool) or not rng[k][0]<=v<=rng[k][1]: print("INVALID",fn,i,k,v); ok=False
        if ok: runs[(m.group(1),m.group(2),int(m.group(3)))]=d
    return runs
def scores_from(d,cond):
    out={}
    for i in IDS:
        x=d[i]
        if cond=="A":
            f={k:x[k] for k in FACT}; r,b=derived_ratings(f); out[i]=comps(r["D"],r["R"],r["E"],r["A"],r["D2"],x["S"])
        else: out[i]=comps(x["D"],x["R"],x["E"],x["A"],x["D2"],x["S"])
    return out
def analyse(runs):
    res={}; models=sorted({k[0] for k in runs})
    for cond in "AB":
        R={k:v for k,v in runs.items() if k[1]==cond}
        if not R: continue
        mods=sorted({k[0] for k in R}); out={"models":mods,"runs":{m:sum(1 for k in R if k[0]==m) for m in mods}}
        sc={k:scores_from(v,cond) for k,v in R.items()}
        # model-level score = mean over its runs
        ms={m:np.array([np.mean([sc[k][i][2] for k in R if k[0]==m]) for i in IDS]) for m in mods}
        mI={m:np.array([np.mean([sc[k][i][0] for k in R if k[0]==m]) for i in IDS]) for m in mods}
        mL={m:np.array([np.mean([sc[k][i][1] for k in R if k[0]==m]) for i in IDS]) for m in mods}
        catS=np.array([cat[i][2] for i in IDS]); catI=np.array([cat[i][0] for i in IDS]); catL=np.array([cat[i][1] for i in IDS])
        # (1) agreement on the inputs: Krippendorff alpha
        keys=FACT+["S"] if cond=="A" else ["D","R","E","A","D2","S"]
        al={}
        for k in keys:
            allruns=np.array([[R[r][i][k] for i in IDS] for r in sorted(R)])
            medm=np.array([[int(np.round(np.median([R[r][i][k] for r in R if r[0]==m]))) for i in IDS] for m in mods])
            al[k]={"all_runs":alpha_ordinal(allruns),"model_medians":alpha_ordinal(medm)}
        out["alpha_items"]=al
        if cond=="A":
            groups={"IEF":IEF,"LEF":LEF,"VEF":VEF,"all14":FACT}
            for gname,gk in groups.items():
                M=np.array([[R[r][i][k] for i in IDS for k in gk] for r in sorted(R)])
                Mm=np.array([[int(np.round(np.median([R[r][i][k] for r in R if r[0]==m]))) for i in IDS for k in gk] for m in mods])
                al["group_"+gname]={"all_runs":alpha_ordinal(M),"model_medians":alpha_ordinal(Mm)}
            # derived rating bands
            bd={}
            for rt in ("D","A","R","E","D2"):
                M=np.array([[bands({k:R[r][i][k] for k in FACT})[rt] for i in IDS] for r in sorted(R)]); bd[rt]=alpha_ordinal(M)
            out["alpha_derived_bands"]=bd
        # (2) agreement on the output: Kendall W across models, pairwise tau
        if len(mods)>=2:
            out["kendall_w_models"]=dict(zip(("W","p"),kendall_w(np.array([ms[m] for m in mods]))))
            out["pairwise_tau"]={f"{a}-{b}":float(stats.kendalltau(ms[a],ms[b])[0]) for a,b in itertools.combinations(mods,2)}
        # (2b) cross-model cell/band agreement and within-model run stability
        if len(mods)>=2:
            lv=lambda arr:[lvl(x) for x in arr]
            cells={m:list(zip(lv(mL[m]),lv(mI[m]))) for m in mods}; bds={m:lv(ms[m]) for m in mods}
            out["cross_model"]={"cell_all_agree":float(np.mean([len({cells[m][j] for m in mods})==1 for j in range(len(IDS))])),
              "cell_pairwise":{f"{x}-{y}":float(np.mean([p==q for p,q in zip(cells[x],cells[y])])) for x,y in itertools.combinations(mods,2)},
              "band_all_agree":float(np.mean([len({bds[m][j] for m in mods})==1 for j in range(len(IDS))])),
              "cell_within1_all":float(np.mean([all(max(abs(cells[x][j][0]-cells[y][j][0]),abs(cells[x][j][1]-cells[y][j][1]))<=1 for x,y in itertools.combinations(mods,2)) for j in range(len(IDS))]))}
        if cond=="A":
            out["alpha_within_model"]={m:alpha_ordinal(np.array([[R[r][i][k] for i in IDS for k in FACT] for r in sorted(R) if r[0]==m])) for m in mods}
        # (3) agreement with the catalogue
        agree={}
        for m in mods:
            lv=lambda arr:[lvl(x) for x in arr]
            cellm=list(zip(lv(mL[m]),lv(mI[m]))); cellc=list(zip(lv(catL),lv(catI)))
            agree[m]={"tau":float(stats.kendalltau(ms[m],catS)[0]),"rho":float(stats.spearmanr(ms[m],catS)[0]),
              "cell_exact":float(np.mean([a==b for a,b in zip(cellm,cellc)])),"cell_within1":float(np.mean([max(abs(a[0]-b[0]),abs(a[1]-b[1]))<=1 for a,b in zip(cellm,cellc)])),
              "band_exact":float(np.mean([a==b for a,b in zip(lv(ms[m]),lv(catS))])),"band_wkappa":wkappa(lv(ms[m]),lv(catS),5),
              "mean_bias":float(np.mean(ms[m]-catS))}
        out["vs_catalogue"]=agree
        ens=np.mean([ms[m] for m in mods],0)
        out["ensemble_vs_catalogue"]={"tau":float(stats.kendalltau(ens,catS)[0]),"rho":float(stats.spearmanr(ens,catS)[0])}
        # (4) the EWTS premise: does model disagreement fall with evidence weight?
        w=np.array([W[r["evidence"]] for r in CAT]); sd=np.std([ms[m] for m in mods],0,ddof=1) if len(mods)>1 else np.zeros(len(IDS))
        gap=np.abs(ens-catS)
        out["premise"]={"between_model_sd_vs_w":dict(zip(("rho","p"),map(float,stats.spearmanr(w,sd)))),"gap_to_catalogue_vs_w":dict(zip(("rho","p"),map(float,stats.spearmanr(w,gap)))),
                        "median_sd_strong_moderate":float(np.median(sd[w>=0.75])),"median_sd_weak_none":float(np.median(sd[w<0.75]))}
        out["per_asset"]={i:{"ens":float(ens[j]),"cat":float(catS[j]),"sd":float(sd[j]),"w":float(w[j])} for j,i in enumerate(IDS)}
        res[cond]=out
    if "A" in res and "B" in res:
        def ens(c): return np.mean([[res[c]["per_asset"][i]["ens"]] for i in IDS],1).ravel()
        res["A_vs_B_tau"]=float(stats.kendalltau(ens("A"),ens("B"))[0])
    return res
def report(res):
    L=["# Rater-study results (auto-generated)\n"]
    for c,name in (("A","Condition A: evidence-factor scoring -> rule engine"),("B","Condition B: direct DREAD ratings (control)")):
        if c not in res: continue
        o=res[c]; L.append(f"## {name}\nModels: {', '.join(o['models'])}; runs per model: {o['runs']}\n")
        if c=="A":
            L.append("### Krippendorff alpha (ordinal) on the evidence factors\n\n| group | all runs | model medians |\n|---|---|---|")
            for g in ("IEF","LEF","VEF","all14"): v=o["alpha_items"]["group_"+g]; L.append(f"| {g} | {v['all_runs']:.2f} | {v['model_medians']:.2f} |")
            L.append("\n| factor | all runs | model medians |\n|---|---|---|")
            for k in FACT+["S"]: v=o["alpha_items"][k]; L.append(f"| {k} | {v['all_runs']:.2f} | {v['model_medians']:.2f} |")
            L.append("\nAlpha on derived rating bands: "+", ".join(f"{k} {v:.2f}" for k,v in o["alpha_derived_bands"].items())+"\n")
        else:
            L.append("### Krippendorff alpha (ordinal) on the ratings\n\n| rating | all runs | model medians |\n|---|---|---|")
            for k in ("D","R","E","A","D2","S"): v=o["alpha_items"][k]; L.append(f"| {k} | {v['all_runs']:.2f} | {v['model_medians']:.2f} |")
        if "kendall_w_models" in o:
            L.append(f"\nKendall's W across models (DREAD-S rank): W={o['kendall_w_models']['W']:.2f}, p={o['kendall_w_models']['p']:.3g}\n")
            L.append("Pairwise Kendall tau: "+", ".join(f"{k} {v:.2f}" for k,v in o["pairwise_tau"].items())+"\n")
        L.append("### Agreement with the catalogue\n\n| model | tau | rho | cell exact | cell within 1 | band exact | band weighted kappa | mean bias |\n|---|---|---|---|---|---|---|---|")
        for m,v in o["vs_catalogue"].items(): L.append(f"| {m} | {v['tau']:.2f} | {v['rho']:.2f} | {v['cell_exact']:.2f} | {v['cell_within1']:.2f} | {v['band_exact']:.2f} | {v['band_wkappa']:.2f} | {v['mean_bias']:+.2f} |")
        e=o["ensemble_vs_catalogue"]; L.append(f"\nEnsemble mean vs catalogue: tau={e['tau']:.2f}, rho={e['rho']:.2f}\n")
        if "cross_model" in o:
            c=o["cross_model"]; L.append(f"Cross-model: all models in the same cell for {c['cell_all_agree']:.2f} of assets; same band {c['band_all_agree']:.2f}; all pairs within one level {c['cell_within1_all']:.2f}.\n")
        if "alpha_within_model" in o: L.append("Within-model run stability (alpha over the 14 factors): "+", ".join(f"{k} {v:.2f}" for k,v in o["alpha_within_model"].items())+"\n")
        p=o["premise"]; L.append(f"### EWTS premise (does disagreement fall with evidence weight?)\nBetween-model SD vs w: rho={p['between_model_sd_vs_w']['rho']:.2f}, p={p['between_model_sd_vs_w']['p']:.3f}. Gap to catalogue vs w: rho={p['gap_to_catalogue_vs_w']['rho']:.2f}, p={p['gap_to_catalogue_vs_w']['p']:.3f}. Median SD Strong/Moderate {p['median_sd_strong_moderate']:.3f} vs Weak/None {p['median_sd_weak_none']:.3f}.\n")
    if "A_vs_B_tau" in res: L.append(f"Rank agreement between condition A and B ensembles: tau={res['A_vs_B_tau']:.2f}\n")
    return "\n".join(L)
def demo(dirn):
    os.makedirs(dirn,exist_ok=True); rng=np.random.default_rng(7)
    for m,bias in (("gemini",0),("claude",0),("gpt",1),("qwen",-1)):
        for run in (1,2,3):
            A=[];B=[]
            for r in CAT:
                base=rng.integers(1,4,14); f={k:int(np.clip(base[j]+rng.integers(-1,2),1,3)) for j,k in enumerate(FACT)}
                A.append({"id":r["id"],**f,"S":int(np.clip(int(r["S"])+rng.integers(-1,2),1,5)),"why":"demo"})
                B.append({"id":r["id"],**{k:int(np.clip(int(r[k])+rng.integers(-1,2)+bias,1,10)) for k in ("D","R","E","A","D2")},"S":int(np.clip(int(r["S"])+rng.integers(-1,2),1,5)),"why":"demo"})
            json.dump(A,open(f"{dirn}/{m}_A_run{run}.json","w")); json.dump(B,open(f"{dirn}/{m}_B_run{run}.json","w"))
if __name__=="__main__":
    here=os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv)>1 and sys.argv[1]=="--demo":
        d=os.path.join(here,"_demo_responses"); demo(d)
    else: d=sys.argv[1] if len(sys.argv)>1 else os.path.join(here,"responses")
    runs=load(d); print(len(runs),"valid response files")
    res=analyse(runs); json.dump(res,open(os.path.join(here,"rater_results.json"),"w"),indent=1)
    open(os.path.join(here,"rater_report.md"),"w").write(report(res)); print(report(res)[:3500])
