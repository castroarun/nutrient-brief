# Project 13 — Editorial Framework

The rules that make this trustworthy. Every edition must pass all of these.

---

## 1. Source validation

### Paper tier (in order of preference)

**Tier 1 — always acceptable:**
- New England Journal of Medicine (NEJM)
- The Lancet (and Lancet specialty journals)
- JAMA / JAMA Internal Medicine / JAMA Network Open
- BMJ
- Nature / Nature Medicine / Nature Metabolism
- Cell / Cell Metabolism
- Annals of Internal Medicine
- Cochrane Reviews (gold standard for systematic reviews)

**Tier 2 — acceptable with context:**
- American Journal of Clinical Nutrition
- Journal of Nutrition
- European Journal of Nutrition
- Advances in Nutrition
- Gut, Diabetes Care, Hypertension
- PubMed-indexed journals with impact factor >3

**Tier 3 — flag as preliminary:**
- Preprints (bioRxiv, medRxiv) — cite but explicitly label as preprint
- Small trials (n <100) — cite with sample size caveat

**Blacklist:**
- Predatory journals (OMICS, MDPI journals with suspect editorial review — case by case)
- Journals without peer review
- Supplement-company-funded studies *unless* disclosure is explicit and we note it
- In-vitro and animal studies — we can reference but never present as settled

### Study quality checklist (applied by pipeline before cite)

- [ ] Peer-reviewed journal (see tiers above)
- [ ] Sample size noted in our edition if <500
- [ ] Methodology type stated (RCT / observational / meta-analysis / in-vitro)
- [ ] Recency: prefer <5 years; if older, justify why still authoritative
- [ ] Conflict-of-interest disclosure checked; funding source noted if supplement industry
- [ ] Effect size > statistical significance: we report *how much* something changes, not just p-values

---

## 2. Credentialed-doctor rules

A quote is only usable if the source meets *all*:

- **Degree:** MD, DO, PhD in relevant field, or MBBS+MD combination (Indian context).
- **Affiliation:** currently or recently at a reputed teaching hospital, research university, or national medical body. Private-practice "Instagram doctors" without institutional tether are a no.
- **Specialty match:** the doctor's published specialty must align with the topic. A cardiologist on statins: yes. A cardiologist on ashwagandha: no.
- **Track record:** >10 peer-reviewed publications in the specialty area.
- **No product conflict:** doctor isn't a promoter/founder of a supplement brand being discussed (and if they are, we don't quote them on that topic).

### Starter whitelist (Indian + international)

*International:*
- Peter Attia (MD; longevity, metabolic health) — his podcast guests are often citable too
- Rhonda Patrick (PhD; aging, micronutrients)
- Eric Topol (MD; Scripps; cardiology, digital health)
- Walter Willett (MD, DrPH; Harvard School of Public Health; nutrition epidemiology)
- David Sinclair (PhD; Harvard; longevity — with skepticism on his own products)
- Andrew Huberman (PhD; Stanford; neuroscience — only for neuroscience topics, not general nutrition)

*India:*
- Dr. V. Mohan (MDRF; diabetes)
- Dr. Ambrish Mithal (Max Healthcare; endocrinology)
- Dr. Randeep Guleria (ex-AIIMS; pulmonology)
- Dr. Naresh Trehan (Medanta; cardiology)
- Dr. Pramod Tripathi (Freedom from Diabetes — with careful framing)
- Dr. Soumya Swaminathan (ex-WHO; pediatrics, TB)

This list expands as we encounter new authoritative voices. Stored in `research/doctor_registry.md`.

---

## 3. The Memory Anchor method

The "enhanced knowledge" promise depends on readers actually remembering what they read. Every edition closes with a Memory Anchor — a one-line analogy that encodes the mechanism vividly.

### What makes a good anchor

- **Concrete over abstract.** "WD-40 for your joints" > "lubricates joint function."
- **Unexpected.** The best anchors link the unfamiliar (nutrient mechanism) to the familiar (everyday object/image) in a way the reader hasn't heard before.
- **Accurate.** Never sacrifice truth for vividness. If the analogy oversimplifies, it's not usable.
- **Standalone.** The anchor should make sense even if you forgot the rest of the post.

### Examples (seed library)

- *Magnesium:* "Your nervous system's volume knob."
- *Omega-3 (EPA/DHA):* "WD-40 for your cell membranes."
- *Creatine:* "A battery backup for your muscles — not fuel, but reserve charge."
- *Fiber:* "Scaffolding for your gut bacteria's city."
- *Vitamin D3 + K2:* "D3 is the delivery truck, K2 is the address — without K2, calcium ends up in the wrong place."
- *Collagen:* "The scaffolding; protein is the bricks."
- *Caffeine:* "A blocker for your 'I'm tired' receptors — doesn't add energy, just hides the signal."
- *Ashwagandha:* "Dampens the stress volume knob, doesn't turn it off."

The library grows with every edition. A freshness check prevents re-using anchors.

---

## 4. Red-flag topics (extra scrutiny required)

Certain topics carry elevated misinformation risk or regulatory sensitivity. They are *not* off-limits, but require senior-review framing:

- Weight loss / fat loss (huge audience; highest misinformation density)
- Cancer prevention claims (legally sensitive in India under Drugs & Magic Remedies Act)
- Fertility / pregnancy nutrition
- Child nutrition
- Diabetes / hypertension reversal claims
- Immunity-boosting (post-COVID especially loaded)
- Anything involving cannabis / CBD
- Specific branded supplements

For these, the framing rule is: *"Here's what the evidence actually says; here's what it doesn't say; here's what to ask your doctor."* Never "do X."

---

## 5. The editorial principle

One line: **We teach mechanism, not prescription.** We explain *how* nutrients work in the body and *what* the evidence says about outcomes. We don't tell the reader what to take, when, or how much. If the reader finishes an edition thinking "now I understand *why* my doctor suggested X" — that's the goal. If they finish thinking "I should go buy X" — we've failed.
