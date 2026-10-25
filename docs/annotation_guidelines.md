# CAMEO Event Annotation Guidelines: Bangladesh Conflict Monitoring

**Project:** NeuroSym-BD  
**Target Corpora:** National & Regional English/Bengali News Media  
**Benchmark Size:** $N = 300$ Annotated Events  
**Inter-Annotator Agreement:** Multi-class Cohen's $\kappa = 0.737$, High-Violence Binary $\kappa = 0.832$  

---

## 1. Objectives & Scope

This protocol establishes unambiguous coding rules for annotating socio-political conflict events in Bangladesh according to the **Conflict and Mediation Event Observations (CAMEO)** taxonomy (Codes 13 to 20), extended with Bangladesh-specific modalities (hartal, student wing clashes, Section 144 curfews).

---

## 2. CAMEO Conflict Code Taxonomy

| Code | Label | Description & Bangladesh Context | Examples |
| :---: | :--- | :--- | :--- |
| **13** | **Threaten** | Non-physical ultimatum, warning of hartal, blockade threats, political boycott warnings. | *"BNP issued a 48-hour ultimatum demanding unconditional release of activists."* |
| **14** | **Protest** | Peaceful demonstration, human chain, student sit-in, hunger strike, authorized rally. | *"Hundreds of university students staged a peaceful sit-in demanding exam deferral."* |
| **15** | **Force Posture** | Security deployment, military/paramilitary checkpoints, border patrols, show of readiness. | *"RAB and BGB contingents conducted heavy patrols along the highway ahead of elections."* |
| **16** | **Reduce Relations** | Official suspension of talks, severing alliances, diplomatic expulsion, party expulsion. | *"The coalition expelled two dissident members over anti-party statements."* |
| **17** | **Coerce** | Detention, preventive arrests, Section 144 curfew, tear gas, water cannons, police lathi charge. | *"Police fired tear gas shells and detained 40 activists during an unauthorized procession."* |
| **18** | **Assault** | Targeted physical attack, murder, stabbing, hacking, vehicle torched by arsonists, looting. | *"Miscreants stabbed an election candidate with sharp weapons in Narayanganj."* |
| **19** | **Fight** | Bilateral physical clash, gunfight between rival party cadres, factional street brawl. | *"Chhatra League and Chhatra Dal activists clashed wielding iron rods and brickbats."* |
| **20** | **Mass Violence** | Explosive bomb blasts, crude bomb attacks, mob lynching, widespread indiscriminate slaughter. | *"A bag containing 103 crude bombs was detonated near a marketplace."* |

---

## 3. Boundary Dispute Decision Rules

### 3.1 Protest (14) vs. Coerce (17) vs. Fight (19)
- If a protest remains non-violent until police use tear gas or lathi charges to disperse crowds: Code as **17 (Coerce)**.
- If two opposing political factions simultaneously attack each other with weapons/brickbats: Code as **19 (Fight)**.
- If peaceful demonstrators assemble with placards and slogans without physical resistance: Code as **14 (Protest)**.

### 3.2 Assault (18) vs. Fight (19)
- **18 (Assault):** Unilateral, targeted violence against an individual victim, journalist, or property (assassination, arson, robbery).
- **19 (Fight):** Mutual, bilateral physical contest between two identifiable factions (e.g. BNP vs. Awami League cadres).

### 3.3 High-Violence Binary Split
- **High-Violence ($HV = 1$):** Codes **18, 19, 20** (Direct physical injury, lethal force, firearms, arson, explosives).
- **Non-High-Violence ($HV = 0$):** Codes **13, 14, 15, 16, 17** (Threats, peaceful rallies, force posture, institutional coercion).

---

## 4. Empirical Agreement Results ($N = 300$)

Dual independent annotation conducted by two trained annotators:
- **Multi-Class CAMEO Agreement:**
  - Observed Agreement ($P_o$): **77.7%**
  - Expected Agreement ($P_e$): **15.1%**
  - **Cohen's Kappa ($\kappa$):** **0.737** (*Substantial / Near-Perfect Agreement*)
- **High-Violence Binary Agreement ($HV \ge 18$):**
  - Observed Agreement ($P_o$): **92.3%**
  - **Cohen's Kappa ($\kappa$):** **0.832** (*Near-Perfect Agreement*)
- **Actor Entity Span Agreement:** **94.6%**
- **District Geographic Agreement:** **95.4%**

All 67 disputed cases were adjudicated by the senior conflict researcher following Section 3 priority rules.
