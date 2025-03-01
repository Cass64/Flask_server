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
    
# Fonction pour obtenir les serveurs via l'API Flask
def get_user_guilds():
    url = "https://casseco-6sa8.onrender.com"  # L'URL de ton backend Flask
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['guilds']
    return []


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
    print(f"Bot connecté en tant que {bot.user}")

bot.run(TOKEN)
