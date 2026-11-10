# Condition C: SecRAM-native assessment (3 models x 3 runs)

Purpose: answer the reviewer objection "no comparison with conventional SecRAM". The LLM raters assess the same 21 assets
using SecRAM 2.0's OWN impact table (7 impact areas, levels 1-5) and likelihood scheme (levels 1-5). The risk level is then
read from the official SecRAM 2.0 matrix by our script. We compare this with the risk level that the framework derives.

## What to do (same as before, 9 new sessions)
1. Open a NEW chat/session for each run. Use the same three models as before: Claude Sonnet 5.5, ChatGPT (GPT-6), Gemini 1.5 Pro.
2. Paste the ENTIRE content of `prompt_C_secram_native.txt` as the first and only message. Do not add anything else.
3. The model must answer with ONE JSON array and nothing else. If it adds text or a code fence, that is fine; if it uses
   curly quotes or cuts the list short, ask it once: "Return the complete JSON array again, straight ASCII quotes, all 21 assets."
4. Save each answer as plain text in `responses_C/` with these exact names:
   claude_C_run1.json, claude_C_run2.json, claude_C_run3.json,
   gpt_C_run1.json, gpt_C_run2.json, gpt_C_run3.json,
   gemini_C_run1.json, gemini_C_run2.json, gemini_C_run3.json
5. Do not edit the values. Do not tell the models about the framework, the catalogue or previous answers.

## Check and analyse
    python3 analyze_secram_native.py responses_C/
Writes `secram_native.json` and `secram_native_report.md`. (Test the pipeline first with `--demo`.)

## What the numbers mean
- Agreement among raters on SecRAM likelihood, impact and risk level (Krippendorff alpha, raw share).
- Native SecRAM level vs the framework's level (catalogue-derived and condition A of the same model).
- With most assets High, alpha and kappa can be low even when raw agreement is high; the paper reports raw agreement too.
