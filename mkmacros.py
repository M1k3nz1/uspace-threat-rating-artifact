import json
R=json.load(open("results.json")); P=R["per"]; A=R["alt_weights"]; M=R["mc"]
f=lambda x,n=2:f"{x:.{n}f}"
m={"nAssets":len(P),"idDiff":"10^{-15}","nCells":R["n_cells"],"tauAddProd":f(R["tau_add_vs_prod"]),"tauDread":f(R["tau_dread_vs_dreads"]),
"topOverlap":R["top5_overlap"],"nReclass":R["n_reclass"],"tauEwts":f(R["tau_ewts"]),
"nCrit":R["bands"]["Critical"],"nHigh":R["bands"]["High"],"nMed":R["bands"]["Medium"],
"nHighAdj":R["ewts_bands"]["High"],"nMedAdj":R["ewts_bands"]["Medium"],
"nAct":len(R["quad"]["Act"]),"nVerify":len(R["quad"]["Verify"]),"nMonitor":len(R["quad"]["Monitor"]),"nDefer":len(R["quad"]["Defer"]),
"mcN":f'{M["N"]:,}'.replace(",","{,}"),"mcMean":f(M["mean_band_stability"]),"mcMin":f(M["min_band_stability"]),"mcCellMean":f(M["mean_cell_stability"]),"mcCellMin":f(M["min_cell_stability"]),
"mcTau":f(M["mean_tau_rank"]),"mcMeanEwts":f(M["mean_band_stability_ewts"]),"nFlag":len(R["flagged"]),
"rcMild":A["mild"]["n_reclass"],"rcLinear":A["linear"]["n_reclass"],"rcTier":A["thesis-tier"]["n_reclass"],"rcSteep":A["steep"]["n_reclass"],
"tauMild":f(A["mild"]["tau"]),"tauSteep":f(A["steep"]["tau"]),"muLow":R["mu_sens"]["2.5"],"muHigh":R["mu_sens"]["3.5"],
"nStrong":R["n_ev"]["Strong"],"nModerate":R["n_ev"]["Moderate"],"nWeak":R["n_ev"]["Weak"],"nNone":R["n_ev"]["None"],
"altSplit":R["altsplit_cell_changes"],"scoreMin":f(R["dreads_range"][0]),"scoreMax":f(R["dreads_range"][1])}
Vd=json.load(open("validation.json")); ra=Vd["rater"]; ex=Vd["exh"]
m.update({"exhVec":f'{ex["vectors"]:,}'.replace(",","{,}"),"exhTies":f'{ex["wstar_float_ties"]:,}'.replace(",","{,}"),"exhChecks":f'{ex["wstar_checks"]:,}'.replace(",","{,}"),
"rhoBetween":f(ra["between_model_sd"]["rho"]),"pBetween":f(ra["between_model_sd"]["p"]),"rhoGap":f(ra["gap_to_catalogue"]["rho"]),"pGap":f(ra["gap_to_catalogue"]["p"]),
"rhoWithin":f(ra["within_model_sd"]["rho"]),"pWithin":f(ra["within_model_sd"]["p"]),
"medBetHi":f(ra["group"]["between_med_strong_mod"]),"medBetLo":f(ra["group"]["between_med_weak_none"]),"medGapHi":f(ra["group"]["gap_med_strong_mod"]),"medGapLo":f(ra["group"]["gap_med_weak_none"]),
"rhoScoreBet":f(ra["rho_score_vs_between"]),"rhoPartial":f(ra["partial_rho_between"]),"nRatings":Vd["n_runs"],"nRaterRuns":21,"nRaterModels":Vd["n_models"],"nGroupHi":ra["group"]["strong_mod_n"],"nGroupLo":ra["group"]["weak_none_n"]})
Fw=json.load(open("framework.json")); E=Fw["example"]
m.update({"exSum":E["sum"],"exI":f(E["I"]),"exL":f(E["L"]),"exR":f(E["dreads"]),"exIzero":f(E["I0"]),"exAdjThree":f(E["adj"]["0.75"]),"exAdjHalf":f(E["adj"]["0.5"]),"exWstar":f(E["wstar"]),
"boxN":E["box"]["n"],"boxSame":E["box"]["same_cell"],"boxHigh":E["box"]["bands"]["4"],"boxCrit":E["box"]["bands"]["5"],
"ruleChecks":f'{Fw["exh"]["rule_checked"]:,}'.replace(",","{,}"),"factorVecs":f'{Fw["exh"]["factor_vectors"]:,}'.replace(",","{,}"),
"slideCellChg":len(Fw["slide_variant_cell_changes"]),"slideBandChg":Fw["slide_variant_band_changes"],"cellMoves":len(Fw["ewts_cell_moves"]),"multReclass":Fw["mult_reclass"]})
open("numbers.tex","w").write("".join("\\newcommand{\\%s}{%s}\n"%(k,v) for k,v in m.items()))
rows=[]
CAT={c["id"]:c for c in Fw["cat"]}
for p in P: c=CAT[p["id"]]; p["cell"]=(f'{c["lL"]}{c["lI"]}' if (c["lL"],c["lI"])==(c["lLa"],c["lIa"]) else f'{c["lL"]}{c["lI"]}$\\to${c["lLa"]}{c["lIa"]}')
for p in sorted(P,key=lambda p:-p["score"]):
    rows.append(f'{p["id"]} & {p["D"]}/{p["R"]}/{p["E"]}/{p["A"]}/{p["D2"]}/{p["S"]} & {p["I"]:.2f} & {p["L"]:.2f} & {p["score"]:.2f} & {p["band"]} & {p["cell"]} & {p["ev"]} & {p["w"]:.2f} & {p["adj"]:.2f} & {p["adjband"]}{"$^\\dagger$" if p["band"]!=p["adjband"] else ""} & {p["quad"]} & {p["stab"]:.2f} \\\\')
open("apptable.tex","w").write("\n".join(r.rstrip("\\").rstrip() if i==len(rows)-1 else r for i,r in enumerate(rows))+"%\n")
print(open("numbers.tex").read())

lt=[]
for k in ["Governance","Service","Data","Infrastructure"]:
    d=R["layers"][k]; lt.append(f'{k} & {d["n"]} & {d["score"]:.2f} & {d["w"]:.2f} & {d["Act"]} & {d["Verify"]} & {d["Monitor"]} & {d["Defer"]} \\\\')
lt[-1]=lt[-1].rstrip("\\").rstrip()
open("layertable.tex","w").write("\n".join(lt)+"%\n")
print(R["layers"])

uc=[("INF-02","Start treatment planning; confirm with SecRAM tables"),("INF-01","Start treatment planning"),("SVC-04","Gather or reproduce evidence first; re-score"),("DAT-05","Gather evidence; band is borderline after discount"),("INF-04","Keep in register; revisit on architectural change")]
pm={p["id"]:p for p in P}; ur=[]
for i,a in uc:
    p=pm[i]; c=CAT[i]
    cell=lambda l,k:f"({l},{k})"
    ur.append(f'{i} & {cell(c["lL"],c["lI"])} & {p["score"]:.2f} & {p["ev"]} & {cell(c["lLa"],c["lIa"])} & {p["adj"]:.2f} & {("--" if p["wmin"]==0 else format(p["wmin"],".2f"))} & {p["quad"]} & {a} \\\\')
ur[-1]=ur[-1].rstrip("\\").rstrip()
open("usecase.tex","w").write("\n".join(ur)+"%\n")

RS=json.load(open("rules_sens.json")); rr=RS["res"]; pc=lambda x:f"{100*x:.0f}\\%"
th=[r for r in rr if r["band_changed"]>0]; ed=[r for r in rr if r["band_changed"]==0]
th1=[r for r in th if not r["name"].startswith("A:")]
extra={"rsThMin":pc(min(r["comp_changed"] for r in th1)),"rsThMax":pc(max(r["comp_changed"] for r in th1)),"rsA":pc([r for r in th if r["name"].startswith("A:")][0]["comp_changed"]),
"rsEdMin":pc(min(r["comp_changed"] for r in ed)),"rsEdMax":pc(max(r["comp_changed"] for r in ed)),"rsMaxShift":max(r["maxshift"] for r in rr),
"rsExSame":sum(r["ex_bands_same"] for r in th),"rsNVar":len(th),"rsTauMin":f(min(r["tau"] for r in th)),"rsTauMax":f(max(r["tau"] for r in th))}
open("numbers.tex","a").write("".join("\\newcommand{\\%s}{%s}\n"%(k,v) for k,v in extra.items()))
tb=[]
for r in rr:
    nm=r["name"].replace(">=",r"$\ge$")
    st="--" if r["ex_cell_same"] is None else ("same" if r["ex_bands_same"] and r["ex_cell_same"] else "changes")
    tb.append(nm+" & "+pc(r["band_changed"])+" & "+pc(r["comp_changed"])+" & "+st+r" \\")
tb[-1]=tb[-1][:-3]
open("rulesens.tex","w").write("\n".join(tb)+"%\n")

# ---- V7: factor-level LLM rater agreement ----
RA=json.load(open("rater_study/rater_results.json"))["A"]; al=RA["alpha_items"]; f2=lambda x:f"{x:.2f}"
vc=RA["vs_catalogue"]; cm=RA["cross_model"]; pt=RA["pairwise_tau"]; pr=RA["premise"]
rng=lambda d,k:(f2(min(v[k] for v in d.values())),f2(max(v[k] for v in d.values())))
fk=[k for k in al if not k.startswith("group_") and k!="S"]
lo=min(fk,key=lambda k:al[k]["all_runs"]); hi=max(fk,key=lambda k:al[k]["all_runs"])
low2=sorted(fk,key=lambda k:al[k]["all_runs"])[:2]
extra2={"lfModels":len(RA["models"]),"lfRuns":sum(RA["runs"].values()),
"lfAll":f2(al["group_all14"]["all_runs"]),"lfAllMed":f2(al["group_all14"]["model_medians"]),"lfIEF":f2(al["group_IEF"]["all_runs"]),"lfLEF":f2(al["group_LEF"]["all_runs"]),"lfVEF":f2(al["group_VEF"]["all_runs"]),
"lfS":f2(al["S"]["all_runs"]),"lfHi":f2(al[hi]["all_runs"]),"lfHiName":hi,"lfLoA":f2(al[low2[0]]["all_runs"]),"lfLoAName":low2[0],"lfLoB":f2(al[low2[1]]["all_runs"]),"lfLoBName":low2[1],
"lfBandMin":f2(min(RA["alpha_derived_bands"].values())),"lfBandMax":f2(max(RA["alpha_derived_bands"].values())),
"lfW":f2(RA["kendall_w_models"]["W"]),"lfWp":"<0.001" if RA["kendall_w_models"]["p"]<0.001 else f2(RA["kendall_w_models"]["p"]),
"lfTauMin":f2(min(pt.values())),"lfTauMax":f2(max(pt.values())),"lfEnsTau":f2(RA["ensemble_vs_catalogue"]["tau"]),"lfEnsRho":f2(RA["ensemble_vs_catalogue"]["rho"]),
"lfCellAll":f"{100*cm['cell_all_agree']:.0f}\\%","lfBandAll":f"{100*cm['band_all_agree']:.0f}\\%","lfWithinOne":f"{100*cm['cell_within1_all']:.0f}\\%",
"lfRunMin":f2(min(RA["alpha_within_model"].values())),"lfRunMax":f2(max(RA["alpha_within_model"].values())),
"lfPremRho":f2(pr["between_model_sd_vs_w"]["rho"]),"lfPremP":f2(pr["between_model_sd_vs_w"]["p"]),"lfGapRho":f2(pr["gap_to_catalogue_vs_w"]["rho"]),"lfGapP":f2(pr["gap_to_catalogue_vs_w"]["p"]),
"lfSdHi":f"{pr['median_sd_strong_moderate']:.2f}","lfSdLo":f"{pr['median_sd_weak_none']:.2f}"}
open("numbers.tex","a").write("".join("\\newcommand{\\%s}{%s}\n"%(k,v) for k,v in extra2.items()))
NAMES={"claude":"Claude Sonnet 5.5","gpt":"ChatGPT (GPT-6)","gemini":"Gemini 1.5 Pro"}
tr=[]
for m in ("claude","gemini","gpt"):
    v=vc[m]; tr.append(f'{NAMES[m]} & {f2(v["tau"])} & {f2(v["rho"])} & {f2(v["cell_exact"])} & {f2(v["cell_within1"])} & {f2(v["band_wkappa"])} & {v["mean_bias"]:+.2f} \\\\')
e=RA["ensemble_vs_catalogue"]; tr.append(f'Mean of models & {f2(e["tau"])} & {f2(e["rho"])} & -- & -- & -- & --')
open("ratertable.tex","w").write("\n".join(tr)+"%\n")

# ---- official SecRAM 2.0 matrix applied ----
SR=json.load(open("secram.json")); V=SR["variants"]; pct=lambda x:f"{100*x:.0f}\\%"
g=lambda d,k:d.get(k,0)
m3={"srHighB":g(V["default"]["before"],"High"),"srMedB":g(V["default"]["before"],"Medium"),"srLowB":g(V["default"]["before"],"Low"),
"srHighA":g(V["default"]["after"],"High"),"srMedA":g(V["default"]["after"],"Medium"),"srLowA":g(V["default"]["after"],"Low"),
"srRiskChg":V["default"]["risk_changes"],"srRiskIds":", ".join(V["default"]["changed_ids"]),
"srRoundHigh":g(V["round"]["before"],"High"),"srRoundMed":g(V["round"]["before"],"Medium"),
"srMaxHigh":g(V["maximpact"]["before"],"High"),"srMaxMed":g(V["maximpact"]["before"],"Medium"),
"srAgreeRound":SR["agree_default_vs_round"],"srAgreeMax":SR["agree_default_vs_max"],
"srBox":sum(SR["example"]["box_risk"].values()),
"srRaterAlpha":f"{SR['raters']['alpha_risk_level']:.2f}","srRaterAll":pct(SR["raters"]["all_runs_same"]),"srModelsSame":pct(SR["raters"]["models_same"]),
"srCatMin":pct(min(SR["raters"]["model_vs_catalogue_same"].values())),"srCatMax":pct(max(SR["raters"]["model_vs_catalogue_same"].values()))}
open("numbers.tex","a").write("".join("\\newcommand{\\%s}{%s}\n"%(k,v) for k,v in m3.items()))

# ---- V8: SecRAM-native baseline (condition C) ----
NV=json.load(open("rater_study/secram_native.json")); RC=NV["route_comparison"]; pc=lambda x:f"{100*x:.0f}\\%"
sm=NV["vs_catalogue_same"]; w1=NV["vs_catalogue_within1"]; fm=NV["same_model_framework_vs_native_same_risk"]
dr=NV["impact_driver_share"]; cf=NV["confusion_catalogue_rows_native_cols"]
nvm={"nvAlphaRisk":f"{RC['alpha_native']['risk']:.2f}","nvAlphaRiskFw":f"{RC['alpha_framework']['risk']:.2f}",
"nvAlphaL":f"{RC['alpha_native']['likelihood']:.2f}","nvAlphaLFw":f"{RC['alpha_framework']['likelihood']:.2f}",
"nvAlphaI":f"{RC['alpha_native']['impact']:.2f}","nvAlphaIFw":f"{RC['alpha_framework']['impact']:.2f}","nvAlphaIMean":f"{RC['native_mean_impact_alpha']:.2f}",
"nvDiffLo":f"{RC['alpha_diff_risk_ci'][0]:.2f}","nvDiffHi":f"{RC['alpha_diff_risk_ci'][1]:.2f}",
"nvSameMin":pc(min(sm.values())),"nvSameMax":pc(max(sm.values())),"nvWithinMin":pc(min(w1.values())),"nvWithinMax":pc(max(w1.values())),
"nvFwSameMin":pc(min(fm.values())),"nvFwSameMax":pc(max(fm.values())),
"nvModelsSame":pc(NV["models_same_risk"]),"nvModelsSameFw":pc(RC["models_same_risk_framework"]),
"nvAllRuns":pc(NV["all_runs_same_risk"]),"nvAllRunsFw":pc(RC["all_runs_same_risk_framework"]),
"nvPairNative":pc(RC["pair_same_risk"]["native"]),"nvPairFw":pc(RC["pair_same_risk"]["framework"]),
"nvCell":pc(NV["models_same_cell"]),"nvTau":f"{NV['ensemble_vs_catalogue']['tau']:.2f}","nvRho":f"{NV['ensemble_vs_catalogue']['rho']:.2f}",
"nvRunMinFw":f"{min(v['framework'] for v in RC['within_model_alpha'].values()):.2f}","nvRunMaxFw":f"{max(v['framework'] for v in RC['within_model_alpha'].values()):.2f}",
"nvRunMinNat":f"{min(v['native'] for v in RC['within_model_alpha'].values()):.2f}","nvRunMaxNat":f"{max(v['native'] for v in RC['within_model_alpha'].values()):.2f}",
"nvHighToMed":cf[2][1],"nvHighToLow":cf[2][0],"nvHighTotal":sum(cf[2]),"nvMedToHigh":cf[1][2],"nvMedTotal":sum(cf[1]),
"nvLCorr":f"{NV['native_cat_corr']['L_vs_catL']:.2f}"}
open("numbers.tex","a").write("".join("\\newcommand{\\%s}{%s}\n"%(k,v) for k,v in nvm.items()))
