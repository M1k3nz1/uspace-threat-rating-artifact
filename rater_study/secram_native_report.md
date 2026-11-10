# Condition C: SecRAM-native assessment

Files: 9; models: claude, gemini, gpt

## Agreement among raters (Krippendorff alpha, ordinal)
- Risk level (Low/Medium/High): 0.22
- SecRAM likelihood L: 0.55
- SecRAM impact (max over 7 areas): 0.20
- Impact areas: people 0.63, capacity 0.80, performance 0.77, economic 0.37, branding 0.17, regulatory 0.37, environment 0.31
- Model medians give the same risk level for 43% of assets; all runs for 33%; same cell for 5%

## Risk-level distribution (model medians)
- claude: {'Medium': 3, 'High': 18}
- gemini: {'Medium': 10, 'High': 10, 'Low': 1}
- gpt: {'High': 19, 'Medium': 2}
- catalogue-derived (framework, default mapping): {'Medium': 4, 'High': 17}

## Native vs framework
- Native vs catalogue-derived level, same level: claude 76%, gemini 67%, gpt 81%
- within one level: claude 100%, gemini 95%, gpt 100%
- weighted kappa: claude 0.15, gemini 0.26, gpt 0.24
- Same model, framework route (condition A) vs native route, same level: claude 76%, gemini 67%, gpt 90%
- Native composite vs catalogue DREAD-S ranking: tau 0.60, rho 0.79
- Which area sets the maximum impact (share of run-asset pairs): people 51%, capacity 22%, performance 39%, economic 20%, branding 49%, regulatory 58%, environment 0%

## Route comparison (framework route A vs SecRAM-native route C)
{
 "alpha_framework": {
  "risk": 0.5576688955404945,
  "likelihood": 0.6780810533013243,
  "impact": 0.7143529483039559
 },
 "alpha_native": {
  "risk": 0.2229220971820589,
  "likelihood": 0.5524731374788897,
  "impact": 0.20021527843318188
 },
 "within_model_alpha": {
  "claude": {
   "framework": 0.9001050329056941,
   "native": 0.5772727272727273
  },
  "gemini": {
   "framework": 0.5875102040816327,
   "native": 0.6203094135297524
  },
  "gpt": {
   "framework": 0.7697948575141558,
   "native": 0.5392847197358475
  }
 },
 "pair_same_risk": {
  "framework": 0.7619047619047619,
  "native": 0.6031746031746031
 },
 "models_same_risk_framework": 0.7142857142857143,
 "all_runs_same_risk_framework": 0.5714285714285714,
 "alpha_diff_risk_ci": [
  0.15905253954961374,
  0.4837036337105712,
  1.0
 ],
 "native_mean_impact_alpha": 0.5539036465487687
}
{"claude": {"L": 3.4126984126984126, "impact_max": 4.142857142857143}, "gemini": {"L": 2.984126984126984, "impact_max": 3.5555555555555554}, "gpt": {"L": 3.253968253968254, "impact_max": 4.619047619047619}}
{"L_vs_catL": 0.6822224128909573, "Imax_vs_catI": 0.49700498603932786}

Confusion (rows catalogue-derived Low/Medium/High, columns native, pooled over models):
[[0, 0, 0], [0, 6, 6], [1, 9, 41]]