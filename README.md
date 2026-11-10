# Threat-rating artifact: DREAD-S, EWTS and the SecRAM 2.0 bridge

Artifact for the paper on DREAD-S threat rating with an Evidence-Weighted Trust Score (EWTS), bridged to the SESAR SecRAM 2.0 risk matrix, applied to a U-space threat catalogue (21 assets).

One command regenerates every number, table and figure of the paper:

    pip install -r requirements.txt
    sh build.sh        # about a minute, python3 only (no LaTeX needed)

Output: `numbers.tex` (all in-text numbers as macros), `apptable.tex`, `layertable.tex`, `usecase.tex`, `rulesens.tex`, `ratertable.tex` (tables), `*.json` (raw results) and `fig/*.pdf` (figures).

## Related resources
- Threat catalogue (v3.1): https://github.com/M1k3nz1/uspace-threat-catalogue
- Evidence register (source register V5): the "Evidence Base Sheet" linked from the paper (view only).
- SecRAM 2.0 matrix: SESAR Joint Undertaking, *SecRAM 2.0* (ed. 02.00.00, 2017), p. 42; encoded in `secram.py`.

## Map: paper section -> script -> data -> output
| Paper part | Script | Input | Output |
|---|---|---|---|
| Ratings, DREAD-S, cells | `analysis.py` | `data/ratings.csv` | `results.json` |
| V1 exhaustive verification, V3 EWTS effect, V4 sensitivity | `validation.py`, `framework.py` | `data/ratings.csv` | `validation.json`, `framework.json` |
| Rule-table sensitivity (14 evidence factors) | `sensitivity_rules.py` | `data/ratings.csv` | `rules_sens.json`, `rulesens.tex` |
| V2 SecRAM 2.0 matrix mapping | `secram.py`, `secram_compare.py` | `framework.json` | `secram.json` |
| V5 seven-LLM premise check | `validation.py` | `data/llm/ratings_all_runs.csv` | `validation.json` |
| V7 LLM raters (factor scoring, 3 models x 3 runs) | `rater_study/analyze_raters.py` | `rater_study/responses/` | `rater_study/rater_results.json`, `rater_report.md` |
| V8 SecRAM-native baseline (condition C) | `rater_study/analyze_secram_native.py` | `rater_study/responses_C/` | `rater_study/secram_native.json`, `secram_native_report.md` |
| Figures | `figs.py`, `figs_new.py`, `figs_fw.py`, `figs_rater.py` | the JSON above | `fig/*.pdf` |
| Macros and tables for LaTeX | `mkmacros.py` | all JSON | `numbers.tex`, `*table.tex` |

## LLM-rater study (prompts and raw responses)
- Prompts: `rater_study/prompt_A_factor_scoring.txt` (framework route), `prompt_B_direct_dread.txt`, `prompt_C_secram_native.txt` (SecRAM-native route). Regenerate with `rater_study/make_prompts.py`.
- Asset descriptions given to the raters: `rater_study/assets_brief.csv`; catalogue reference ratings: `rater_study/catalogue_ratings.csv`.
- Raw model responses: `rater_study/responses/` and `rater_study/responses_C/` (see `NOTES.txt` in each for model names and run protocol). Responses are stored as returned; only typographic quotes were converted to ASCII.
- Details: `rater_study/README_rater_study.md`, `rater_study/README_condition_C.md`.
- Human assessors: add files named `human<N>_A_run1.json` to `rater_study/responses/` and rerun `analyze_raters.py`.

## Notes
- The code is deterministic; random seeds for bootstraps are fixed in the scripts.
- Mapping assumption (stated in the paper): lambda(L) is used as SecRAM likelihood and lambda(I) as SecRAM impact. It differs from SecRAM in impact aggregation (mean vs max), likelihood semantics (ease of attack vs chance of success) and risk type (inherent vs residual).
- Tested with Python 3, numpy 2.x, scipy 1.18, matplotlib 3.11.
