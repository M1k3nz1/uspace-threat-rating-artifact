#!/usr/bin/env python3
"""Condition C: SecRAM-native assessment by LLM raters, compared with the framework's SecRAM risk levels.
Usage:  python3 analyze_secram_native.py responses_C/        (real data)
        python3 analyze_secram_native.py --demo              (synthetic data, tests the pipeline)
File names: responses_C/<model>_C_run<k>.json  (model: claude, gpt, gemini)
Needs: numpy, scipy.  Output: secram_native.json and secram_native_report.md"""
import sys, os, re, json, glob, collections
import numpy as np
from scipy import stats
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,".."))
import analyze_raters as ar
from secram import risk, CLS
AREAS=["people","capacity","performance","economic","branding","regulatory","environment"]
IDS=ar.IDS; NAMES=["Low","Medium","High"]
def lam(v): return ar.lvl(v)
def load(dirn):
    runs={}
    for fn in sorted(glob.glob(os.path.join(dirn,"*.json"))):
        m=re.match(r"(.+)_C_run(\d+)\.json$",os.path.basename(fn))
        if not m: print("skip (name):",fn); continue
        txt=open(fn).read().strip(); txt=re.sub(r"^```(?:json)?|```$","",txt,flags=re.M).strip()
        txt=txt.replace("“",'"').replace("”",'"').replace("’","'")
        try: arr=json.loads(txt)
        except Exception as e: print("BAD JSON",fn,e); continue
        d={x["id"]:x for x in arr}
        if any(i not in d for i in IDS): print("MISSING ids in",fn,[i for i in IDS if i not in d]); continue
        bad=[(i,k) for i in IDS for k in AREAS+["L"] if not (isinstance(d[i].get(k),int) and 1<=d[i][k]<=5)]
        if bad: print("OUT OF RANGE in",fn,bad[:5]); continue
        runs[(m.group(1),int(m.group(2)))]=d
    return runs
def demo(dirn):
    rng=np.random.default_rng(7); os.makedirs(dirn,exist_ok=True)
    for m in ("claude","gpt","gemini"):
        for k in (1,2,3):
            arr=[]
            for i in IDS:
                I,L,_=ar.cat[i]; base=max(1,min(5,round(I))); l=max(1,min(5,round(L+rng.normal(0,.6))))
                a={x:int(max(1,min(5,base+rng.integers(-1,2)-(x in("branding","environment"))))) for x in AREAS}
                arr.append({"id":i,**a,"L":int(l),"why":"demo"})
            json.dump(arr,open(os.path.join(dirn,f"{m}_C_run{k}.json"),"w"))
def impact(x): return max(x[a] for a in AREAS)
def main(dirn):
    runs=load(dirn)
    if not runs: print("no valid files"); return
    keys=sorted(runs); mods=sorted({k[0] for k in keys}); res={"files":len(keys),"models":mods}
    # per-run native cell and risk
    nat={k:{i:(runs[k][i]["L"],impact(runs[k][i])) for i in IDS} for k in keys}
    cls={k:[CLS[risk(*nat[k][i])] for i in IDS] for k in keys}
    M=np.array([cls[k] for k in keys]); Lm=np.array([[runs[k][i]["L"] for i in IDS] for k in keys]); Im=np.array([[nat[k][i][1] for i in IDS] for k in keys])
    res["alpha"]={"risk_level":ar.alpha_ordinal(M),"likelihood":ar.alpha_ordinal(Lm),"impact_max":ar.alpha_ordinal(Im)}
    res["alpha"]["areas"]={a:ar.alpha_ordinal(np.array([[runs[k][i][a] for i in IDS] for k in keys])) for a in AREAS}
    res["all_runs_same_risk"]=float(np.mean([len(set(M[:,j]))==1 for j in range(M.shape[1])]))
    # model medians
    mm=np.array([[int(np.round(np.median([cls[k][j] for k in keys if k[0]==m]))) for j in range(len(IDS))] for m in mods])
    res["models_same_risk"]=float(np.mean([len(set(mm[:,j]))==1 for j in range(mm.shape[1])]))
    res["alpha_models_risk"]=ar.alpha_ordinal(mm)
    res["dist"]={m:dict(collections.Counter(NAMES[x] for x in mm[n])) for n,m in enumerate(mods)}
    # cell agreement among models
    cellmed={m:[ (int(np.round(np.median([nat[k][i][0] for k in keys if k[0]==m]))), int(np.round(np.median([nat[k][i][1] for k in keys if k[0]==m])))) for i in IDS] for m in mods}
    res["models_same_cell"]=float(np.mean([len({cellmed[m][j] for m in mods})==1 for j in range(len(IDS))]))
    # driver of max impact
    drv=collections.Counter()
    for k in keys:
        for i in IDS:
            mx=impact(runs[k][i]); [drv.update([a]) for a in AREAS if runs[k][i][a]==mx]
    res["impact_driver_share"]={a:drv[a]/(len(keys)*len(IDS)) for a in AREAS}
    # reference: catalogue-derived (default mapping) and framework-derived from condition A runs
    catcls=[CLS[risk(lam(ar.cat[i][1]),lam(ar.cat[i][0]))] for i in IDS]; res["catalogue_dist"]=dict(collections.Counter(NAMES[x] for x in catcls))
    res["vs_catalogue_same"]={m:float(np.mean(mm[n]==np.array(catcls))) for n,m in enumerate(mods)}
    res["vs_catalogue_within1"]={m:float(np.mean(abs(mm[n]-np.array(catcls))<=1)) for n,m in enumerate(mods)}
    res["vs_catalogue_kappa_w"]={m:ar.wkappa(mm[n]+1,np.array(catcls)+1,3) for n,m in enumerate(mods)}
    conf=np.zeros((3,3),int)
    for n in range(len(mods)):
        for a,b in zip(catcls,mm[n]): conf[a,b]+=1
    res["confusion_catalogue_rows_native_cols"]=conf.tolist()
    # framework-derived from condition A, same model, same run-median
    aruns=ar.load(os.path.join(HERE,"responses")) if os.path.isdir(os.path.join(HERE,"responses")) else {}
    fw={}
    for m in mods:
        ks=[k for k in aruns if k[0]==m and k[1]=="A"]
        if not ks: continue
        c=[[CLS[risk(lam(ar.scores_from(aruns[k],"A")[i][1]),lam(ar.scores_from(aruns[k],"A")[i][0]))] for i in IDS] for k in ks]
        fw[m]=[int(np.round(np.median([c[r][j] for r in range(len(ks))]))) for j in range(len(IDS))]
    res["same_model_framework_vs_native_same_risk"]={m:float(np.mean(np.array(fw[m])==mm[mods.index(m)])) for m in fw}
    res["same_model_framework_dist"]={m:dict(collections.Counter(NAMES[x] for x in fw[m])) for m in fw}
    # ranking: native composite vs catalogue DREAD-S and vs framework ensemble
    comp=np.array([[ (nat[k][i][0]+nat[k][i][1])/2 for i in IDS] for k in keys]).mean(0)
    catS=np.array([ar.cat[i][2] for i in IDS]); tau,p=stats.kendalltau(comp,catS); rho,pr=stats.spearmanr(comp,catS)
    res["ensemble_vs_catalogue"]={"tau":float(tau),"rho":float(rho)}
    # per-asset table
    res["assets"]=[{"id":i,"catalogue":NAMES[catcls[j]],"native_models":{m:NAMES[mm[n][j]] for n,m in enumerate(mods)},"framework_models":{m:NAMES[fw[m][j]] for m in fw},"mean_L":float(Lm[:,j].mean()),"mean_impact":float(Im[:,j].mean())} for j,i in enumerate(IDS)]

    # ---- route comparison: framework route (condition A) vs SecRAM-native route (condition C), same models and runs ----
    rc={}
    if aruns:
        ak=sorted(k for k in aruns if k[1]=="A" and k[0] in mods)
        Asc={k:ar.scores_from(aruns[k],"A") for k in ak}
        Arisk=np.array([[CLS[risk(lam(Asc[k][i][1]),lam(Asc[k][i][0]))] for i in IDS] for k in ak])
        AL=np.array([[lam(Asc[k][i][1]) for i in IDS] for k in ak]); AI=np.array([[lam(Asc[k][i][0]) for i in IDS] for k in ak])
        rc["alpha_framework"]={"risk":ar.alpha_ordinal(Arisk),"likelihood":ar.alpha_ordinal(AL),"impact":ar.alpha_ordinal(AI)}
        rc["alpha_native"]={"risk":res["alpha"]["risk_level"],"likelihood":res["alpha"]["likelihood"],"impact":res["alpha"]["impact_max"]}
        # within model
        rc["within_model_alpha"]={m:{"framework":ar.alpha_ordinal(Arisk[[n for n,k in enumerate(ak) if k[0]==m]]),"native":ar.alpha_ordinal(M[[n for n,k in enumerate(keys) if k[0]==m]])} for m in mods}
        # pairwise model agreement on risk (run medians)
        fmm=np.array([fw[m] for m in mods]); import itertools
        rc["pair_same_risk"]={"framework":float(np.mean([np.mean(fmm[a]==fmm[b]) for a,b in itertools.combinations(range(len(mods)),2)])),"native":float(np.mean([np.mean(mm[a]==mm[b]) for a,b in itertools.combinations(range(len(mods)),2)]))}
        rc["models_same_risk_framework"]=float(np.mean([len(set(fmm[:,j]))==1 for j in range(fmm.shape[1])]))
        rc["all_runs_same_risk_framework"]=float(np.mean([len(set(Arisk[:,j]))==1 for j in range(Arisk.shape[1])]))
        # paired bootstrap over assets of alpha(framework) - alpha(native) on risk
        rng=np.random.default_rng(2027); d=[]
        for _ in range(1000):
            ix=rng.integers(0,len(IDS),len(IDS)); a1=ar.alpha_ordinal(Arisk[:,ix]); a2=ar.alpha_ordinal(M[:,ix])
            if np.isfinite(a1) and np.isfinite(a2): d.append(a1-a2)
        rc["alpha_diff_risk_ci"]=[float(np.percentile(d,2.5)),float(np.percentile(d,97.5)),float(np.mean(np.array(d)>0))]
        # impact aggregation: native mean-over-areas vs max
        Imean=np.array([[np.mean([runs[k][i][a] for a in AREAS]) for i in IDS] for k in keys])
        rc["native_mean_impact_alpha"]=ar.alpha_ordinal(np.rint(Imean).astype(int))
        # people rating alone vs framework safety
    res["route_comparison"]=rc
    # per-model likelihood and impact distribution
    res["native_mean_by_model"]={m:{"L":float(np.mean([[runs[k][i]["L"] for i in IDS] for k in keys if k[0]==m])),"impact_max":float(np.mean([[impact(runs[k][i]) for i in IDS] for k in keys if k[0]==m]))} for m in mods}
    res["native_cat_corr"]={"L_vs_catL":float(stats.spearmanr(Lm.mean(0),[ar.cat[i][1] for i in IDS])[0]),"Imax_vs_catI":float(stats.spearmanr(Im.mean(0),[ar.cat[i][0] for i in IDS])[0])}
    json.dump(res,open("secram_native.json","w"),indent=1)
    f=lambda x:f"{x:.2f}"
    L=["# Condition C: SecRAM-native assessment","",f"Files: {len(keys)}; models: {', '.join(mods)}","",
     "## Agreement among raters (Krippendorff alpha, ordinal)",f"- Risk level (Low/Medium/High): {f(res['alpha']['risk_level'])}",f"- SecRAM likelihood L: {f(res['alpha']['likelihood'])}",f"- SecRAM impact (max over 7 areas): {f(res['alpha']['impact_max'])}",
     "- Impact areas: "+", ".join(f"{a} {f(v)}" for a,v in res['alpha']['areas'].items()),
     f"- Model medians give the same risk level for {res['models_same_risk']:.0%} of assets; all runs for {res['all_runs_same_risk']:.0%}; same cell for {res['models_same_cell']:.0%}",
     "","## Risk-level distribution (model medians)"]+[f"- {m}: {d}" for m,d in res['dist'].items()]+[f"- catalogue-derived (framework, default mapping): {res['catalogue_dist']}","",
     "## Native vs framework","- Native vs catalogue-derived level, same level: "+", ".join(f"{m} {v:.0%}" for m,v in res['vs_catalogue_same'].items()),
     "- within one level: "+", ".join(f"{m} {v:.0%}" for m,v in res['vs_catalogue_within1'].items()),
     "- weighted kappa: "+", ".join(f"{m} {f(v)}" for m,v in res['vs_catalogue_kappa_w'].items()),
     "- Same model, framework route (condition A) vs native route, same level: "+", ".join(f"{m} {v:.0%}" for m,v in res['same_model_framework_vs_native_same_risk'].items()),
     f"- Native composite vs catalogue DREAD-S ranking: tau {f(res['ensemble_vs_catalogue']['tau'])}, rho {f(res['ensemble_vs_catalogue']['rho'])}",
     "- Which area sets the maximum impact (share of run-asset pairs): "+", ".join(f"{a} {v:.0%}" for a,v in res['impact_driver_share'].items()),
     "","## Route comparison (framework route A vs SecRAM-native route C)",json.dumps(res["route_comparison"],indent=1),json.dumps(res["native_mean_by_model"]),json.dumps(res["native_cat_corr"]),
     "","Confusion (rows catalogue-derived Low/Medium/High, columns native, pooled over models):",str(res['confusion_catalogue_rows_native_cols'])]
    open("secram_native_report.md","w").write("\n".join(L)); print("\n".join(L))
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--demo":
        demo("responses_C_demo"); main("responses_C_demo")
    else: main(sys.argv[1] if len(sys.argv)>1 else "responses_C")
