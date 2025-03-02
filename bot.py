import discord
from discord.ext import commands
import os
import json
import requests
from flask import Flask
import threading

# Récupérer le token depuis Render
TOKEN = os.getenv("TOKEN_BOT_DISCORD")

# Création du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!!", intents=intents)

# Serveur Flask pour Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne 🚀"

def run_flask():
    port = int(os.getenv("PORT", 10000))  # Render assigne un port spécifique
    app.run(host="0.0.0.0", port=port, debug=False)

# Charger les commandes du serveur depuis JSON
def load_commands(server_id):
    file_path = f'commands/{server_id}.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)
    with open(file_path, 'r') as f:
        return json.load(f)

# Exécuter les commandes personnalisées
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    server_id = str(message.guild.id)
    commands_data = load_commands(server_id)

    for command, response in commands_data.items():
        if message.content.startswith(command):
            await message.channel.send(response)
            return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

# Lancer Flask en parallèle du bot
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()  # Lancer Flask en arrière-plan
    bot.run(TOKEN)
