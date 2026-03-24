#Projet : Naturalia
#Auteurs : Margot, Hugo, Carl, Killian

import os
import random
import json

#BASE_DIR = os.path.dirname(os.path.abspath(__file__)) Pour le serveur
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #Pour local

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
    def __init__(self, meutes: list[Meute], proies: list[Proie], vegetaux: list[Vegetal]):
        self.meutes = meutes
        self.proies = proies
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
        for meute in self.meutes:  # On parcourt chaque meute
            for k in meute.predateurs:
                k.age += 1

            freq_loup = randint(data["loup"]["reproduction"]["tout_les"][0],
                                data["loup"]["reproduction"]["tout_les"][1])
            if annee % freq_loup == 0:
                age_min = data["loup"]["reproduction"]["maturiter_sexuel"]
                majeurs = [k for k in meute.predateurs if k.age > age_min]
                reproducteurs = sorted(majeurs, key=lambda k: k.age, reverse=True)[:2]  # Les 2 plus vieux de CETTE meute
                if len(reproducteurs) == 2:
                    petits = randint(data["loup"]["reproduction"]["nombre_de_nv_nee"][0],
                                    data["loup"]["reproduction"]["nombre_de_nv_nee"][1])
                    for _ in range(petits):
                        if _rnd.random() < 0.35:
                            meute.predateurs.append(Predateur("loup", 0))  # Ajout dans CETTE meute

        #Cerfs
        for k in self.proies:
            k.age += 1 #On augmente l'age de chaque cerfs avant la reproduction

        freq_cerf = randint(data["cerf"]["reproduction"]["tout_les"][0],
                            data["cerf"]["reproduction"]["tout_les"][1])
        if annee % freq_cerf == 0: #Si c'est le moment de ce reproduire
            age_min = data["cerf"]["reproduction"]["maturiter_sexuel"]
            majeurs = [k for k in self.proies if k.age > age_min]
            nb_couples = len(majeurs) // 2
            nb_cerfs = max(1, len(self.proies)) #On utlise max() pour eviter les bugs

            #Plus l'herbe est rare par rapport au nombre de cerfs, moins les cerfs se reproduisent.
            herbe_par_cerf = len(self.vegetaux) / nb_cerfs
            facteur_herbe = min(1.0, herbe_par_cerf / 5.0) #On utilise min() pour éviter d'avoir un taux de reproduction trop haut

            for _ in range(nb_couples):
                if _rnd.random() > facteur_herbe:
                    continue #Pas de reproduction si herbe insuffisante
                petits = randint(data["cerf"]["reproduction"]["nombre_de_nv_nee"][0],
                                 data["cerf"]["reproduction"]["nombre_de_nv_nee"][1])
                for _ in range(petits):
                    if _rnd.random() < 0.40: #Valeur entre 0.0 et 1.0 (On utilise cela pour le taux de survie)
                        self.proies.append(Proie("cerf", 0))

        #Herbe
        N = len(self.vegetaux) #Nombre d'herbes
        r = data["herbe"]["reproduction"]["taux_r"] #Taux de croissance
        K = data["herbe"]["reproduction"]["capacite"] #Capacité maximal
        croissance = int(r * N * (1 - N / K)) #Equation de Verhulst
        croissance = max(0, croissance) #max() pour eviter les bugs
        for _ in range(croissance):
            self.vegetaux.append(Vegetal("herbe"))


    def mort(self, data: dict, annee: int):
        """Morts naturelles et prédation."""
        for meute in self.meutes:
            meute.predateurs = [k for k in meute.predateurs if k.age < 15] #Les loups de 15 ans meurts
        self.proies = [k for k in self.proies if k.age < 12] #Les cerfs de 12 ans meurts
        self.taux_de_survie() #Les morts naturelle

        #Loups
        for meute in self.meutes:
            if annee % data["loup"]["mange"]["tout_les"] == 0:
                combien = data["loup"]["mange"]["combien"]
                necessaires = len(meute.predateurs) * combien
                if len(self.proies) >= necessaires:
                    for _ in range(necessaires):
                        self.proies.pop()
                else:
                    survivants = len(self.proies) // combien
                    self.proies = []
                    if survivants <= 0:
                        meute.predateurs = []
                    else:
                        meute.predateurs = meute.predateurs[:survivants]

        #Cerfs
        """Chaque cerf mange X touffes par an.
        Si l'herbe manque, la pression de faim est progressive :
        Les cerfs meurent proportionnellement au manque, pas tous d'un coup."""
        touffes_dispo = len(self.vegetaux)
        touffes_par_cerf = data["cerf"]["mange"]["combien"]
        nb_cerfs = len(self.proies)
        touffes_requises = nb_cerfs * touffes_par_cerf

        if touffes_dispo >= touffes_requises: #S'il y a assez de touffes pour tout le monde
            self.vegetaux = self.vegetaux[touffes_requises:] #On enlève les touffes manger
        elif touffes_dispo > 0: #Manque d'herbe : taux de survie proportionnel à la disponibilité
            taux_satisfaction = touffes_dispo / touffes_requises #Les cerfs meurent partiellement mortalité douce par famine
            import random as _r
            self.proies = [c for c in self.proies if _r.random() < (0.3 + 0.7 * taux_satisfaction)] #???
            self.vegetaux = [] #On enlève l'herbe
        else: #Plus d'herbe du tout
            import random as _r
            self.proies = [c for c in self.proies if _r.random() < 0.2] #???
            self.vegetaux = []

    def taux_de_survie(self):
        """Mortalité naturelle aléatoire."""
        for meute in self.meutes:
            meute.predateurs = [
                k for k in meute.predateurs
                if random.random() < (0.5 if k.age == 0 else 0.95)
        ] #Gère le taux de mort en fonction de l'age du loup
        self.proies = [
            k for k in self.proies
            if random.random() < (0.5 if k.age == 0 else 0.95)
        ] #Gère le taux de mort en fonction de l'age du cerf

    def appliquer_meteo(self, evenement: dict) -> dict:
        """
        Applique un événement météo sur les populations.
        evenement = un dict du meteo.json (avec clé 'effet').
        Retourne le dict de l'événement pour l'afficher dans Flask.
        Les effets positifs ajoutent des individus, les négatifs en retirent.
        """
        effet = evenement["effet"]

        #Herbes
        nb_herbe = len(self.vegetaux)
        delta_herbe = int(nb_herbe * effet["herbe"])#on applique le taux assigner a l'herbe
        if delta_herbe > 0: #Si c'est positif
            for _ in range(delta_herbe):
                self.vegetaux.append(Vegetal("herbe")) #On ajoute le bonus d'herbe
        elif delta_herbe < 0:#Si il est négatif
            retirer = min(abs(delta_herbe), nb_herbe)#on prend la valeur la plus spetite entre delta_herbe le nombre de herbe
            self.vegetaux = self.vegetaux[retirer:]#on prend la fin de la liste apres lindice selectionner

        #Cerfs
        nb_cerf = len(self.proies)
        delta_cerf = int(nb_cerf * effet["cerf"])#on applique le taux assigner au cerf
        if delta_cerf > 0:#Si c'est positif
            for _ in range(delta_cerf):
                self.proies.append(Proie("cerf", 1))#on ajoute une année au cerf
        elif delta_cerf < 0:#Si il est négatif
            retirer = min(abs(delta_cerf), nb_cerf)#on prend la valeur la plus spetite entre delta_cerfet le nombre de cerf
            self.proies = self.proies[retirer:]#on prend la fin de la liste apres lindice selectionner

        # Loups
        for meute in self.meutes:
            nb_loup = len(meute.predateurs)
            delta_loup = int(nb_loup * effet["loup"])
            if delta_loup > 0:
                for _ in range(delta_loup):
                    meute.predateurs.append(Predateur("loup", 1))
            elif delta_loup < 0:
                retirer = min(abs(delta_loup), nb_loup)
                meute.predateurs = meute.predateurs[retirer:]

        return evenement

    def update(self, annee: int, data: dict = None):
        """
        La fonction update permet de mettre à jour le jeu.
        data : dictionnaire des règles biologiques. Si None, charge depuis data.json (fallback).
        """
        #On appelle le fichier data avec les information sur les animaux.
        if data is None:
            with open(os.path.join(BASE_DIR, 'data', 'data.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)

        #On appelle les fonctions mort et naissance. 
        #Ces fonctions vont donc être appelée pour permettre a l'écosystème de paraitre plus naturel.
        #Pour avoir plus d'information sur ces fonctions, veuillez regarder les fonctions
        self.naissance(data, annee)
        self.mort(data, annee)

        #Il y a un nombre minimum d'herbe à avoir dans le jeu. 
        #Si celui-ci est plus bas que 10 herbes, d'autres se rajoutent automatiquement.
        if len(self.vegetaux) < 10:
            for _ in range(15):
                self.vegetaux.append(Vegetal("herbe"))

        #On va maintenant appliquer les météos
        meteo_event = None
        with open(os.path.join(BASE_DIR, 'data', 'meteo.json'), 'r', encoding='utf-8') as f:
            meteo = json.load(f)

        for cle, ev in meteo.items(): #On va instancier deux variables qui sont dans meteo
            if random.random() < ev["chance"]: #On va prendre un decimal random. si celui-ci est plus petit que la probilité de la météo
                meteo_event = dict(ev) 
                meteo_event["cle"] = cle 
                self.appliquer_meteo(ev) #On va enfin finir par appeler la fonction qui permet d'appliquer l'evenement meteo dans la partie
                break  # un seul événement par année

        return self.meutes, self.proies, self.vegetaux, meteo_event
