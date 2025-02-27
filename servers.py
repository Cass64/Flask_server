from flask import Flask, request, redirect, jsonify
import requests
import os

app = Flask(__name__)

# ⚠️ Ces variables doivent être dans les variables d'environnement sur Render
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "https://ton-site.onrender.com/callback"  # Remplace par l'URL de ton site

@app.route("/auth/callback")
def auth_callback():
    """ Cette route gère le callback après l'authentification Discord """
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Obtenir le token d'accès
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to get token"}), 400

    # Récupérer le token et rediriger vers la page des serveurs
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    # Redirection vers /servers avec le token d'accès
    return redirect(f"/servers?access_token={access_token}")

@app.route("/servers", methods=["GET"])
def get_user_guilds():
    """ Cette route récupère les serveurs de l'utilisateur (guilds) """
    token = request.args.get("access_token")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    # Récupérer les guilds de l'utilisateur
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch guilds"}), 400

    guilds = response.json()

    # Filtrer les serveurs où l'utilisateur a des permissions d'administrateur
    admin_guilds = [guild for guild in guilds if "administrator" in guild.get("permissions", [])]

    return jsonify({"guilds": admin_guilds})

@app.route("/auth/user", methods=["GET"])
def get_user():
    """ Cette route récupère les données de l'utilisateur """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    # Récupérer les données de l'utilisateur via l'API Discord
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user data"}), 400

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render va utiliser ce port automatiquement
