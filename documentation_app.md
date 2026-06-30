# 📖 Documentation — Suivi Entraînement

> Cette documentation explique la logique scientifique derrière chaque métrique de l'application : pourquoi elle existe, comment elle se calcule, et comment l'interpréter pour prendre des décisions d'entraînement éclairées.

> **Note sur les niveaux de confiance.** La physiologie de l'endurance comporte des principes solides et des zones encore débattues. Les passages marqués **⚠️ Débattu** signalent des points où la littérature n'est pas consensuelle — à prendre comme repères, pas comme vérités.

---

## Table des matières

1. [Entraînement & charge](#1-entraînement--charge)
2. [Récupération & HRV](#2-récupération--hrv)
3. [Nutrition](#3-nutrition)
4. [Physiologie transversale](#4-physiologie-transversale)
5. [Glossaire](#glossaire)
6. [Références](#références)

---

# 1. Entraînement & charge

## 1.1 Les zones d'intensité

L'intensité d'un effort se découpe en zones délimitées par deux **seuils physiologiques** :

| Seuil | Synonymes | Signification physiologique |
|-------|-----------|----------------------------|
| **SV1** (seuil ventilatoire 1) | Seuil aérobie, LT1 | Première rupture de linéarité de la ventilation. En dessous, l'effort est quasi 100 % aérobie, le lactate reste à son niveau de base (~2 mmol/L). |
| **SV2** (seuil ventilatoire 2) | Seuil anaérobie, LT2, MLSS | Point au-delà duquel le lactate s'accumule plus vite qu'il n'est éliminé. C'est la plus haute intensité tenable en quasi-équilibre (~30-60 min selon le niveau). |

Ces seuils sont **bien plus pertinents que les %FCmax** pour piloter l'entraînement : deux athlètes avec la même FCmax peuvent avoir des seuils très différents selon leur niveau.

### Le modèle 3 zones (recommandé)

```
Zone 1  → < SV1        → Endurance fondamentale, "facile"
Zone 2  → SV1 – SV2    → Tempo / seuil, "moyennement dur"
Zone 3  → > SV2        → Haute intensité, VO2max et au-delà
```

C'est le modèle physiologiquement le plus propre : chaque zone correspond à un régime métabolique distinct. Le modèle 5 zones (souvent utilisé par les montres) subdivise ces régions mais introduit des frontières plus arbitraires.

### Pourquoi la zone 1 domine

L'erreur classique de l'amateur est de passer trop de temps en zone 2 ("no man's land") : assez dur pour fatiguer, pas assez pour maximiser l'adaptation aérobie ou la puissance.

**⚠️ Débattu — distribution polarisée vs pyramidale.**
- **Modèle polarisé (Seiler)** : ~80 % du *volume* en zone 1, ~20 % en zone 3, très peu en zone 2. Soutenu par l'observation des athlètes d'élite en endurance.
- **Modèle pyramidal** : majorité en zone 1, une part décroissante en zone 2 puis zone 3. Certaines études le trouvent aussi efficace, surtout en phase de préparation spécifique.

En pratique pour l'ultra-trail, la base reste la même : **la grande majorité du volume doit être facile**, l'intensité étant une dose concentrée et minoritaire. Le débat porte sur les 20 % restants, pas sur le principe.

---

## 1.2 Quantifier la charge d'une séance

Une "charge d'entraînement" cherche à résumer en un nombre le stress imposé à l'organisme. Deux familles : basées sur la perception (sRPE) ou sur la fréquence cardiaque (TRIMP).

### sRPE — Session RPE

```
sRPE = RPE × durée (min)
```

Le **RPE** (Rating of Perceived Exertion) est noté sur une échelle 1-10 (CR-10 de Borg), évalué **~30 min après la séance** pour capturer la sensation globale.

**Pourquoi c'est robuste :**
- Capture *tout* : fatigue mentale, chaleur, altitude, dénivelé technique, sommeil de la veille — des facteurs qu'aucun capteur ne mesure.
- Validé massivement (Foster et coll.). Corrèle bien avec les marqueurs objectifs de charge.
- Fonctionne pour toutes les disciplines, sans matériel.

**Sa limite :** subjectif. Mais sur la durée, ta propre cohérence interne (tu notes toujours de la même façon) suffit à rendre le signal exploitable.

### TRIMP — Training Impulse (Banister)

Version exponentielle, la plus utilisée :

```
TRIMP = durée(min) × ΔHR_ratio × 0.64 × e^(k × ΔHR_ratio)

ΔHR_ratio = (FC_moy − FC_repos) / (FC_max − FC_repos)
k = 1.92 (homme) | 1.67 (femme)
```

**Le cœur du concept : la pondération exponentielle.** Un effort intense ne coûte pas linéairement plus qu'un effort facile — il coûte *disproportionnellement* plus. La fonction exponentielle reproduit la réponse lactate, qui explose aux hautes intensités.

| ΔHR_ratio | Régime | Poids exponentiel |
|-----------|--------|-------------------|
| 0.50 | modéré | ≈ 2.6 |
| 0.80 | dur | ≈ 4.8 |
| 0.95 | quasi-maximal | ≈ 6.4 |

Concrètement : 10 min à 95 % "pèsent" autant que beaucoup plus de minutes faciles.

**Limite majeure en trail :** TRIMP est purement cardiaque. Il ignore le coût musculaire du dénivelé, l'usage des bâtons (travail des bras invisible à la FC), et la fatigue neuromusculaire des descentes techniques (FC parfois basse, dégâts élevés). **Il sous-estime systématiquement les longues sorties techniques.**

### Variante : TRIMP par zones (Lucia)

```
TRIMP_zones = (min_Z1 × 1) + (min_Z2 × 2) + (min_Z3 × 3)
```

Chaque minute en zone N vaut N points. Plus grossier que la version exponentielle, mais immédiat si les minutes par zone sont déjà connues. Bon compromis pour un suivi quotidien.

---

## 1.3 Modéliser fitness et fatigue : CTL / ATL / TSB

On passe de la charge d'*une* séance à la dynamique sur des *semaines*. Le modèle (Banister, popularisé par TrainingPeaks) repose sur une idée : **chaque entraînement produit à la fois de la forme et de la fatigue, mais elles ne disparaissent pas au même rythme.**

Le mécanisme : des **moyennes pondérées exponentielles** de la charge quotidienne. Les jours récents pèsent plus que les anciens.

### Les trois métriques

```
ATL (fatigue) = moyenne exponentielle sur 7 jours
   ATL_j = ATL_(j-1) × (6/7)  + charge_j × (1/7)

CTL (forme)   = moyenne exponentielle sur 42 jours
   CTL_j = CTL_(j-1) × (41/42) + charge_j × (1/42)

TSB (fraîcheur) = CTL − ATL
```

- **ATL** (Acute Training Load) réagit **vite** (7 j) — la fatigue récente.
- **CTL** (Chronic Training Load) réagit **lentement** (42 j) — la forme construite sur le long terme. Une semaine de repos ne le fait presque pas bouger.
- **TSB** (Training Stress Balance) = la différence — indique si tu es **frais ou cuit, relativement à ta forme générale**.

### Lire le TSB

| TSB | État | Interprétation |
|-----|------|----------------|
| **> +10** | Frais | Compétition possible, performance optimale |
| **0 à −10** | Équilibre | Fatigue légère, normale |
| **−10 à −30** | En charge | Tu construis. Pas de pic de forme attendu |
| **< −30** | Surcharge | Risque de surmenage |
| **> +25** | Désentraîné | Affûtage trop long, la forme s'érode |

**Le principe à retenir :** la progression vient d'une **CTL qui monte progressivement** (surcharge), entrecoupée de phases où on laisse la TSB remonter pour absorber et performer. Monter la CTL trop vite (> ~5-7 pts/semaine) augmente le risque de blessure.

**⚠️ Limite :** le modèle a été calibré pour le cyclisme avec capteur de puissance (la charge = TSS). En trail, on l'alimente avec du sRPE — la logique reste valable mais la précision est moindre. **C'est un indicateur de tendance, pas une vérité au point près.**

---

## 1.4 Monotonie & Strain

Deux séances de même charge totale n'ont pas le même impact selon leur *répartition*. Foster a formalisé ça :

```
Monotonie = charge_moyenne_quotidienne / écart-type_quotidien   (sur 7 j)
Strain    = charge_totale_semaine × Monotonie
```

**Ce que ça capture :** faire la *même* charge tous les jours (monotonie élevée) est plus délétère que d'alterner jours durs et jours faciles. L'organisme s'adapte à la variation, pas à la répétition uniforme.

| Monotonie | Lecture |
|-----------|---------|
| **< 1.5** | Bonne variation (alternance dur/facile) |
| **1.5 – 2.0** | Acceptable |
| **> 2.0** | Monotonie élevée — risque accru de surmenage/maladie |

Le **Strain** combine volume et monotonie : un gros volume *réparti uniformément* produit un strain très élevé, signal d'alerte. La règle pratique : **inclure de vrais jours faciles et de vrais jours de repos** fait baisser la monotonie et protège.

---

# 2. Récupération & HRV

## 2.1 Le système nerveux autonome (SNA)

Le SNA régule les fonctions involontaires (cœur, digestion, etc.) via deux branches antagonistes :

- **Parasympathique (PNS)** — "repos & digestion". Ralentit le cœur, favorise la récupération. Dominant quand tu es reposé.
- **Sympathique (SNS)** — "combat ou fuite". Accélère le cœur, mobilise l'énergie. Dominant sous stress, effort, fatigue.

**L'idée centrale de la HRV :** l'équilibre entre ces deux branches se lit dans la variabilité du rythme cardiaque. Un cœur bien récupéré est sous influence parasympathique — ses battements varient davantage. Un cœur stressé est sous influence sympathique — il bat de façon plus régulière, "métronomique".

C'est contre-intuitif : **plus de variabilité = meilleur état**.

---

## 2.2 Les métriques HRV

### RMSSD — le marqueur de référence

*Root Mean Square of Successive Differences* : la racine de la moyenne des carrés des différences entre intervalles RR successifs (battement à battement).

```
RR : 980 ms → 1020 ms → 960 ms → 1100 ms ...
RMSSD mesure l'ampleur de ces variations.
```

- **Médié par le nerf vague** (parasympathique) — reflète directement l'état de récupération.
- RMSSD élevé (athlète bien récupéré : souvent 60-100 ms) = parasympathique actif.
- RMSSD bas (chute de 20-30 % vs ta baseline) = fatigue accumulée, **avant même que la performance ne chute**.

C'est le signal brut le plus fiable. Les indices Kubios en dérivent.

### SDNN — variabilité globale

Écart-type de tous les intervalles RR. Capture la variabilité *totale* (parasympathique + sympathique + rythmes plus lents). Repères : > 30 ms = sain, > 50 ms = profil athlétique. Moins spécifique que le RMSSD pour la récupération à court terme.

### PNS Index & SNS Index (Kubios)

Kubios combine plusieurs paramètres en deux scores **standardisés contre une population normale au repos** :

```
0   = valeur moyenne de la population
> 0 = au-dessus de la normale
< 0 = en dessous de la normale
Échelle typique : environ −2 à +2 (en écarts-types)
```

- **PNS Index** (dérivé de RMSSD, FC moyenne, et composante haute fréquence) : élevé = bonne dominance parasympathique = récupéré.
- **SNS Index** (dérivé de FC moyenne, composante basse fréquence, et indices géométriques) : élevé = dominance sympathique = stress/fatigue.

Au repos matinal, on cherche **PNS positif et SNS négatif**.

**⚠️ Débattu — l'interprétation de la composante LF.** La métrique LF (basse fréquence) a longtemps été présentée comme un pur reflet du tonus sympathique. C'est une **simplification contestée** : la LF est en réalité influencée par les deux branches du SNA (et par la respiration, le baroréflexe). Le ratio LF/HF comme "balance sympatho-vagale" est aujourd'hui considéré comme peu fiable. C'est pourquoi le **RMSSD et le PNS Index** (vagalement médiés, robustes) sont à privilégier sur les indices basés sur la LF.

### Readiness (%)

Score composite propriétaire Kubios (combine RMSSD, FC, et autres paramètres) ramené sur 0-100 %. Pratique comme **signal go/no-go** synthétique, mais opaque : préfère vérifier les composantes brutes (RMSSD, PNS, FC) pour comprendre *pourquoi* le Readiness monte ou descend.

| Readiness | Lecture |
|-----------|---------|
| **> 75 %** | Excellente fenêtre pour l'intensité |
| **50–75 %** | Entraînement normal OK |
| **25–50 %** | Léger seulement |
| **< 25 %** | Repos |

---

## 2.3 Fréquence cardiaque de repos (FC repos)

Le proxy le plus simple — et étonnamment robuste. Mesurée au réveil, allongé, avant le lever.

- **Stable** vs ta baseline = système équilibré.
- **Élevée de +5 à +10 bpm** = fatigue, infection naissante, sous-récupération, ou stress.

Moins fine que la HRV, mais c'est un excellent **garde-fou de cohérence** : si la FC repos grimpe alors que le Readiness reste haut, c'est probablement du bruit (café, mesure tardive). Si les deux signalent la fatigue, le message est solide.

---

## 2.4 Sommeil

Le levier de récupération n°1, devant tout le reste. Deux dimensions :

- **Durée** : la quantité de sécrétion d'hormone de croissance, la consolidation neuromusculaire et la clairance métabolique en dépendent.
- **Qualité** : un sommeil long mais fragmenté ne vaut pas un sommeil continu.

Point important : **la HRV et la qualité de sommeil peuvent diverger**. Après un effort intense, l'organisme peut récupérer physiologiquement (bonne HRV au matin) tout en ayant produit un sommeil agité. Croiser les deux évite les fausses conclusions.

---

## 2.5 Protocole de mesure HRV

La fiabilité de tout le suivi dépend de la **standardisation**. Les règles :

1. **Moment** : dans les ~10 min après le réveil, **avant** de te lever, avant l'eau, le café, le téléphone.
2. **Position** : **allongé** (parasympathique mieux mesuré, moins de bruit que debout/assis).
3. **Durée** : 3-5 min (5 recommandé pour la stabilité ; < 3 min = trop de bruit).
4. **Régularité** : même créneau (±30 min) chaque jour. Le matin, plus tu attends, plus le cortisol et le mouvement élèvent le sympathique — tu mélangerais fatigue réelle et bruit horaire.
5. **Respiration** : naturelle, non forcée.

**La baseline est personnelle.** Les 10 premiers jours servent à l'établir. Ensuite, **ce sont les écarts à ta baseline qui comptent**, pas les valeurs absolues comparées à d'autres athlètes.

**Seuils d'alerte (à personnaliser sur ta baseline) :**
- RMSSD en baisse > 25-30 %
- PNS Index en chute marquée
- SNS Index qui passe positif
- FC repos > +5 bpm

→ Plusieurs signaux concordants sur 2-3 jours = réduire la charge.

---

# 3. Nutrition

## 3.1 Le bilan énergétique

Tout part de l'équation :

```
Balance = Apports − Dépenses
```

- **Dépenses** = métabolisme de base (BMR) + thermogenèse alimentaire + activité quotidienne (NEAT) + entraînement.
- **Apports** = ce que tu manges.

### BMR — équation de Mifflin-St Jeor

La plus précise pour la population générale :

```
Homme  : BMR = 10×poids(kg) + 6.25×taille(cm) − 5×âge + 5
Femme  : BMR = 10×poids(kg) + 6.25×taille(cm) − 5×âge − 161
```

La **dépense totale (TDEE)** = BMR × facteur d'activité + dépense d'entraînement du jour. C'est pourquoi la cible calorique de l'app est dynamique : elle s'ajuste à l'entraînement réalisé.

**⚠️ Rappel critique sur les calories d'effort.** Les dépenses fournies par les apps de sport (Strava et consorts) sont peu fiables : **±20-30 % sans capteur de puissance, davantage en trail technique**. À utiliser comme ordre de grandeur et tendance, jamais comme calibration alimentaire au gramme près. Le vrai juge de paix reste le **suivi du poids sur plusieurs semaines** : poids stable à entraînement stable = ton TDEE réel est trouvé.

---

## 3.2 Les macronutriments

### Glucides — le carburant de l'intensité

Le substrat dominant dès que l'intensité monte. Les réserves (glycogène musculaire + hépatique) sont **limitées** (~400-600 g, soit ~1600-2400 kcal) — d'où leur importance centrale en endurance.

Besoins selon la charge (ACSM/IOC) :

| Charge d'entraînement | Glucides (g/kg/jour) |
|-----------------------|----------------------|
| Léger (faible intensité) | 3 – 5 |
| Modéré (~1 h/jour) | 5 – 7 |
| Élevé (1-3 h/jour intense) | 6 – 10 |
| Très élevé (> 4-5 h/jour) | 8 – 12 |

### Protéines — réparation et adaptation

Pour l'athlète d'endurance : **1.4 – 2.0 g/kg/jour** (au-dessus des 0.8 g/kg de la population sédentaire). Rôle : réparation des fibres, synthèse des adaptations, soutien immunitaire. Répartition idéale : ~20-40 g par prise, étalée sur la journée.

**⚠️ Débattu :** la borne haute (jusqu'à ~2.2 g/kg) fait l'objet de discussions, surtout en phase de déficit calorique où un apport protéique plus élevé protège la masse maigre.

### Lipides — le reste

Complètent l'apport énergétique une fois glucides et protéines fixés. Plancher de ~1 g/kg/jour (≈ 20 % de l'énergie minimum) pour la fonction hormonale et l'absorption des vitamines liposolubles. Important hors séance ; on les réduit autour des efforts pour ne pas gêner la digestion.

---

## 3.3 Périodisation glucidique

Concept moderne : **adapter l'apport glucidique à la demande du jour** ("fuel for the work required", Impey & coll.), plutôt qu'un apport élevé uniforme.

- **Train high** : glycogène plein avant les séances clés (intensité, séances longues spécifiques) — qualité d'exécution.
- **Train low** : certaines séances faciles réalisées avec un glycogène réduit — stimule des **adaptations mitochondriales** et l'oxydation des lipides.

**⚠️ Débattu / à manier avec prudence :** le "train low" a un coût (qualité de séance réduite, stress immunitaire, risque accru de blessure si mal dosé). C'est un outil avancé, à utiliser ponctuellement et sur des séances *faciles*, jamais sur les séances de qualité.

---

## 3.4 Nutrition d'effort (longues sorties & course)

Sur les efforts prolongés, l'apport glucidique externe devient déterminant — c'est ce qui retarde l'épuisement du glycogène.

### Les limites d'oxydation (Jeukendrup)

L'organisme ne peut oxyder qu'une quantité limitée de glucides ingérés par heure, **plafonnée par le transport intestinal** :

| Type de glucides | Débit max oxydable |
|------------------|---------------------|
| Glucose seul | **~60 g/h** (transporteur SGLT1 saturé) |
| Glucose + fructose (ratio ~2:1 ou 1:0.8) | **~90 g/h** (le fructose emprunte un 2e transporteur, GLUT5) |

C'est la base des gels et boissons "multi-transportables" : combiner glucose et fructose lève le plafond.

### Repères pratiques par durée d'effort

| Durée | Glucides/h |
|-------|-----------|
| < 45 min | inutile (réserves suffisantes) |
| 45-75 min | rinçage de bouche / petites quantités |
| 1-2.5 h | 30-60 g/h |
| > 2.5 h | 60-90 g/h (nécessite glucose+fructose) |

### L'entraînement intestinal ("gut training")

Tolérer 90 g/h ne s'improvise pas : l'intestin **s'entraîne**. Habituer progressivement le système digestif à de fortes charges glucidiques à l'effort réduit les troubles gastro-intestinaux le jour J. À travailler à l'entraînement, comme le reste.

---

## 3.5 Hydratation

Hautement individuelle (le taux de sudation varie d'un facteur 3-4 entre individus).

- **Volume** : ~0.4 à 0.8 L/h selon la chaleur et le taux de sudation. Se peser avant/après une longue séance donne une estimation directe des pertes (1 kg perdu ≈ 1 L).
- **Sodium** : ~300-600 mg/L de boisson, davantage chez les "gros saleurs" et par forte chaleur. Le sodium soutient la volémie et l'absorption.

**Éviter les deux extrêmes :** la déshydratation (> 2-3 % du poids corporel dégrade la performance) **et** la sur-hydratation à l'eau pure (risque d'**hyponatrémie**, dangereux sur les très longs efforts). Boire à sa soif, en salant, est un bon point de départ.

---

# 4. Physiologie transversale

## 4.1 Substrats énergétiques & point de crossover

À l'effort, le corps puise dans deux carburants principaux : **lipides** et **glucides**. Leur proportion dépend de l'intensité.

```
Faible intensité  → majorité lipides (réserves quasi illimitées, mais débit lent)
Intensité élevée  → majorité glucides (débit rapide, réserves limitées)
```

Le **point de crossover** (Brooks) est l'intensité où les glucides deviennent la source dominante. La **FatMax** est l'intensité où l'oxydation des lipides est maximale en valeur absolue (typiquement en zone 1).

**Pourquoi ça compte en ultra :** un athlète entraîné en endurance déplace son crossover **vers le haut** — il oxyde plus de lipides à une intensité donnée, épargnant son glycogène limité. C'est un objectif d'adaptation central pour les longs formats, et l'une des justifications du gros volume facile (zone 1) et du "train low" ponctuel.

---

## 4.2 Dérive cardiaque (cardiac drift)

Sur un effort prolongé à **allure constante**, la FC **augmente progressivement** alors que l'intensité réelle ne change pas.

Causes principales : déshydratation → baisse du volume plasmatique → le cœur compense en accélérant ; accumulation de chaleur ; fatigue.

**Conséquence pratique :** sur une longue sortie, la FC moyenne **surestime** l'intensité métabolique réelle de la fin de séance. C'est une raison de plus pour laquelle les métriques purement cardiaques (TRIMP) sont imparfaites sur le long, et pourquoi la sensation (RPE) et l'allure/puissance restent des repères complémentaires.

---

## Glossaire

| Terme | Définition courte |
|-------|-------------------|
| **ATL** | Acute Training Load — fatigue (moyenne pondérée 7 j) |
| **CTL** | Chronic Training Load — forme (moyenne pondérée 42 j) |
| **TSB** | Training Stress Balance — fraîcheur (CTL − ATL) |
| **sRPE** | Charge perçue = RPE × durée |
| **RPE** | Effort perçu, échelle 1-10 |
| **TRIMP** | Training Impulse — charge basée sur la FC |
| **RMSSD** | Marqueur HRV de référence, médié par le nerf vague |
| **SDNN** | Variabilité globale des intervalles RR |
| **PNS / SNS** | Branches parasympathique / sympathique du SNA |
| **SV1 / SV2** | Seuils ventilatoires 1 (aérobie) et 2 (anaérobie) |
| **MLSS** | Maximal Lactate Steady State — proche de SV2 |
| **FatMax** | Intensité d'oxydation maximale des lipides |
| **BMR** | Métabolisme de base |
| **TDEE** | Dépense énergétique totale quotidienne |
| **NEAT** | Dépense d'activité hors exercice structuré |

---

## Références

Sélection de sources fondatrices pour approfondir :

- **Banister EW** (1991) — modèle impulse-response fitness/fatigue (base de CTL/ATL/TSB et du TRIMP).
- **Foster C** (1998) — *Monitoring training in athletes with reference to overtraining syndrome* (sRPE, monotonie, strain).
- **Seiler S** (2010) — *What is best practice for training intensity and duration distribution?* (modèle polarisé).
- **Jeukendrup AE** — travaux sur l'oxydation des glucides exogènes et les glucides multi-transportables.
- **Burke LM, Impey SG et coll.** — périodisation glucidique, "fuel for the work required".
- **Brooks GA** — concept du point de crossover des substrats.
- **Shaffer F & Ginsberg JP** (2017) — *An Overview of Heart Rate Variability Metrics and Norms* (référence sur l'interprétation des métriques HRV, y compris les limites de la LF).
- **Documentation Kubios HRV** — définition des indices PNS/SNS et du Readiness.
- **ACSM / IOC Consensus on Nutrition for Athletes** — recommandations macronutriments.

---

*Cette documentation est un support pédagogique fondé sur la littérature en physiologie de l'exercice. Elle ne remplace pas un suivi médical ou un accompagnement par un professionnel qualifié.*
