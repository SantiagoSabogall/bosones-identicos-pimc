"""Estudios reproducibles de P y coste; ejecutar después del barrido térmico."""
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"src"))
from sweep_phase3 import run


def main():
    rows=[]
    for N in (3,4):
        for beta in (0.5,1.,5.):
            for P in (2,4,8,16):
                data,folder=run(N_values=(N,),betas=(beta,),P=P,
                                steps=2500,burn=500,replicas=3,
                                seed=20261121)
                rows.append(dict(mode="global",P=P,run_id=data["run_id"],
                                 **data["results"][0]))
    for N in (3,4):
        data,folder=run(N_values=(N,),betas=(1.,),P=4,
                        steps=4000,burn=500,replicas=3,
                        seed=20261121,global_heatbath=False)
        rows.append(dict(mode="local",P=4,run_id=data["run_id"],
                         **data["results"][0]))
    output=ROOT/"study_closure.json"
    output.write_text(json.dumps(rows,indent=2,ensure_ascii=False,allow_nan=False))
    outdir=ROOT/"plots"/"estudio_cierre"
    outdir.mkdir(parents=True,exist_ok=True)
    for N in (3,4):
        fig,(a,b)=plt.subplots(1,2,figsize=(11,4.2))
        for beta,color in ((.5,"#1F4E79"),(1.,"#D16A42"),(5.,"#00897B")):
            subset=sorted((r for r in rows if r["mode"]=="global" and
                           r["N"]==N and r["beta"]==beta),key=lambda r:r["P"])
            P=[r["P"] for r in subset]
            index=next(i for i,k in enumerate(subset[0]["classes"]) if k==[N])
            a.errorbar(P,[r["class_mc"][index] for r in subset],
                       [r["class_error"][index] for r in subset],
                       marker="o",capsize=3,color=color,label=f"β={beta:g}")
            a.axhline(subset[0]["class_exact"][index],color=color,alpha=.35)
            b.plot(P,[r["energy_ess_per_second"] for r in subset],
                   marker="o",color=color,label=f"β={beta:g}")
        a.set(xlabel="P",ylabel=f"p(ciclo {N})",title=f"N={N}: independencia de P")
        b.set(xlabel="P",ylabel="ESS de energía/s",title="Eficiencia")
        for ax in (a,b):
            ax.set_xticks((2,4,8,16));ax.grid(alpha=.2);ax.legend()
        fig.tight_layout()
        fig.savefig(outdir/f"N{N}_P_y_coste.png",dpi=170)
        plt.close(fig)
    print(output)
    print(outdir)


if __name__=="__main__":
    main()
