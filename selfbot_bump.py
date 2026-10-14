# language: Python 3, file: selfbot_bump.py, target: Cross-platform
# *executa o slash command /bump do Disboard periodicamente usando token de usuario (selfbot)*

import asyncio
import discord
from discord.ext import commands, tasks

# Requer instalacao previa: pip install discord.py-self
TOKEN = "MTU1NjA0OTI4NzYzOTYwMTE5Ng.GeEUJW.-LETLZ6MppRyLhYChi-_rrfadAWFvWBg0hVcG4"
CHANNEL_ID = 1551783089389445271  # ID do canal onde o comando sera disparado
DISBOARD_ID = 302050872383242240  # ID oficial do Disboard

bot = commands.Bot(command_prefix="!", self_bot=True)

@tasks.loop(hours=2)
async def auto_bump():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("[-] Canal nao encontrado.")
        return
    
    try:
        # Busca os comandos disponiveis no canal e filtra o /bump do Disboard
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado com sucesso pelo selfbot.")
        else:
            print("[-] Comando /bump do Disboard nao visivel neste canal.")
    except Exception as e:
        print(f"[-] Erro na execucao do bump: {e}")

@bot.event
async def on_ready():
    print(f"[*] Conectado como {bot.user} (Selfbot ativo).")
    if not auto_bump.is_running():
        auto_bump.start()

bot.run(TOKEN)