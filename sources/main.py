#Projet : Naturalia
#Auteurs : Margot, Hugo, Carl, Killian

"""
Point d'entrée principal de l'application Naturalia.
Lance le serveur Flask en mode développement.
"""

from app import app

if __name__ == "__main__":
    app.run(debug=True)
