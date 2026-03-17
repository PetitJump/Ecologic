# base_donnee.py — Documentation

Script de gestion de la base de données Ecologic.
À lancer depuis le dossier `sql/` ou depuis n'importe où.

---

## Prérequis

- Python 3.10+
- La base de données `database.db` doit être présente dans `sources/`

---

## Utilisation

```bash
# Depuis le dossier sources/
python sql/base_donnee.py --<commande>

# Depuis le dossier sql/
python base_donnee.py --<commande>
```

---

## Commandes disponibles

### `--liste`
Affiche tous les utilisateurs enregistrés avec leurs statistiques complètes.

```bash
python sql/base_donnee.py --liste
```

Colonnes affichées : ID, Pseudo, Parties jouées, Max années, Max loups, Max cerfs.

---

### `--leaderboard`
Affiche les top 10 pour chaque catégorie : années, loups, cerfs.

```bash
python sql/base_donnee.py --leaderboard
```

Les 3 premiers reçoivent les médailles 🥇 🥈 🥉.

---

### `--supprimer <pseudo>`
Supprime un utilisateur et **toutes ses stats** de la base de données.
Une confirmation est demandée avant la suppression.

```bash
python sql/base_donnee.py --supprimer killian
```

Exemple d'interaction :
```
Utilisateur trouvé : ID=3 — pseudo='killian'
Confirmer la suppression ? (oui/non) : oui
Utilisateur 'killian' supprimé avec succès.
```

> ⚠️ Cette action est irréversible. Les stats sont perdues définitivement.

---

### `--reset <pseudo>`
Remet les statistiques d'un utilisateur à zéro (parties, max années, max loups, max cerfs).
Le compte reste existant, seules les stats sont effacées.

```bash
python sql/base_donnee.py --reset alice
```

Exemple d'interaction :
```
Stats actuelles de 'alice' :
  Parties : 12  |  Max années : 45  |  Max loups : 130  |  Max cerfs : 400
Confirmer la réinitialisation ? (oui/non) : oui
Stats de 'alice' réinitialisées.
```

---

### `--export`
Exporte toutes les données dans un fichier CSV horodaté, enregistré dans le dossier `sql/`.

```bash
python sql/base_donnee.py --export
```

Le fichier généré s'appelle `export_ecologic_YYYYMMDD_HHMMSS.csv`.

Colonnes exportées :

| Colonne | Description |
|---|---|
| id | Identifiant unique en base |
| pseudo | Nom d'utilisateur |
| nb_parties | Nombre total de parties jouées |
| max_annees | Record de longévité (en années) |
| max_loups | Record de population de loups |
| max_cerfs | Record de population de cerfs |

Les données sont triées par `max_annees` décroissant (meilleurs joueurs en premier).

---

## Structure de la base de données

### Table `Compte`
| Colonne | Type | Description |
|---|---|---|
| id | INTEGER | Clé primaire auto-incrémentée |
| username | TEXT UNIQUE | Pseudo du joueur |
| password | TEXT | Mot de passe hashé (bcrypt) |

### Table `Stats`
| Colonne | Type | Description |
|---|---|---|
| id | INTEGER | Clé primaire auto-incrémentée |
| user_id | INTEGER | Clé étrangère vers Compte.id |
| nb_parties | INTEGER | Nombre de parties terminées |
| max_loups | INTEGER | Maximum de loups atteint simultanément |
| max_cerfs | INTEGER | Maximum de cerfs atteint simultanément |
| max_annees | INTEGER | Maximum d'années tenues |

---

## Cas d'erreurs

| Erreur | Cause | Solution |
|---|---|---|
| `base de données introuvable` | `database.db` absent de `sources/` | Vérifier que le projet est lancé au moins une fois |
| `aucun utilisateur avec le pseudo X` | Pseudo inexistant ou mal orthographié | Vérifier avec `--liste` |
| Pas de données dans `--leaderboard` | Aucune partie terminée | Jouer et finir une partie |