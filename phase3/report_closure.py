"""Tabla de auditoría y resultados finales desde los JSON de las corridas."""
import json
from pathlib import Path
import numpy as np
from audit_series import half_discrepancy

ROOT=Path(__file__).resolve().parent
THERMAL=ROOT/"data"/"f58f237895157d1b"/"summary.json"
STUDY=ROOT/"study_closure.json"
FOLLOWUP=ROOT/"data"/"7837d0146dbd1097"/"summary.json"


def max_split_cycle_discrepancy(run_id, beta_index):
    values=[]
    for replica in range(3):
        path=ROOT/"data"/run_id/f"N3_beta{beta_index}_replica{replica}.npz"
        with np.load(path) as raw:
            value=half_discrepancy(raw["class_flags"][:, -1])
            if value is not None:values.append(value)
    return max(values)


def main():
    thermal=json.loads(THERMAL.read_text())
    study=json.loads(STUDY.read_text())
    followup=json.loads(FOLLOWUP.read_text())["results"][0]
    short_split=max_split_cycle_discrepancy("f58f237895157d1b",1)
    long_split=max_split_cycle_discrepancy("7837d0146dbd1097",0)
    lines=[
        "# Auditoría cuantitativa del cierre de Fase 3",
        "",
        "Los valores de esta página se generan de los resúmenes guardados, sin editar cifras a mano.",
        f"Barrido térmico: `{thermal['run_id']}`. Estudio de P y coste: `study_closure.json`.",
        "",
        "## Barrido térmico y normalización",
        "",
        "| N | β | clases resueltas | máximo residuo resuelto | Z_MC/Z_ocup | residuo Z | ESS energía/s |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in thermal["results"]:
        residuals=[abs(a-b)/e for a,b,e,ok in zip(
            r["class_mc"],r["class_exact"],r["class_error"],r["class_resolved"])
            if ok and e>0]
        zsig=(r["z_mc"]-r["z_exact"])/r["z_error"]
        lines.append(f"| {r['N']} | {r['beta']:g} | {sum(r['class_resolved'])}/{len(r['classes'])} | "
                     f"{max(residuals):.2f}σ | {r['z_mc']/r['z_exact']:.4f} | "
                     f"{zsig:+.2f}σ | {r['energy_ess_per_second']:.1f} |")
    lines+=["","En β=0.1, las clases de ciclo más largo no alcanzaron el umbral de 20 "
            "apariciones por réplica; sus puntos se muestran como exploratorios. "
            "La prueba independiente del factor 1/N! procede del producto de ocupaciones "
            "y de la suma directa de estados de Fock, no de la reconstrucción MC.",
            "",
            "## Corrida de seguimiento para N=3, β=1",
            "",
            f"Una réplica corta mostró una diferencia de {short_split:.2f} errores entre mitades "
            "en el indicador del ciclo de longitud tres. Se repitió el punto con "
            "12000 mediciones y 2000 barridos descartados por cada una de tres cadenas. "
            f"El resultado fue p(3)={followup['class_mc'][-1]:.5f} ± "
            f"{followup['class_error'][-1]:.5f}, frente a "
            f"{followup['class_exact'][-1]:.5f} exacto. "
            f"Z_MC/Z_ocup={followup['z_mc']/followup['z_exact']:.4f}. "
            f"La mayor diferencia entre mitades en esta repetición fue {long_split:.2f} errores. "
            "Los errores de ambas comparaciones incluyen autocorrelación de cada mitad.",
            "",
            "## Dependencia con P","",
            "| N | β | P | ciclo largo MC ± error | exacto | energía MC ± error | ESS energía/s |",
            "|---:|---:|---:|---:|---:|---:|---:|"]
    for r in study:
        if r["mode"]!="global":continue
        j=next(i for i,k in enumerate(r["classes"]) if k==[r["N"]])
        lines.append(f"| {r['N']} | {r['beta']:g} | {r['P']} | "
                     f"{r['class_mc'][j]:.4f} ± {r['class_error'][j]:.4f} | "
                     f"{r['class_exact'][j]:.4f} | "
                     f"{r['energy_mc']:.4f} ± {r['energy_error']:.4f} | "
                     f"{r['energy_ess_per_second']:.1f} |")
    lines+=["","## Actualización global frente a local","",
            "| N | método | ciclo largo MC ± error | ESS energía/s | aceptación de permutación |",
            "|---:|---|---:|---:|---:|"]
    for N in (3,4):
        for mode in ("global","local"):
            candidates=[r for r in study if r["N"]==N and r["beta"]==1.
                        and r["P"]==4 and r["mode"]==mode]
            r=candidates[0]
            j=next(i for i,k in enumerate(r["classes"]) if k==[N])
            accept=np.mean([a["permutation"] for a in r["acceptance"]])
            lines.append(f"| {N} | {mode} | {r['class_mc'][j]:.4f} ± "
                         f"{r['class_error'][j]:.4f} | "
                         f"{r['energy_ess_per_second']:.1f} | {accept:.3f} |")
    (ROOT/"RESULTADOS_CIERRE.md").write_text("\n".join(lines)+"\n")
    print(ROOT/"RESULTADOS_CIERRE.md")


if __name__=="__main__":
    main()
