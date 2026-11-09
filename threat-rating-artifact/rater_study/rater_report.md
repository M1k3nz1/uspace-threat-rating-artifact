# Rater-study results (auto-generated)

## Condition A: evidence-factor scoring -> rule engine
Models: claude, gemini, gpt; runs per model: {'claude': 3, 'gemini': 3, 'gpt': 3}

### Krippendorff alpha (ordinal) on the evidence factors

| group | all runs | model medians |
|---|---|---|
| IEF | 0.67 | 0.65 |
| LEF | 0.63 | 0.64 |
| VEF | 0.43 | 0.36 |
| all14 | 0.60 | 0.58 |

| factor | all runs | model medians |
|---|---|---|
| safety | 0.79 | 0.76 |
| scope | 0.61 | 0.59 |
| regulatory | 0.55 | 0.58 |
| cascading | 0.61 | 0.61 |
| recovery | 0.64 | 0.55 |
| exposure | 0.66 | 0.59 |
| access | 0.59 | 0.59 |
| maturity | 0.43 | 0.41 |
| tools | 0.60 | 0.77 |
| automation | 0.66 | 0.69 |
| documentation | 0.48 | 0.49 |
| interface | 0.68 | 0.73 |
| complexity | 0.01 | -0.30 |
| monitoring | 0.14 | 0.05 |
| S | 0.81 | 0.85 |

Alpha on derived rating bands: D 0.64, A 0.64, R 0.59, E 0.67, D2 0.67


Kendall's W across models (DREAD-S rank): W=0.94, p=2.45e-05

Pairwise Kendall tau: claude-gemini 0.79, claude-gpt 0.80, gemini-gpt 0.73

### Agreement with the catalogue

| model | tau | rho | cell exact | cell within 1 | band exact | band weighted kappa | mean bias |
|---|---|---|---|---|---|---|---|
| claude | 0.53 | 0.72 | 0.14 | 0.95 | 0.57 | 0.59 | -0.10 |
| gemini | 0.60 | 0.82 | 0.29 | 0.95 | 0.57 | 0.64 | -0.09 |
| gpt | 0.59 | 0.75 | 0.14 | 1.00 | 0.48 | 0.49 | +0.15 |

Ensemble mean vs catalogue: tau=0.58, rho=0.78

Cross-model: all models in the same cell for 0.10 of assets; same band 0.52; all pairs within one level 0.81.

Within-model run stability (alpha over the 14 factors): claude 0.87, gemini 0.61, gpt 0.79

### EWTS premise (does disagreement fall with evidence weight?)
Between-model SD vs w: rho=0.16, p=0.485. Gap to catalogue vs w: rho=-0.16, p=0.482. Median SD Strong/Moderate 0.256 vs Weak/None 0.165.
