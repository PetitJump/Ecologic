#Projet : Ecologic
#Auteurs : Margot, Hugo, Carl, Killian

from flask import Flask, render_template, request, session, redirect, url_for
import json, os
import sqlite3
from algo import Predateur, Vegetal, Proie, Meute, Jeu
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
# BASE_DIR : dossier contenant data/ (même dossier que app.py sur le serveur)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Stockage des parties en cours par session id
# jeu : dict {session_id -> objet Jeu} — non sérialisable, reste en mémoire serveur
# historique : stocké dans session Flask (listes de nombres, sérialisable)
_jeux = {}  # {session_id: Jeu}

def get_session_id():
    """Retourne un identifiant unique par session utilisateur."""
    if '_sid' not in session:
        import uuid
        session['_sid'] = str(uuid.uuid4())
        session.modified = True
    return session['_sid']

def get_jeu():
    return _jeux.get(get_session_id())

def set_jeu(j):
    _jeux[get_session_id()] = j

def get_historique():
    return session.get('historique', {"loup": [], "cerf": [], "herbe": []})

def set_historique(h):
    session['historique'] = h
    session.modified = True

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

# ── Succès ────────────────────────────────────────────────────────────────────

def charger_succes_permanents():
    """Charge les succes : depuis la DB si connecte, depuis la session si invite."""
    username = session.get('username') if session else None
    if username:
        conn = get_db_connection()
        try:
            rows = conn.execute(
                "SELECT succes_id, obtenu FROM Succes WHERE user_id = (SELECT id FROM Compte WHERE username = ?)",
                (username,)
            ).fetchall()
        finally:
            conn.close()
        if rows:
            return {r['succes_id']: bool(r['obtenu']) for r in rows}
        # Premiere connexion : initialiser la ligne pour chaque succes
        conn = get_db_connection()
        try:
            uid = conn.execute("SELECT id FROM Compte WHERE username = ?", (username,)).fetchone()
            if uid:
                for s in SUCCES_DEF:
                    conn.execute(
                        "INSERT OR IGNORE INTO Succes (user_id, succes_id, obtenu) VALUES (?,?,0)",
                        (uid['id'], s['id'])
                    )
                conn.commit()
        finally:
            conn.close()
        return {s['id']: False for s in SUCCES_DEF}
    # Invite ou non connecte : utiliser la session
    return session.get('succes_session', {s['id']: False for s in SUCCES_DEF})

def sauvegarder_succes_permanents(succes):
    """Sauvegarde les succes : dans la DB si connecte, dans la session si invite."""
    username = session.get('username') if session else None
    if username:
        conn = get_db_connection()
        try:
            uid = conn.execute("SELECT id FROM Compte WHERE username = ?", (username,)).fetchone()
            if uid:
                for succes_id, obtenu in succes.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO Succes (user_id, succes_id, obtenu) VALUES (?,?,?)",
                        (uid['id'], succes_id, 1 if obtenu else 0)
                    )
                conn.commit()
        finally:
            conn.close()
    else:
        session['succes_session'] = succes
        session.modified = True

# ── Prévisions ────────────────────────────────────────────────────────────────

def calculer_prevision(historique, dernier_meteo_cle):
    loup  = historique["loup"]
    cerf  = historique["cerf"]
    herbe = historique["herbe"]
    n = len(loup)
    if n < 3:
        return None
    alertes = []

    if cerf[-1] > 0 and loup[-1] / cerf[-1] > 0.5 and cerf[-1] < cerf[-2]:
        alertes.append({"emoji": "🐺", "texte": "Les loups sont trop nombreux face aux cerfs — famine imminente.", "niveau": "danger"})

    if n >= 4 and herbe[-1] < herbe[-2] < herbe[-3] and herbe[-1] < herbe[-3] * 0.6:
        alertes.append({"emoji": "🌿", "texte": "L'herbe s'effondre — les cerfs vont manquer de nourriture.", "niveau": "danger"})

    if cerf[-1] < cerf[-2] * 0.55 and cerf[-1] < cerf[-3] * 0.55:
        alertes.append({"emoji": "🦌", "texte": "Les cerfs disparaissent rapidement — les loups vont mourir de faim.", "niveau": "warning"})

    if (herbe[-1] > herbe[-2] * 1.4 and herbe[-2] > herbe[-3] * 1.2
            and cerf[-1] > cerf[-2] and cerf[-1] > 0):
        alertes.append({"emoji": "🦌", "texte": "L'herbe abonde et les cerfs prolifèrent — la meute va croître.", "niveau": "info"})

    if not alertes:
        def variation(lst): return max(abs(lst[-1]-lst[-2]), abs(lst[-2]-lst[-3]))
        if (loup[-1] > 0 and cerf[-1] > 0
                and variation(loup) < loup[-1] * 0.12
                and variation(cerf) < cerf[-1] * 0.12):
            alertes.append({"emoji": "🌤️", "texte": "L'écosystème est stable pour l'instant.", "niveau": "ok"})

    return alertes[0] if alertes else None

# ── Journal ───────────────────────────────────────────────────────────────────

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

# ── Vérification succès ───────────────────────────────────────────────────────

def verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants):
    nouveaux = []
    def debloquer(sid):
        if not succes_courants.get(sid):
            succes_courants[sid] = True
            defn = next(s for s in SUCCES_DEF if s["id"] == sid)
            nouveaux.append(defn)
    if annee >= 1:   debloquer("premier_pas")
    if annee >= 20:  debloquer("cycle")
    if predateur >= 75: debloquer("meute_royale")
    if proie >= 1200:      debloquer("troupeau")
    if vegetal >= 7000:   debloquer("foret_dense")
    if annee >= 40 and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("equilibre")
    if meteo_cle == "secheresse" and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("survie_seche")
    if meteo_cle == "hiver" and predateur > 0 and proie > 0 and vegetal > 0:
        debloquer("survie_hiver")
    if predateur == 0 or proie == 0 or vegetal == 0:
        debloquer("extinction")
    return nouveaux

# ── Build render args ─────────────────────────────────────────────────────────

def build_render_args(annee, predateur, proie, vegetal, meteo_event,
                      nouveaux_succes, prev_l, prev_c, prev_v, historique):
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

# ── Base de données ───────────────────────────────────────────────────────────

# Règles biologiques par défaut
DEFAULT_DATA = {
    "loup": {
        "reproduction": {"tout_les": [3, 3], "nombre_de_nv_nee": [1, 2], "maturiter_sexuel": 2},
        "mange": {"qui": "cerf", "tout_les": 1, "combien": 2}
    },
    "cerf": {
        "reproduction": {"tout_les": [1, 1], "nombre_de_nv_nee": [1, 2], "maturiter_sexuel": 2},
        "mange": {"qui": "herbe", "tout_les": 1, "combien": 2}
    },
    "herbe": {
        "reproduction": {"taux_r": 0.6, "capacite": 5000, "tout_les": [1, 1], "nombre_de_nv_nee": [1, 1]}
    }
}

def charger_regles():
    """Charge les règles biologiques de l'utilisateur connecté depuis la DB.
    Retourne les règles par défaut si invité ou aucune règle perso."""
    username = session.get('username') if session else None
    if username:
        conn = get_db_connection()
        try:
            row = conn.execute(
                "SELECT data FROM Regles WHERE user_id = (SELECT id FROM Compte WHERE username = ?)",
                (username,)
            ).fetchone()
        finally:
            conn.close()
        if row:
            data = json.loads(row['data'])
            # S'assurer que tout_les est bien une liste [min, max]
            for espece in data:
                tl = data[espece]["reproduction"]["tout_les"]
                if isinstance(tl, int):
                    data[espece]["reproduction"]["tout_les"] = [tl, tl]
            return data
    # Invité ou pas de règles perso : règles par défaut
    import copy
    return copy.deepcopy(DEFAULT_DATA)

def sauvegarder_regles(data):
    """Sauvegarde les règles biologiques en DB pour l'utilisateur connecté.
    Ignoré si invité."""
    username = session.get('username') if session else None
    if not username:
        return
    conn = get_db_connection()
    try:
        uid = conn.execute("SELECT id FROM Compte WHERE username = ?", (username,)).fetchone()
        if uid:
            conn.execute(
                "INSERT OR REPLACE INTO Regles (user_id, data) VALUES (?, ?)",
                (uid['id'], json.dumps(data, ensure_ascii=False))
            )
            conn.commit()
    finally:
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Table Compte sans colonne statut
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Compte (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Stats (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            nb_parties INTEGER DEFAULT 0,
            max_loups  INTEGER DEFAULT 0,
            max_cerfs  INTEGER DEFAULT 0,
            max_annees INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Compte(id)
        )
    ''')
    # Table Regles par utilisateur (JSON stocké comme texte)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Regles (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            data    TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Compte(id)
        )
    ''')
    # Table Succes par utilisateur
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Succes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            succes_id TEXT NOT NULL,
            obtenu    INTEGER DEFAULT 0,
            UNIQUE(user_id, succes_id),
            FOREIGN KEY (user_id) REFERENCES Compte(id)
        )
    ''')
    # Migration automatique : supprimer colonne statut si elle existe encore
    cols = [c[1] for c in conn.execute("PRAGMA table_info(Compte)").fetchall()]
    if 'statut' in cols:
        conn.execute("ALTER TABLE Compte RENAME TO Compte_old")
        conn.execute('''
            CREATE TABLE Compte (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute("INSERT INTO Compte (id, username, password) SELECT id, username, password FROM Compte_old")
        conn.execute("DROP TABLE Compte_old")
    conn.commit()
    conn.close()

def maj_stats(username, annee_fin, historique):
    """Met à jour les stats du joueur connecté après une partie."""
    if not username:
        return
    max_l = max(historique["loup"]) if historique["loup"] else 0
    max_c = max(historique["cerf"]) if historique["cerf"] else 0
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT id FROM Compte WHERE username = ?', (username,)).fetchone()
        if not user:
            return
        user_id = user['id']
        stats = conn.execute('SELECT * FROM Stats WHERE user_id = ?', (user_id,)).fetchone()
        if stats:
            # MAX calculé en Python — MAX() est une fonction d'agrégat SQL, invalide dans UPDATE
            nouveau_max_l = max(stats['max_loups'],  max_l)
            nouveau_max_c = max(stats['max_cerfs'],  max_c)
            nouveau_max_a = max(stats['max_annees'], annee_fin)
            conn.execute('''UPDATE Stats SET
                nb_parties = nb_parties + 1,
                max_loups  = ?,
                max_cerfs  = ?,
                max_annees = ?
                WHERE user_id = ?''', (nouveau_max_l, nouveau_max_c, nouveau_max_a, user_id))
        else:
            conn.execute('INSERT INTO Stats (user_id, nb_parties, max_loups, max_cerfs, max_annees) VALUES (?,1,?,?,?)',
                         (user_id, max_l, max_c, annee_fin))
        conn.commit()
    finally:
        conn.close()

def get_stats(username):
    """Récupère les stats d'un joueur."""
    if not username:
        return None
    conn = get_db_connection()
    row = conn.execute('''
        SELECT s.nb_parties, s.max_loups, s.max_cerfs, s.max_annees
        FROM Stats s JOIN Compte c ON s.user_id = c.id
        WHERE c.username = ?
    ''', (username,)).fetchone()
    conn.close()
    if row:
        return {'nb_parties': row['nb_parties'], 'max_loups': row['max_loups'],
                'max_cerfs': row['max_cerfs'], 'max_annees': row['max_annees']}
    return {'nb_parties': 0, 'max_loups': 0, 'max_cerfs': 0, 'max_annees': 0}

def get_leaderboards():
    """Retourne les 3 leaderboards top 10."""
    conn = get_db_connection()
    lb_annees = conn.execute('''
        SELECT c.username, s.max_annees as score
        FROM Stats s JOIN Compte c ON s.user_id = c.id
        WHERE s.max_annees > 0
        ORDER BY s.max_annees DESC LIMIT 10
    ''').fetchall()
    lb_loups = conn.execute('''
        SELECT c.username, s.max_loups as score
        FROM Stats s JOIN Compte c ON s.user_id = c.id
        WHERE s.max_loups > 0
        ORDER BY s.max_loups DESC LIMIT 10
    ''').fetchall()
    lb_cerfs = conn.execute('''
        SELECT c.username, s.max_cerfs as score
        FROM Stats s JOIN Compte c ON s.user_id = c.id
        WHERE s.max_cerfs > 0
        ORDER BY s.max_cerfs DESC LIMIT 10
    ''').fetchall()
    conn.close()
    return lb_annees, lb_loups, lb_cerfs

# Initialiser la DB au démarrage (avec migration automatique si besoin)
init_db()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    set_historique({"loup": [], "cerf": [], "herbe": []})
    session["journal"] = []
    succes_courants = charger_succes_permanents()
    user_stats = get_stats(session.get('username'))
    lb_annees, lb_loups, lb_cerfs = get_leaderboards()
    return render_template("index.html",
        succes_list=SUCCES_DEF, succes_courants=succes_courants,
        user_stats=user_stats,
        lb_annees=lb_annees, lb_loups=lb_loups, lb_cerfs=lb_cerfs)

@app.route("/init")
def init():
    return render_template("init.html")

@app.route("/tutoriel")
def tutoriel():
    return render_template("tutoriel.html")

@app.route("/complexite")
def complexite():
    return render_template("complexite.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    annee = int(request.form["annee"])
    if annee == 0:
        j = Jeu(
            Meute([Predateur("loup", 0) for _ in range(int(request.form["loup"]))]),
            [Proie("cerf", 0) for _ in range(int(request.form["cerf"]))],
            [Vegetal("herbe") for _ in range(int(request.form["herbe"]))]
        )
        set_jeu(j)
        set_historique({"loup": [], "cerf": [], "herbe": []})
        session["journal"] = []

    jeu = get_jeu()
    historique = get_historique()
    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    data_regles = charger_regles()
    _, _, _, meteo_event = jeu.update(annee, data_regles)
    annee += 1
    predateur = len(jeu.meute.predateurs)
    proie     = len(jeu.proies)
    vegetal   = len(jeu.vegetaux)
    historique["loup"].append(predateur)
    historique["cerf"].append(proie)
    historique["herbe"].append(vegetal)
    set_historique(historique)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        sc = charger_succes_permanents()
        verifier_succes(annee, predateur, proie, vegetal,
                        meteo_event["cle"] if meteo_event else None, sc)
        sauvegarder_succes_permanents(sc)
        maj_stats(session.get('username'), annee, historique)
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=sc,
            historique=json.dumps(historique))

    args = build_render_args(annee, predateur, proie, vegetal, meteo_event, [], prev_l, prev_c, prev_v, historique)
    return render_template("game.html", **args)

@app.route("/accelerer", methods=["POST"])
def accelerer():
    """Simule N années d'un coup."""
    nb_annees = max(1, min(50, int(request.form.get("nb_annees", 5))))
    annee = int(request.form["annee"])
    jeu = get_jeu()
    historique = get_historique()

    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    dernier_meteo = None
    data_regles = charger_regles()
    for _ in range(nb_annees):
        _, _, _, meteo_event = jeu.update(annee, data_regles)
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
            maj_stats(session.get('username'), annee, historique)
            return render_template("fin.html",
                annee=annee, espece_morte=espece_morte,
                predateur=predateur, proie=proie, vegetal=vegetal,
                succes_list=SUCCES_DEF, succes_courants=sc,
                historique=json.dumps(historique))

    set_historique(historique)
    args = build_render_args(annee, predateur, proie, vegetal,
                             dernier_meteo, [], prev_l, prev_c, prev_v, historique)
    args["annees_sautees"] = nb_annees
    return render_template("game.html", **args)

@app.route("/update_ajouter", methods=["GET", "POST"])
def update_ajouter():
    jeu = get_jeu()
    historique = get_historique()
    annee = int(request.form["base_annee"])
    for _ in range(int(request.form["loup"])): jeu.meute.predateurs.append(Predateur("loup", 0))
    for _ in range(int(request.form["cerf"])): jeu.proies.append(Proie("cerf", 0))
    for _ in range(int(request.form["herbe"])): jeu.vegetaux.append(Vegetal("herbe"))

    prev_l = historique["loup"][-1] if historique["loup"] else None
    prev_c = historique["cerf"][-1] if historique["cerf"] else None
    prev_v = historique["herbe"][-1] if historique["herbe"] else None

    data_regles = charger_regles()
    _, _, _, meteo_event = jeu.update(annee, data_regles)
    annee += 1
    predateur = len(jeu.meute.predateurs)
    proie     = len(jeu.proies)
    vegetal   = len(jeu.vegetaux)
    historique["loup"].append(predateur)
    historique["cerf"].append(proie)
    historique["herbe"].append(vegetal)
    set_historique(historique)

    if predateur == 0 or proie == 0 or vegetal == 0:
        espece_morte = "loups" if predateur == 0 else ("cerfs" if proie == 0 else "herbe")
        sc = charger_succes_permanents()
        verifier_succes(annee, predateur, proie, vegetal,
                        meteo_event["cle"] if meteo_event else None, sc)
        sauvegarder_succes_permanents(sc)
        maj_stats(session.get('username'), annee, historique)
        return render_template("fin.html",
            annee=annee, espece_morte=espece_morte,
            predateur=predateur, proie=proie, vegetal=vegetal,
            succes_list=SUCCES_DEF, succes_courants=sc,
            historique=json.dumps(historique))

    args = build_render_args(annee, predateur, proie, vegetal, meteo_event, [], prev_l, prev_c, prev_v, historique)
    return render_template("game.html", **args)

@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    jeu = get_jeu()
    annee = int(request.form["annee"])
    return render_template("ajouter.html",
        annee=annee, predateur=len(jeu.meute.predateurs),
        proie=len(jeu.proies), vegetal=len(jeu.vegetaux))

@app.route("/reset_succes")
def reset_succes():
    sauvegarder_succes_permanents({s["id"]: False for s in SUCCES_DEF})
    return "Succes reinitialises.", 200

@app.route("/parametre")
def regles():
    data = charger_regles()
    return render_template("parametre.html", data=data)

@app.route("/modifier", methods=["GET", "POST"])
def modifier():
    vitesse_herbe = request.form.get("vitesse_herbe", "normal")
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
    sauvegarder_regles(data)

    # Passer toutes les variables nécessaires à index.html
    succes_courants = charger_succes_permanents()
    user_stats = get_stats(session.get('username'))
    lb_annees, lb_loups, lb_cerfs = get_leaderboards()
    return render_template("index.html",
        succes_list=SUCCES_DEF, succes_courants=succes_courants,
        user_stats=user_stats,
        lb_annees=lb_annees, lb_loups=lb_loups, lb_cerfs=lb_cerfs)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    erreur = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Compte (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            erreur = "Ce nom d'utilisateur est déjà pris."
        finally:
            conn.close()
    return render_template('signup.html', erreur=erreur)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM Compte WHERE username = ?', (username,)).fetchone()
        finally:
            conn.close()
        if user and check_password_hash(user['password'], password):
            session.pop('guest', None)
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            erreur = "Identifiants ou mot de passe incorrects."
    return render_template('login.html', erreur=erreur)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('guest', None)
    return redirect(url_for('login'))

@app.route('/guest')
def guest():
    """Connexion en tant qu'invité — stats non enregistrées."""
    session.pop('username', None)
    session['guest'] = True
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)