# Ecologic — Guide de lancement

## Prérequis

- Python 3.10 ou supérieur
- pip

## Installation

Cloner ou télécharger le projet, puis depuis le répertoire `sources/` :

```bash
pip install -r ../requirements.txt
```

## Lancement

Depuis le répertoire `sources/` :

```bash
python main.py
```

Ouvrir ensuite un navigateur à l'adresse : [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Structure du projet

```
2026_ID_Ecologic/
├── sources/
│   ├── main.py          ← point d'entrée (lancer ce fichier)
│   ├── app.py           ← routes Flask et logique principale
│   └── algo.py          ← moteur de simulation (classes Jeu, Meute, etc.)
├── data/
│   ├── data.json        ← paramètres biologiques de la simulation
│   ├── meteo.json       ← événements météorologiques
│   └── succes_permanents.json  ← succès débloqués (généré automatiquement)
├── static/
│   ├── style.css
│   ├── app.js
│   ├── regle.js
│   └── update.js
├── templates/
│   ├── index.html
│   ├── init.html
│   ├── game.html
│   ├── fin.html
│   ├── parametre.html
│   └── ajouter.html
├── presentation.md
├── readme.md
├── LICENSE
├── requirements.txt
└── usage_ia.md
```

## Remarques

- Le fichier `succes_permanents.json` est créé automatiquement dans `data/` au premier lancement.
- Les paramètres biologiques sont modifiables depuis l'interface (page Paramètres).
- Le projet ne nécessite pas de base de données ni de connexion internet.
