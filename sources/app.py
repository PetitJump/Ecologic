# Projet : Naturalia
# Auteurs : Margot, Hugo, Carl, Killian

from flask import Flask, render_template, request, session, redirect, url_for
import json, os
import sqlite3
from algo import Predateur, Vegetal, Proie, Meute, Jeu
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

# --- CONFIGURATION CHEMINS ---
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUCCES_FILE = os.path.join(DATA_DIR, "succes_permanents.json")

# Assurer l'existence du dossier data
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

SUCCES_DEF = [
    {"id": "premier_pas",  "emoji": "🌱", "nom": "Premier pas", "desc": "Lancer la simulation pour la première fois."},
    {"id": "equilibre",    "emoji": "⚖️",  "nom": "Équilibre fragile", "desc": "Maintenir la vie pendant 10 ans."},
    {"id": "meute_royale", "emoji": "🐺", "nom": "Meute royale", "desc": "Atteindre 100 loups."},
    {"id": "troupeau",     "emoji": "🦌", "nom": "Troupeau parfait", "desc": "Atteindre 50 cerfs."},
    {"id": "foret_dense",  "emoji": "🌿", "nom": "Forêt dense", "desc": "Atteindre 200 herbes."},
    {"id": "survie_seche", "emoji": "☀️",  "nom": "Résistance solaire", "desc": "Survivre à une sécheresse."},
    {"id": "survie_hiver", "emoji": "❄️",  "nom": "Hiver de fer", "desc": "Survivre à un hiver rigoureux."},
    {"id": "cycle",        "emoji": "🔄", "nom": "Le Grand Cycle", "desc": "Atteindre l'année 20."},
    {"id": "extinction",   "emoji": "💀", "nom": "Extinction", "desc": "Une espèce a disparu."}
]

# --- BASE DE DONNÉES ---

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Table Comptes
    conn.execute('''CREATE TABLE IF NOT EXISTS Compte 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, statut TEXT NOT NULL)''')
    # Table Scores
    conn.execute('''CREATE TABLE IF NOT EXISTS Scores 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, score INTEGER NOT NULL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- LOGIQUE SYSTÈME ---

def charger_succes_permanents():
    if os.path.exists(SUCCES_FILE):
        with open(SUCCES_FILE, "r") as f: return json.load(f)
    return {s["id"]: False for s in SUCCES_DEF}

def sauvegarder_succes_permanents(succes):
    with open(SUCCES_FILE, "w") as f: json.dump(succes, f, indent=2)

def verifier_succes(annee, predateur, proie, vegetal, meteo_cle, succes_courants):
    nouveaux = []
    def debloquer(sid):
        if not succes_courants.get(sid):
            succes_courants[sid] = True
            nouveaux.append(next(s for s in SUCCES_DEF if s["id"] == sid))
    
    if annee >= 1: debloquer("premier_pas")
    if annee >= 20: debloquer("cycle")
    if predateur >= 100: debloquer("meute_royale")
    if proie >= 50: debloquer("troupeau")
    if vegetal >= 200: debloquer("foret_dense")
    if annee >= 10 and predateur > 0 and proie > 0 and vegetal > 0: debloquer("equilibre")
    if predateur == 0 or proie == 0 or vegetal == 0: debloquer("extinction")
    return nouveaux

def enregistrer_score(annee):
    if 'username' in session:
        conn = get_db_connection()
        conn.execute('INSERT INTO Scores (username, score) VALUES (?, ?)', (session['username'], annee))
        conn.commit()
        conn.close()

def build_render_args(annee, predateur, proie, vegetal, meteo_event, nouveaux_succes, prev_l, prev_c, prev_v):
    sc = charger_succes_permanents()
    m_cle = meteo_event["cle"] if meteo_event else None
    nouveaux = verifier_succes(annee, predateur, proie, vegetal, m_cle, sc)
    if nouveaux: sauvegarder_succes_permanents(sc)
    
    return dict(
        annee=annee, predateur=predateur, proie=proie, vegetal=vegetal,
        delta_l=predateur - prev_l if prev_l is not None else 0,
        delta_c=proie - prev_c if prev_c is not None else 0,
        delta_v=vegetal - prev_v if prev_v is not None else 0,
        meteo=meteo_event, nouveaux_succes=nouveaux_succes + nouveaux,
        succes_list=SUCCES_DEF, succes_courants=sc,
        historique=json.dumps(historique), journal=session.get("journal", [])
    )

# --- ROUTES ---

@app.route("/")
def index():
    global historique
    historique = {"loup": [], "cerf": [], "herbe": []}
    session["journal"] = []
    
    # Récupération du TOP 5 des scores
    conn = get_db_connection()
    scores = conn.execute('''SELECT username, MAX(score) as score FROM Scores 
                             GROUP BY username ORDER BY score DESC LIMIT 5''').fetchall()
    conn.close()
    
    return render_template("index.html", succes_list=SUCCES_DEF, 
                           succes_courants=charger_succes_permanents(), 
                           scores_leaderboard=scores)

@app.route("/game", methods=["GET", "POST"])
def game():
    global historique, jeu
    if request.method == "GET": return redirect(url_for('init'))
    
    annee = int(request.form.get("annee", 0))
    if annee == 0:
        jeu = Jeu(
            Meute([Predateur("loup", 0) for _ in range(int(request.form["loup"]))]),
            [Proie("cerf", 0) for _ in range(int(request.form["cerf"]))],
            [Vegetal("herbe") for _ in range(int(request.form["herbe"]))]
        )
        historique = {"loup": [], "cerf": [], "herbe": []}

    prev_l, prev_c, prev_v = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
    _, _, _, meteo_event = jeu.update(annee)
    annee += 1
    
    l, c, v = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
    historique["loup"].append(l); historique["cerf"].append(c); historique["herbe"].append(v)

    if l == 0 or c == 0 or v == 0:
        enregistrer_score(annee)
        return render_template("fin.html", annee=annee, predateur=l, proie=c, vegetal=v, historique=json.dumps(historique))

    return render_template("game.html", **build_render_args(annee, l, c, v, meteo_event, [], prev_l, prev_c, prev_v))

@app.route("/accelerer", methods=["POST"])
def accelerer():
    global historique, jeu
    nb = int(request.form.get("nb_annees", 5))
    annee = int(request.form["annee"])
    prev_l, prev_c, prev_v = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
    
    meteo = None
    for _ in range(nb):
        _, _, _, m = jeu.update(annee)
        if m: meteo = m
        annee += 1
        l, c, v = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
        historique["loup"].append(l); historique["cerf"].append(c); historique["herbe"].append(v)
        
        if l == 0 or c == 0 or v == 0:
            enregistrer_score(annee)
            return render_template("fin.html", annee=annee, predateur=l, proie=c, vegetal=v, historique=json.dumps(historique))

    return render_template("game.html", **build_render_args(annee, l, c, v, meteo, [], prev_l, prev_c, prev_v))

@app.route("/update_ajouter", methods=["POST"])
def update_ajouter():
    global jeu
    annee = int(request.form["base_annee"])
    pl, pc, pv = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
    
    for _ in range(int(request.form.get("loup", 0))): jeu.meute.predateurs.append(Predateur("loup", 0))
    for _ in range(int(request.form.get("cerf", 0))): jeu.proies.append(Proie("cerf", 0))
    for _ in range(int(request.form.get("herbe", 0))): jeu.vegetaux.append(Vegetal("herbe"))
    
    l, c, v = len(jeu.meute.predateurs), len(jeu.proies), len(jeu.vegetaux)
    return render_template("game.html", **build_render_args(annee, l, c, v, None, [], pl, pc, pv))

# --- AUTHENTIFICATION ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Compte WHERE username = ?', (request.form['username'],)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], request.form['password']):
            session['username'] = user['username']
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        hashed = generate_password_hash(request.form['password'])
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Compte (username, password, statut) VALUES (?, ?, ?)',
                         (request.form['username'], hashed, request.form['statut']))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except: return render_template('signup.html', erreur="Nom déjà pris.")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# --- AUTRES ROUTES ---
@app.route("/init")
def init(): return render_template("init.html")

@app.route("/ajouter", methods=["POST"])
def ajouter(): 
    return render_template("ajouter.html", annee=request.form["annee"], 
                           predateur=len(jeu.meute.predateurs), proie=len(jeu.proies), vegetal=len(jeu.vegetaux))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
