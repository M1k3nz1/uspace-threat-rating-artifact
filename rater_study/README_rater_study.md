# Rater study: 4 LLMs as independent experts (VehicleSec '27 paper)

Goal: test whether independent raters agree (a) on the 14 evidence factors, (b) on the DREAD ratings the rules derive from them, and (c) on the final DREAD-S / matrix cell, and how all this compares with the catalogue's expert ratings. Report Krippendorff's alpha, Kendall's W, Kendall tau, weighted kappa, cell agreement.

## Design
- Raters: Gemini, Claude, GPT, Qwen (4 vendors). Each gets the identical prompt; 3 fresh runs each (new chat every time, no memory, default temperature).
- Condition A (main): rater scores the 14 factors + S; the rule engine derives the ratings (so disagreement is measured on observable inputs).
- Condition B (control): rater gives D, R, E, A, D2 directly (as in the TDSC study). A vs B shows whether factor-based elicitation changes agreement.
- Raters never see the catalogue scores. They see the same brief a human assessor would: attack types, vectors, weaknesses, scenario, damage, affected parts, propagation, regulation, cited sources, CVE basis.

## Steps
1. Open `prompt_A_factor_scoring.txt`, copy ALL of it, paste into a NEW chat with model 1. Wait for the JSON array.
2. Save the reply EXACTLY as returned (the script strips a ``` fence) as `responses/<model>_A_run1.json`, with <model> one of `gemini`, `claude`, `gpt`, `qwen`. Open a new chat, paste again, save as `..._A_run2.json`, then run3.
3. Repeat for the other 3 models (12 files for A).
4. Do the same with `prompt_B_direct_dread.txt` -> `responses/<model>_B_run<k>.json` (another 12 files). Condition B is optional but recommended (2 hours total).
5. Record for each chat: exact model name/ID shown by the product, date, web-search/tools on or off (turn them OFF), temperature if you can set it. Put this in `responses/MODELS.txt`.
6. Run: `pip install numpy scipy` then `python3 analyze_raters.py responses/`. It prints validation errors (bad JSON, missing assets, out-of-range values); fix by re-running that chat. It writes `rater_results.json` and `rater_report.md`.
7. Send me `rater_report.md`, `rater_results.json`, `MODELS.txt`; I will add Section "Rater agreement" to the paper, update the validation matrix and abstract.

## Rules for a valid study
- Fresh chat for every run; do not paste previous answers; do not tell the model what other models said.
- Do not edit answers. If JSON is invalid, re-run (keep a note of how many re-runs).
- Use the exact model names that the products report; "Gemini 1.5 Pro", "GPT-6" and "Qwen 3.8 Flash" must match what the interface or API actually says, otherwise the paper must use the real ID.
- Keep tools/web search off so models rate from the brief only.

## How to read the output
- Krippendorff alpha (ordinal): >= 0.80 reliable, 0.667-0.80 tentative, < 0.667 weak. Computed per factor and per group; "model medians" uses each model's median of its 3 runs.
- Kendall's W (0 to 1): agreement of the 4 models on the DREAD-S ranking of the 21 assets.
- vs catalogue: tau/rho of ranks, exact and within-one-level agreement of matrix cells, weighted kappa on the 5 levels.
- Premise test: whether between-model SD falls with evidence weight (the same test as V5, now with factor-level raters).

## Strongly recommended addition
Have 1-2 human assessors (a co-author or a U-space practitioner) score the same 14 factors with prompt A's rubric, and add their files as `human1_A_run1.json`. LLM raters share priors; a human check is what a reviewer will ask for.
