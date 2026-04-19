# Topic Backlog

Ordered queue. Pipeline reads this daily, picks highest-priority entry in the day's category where `last_touched` is blank or older than 180 days.

**Source strength:** Tier-1 (multiple RCTs / meta-analyses), Tier-2 (RCTs or strong observational), Tier-3 (preliminary).
**Priority:** 1 = publish next in category, 2 = mid-queue, 3 = backfill.

---

| slug | category | priority | source_strength | last_touched | notes |
|---|---|---|---|---|---|
| magnesium-glycinate | micro | 1 | Tier-1 | — | Sleep + anxiety angle; NMDA/GABA mechanism |
| vitamin-d3-k2 | micro | 1 | Tier-1 | — | Synergy: D3 pulls Ca from gut, K2 routes it to bone vs artery |
| creatine-monohydrate | macro | 1 | Tier-1 | — | Lift + cognition + sarcopenia; pull up if trending lane fires |
| omega-3-epa-dha | macro | 1 | Tier-1 | — | EPA vs DHA distinction; triglycerides, mood, inflammation |
| zinc | micro | 1 | Tier-1 | — | Immunity, skin, taste; zinc:copper ratio caution |
| protein-quality | macro | 1 | Tier-1 | — | PDCAAS vs DIAAS; veg-heavy Indian diet gap |
| fiber-soluble-insoluble | macro | 1 | Tier-1 | — | Short-chain fatty acids; microbiome; glucose curve |
| iron-heme-nonheme | micro | 1 | Tier-1 | — | Indian women deficiency rate; absorption with C vs inhibited by tea |
| iodine | micro | 2 | Tier-1 | — | Goitre belt history; thyroid; salt iodization success |
| selenium | micro | 2 | Tier-2 | — | Thyroid hormone conversion; Brazil-nut anchor |
| b12-cobalamin | micro | 1 | Tier-1 | — | Vegetarian deficiency; methyl vs cyano forms |
| folate-methylfolate | micro | 2 | Tier-1 | — | MTHFR gene; pregnancy; synthetic vs natural |
| choline | micro | 2 | Tier-2 | — | Liver, brain, under-consumed; eggs + liver |
| creatine-for-women | macro | 2 | Tier-1 | — | Specific sub-angle if trending lane triggers |
| ashwagandha | traditional | 1 | Tier-2 | — | Cortisol claims; KSM-66 vs Sensoril forms |
| turmeric-curcumin | traditional | 1 | Tier-2 | — | Bioavailability problem; piperine; joint pain |
| triphala | traditional | 2 | Tier-3 | — | Gut/digestion; evidence is mostly preliminary |
| ghee | traditional | 2 | Tier-2 | — | Saturated fat narrative; butyrate angle |
| neem | traditional | 3 | Tier-3 | — | Blood-sugar claims; mostly animal data |
| moringa | traditional | 2 | Tier-3 | — | Nutrient density hype vs practical dose |
| giloy | traditional | 3 | Tier-3 | — | Immunity claims; COVID-era misinformation case study |
| cinnamon | traditional | 2 | Tier-2 | — | Ceylon vs cassia; glucose effect modest |
| green-tea-catechins | macro | 2 | Tier-2 | — | Fat-oxidation overstated; polyphenol effects |
| coffee-caffeine | macro | 2 | Tier-1 | — | Endurance, cognition, timing caveats |
| vitamin-c-ascorbic | micro | 2 | Tier-1 | — | Immunity myth vs reality; iron absorption pairing |
| vitamin-e-tocopherols | micro | 3 | Tier-2 | — | Why supplements failed in trials; mixed vs alpha |
| vitamin-a-retinol-carotene | micro | 2 | Tier-1 | — | Indian deficiency; pre-formed vs pro-vitamin |
| calcium-absorption | micro | 2 | Tier-1 | — | Dairy vs non-dairy; D/K2 pairing; supplement CVD flag |
| potassium | micro | 2 | Tier-1 | — | Sodium:potassium ratio; BP; most Indians deficient |
| collagen | macro | 2 | Tier-2 | — | Skin + joint trial data; amino acid argument |
| glycine | macro | 3 | Tier-2 | — | Sleep; collagen building block; connective tissue |
| taurine | macro | 3 | Tier-2 | — | Longevity paper; cardiac; energy drinks framing |
| l-theanine | macro | 3 | Tier-2 | — | Focus + caffeine synergy; green tea |
| probiotics-strains | traditional | 2 | Tier-2 | — | Strain specificity; yogurt vs capsule |
| prebiotics-inulin | traditional | 3 | Tier-2 | — | FODMAP caution; bloating |
| nitrates-leafy-greens | macro | 2 | Tier-2 | — | BP; endurance; beet shots |
| polyphenols-berries | macro | 3 | Tier-2 | — | Pigment family; overstated claims |
| seed-oils-linoleic | macro | 2 | Tier-2 | — | Viral-claim audit framing; omega-6:3 ratio reality |
| saturated-fat-heart | macro | 2 | Tier-1 | — | Viral-claim audit; meta-analyses rethink |
| apple-cider-vinegar | traditional | 2 | Tier-3 | — | Glucose spike dampening; minor effect |

---

## How to add entries manually

Append a row. Pipeline honors manual adds with priority 1 if you flag them `notes: MANUAL`.

## Auto-top-up

Sunday's prep run appends any nutrient with >=3 new high-quality papers from the last 30 days that isn't already scheduled within 30 days. Entries marked `notes: MANUAL` are never removed automatically.
