from flask import Flask, request, redirect, jsonify
import requests
import os

app = Flask(__name__)

# ⚠️ Ces variables doivent être dans les variables d'environnement sur Render
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "https://dashboard-l77g.onrender.com/callback"  

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
    admin_guilds = [guild for guild in guilds if int(guild["permissions"]) & 0x8]

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

import os

print("Démarrage du serveur Flask...")  
print(f"PORT utilisé : {os.getenv('PORT', 10000)}")  
print(f"Client ID : {os.getenv('DISCORD_CLIENT_ID')}")  
print(f"Client Secret : {os.getenv('DISCORD_CLIENT_SECRET')}")  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(("127.0.0.1", int(os.getenv("PORT", 10000))))

if result == 0:
    print("✅ Flask écoute bien sur le port 10000")
else:
    print("❌ Flask ne tourne pas sur le port 10000")


