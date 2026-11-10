import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix","font.size":7,"axes.linewidth":.6,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
R=json.load(open("results.json")); P=R["per"]
INK="#1f2937"; MUT="#6b7280"
BAND={"Medium":"#FDD49E","High":"#FC8D59","Critical":"#B30000"}
EVC={"Strong":"#08519C","Moderate":"#4A90C2","Weak":"#A9CCE3","None":"#FFFFFF"}
CUT=[1.8,2.6,3.4,4.2]
# ---------- Fig 3 EWTS dumbbell + quadrant ----------
Ps=sorted(P,key=lambda p:p["score"])
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.0,3.5),gridspec_kw={"width_ratios":[1.15,1],"wspace":.32})
for t in CUT[1:]: a1.axvline(t,color="#d1d5db",lw=.7,zorder=0)
for k,p in enumerate(Ps):
    a1.plot([p["adj"],p["score"]],[k,k],color=MUT,lw=.9,zorder=1)
    a1.scatter(p["score"],k,s=17,marker="o",fc="white",ec=INK,lw=.8,zorder=3)
    a1.scatter(p["adj"],k,s=22,marker="o",fc=EVC[p["ev"]],ec=INK,lw=.7,zorder=4,hatch="////" if p["ev"]=="None" else None)
    if p["band"]!=p["adjband"]: a1.text(p["adj"]-.04,k,"↓",ha="right",va="center",fontsize=7,color="#B30000",fontweight="bold")
a1.set_yticks(range(len(Ps))); a1.set_yticklabels([p["id"] for p in Ps],fontsize=5.8); a1.set_ylim(-.8,len(Ps)-.2); a1.set_xlim(2.7,4.6)
for t,n in zip(CUT[1:],["Medium|High","High|Critical"]): pass
a1.text(3.4,len(Ps)-.1,"High",ha="left",va="bottom",fontsize=5.8,color=MUT); a1.text(4.2,len(Ps)-.1,"Critical",ha="left",va="bottom",fontsize=5.8,color=MUT); a1.text(2.75,len(Ps)-.1,"Medium",ha="left",va="bottom",fontsize=5.8,color=MUT)
a1.set_xlabel("DREAD-S score (○)  →  evidence-adjusted score (●)",fontsize=7); a1.tick_params(axis="y",length=0)
a1.set_title("(a) Effect of the EWTS discount",fontsize=7.6,loc="left",fontweight="bold",pad=12)
h=[plt.Line2D([],[],marker="o",ls="",mfc=EVC[k] if k!="None" else "white",mec=INK,ms=4,label=k) for k in ["Strong","Moderate","Weak","None"]]
a1.legend(handles=h,fontsize=5.6,title="Evidence",title_fontsize=5.8,loc="lower right",frameon=False)
# quadrant
a2.axhline(3.4,color="#9ca3af",lw=.8,ls="--"); a2.axvline(.625,color="#9ca3af",lw=.8,ls="--")
a2.set_xlim(.15,1.1); a2.set_ylim(2.75,4.55)
QC={"Act":"#B30000","Verify":"#D97706","Monitor":"#2563EB","Defer":"#6b7280"}
rng=np.random.default_rng(7)
off={}
for p in P:
    key=(round(p["w"],2),round(p["score"],1)); off[key]=off.get(key,0)+1
    jx=(rng.random()-.5)*.09
    a2.scatter(p["w"]+jx,p["score"],s=20,fc=EVC[p["ev"]],ec=QC[p["quad"]],lw=1.3,zorder=3,hatch="////" if p["ev"]=="None" else None)
for q,(x,y,ha,va) in {"Act":(1.08,4.5,"right","top"),"Verify":(.18,4.5,"left","top"),"Monitor":(1.08,2.8,"right","bottom"),"Defer":(.18,2.8,"left","bottom")}.items():
    a2.text(x,y,q,ha=ha,va=va,fontsize=8,fontweight="bold",color=QC[q],alpha=.9)
for pid,dx,dy in [("INF-02",-.03,.0),("DAT-02",-.03,-.0),("INF-07",.03,.06),("INF-01",-.03,0),("SVC-05",-.03,.0),("DAT-03",-.03,-.07)]:
    p=next(x for x in P if x["id"]==pid); a2.annotate(pid,(p["w"],p["score"]),(p["w"]+dx,p["score"]+dy),fontsize=5.6,ha="right" if dx<0 else "left",va="center",color=INK)
a2.set_xticks([.25,.5,.75,1.0]); a2.set_xticklabels(["None\n0.25","Weak\n0.50","Moderate\n0.75","Strong\n1.00"],fontsize=6)
a2.set_xlabel("Evidence weight $w$",fontsize=7); a2.set_ylabel("DREAD-S score",fontsize=7)
a2.set_title("(b) Risk–evidence decision quadrants",fontsize=7.6,loc="left",fontweight="bold",pad=12)
fig.savefig("fig/fig3_ewts.pdf",bbox_inches="tight",pad_inches=.03); plt.close(fig)
# ---------- Fig 4 sensitivity ----------
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.0,2.35),gridspec_kw={"width_ratios":[1,1.35],"wspace":.28})
sc=["mild","linear","thesis-tier","default","steep"]; names=["mild\n1/.9/.8/.7","linear\n1/.8/.6/.4","tier-only\n1/.75/.5/.5","default\n1/.75/.5/.25","steep\n1/.6/.3/.1"]
vals=[R["alt_weights"][k]["n_reclass"] for k in sc]
b=a1.bar(range(5),vals,color=["#9ecae1"]*5,ec=INK,lw=.5,width=.62); b[3].set_color("#08519C")
for i,v in enumerate(vals): a1.text(i,v+.25,str(v),ha="center",fontsize=6.5)
a1.set_xticks(range(5)); a1.set_xticklabels(names,fontsize=5.4); a1.set_ylabel("Assets changing band (of 21)",fontsize=6.6); a1.set_ylim(0,13)
a1.set_title("(a) Weight-scheme sensitivity",fontsize=7.6,loc="left",fontweight="bold")
Pm=sorted(P,key=lambda p:-p["stab"])
for k,p in enumerate(Pm):
    a2.vlines(k,p["stab"],1,color="#d1d5db",lw=.8)
    a2.scatter(k,p["stab"],s=22,fc=EVC[p["ev"]],ec=INK,lw=.6,zorder=3,hatch="////" if p["ev"]=="None" else None)
a2.axhline(.75,color="#B30000",lw=.7,ls="--"); a2.text(20.4,.76,"0.75",fontsize=5.6,color="#B30000",ha="right",va="bottom")
a2.set_xticks(range(21)); a2.set_xticklabels([p["id"] for p in Pm],rotation=90,fontsize=5.2); a2.set_ylim(.4,1.02); a2.set_ylabel("Band stability under ±1 noise",fontsize=6.6)
a2.set_title("(b) Per-asset stability (20,000 draws)",fontsize=7.6,loc="left",fontweight="bold")
fig.savefig("fig/fig4_sens.pdf",bbox_inches="tight",pad_inches=.03); plt.close(fig)
print("ok")
