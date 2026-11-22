# Editorial plan for the six-page paper

## Decisions fixed for the current draft

1. **Language and format.** English, REVTeX 4.2f with
   `\documentclass[aps,pra,reprint,floatfix]{revtex4-2}` and two columns. The
   `pra` option is a style choice suited to a quantum-mechanics topic;
   this course manuscript is not represented as an APS submission.
2. **Page cap.** Six pages for the main article, including references.
   Illustrated appendices follow the bibliography in the same PDF and
   are outside that cap. The current main article has four pages;
   appendices occupy pages 5--8. Approximately two main-text pages remain
   for Phase 4 and final revision. Recheck the main-text page count after
   every substantive edit.
3. **Narrative.** The main claim is an exact small-system benchmark for
   exchange cycles, followed by a controlled change of *external*
   confinement. The title and abstract remain provisional until the
   Phase 4 results exist. No boson-boson interaction or condensation
   transition is claimed.
4. **Main figures.** Five vector-PDF figures are included:
   `exchange_cycles.pdf` (full-cycle probabilities for $N=2,3,4$),
   `partition_check.pdf` (independent normalization),
   `energy_control.pdf` (two-panel thermal energy),
   `class_probabilities_N4.pdf` (all five $N=4$ classes), and
   `p_convergence.pdf` (two-panel slice check). The first, second and
   fourth occupy one REVTeX column; the third and fifth span two.
5. **Figures after the bibliography.** Appendix A contains
   `worldline_topology.pdf`, `phase2_partition_ratio.pdf`, and
   `phase2_energy.pdf`; Appendix B contains
   `class_probabilities_N3.pdf`, `class_histograms.pdf`, and
   `particle_cycle_fractions.pdf`; Appendix C contains
   `sampling_cost.pdf`. They retain the full diagnostic record without
   consuming the six-page main-text allowance. Each is cited and
   interpreted in the appendix text, and each caption states the exact
   reference, Monte Carlo sampling, and relevant statistical limits.
   Historical PNGs remain in the phase folders as raw project artifacts.
6. **Graphics standard.** A reproducible Python script uses Seaborn's
   `paper` context, readable labels at column width, color plus line and
   marker distinctions, embedded TrueType fonts, and no axes titles.
   Each figure's physical meaning and sample convention belong in its
   LaTeX caption. The same standard applies to main and appendix figures.
7. **Provenance.** The figures read only saved summary files. The $N=3$,
   $\beta\hbar\omega=1$ short closure point is replaced by the longer
   diagnostic repeat; high-temperature full cycles that fail the class
   resolution threshold are omitted as Monte Carlo points.

## Space reserved for Phase 4

| Part of final main text | Estimated space |
|---|---:|
| Completed Phase 2/3 text, figures and references | 4 pages in the present draft |
| New external potential, propagator approximation and spectral reference | approximately 0.75 page |
| Phase 4 results and one compact vector figure | approximately 1 page |
| Revision of joint discussion, abstract and conclusions | within remaining space |
| **Final maximum** | **6 pages** |

The expanded Phase 2/3 layout leaves a tight two-page margin. If Phase 4
needs more than one main figure, move the $P$ figure or the detailed
$N=4$ class figure to the appendices rather than shrinking labels.
The manual page break before the present conclusion is a draft layout aid
and must be removed after inserting the Phase 4 section.

The proposed Phase 4 comparison is a **softened external Yukawa term in
a harmonic trap**, with $g=0$ recovering the present exact control.
The final potential, parameters, spectral-convergence thresholds and
PIMC runs must be fixed before any Phase 4 numerical claim is inserted.
Unlike the harmonic Mehler calculation, that extension will require an
explicit convergence study in imaginary-time slices $P$.

## Submission checks still needed after Phase 4

- Recheck every quantitative statement against saved run IDs and raw data.
- Count main-text pages through the references in the final `reprint` PDF;
  keep appendices after the bibliography in that same PDF.
- Review physical labels, error bars, font embedding, captions and grayscale legibility.
- Update the title, abstract, discussion, bibliography and data availability
  information for the actual final article.
- If submitted to an APS journal rather than only to the course, follow the
  journal's current policies on data availability and AI-tool disclosure.
