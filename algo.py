#Projet : Naturalia
#Auteurs : Margot, Hugo, Carl, Killian

import random
import json

class Predateur:
    def __init__(self, nom: str, age: int):
        self.nom = nom
        self.age = age

class Meute:
    def __init__(self, predateurs: list):
        self.predateurs = predateurs

class Proie:
    def __init__(self, nom: str, age: int):
        self.nom = nom
        self.age = age

class Vegetal:
    def __init__(self, nom: str):
        self.nom = nom

class Jeu:
    def __init__(self, meute: Meute, proies: list, vegetaux: list):
        self.meute   = meute
        self.proies  = proies
        self.vegetaux = vegetaux

    def naissance(self, data: dict, annee: int):
        """Naissances et vieillissement.
        Respecte exactement les parametres configures par l'utilisateur.
        tout_les [min,max] : frequence de reproduction
        nombre_de_nv_nee [min,max] : petits par couple
        """
        import random as _rnd
        from random import randint

        # Loups
        freq_loup = randint(data["loup"]["reproduction"]["tout_les"][0],
                            data["loup"]["reproduction"]["tout_les"][1])
        if annee % freq_loup == 0:
            age_min = data["loup"]["reproduction"]["maturiter_sexuel"]
            majeurs = [k for k in self.meute.predateurs if k.age > age_min]
            nb_couples = len(majeurs) // 2
            for _ in range(nb_couples):
                petits = randint(data["loup"]["reproduction"]["nombre_de_nv_nee"][0],
                                 data["loup"]["reproduction"]["nombre_de_nv_nee"][1])
                for _ in range(petits):
                    if _rnd.random() < 0.35:  # 35% survie juvénile loups
                        self.meute.predateurs.append(Predateur("loup", 0))

        for k in self.meute.predateurs:
            k.age += 1

        # Cerfs - repro limitée par la disponibilité de l'herbe
        freq_cerf = randint(data["cerf"]["reproduction"]["tout_les"][0],
                            data["cerf"]["reproduction"]["tout_les"][1])
        if annee % freq_cerf == 0:
            age_min = data["cerf"]["reproduction"]["maturiter_sexuel"]
            majeurs = [k for k in self.proies if k.age > age_min]
            nb_couples = len(majeurs) // 2
            # Si l'herbe est rare, les cerfs se reproduisent moins bien
            nb_cerfs = max(1, len(self.proies))
            herbe_par_cerf = len(self.vegetaux) / nb_cerfs
            # Seuil de confort: 5 touffes/cerf = repro pleine. Moins = repro réduite
            facteur_herbe = min(1.0, herbe_par_cerf / 5.0)
            for _ in range(nb_couples):
                if _rnd.random() > facteur_herbe:
                    continue  # pas de repro si herbe insuffisante
                petits = randint(data["cerf"]["reproduction"]["nombre_de_nv_nee"][0],
                                 data["cerf"]["reproduction"]["nombre_de_nv_nee"][1])
                for _ in range(petits):
                    if _rnd.random() < 0.40:
                        self.proies.append(Proie("cerf", 0))

        for k in self.proies:
            k.age += 1

        # Herbe - croissance logistique
        N = len(self.vegetaux)
        r = data["herbe"]["reproduction"]["taux_r"]
        K = data["herbe"]["reproduction"]["capacite"]
        croissance = int(r * N * (1 - N / K))
        croissance = max(0, croissance)
        for _ in range(croissance):
            self.vegetaux.append(Vegetal("herbe"))


    def mort(self, data: dict, annee: int):
        """Morts naturelles et prédation."""
        self.meute.predateurs = [k for k in self.meute.predateurs if k.age < 20]
        self.proies           = [k for k in self.proies           if k.age < 12]  # cerfs vivent moins longtemps
        self.taux_de_survie()

        # ── Loups chassent les cerfs ──────────────────────
        if annee % data["loup"]["mange"]["tout_les"] == 0:
            combien = data["loup"]["mange"]["combien"]
            necessaires = len(self.meute.predateurs) * combien
            if len(self.proies) >= necessaires:
                for _ in range(necessaires):
                    self.proies.pop()
            else:
                survivants = len(self.proies) // combien
                self.proies = []
                if survivants <= 0:
                    self.meute.predateurs = []
                else:
                    self.meute.predateurs = self.meute.predateurs[:survivants]

        # ── Cerfs broutent l'herbe ────────────────────────
        # Chaque cerf mange X touffes par an.
        # Si l'herbe manque, la pression de faim est progressive :
        # les cerfs meurent proportionnellement au manque, pas tous d'un coup.
        touffes_dispo    = len(self.vegetaux)
        touffes_par_cerf = data["cerf"]["mange"]["combien"]
        nb_cerfs         = len(self.proies)
        touffes_requises = nb_cerfs * touffes_par_cerf

        if touffes_dispo >= touffes_requises:
            # Assez d'herbe pour tout le monde
            self.vegetaux = self.vegetaux[touffes_requises:]
        elif touffes_dispo > 0:
            # Manque d'herbe : taux de survie proportionnel à la disponibilité
            taux_satisfaction = touffes_dispo / touffes_requises
            # Les cerfs meurent partiellement — mortalité douce par famine
            import random as _r
            self.proies = [c for c in self.proies if _r.random() < (0.3 + 0.7 * taux_satisfaction)]
            self.vegetaux = []
        else:
            # Plus d'herbe du tout — forte mortalité mais pas extinction immédiate
            import random as _r
            self.proies = [c for c in self.proies if _r.random() < 0.2]
            self.vegetaux = []

    def taux_de_survie(self):
        """Mortalité naturelle aléatoire."""
        self.meute.predateurs = [
            k for k in self.meute.predateurs
            if random.random() < (0.5 if k.age == 0 else 0.95)
        ]
        self.proies = [
            k for k in self.proies
            if random.random() < (0.5 if k.age == 0 else 0.95)
        ]

    def appliquer_meteo(self, evenement: dict) -> dict:
        """
        Applique un événement météo sur les populations.
        evenement = un dict du meteo.json (avec clé 'effet').
        Retourne le dict de l'événement pour l'afficher dans Flask.
        Les effets positifs ajoutent des individus, les négatifs en retirent.
        """
        effet = evenement["effet"]

        # ── Herbe ──────────────────────────────────────────
        nb_herbe = len(self.vegetaux)
        delta_herbe = int(nb_herbe * effet["herbe"])
        if delta_herbe > 0:
            for _ in range(delta_herbe):
                self.vegetaux.append(Vegetal("herbe"))
        elif delta_herbe < 0:
            retirer = min(abs(delta_herbe), nb_herbe)
            self.vegetaux = self.vegetaux[retirer:]

        # ── Cerfs ──────────────────────────────────────────
        nb_cerf = len(self.proies)
        delta_cerf = int(nb_cerf * effet["cerf"])
        if delta_cerf > 0:
            for _ in range(delta_cerf):
                self.proies.append(Proie("cerf", 1))
        elif delta_cerf < 0:
            retirer = min(abs(delta_cerf), nb_cerf)
            self.proies = self.proies[retirer:]

        # ── Loups ──────────────────────────────────────────
        nb_loup = len(self.meute.predateurs)
        delta_loup = int(nb_loup * effet["loup"])
        if delta_loup > 0:
            for _ in range(delta_loup):
                self.meute.predateurs.append(Predateur("loup", 1))
        elif delta_loup < 0:
            retirer = min(abs(delta_loup), nb_loup)
            self.meute.predateurs = self.meute.predateurs[retirer:]

        return evenement

    def update(self, annee: int):
        """Fonction principale appelée par Flask. Retourne aussi l'évent météo éventuel."""
        from petites_fonctions import random_repro

        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # random_repro supprime - les parametres sont appliques directement dans naissance()

        self.naissance(data, annee)
        self.mort(data, annee)

        # Plancher végétal minimal
        if len(self.vegetaux) < 10:
            for _ in range(15):
                self.vegetaux.append(Vegetal("herbe"))

        # ── Météo ─────────────────────────────────────────
        meteo_event = None
        with open('meteo.json', 'r', encoding='utf-8') as f:
            meteo = json.load(f)

        for cle, ev in meteo.items():
            if random.random() < ev["chance"]:
                meteo_event = dict(ev)
                meteo_event["cle"] = cle
                self.appliquer_meteo(ev)
                break  # un seul événement par année

        return self.meute.predateurs, self.proies, self.vegetaux, meteo_event
