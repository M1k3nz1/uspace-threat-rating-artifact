# Evidence-Weighted Threat Rating for U-Space: Reproducibility Artifact

Artifact accompanying the paper on **DREAD-S** threat rating with an **Evidence-Weighted Trust Score (EWTS)**, bridged to the risk matrix of **SESAR SecRAM 2.0**, and applied to a layered U-Space threat catalogue (21 assets).

**One command regenerates every number, table and figure in the paper.**

```bash
pip install -r requirements.txt
sh build.sh          # about a minute; Python only, no LaTeX needed
```

## What the framework does

1. **DREAD-S.** Six factors (D, R, E, A, D2, S) are rescaled to a 1-5 range and combined into an Impact score `I` and a Likelihood score `L`; `DREAD-S = (I + L) / 2`. Cut-offs at 1.8 / 2.6 / 3.4 / 4.2 give five levels, so each asset sits in a cell `(level(L), level(I))`.
2. **EWTS.** Each rating `r` is pulled toward the neutral value `mu = 3` according to the strength of its supporting evidence: `r~ = mu + w (r - mu)` with `w = 1 / 0.75 / 0.5 / 0.25` for Strong / Moderate / Weak / No evidence. A rule table maps 14 evidence factors (scored 1-3) to these bands. The band-preservation threshold `w* = (tau - mu) / (r - mu)` shows when a rating survives down-weighting.
3. **SecRAM 2.0 bridge.** The cell `(level(L), level(I))` is read against the official SecRAM 2.0 risk matrix (SESAR JU, ed. 02.00.00, 2017, p. 42) to obtain Low / Medium / High risk. Decisions are Act / Verify / Monitor / Defer.

The mapping `level(L) -> SecRAM likelihood`, `level(I) -> SecRAM impact` is an explicit assumption; it differs from SecRAM in impact aggregation (mean vs maximum over areas), likelihood semantics (ease of attack vs chance of success) and risk type (inherent vs residual). The paper quantifies each difference.

## Validation checks reproduced here (V1-V8)

| ID | Check | Where |
|---|---|---|
| V1 | Exhaustive verification of the scoring and EWTS properties | `validation.py` |
| V2 | Mapping onto the official SecRAM 2.0 matrix | `secram.py`, `secram_compare.py` |
| V3 | Effect of EWTS on cells and risk levels | `framework.py` |
| V4 | Sensitivity analysis (weights, cut-offs, rule thresholds) | `validation.py`, `sensitivity_rules.py` |
| V5 | Premise check with seven LLMs | `validation.py`, `data/llm/` |
| V6 | Worked use case | `framework.py`, `mkmacros.py` (-> `usecase.tex`) |
| V7 | LLM raters on the 14 evidence factors (3 models x 3 runs) | `rater_study/analyze_raters.py` |
| V8 | SecRAM-native baseline vs framework route (condition C) | `rater_study/analyze_secram_native.py` |

## Repository layout

```
.
├── build.sh                    one command: regenerates all numbers, tables, figures
├── requirements.txt            numpy, scipy, matplotlib
├── data/
│   ├── ratings.csv             21 assets: D, R, E, A, D2, S ratings + evidence labels
│   └── llm/ratings_all_runs.csv   seven-LLM runs used in V5
├── analysis.py                 DREAD-S scores, cells, levels
├── framework.py                EWTS, rule table, SecRAM mapping, use case
├── validation.py               V1, V4, V5
├── sensitivity_rules.py        rule-threshold sensitivity
├── secram.py                   official SecRAM 2.0 likelihood x impact matrix
├── secram_compare.py           matrix comparison (V2) and variants
├── figs.py figs_new.py figs_fw.py figs_rater.py   figure scripts -> fig/*.pdf
├── mkmacros.py                 JSON -> LaTeX macros and table fragments
├── fig/                        generated figures (PDF)
├── rater_study/                LLM-rater study (V7, V8)
│   ├── prompt_A_factor_scoring.txt      framework route
│   ├── prompt_B_direct_dread.txt        direct DREAD rating
│   ├── prompt_C_secram_native.txt       SecRAM-native route
│   ├── assets_brief.csv                 asset descriptions given to raters
│   ├── catalogue_ratings.csv            catalogue reference ratings
│   ├── responses/  responses_C/         raw model responses (conditions A and C)
│   ├── make_prompts.py  analyze_raters.py  analyze_secram_native.py
│   └── README_rater_study.md  README_condition_C.md
└── *.json, *.tex               generated results, macros and tables
```

## Outputs

`sh build.sh` writes: `results.json`, `framework.json`, `validation.json`, `rules_sens.json`, `secram.json`, `rater_study/rater_results.json`, `rater_study/secram_native.json` (raw results); `numbers.tex` (every in-text number as a LaTeX macro); `apptable.tex`, `layertable.tex`, `usecase.tex`, `rulesens.tex`, `ratertable.tex` (tables); and `fig/*.pdf` (figures). The committed copies are the ones used in the paper, so the outputs can be diffed against a fresh run.

## LLM-rater study

- **Condition A (framework route):** raters score the 14 evidence factors per asset with the rubric in `prompt_A_factor_scoring.txt`; the rule table turns scores into ratings. **Condition C (SecRAM-native):** raters assign SecRAM impact areas and likelihood directly using `prompt_C_secram_native.txt`.
- Three models from three vendors, three runs each. `responses/NOTES.txt` and `responses_C/NOTES.txt` document the protocol. Responses are stored as returned; only typographic quotes were converted to ASCII.
- To add human assessors, place files named `human<N>_A_run1.json` in `rater_study/responses/` and rerun `python3 analyze_raters.py responses/` inside `rater_study/`.
- Regenerate the prompts with `python3 make_prompts.py`.

## Related resources

- Threat catalogue (v3.1): <https://github.com/M1k3nz1/uspace-threat-catalogue>
- Evidence register (source register V5): the "Evidence Base Sheet" linked from the paper (view only).
- SESAR Joint Undertaking, *SecRAM 2.0*, edition 02.00.00, 2017 (risk matrix, p. 42).

## Requirements and reproducibility

Python 3 with numpy, scipy and matplotlib (tested with numpy 2.x, scipy 1.18, matplotlib 3.11). Scripts are deterministic; bootstrap seeds are fixed in the code. No network access and no LaTeX installation are needed.

## Citation

Citation details will be added when the paper is published.

## Licence

Code, data and ratings are released under the MIT licence (see `LICENSE`). SecRAM 2.0 is a SESAR JU publication; only the numeric matrix is encoded here, for reproducibility.

## Author

Moiz Abdullah, CISUC, University of Coimbra.
