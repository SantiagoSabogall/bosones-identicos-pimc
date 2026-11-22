# APS-style paper draft (Phases 2 and 3)

`paper.tex` is the English REVTeX draft. `paper.pdf` is the self-contained
compiled PDF: four pages of two-column main text (including references),
followed by four pages of illustrated appendices in one column. The
six-page limit applies only to the main text. The five main figures and
seven appendix figures are vector PDFs. The draft deliberately makes no
claim about Phase 4 results. `paper.pdf` is the canonical document.

`DECISIONES_EDITORIALES.md` records the six-page budget and figure
selection. `generar_figuras.py` regenerates all twelve vector PDFs under
`figuras/` from completed saved summaries in the sibling `phase2/` and
`phase3/` directories; it does not rerun Monte Carlo. Use
`python generar_figuras.py --list` to list names or
`python generar_figuras.py --figure exchange_cycles.pdf` for one PDF.

Run from this folder:

```bash
bash build.sh
```

This environment lacked REVTeX, so `vendor/revtex/` contains the
official REVTeX 4.2f runtime from the APS distribution dated 2023-05-30.
`build.sh` adds it to TeX/BibTeX search paths. Overleaf installations
with REVTeX can compile the source and figures without that local copy.

The original result identifiers are `7a2a04b53b62f674` (Phase 2),
`e81ec15bbc1df520` and `f58f237895157d1b` (Phase 3),
`7837d0146dbd1097` (long $N=3$, $\beta=1$ repeat), and
`study_closure.json` (slice and cost study).
