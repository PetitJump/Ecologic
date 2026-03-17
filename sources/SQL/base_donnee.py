#Projet : Ecologic
#Auteurs : Margot, Hugo, Carl, Killian

"""
Outil de gestion de la base de données Ecologic.
La base de données database.db doit se trouver dans sources/ (dossier parent de sql/).

Usage :
    python base_donnee.py --liste
    python base_donnee.py --leaderboard
    python base_donnee.py --supprimer <pseudo>
    python base_donnee.py --reset <pseudo>
    python base_donnee.py --export
    python base_donnee.py --help
"""

import sqlite3
import os
import sys
import csv
import argparse
from datetime import datetime

# Chemin vers la DB : sources/database.db (dossier parent de sql/)
DB = os.path.join(os.path.dirname(__file__), '..', 'database.db')
DB = os.path.abspath(DB)


# ── Connexion ──────────────────────────────────────────────────────────────────

def get_conn():
    if not os.path.exists(DB):
        print(f"Erreur : base de données introuvable à {DB}")
        sys.exit(1)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ── Couleurs terminal ──────────────────────────────────────────────────────────

VERT   = "\033[92m"
ROUGE  = "\033[91m"
JAUNE  = "\033[93m"
BLEU   = "\033[94m"
GRIS   = "\033[90m"
RESET  = "\033[0m"
GRAS   = "\033[1m"


# ── Commandes ──────────────────────────────────────────────────────────────────

def cmd_liste():
    """Affiche tous les utilisateurs et leurs statistiques."""
    conn = get_conn()
    try:
        rows = conn.execute('''
            SELECT
                c.id,
                c.username,
                COALESCE(s.nb_parties, 0) AS nb_parties,
                COALESCE(s.max_annees,  0) AS max_annees,
                COALESCE(s.max_loups,   0) AS max_loups,
                COALESCE(s.max_cerfs,   0) AS max_cerfs
            FROM Compte c
            LEFT JOIN Stats s ON s.user_id = c.id
            ORDER BY c.id ASC
        ''').fetchall()
    finally:
        conn.close()

    if not rows:
        print(f"{JAUNE}Aucun utilisateur enregistré.{RESET}")
        return

    print(f"\n{GRAS}{'ID':<5} {'Pseudo':<20} {'Parties':>8} {'Max Années':>11} {'Max Loups':>10} {'Max Cerfs':>10}{RESET}")
    print(GRIS + "─" * 68 + RESET)
    for r in rows:
        print(
            f"{GRIS}{r['id']:<5}{RESET}"
            f"{VERT}{r['username']:<20}{RESET}"
            f"{r['nb_parties']:>8}"
            f"{BLEU}{r['max_annees']:>11}{RESET}"
            f"{JAUNE}{r['max_loups']:>10}{RESET}"
            f"{r['max_cerfs']:>10}"
        )
    print(GRIS + "─" * 68 + RESET)
    print(f"  {GRAS}{len(rows)} utilisateur(s){RESET}\n")


def cmd_leaderboard():
    """Affiche les top 10 pour chaque catégorie."""
    conn = get_conn()
    try:
        categories = [
            ("max_annees", "ans",   "Années"),
            ("max_loups",  "loups", "Loups"),
            ("max_cerfs",  "cerfs", "Cerfs"),
        ]
        for col, unite, titre in categories:
            rows = conn.execute(f'''
                SELECT c.username, s.{col} as score
                FROM Stats s JOIN Compte c ON s.user_id = c.id
                WHERE s.{col} > 0
                ORDER BY s.{col} DESC LIMIT 10
            ''').fetchall()

            print(f"\n{GRAS}{'═'*35}")
            print(f"  TOP 10 — {titre}")
            print(f"{'═'*35}{RESET}")

            if not rows:
                print(f"  {GRIS}Aucun score enregistré.{RESET}")
            else:
                medailles = ["🥇", "🥈", "🥉"]
                for i, r in enumerate(rows):
                    med = medailles[i] if i < 3 else f"   {i+1}."
                    couleur = VERT if i == 0 else (JAUNE if i == 1 else (BLEU if i == 2 else RESET))
                    print(f"  {med} {couleur}{r['username']:<20}{RESET} {r['score']} {unite}")
    finally:
        conn.close()
    print()


def cmd_supprimer(username):
    """Supprime un utilisateur et toutes ses stats."""
    conn = get_conn()
    try:
        user = conn.execute("SELECT id, username FROM Compte WHERE username = ?", (username,)).fetchone()
        if not user:
            print(f"{ROUGE}Erreur : aucun utilisateur avec le pseudo '{username}'.{RESET}")
            return

        print(f"\n{JAUNE}Utilisateur trouvé : ID={user['id']} — pseudo='{user['username']}'{RESET}")
        confirm = input(f"Confirmer la suppression ? {ROUGE}(oui/non){RESET} : ").strip().lower()
        if confirm != "oui":
            print(f"{GRIS}Annulé.{RESET}")
            return

        conn.execute("DELETE FROM Stats   WHERE user_id = ?", (user['id'],))
        conn.execute("DELETE FROM Compte  WHERE id       = ?", (user['id'],))
        conn.commit()
        print(f"{VERT}Utilisateur '{username}' supprimé avec succès.{RESET}\n")
    finally:
        conn.close()


def cmd_reset(username):
    """Réinitialise les stats d'un utilisateur (remet tout à 0)."""
    conn = get_conn()
    try:
        user = conn.execute("SELECT id, username FROM Compte WHERE username = ?", (username,)).fetchone()
        if not user:
            print(f"{ROUGE}Erreur : aucun utilisateur avec le pseudo '{username}'.{RESET}")
            return

        stats = conn.execute("SELECT * FROM Stats WHERE user_id = ?", (user['id'],)).fetchone()
        if not stats:
            print(f"{JAUNE}'{username}' n'a aucune stat enregistrée.{RESET}")
            return

        print(f"\n{JAUNE}Stats actuelles de '{username}' :{RESET}")
        print(f"  Parties : {stats['nb_parties']}  |  Max années : {stats['max_annees']}  |  Max loups : {stats['max_loups']}  |  Max cerfs : {stats['max_cerfs']}")
        confirm = input(f"Confirmer la réinitialisation ? {ROUGE}(oui/non){RESET} : ").strip().lower()
        if confirm != "oui":
            print(f"{GRIS}Annulé.{RESET}")
            return

        conn.execute('''UPDATE Stats SET
            nb_parties = 0,
            max_loups  = 0,
            max_cerfs  = 0,
            max_annees = 0
            WHERE user_id = ?''', (user['id'],))
        conn.commit()
        print(f"{VERT}Stats de '{username}' réinitialisées.{RESET}\n")
    finally:
        conn.close()


def cmd_export():
    """Exporte tous les utilisateurs et stats dans un fichier CSV."""
    conn = get_conn()
    try:
        rows = conn.execute('''
            SELECT
                c.id,
                c.username,
                COALESCE(s.nb_parties, 0) AS nb_parties,
                COALESCE(s.max_annees,  0) AS max_annees,
                COALESCE(s.max_loups,   0) AS max_loups,
                COALESCE(s.max_cerfs,   0) AS max_cerfs
            FROM Compte c
            LEFT JOIN Stats s ON s.user_id = c.id
            ORDER BY s.max_annees DESC
        ''').fetchall()
    finally:
        conn.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_ecologic_{timestamp}.csv"
    # Sauvegarder dans le même dossier que ce script
    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "pseudo", "nb_parties", "max_annees", "max_loups", "max_cerfs"])
        for r in rows:
            writer.writerow([r['id'], r['username'], r['nb_parties'], r['max_annees'], r['max_loups'], r['max_cerfs']])

    print(f"\n{VERT}Export réussi : {filename}{RESET}")
    print(f"{GRIS}Chemin : {filepath}{RESET}")
    print(f"{GRIS}{len(rows)} utilisateur(s) exporté(s).{RESET}\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="base_donnee.py",
        description="Outil de gestion de la base de données Ecologic.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python base_donnee.py --liste
  python base_donnee.py --leaderboard
  python base_donnee.py --supprimer killian
  python base_donnee.py --reset alice
  python base_donnee.py --export
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--liste",
        action="store_true",
        help="Afficher tous les utilisateurs et leurs statistiques"
    )
    group.add_argument(
        "--leaderboard",
        action="store_true",
        help="Afficher les top 10 par catégorie (années, loups, cerfs)"
    )
    group.add_argument(
        "--supprimer",
        metavar="PSEUDO",
        help="Supprimer un utilisateur et toutes ses stats"
    )
    group.add_argument(
        "--reset",
        metavar="PSEUDO",
        help="Remettre les stats d'un utilisateur à zéro"
    )
    group.add_argument(
        "--export",
        action="store_true",
        help="Exporter toutes les données dans un fichier CSV"
    )

    args = parser.parse_args()

    if args.liste:
        cmd_liste()
    elif args.leaderboard:
        cmd_leaderboard()
    elif args.supprimer:
        cmd_supprimer(args.supprimer)
    elif args.reset:
        cmd_reset(args.reset)
    elif args.export:
        cmd_export()


if __name__ == "__main__":
    main()