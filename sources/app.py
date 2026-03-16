#Projet : Ecologic
#Auteurs : Margot, Hugo, Carl, Killian

from flask import Flask, render_template, request, session
import json
import os, os
from Naturalia.sources.algo import Predateur, Vegetal, Proie, Meute, Jeu

app = Flask(__name__)
app.secret_key = "naturalia_nsi_2025"

SUCCES_FILE = os.path.join("data", "succes_permanents.json")

SUCCES_DEF = [
    {"id": "premier_pas",  "emoji": "🌱", "nom": "Premier pas",
     "desc": "Lancer la simulation pour la première fois. Bienvenue dans l'écosystème !"},
    {"id": "equilibre",    "emoji": "⚖️",  "nom": "Équilibre fragile",
     "desc": "Maintenir les trois espèces en vie pendant au moins 10 ans. La nature trouve son équilibre."},
    {"id": "meute_royale", "emoji": "🐺", "nom": "Meute royale",
     "desc": "Atteindre une population de 100 loups simultanément. La forêt leur appartient."},
    {"id": "troupeau",     "emoji": "🦌", "nom": "Troupeau parfait",
     "desc": "Atteindre une population de 50 cerfs simultanément. Le troupeau est au complet."},
    {"id": "foret_dense",  "emoji": "🌿", "nom": "Forêt dense",
     "desc": "Atteindre une végétation de 200 touffes d'herbe simultanément. La prairie est luxuriante."},
    {"id": "survie_seche", "emoji": "☀️",  "nom": "Résistance solaire",
     "desc": "Survivre à une sécheresse sans qu'aucune espèce ne disparaisse. La vie persiste malgré la chaleur."},
    {"id": "survie_hiver", "emoji": "❄️",  "nom": "Hiver de fer",
     "desc": "Survivre à un hiver rigoureux sans qu'aucune espèce ne disparaisse. La forêt résiste au gel."},
    {"id": "cycle",        "emoji": "🔄", "nom": "Le Grand Cycle",
     "desc": "Atteindre l'année 20. Vingt ans de cycles naturels, de prédation et de renouveau."},
    {"id": "extinction",   "emoji": "💀", "nom": "Extinction",
     "desc": "Laisser disparaître une espèce de l'écosystème. L'équilibre s'est brisé."},
]

def charger_succes_permanents():
    if os.path.exists(SUCCES_FILE):
        with open(SUCCES_FILE, "r") as f:
            return json.load(f)
    return {s["id"]: False for s in SUCCES_DEF}

def sauvegarder_succes_permanents(succes):
    with open(SUCCES_FILE, "w") as f:
        json.dump(succes, f, indent=2)

def calculer_prevision(historique, dernier_meteo_cle):
    loup  = historique["loup"]
    cerf  = historique["cerf"]
    herbe = historique["herbe"]
    n = len(loup)
    if n < 3:
        return None
    alertes = []

    # Famine loups : ratio loups/cerfs élevé ET les cerfs baissent déjà
    if cerf[-1] > 0 and loup[-1] / cerf[-1] > 0.5 and cerf[-1] < cerf[-2]:
        alertes.append({"emoji": "🐺", "texte": "Les loups sont trop nombreux face aux cerfs — famine imminente.", "niveau": "danger"})

    # Herbe en chute sur 3 ans consécutifs (pas juste un rebond)
    if n >= 4 and herbe[-1] < herbe[-2] < herbe[-3] and herbe[-1] < herbe[-3] * 0.6:
        alertes.append({"emoji": "🌿", "texte": "L'herbe s'effondre — les cerfs vont manquer de nourriture.", "niveau": "danger"})

    # Cerfs en chute rapide sur 2 ans
    if cerf[-1] < cerf[-2] * 0.55 and cerf[-1] < cerf[-3] * 0.55:
        alertes.append({"emoji": "🦌", "texte": "Les cerfs disparaissent rapidement — les loups vont mourir de faim.", "niveau": "warning"})

    # Prolifération cerfs : herbe abondante ET cerfs déjà en hausse sur 2 ans
    if (herbe[-1] > herbe[-2] * 1.4 and herbe[-2] > herbe[-3] * 1.2
            and cerf[-1] > cerf[-2] and cerf[-1] > 0):
        alertes.append({"emoji": "🦌", "texte": "L'herbe abonde et les cerfs prolifèrent — la meute va croître.", "niveau": "info"})

    # Stable : peu de variation sur 3 ans pour loups ET cerfs
    if not alertes:
        def variation(lst): return max(abs(lst[-1]-lst[-2]), abs(lst[-2]-lst[-3]))
        if (loup[-1] > 0 and cerf[-1] > 0
                and variation(loup) < loup[-1] * 0.12
                and variation(cerf) < cerf[-1] * 0.12):
            alertes.append({"emoji": "🌤️", "texte": "L'écosystème est stable pour l'instant.", "niveau": "ok"})

    return alertes[0] if alertes else None

def maj_journal(journal, annee, predateur, proie, vegetal, meteo_event, nouveaux_succes, prev_pred, prev_proie, prev_veg):
    entrees = []
    if meteo_event:
        entrees.append({"annee": annee, "emoji": meteo_event["emoji"], "texte": meteo_event["nom"], "type": "meteo"})
    for s in nouveaux_succes:
        entrees.append({"annee": annee, "emoji": s["emoji"], "texte": f"Succès débloqué : {s['nom']}", "type": "succes"})
    if prev_pred and predateur > 0 and prev_pred > 0:
        ratio = predateur / prev_pred
        if ratio >= 1.5:
            entrees.append({"annee": annee, "emoji": "📈", "texte": f"Explosion des loups ({prev_pred} → {predateur})", "type": "pop"})
        elif ratio <= 0.5:
            entrees.append({"annee": annee, "emoji": "📉", "texte": f"Chute des loups ({prev_pred} → {predateur})", "type": "pop"})
    if prev_proie and proie > 0 and prev_proie > 0:
        ratio = proie / prev_proie
        if ratio >= 2.0:
            entrees.append({"annee": annee, "emoji": "📈", "texte": f"Explosion des cerfs ({prev_proie} → {proie})", "type": "pop"})
        elif ratio <= 0.4:
            entrees.append({"annee": annee, "emoji": "📉", "texte": f"Effondrement des cerfs ({prev_proie} → {proie})", "type": "pop"})
    for e in entrees:
        journal.insert(0, e)
    return journal[:12]

def verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants):
    nouveaux = []
    def debloquer(sid):
        if not succes_courants.get(sid):
            succes_courants[sid] = True
            defn = next(s for s in SUCCES_DEF if s["id"] == sid)
            nouveaux.append(defn)
    if annee >= 1:   debloquer("premier_pas")
    if annee >= 20:  debloquer("cycle")
    if predateur == 100: debloquer("meute_royale")
    if proie == 50:      debloquer("troupeau")
    if vegetal == 200:   debloquer("foret_dense")
    if annee >= 10 and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("equilibre")
    if meteo_cle == "secheresse" and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("survie_seche")
    if meteo_cle == "hiver" and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("survie_hiver")
    if predateur == 0 or proie == 0 or vegetal == 0:
        debloquer("extinction")
    return nouveaux

def build_render_args(annee, predateur, proie, vegetal, meteo_event,
                      nouveaux_succes, prev_l, prev_c, prev_v):
    succes_courants = charger_succes_permanents()
    meteo_cle = meteo_event["cle"] if meteo_event else None
    nouveaux = verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants)
    nouveaux_succes += nouveaux
    if nouveaux:
        sauvegarder_succes_permanents(succes_courants)

    journal = session.get("journal", [])
    journal = maj_journal(journal, annee, predateur, proie, vegetal,
                          meteo_event, nouveaux_succes, prev_l, prev_c, prev_v)
    session["journal"] = journal
    session.modified = True

    prevision = calculer_prevision(historique, meteo_cle)

    # Deltas pour afficher +/- sur les stats
    delta_l = predateur - prev_l if prev_l is not None else None
    delta_c = proie     - prev_c if prev_c is not None else None
    delta_v = vegetal   - prev_v if prev_v is not None else None

    return dict(
        annee=annee, predateur=predateur, proie=proie, vegetal=vegetal,
        delta_l=delta_l, delta_c=delta_c, delta_v=delta_v,
        meteo=meteo_event, nouveaux_succes=nouveaux_succes,
        succes_list=SUCCES_DEF, succes_courants=succes_courants,
        historique=json.dumps(historique),
        journal=journal, prevision=prevision
    )

@app.route("/")
def index():
    global historique
    historique = {"loup": [], "cerf": [], "herbe": []}
    session["journal"] = []
    succes_courants = charger_succes_permanents()
    return render_template("index.html", succes_list=SUCCES_DEF, succes_courants=succes_courants)

@app.route("/init")
def init():
    return render_template("init.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    global historique, jeu
    annee = int(request.form["annee"])
    if annee == 0:
        jeu = Jeu(
            Meute([Predateur("loup", 0) for _ in range(int(request.form["loup"]))]),
            [Proie("cerf", 0) for _ in range(int(request.form["cerf"]))],
            [Vegetal("herbe") for _ in range(int(request.form["herbe"]))]
        )
        historique = {"loup": [], "cerf": [], "herbe": []}
        session["journal"] = []

    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    _, _, _, meteo_event = jeu.update(annee)
    annee += 1
    predateur = len(jeu.meute.predateurs)
    proie     = len(jeu.proies)
    vegetal   = len(jeu.vegetaux)
    historique["loup"].append(predateur)
    historique["cerf"].append(proie)
    historique["herbe"].append(vegetal)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        sc = charger_succes_permanents()
        verifier_succes(annee, predateur, proie, vegetal,
                        meteo_event["cle"] if meteo_event else None, sc)
        sauvegarder_succes_permanents(sc)
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=sc,
            historique=json.dumps(historique))

    args = build_render_args(annee, predateur, proie, vegetal, meteo_event, [], prev_l, prev_c, prev_v)
    return render_template("game.html", **args)

@app.route("/accelerer", methods=["POST"])
def accelerer():
    """Simule N années d'un coup et redirige vers game.html."""
    global historique, jeu
    nb_annees = max(1, min(50, int(request.form.get("nb_annees", 5))))
    annee = int(request.form["annee"])

    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    dernier_meteo = None
    for _ in range(nb_annees):
        _, _, _, meteo_event = jeu.update(annee)
        annee += 1
        predateur = len(jeu.meute.predateurs)
        proie     = len(jeu.proies)
        vegetal   = len(jeu.vegetaux)
        historique["loup"].append(predateur)
        historique["cerf"].append(proie)
        historique["herbe"].append(vegetal)
        if meteo_event:
            dernier_meteo = meteo_event
        if predateur == 0 or proie == 0 or vegetal == 0:
            espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
            sc = charger_succes_permanents()
            verifier_succes(annee, predateur, proie, vegetal,
                            meteo_event["cle"] if meteo_event else None, sc)
            sauvegarder_succes_permanents(sc)
            return render_template("fin.html",
                annee=annee, espece_morte=espece_morte,
                predateur=predateur, proie=proie, vegetal=vegetal,
                succes_list=SUCCES_DEF, succes_courants=sc,
                historique=json.dumps(historique))

    args = build_render_args(annee, predateur, proie, vegetal,
                             dernier_meteo, [], prev_l, prev_c, prev_v)
    # Indiquer combien d'années ont été sautées
    args["annees_sautees"] = nb_annees
    return render_template("game.html", **args)

@app.route("/update_ajouter", methods=["GET", "POST"])
def update_ajouter():
    global jeu, historique
    annee = int(request.form["base_annee"])
    for _ in range(int(request.form["loup"])): jeu.meute.predateurs.append(Predateur("loup", 0))
    for _ in range(int(request.form["cerf"])): jeu.proies.append(Proie("cerf", 0))
    for _ in range(int(request.form["herbe"])): jeu.vegetaux.append(Vegetal("herbe"))

    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    _, _, _, meteo_event = jeu.update(annee)
    annee += 1
    predateur = len(jeu.meute.predateurs)
    proie     = len(jeu.proies)
    vegetal   = len(jeu.vegetaux)
    historique["loup"].append(predateur)
    historique["cerf"].append(proie)
    historique["herbe"].append(vegetal)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        sc = charger_succes_permanents()
        verifier_succes(annee, predateur, proie, vegetal,
                        meteo_event["cle"] if meteo_event else None, sc)
        sauvegarder_succes_permanents(sc)
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=sc,
            historique=json.dumps(historique))

    args = build_render_args(annee, predateur, proie, vegetal, meteo_event, [], prev_l, prev_c, prev_v)
    return render_template("game.html", **args)

@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    global jeu, historique
    annee = int(request.form["annee"])
    return render_template("ajouter.html",
        annee=annee, predateur=len(jeu.meute.predateurs),
        proie=len(jeu.proies), vegetal=len(jeu.vegetaux))

@app.route("/reset_succes")
def reset_succes():
    sauvegarder_succes_permanents({s["id"]: False for s in SUCCES_DEF})
    return "Succès réinitialisés.", 200

@app.route("/parametre")
def regles():
    with open(os.path.join("data", "data.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    # S'assurer que tout_les est toujours une liste [min, max]
    for espece in data:
        tl = data[espece]["reproduction"]["tout_les"]
        if isinstance(tl, int):
            data[espece]["reproduction"]["tout_les"] = [tl, tl]
    return render_template("parametre.html", data=data)

@app.route("/modifier", methods=["GET", "POST"])
def modifier():
    # Vitesse de repousse de l'herbe
    vitesse_herbe = request.form.get("vitesse_herbe", "normal")
    # Croissance linéaire sans plafond — les cerfs régulent naturellement
    # Lent: +60/an  → prairie fragile, cerfs en compétition
    # Normal: +120/an → équilibre naturel
    # Rapide: +250/an → prairie vivace, cerfs bien nourris
    # taux_r : vitesse de montée, capacite : plafond souple
    # Lent: pousse douce, plafond bas → prairies fragiles
    # Normal: équilibre naturel, plafond 3500
    # Rapide: prairie vivace, plafond plus haut
    herbe_presets = {
        "lent":   {"taux_r": 0.15, "capacite": 2500, "tout_les": [1, 1], "nombre_de_nv_nee": [1, 1]},
        "normal": {"taux_r": 0.25, "capacite": 3500, "tout_les": [1, 1], "nombre_de_nv_nee": [1, 1]},
        "rapide": {"taux_r": 0.40, "capacite": 5000, "tout_les": [1, 1], "nombre_de_nv_nee": [1, 1]},
    }
    herbe_repro = herbe_presets.get(vitesse_herbe, herbe_presets["normal"])

    def to_annees(val, unite_key):
        v = max(1, int(val))
        if request.form.get(unite_key) == "mois":
            return max(1, round(v / 12))
        return v

    tl_preda = to_annees(request.form["nb_bebe_tout_les_preda"], "unite_repro_loup")
    tl_proie = to_annees(request.form["nb_bebe_tout_les_proie"], "unite_repro_cerf")

    data = {
        "loup": {
            "reproduction": {
                "tout_les": [tl_preda, tl_preda],
                "nombre_de_nv_nee": [int(request.form["nb_bebe_predateur1"]), int(request.form["nb_bebe_predateur2"])],
                "maturiter_sexuel": 2
            },
            "mange": {"qui": "cerf", "tout_les": 1, "combien": int(request.form["nb_de_nourriture_predateur"])}
        },
        "cerf": {
            "reproduction": {
                "tout_les": [tl_proie, tl_proie],
                "nombre_de_nv_nee": [int(request.form["nb_bebe_proie1"]), int(request.form["nb_bebe_proie2"])],
                "maturiter_sexuel": 2
            },
            "mange": {"qui": "herbe", "tout_les": 1, "combien": int(request.form["nb_de_nourriture_proie"])}
        },
        "herbe": {
            "reproduction": herbe_repro
        }
    }
    with open(os.path.join("data", "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return render_template("index.html",
        succes_list=SUCCES_DEF,
        succes_courants=charger_succes_permanents())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
