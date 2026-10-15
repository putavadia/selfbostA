# language: Python 3, file: main.py, target: Railway Worker
# *selfbot limpo com multiconte e delay aleatorio dentro da tarefa assincrona*

import os
import asyncio
import discord
from discord.ext import tasks
import random
import time

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
DISBOARD_ID = 302050872383242240

# IDs das contas autorizadas a disparar o comando !bump
AUTHORIZED_USERS = [
    # Adicione IDs extras aqui se necessario, ex: 123456789012345678
]

bot = discord.Client(self_bot=True)

@tasks.loop(hours=2)
async def auto_bump():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("[-] Canal nao encontrado.")
        return
    
    # Delay aleatorio entre 5 (300s) e 10 minutos (600s) estritamente dentro da funcao async
    delay_extra = random.randint(300, 600)
    delay_minutos = delay_extra // 60
    print(f"[*] Aguardando {delay_minutos} minutos ({delay_extra} segundos) de delay aleatorio...")
    await asyncio.sleep(delay_extra)
    
    try:
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado com sucesso.")
        else:
            print("[-] Comando /bump do Disboard nao visivel neste canal.")
    except Exception as e:
        print(f"[-] Erro na execucao do bump: {e}")

@bot.event
async def on_message(message):
    if message.content.strip() == "!bump" and message.channel.id == CHANNEL_ID:
        is_owner = message.author.id == bot.user.id
        is_authorized = message.author.id in AUTHORIZED_USERS
        
        if is_owner or is_authorized:
            try:
                await message.delete()
            except Exception:
                pass
            
            print(f"[*] Comando !bump acionado por {message.author} (ID: {message.author.id}).")
            if not auto_bump.is_running():
                auto_bump.start()
                await message.channel.send(f"[+] Auto-bump ativado por {message.author.mention}! Ciclo de 2h + margem iniciado.", delete_after=5)
            else:
                await message.channel.send("[!] O ciclo ja esta em execucao.", delete_after=5)

@bot.event
async def on_ready():
    print(f"[*] Conectado como {bot.user}. Pronto para receber comando de contas autorizadas.")

if __name__ == "__main__":
    if not TOKEN:
        print("[-] Erro: Variavel DISCORD_TOKEN nao configurada.")
        exit(1)
    
    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"[-] Conexao perdida: {e}. Reconectando em 10 segundos...")
            time.sleep(10)
