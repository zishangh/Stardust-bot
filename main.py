import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import datetime

# Flask Setup (To keep the bot alive on Render background)
app = Flask('')

@app.route('/')
def home():
    return "Stardust Cafe Bot is running perfectly!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot Setup with High-Level Permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} high-level command(s) successfully!")
    except Exception as e:
        print(f"Sync Error: {e}")
    await bot.change_presence(activity=discord.Game(name="Managing Stardust Cafe ☕"))

# =========================================================
# 🛠️ MODULE 1: HIGH-LEVEL MODERATION COMMANDS (English)
# =========================================================

# 1. KICK COMMAND
@bot.tree.command(name="kick", description="🔒 Kick a member from the server")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="🔨 Member Kicked",
            description=f"**{member.name}** has been successfully removed from the server.",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text="Stardust Security System ✨")
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Error: I do not have permission to kick this member.", ephemeral=True)

# 2. BAN COMMAND
@bot.tree.command(name="ban", description="🚫 Permanently ban a member from the server")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🚨 Member Banned",
            description=f"**{member.name}** has been permanently banned from the server.",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text="Stardust Security System ✨")
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Error: Failed to ban. Please check my role hierarchy.", ephemeral=True)

# 3. MUTE / TIMEOUT COMMAND
@bot.tree.command(name="mute", description="🤫 Timeout a member for a specific duration")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🤫 Member Muted",
            description=f"**{member.mention}** has been placed in timeout for `{minutes}` minutes.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text="Stardust Security System ✨")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: Could not mute member: {e}", ephemeral=True)

# =========================================================
# 🍧 MODULE 2: CUTE & UNIQUE CAFE FEATURES
# =========================================================

@bot.tree.command(name="serve", description="☕ Serve a fresh, warm coffee to a friend")
async def serve(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="✨ Stardust Cafe Special Order ✨",
        description=f"{interaction.user.mention} has served a fresh, warm **Stardust Special Coffee** to {member.mention}! ☕🍰",
        color=discord.Color.from_rgb(245, 222, 179)
    )
    embed.set_footer(text="Have a cozy day at Stardust Cafe! 💕")
    await interaction.response.send_message(embed=embed)

# =========================================================
# 📜 MODULE 3: TOP LEVEL HELP & INFO MENU
# =========================================================

@bot.tree.command(name="help", description="📖 View all available commands for Stardust Bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ Stardust Cafe Bot - Premium Menu ✨",
        description="Welcome! I am a premium utility and moderation bot built for your community. Here are my features:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🛡️ Moderation System", value="`/kick` - Remove a disruptive member\n`/ban` - Permanently ban a user\n`/mute` - Timeout a user (specify minutes)", inline=False)
    embed.add_field(name="☕ Cafe & Fun System", value="`/serve` - Serve a cute coffee to a server member\n`/ping` - Check bot's connection latency", inline=False)
    embed.set_footer(text="Crafted with care for the Stardust Cafe Community 🌟")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Test the bot's reaction speed")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency is `{latency}ms` ✨")

# Bot Deployment
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN is missing!")
