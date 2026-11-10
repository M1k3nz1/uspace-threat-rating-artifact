#!/usr/bin/env python3
"""Builds prompt_A_factor_scoring.txt and prompt_B_direct_dread.txt from assets_brief.csv."""
import csv
rows=list(csv.DictReader(open("assets_brief.csv")))
def brief(r):
    cve={"DIRECT":f"{r['cve_count']} CVE record(s) in UAS/U-Space/GNSS products","REPRESENTATIVE":f"{r['cve_count']} CVE record(s) in the same technology class (not this exact product)","NONE":"no CVE applicable"}[r["cve_basis"]]
    return (f"[{r['id']}] {r['asset']} ({r['layer']} layer)\n"
      f"  Attack types: {r['attack_types']}\n  Attack vectors: {r['attack_vectors']}\n  Weaknesses: {r['vulnerabilities']}\n"
      f"  Threat scenario: {r['threat_scenario']}\n  Potential damage: {r['potential_damage']}\n  Affected parts: {r['affected_parts']}\n"
      f"  Cross-layer propagation: {r['propagation']}\n  Regulation: {r['regulation']}\n  Cited sources: {r['references']}\n  Vulnerability records: {cve}\n")
ASSETS="\n".join(brief(r) for r in rows)
COMMON="""You are an experienced security risk assessor for U-Space (the EU framework for unmanned-aircraft traffic management). You will assess {n} architectural assets of a U-Space system. Each asset has a short brief. Use ONLY the brief and your general domain knowledge. You are NOT given, and must NOT try to recall, any risk score from any catalogue or paper. Rate every asset independently on the same scale; do not force a spread and do not rank the assets against each other.
"""
A=COMMON.format(n=len(rows))+"""
TASK. For each asset, score the 14 evidence factors below as 1 (Low), 2 (Medium) or 3 (High). Orientation: a higher score ALWAYS means a higher resulting risk rating. Also give the safety rating S (integer 1-5).

IMPACT EVIDENCE FACTORS
 safety      : 1 = no safety consequence; 2 = degrades separation, situational awareness or a safety barrier but no direct collision path; 3 = could plausibly contribute to loss of an aircraft, collision or harm to people.
 scope       : 1 = single UAV or single operator; 2 = several operators or one service area; 3 = fleet-wide or the whole U-Space airspace.
 regulatory  : 1 = little regulatory consequence; 2 = indirect consequence for compliance; 3 = breach of mandatory EU U-Space / EASA / Part-IS obligations with certification or legal consequence.
 cascading   : 1 = isolated to the asset; 2 = spreads to several components in one layer; 3 = propagates across two or more layers (see the propagation field).
 recovery    : 1 = quick, automatic or trivial recovery; 2 = hours of manual effort or partial loss; 3 = hard to recover (integrity loss that is hard to detect, hardware replacement, long manual fallback).
LIKELIHOOD EVIDENCE FACTORS
 exposure    : 1 = internal or physically restricted; 2 = partner / authenticated network; 3 = publicly reachable (internet or open radio interface).
 access      : 1 = needs privileged or physical access; 2 = needs a valid account or radio proximity; 3 = no or low barrier (remote, unauthenticated).
 maturity    : 1 = theoretical only; 2 = demonstrated in research or simulation; 3 = documented in the wild or public proof of concept.
 tools       : 1 = custom development needed; 2 = existing tools need specialist adaptation; 3 = freely available, ready-to-use tools.
 automation  : 1 = manual, one-off effort; 2 = partly scriptable; 3 = fully scriptable and repeatable at scale.
VISIBILITY EVIDENCE FACTORS
 documentation : 1 = proprietary or undocumented; 2 = partly documented; 3 = publicly documented specifications.
 interface     : 1 = opaque interfaces; 2 = partly transparent; 3 = public and transparent interfaces.
 complexity    : 1 = complex, hard to find weaknesses; 2 = moderate; 3 = simple, easy to understand and probe.
 monitoring    : 1 = strong monitoring and detection; 2 = partial; 3 = effectively no monitoring (flaws stay unnoticed).
SAFETY RATING S: 1 = none (SAIL I); 2 = minor; 3 = moderate (SAIL III); 4 = serious (SAIL IV); 5 = catastrophic (SAIL V-VI).

OUTPUT. Reply with ONE JSON array and nothing else (no markdown fence, no commentary). One object per asset, in the order given, exactly this shape:
{"id":"<asset id>","safety":n,"scope":n,"regulatory":n,"cascading":n,"recovery":n,"exposure":n,"access":n,"maturity":n,"tools":n,"automation":n,"documentation":n,"interface":n,"complexity":n,"monitoring":n,"S":n,"why":"<=20 words"}
All values except id and why are integers.

ASSETS
"""+ASSETS
B=COMMON.format(n=len(rows))+"""
TASK. For each asset give five DREAD ratings, each an integer 1-10, plus the safety rating S (integer 1-5).
 D  Damage potential          1 = negligible ... 10 = catastrophic
 R  Reproducibility           1 = very hard to repeat ... 10 = trivial to repeat
 E  Exploitability            1 = very hard to launch ... 10 = trivial to launch
 A  Affected assets / users   1 = very few ... 10 = all
 D2 Discoverability           1 = hidden ... 10 = obvious
 S  Safety impact             1 = none (SAIL I), 2 = minor, 3 = moderate (SAIL III), 4 = serious (SAIL IV), 5 = catastrophic (SAIL V-VI)

OUTPUT. Reply with ONE JSON array and nothing else (no markdown fence, no commentary). One object per asset, in the order given:
{"id":"<asset id>","D":n,"R":n,"E":n,"A":n,"D2":n,"S":n,"why":"<=20 words"}

ASSETS
"""+ASSETS
open("prompt_A_factor_scoring.txt","w").write(A); open("prompt_B_direct_dread.txt","w").write(B)
C=COMMON.format(n=len(rows))+"""
TASK. Assess each asset with the SESAR SecRAM 2.0 method. For the threat scenario in the brief, assume the weaknesses listed are present and that no controls beyond those described are in place. Give (1) an impact level for EACH of the seven SecRAM impact areas, on the 1-5 scale of SecRAM Table 1 (worst credible outcome of a successful attack, over confidentiality, integrity and availability), and (2) a likelihood level 1-5 from the SecRAM likelihood scheme. Do not compute the final risk level; it will be read from the SecRAM matrix afterwards.

SECRAM IMPACT SCALE (Table 1, primary-asset impact assessment). Levels: 5 Catastrophic, 4 Critical, 3 Severe, 2 Minor, 1 No impact / NA.
 people      : 5 = fatalities; 4 = multiple severe injuries; 3 = severe injuries; 2 = minor injuries; 1 = no injuries.
 capacity    : 5 = loss of 60-100% of capacity; 4 = loss of 30-60%; 3 = loss of 10-30%; 2 = loss of up to 10%; 1 = no capacity loss.
 performance : 5 = major quality abuse that makes multiple major systems inoperable; 4 = major quality abuse that makes a major system inoperable; 3 = severe quality abuse that makes systems partially inoperable; 2 = minor system quality abuse; 1 = no quality abuse.
 economic    : 5 = bankruptcy or loss of all income; 4 = serious loss of income; 3 = large loss of income; 2 = minor loss of income or increased expenses; 1 = no effect.
 branding    : 5 = government and international attention; 4 = national attention; 3 = complaints and local attention; 2 = minor complaints; 1 = no impact.
 regulatory  : 5 = multiple major regulatory infractions; 4 = a major regulatory infraction; 3 = multiple minor regulatory infractions; 2 = a minor regulatory infraction; 1 = no impact.
 environment : 5 = widespread or catastrophic impact on the environment; 4 = severe pollution with long-term impact; 3 = severe pollution with noticeable impact; 2 = short-term impact on the environment; 1 = insignificant.

SECRAM LIKELIHOOD SCHEME (Table 4; the value is the chance that the scenario successfully occurs, considering exposure, attractiveness of the target, history of such threats and the probability that an attack succeeds; "lifetime of the project" means the operational deployment of the U-Space service):
 L = 5 : a high chance that the scenario successfully occurs in the short term.
 L = 4 : a high chance that the scenario successfully occurs in the medium term.
 L = 3 : a high chance that the scenario successfully occurs during the lifetime of the project.
 L = 2 : a low chance that the scenario successfully occurs during the lifetime of the project.
 L = 1 : very little or no chance that the scenario successfully occurs during the lifetime of the project.

OUTPUT. Reply with ONE JSON array and nothing else (no markdown fence, no commentary). Use straight ASCII double quotes only. One object per asset, in the order given, exactly this shape:
{"id":"<asset id>","people":n,"capacity":n,"performance":n,"economic":n,"branding":n,"regulatory":n,"environment":n,"L":n,"why":"<=20 words"}
All values except id and why are integers from 1 to 5.

ASSETS
"""+ASSETS
open("prompt_C_secram_native.txt","w").write(C)

print(len(A.split()),len(B.split()))
