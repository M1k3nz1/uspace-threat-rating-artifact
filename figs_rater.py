import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix","font.size":7,"axes.linewidth":.6,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
R=json.load(open("rater_study/rater_results.json"))["A"]; al=R["alpha_items"]
INK="#1f2937"; MUT="#6b7280"
grp=[("IEF","#2F5D9B",["safety","scope","regulatory","cascading","recovery"]),("LEF","#B45309",["exposure","access","maturity","tools","automation"]),("VEF","#1E7B4B",["documentation","interface","complexity","monitoring"]),("S","#4B5563",["S"])]
rows=[(k,c,g) for g,c,ks in grp for k in ks]
fig,ax=plt.subplots(figsize=(3.45,3.15))
ys=list(range(len(rows)))[::-1]
for y,(k,c,g) in zip(ys,rows):
    v=al[k]["all_runs"]; ax.barh(y,max(v,0),color=c,height=.62,edgecolor="white",lw=.6)
    ax.text(max(v,0)+.012,y,f"{v:.2f}",va="center",fontsize=6.3,color=INK)
ax.set_yticks(ys); ax.set_yticklabels([k for k,_,_ in rows],fontsize=6.4)
for x,t in ((0.667,"0.667"),(0.8,"0.80")): ax.axvline(x,color=MUT,lw=.6,ls=(0,(3,2))); ax.text(x+(-.008 if x<.7 else .008),len(rows)-.15,t,ha=("right" if x<.7 else "left"),va="bottom",fontsize=5.8,color=MUT)
ax.set_xlim(0,1); ax.set_ylim(-.7,len(rows)+.4); ax.set_xlabel("Krippendorff's $\\alpha$ (ordinal), 3 models $\\times$ 3 runs",fontsize=6.8)
ax.tick_params(length=2,width=.5); ax.grid(axis="x",lw=.3,color="#e5e7eb"); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c,label=n) for n,c in (("impact (IEF)","#2F5D9B"),("likelihood (LEF)","#B45309"),("visibility (VEF)","#1E7B4B"),("safety $S$","#4B5563"))],fontsize=5.8,frameon=True,facecolor="white",edgecolor="none",framealpha=1,loc="center right",bbox_to_anchor=(1.0,0.115),ncol=2,columnspacing=.8,handlelength=1,borderaxespad=.1)
fig.tight_layout(pad=.4); fig.savefig("fig/fig7_factors.pdf"); print("ok")
