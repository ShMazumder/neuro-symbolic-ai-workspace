This third iteration (**`poster (3).pdf`**) is **camera-ready and submission-grade**. Every major theoretical, statistical, and presentation vulnerability from the previous two rounds has been cleanly neutralized.

### 1. Final Verification of Your Fixes

* **Constrained Decoding Formulation (Box 4 & Box 9):** Replacing the flawed metric-distance fallback with constrained logit decoding—$\arg\max_{c \in V} P_{\text{neural}}(c)$ (masking inadmissible transition logits)—is mathematically sound and aligns with the Box 9 Savar Garment Strike walkthrough. When `CAMEO 20` is masked out by the $\mathcal{ALC}$ transition gate (`C-ONTO`), the highest remaining probability logit from the neural distribution naturally lands on `CAMEO 14 (Protest/Blockade)`.


* **Framing as a Low-Resource Gold Benchmark (`BD-Conflict-180`):** Naming the dataset **`BD-Conflict-180`** across Boxes 6, 8, and 10 and explicitly positioning the 654 core relational triples as a **"low-resource NeSy benchmark"** turns what would have been a reviewer attack vector (corpus size) into a deliberate, scoped contribution (releasing a human-audited, PROV-O grounded benchmark for low-resource socio-political event extraction).


* **Double-Blind Compliance (Header & Box 10):** Replacing the institutional affiliation header with *"Anonymous Authors — Anonymized for Double-Blind Review"* alongside the anonymized GitHub URL ensures full compliance with ACL/ISWC/NeSy anonymity policies.



---

### 2. Three Micro-Typos to Fix in Your `.tex` Source Before Exporting Final PDF

If you zoom in closely on the vector graphics and text boxes in `poster (3).pdf`, there are **three minor rendering/LaTeX glitches** worth cleaning up before you submit:

1. **Box 4 (`C-ONTO` Math Double-Rendering):**
* Look closely at the `C-ONTO (Hard Gate)` bullet in Box 4: the math expression renders twice right next to each other (`\argmax_{c \in V} ... \arg\max_{c \in V} P_{\text{neural}}(c)`). Check your LaTeX source on that line—you likely left part of the old or duplicate `\argmax` macro inside the inline math `$ ... $` block.




2. **Box 4 (`Dense Neural Fusion` Node in the Diagram):**
* Inside the green box in the architecture flowchart (`Dense Neural Fusion`), the subtitle text has a slight character encoding or math-mode glitch: `BiLSTM + R-GCN (64d)` has a stray symbol orgarbled character right before `BiLSTM`.




3. **Box 8 (`Significant Synergy` Bullet):**
* In the second bullet below the Ablation Table, the false positive reduction now reads `(FP: 4 -> 1, p = 0.0129 McNemar test)` whereas in `poster (2).pdf` it read `(FP: 16 -> 4, p = 0.0129)`. Verify which exact false-positive counts on $n = 191$ yield $p = 0.0129$ under McNemar's test (note: a $16 \rightarrow 4$ discordance gives $p \approx 0.012$, whereas $4 \rightarrow 1$ is too small to reach $p = 0.0129$). Make sure the `16 -> 4` didn't get accidentally overwritten!





---

### 3. Final Verdict & Recommended Submission Order

Once those three micro-typos in the LaTeX source are patched, this work is ready to go out:

1. **Primary Conference Target:** **CASE Workshop @ ACL / EMNLP** (Workshop on Challenges and Applications of Automated Extraction of Socio-political Events from Text) — *Pitch as a full paper introducing both the `BD-Conflict-180` benchmark/ontology and the `C-ONTO` constrained decoding architecture*.


2. **Primary Semantic Web Target:** **ISWC or ESWC (Resource / In-Use Track)** — *Lead with the 28-class OWL 2 `BD-CAMEO` extension, W3C PROV-O sentence grounding, and the 50-query NL2SPARQL benchmark*.


3. **Primary Neuro-Symbolic Target:** **NeSy (International Conference on Neural-Symbolic Learning and Reasoning)** — *Lead with the model-agnostic $\mathcal{ALC}$ Description Logic constraint gating (`Zero-Shot NLI + C-ONTO` and `BiLSTM/R-GCN + C-ONTO`)*.