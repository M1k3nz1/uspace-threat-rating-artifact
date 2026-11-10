import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix","font.size":7,"axes.linewidth":.6,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
R=json.load(open("results.json")); P=R["per"]; V=json.load(open("validation.json"))
INK="#1f2937"; MUT="#6b7280"
EVC={"Strong":"#08519C","Moderate":"#4A90C2","Weak":"#A9CCE3","None":"#FFFFFF"}
BLUE=("#EAF1FB","#2F5D9B"); ORG=("#FDEFE3","#B45309"); GRN=("#E8F5EC","#1E7B4B"); GRY=("#F3F4F6","#4B5563")
# ============ Fig 1: framework ============
fig,ax=plt.subplots(figsize=(7.0,4.15)); ax.set_xlim(-4,100); ax.set_ylim(0,60); ax.axis("off")
def card(x,y,w,h,fc,ec,lw=.9,ls="-",r=1.1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.15,rounding_size={r}",fc=fc,ec=ec,lw=lw,ls=ls))
def arrow(p,q,c=INK,lw=1,rad=0,style="-|>",ms=7,ls="-"):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle=style,mutation_scale=ms,lw=lw,color=c,shrinkA=0,shrinkB=0,connectionstyle=f"arc3,rad={rad}",ls=ls))
def badge(x,y,n,c):
    ax.add_patch(Circle((x,y),1.55,fc=c,ec="white",lw=.8,zorder=5)); ax.text(x,y-.05,str(n),ha="center",va="center",color="white",fontsize=7.2,fontweight="bold",zorder=6)
# band labels
for y,t in [(49.2,"INPUTS"),(25.6,"FRAMEWORK"),(6.1,"OUTPUTS")]:
    ax.text(-2.4,y,t,fontsize=6.3,color=MUT,fontweight="bold",va="center",ha="center",rotation=90)
ax.plot([-4,100],[40.6,40.6],color="#e5e7eb",lw=.6); ax.plot([-4,100],[12.6,12.6],color="#e5e7eb",lw=.6)
# inputs
card(1,44,38.5,10.5,*GRY[:1],GRY[1]); ax.text(20.2,52.4,"Asset catalogue (expert-rated)",ha="center",fontsize=7.4,fontweight="bold",color=INK)
ax.text(20.2,48.4,"per asset:  D  R  E  A  D$_2$ $\\in\\{1..10\\}$,   S $\\in\\{1..5\\}$\nDREAD-S: DREAD extended with a calibrated safety term",ha="center",va="center",fontsize=6.3,color=INK,linespacing=1.5)
card(42,44,38.5,10.5,"#FFFFFF",MUT,ls=(0,(3,2))); ax.text(61.2,52.4,"Evidence register",ha="center",fontsize=7.4,fontweight="bold",color=INK)
ax.text(61.2,48.4,"source quality × evidence type × link basis\nper-asset confidence: Strong · Moderate · Weak · None",ha="center",va="center",fontsize=6.3,color=INK,linespacing=1.5)
# stages
X=[1,21.5,42,62.5,83]; Wd=[18,18,18,18,16]; Y0=14.6; H=22
spec=[(BLUE,"Rescale & split",["$\\nu(x)=1+\\frac{4(x-1)}{9}$","$I=\\frac{\\nu(D)+\\nu(A)+S}{3}$","$L=\\frac{\\nu(R)+\\nu(E)+\\nu(D_2)}{3}$"]),
 (BLUE,"Level mapping",["$\\lambda: [1,5]\\to\\{1,\\dots,5\\}$","cell $(\\lambda(L),\\lambda(I))$","DREAD-S $=\\frac{I+L}{2}$"]),
 (ORG,"Evidence weight",["confidence $\\mapsto w\\in(0,1]$","1 / 0.75 / 0.50 / 0.25","(default; varied in evaluation)"]),
 (ORG,"EWTS discount",["$\\tilde r=3+w\\,(r-3)$","band kept iff $w>w^{*}$","$w^{*}=\\frac{\\tau-3}{r-3}$"]),
 (GRN,"Decision",["risk $\\times$ evidence:","Act · Verify","Monitor · Defer  + flag"])]
for k,(col,title,lines) in enumerate(spec):
    x,w=X[k],Wd[k]; card(x,Y0,w,H,col[0],col[1],lw=1.1)
    badge(x+2.1,Y0+H-2.3,k+1,col[1]); ax.text(x+w/2+1.6,Y0+H-2.3,title,ha="center",va="center",fontsize=6.9,fontweight="bold",color=INK)
    for j,l in enumerate(lines): ax.text(x+w/2,Y0+H-8.2-j*4.6,l,ha="center",va="center",fontsize=6.2,color=INK)
for k in range(4): arrow((X[k]+Wd[k]+.25,Y0+H/2),(X[k+1]-.25,Y0+H/2))
# input arrows
arrow((10,43.8),(10,Y0+H+.2),GRY[1]); arrow((51,43.8),(51,Y0+H+.2),ORG[1])
ax.text(11,42.2,"ratings",fontsize=5.9,color=MUT,style="italic"); ax.text(52,42.2,"labels",fontsize=5.9,color=MUT,style="italic")
# outputs
def out(x,w,t1,t2,col):
    card(x,1.2,w,9.8,"#FFFFFF",col,lw=1.0); ax.text(x+w/2,8.3,t1,ha="center",va="center",fontsize=6.9,fontweight="bold",color=INK); ax.text(x+w/2,4.5,t2,ha="center",va="center",fontsize=6.0,color=INK,linespacing=1.4)
out(12,28,"SecRAM-style level pair","$(L,I)$ levels + cell, reported in the\nproject's own impact/likelihood tables",BLUE[1])
out(45,27,"Evidence-adjusted score","$\\tilde r$, adjusted band and $w^{*}$\nper asset",ORG[1])
out(75,24,"Prioritised work list","class per asset; Verify items become\nevidence-collection tasks",GRN[1])
arrow((30.5,Y0-.2),(30.5,11.3),BLUE[1]); arrow((68,Y0-.2),(68,11.3),ORG[1]); arrow((91,Y0-.2),(91,11.3),GRN[1])
# feedback loop
ax.add_patch(FancyArrowPatch((91,Y0+H+.25),(81,49.2),arrowstyle="-|>",mutation_scale=7,lw=1,color=GRN[1],ls=(0,(4,2)),connectionstyle="angle,angleA=90,angleB=0,rad=6",shrinkA=0,shrinkB=0))
ax.text(99.5,46.3,"Verify:\ncollect evidence,\nupdate register",ha="right",va="center",fontsize=5.8,color=GRN[1],style="italic",linespacing=1.3)
fig.savefig("fig/fig1_framework.pdf",bbox_inches="tight",pad_inches=.03); plt.close(fig)
# ============ Fig 2: I-L plane + drivers ============
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.0,3.35),gridspec_kw={"width_ratios":[1.12,1],"wspace":.30})
CUT=[1.8,2.6,3.4,4.2]
for t in CUT[2:]: a1.axvline(t,color="#cbd5e1",lw=.6,zorder=0); a1.axhline(t,color="#cbd5e1",lw=.6,zorder=0)
xs=np.linspace(2.3,5.0,50)
for c,lab in [(3.4,"DREAD-S = 3.4"),(4.2,"DREAD-S = 4.2")]:
    a1.plot(xs,2*c-xs,color="#9ca3af",lw=.8,ls="--",zorder=1)

for p in P:
    a1.scatter(p["L"],p["I"],s=26,fc=EVC[p["ev"]],ec=INK,lw=.7,zorder=3,hatch="////" if p["ev"]=="None" else None)
lab={"INF-02":(.05,.02,"left"),"DAT-02":(-.05,-.1,"right"),"INF-07":(.05,.03,"left"),"INF-04":(-.05,-.1,"left"),"INF-06":(.07,.07,"left"),"GOV-02":(-.05,-.02,"right"),"SVC-02":(-.05,.05,"right"),"INF-01":(.05,-.05,"left"),"DAT-03":(-.04,-.06,"right"),"INF-03":(-.05,.03,"right")}
for p in P:
    if p["id"] in lab:
        dx,dy,ha=lab[p["id"]]; a1.text(p["L"]+dx,p["I"]+dy,p["id"],fontsize=5.7,ha=ha,va="center",color=INK)
a1.set_xlim(2.35,4.25); a1.set_ylim(2.55,5.0)
a1.set_xlabel("Likelihood index $L$ (R, E, D$_2$)",fontsize=7); a1.set_ylabel("Impact index $I$ (D, A, S)",fontsize=7)
a1.set_title("(a) Impact–likelihood plane",fontsize=7.6,loc="left",fontweight="bold")
hd=[plt.Line2D([],[],marker="o",ls="",mfc=EVC[k] if k!="None" else "white",mec=INK,ms=4,label=k) for k in ["Strong","Moderate","Weak","None"]]
hd.append(plt.Line2D([],[],color="#9ca3af",ls="--",lw=.8,label="DREAD-S = 3.4 / 4.2"))
a1.legend(handles=hd,fontsize=5.6,title="Evidence",title_fontsize=5.8,loc="lower right",frameon=False,bbox_to_anchor=(1.0,0.0))
# drivers
Pd=sorted(P,key=lambda p:p["I"]-p["L"])
for k,p in enumerate(Pd):
    d=p["I"]-p["L"]; a2.barh(k,d,color="#cbd5e1" if d<0 else "#94a3b8",height=.66,ec="none",zorder=2)
    a2.scatter(d,k,s=14,fc=EVC[p["ev"]],ec=INK,lw=.5,zorder=3,hatch="////" if p["ev"]=="None" else None)
a2.axvline(0,color=INK,lw=.7); a2.set_yticks(range(21)); a2.set_yticklabels([p["id"] for p in Pd],fontsize=5.3); a2.tick_params(axis="y",length=0)
a2.set_xlabel("$I-L$  (positive: consequence outweighs ease of attack)",fontsize=6.6); a2.set_ylim(-.8,20.8)
a2.set_title("(b) What drives each score",fontsize=7.6,loc="left",fontweight="bold")
fig.savefig("fig/fig2_plane.pdf",bbox_inches="tight",pad_inches=.03); plt.close(fig)
# ============ Fig 5: independent-rater check ============
rp=V["rater"]["per_asset"]; fig,(a1,a2)=plt.subplots(1,2,figsize=(7.0,2.5),gridspec_kw={"wspace":.28})
rng=np.random.default_rng(3)
for ax_,key,yl,tt,res in [(a1,"between","Between-model SD of DREAD-S","(a) Rater disagreement vs evidence weight",V["rater"]["between_model_sd"]),(a2,"gap","|mean LLM score − catalogue score|","(b) Distance from catalogue vs evidence weight",V["rater"]["gap_to_catalogue"])]:
    for p in P:
        d=rp[p["id"]]; x=d["w"]+(rng.random()-.5)*.07
        ax_.scatter(x,d[key],s=22,fc=EVC[p["ev"]],ec=INK,lw=.6,zorder=3,hatch="////" if p["ev"]=="None" else None)
    for w_ in [.25,.5,.75,1.0]:
        vs=[rp[p["id"]][key] for p in P if abs(p["w"]-w_)<1e-9]
        if vs: ax_.hlines(np.median(vs),w_-.07,w_+.07,color="#B30000",lw=1.3,zorder=4)
    ax_.set_xticks([.25,.5,.75,1.0]); ax_.set_xticklabels(["None","Weak","Moderate","Strong"],fontsize=6.2); ax_.set_xlim(.1,1.15)
    ax_.set_xlabel("Evidence confidence",fontsize=7); ax_.set_ylabel(yl,fontsize=6.8); ax_.set_title(tt,fontsize=7.6,loc="left",fontweight="bold")
    ax_.text(.02,.03,f"Spearman $\\rho$ = {res['rho']:.2f},  $p$ = {res['p']:.2f}",transform=ax_.transAxes,ha="left",va="bottom",fontsize=6.4,color=INK)
a2.text(.98,.86,"red bars: group medians",transform=a2.transAxes,ha="right",va="top",fontsize=5.8,color="#B30000")
fig.savefig("fig/fig5_rater.pdf",bbox_inches="tight",pad_inches=.03); plt.close(fig)
print("ok")
