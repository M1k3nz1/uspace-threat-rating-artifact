import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix","font.size":7,"axes.linewidth":.6,"pdf.fonttype":42})
INK="#1f2937"; MUT="#6b7280"
EVC={"Strong":"#08519C","Moderate":"#4A90C2","Weak":"#A9CCE3","None":"#FFFFFF"}
from secram import risk as _risk, CLS as _CLS
SEV=["#CFE5C6","#FBD98B","#E8786A"]   # SecRAM 2.0 risk levels: Low, Medium, High
BLUE=("#EAF1FB","#2F5D9B"); ORG=("#FDEFE3","#B45309"); GRN=("#E8F5EC","#1E7B4B"); GRY=("#F3F4F6","#4B5563"); TEAL=("#E6F4F1","#17756B")
CUT=[1.8,2.6,3.4,4.2]
def cls(l,i):   # official SecRAM 2.0 risk level (0 Low, 1 Medium, 2 High) for likelihood l, impact i
    return _CLS[_risk(l,i)]
def card(ax,x,y,w,h,fc,ec,lw=.9,ls="-",r=.9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.12,rounding_size={r}",fc=fc,ec=ec,lw=lw,ls=ls))
def arrow(ax,p,q,c=INK,lw=.9,rad=0,ms=6,ls="-"):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle="-|>",mutation_scale=ms,lw=lw,color=c,shrinkA=0,shrinkB=0,connectionstyle=f"arc3,rad={rad}",ls=ls))
def badge(ax,x,y,n,c):
    ax.add_patch(Circle((x,y),1.35,fc=c,ec="white",lw=.8,zorder=5)); ax.text(x,y-.05,str(n),ha="center",va="center",color="white",fontsize=6.6,fontweight="bold",zorder=6)
def matrix(ax,x0,y0,cw,ch,hi=None,box=None,label=True,fs=5.6):
    for l in range(1,6):
        for i in range(1,6):
            ax.add_patch(Rectangle((x0+(l-1)*cw,y0+(i-1)*ch),cw,ch,fc=SEV[cls(l,i)],ec="white",lw=.8))
    if box:
        (l1,l2),(i1,i2)=box
        ax.add_patch(Rectangle((x0+(l1-1)*cw,y0+(i1-1)*ch),(l2-l1+1)*cw,(i2-i1+1)*ch,fc="none",ec=INK,lw=.9,ls=(0,(3,2)),zorder=4))
    if hi:
        l,i=hi; ax.add_patch(Rectangle((x0+(l-1)*cw,y0+(i-1)*ch),cw,ch,fc="none",ec=INK,lw=1.6,zorder=5))
    if label:
        for k in range(1,6):
            ax.text(x0+(k-.5)*cw,y0-ch*.55,str(k),ha="center",va="center",fontsize=fs,color=INK)
            ax.text(x0-cw*.45,y0+(k-.5)*ch,str(k),ha="center",va="center",fontsize=fs,color=INK)
# ================= Fig A: framework =================
fig,ax=plt.subplots(figsize=(7.0,4.75)); ax.set_xlim(0,100); ax.set_ylim(0,67); ax.axis("off")
TY=65.2
x1,w1=0.8,26.4
def panel(y,h,title,sub,items,col):
    card(ax,x1,y,w1,h,"#FFFFFF",col[1],lw=1.0)
    ax.add_patch(Rectangle((x1-.12,y+h-3.4),w1+.24,3.5,fc=col[0],ec="none",zorder=1))
    ax.text(x1+1.2,y+h-1.7,title,fontsize=6.3,fontweight="bold",color=INK,va="center",zorder=2); ax.text(x1+w1-.9,y+h-1.7,sub,fontsize=5.8,color=MUT,ha="right",va="center",style="italic",zorder=2)
    for j,t in enumerate(items):
        yy=y+h-5.4-j*1.75
        ax.add_patch(Rectangle((x1+1.2,yy-.5),1.0,1.0,fc="white",ec=MUT,lw=.5)); ax.text(x1+3.2,yy,t,fontsize=6.0,color=INK,va="center")
badge(ax,x1+1.5,TY,1,GRY[1]); ax.text(x1+3.6,TY,"Observable evidence factors",fontsize=7,fontweight="bold",color=INK,va="center")
panel(48.4,14.2,"IEF  impact evidence","$\\to$ D, A",["Safety criticality","Operational scope","Regulatory consequence","Cascading potential","Recovery complexity"],BLUE)
panel(33.4,14.2,"LEF  likelihood evidence","$\\to$ R, E",["Exposure level","Access requirement","Attack maturity","Tool availability","Automation potential"],ORG)
panel(20.6,11.6,"VEF  visibility evidence","$\\to$ D$_2$",["Documentation exposure","Interface transparency","Complexity","Monitoring gap"],TEAL)
ax.text(x1+w1/2,18.7,"each factor scored Low 1 · Medium 2 · High 3",fontsize=5.8,color=MUT,ha="center",style="italic")
# ---- Step 2: rules
x2,w2=31.5,24.0
badge(ax,x2+1.5,TY,2,BLUE[1]); ax.text(x2+3.6,TY,"Rule-based thresholds",fontsize=7,fontweight="bold",color=INK,va="center")
rules=[("D","$\\geq$3 High IEF $\\to$ 8–10",BLUE,58.2),("A","fleet / cross-layer $\\to$ 8–10",BLUE,52.8),("S","SAIL / ARA class $\\to$ 1–5",GRY,47.4),
       ("R","automated & stable $\\to$ 8–10",ORG,42.0),("E","public + known tools $\\to$ 8–10",ORG,36.6),("D$_2$","public interfaces $\\to$ 7–10",TEAL,31.2)]
for t,r,c,y in rules:
    card(ax,x2,y-2.2,w2,4.4,c[0],c[1],lw=.9,r=.6); ax.text(x2+2.4,y,t,fontsize=7,fontweight="bold",color=INK,ha="center",va="center"); ax.text(x2+5.0,y,r,fontsize=5.7,color=INK,va="center")
ax.text(x2+w2/2,26.6,"top-band rules as in the framework;\nintermediate bands in Table 2",fontsize=5.6,color=MUT,ha="center",va="center",style="italic",linespacing=1.3)
ex=x1+w1+.3; ent=x2-.35
arrow(ax,(ex,57.0),(ent,58.2)); arrow(ax,(ex,55.0),(ent,52.8))
arrow(ax,(ex,42.0),(ent,42.0)); arrow(ax,(ex,40.0),(ent,36.6)); arrow(ax,(ex,26.5),(ent,31.2))
ax.text(x2-.6,47.4,"",fontsize=5)
# ---- Step 3: normalisation
x3,w3=59.5,17.0
badge(ax,x3+1.5,TY,3,BLUE[1]); ax.text(x3+3.6,TY,"DREAD-S split",fontsize=7,fontweight="bold",color=INK,va="center")
card(ax,x3,47.2,w3,11.8,BLUE[0],BLUE[1]); ax.text(x3+w3/2,57.0,"Impact index",fontsize=6.4,fontweight="bold",color=INK,ha="center",va="center"); ax.text(x3+w3/2,51.9,"$I=\\dfrac{\\nu(D)+\\nu(A)+S}{3}$",fontsize=6.5,ha="center",va="center",color=INK)
card(ax,x3,31.2,w3,11.8,ORG[0],ORG[1]); ax.text(x3+w3/2,41.0,"Likelihood index",fontsize=6.4,fontweight="bold",color=INK,ha="center",va="center"); ax.text(x3+w3/2,35.9,"$L=\\dfrac{\\nu(R)+\\nu(E)+\\nu(D_2)}{3}$",fontsize=6.5,ha="center",va="center",color=INK)
card(ax,x3+1.2,43.8,w3-2.4,2.6,"#FFFFFF",MUT,r=.5); ax.text(x3+w3/2,45.1,"DREAD-S $=(I+L)/2$",fontsize=5.9,ha="center",va="center",color=INK)
bx=x2+w2+1.4
for ys,c,mid,tgt in [((58.2,52.8,47.4),BLUE[1],53.1,53.1),((42.0,36.6,31.2),ORG[1],36.6,37.1)]:
    ax.plot([bx,bx],[min(ys),max(ys)],color=c,lw=.9)
    for y in ys: ax.plot([x2+w2+.15,bx],[y,y],color=c,lw=.9)
    arrow(ax,(bx,mid),(x3-.35,tgt),c)
# ---- Step 4: SecRAM matrix
x4=81.0
badge(ax,x4+1.5,TY,4,GRN[1]); ax.text(x4+3.6,TY,"SecRAM cell",fontsize=7,fontweight="bold",color=INK,va="center")
cw,ch=3.0,4.3; mx,my=x4+4.3,37.6
matrix(ax,mx,my,cw,ch,hi=(4,4))
ax.text(mx+2.5*cw,my-ch*1.5,"likelihood level $\\lambda(L)$",fontsize=6,ha="center",va="center",color=INK)
ax.text(mx-cw*1.45,my+2.5*ch,"impact level $\\lambda(I)$",fontsize=6,ha="center",va="center",rotation=90,color=INK)
ax.text(mx+3.5*cw,my+3.5*ch,"$\\bigstar$",fontsize=8.5,ha="center",va="center",color="white",zorder=7)
ax.text(mx+2.5*cw,my+5*ch+1.7,"cell $(\\lambda(L),\\lambda(I))$",fontsize=6,ha="center",va="center",color=INK)
arrow(ax,(x3+w3+.35,53.1),(mx-cw*1.9,53.1),BLUE[1])
arrow(ax,(x3+w3+.35,36.6),(mx+0.9,my-ch*1.5+.2),ORG[1],rad=.0)
ax.text(mx+2.5*cw,my-ch*2.5,"SecRAM 2.0 risk levels",fontsize=5.4,ha="center",va="center",color=MUT,style="italic")
# ---- Step 5: evidence weighting (bottom row)
ax.plot([0,100],[16.4,16.4],color="#e5e7eb",lw=.7)
badge(ax,x1+1.5,14.6,5,ORG[1]); ax.text(x1+3.6,14.6,"Evidence weighting and decision",fontsize=7,fontweight="bold",color=INK,va="center")
card(ax,0.8,1.0,34.5,11.4,"#FFFFFF",ORG[1],lw=1.0)
ax.text(18.0,10.6,"Evidence register",fontsize=6.4,fontweight="bold",color=INK,ha="center",va="center"); ax.text(18.0,5.8,"link strength = source quality $\\times$ type weight\n$\\times$ link basis; type weight: PoC/live 1.00,\nsimulation 0.75, model-based 0.50;\nasset confidence $\\mapsto w\\in\\{1,.75,.5,.25\\}$",fontsize=5.8,ha="center",va="center",color=INK,linespacing=1.4)
card(ax,40.5,1.0,29.0,11.4,ORG[0],ORG[1],lw=1.0)
ax.text(55.0,10.6,"EWTS adjusted score",fontsize=6.4,fontweight="bold",color=INK,ha="center",va="center"); ax.text(55.0,6.0,"$\\tilde r=\\mu+w\\,(r-\\mu)$,  $\\mu=3$\nadjusted cell $(\\lambda(\\tilde L),\\lambda(\\tilde I))$\nband kept iff $w>w^{*}$",fontsize=6.0,ha="center",va="center",color=INK,linespacing=1.4)
card(ax,74.7,1.0,24.5,11.4,GRN[0],GRN[1],lw=1.0)
ax.text(87.0,10.6,"Decision",fontsize=6.4,fontweight="bold",color=INK,ha="center",va="center"); ax.text(87.0,6.0,"risk $\\times$ evidence:\nAct · Verify · Monitor · Defer\n+ stability flag",fontsize=6.0,ha="center",va="center",color=INK,linespacing=1.4)
arrow(ax,(35.7,6.7),(40.1,6.7),ORG[1]); arrow(ax,(69.9,6.7),(74.3,6.7),GRN[1])
arrow(ax,(x3+w3/2-2,30.9),(58.0,12.9),BLUE[1],rad=0.0)
ax.text(x3+w3/2-1.0,22.5,"$r$, $I$, $L$ from step 3",fontsize=5.8,color=MUT,style="italic",va="center",ha="left")
fig.savefig("fig/figA_framework.pdf",bbox_inches="tight",pad_inches=.03); fig.savefig("fig/figA_framework.png",dpi=170,bbox_inches="tight",pad_inches=.03); plt.close(fig)
print("A done")

# ================= Fig B: worked example =================
import json
F=json.load(open("framework.json")); E=F["example"]; fa=E["factors"]
fig,ax=plt.subplots(figsize=(7.0,3.55)); ax.set_xlim(0,100); ax.set_ylim(0,50.5); ax.axis("off")
CH={1:"#DCE9F6",2:"#74A9D8",3:"#08519C"}
def head(x,y,n,t): badge(ax,x+1.4,y,n,GRY[1]); ax.text(x+3.4,y,t,fontsize=7,fontweight="bold",color=INK,va="center")
head(0.5,49.0,1,"Evidence scored (worked example)")
groups=[("IEF",["Safety criticality","Operational scope","Regulatory consequence","Cascading potential","Recovery complexity"],["safety","scope","regulatory","cascading","recovery"],BLUE),
        ("LEF",["Exposure level","Access requirement","Attack maturity","Tool availability","Automation potential"],["exposure","access","maturity","tools","automation"],ORG),
        ("VEF",["Documentation exposure","Interface transparency","Complexity","Monitoring gap"],["documentation","interface","complexity","monitoring"],TEAL)]
y=45.0
for g,names,keys,col in groups:
    ax.add_patch(Rectangle((0.5,y-1.0),33,2.0,fc=col[0],ec="none")); ax.text(1.2,y,g,fontsize=6.2,fontweight="bold",color=INK,va="center")
    for k in "LMH": pass
    for j,(nm,ky) in enumerate(zip(names,keys)):
        yy=y-2.4-j*2.3
        ax.text(1.2,yy,nm,fontsize=5.7,color=INK,va="center")
        for t,lab in zip((1,2,3),"LMH"):
            xx=21.5+(t-1)*4.1; on=fa[ky]==t
            ax.add_patch(Rectangle((xx,yy-1.0),3.8,2.0,fc=CH[t] if on else "white",ec=MUT if not on else INK,lw=.5 if not on else .8))
            ax.text(xx+1.9,yy,lab,fontsize=5.4,ha="center",va="center",color="white" if (on and t>=2) else (INK if on else "#9ca3af"))
    y-=2.4+len(names)*2.3+.5
ax.text(0.5,0.9,"L = Low (1), M = Medium (2), H = High (3)",fontsize=5.6,color=MUT,style="italic")
# (b) bands -> ratings
head(37.5,49.0,2,"Rule band $\\to$ rating")
xs=44.0; wid=20.5; sc=lambda v:xs+(v-1)/9*wid
rows=[("D","$\\geq$3 High in IEF",E["bands"]["D"],E["points"]["D"],(1,4),(5,7),(8,10)),("A","scope/cascading High",E["bands"]["A"],E["points"]["A"],(1,4),(5,7),(8,10)),
      ("R","automation + maturity High",E["bands"]["R"],E["points"]["R"],(1,4),(5,7),(8,10)),("E","exposure High, tools Med.",E["bands"]["E"],E["points"]["E"],(1,4),(5,7),(8,10)),
      ("D$_2$","interface Med., sum 8",E["bands"]["D2"],E["points"]["D2"],(1,3),(4,6),(7,10))]
ycs=[43.4,37.3,31.2,25.1,19.0]
for (nm,why,bd,pt,lo,mi,hi),yc in zip(rows,ycs):
    ax.text(38.0,yc+.4,nm,fontsize=7,fontweight="bold",color=INK,va="center")
    for (a,b),c,k in zip((lo,mi,hi),("#EEF2F7","#DCE9F6","#C3D9EE"),"LMH"):
        on=(bd==k)
        ax.add_patch(Rectangle((sc(a)-wid/18,yc-1.6),(b-a+1)*wid/9,3.2,fc=("#74A9D8" if on else c),ec="white",lw=.8))
    ax.add_patch(Circle((sc(pt),yc),1.15,fc=INK,ec="white",lw=.7,zorder=5)); ax.text(xs+wid+wid/18+.9,yc,f"= {pt}",fontsize=6.6,ha="left",va="center",fontweight="bold",color=INK)
    ax.text(xs-wid/18,yc-3.0,why,fontsize=5.3,color=MUT,va="center",style="italic")
for v in (1,5,10): ax.text(sc(v),13.9,str(v),fontsize=5.4,ha="center",color=MUT)
ax.text(38.0,10.6,"S",fontsize=7,fontweight="bold",color=INK,va="center"); ax.text(xs-wid/18,10.6,"4  (SAIL / ARA class, external input)",fontsize=5.8,color=INK,va="center")
ax.text(xs-wid/18,7.6,"shaded: band selected by rule; dot: recorded rating",fontsize=5.4,color=MUT,style="italic",va="center")
ax.text(38.0,4.4,"$I=4.07$,  $L=3.67$,  DREAD-S $=3.87$ (sum of D–D$_2$ = 37)",fontsize=6.2,color=INK,va="center")
ax.text(38.0,1.2,"DREAD-S band: High (3.4–4.2]",fontsize=6.2,color=INK,va="center")
# (c) matrix
head(71.0,49.0,3,"SecRAM cell")
cw,ch=4.5,5.5; mx,my=77.0,10.0
matrix(ax,mx,my,cw,ch,hi=(4,4),box=((3,4),(4,5)),fs=5.8)
shares={(4,5):136,(3,5):80,(4,4):17,(3,4):10}
for (l,i),n in shares.items():
    if (l,i)!=(4,4): ax.text(mx+(l-.5)*cw,my+(i-.5)*ch-1.3,f"{n}/243",fontsize=5.4,ha="center",va="center",color=INK)
ax.text(mx+3.5*cw,my+3.5*ch+.9,"$\\bigstar$",fontsize=9,ha="center",va="center",color="white",zorder=7)
ax.text(mx+3.5*cw,my+3.5*ch-1.5,"17/243",fontsize=5.4,ha="center",va="center",color="white",zorder=7)
ax.text(mx+2.5*cw,my-ch*.5-2.2,"likelihood level $\\lambda(L)$",fontsize=6.2,ha="center",va="center",color=INK)
ax.text(mx-cw*.95,my+2.5*ch,"impact level $\\lambda(I)$",fontsize=6.2,ha="center",va="center",rotation=90,color=INK)
ax.text(mx+2.5*cw,my+5*ch+1.8,"dashed: cells reachable within the rule bands",fontsize=5.4,ha="center",va="center",color=MUT,style="italic")
ax.text(mx+2.5*cw,my+5*ch+4.0,"star: recorded ratings, cell (4, 4) = (High, High)",fontsize=5.4,ha="center",va="center",color=MUT,style="italic")
fig.savefig("fig/figB_example.pdf",bbox_inches="tight",pad_inches=.03); fig.savefig("fig/figB_example.png",dpi=170,bbox_inches="tight",pad_inches=.03); plt.close(fig)
print("B done")

# ================= Fig C: catalogue in the SecRAM matrix =================
from collections import defaultdict, Counter
cat=F["cat"]
fig=plt.figure(figsize=(7.0,3.55)); gs=fig.add_gridspec(1,2,width_ratios=[1.45,1.0],wspace=.16,left=.075,right=.995,top=.9,bottom=.14)
a=fig.add_subplot(gs[0]); b=fig.add_subplot(gs[1])
EDG=[1.0,1.8,2.6,3.4,4.2,5.0]; XL=(2.25,4.4); YL=(2.45,5.0)
for l in range(1,6):
    for i in range(1,6):
        a.add_patch(Rectangle((EDG[l-1],EDG[i-1]),EDG[l]-EDG[l-1],EDG[i]-EDG[i-1],fc=SEV[cls(l,i)],ec="white",lw=1.0,zorder=0))
a.set_xlim(*XL); a.set_ylim(*YL)
ctr=[(EDG[k]+EDG[k+1])/2 for k in range(5)]
ctr_x=[max(c,XL[0]+.12) if k==1 else c for k,c in enumerate(ctr)]
a.set_xticks([c for k,c in enumerate(ctr) if XL[0]<c<XL[1]]); a.set_xticklabels([str(k+1) for k,c in enumerate(ctr) if XL[0]<c<XL[1]],fontsize=6.4)
a.set_yticks([c for k,c in enumerate(ctr) if YL[0]<c<YL[1]]); a.set_yticklabels([str(k+1) for k,c in enumerate(ctr) if YL[0]<c<YL[1]],fontsize=6.4)
for t in EDG[1:-1]:
    a.axvline(t,color="white",lw=1.0,zorder=1); a.axhline(t,color="white",lw=1.0,zorder=1)
a.set_xlabel("likelihood level $\\lambda(L)$  (axis: $L$, truncated)",fontsize=6.8); a.set_ylabel("impact level $\\lambda(I)$  (axis: $I$, truncated)",fontsize=6.8)
a.tick_params(length=0,pad=2)
for sp in a.spines.values(): sp.set_visible(False)
grp=defaultdict(list)
for c in cat: grp[(round(c["L"],3),round(c["I"],3))].append(c)
for (l,i),cs in grp.items():
    c=cs[0]; mv=[x for x in cs if (x["lL"],x["lI"])!=(x["lLa"],x["lIa"])]
    for x in mv:
        a.add_patch(FancyArrowPatch((x["L"],x["I"]),(x["La"],x["Ia"]),arrowstyle="-|>",mutation_scale=5,lw=.6,color=INK,shrinkA=2.2,shrinkB=1.5,zorder=3,alpha=.8))
        a.scatter(x["La"],x["Ia"],s=11,marker="o",fc=EVC[x["ev"]],ec=INK,lw=.5,zorder=4,hatch="////" if x["ev"]=="None" else None,alpha=.95)
    for x in cs[:1]:
        pass
    a.scatter(l,i,s=24,marker="o",fc=EVC[c["ev"]],ec=INK,lw=.7,zorder=5,hatch="////" if c["ev"]=="None" else None)
# labels
lab={ (3.963,4.852):("INF-02",(.04,.0),"left"),(3.963,4.556):("DAT-02",(.04,-.02),"left"),(3.519,4.852):("INF-07",(-.04,.0),"right"),
      (4.111,4.222):("SVC-02, DAT-06",(.04,.07),"left"),(3.667,4.556):("SVC-03",(-.04,.0),"right"),(3.963,4.222):("DAT-01",(.0,-.1),"center"),
      (3.667,4.074):("SVC-04",(-.04,.0),"right"),(3.519,4.222):("INF-01",(-.04,.04),"right"),(3.815,3.741):("SVC-01, DAT-05",(.04,.02),"left"),
      (3.667,3.778):("INF-05",(.03,.10),"left"),(3.222,4.074):("INF-03",(-.04,.0),"right"),(3.519,3.741):("DAT-04",(-.04,.0),"right"),
      (3.519,3.444):("SVC-05",(.04,-.07),"left"),(3.370,3.444):("DAT-03",(-.04,.0),"right"),(2.630,3.741):("INF-06",(.05,.0),"left"),(2.481,3.741):("INF-04",(-.04,.0),"right")}
for (l,i),cs in grp.items():
    k=(round(l,3),round(i,3))
    if k in lab:
        t,(dx,dy),ha=lab[k]; a.text(l+dx,i+dy,t,fontsize=5.1,ha=ha,va="center",color=INK,zorder=6)
    else: a.text(l+.05,i-.0,"/".join(x["id"] for x in cs),fontsize=5.1,ha="left",va="center",color=INK,zorder=6)
a.set_title("(a) Catalogue in the impact–likelihood plane; arrows: EWTS moves a cell",fontsize=7,loc="left",fontweight="bold",pad=4)
h=[plt.Line2D([],[],marker="o",ls="",mfc=EVC[k] if k!="None" else "white",mec=INK,ms=4,label=k) for k in ["Strong","Moderate","Weak","None"]]
a.legend(handles=h,fontsize=5.6,title="Evidence",title_fontsize=5.8,loc="upper left",frameon=True,facecolor="white",edgecolor="none",framealpha=.9,ncol=2,columnspacing=.8,handletextpad=.2)
# (b) count matrices
b.set_xlim(0,21.5); b.set_ylim(-3.2,13.2); b.axis("off")
def counts(x0,key):
    cn=Counter((c[key[0]],c[key[1]]) for c in cat)
    cw=3.6; ch=1.9
    for l in range(1,6):
        for i in range(1,6):
            b.add_patch(Rectangle((x0+(l-1)*cw,(i-1)*ch+.2),cw,ch,fc=SEV[cls(l,i)],ec="white",lw=.8))
            n=cn.get((l,i),0)
            if n: b.text(x0+(l-.5)*cw,(i-.5)*ch+.2,str(n),fontsize=7.2,fontweight="bold",ha="center",va="center",color=INK)
    for k in range(1,6): b.text(x0+(k-.5)*cw,-.5,str(k),fontsize=6.2,ha="center",va="center",color=INK)
    return cn
c0=counts(1.8,("lL","lI")); c1=counts(1.8,("lL","lI"))
b.cla(); b.set_xlim(0,40); b.set_ylim(-3.2,13.2); b.axis("off")
def counts2(x0,key,title):
    cn=Counter((c[key[0]],c[key[1]]) for c in cat); cw,ch=3.3,1.9
    for l in range(1,6):
        for i in range(1,6):
            b.add_patch(Rectangle((x0+(l-1)*cw,(i-1)*ch+.2),cw,ch,fc=SEV[cls(l,i)],ec="white",lw=.8))
            n=cn.get((l,i),0)
            if n: b.text(x0+(l-.5)*cw,(i-.5)*ch+.2,str(n),fontsize=7.4,fontweight="bold",ha="center",va="center",color=INK)
    for k in range(1,6): b.text(x0+(k-.5)*cw,-.55,str(k),fontsize=6.2,ha="center",va="center",color=INK)
    b.text(x0+2.5*cw,-2.2,"likelihood level",fontsize=6.2,ha="center",va="center",color=INK)
    b.text(x0+2.5*cw,10.2,title,fontsize=6.8,ha="center",va="center",color=INK,fontweight="bold")
counts2(2.2,("lL","lI"),"before: $(\\lambda(L),\\lambda(I))$"); counts2(22.0,("lLa","lIa"),"after EWTS: $(\\lambda(\\tilde L),\\lambda(\\tilde I))$")
for k in range(1,6): b.text(1.3,(k-.5)*1.9+.2,str(k),fontsize=6.2,ha="center",va="center",color=INK)
b.text(-.1,4.7,"impact level",fontsize=6.2,rotation=90,ha="center",va="center",color=INK)
b.text(0.0,11.6,"(b) Assets per SecRAM 2.0 cell",fontsize=7,fontweight="bold",ha="left",va="center",color=INK)
fig.savefig("fig/figC_matrix.pdf",bbox_inches="tight",pad_inches=.03); fig.savefig("fig/figC_matrix.png",dpi=170,bbox_inches="tight",pad_inches=.03); plt.close(fig)
print("C done")
