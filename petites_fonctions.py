#Projet : Naturalia
#Auteurs : Margot, Hugo, Carl, Killian

from random import randint

def random_repro(data: dict) -> dict:
    """
    La fonction va prendre en compte la reproduction des êtres vivants. Un nombre aléatoire de bébés vont naitre.
    C'est ce que la fonction va nous permettre de faire. randomiser le nombre de bébés a chaque naissance pour chaque couples.
    """
    for i in data:
        nv_j = randint(data[i]["reproduction"]["tout_les"][0], data[i]["reproduction"]["tout_les"][1])
        data[i]["reproduction"]["tout_les"] =  nv_j
        nvl_repro = randint(data[i]["reproduction"]["nombre_de_nv_nee"][0], data[i]["reproduction"]["nombre_de_nv_nee"][1])
        data[i]["reproduction"]["nombre_de_nv_nee"] = nvl_repro 
    return data