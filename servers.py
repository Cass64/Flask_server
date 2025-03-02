from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Récupérer les variables d'environnement
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "https://casseco-6sa8.onrender.com/auth/callback"

@app.route("/auth/callback")
def auth_callback():
    """ Callback après l'authentification Discord """
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

    token_data = response.json()
    return jsonify({"access_token": token_data.get("access_token")})

@app.route("/servers")
def get_user_guilds():
    """ Récupère les serveurs de l'utilisateur """
    token = request.args.get("access_token")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch guilds"}), 400

    guilds = response.json()
    admin_guilds = [guild for guild in guilds if int(guild["permissions"]) & 0x8]

    return jsonify({"guilds": admin_guilds})

@app.route("/auth/user")
def get_user():
    """ Récupère les infos de l'utilisateur """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "No token provided"}), 401

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user data"}), 400

    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

