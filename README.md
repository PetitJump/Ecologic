# Ecologic

Toute la logique du projet (algorithmes de simulation, routes Flask, base de données) a été écrite à la main par les membres de l'équipe. L'interface graphique a été développée avec l'aide d'une intelligence artificielle.
Ce README a également été rédigé avec l'aide d'une intelligence artificielle.

## Le projet en quelques mots

Ecologic est un simulateur d'écosystème qui tourne dans le navigateur. On y observe trois espèces qui vivent ensemble : des loups, des cerfs et de l'herbe. Chaque tour de jeu représente une année. Les loups chassent les cerfs, les cerfs broutent l'herbe, l'herbe repousse, et tout ce petit monde vieillit, se reproduit et meurt selon des règles biologiques précises. Le but du joueur est de garder cet équilibre vivant le plus longtemps possible, sachant qu'une espèce qui disparaît entraîne souvent les autres dans sa chute.

Rien n'est laissé au hasard total : la croissance de l'herbe suit l'équation logistique de Verhulst, un modèle mathématique réel utilisé en écologie pour décrire une population qui grandit puis plafonne quand les ressources deviennent limitées. La reproduction des cerfs dépend directement de la quantité d'herbe disponible par individu, et la famine ne tue pas tout le troupeau d'un coup mais frappe proportionnellement au manque. Chaque animal est un objet Python avec son âge propre, ce qui permet de gérer la maturité sexuelle, la mortalité infantile et la mort de vieillesse individuellement.

Le joueur peut modifier tous les paramètres biologiques depuis l'interface (fréquence de reproduction, taille des portées, âge de maturité, quantité de nourriture consommée) et voir immédiatement l'effet sur la simulation. Des événements météo aléatoires viennent perturber l'équilibre : sécheresse, pluies abondantes, hiver rigoureux, incendie, printemps précoce, chacun avec sa probabilité et son impact chiffré sur chaque espèce. Un mode accéléré permet de simuler plusieurs années d'un coup, et neuf succès sont déblocables pour encourager le joueur à tester des configurations extrêmes.

Techniquement, le projet repose sur Flask pour le serveur web, SQLite pour les comptes joueurs et la sauvegarde des succès et statistiques, et du JavaScript pur (sans aucune bibliothèque externe) pour les graphiques animés en canvas qui affichent l'évolution des populations en temps réel. Les mots de passe sont hachés avec Werkzeug. Un outil en ligne de commande permet aussi d'administrer la base de données (lister les comptes, consulter le classement, exporter en CSV).

## Contexte du projet

Ecologic a été réalisé dans le cadre des Trophées NSI, concours national porté par l'Éducation nationale et ouvert aux élèves de spécialité Numérique et Sciences Informatiques. Le thème de l'édition, annoncé en décembre 2025, était "Nature et Informatique". Le projet a remporté le prix du meilleur projet de l'académie de Montpellier.

Quelques chiffres :

• Environ 4968 lignes de code au total, réparties entre Python, HTML, CSS et JavaScript
• 1396 lignes de Python, dont 839 pour le serveur Flask et 229 pour le moteur de simulation
• Quatre mois de développement, de décembre 2025 à mars 2026
• Une équipe de quatre personnes : PetitJump, Hoshi9244, kyniops et Nekosama20

PetitJump tenait le rôle de chef de projet : conception et écriture du cœur algorithmique de la simulation (le fichier algo.py), répartition des tâches entre les membres selon leurs affinités, arbitrage des choix techniques comme le passage du procédural à la programmation orientée objet, relecture et intégration du travail de chacun, tenue du calendrier du concours.

## Comment le lancer

Il faut Python 3.10 ou supérieur.

1. Récupérer le dépôt :

```bash
git clone https://github.com/PetitJump/Ecologic.git
```

2. Installer la seule dépendance nécessaire, Flask :

```bash
pip install flask
```

3. Se placer dans le dossier sources et lancer le serveur :

```bash
cd Ecologic/sources && python3 main.py
```

4. Ouvrir un navigateur à l'adresse http://127.0.0.1:5000

La base de données SQLite est créée automatiquement au premier lancement. Il est possible de jouer en tant qu'invité, mais créer un compte permet de conserver ses succès et ses statistiques entre les parties.

Pour administrer la base de données depuis le terminal :

```bash
cd Ecologic/sources/SQL && python3 base_donnee.py --help
```
