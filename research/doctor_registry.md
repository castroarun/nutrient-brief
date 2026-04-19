# Doctor Registry

Whitelist of clinicians the pipeline may cite. Indian-first by default; international fallback only when no Indian specialist with a topic-match exists.

**Every quote is paraphrased from the clinician's *published* work** (peer-reviewed paper, professional blog, book, or public talk). Never from private correspondence, never fabricated.

**Attribution format:** "Paraphrased from published work of Dr. [Name], [degree], [institution] (~N publications on [topic area])."

---

## Indian clinicians — primary pool

| name | degree | institution | specialty | topic-match tags | last_used |
|---|---|---|---|---|---|
| Dr. V. Mohan | MD, PhD, DSc | Madras Diabetes Research Foundation, Chennai | Diabetology, nutrition epidemiology | glucose, fiber, carbs, protein, Indian-diet, micronutrients | — |
| Dr. Shweta Khandelwal | PhD, MSc | Public Health Foundation of India, Delhi | Nutrition epidemiology, maternal | folate, iron, omega-3, pregnancy, deficiency | — |
| Dr. Anoop Misra | MD, DM | Fortis-C-DOC, Delhi | Endocrinology, metabolic syndrome | vitamin D, obesity, insulin resistance, Indian phenotype | — |
| Dr. Rujuta Diwekar | MSc, Certified Sports Nutritionist | Independent | Traditional Indian nutrition | ghee, grains, seasonal eating, traditional foods | — *Note: verify every claim against RCT data.* |
| Dr. Ishi Khosla | MSc, Clinical Nutritionist | The Celiac Society of India | Gut health, autoimmune | gluten, probiotics, gut-brain, inflammation | — |
| Dr. Anurag Agrawal | MD, DPhil (Oxon) | Ashoka University, Delhi | Respiratory biology, translational | vitamin D, immunity, air quality, systems biology | — |
| Dr. Dharini Krishnan | PhD, RD | Independent, Chennai | Clinical nutrition, diabetes | DASH, Indian staples, diabetes management | — |
| Dr. Shilpa Bhupathiraju | PhD | Harvard T.H. Chan (Indian-origin, US-based) | Nutrition epidemiology | whole grains, protein, cardiovascular, T2D | — |
| Dr. Darshan Shah | MD (wellness/holistic) | Next Health, Mumbai | Longevity, metabolic health | creatine, supplements, biomarkers | — *Note: wellness-leaning; verify claims against primary literature.* |
| Dr. K. Srinath Reddy | MD, DM, MSc | Public Health Foundation of India | Cardiology, public health nutrition | salt, saturated fat, policy-level nutrition | — |

---

## International clinicians — fallback only

Used only when the topic has no Indian specialist with a verified match.

| name | degree | institution | specialty | topic-match tags | last_used |
|---|---|---|---|---|---|
| Dr. Walter Willett | MD, DrPH | Harvard T.H. Chan | Nutrition epidemiology, chronic disease | omega-3, dietary patterns, fat, cardiovascular | — |
| Dr. Christopher Gardner | PhD | Stanford | Nutrition science, plant vs animal | protein, plant diets, weight-loss trials | — |
| Dr. David Ludwig | MD, PhD | Boston Children's / Harvard | Obesity, carbohydrate-insulin model | glycemic index, insulin, fiber | — |
| Dr. Shawn Arent | PhD, CSCS | Univ. of South Carolina | Sports nutrition, ergogenic aids | creatine, caffeine, beta-alanine, protein timing | — |
| Dr. Stuart Phillips | PhD | McMaster | Protein + muscle metabolism | protein, leucine, sarcopenia, muscle | — |
| Dr. Tim Spector | MD, FRCP | King's College London | Microbiome, personalized nutrition | fiber, probiotics, gut, glucose variability | — |
| Dr. Layne Norton | PhD | Independent / content + research | Evidence-based supplements | creatine, protein, body composition | — |

---

## Consent & verification rules

Pipeline checks before citing:

1. **Public work exists** — PubMed search (for academics) or canonical book/talk citation (for popular voices) matching the topic tag.
2. **Specialty-topic match** — clinician's publication record on the specific topic must exceed a minimum threshold (3 papers for academics, 1 published book section or >=5 articles for popular voices).
3. **Quote is paraphrased, not invented** — paraphrase must trace to an actual documented statement.
4. **Attribution includes pub-count** — so readers can verify independently.

## How to add

Append a row with name, degree, institution, specialty, at least 3 topic tags. Leave `last_used` blank.

## Cooldown

Same clinician not cited more than once per 60 days to preserve source diversity. Pipeline checks `last_used` before selecting.
