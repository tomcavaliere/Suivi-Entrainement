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

L'intensité d'un effort se découpe en zones délimitées par deux **seuils physiologiques**. Tout le pilotage de l'entraînement repose sur eux — bien plus que sur les %FCmax, car deux athlètes de même FCmax peuvent avoir des seuils très différents selon leur niveau.

### SV1 — le seuil aérobie (≈ LT1)

*Synonymes : premier seuil ventilatoire, seuil aérobie, LT1.*

C'est la **première** rupture de linéarité de la ventilation à l'effort croissant. En dessous, l'effort est quasi **100 % aérobie** : le lactate reste à son niveau de repos (~1-2 mmol/L), entièrement recyclé au fil de sa production. On peut tenir des **heures** à cette intensité.

Repère subjectif : c'est la limite haute du « confortable », où l'on peut encore **parler en phrases complètes**. C'est la frontière du véritable travail d'endurance fondamentale.

### SV2 — le seuil anaérobie (≈ LT2 / MLSS)

*Synonymes : second seuil ventilatoire, seuil anaérobie, LT2, proche du MLSS.*

C'est le point au-delà duquel le lactate **s'accumule plus vite qu'il n'est éliminé** : l'équilibre bascule. C'est la **plus haute intensité tenable en quasi-équilibre métabolique** — soutenable ~**30 à 60 min** selon le niveau (proche de l'allure semi-marathon à marathon pour un coureur entraîné).

Repère subjectif : on ne parle plus que par **mots isolés**. Au-dessus, l'horloge tourne vite.

> Ces deux seuils découpent trois grands **régimes métaboliques** : sous SV1 (aérobie pur), entre SV1 et SV2 (zone de transition), au-dessus de SV2 (accumulation lactique). Le modèle 5 zones ci-dessous subdivise ces régimes pour un pilotage plus fin.

### Le modèle 5 zones (ancré sur SV1 / SV2)

| Zone | Bornes (vs seuils) | Lactate | RPE /10 | Durée tenable | Filière & adaptation visée |
|------|--------------------|---------|---------|---------------|----------------------------|
| **Z1 — Récupération** | nettement < SV1 | base | 1-2 | illimitée | Récup active, drainage. Aucune contrainte. |
| **Z2 — Endurance fondamentale** | jusqu'à SV1 | base (~1-2) | 3-4 | plusieurs heures | **Base aérobie** : densité mitochondriale, capillarisation, oxydation des lipides, volume d'éjection cardiaque. *Le cœur du volume.* |
| **Z3 — Tempo / allure spécifique** | SV1 — juste sous SV2 | léger (~2-3) | 5-6 | 1-3 h | Endurance « tempo », allure marathon/ultra. Économie, soutien de l'allure aérobie. |
| **Z4 — Seuil** | autour de SV2 | (~3-4+) | 7-8 | 30-60 min | **Élève le SV2/MLSS** et la clairance du lactate. L'un des meilleurs ROI en endurance. |
| **Z5 — VO2max / anaérobie** | > SV2 | élevé, croissant | 9-10 | quelques min | Plafond aérobie (**VO2max**), puissance, capacité anaérobie. Doses courtes. |

### Exemple chiffré — tes propres repères

Avec tes valeurs (test 2024 : **SV1 = 175**, **SV2 = 185**, **FCmax = 205**, FC repos ~52) :

```
Z1 Récupération        : < ~160 bpm
Z2 Endurance fond.     : ~160 – 175 bpm   (plafond = SV1)
Z3 Tempo               : ~175 – 183 bpm
Z4 Seuil               : ~183 – 188 bpm   (autour de SV2)
Z5 VO2max / anaérobie  : > ~188 bpm       (jusqu'à 205)
```

Remarque : tes deux seuils sont **rapprochés (10 bpm)**, donc tes zones Z3-Z4-Z5 sont étroites. C'est individuel et normal — raison de plus pour piloter au seuil, pas au %FCmax. À revalider régulièrement (voir [1.2](#12-évaluer-ses-repères--fcmax-seuils-vo2max)).

### Distribution de l'intensité : combien dans chaque zone ?

L'erreur classique de l'amateur est de vivre en **Z3** (« no man's land ») : assez dur pour fatiguer, pas assez pour maximiser ni la base aérobie ni la puissance.

**⚠️ Débattu — polarisé vs pyramidal.** En regroupant les 5 zones en 3 régimes (bas = Z1-Z2, intermédiaire = Z3, haut = Z4-Z5) :
- **Modèle polarisé (Seiler)** : ~80 % du *volume* en bas (Z1-Z2), ~20 % en haut (Z4-Z5), **très peu** d'intermédiaire (Z3). Observé chez beaucoup d'athlètes d'élite.
- **Modèle pyramidal** : majorité en bas, part décroissante d'intermédiaire puis de haut. Aussi efficace selon certaines études, surtout en phase spécifique.

Pour l'ultra-trail, le principe est constant : **la grande majorité du volume reste facile (Z1-Z2)**, l'intensité étant une dose concentrée et minoritaire. Le débat porte sur la place de la Z3, pas sur le socle.

---

## 1.2 Évaluer ses repères : FCmax, seuils, VO2max

Les zones ne valent que si leurs ancrages sont justes. Voici comment déterminer chaque repère, du plus accessible au gold standard.

### Fréquence cardiaque maximale (FCmax)

**À retenir d'emblée :** la FCmax est **largement génétique**, ne s'améliore **pas** à l'entraînement, et décline lentement avec l'âge. C'est un plafond individuel, pas un objectif.

- **Formules théoriques** — `220 − âge` ou Tanaka `208 − 0.7 × âge`. **⚠️ Très imprécises** (écart-type ~10-12 bpm). Bon point de départ grossier, rien de plus.
- **Test terrain (fiable)** — après échauffement complet : effort progressif jusqu'à épuisement, typiquement une **série de montées dures** ou un **2-3 km en accélération finale maximale**. La FCmax = la valeur la plus haute jamais observée en effort maximal ou en compétition (fin de 5 km, côtes répétées à fond).
- Ta valeur : **205 bpm**. Si elle vient d'un vrai effort maximal, garde-la ; les formules te donneraient ~190, ce qui sous-estimerait tes zones hautes.

### Seuils SV1 / SV2 (le plus important)

| Méthode | Cible | Principe | Précision |
|---------|-------|----------|-----------|
| **Test labo** | SV1 **et** SV2 | Test incrémental avec analyse des **gaz expirés** (seuils ventilatoires) ou prises de **lactate** sanguin (seuils lactiques). | Gold standard (c'est ton test 2024) |
| **Talk test** | SV1 | La plus haute intensité où tu parles encore en **phrases complètes**. | Bon, gratuit |
| **Test 30 min (Friel)** | SV2 (LTHR) | Contre-la-montre solo de 30 min à fond ; la **FC moyenne des 20 dernières min** — FC au seuil. | Bon terrain |
| **CLM 20 min** | SV2 | FC/puissance moyenne à ~0.95 (logique « FTP »). | Bon terrain |
| **DFA alpha-1** | SV1 **et** SV2 | Analyse de la **variabilité RR** pendant un effort progressif (detrended fluctuation analysis). α1 ≈ **0.75 → SV1**, α1 ≈ **0.5 → SV2**. | ⚠️ Émergent |

**Focus DFA α1 — pertinent pour toi.** Cette méthode estime les **deux seuils sur le terrain** à partir des seuls intervalles RR, sans labo ni lactate. Elle exige une captation RR **propre** — ta **Polar H10 est idéale** (bien meilleure qu'un capteur optique au poignet). Outils : Runalyze, AI Endurance, FatMaxxer. **⚠️ Encore en validation** : sensible aux artefacts et aux conditions de mesure. À utiliser en **recoupant** avec tes ancrages connus (test labo, talk test), pas en aveugle.

### VO2max

- **Test labo** — mesure directe de la consommation d'oxygène lors d'un test incrémental maximal. Gold standard.
- **Estimations terrain** — test de Cooper (distance sur 12 min → formule), **prédiction par une perf** (ex. VDOT de Daniels à partir d'un temps de course), **vVO2max** (vitesse à VO2max) via test de terrain, ou estimation des montres (rapport FC/allure — **⚠️ approximatif**).

**⚠️ Ne survalorise pas le VO2max.** C'est un **plafond**, mais la performance en endurance dépend surtout de **deux autres facteurs** : la **fraction de VO2max soutenable** au seuil (utilisation fractionnaire) et l'**économie de course** (coût énergétique à allure donnée). Deux athlètes de même VO2max peuvent être très inégaux en course. Pour l'ultra, économie et seuil priment.

### À quelle fréquence retester ?

- **Seuils & VO2max** : ils **évoluent avec la forme** — retest toutes les **6-12 semaines** ou à chaque changement de bloc. Des zones calées sur de vieux seuils faussent tout le pilotage.
- **FCmax** : stable — rarement besoin de retester (hors progression de l'âge).

---

## 1.3 Les séances types par qualité développée

Chaque qualité physiologique se travaille par un type de séance et une zone dédiés. Voici la boîte à outils, de la base au plus spécifique.

### 1 — Endurance fondamentale (Z1-Z2)

- **Objectif :** densité mitochondriale, capillarisation, oxydation des lipides, volume cardiaque. **Le socle de tout.**
- **Formats :** sorties longues continues (LSD, *long slow distance*), footings faciles. Durée de 45 min à plusieurs heures.
- **Placement :** la majorité du volume hebdomadaire. En ultra, la **sortie longue** est la séance reine (progresser la durée avant l'intensité).
- **Piège :** courir trop vite. Si tu ne peux pas tenir une conversation, tu es trop haut.

### 2 — Endurance active / tempo (Z3)

- **Objectif :** soutenir l'allure aérobie, économie, allure spécifique marathon/ultra.
- **Formats :** tempo continu de 20-40 min ; blocs d'allure spécifique au sein d'une sortie longue (ex. derniers 30-45 min en Z3).
- **Placement :** en phase spécifique surtout. À doser — c'est la zone qu'on **limite** en approche polarisée.

### 3 — Seuil (Z4) — fort ROI

- **Objectif :** **élever le SV2/MLSS** et la clairance du lactate. L'une des séances les plus rentables en endurance.
- **Formats :**
  - **Intervalles au seuil** : `3 × 10 min` ou `4 × 8 min` autour de SV2, récup 2-3 min.
  - **« Cruise intervals »** : fractions de 5-8 min répétées.
  - **Seuil continu** : 20-30 min à SV2 (plus exigeant mentalement).
- **Placement :** 1 séance/semaine en phase de développement. Toujours sur jambes fraîches.

### 4 — VO2max / PMA (Z5)

- **Objectif :** repousser le **plafond aérobie**, la puissance aérobie maximale.
- **Formats :**
  - **Intervalles longs** : `5 × 3 min` ou `4 × 4 min` à ~95-100 % VO2max, récup ~égale au temps d'effort.
  - **Intervalles courts** : `30/30`, `40/20` (30 s dur / 30 s facile), efficaces pour accumuler du temps à haute intensité.
  - **Côtes** : répétitions de 2-4 min en montée raide (combine VO2max et force).
- **Placement :** 1 séance/semaine max en phase d'affûtage de la puissance. Très coûteuse en récupération.

### 5 — Vitesse & puissance neuromusculaire (> Z5)

- **Objectif :** recrutement neuromusculaire, **économie de course**, capacité anaérobie (W'), raideur musculo-tendineuse. *Pas* l'aérobie.
- **Formats :**
  - **Lignes droites (strides)** : 6-8 × 15-20 s en accélération fluide, récup complète. Excellent travail d'économie, peu fatigant — à glisser en fin de footing facile.
  - **Sprints courts** : 10-15 × 10-30 s à fond, récup longue.
  - **Sprints en côte** : 8-12 × 10-15 s en montée raide — force + puissance, faible impact.
- **Placement :** les strides peuvent être quasi quotidiens (entretien). Les sprints durs, 1 fois/semaine.

### 6 — Spécifique trail : côtes & descentes

- **Objectif :** force spécifique en montée, **tolérance excentrique** en descente (le vrai facteur limitant en ultra-trail : les dégâts musculaires des descentes).
- **Formats :**
  - **Montée :** répétitions de dénivelé (ex. `5-8 × 3 min` de grimpe), ou « vert » continu (D+ accumulé en Z2-Z3).
  - **Descente :** descentes techniques **progressivement** intégrées — le muscle s'habitue à la charge excentrique sur des semaines. À doser : très traumatisant, courbatures durables (DOMS).
- **Placement :** spécifique à ton objectif. La **résistance à la descente se construit lentement** — commencer tôt dans la prépa.

### Comment enchaîner ces séances ?

Une logique de **périodisation** classique : poser d'abord la **base** (volume Z1-Z2 + strides), puis ajouter le **seuil** (Z4), puis la **puissance** (Z5) et le **spécifique** (côtes/descentes) en se rapprochant de l'objectif, avant un **affûtage** (volume réduit, intensité maintenue) — c'est la phase où la TSB remonte (voir [1.5](#15-modéliser-fitness-et-fatigue--ctl--atl--tsb)). Règle d'or transversale : **une seule qualité dure à la fois par séance**, et jamais deux séances dures sans récupération entre elles (voir Monotonie, [1.6](#16-monotonie--strain)).

---

## 1.4 Quantifier la charge d'une séance

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
            + (min_Z4 × 4) + (min_Z5 × 5)
```

Chaque minute en zone N vaut N points. Plus grossier que la version exponentielle, mais immédiat puisque tes minutes par zone (`hr_z1_min` … `hr_z5_min`) sont déjà stockées. Bon compromis pour un suivi quotidien.

---

## 1.5 Modéliser fitness et fatigue : CTL / ATL / TSB

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

## 1.6 Monotonie & Strain

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

Complètent l'apport énergétique une fois glucides et protéines fixés. Plancher de ~1 g/kg/jour (≈ 20 % de l'énergie minimum) pour la fonction hormonale et l'absorption des vitamines liposolubles. Important hors séance ; on les réduit autour des efforts pour ne pas gêner la digestion. La *qualité* des lipides (profil en acides gras) est détaillée en [3.4](#34-les-acides-gras-essentiels--oméga-3--oméga-6).

---

## 3.3 Les acides aminés

Les protéines sont des chaînes de 20 acides aminés. Au-delà de la quantité (g/kg vue en 3.2), c'est leur **composition** qui détermine la qualité d'une source protéique et sa capacité à déclencher l'adaptation.

### Essentiels, non-essentiels, conditionnellement essentiels

```
ESSENTIELS (9) — l'organisme ne peut PAS les synthétiser, apport alimentaire obligatoire
  Histidine, Isoleucine, Leucine, Lysine, Méthionine,
  Phénylalanine, Thréonine, Tryptophane, Valine

NON-ESSENTIELS — synthétisables à partir d'autres composés

CONDITIONNELLEMENT ESSENTIELS — deviennent indispensables sous stress
  (maladie, effort intense prolongé) : glutamine, arginine, glycine...
```

Les **9 essentiels (EAA)** sont le facteur limitant : c'est leur disponibilité, et non l'azote total, qui pilote la synthèse protéique musculaire (MPS).

### La leucine — le déclencheur

Parmi les EAA, la **leucine** joue un rôle de signal : elle active la voie **mTOR**, principal interrupteur de la synthèse protéique. D'où la notion de **seuil leucine** (~2-3 g par prise) à atteindre pour "allumer" pleinement la MPS.

C'est aussi pourquoi **toutes les protéines ne se valent pas** :

| Source | Qualité (profil EAA + digestibilité) |
|--------|--------------------------------------|
| Animales (œuf, lait, viande, poisson) | Complètes, riches en leucine, hautement digestibles |
| Végétales isolées (sauf soja) | Souvent déficitaires en 1+ EAA (ex : lysine dans les céréales, méthionine dans les légumineuses) |

→ Une alimentation végétale doit **combiner** les sources (céréales + légumineuses) et viser un apport total un peu plus élevé pour compenser une teneur en leucine et une digestibilité moindres. C'est la notion de **complémentarité protéique**.

### Les BCAA (acides aminés à chaîne ramifiée)

**Leucine, isoleucine, valine.** Particularité : métabolisés directement dans le **muscle** (et non le foie), ils peuvent servir de substrat énergétique lors d'efforts prolongés qui épuisent le glycogène.

**⚠️ Débattu — l'hypothèse de la "fatigue centrale".**
Le raisonnement théorique : à l'effort long, les BCAA sont oxydés → leur taux plasmatique chute → le tryptophane libre (qui leur "fait concurrence" pour franchir la barrière hémato-encéphalique) entre plus facilement dans le cerveau → plus de **sérotonine** → sensation de fatigue centrale. La supplémentation en BCAA est censée retarder ce mécanisme.

**En pratique, les preuves sont faibles et incohérentes** en conditions réelles, surtout lorsque l'apport en **glucides est suffisant** (les glucides limitent eux-mêmes la montée du tryptophane libre). Verdict pragmatique : avec un apport glucidique correct à l'effort et des protéines suffisantes sur la journée, **la supplémentation isolée en BCAA n'apporte pas grand-chose**. Mieux vaut viser des protéines complètes (qui contiennent les BCAA *et* les autres EAA).

### La glutamine

Acide aminé le plus abondant du plasma. Impliquée dans la **fonction immunitaire** et l'**intégrité de la barrière intestinale**. Son taux plasmatique chute après un effort intense/prolongé, ce qui a nourri la théorie de la "fenêtre immunitaire ouverte" post-effort.

**⚠️ Débattu :** la supplémentation en glutamine pour soutenir l'immunité ou la performance a des **preuves globalement décevantes** chez l'athlète bien nourri. Un intérêt possible subsiste pour le confort digestif sur les très longs formats, mais sans consensus fort.

### Acides aminés à visée ergogénique (hors construction protéique)

Quelques dérivés d'acides aminés ont un intérêt documenté, surtout pour les **efforts à haute intensité** (relances, bosses, sprints) plus que pour l'ultra-endurance pure :

| Composé | Mécanisme | Niveau de preuve |
|---------|-----------|------------------|
| **Bêta-alanine** | Précurseur de la **carnosine** musculaire (tampon contre l'acidose). Bénéfice sur efforts de ~1-4 min. | Solide pour la haute intensité |
| **Citrulline / arginine** | Précurseurs du **monoxyde d'azote** (NO) — vasodilatation, débit sanguin. | ⚠️ Modeste, variable |
| **Taurine** | Présente dans le muscle, rôle dans la contraction et l'antioxydation. | ⚠️ Émergent, incertain |

Pour un profil ultra-trail, **la bêta-alanine** peut avoir un intérêt sur les portions explosives (montées raides), mais reste secondaire devant les fondamentaux (volume, glucides, récup).

### Synthèse pratique — acides aminés

- Vise des **protéines complètes** réparties en prises de ~20-40 g (≥ seuil leucine).
- Une **prise post-effort** combinant protéines + glucides optimise la récupération (réparation + recharge glycogénique).
- **Oublie les BCAA isolés** si ton alimentation est correcte : redondants.
- Les acides aminés "ergogéniques" (bêta-alanine surtout) sont un *bonus* ciblé, pas une base.

---

## 3.4 Les acides gras essentiels : oméga-3 & oméga-6

Deux familles d'acides gras polyinsaturés que l'organisme **ne peut pas synthétiser** : ce sont les seuls lipides réellement "essentiels".

```
OMÉGA-3 — chef de file : acide alpha-linolénique (ALA)
  — se convertit (mal) en EPA et DHA, les formes biologiquement actives

OMÉGA-6 — chef de file : acide linoléique (LA)
  — se convertit en acide arachidonique (AA)
```

### Pourquoi ils comptent

Ces acides gras ont deux rôles majeurs :

1. **Structure membranaire** : ils s'intègrent aux membranes cellulaires et en règlent la **fluidité** (impact sur la fonction des récepteurs, le transport, etc.). Le DHA est particulièrement concentré dans le cerveau et la rétine.
2. **Précurseurs des eicosanoïdes** : molécules de signalisation qui modulent l'**inflammation**.
   - Les dérivés d'**oméga-3 (EPA/DHA)** — eicosanoïdes plutôt **anti-inflammatoires / résolvants**.
   - Les dérivés d'**oméga-6 (AA)** — eicosanoïdes plutôt **pro-inflammatoires**.

⚠️ Attention au raccourci : l'oméga-6 n'est **pas** "mauvais". L'acide arachidonique et l'inflammation aiguë sont **nécessaires** (réparation tissulaire, adaptation à l'entraînement). Le problème est un **déséquilibre chronique**, pas la présence d'oméga-6.

### La question du ratio

L'alimentation occidentale moderne fournit un ratio oméga-6:oméga-3 de l'ordre de **15-20:1**, contre un ratio ancestral estimé à **~1-4:1** (excès d'huiles végétales raffinées riches en LA, déficit en poissons gras).

**⚠️ Débattu :** le cadre "ratio" est utile pédagogiquement mais **contesté**. Pour beaucoup de chercheurs, **l'apport absolu d'EPA + DHA** est un meilleur déterminant que le ratio lui-même. Autrement dit : augmenter les oméga-3 (EPA/DHA) prime sur l'obsession du dénominateur oméga-6.

### Le piège de la conversion

L'**ALA végétal** (lin, chia, noix) ne se convertit en EPA/DHA qu'à **~5-10 % (EPA) et < 1-5 % (DHA)**. Conséquence directe :

| Source | Apporte |
|--------|---------|
| Poissons gras (saumon, maquereau, sardine, hareng) | EPA + DHA **directement** (forme active) |
| Huile d'algue | EPA + DHA directement — **option végane** |
| Lin, chia, noix | **ALA seulement** — conversion faible, ne suffit pas à couvrir les besoins en DHA |

→ Compter uniquement sur les graines pour ses oméga-3 actifs est une erreur fréquente. Pour un végétarien/végan, **l'huile d'algue** est la voie fiable.

### Intérêt pour l'athlète d'endurance

- **Gestion de l'inflammation** et possible amélioration de la **récupération** (courbatures, marqueurs inflammatoires).
- Bénéfices **cardiovasculaires** établis.
- Effets potentiels sur la fonction neuromusculaire et la synthèse protéique (émergent).

**⚠️ Nuance d'adaptation :** par analogie avec les antioxydants (voir 3.5), on pourrait craindre qu'émousser systématiquement l'inflammation post-effort nuise à l'adaptation. Pour les oméga-3 aux doses usuelles, **les données ne montrent globalement pas cet effet délétère** — ils sont considérés comme bénéfiques ou neutres. La prudence reste de mise pour les **mégadoses**.

### Repères pratiques — oméga-3

| Objectif | EPA + DHA / jour |
|----------|-------------------|
| Santé générale | ~250-500 mg |
| Athlète (gestion inflammation/récup) | ~1-2 g (souvent cité, ⚠️ sans consensus ferme) |

Le plus simple : **2-3 portions de poissons gras par semaine** couvrent l'essentiel. À défaut, une supplémentation EPA/DHA (ou huile d'algue) de qualité, en parallèle d'une **réduction des huiles végétales raffinées** riches en oméga-6.

---

## 3.5 Les micronutriments

Vitamines et minéraux ne fournissent **aucune énergie**, mais sont les **cofacteurs** indispensables au métabolisme. Chez l'athlète d'endurance, les besoins sont accrus (pertes sudorales, turnover élevé, stress oxydatif) et certaines carences ont un **impact direct et démontré** sur la performance.

### Le fer — le minéral critique de l'endurance

Le plus important à surveiller. Composant de l'**hémoglobine** (transport de l'O₂), de la **myoglobine** (O₂ musculaire) et d'enzymes mitochondriales. Une carence dégrade directement le transport d'oxygène — la performance aérobie.

**Pourquoi l'athlète d'endurance est à risque élevé :**

```
- Hémolyse d'impact (destruction de globules rouges à chaque foulée, surtout en course)
- Pertes digestives microscopiques
- Pertes sudorales
- Menstruations (femmes)
- Hepcidine : l'inflammation post-effort élève cette hormone qui BLOQUE
  l'absorption intestinale du fer pendant plusieurs heures
```

**Point crucial :** une **carence sans anémie** (ferritine basse, hémoglobine encore normale) **dégrade déjà la performance** et la récupération. Le marqueur à suivre est la **ferritine**, pas seulement l'hémoglobine.

**Optimiser l'absorption :**

| Favorise | Inhibe |
|----------|--------|
| Fer héminique (viande, poisson) — bien mieux absorbé | Thé, café (tanins) autour du repas |
| Vitamine C avec le fer non-héminique (végétal) | Calcium en même temps que le fer |
| Prise du fer **loin de l'effort** (hepcidine basse, ex : matin au repos) | Prise juste après une séance (hepcidine haute) |

**⚠️ Ne jamais se supplémenter en fer "à l'aveugle".** La **surcharge en fer est toxique** (foie, stress oxydatif). On teste (bilan martial : ferritine, coefficient de saturation) **avant** de supplémenter, idéalement avec un suivi médical.

### Vitamine D

Synthétisée par la peau sous UV. Rôles : **santé osseuse** (avec calcium), **fonction musculaire**, **immunité**.

**Pertinence locale :** carence **très fréquente en hiver et aux latitudes nord** (faible ensoleillement) — un enjeu réel dans une région alpine comme **Annecy** de novembre à mars. Un bilan en fin d'hiver est pertinent, et une supplémentation hivernale souvent justifiée (à doser selon le statut).

### Magnésium

Cofacteur de **300+ réactions enzymatiques**, dont le métabolisme de l'**ATP** et la fonction neuromusculaire. Perdu dans la sueur, besoins accrus à fort volume.

**⚠️ Débattu :** le lien magnésium — **crampes** est populaire mais **mal étayé** — les crampes d'effort relèvent surtout de la fatigue neuromusculaire, pas systématiquement d'un déficit en magnésium. Couvrir ses besoins reste utile pour le métabolisme énergétique ; n'attends pas un effet miracle anti-crampes.

### Calcium

**Santé osseuse** et contraction musculaire. Enjeu majeur à fort volume d'impact (course, dénivelé) et en cas de **déficit énergétique** : un apport énergétique insuffisant (RED-S, voir ci-dessous) fragilise l'os malgré un calcium correct.

### Zinc

**Immunité**, cicatrisation, synthèse protéique. Perdu dans la sueur — besoins légèrement accrus chez l'athlète. Carence associée à une fonction immunitaire diminuée.

### Vitamines du groupe B

Cofacteurs du **métabolisme énergétique** (B1, B2, B3, B6...) et de la production de globules rouges (**B9 folate, B12**). Généralement couvertes par un apport énergétique et une alimentation variés.

**Point d'attention végan/végétarien :** la **B12** est quasi absente du végétal — **supplémentation indispensable** en régime végan. Folates et B12 conditionnent aussi la production de globules rouges, en lien avec le transport d'O₂.

### Vitamines antioxydantes (C, E) — la nuance contre-intuitive

**⚠️ Important — ne pas mégadoser.** Réflexe courant : avaler de fortes doses de vitamine C/E pour "mieux récupérer". **Contre-productif.** Les **espèces réactives de l'oxygène (ROS)** produites à l'effort ne sont pas que des déchets : ce sont des **signaux** qui déclenchent une partie des adaptations (biogenèse mitochondriale). Saturer l'organisme d'antioxydants **émousse ces signaux** et peut **réduire les bénéfices de l'entraînement**.

→ Règle : couvrir ses besoins antioxydants **par l'alimentation** (fruits, légumes, variété), **pas par des mégadoses** de compléments en période d'entraînement.

### RED-S — le contexte qui chapeaute tout

**Relative Energy Deficiency in Sport.** Un apport énergétique chroniquement insuffisant par rapport à la dépense (souvent involontaire à fort volume) perturbe l'ensemble du système : **santé osseuse, hormones, immunité, performance**. Aucune optimisation micronutritionnelle ne compense un **déficit énergétique** de fond. C'est le garde-fou n°1 : **couvrir d'abord l'énergie totale**, ensuite affiner les micronutriments.

### Synthèse pratique — micronutriments

- **Fer** : le surveiller (ferritine), surtout en course et chez la femme. Tester avant de supplémenter.
- **Vitamine D** : bilan/supplémentation hivernale pertinents en région alpine.
- **Antioxydants (C/E)** : par l'alimentation, **pas de mégadoses**.
- **B12** : supplémentation obligatoire si végan.
- **Base de tout** : un apport énergétique suffisant (éviter le RED-S) et une alimentation variée couvrent l'essentiel ; la supplémentation cible les déficits **objectivés**, pas l'inverse.

---

## 3.6 Périodisation glucidique

Concept moderne : **adapter l'apport glucidique à la demande du jour** ("fuel for the work required", Impey & coll.), plutôt qu'un apport élevé uniforme.

- **Train high** : glycogène plein avant les séances clés (intensité, séances longues spécifiques) — qualité d'exécution.
- **Train low** : certaines séances faciles réalisées avec un glycogène réduit — stimule des **adaptations mitochondriales** et l'oxydation des lipides.

**⚠️ Débattu / à manier avec prudence :** le "train low" a un coût (qualité de séance réduite, stress immunitaire, risque accru de blessure si mal dosé). C'est un outil avancé, à utiliser ponctuellement et sur des séances *faciles*, jamais sur les séances de qualité.

---

## 3.7 Nutrition d'effort (longues sorties & course)

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

Tolérer 90 g/h ne s'improvise pas : l'intestin **s'entraîne**. Habituer progressivement le système digestif à de fortes charges glucidiques à l'effort réduit les troubles gastro-intestinaux le jour J. À travaillerr à l'entraînement, comme le reste.

---

## 3.8 Hydratation

Hautement individuelle (le taux de sudation varie d'un facteur 3-4 entre individus).

- **Volume** : ~0.4 – 0.8 L/h selon la chaleur et le taux de sudation. Se peser avant/après une longue séance donne une estimation directe des pertes (1 kg perdu ≈ 1 L).
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
| **TSB** | Training Stress Balance — fraîcheur (CTL — ATL) |
| **sRPE** | Charge perçue = RPE × durée |
| **RPE** | Effort perçu, échelle 1-10 |
| **TRIMP** | Training Impulse — charge basée sur la FC |
| **RMSSD** | Marqueur HRV de référence, médié par le nerf vague |
| **SDNN** | Variabilité globale des intervalles RR |
| **PNS / SNS** | Branches parasympathique / sympathique du SNA |
| **SV1 / SV2** | Seuils ventilatoires 1 (aérobie) et 2 (anaérobie) |
| **MLSS** | Maximal Lactate Steady State — proche de SV2 |
| **FatMax** | Intensité d'oxydation maximale des lipides |
| **VO2max** | Consommation maximale d'oxygène — plafond aérobie |
| **vVO2max** | Vitesse associée à VO2max |
| **PMA** | Puissance aérobie maximale (équivalent vélo de vVO2max) |
| **LTHR** | Fréquence cardiaque au seuil (Lactate Threshold HR) |
| **DFA α1** | Indice HRV (detrended fluctuation analysis) estimant les seuils à l'effort |
| **VDOT** | Indice de performance de Daniels, dérivé d'un temps de course |
| **Économie de course** | Coût énergétique à allure donnée — déterminant majeur de la perf |
| **DOMS** | Courbatures à retardement (dégâts musculaires, surtout en descente) |
| **W'** | Réserve de travail au-dessus de la puissance critique (capacité anaérobie) |
| **BMR** | Métabolisme de base |
| **TDEE** | Dépense énergétique totale quotidienne |
| **NEAT** | Dépense d'activité hors exercice structuré |
| **EAA** | Acides aminés essentiels (9), non synthétisables |
| **BCAA** | Acides aminés à chaîne ramifiée (leucine, isoleucine, valine) |
| **mTOR** | Voie de signalisation déclenchant la synthèse protéique |
| **MPS** | Synthèse protéique musculaire |
| **EPA / DHA** | Oméga-3 actifs (issus du poisson/algue ou de la conversion de l'ALA) |
| **ALA** | Acide alpha-linolénique — oméga-3 végétal, mal converti en EPA/DHA |
| **LA / AA** | Acide linoléique (oméga-6) / acide arachidonique (son dérivé) |
| **Ferritine** | Marqueur des réserves en fer (à surveiller en endurance) |
| **Hepcidine** | Hormone qui bloque l'absorption du fer ; élevée après l'effort |
| **ROS** | Espèces réactives de l'oxygène — déchets *et* signaux d'adaptation |
| **RED-S** | Déficit énergétique relatif dans le sport |

---

## Références

Sélection de sources fondatrices pour approfondir :

- **Banister EW** (1991) — modèle impulse-response fitness/fatigue (base de CTL/ATL/TSB et du TRIMP).
- **Foster C** (1998) — *Monitoring training in athletes with reference to overtraining syndrome* (sRPE, monotonie, strain).
- **Seiler S** (2010) — *What is best practice for training intensity and duration distribution?* (modèle polarisé).
- **Daniels J** — *Daniels' Running Formula* (VDOT, allures d'entraînement par qualité).
- **Billat V** — travaux sur la vVO2max et l'entraînement intermittent à VO2max.
- **Laursen P & Buchheit M** — *Science and Application of High-Intensity Interval Training* (formats HIIT, dosage).
- **Rogers B & Gronwald T** (2022) — DFA alpha-1 comme estimateur des seuils sur le terrain.
- **Tanaka H et coll.** (2001) — équation de prédiction de la FCmax (208 − 0.7 × âge).
- **Jeukendrup AE** — travaux sur l'oxydation des glucides exogènes et les glucides multi-transportables.
- **Burke LM, Impey SG et coll.** — périodisation glucidique, "fuel for the work required".
- **Brooks GA** — concept du point de crossover des substrats.
- **Shaffer F & Ginsberg JP** (2017) — *An Overview of Heart Rate Variability Metrics and Norms* (référence sur l'interprétation des métriques HRV, y compris les limites de la LF).
- **Documentation Kubios HRV** — définition des indices PNS/SNS et du Readiness.
- **ACSM / IOC Consensus on Nutrition for Athletes** — recommandations macronutriments.
- **Phillips SM & van Loon LJC** — besoins protéiques et rôle de la leucine/EAA dans l'adaptation.
- **Calder PC** — oméga-3, eicosanoïdes et inflammation.
- **Sim M, Garvican-Lewis LA et coll.** — métabolisme du fer chez l'athlète, rôle de l'hepcidine.
- **Larson-Meyer DE, Willis KS** — vitamine D et performance.
- **Powers SK, Jackson MJ** — ROS comme signaux d'adaptation, effet contre-productif des antioxydants à haute dose.
- **Mountjoy M et coll.** (IOC Consensus) — syndrome RED-S.

---

*Cette documentation est un support pédagogique fondé sur la littérature en physiologie de l'exercice. Elle ne remplace pas un suivi médical ou un accompagnement par un professionnel qualifié.*
