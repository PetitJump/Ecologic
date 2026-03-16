# Ecologic — Présentation du projet

---

## 1 — Présentation globale du projet

### Naissance de l'idée

En dehors des cours, nous avons toujours aimé coder des simulations pour le plaisir et explorer la puissance de calcul des ordinateurs. Quand le thème "Nature & Informatique" a été annoncé en septembre 2025, l'idée d'une simulation d'écosystème s'est imposée naturellement : c'était l'occasion de concevoir de vrais algorithmes complexes tout en répondant au thème du concours.

### Problématique initiale

Comment modéliser numériquement la dynamique d'un écosystème loups / cerfs / herbe de façon réaliste et interactive, en s'appuyant sur des modèles mathématiques solides ?

### Objectifs

- Implémenter un moteur de simulation biologique s'appuyant sur des modèles mathématiques réels (croissance logistique, mortalité proportionnelle, capacité de charge)
- Proposer une interface web fluide et accessible permettant de visualiser les populations en temps réel
- Offrir un système de paramètres modifiables pour comprendre l'impact de chaque variable biologique
- Rendre la simulation ludique grâce à un système de succès et d'événements météo aléatoires

---

## 2 — Organisation du travail

### Présentation de l'équipe

Équipe de 4 élèves de Terminale NSI.

| Membre   | Rôle principal                                        |
|----------|-------------------------------------------------------|
| Killian  | Algorithmique principale                              |
| Carl     | Algorithmique, phase de tests                         |
| Margaux  | Algorithmique, gestion des données, Flask et routes   |
| Hugo     | Flask, algorithmique, HTML, routes, phase de tests    |

### Répartition des tâches

- **Killian** : conception et développement du cœur algorithmique de la simulation (`algo.py`), modèle de reproduction, de mortalité et de prédation
- **Carl** : développement algorithmique, phase de tests et détection de bugs
- **Margaux** : algorithmique liée à la gestion des données (`data.json`, `meteo.json`), mise en place de Flask et des routes principales
- **Hugo** : amélioration des routes Flask avec les derniers algorithmes, structure HTML initiale, phase de tests

### Temps passé sur le projet

Nous avons commencé dès l'annonce du thème en septembre 2025, soit environ 6 mois de développement. Chaque membre a consacré en moyenne 4 à 6 heures par semaine au projet.

---

## 3 — Présentation des étapes du projet

### Étape 1 — Simulation en ligne de commande

Nous avons commencé par développer entièrement la logique de simulation dans le terminal, sans interface. L'objectif était d'avoir un algorithme solide et cohérent avant de penser à la présentation. Le code était écrit de façon procédurale, sans programmation orientée objet, et les paramètres biologiques (reproduction, chasse, mortalité) étaient codés directement en dur dans le programme.

### Étape 2 — Première intégration Flask

Une fois la simulation fonctionnelle en terminal, nous avons intégré Flask pour avoir un premier rendu visuel dans le navigateur. Cette version était très minimaliste : pas de CSS, pas de JavaScript, juste les données affichées sous forme de texte. L'objectif était de valider le passage de la logique Python vers le web.

### Étape 3 — Refonte complète en programmation orientée objet

Pour permettre à l'utilisateur de modifier les paramètres et d'interagir vraiment avec la simulation, nous avons réécrit entièrement `algo.py` en programmation orientée objet. Nous avons créé les classes `Predateur`, `Proie`, `Vegetal`, `Meute` et `Jeu`, chaque individu ayant son propre âge et ses propres caractéristiques. Ce changement profond a entraîné une refonte de toute l'architecture du projet, Flask inclus.

### Étape 4 — Paramètres dynamiques et stockage JSON

Les données biologiques ont été externalisées dans un fichier `data.json`, modifiable depuis l'interface. Nous avons testé plusieurs approches pour stocker et transmettre les valeurs entre les pages Flask (variables globales, fichiers JSON, sessions). Nous avons finalement opté pour une combinaison de sessions Flask et de fichiers JSON pour les paramètres persistants.

### Étape 5 — Tests utilisateurs et améliorations algorithmiques

Nous avons fait tester le projet à plusieurs proches pour recueillir leurs retours. Ces tests ont mis en évidence des problèmes d'équilibre (parties trop courtes, extinctions trop rapides) et des bugs dans la prise en compte des paramètres. Nous avons progressivement affiné le modèle biologique : broutage progressif des cerfs, reproduction liée à la disponibilité de l'herbe, calibrage des taux de survie.

### Étape 6 — Interface visuelle avec Claude

Pour obtenir une interface soignée et des visualisations de qualité dans les délais du concours, nous avons utilisé Claude (IA d'Anthropic) comme assistant pour développer l'interface graphique. Cela nous a permis d'intégrer un graphique double axe animé en canvas JavaScript pur, un système de donuts de population, une bannière de prévisions et un style documentaire cohérent.

### Étape 7 — Système de succès

Le dernier ajout a été un système de 9 succès débloquables, sauvegardés entre les parties. Cet ajout rend la simulation plus ludique et encourage le joueur à explorer différentes configurations (atteindre exactement 100 loups, survivre à une sécheresse, tenir 20 ans…).

---

## 4 — Validation du fonctionnement

### État d'avancement

Le projet est complet et fonctionnel. Toutes les fonctionnalités prévues sont implémentées :
- Simulation tour par tour avec graphiques en temps réel
- Paramètres biologiques modifiables depuis l'interface
- Événements météo aléatoires (sécheresse, hiver, incendie, pluies, printemps)
- Système de 9 succès permanents inter-parties
- Mode accéléré (simuler plusieurs années d'un coup)
- Page de fin avec récapitulatif complet de la partie

### Approches pour vérifier l'absence de bugs

- Tests manuels répétés avec différentes configurations de départ
- Tests utilisateurs auprès de proches pour détecter des comportements inattendus
- Simulations automatiques en boucle (50 parties) pour valider la durée moyenne et l'équilibre général
- Vérification que les paramètres configurés sont bien pris en compte par le moteur de simulation

### Difficultés rencontrées et solutions

| Difficulté | Solution apportée |
|------------|-------------------|
| La fonction `random_repro` écrasait les paramètres configurés par l'utilisateur | Suppression de cette fonction, randomisation directement dans `naissance()` en respectant les fourchettes `[min, max]` configurées |
| Les cerfs ne mangeaient pas réellement l'herbe (paramètre ignoré) | Ajout d'une logique de broutage explicite avec mortalité progressive selon la disponibilité de l'herbe |
| Parties trop courtes (extinction en moins de 15 ans) | Calibrage du modèle logistique, réduction des portées, lien entre reproduction des cerfs et quantité d'herbe disponible |
| Passage de la version procédurale à la version orientée objet | Réécriture complète de `algo.py` et adaptation de toutes les routes Flask |

---

## 5 — Ouverture

### Idées d'amélioration

- Ajouter une troisième espèce animale (renard, ours)
- Système de zones géographiques avec migration entre zones
- Mode multijoueur : chaque joueur gère une espèce
- Export CSV de l'historique pour analyse externe
- Visualisation cartographique de l'écosystème

### Analyse critique

Le modèle reste une simplification de la réalité : les individus n'ont pas de position spatiale, la reproduction est discrète (tous les X ans) plutôt que continue, et certains comportements collectifs (meutes, migrations) ne sont pas modélisés. Un modèle plus réaliste utiliserait des équations différentielles continues ou une simulation agent-based avec positions spatiales.

### Compétences personnelles développées

- Modélisation mathématique appliquée à la biologie (modèle logistique, dynamique prédateur-proie)
- Développement web full-stack avec Flask
- Programmation orientée objet en Python
- Débogage et tests de simulation
- Visualisation de données en JavaScript pur (canvas)
- Travail collaboratif et itératif sur un projet de longue durée

### Démarche d'inclusion

Nous avons veillé à ce que chaque membre de l'équipe contribue à des aspects techniques variés, sans se limiter à un seul domaine. L'interface a été conçue pour être accessible : contrastes suffisants, textes explicatifs dans les paramètres, descriptions des événements météo en langage simple.