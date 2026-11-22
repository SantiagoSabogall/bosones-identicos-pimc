"""Gráficas de clases y probabilidad de pertenencia a ciclos."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS=['#1F4E79','#D16A42','#00897B','#7E57A6','#78909C']


def make_plots(data,outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    paths=[]
    for N in data['config']['N_values']:
        rows=sorted((r for r in data['results'] if r['N']==N),key=lambda r:r['T'])
        T=np.array([r['T'] for r in rows]); valid=np.array([r['valid'] for r in rows])
        kinds=[tuple(k) for k in rows[0]['classes']]
        for observable,cols,name in [('class',kinds,'clases'),('particle',range(1,N+1),'particulas_en_ciclos')]:
            fig,ax=plt.subplots(figsize=(9,5.5))
            for i,col in enumerate(cols):
                exact=np.array([r[f'{observable}_exact'][i] for r in rows])
                measured=np.array([r[f'{observable}_mc'][i] for r in rows])
                errors=np.array([r[f'{observable}_error'][i] for r in rows])
                color=COLORS[i]
                label=(' + '.join(map(str,col)) if observable=='class' else f'longitud {col}')
                ax.plot(T,exact,color=color,lw=1.8,label=label+' exacta')
                resolved=(np.array([r['class_resolved'][i] for r in rows])
                          if observable=='class' else valid)
                ax.errorbar(T[resolved],measured[resolved],errors[resolved],
                            fmt='o',color=color,capsize=3)
                if (~resolved).any():
                    ax.scatter(T[~resolved],measured[~resolved],marker='x',color=color)
            ax.set_xscale('log');ax.set_ylim(-.03,1.03)
            ax.set_xlabel(r'Temperatura $T=1/\beta$ (unidades $\omega=1$)')
            ax.set_ylabel('Probabilidad de clase' if observable=='class' else 'Probabilidad de una partícula')
            ax.set_title(f'N={N}: '+('tipos de ciclos' if observable=='class' else 'pertenencia a ciclos'))
            ax.grid(alpha=.18);ax.legend(ncol=2,fontsize=9)
            fig.tight_layout()
            path=outdir/f'N{N}_{name}.png';fig.savefig(path,dpi=170);plt.close(fig);paths.append(path)
        # Histograma en beta cercana a 1, con barras exactas y MC.
        row=min(rows,key=lambda r:abs(r['beta']-1.))
        x=np.arange(len(kinds));fig,ax=plt.subplots(figsize=(8,5))
        ax.bar(x-.18,row['class_exact'],width=.36,color='#1F4E79',label='exacta')
        ax.bar(x+.18,row['class_mc'],width=.36,yerr=row['class_error'],color='#D16A42',
               capsize=4,label='Monte Carlo')
        ax.set_xticks(x,['+'.join(map(str,k)) for k in kinds]);ax.set_ylim(0,.65)
        ax.set_ylabel('Probabilidad');ax.set_title(f'N={N}, β={row["beta"]:.3g}: clases de ciclos')
        ax.legend();fig.tight_layout()
        path=outdir/f'N{N}_histograma.png';fig.savefig(path,dpi=170);plt.close(fig);paths.append(path)
        # Energía: dos estimadores de la misma corrida, contrastados con ocupaciones.
        fig,ax=plt.subplots(figsize=(8,5))
        exact=np.array([r['energy_occupation'] for r in rows])
        ax.plot(T,exact,color='#1F4E79',label='exacta (ocupaciones)')
        for key,error,color,label in [('energy_mc','energy_error','#D16A42','termodinámica'),
                                      ('virial_mc','virial_error','#00897B','virial')]:
            ax.errorbar(T,[r[key] for r in rows],[r[error] for r in rows],
                        fmt='o',capsize=3,color=color,label=label)
        ax.set_xscale('log');ax.set_xlabel(r'$T=1/\beta$')
        ax.set_ylabel(r'$E/\hbar\omega$');ax.set_title(f'N={N}: energía')
        ax.grid(alpha=.18);ax.legend();fig.tight_layout()
        path=outdir/f'N{N}_energia.png';fig.savefig(path,dpi=170);plt.close(fig);paths.append(path)
        # Reconstrucción de la función de partición a partir del sector identidad.
        fig,ax=plt.subplots(figsize=(8,5))
        reference=np.array([r['z_exact'] for r in rows])
        ax.plot(T,reference,color='#1F4E79',label='exacta (ocupaciones)')
        good=np.array([r['z_mc'] is not None for r in rows])
        ax.errorbar(T[good],[r['z_mc'] for r in rows if r['z_mc'] is not None],
                    [r['z_error'] for r in rows if r['z_mc'] is not None],
                    fmt='o',capsize=3,color='#D16A42',label='reconstrucción MC')
        ax.set_xscale('log');ax.set_yscale('log')
        ax.set_xlabel(r'$T=1/\beta$');ax.set_ylabel(r'$Z_N$')
        ax.set_title(f'N={N}: función de partición')
        ax.grid(alpha=.18);ax.legend();fig.tight_layout()
        path=outdir/f'N{N}_particion.png';fig.savefig(path,dpi=170);plt.close(fig);paths.append(path)
    return [str(p) for p in paths]
