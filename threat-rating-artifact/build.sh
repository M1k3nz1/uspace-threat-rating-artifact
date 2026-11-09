#!/bin/sh
# regenerates every number, table (tex fragments) and figure used in the paper
set -e
python3 analysis.py >/dev/null
python3 validation.py >/dev/null
python3 framework.py >/dev/null
python3 sensitivity_rules.py >/dev/null
python3 figs.py
python3 figs_new.py
python3 figs_fw.py
(cd rater_study && python3 analyze_raters.py responses/ >/dev/null)
python3 figs_rater.py
(cd rater_study && python3 analyze_secram_native.py responses_C/ >/dev/null)
python3 secram_compare.py >/dev/null
python3 mkmacros.py >/dev/null
echo "done: numbers.tex, *table.tex, *.json and fig/*.pdf regenerated"
