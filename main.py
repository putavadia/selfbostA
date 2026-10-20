# language: Python 3, file: main.py, target: Railway Worker
# *selfbot com auto-bump, delay aleatorio, comandos !bump, !rbump e !ping para contas autorizadas*

import os
import asyncio
import discord
from discord.ext import tasks
import random
import time

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
DISBOARD_ID = 302050872383242240

# IDs das contas autorizadas a disparar comandos (!bump, !rbump, !ping) de qualquer conta
AUTHORIZED_USERS = [ 1544934280256299050
    # Adicione os IDs das contas permitidas aqui, exemplo:
    # 1544934280256299050
]

bot = discord.Client(self_bot=True)

@tasks.loop(hours=2)
async def auto_bump():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("[-] Canal não encontrado.")
        return
    
    # Delay aleatório entre 5 (300s) e 10 minutos (600s) estritamente dentro da função async
    delay_extra = random.randint(300, 600)
    delay_minutos = delay_extra // 60
    print(f"[*] Aguardando {delay_minutos} minutos ({delay_extra} segundos) de delay aleatório...")
    await asyncio.sleep(delay_extra)
    
    try:
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado com sucesso.")
        else:
            print("[-] Comando /bump do Disboard não visível neste canal.")
    except Exception as e:
        print(f"[-] Erro na execução do bump: {e}")

@bot.event
async def on_message(message):
    # Apenas processa mensagens no canal configurado do bump
    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip()
    is_owner = message.author.id == bot.user.id
    is_authorized = message.author.id in AUTHORIZED_USERS

    # Permite que o dono ou usuários autorizados utilizem os comandos de qualquer conta
    if is_owner or is_authorized:
        
        # 1. Comando !bump
        if content == "!bump":
            try:
                await message.delete()
            except Exception:
                pass
            
            print(f"[*] Comando !bump acionado por {message.author} (ID: {message.author.id}).")
            if not auto_bump.is_running():
                auto_bump.start()
                await message.channel.send(f"[+] Auto-bump ativado por {message.author.mention}! Ciclo de 2h + margem iniciado.", delete_after=5)
            else:
                await message.channel.send("[!] O ciclo já está em execução.", delete_after=5)

        # 2. Comando !rbump (Reinicia o ciclo do auto-bump com segurança)
        elif content == "!rbump":
            try:
                await message.delete()
            except Exception:
                pass
            
            print(f"[*] Comando !rbump (reiniciar) acionado por {message.author} (ID: {message.author.id}).")
            
            if auto_bump.is_running():
                auto_bump.cancel()
            
            auto_bump.start()
            await message.channel.send(f"[+] Ciclo de auto-bump reiniciado por {message.author.mention}!", delete_after=5)

        # 3. Comando !ping (Testa a latência/resposta do selfbot)
        elif content == "!ping":
            try:
                await message.delete()
            except Exception:
                pass
            
            latency = round(bot.latency * 1000)
            await message.channel.send(f"[pong] Selfbot online e operacional! Latência: {latency}ms (Solicitado por {message.author.mention})", delete_after=6)

@bot.event
async def on_ready():
    print(f"[*] Conectado como {bot.user}. Pronto para receber comandos de contas autorizadas.")

if __name__ == "__main__":
    if not TOKEN:
        print("[-] Erro: Variável DISCORD_TOKEN não configurada.")
        exit(1)
    
    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"[-] Conexão perdida: {e}. Reconectando em 10 segundos...")
            time.sleep(10)
