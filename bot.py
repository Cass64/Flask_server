import discord
from discord.ext import commands
import os
import json
import requests

# Récupérer le token depuis Render
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Création du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!!", intents=intents)

# Fonction pour obtenir les serveurs via l'API Flask
def get_user_guilds():
    url = "https://ton-site.onrender.com/callback"  # L'URL de ton backend Flask
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['guilds']
    return []

# Charger les commandes du serveur depuis JSON
def load_commands(server_id):
    try:
        with open(f'commands/{server_id}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

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
    print(f"Bot connecté en tant que {bot.user}")

bot.run(TOKEN)
