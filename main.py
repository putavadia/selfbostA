# language: Python 3, file: main.py, target: Railway Worker
# *selfbot com auto-bump e execução robusta de slash commands*

import os
import asyncio
import discord
from discord.ext import tasks
import random
import time

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
DISBOARD_ID = 302050872383242240

AUTHORIZED_USERS = [ 
    1544934280256299050
]

bot = discord.Client(self_bot=True)

async def executar_bump(channel):
    try:
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado com sucesso.")
            return True
        else:
            print("[-] Comando /bump do Disboard não visível neste canal.")
            return False
    except Exception as e:
        print(f"[-] Erro na execução do bump: {e}")
        return False

@tasks.loop(hours=2)
async def auto_bump():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("[-] Canal não encontrado.")
        return
    
    # Delay fixo de 5 minutos (convertido para segundos para o asyncio.sleep)
    delay_minutos = 5
    delay_segundos = delay_minutos * 60
    
    print(f"[*] Aguardando o delay fixo de {delay_minutos} minuto(s)...")
    await asyncio.sleep(delay_segundos)
    
    await executar_bump(channel)

@bot.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip()
    is_owner = message.author.id == bot.user.id
    is_authorized = message.author.id in AUTHORIZED_USERS

    if is_owner or is_authorized:
        
        # 1. Comando !bump
        if content == "!bump":
            try:
                await message.delete()
            except Exception:
                pass
            
            print(f"[*] Comando !bump acionado por {message.author} (ID: {message.author.id}).")
            sucesso = await executar_bump(message.channel)

            if not auto_bump.is_running():
                auto_bump.start()
                await message.channel.send(f"[+] Auto-bump ativado por {message.author.mention}!", delete_after=5)
            else:
                if sucesso:
                    await message.channel.send(f"[+] Bump executado manualmente por {message.author.mention}!", delete_after=5)
                else:
                    await message.channel.send(f"[!] O ciclo está ativo, mas o comando /bump falhou.", delete_after=5)

        # 2. Comando !rbump (Reinicia o ciclo e executa o bump na hora)
        elif content == "!rbump":
            try:
                await message.delete()
            except Exception:
                pass
            
            print(f"[*] Comando !rbump (reiniciar) acionado por {message.author} (ID: {message.author.id}).")
            
            if auto_bump.is_running():
                auto_bump.cancel()
            
            auto_bump.start()
            sucesso = await executar_bump(message.channel)

            if sucesso:
                await message.channel.send(f"[+] Ciclo reiniciado e bump executado por {message.author.mention}!", delete_after=5)
            else:
                await message.channel.send(f"[+] Ciclo reiniciado por {message.author.mention}, mas houve um erro ao disparar o /bump.", delete_after=5)

        # 3. Comando !ping
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
