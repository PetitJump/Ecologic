# Naturalia — Guide de lancement

## Prérequis

- Python 3.10 ou supérieur
- pip

## Installation

Cloner ou télécharger le projet, puis depuis le répertoire racine :

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

Ouvrir ensuite un navigateur et aller à l'adresse : [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Structure du projet

```
naturalia/
├── main.py                  ← point d'entrée (lancer ce fichier)
├── app.py                   ← routes Flask et logique principale
├── algo.py                  ← moteur de simulation (classes Jeu, Meute, etc.)
├── petites_fonctions.py     ← fonctions utilitaires
├── data.json                ← paramètres biologiques de la simulation
├── meteo.json               ← événements météorologiques
├── succes_permanents.json   ← sauvegarde des succès débloqués (généré automatiquement)
├── static/
│   ├── style.css            ← feuille de style (thème documentaire)
│   ├── app.js               ← interactions sliders page d'initialisation
│   └── regle.js             ← validation formulaire paramètres
└── templates/
    ├── index.html           ← page d'accueil
    ├── init.html            ← configuration des populations de départ
    ├── game.html            ← interface de jeu principale
    ├── fin.html             ← écran de fin de partie
    ├── parametre.html       ← réglages biologiques
    └── ajouter.html         ← ajout manuel d'individus
```

## Remarques

- Le fichier `succes_permanents.json` est créé automatiquement au premier lancement.
- Les paramètres biologiques peuvent être modifiés depuis l'interface (page Paramètres) ou directement dans `data.json`.
- Le projet ne nécessite pas de base de données ni de connexion internet.
