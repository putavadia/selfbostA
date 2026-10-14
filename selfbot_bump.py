# language: Python 3, file: main.py, target: Railway Worker
# *selfbot com ativacao via comando de chat !bump*

import os
import asyncio
import discord
from discord.ext import tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
DISBOARD_ID = 302050872383242240

bot = discord.Client(self_bot=True)

@tasks.loop(hours=2)
async def auto_bump():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("[-] Canal nao encontrado.")
        return
    
    try:
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado automaticamente.")
        else:
            print("[-] Comando /bump do Disboard nao visivel neste canal.")
    except Exception as e:
        print(f"[-] Erro na execucao do bump: {e}")

@bot.event
async def on_message(message):
    # Garante que o comando so responde a mensagens enviadas por voce mesmo no chat
    if message.author.id == bot.user.id and message.content.strip() == "!bump":
        if message.channel.id == CHANNEL_ID:
            await message.delete() # Opcional: apaga a sua mensagem "!bump"
            print("[*] Comando !bump recebido. Disparando ciclo de auto-bump...")
            if not auto_bump.is_running():
                auto_bump.start()
                await message.channel.send("[+] Auto-bump ativado com sucesso! Ciclo de 2 horas iniciado.", delete_after=5)
            else:
                await message.channel.send("[!] O auto-bump ja esta rodando.", delete_after=5)

@bot.event
async def on_ready():
    print(f"[*] Conectado como {bot.user}. Digite '!bump' no canal configurado para iniciar o ciclo.")

if __name__ == "__main__":
    if not TOKEN:
        print("[-] Erro: Variavel DISCORD_TOKEN nao configurada.")
        exit(1)
    bot.run(TOKEN)
