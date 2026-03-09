# Naturalia — Présentation du projet

---

## 1 — Présentation globale du projet

### Naissance de l'idée

L'idée de Naturalia est née d'une question simple : comment fonctionne réellement un écosystème ? Nous voulions créer une simulation qui montre de façon concrète et interactive les relations entre prédateurs, proies et végétaux — et comment une perturbation (météo, surpopulation, extinction) peut déséquilibrer l'ensemble.

Le thème "Nature & Informatique" des Trophées NSI 2026 correspondait exactement à notre projet.

### Problématique initiale

Comment modéliser numériquement la dynamique d'un écosystème loups / cerfs / herbe de façon réaliste, interactive et pédagogique ?

### Objectifs

- Implémenter un moteur de simulation biologique s'appuyant sur des modèles mathématiques réels (croissance logistique, mortalité proportionnelle, capacité de charge)
- Proposer une interface web fluide et accessible permettant de visualiser les populations en temps réel
- Offrir un système de paramètres modifiables pour comprendre l'impact de chaque variable
- Rendre la simulation ludique grâce à un système de succès et d'événements météo aléatoires

---

## 2 — Organisation du travail

### Présentation de l'équipe

Équipe de 4 élèves, classe de [Première / Terminale] NSI.

| Membre   | Rôle principal                          |
|----------|-----------------------------------------|
| Margot   | Flask (routes), algorithmique           |
| Hugo     | HTML / CSS / JavaScript, algorithmique  |
| Carl     | Flask, algorithmique, JSON              |
| Killian  | Algorithmique principale, JSON          |

### Répartition des tâches

- **Killian** : moteur de simulation (`algo.py`, `petites_fonctions.py`), modèle mathématique de croissance logistique, paramétrage biologique (`data.json`, `meteo.json`)
- **Carl** : routes Flask (`app.py`), gestion de session, système de succès permanents, logique de jeu
- **Margot** : routes Flask, page paramètres, formulaires, validation des données
- **Hugo** : interface utilisateur (HTML/CSS/JS), graphiques canvas double axe, animations, style documentaire

### Temps passé sur le projet

Environ [X] heures par membre sur [Y] semaines.

---

## 3 — Présentation des étapes du projet

### Phase 1 — Conception du modèle biologique

Nous avons commencé par définir les règles biologiques : comment les loups chassent les cerfs, comment les cerfs broutent l'herbe, comment chaque espèce se reproduit. Nous avons étudié le modèle de Lotka-Volterra (prédateur-proie) et le modèle logistique pour l'herbe, puis nous les avons adaptés à notre simulation discrète (par année).

### Phase 2 — Implémentation du moteur (`algo.py`)

Création des classes `Predateur`, `Proie`, `Vegetal`, `Meute`, `Jeu`. Chaque individu a un âge, une mortalité naturelle, et participe à la dynamique de population. La reproduction est probabiliste : chaque couple a une chance de donner des petits selon les paramètres configurés.

### Phase 3 — Interface Flask

Mise en place des routes : initialisation de la simulation, tour par tour, paramètres, page de fin. Gestion de la session pour conserver l'état entre les requêtes. Système de succès sauvegardés sur disque entre les parties.

### Phase 4 — Interface utilisateur

Développement de l'interface en HTML/CSS/JS avec un style "documentaire naturaliste" (fond crème, typographie Playfair Display). Graphique double axe animé en canvas pur (sans bibliothèque externe), donut de répartition, journal de bord, bannière de prévisions.

### Phase 5 — Équilibrage et tests

Nombreuses simulations pour calibrer les paramètres par défaut : durée de vie, taux de reproduction, capacité de charge de l'herbe. Correction de bugs (notamment la randomisation qui écrasait les paramètres utilisateur).

---

## 4 — Validation du fonctionnement

### État d'avancement

Le projet est complet et fonctionnel. Toutes les fonctionnalités prévues sont implémentées :
- Simulation tour par tour avec graphiques temps réel
- Paramètres biologiques modifiables
- Événements météo aléatoires (sécheresse, hiver, incendie, pluies, printemps)
- Système de 9 succès permanents inter-parties
- Mode accéléré (simuler X années d'un coup)
- Page de fin avec récapitulatif complet

### Approches pour vérifier l'absence de bugs

- Tests manuels de nombreuses parties avec différentes configurations
- Simulations automatiques (50 parties en boucle) pour valider l'équilibre et la durée moyenne
- Vérification de la syntaxe Python avec `ast.parse()`
- Test que les paramètres configurés sont bien respectés (suppression du bug `random_repro`)

### Difficultés rencontrées et solutions

| Difficulté | Solution apportée |
|------------|-------------------|
| La fonction `random_repro` écrasait les paramètres configurés par l'utilisateur | Suppression de `random_repro`, randomisation directement dans `naissance()` en respectant les fourchettes `[min, max]` |
| Les cerfs ne mangeaient pas l'herbe (paramètre ignoré) | Ajout d'une logique de broutage explicite dans `mort()` avec mortalité proportionnelle au manque d'herbe |
| Parties trop courtes (extinction en 10 ans) | Calibrage du modèle logistique, réduction de la taille des portées, lien entre repro des cerfs et disponibilité de l'herbe |
| Explosions démographiques brutales | Remplacement du nombre absolu de naissances par un taux probabiliste par couple |

---

## 5 — Ouverture

### Idées d'amélioration

- Ajouter une troisième espèce animale (renard, ours)
- Système de zones géographiques avec migration entre zones
- Mode multijoueur : chaque joueur gère une espèce
- Visualisation cartographique de l'écosystème
- Export CSV de l'historique pour analyse externe

### Analyse critique

Le modèle reste une simplification de la réalité : les individus n'ont pas de position spatiale, la reproduction est synchrone (tous les X ans au lieu de continue), et certains paramètres biologiques (maturité sexuelle fixe à 2 ans) ne varient pas. Un modèle plus réaliste utiliserait des équations différentielles continues ou une simulation agent-based avec positions spatiales.

### Compétences personnelles développées

- Modélisation mathématique appliquée à la biologie
- Développement web full-stack avec Flask
- Programmation orientée objet en Python
- Débogage et tests de simulation
- Visualisation de données en JavaScript pur (canvas)
- Collaboration avec Git

### Démarche d'inclusion

Nous avons veillé à ce que chaque membre de l'équipe contribue à des aspects techniques variés. L'interface a été conçue pour être accessible : contrastes suffisants, textes explicatifs dans les paramètres, descriptions des événements en langage simple.
