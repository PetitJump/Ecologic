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
        """Naissances et vieillissement."""
        if annee % data["loup"]["reproduction"]["tout_les"] == 0:
            age_min = data["loup"]["reproduction"]["maturiter_sexuel"]
            majeurs = [k for k in self.meute.predateurs if k.age > age_min]
            nb = data["loup"]["reproduction"]["nombre_de_nv_nee"] * (len(majeurs) // 2)
            for _ in range(nb):
                self.meute.predateurs.append(Predateur("loup", 0))

        for k in self.meute.predateurs:
            k.age += 1

        if annee % data["cerf"]["reproduction"]["tout_les"] == 0:
            age_min = data["cerf"]["reproduction"]["maturiter_sexuel"]
            majeurs = [k for k in self.proies if k.age > age_min]
            nb = data["cerf"]["reproduction"]["nombre_de_nv_nee"] * (len(majeurs) // 2)
            for _ in range(nb):
                self.proies.append(Proie("cerf", 0))

        for k in self.proies:
            k.age += 1

        if annee % data["herbe"]["reproduction"]["tout_les"] == 0 and len(self.vegetaux) < 2500:
            nb = data["herbe"]["reproduction"]["nombre_de_nv_nee"] * (len(self.vegetaux) // 2)
            for _ in range(nb):
                self.vegetaux.append(Vegetal("herbe"))

    def mort(self, data: dict, annee: int):
        """Morts naturelles et prédation."""
        self.meute.predateurs = [k for k in self.meute.predateurs if k.age < 20]
        self.proies           = [k for k in self.proies           if k.age < 20]
        self.taux_de_survie()

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

    def taux_de_survie(self):
        """Mortalité naturelle aléatoire."""
        self.meute.predateurs = [
            k for k in self.meute.predateurs
            if random.random() < (0.6 if k.age == 0 else 0.9)
        ]
        self.proies = [
            k for k in self.proies
            if random.random() < (0.6 if k.age == 0 else 0.9)
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
        data = random_repro(data)

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
