# language: Python 3, file: main.py, target: Railway Selfbot Worker
# *selfbot unificado: disboard bump + auditor de bio via canal de log + varredura de 30 min*

import os
import asyncio
import discord
from discord.ext import tasks
import random
import time

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
DISBOARD_ID = 302050872383242240

GUILD_ID = 1551752786088304640          # ID do servidor
ROLE_ID = 1560113149171077182            # ID do cargo Leais
LOG_CHANNEL_ID = 1560121886761947149     # Canal onde o bot oficial manda o sinal VERIFY_REQUEST

bot = discord.Client(self_bot=True)

@tasks.loop(hours=2)
async def auto_bump():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return
    
    delay_extra = random.randint(300, 600)
    await asyncio.sleep(delay_extra)
    
    try:
        commands_list = await channel.application_commands()
        bump_cmd = next((cmd for cmd in commands_list if cmd.name == "bump" and cmd.application_id == DISBOARD_ID), None)
        if bump_cmd:
            await bump_cmd.__call__(channel=channel)
            print("[+] /bump executado com sucesso.")
    except Exception as e:
        print(f"[-] Erro no bump: {e}")

@tasks.loop(minutes=30)
async def audit_existing_roles():
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
        
    role = guild.get_role(ROLE_ID)
    if not role:
        return

    print("[*] Iniciando auditoria de 30 minutos nos membros com o cargo Leais...")
    for member in role.members:
        if member.bot:
            continue
        try:
            profile = await member.profile()
            bio = profile.bio if profile.bio else ""
            termos = ["discord.gg/bolha", "https://discord.gg/bolha", "/bolha"]
            encontrou = any(termo in bio.lower() for termo in termos)
            
            if not encontrou:
                await member.remove_roles(role)
                print(f"[-] Removido cargo Leais de {member} (convite ausente na bio).")
        except Exception as e:
            continue

@bot.event
async def on_message(message):
    content = message.content.strip()
    
    # 1. Acionador manual de bump via chat
    if message.author.id == bot.user.id and content == "!bump" and message.channel.id == CHANNEL_ID:
        try:
            await message.delete()
        except:
            pass
        if not auto_bump.is_running():
            auto_bump.start()
            await message.channel.send("[+] Auto-bump ativado!", delete_after=5)

    # 2. Intercepta o sinal do Bot Oficial no canal de log (1560121886761947149)
    if message.channel.id == LOG_CHANNEL_ID and content.startswith("VERIFY_REQUEST:"):
        try:
            _, user_id_str, guild_id_str = content.split(":")
            guild = bot.get_guild(int(guild_id_str))
            if not guild:
                return
                
            member = guild.get_member(int(user_id_str))
            role = guild.get_role(ROLE_ID)
            if not member or not role:
                return

            profile = await member.profile()
            bio = profile.bio if profile.bio else ""
            
            termos = ["discord.gg/bolha", "https://discord.gg/bolha", "/bolha"]
            encontrou = any(termo in bio.lower() for termo in termos)
            
            log_channel = message.channel
            if encontrou:
                if role not in member.roles:
                    await member.add_roles(role)
                    await log_channel.send(f"[+] Biografia verificada para {member.mention}! Cargo Leais concedido.", delete_after=6)
                else:
                    await log_channel.send(f"[!] {member.mention}, você já possui o cargo Leais.", delete_after=5)
            else:
                await log_channel.send(f"[-] {member.mention}, convite não encontrado na sua biografia.", delete_after=6)
                
            # Opcional: apaga a mensagem de sinal do bot oficial para manter o canal limpo
            await message.delete()
        except Exception as e:
            print(f"[-] Erro ao processar sinal de verificacao: {e}")

@bot.event
async def on_ready():
    print(f"[*] Selfbot operacional como {bot.user}.")
    if not audit_existing_roles.is_running():
        audit_existing_roles.start()

if __name__ == "__main__":
    if not TOKEN:
        exit(1)
    while True:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"[-] Conexão perdida: {e}. Reconectando...")
            time.sleep(10)
