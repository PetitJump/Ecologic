from flask import Flask, render_template, request, session
import json, os, random
from algo import Predateur, Vegetal, Proie, Meute, Jeu

app = Flask(__name__)
app.secret_key = "naturalia_nsi_2025"

# ── Fichier de persistance succès ────────────────────────
SUCCES_FILE = "succes_permanents.json"

SUCCES_DEF = [
    {"id": "premier_pas",  "emoji": "🌱", "nom": "Premier pas",       "desc": "Lancer la simulation pour la première fois."},
    {"id": "equilibre",    "emoji": "⚖️",  "nom": "Équilibre fragile", "desc": "Maintenir les 3 espèces en vie pendant 10 ans."},
    {"id": "meute_royale", "emoji": "🐺", "nom": "Meute royale",      "desc": "Atteindre exactement 100 loups."},
    {"id": "troupeau",     "emoji": "🦌", "nom": "Troupeau parfait",  "desc": "Atteindre exactement 50 cerfs."},
    {"id": "foret_dense",  "emoji": "🌿", "nom": "Forêt dense",       "desc": "Atteindre exactement 200 touffes d'herbe."},
    {"id": "survie_seche", "emoji": "☀️",  "nom": "Résistance solaire","desc": "Survivre a une secheresse sans extinction."},
    {"id": "survie_hiver", "emoji": "❄️",  "nom": "Hiver de fer",     "desc": "Survivre a un hiver rigoureux sans extinction."},
    {"id": "cycle",        "emoji": "🔄", "nom": "Le Cycle",          "desc": "Atteindre l'annee 20."},
    {"id": "extinction",   "emoji": "💀", "nom": "Extinction",        "desc": "Laisser disparaitre une espece."},
]

# ── Persistance succès sur disque ────────────────────────
def charger_succes_permanents():
    if os.path.exists(SUCCES_FILE):
        with open(SUCCES_FILE, "r") as f:
            return json.load(f)
    return {s["id"]: False for s in SUCCES_DEF}

def sauvegarder_succes_permanents(succes):
    with open(SUCCES_FILE, "w") as f:
        json.dump(succes, f, indent=2)

# ── Prévision météo ──────────────────────────────────────
def calculer_prevision(historique, dernier_meteo_cle):
    """
    Analyse les tendances pour suggérer une prévision.
    Retourne un dict {emoji, texte, niveau} ou None.
    """
    loup  = historique["loup"]
    cerf  = historique["cerf"]
    herbe = historique["herbe"]
    n = len(loup)
    if n < 2:
        return None

    alertes = []

    # Sécheresse probable si l'herbe chute fortement
    if n >= 3:
        tendance_herbe = herbe[-1] - herbe[-3]
        if tendance_herbe < -herbe[-1] * 0.3:
            alertes.append({"emoji": "☀️", "texte": "Risque de sécheresse — l'herbe décline rapidement.", "niveau": "danger"})

    # Surpopulation prédateur → famine imminente
    if cerf[-1] > 0 and loup[-1] / cerf[-1] > 0.4:
        alertes.append({"emoji": "🐺", "texte": "Trop de loups pour les cerfs — famine imminente.", "niveau": "danger"})

    # Effondrement herbivores → loups en danger
    if n >= 2 and cerf[-1] < cerf[-2] * 0.6:
        alertes.append({"emoji": "🦌", "texte": "Les cerfs chutent vite — les loups vont souffrir.", "niveau": "warning"})

    # Explosion herbe → boom proies attendu
    if n >= 2 and herbe[-1] > herbe[-2] * 1.5:
        alertes.append({"emoji": "🌿", "texte": "L'herbe explose — une prolifération de cerfs est attendue.", "niveau": "info"})

    # Équilibre stable
    if not alertes and n >= 3:
        stable = all(
            abs(loup[i] - loup[i-1]) < loup[i] * 0.15 and
            abs(cerf[i] - cerf[i-1]) < cerf[i] * 0.15
            for i in range(-1, -3, -1) if loup[i] > 0 and cerf[i] > 0
        )
        if stable:
            alertes.append({"emoji": "🌤️", "texte": "Ecosystème stable — les populations s'équilibrent.", "niveau": "ok"})

    return alertes[0] if alertes else None

# ── Journal de bord ──────────────────────────────────────
def maj_journal(journal, annee, predateur, proie, vegetal, meteo_event, nouveaux_succes, prev_predateur, prev_proie, prev_vegetal):
    """Ajoute les événements notables de cette année au journal."""
    entrees = []

    if meteo_event:
        entrees.append({
            "annee": annee,
            "emoji": meteo_event["emoji"],
            "texte": f"{meteo_event['nom']}",
            "type": "meteo"
        })

    for s in nouveaux_succes:
        entrees.append({
            "annee": annee,
            "emoji": s["emoji"],
            "texte": f"Succès : {s['nom']}",
            "type": "succes"
        })

    # Pics / chutes notables
    if prev_predateur and predateur > 0 and prev_predateur > 0:
        ratio = predateur / prev_predateur
        if ratio >= 1.5:
            entrees.append({"annee": annee, "emoji": "📈", "texte": f"Boom des loups ({prev_predateur}→{predateur})", "type": "pop"})
        elif ratio <= 0.5:
            entrees.append({"annee": annee, "emoji": "📉", "texte": f"Chute des loups ({prev_predateur}→{predateur})", "type": "pop"})

    if prev_proie and proie > 0 and prev_proie > 0:
        ratio = proie / prev_proie
        if ratio >= 2.0:
            entrees.append({"annee": annee, "emoji": "📈", "texte": f"Explosion des cerfs ({prev_proie}→{proie})", "type": "pop"})
        elif ratio <= 0.4:
            entrees.append({"annee": annee, "emoji": "📉", "texte": f"Effondrement des cerfs ({prev_proie}→{proie})", "type": "pop"})

    for e in entrees:
        journal.insert(0, e)

    return journal[:12]  # garder les 12 dernières entrées

# ── Helpers session ──────────────────────────────────────
def get_succes_session():
    """Fusionne les succès permanents (disque) avec la session courante."""
    permanents = charger_succes_permanents()
    return permanents

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

# ── Routes ───────────────────────────────────────────────
@app.route("/")
def index():
    global historique
    historique = {"loup": [], "cerf": [], "herbe": []}
    session["journal"] = []
    succes_courants = charger_succes_permanents()
    return render_template("index.html",
        succes_list=SUCCES_DEF,
        succes_courants=succes_courants)

@app.route("/init")
def init():
    return render_template("init.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    global historique, jeu
    annee = int(request.form["annee"])

    if annee == 0:
        nb_loup  = int(request.form["loup"])
        nb_cerf  = int(request.form["cerf"])
        nb_herbe = int(request.form["herbe"])
        jeu = Jeu(
            Meute([Predateur("loup", 0) for _ in range(nb_loup)]),
            [Proie("cerf", 0) for _ in range(nb_cerf)],
            [Vegetal("herbe") for _ in range(nb_herbe)]
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

    # Succès permanents
    succes_courants = charger_succes_permanents()
    meteo_cle = meteo_event["cle"] if meteo_event else None
    nouveaux_succes = verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants)
    if nouveaux_succes:
        sauvegarder_succes_permanents(succes_courants)

    # Journal
    journal = session.get("journal", [])
    journal = maj_journal(journal, annee, predateur, proie, vegetal,
                          meteo_event, nouveaux_succes, prev_l, prev_c, prev_v)
    session["journal"] = journal
    session.modified = True

    # Prévision météo
    prevision = calculer_prevision(historique, meteo_cle)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=succes_courants)

    return render_template("game.html",
        annee=annee, predateur=predateur, proie=proie, vegetal=vegetal,
        meteo=meteo_event, nouveaux_succes=nouveaux_succes,
        succes_list=SUCCES_DEF, succes_courants=succes_courants,
        historique=json.dumps(historique),
        journal=journal, prevision=prevision)

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

    succes_courants = charger_succes_permanents()
    meteo_cle = meteo_event["cle"] if meteo_event else None
    nouveaux_succes = verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants)
    if nouveaux_succes:
        sauvegarder_succes_permanents(succes_courants)

    journal = session.get("journal", [])
    journal = maj_journal(journal, annee, predateur, proie, vegetal,
                          meteo_event, nouveaux_succes, prev_l, prev_c, prev_v)
    session["journal"] = journal
    session.modified = True

    prevision = calculer_prevision(historique, meteo_cle)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=succes_courants)

    return render_template("game.html",
        annee=annee, predateur=predateur, proie=proie, vegetal=vegetal,
        meteo=meteo_event, nouveaux_succes=nouveaux_succes,
        succes_list=SUCCES_DEF, succes_courants=succes_courants,
        historique=json.dumps(historique),
        journal=journal, prevision=prevision)

@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    global jeu, historique
    annee = int(request.form["annee"])
    return render_template("ajouter.html",
        annee=annee,
        predateur=len(jeu.meute.predateurs),
        proie=len(jeu.proies),
        vegetal=len(jeu.vegetaux))

@app.route("/reset_succes")
def reset_succes():
    """Route utilitaire pour remettre à zéro les succès (debug)."""
    sauvegarder_succes_permanents({s["id"]: False for s in SUCCES_DEF})
    return "Succès réinitialisés.", 200

@app.route("/parametre")
def regles():
    return render_template("parametre.html")

@app.route("/modifier", methods=["GET", "POST"])
def modifier():
    data = {
        "loup": {
            "reproduction": {
                "tout_les": int(request.form["nb_bebe_tout_les_preda"]),
                "nombre_de_nv_nee": [int(request.form["nb_bebe_predateur1"]), int(request.form["nb_bebe_predateur2"])],
                "maturiter_sexuel": 2
            },
            "mange": {"qui": "cerf", "tout_les": int(request.form["nb_de_nourriture_tout_les_predateur"]), "combien": int(request.form["nb_de_nourriture_predateur"])}
        },
        "cerf": {
            "reproduction": {
                "tout_les": int(request.form["nb_bebe_tout_les_proie"]),
                "nombre_de_nv_nee": [int(request.form["nb_bebe_proie1"]), int(request.form["nb_bebe_proie2"])],
                "maturiter_sexuel": 2
            },
            "mange": {"qui": "herbe", "tout_les": int(request.form["nb_de_nourriture_tout_les_proie"]), "combien": int(request.form["nb_de_nourriture_proie"])}
        },
        "herbe": {
            "reproduction": {
                "tout_les": int(request.form["nb_bebe_tout_les_vegetal"]),
                "nombre_de_nv_nee": [int(request.form["nb_bebe_vegetal1"]), int(request.form["nb_bebe_vegetal2"])]
            }
        }
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
