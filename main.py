import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import json

# Flask Setup for Render Deployment
app = Flask('')

@app.route('/')
def home():
    return "Stardust Enterprise Bot is running perfectly at maximum capacity!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Data Persistence / Database Setup (JSON Files)
DATA_FILE = "server_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initializing Bot with Premium Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Enterprise Level: Successfully synced {len(synced)} high-end slash command(s) globally!")
    except Exception as e:
        print(f"Sync Error: {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="Stardust Global Network 🌐"))

# =========================================================
# ⚙️ SYSTEM 1: AUTOMATIC ADVANCED GREETING SYSTEM
# =========================================================

# 1. SET WELCOME CHANNEL COMMAND
@bot.tree.command(name="set-welcome", description="⚙️ Configure the premium welcome channel for this server")
@app_commands.checks.has_permissions(administrator=True)
async def set_welcome(interaction: discord.Interaction, channel: discord.TextChannel):
    data = load_data()
    guild_id = str(interaction.guild.id)
    
    if guild_id not in data:
        data[guild_id] = {}
        
    data[guild_id]["welcome_channel"] = channel.id
    save_data(data)
    
    embed = discord.Embed(
        title="⚙️ Configuration Updated",
        description=f"Premium Welcome module has been successfully mapped to {channel.mention}.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Stardust Administration Panel 🖥️")
    await interaction.response.send_message(embed=embed)

# 2. AUTOMATIC WELCOME EVENT (Premium Card Layout)
@bot.event
async def on_member_join(member: discord.Member):
    data = load_data()
    guild_id = str(member.guild.id)
    
    if guild_id in data and "welcome_channel" in data[guild_id]:
        channel_id = data[guild_id]["welcome_channel"]
        channel = member.guild.get_channel(channel_id)
        
        if channel:
            member_count = member.guild.member_count
            
            # Ultra-clean premium embedded card layout like top bots
            embed = discord.Embed(
                title="✨ WELCOME TO THE COMMUNITY ✨",
                description=f"Welcome {member.mention} to **{member.guild.name}**!\nWe are absolutely thrilled to have you here with us.",
                color=discord.Color.from_rgb(255, 192, 203) # Premium aesthetic pink
            )
            embed.add_field(name="User Identity", value=f"👤 **Tag:** {member.name}\n🆔 **ID:** {member.id}", inline=True)
            embed.add_field(name="Server Scale", value=f"📈 **Member Count:** {member_count}th member", inline=True)
            
            # Premium abstract layout header image banner
            embed.set_image(url="https://i.imgur.com/uNbe7w2.png")
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Account Created: {member.created_at.strftime('%Y-%m-%d')}")
            
            # Outside ping for guaranteed blue notification highlights
            await channel.send(content=f"👋 Welcome {member.mention}!", embed=embed)

# 3. AUTOMATIC LEAVE EVENT
@bot.event
async def on_member_remove(member: discord.Member):
    data = load_data()
    guild_id = str(member.guild.id)
    
    if guild_id in data and "welcome_channel" in data[guild_id]:
        channel_id = data[guild_id]["welcome_channel"]
        channel = member.guild.get_channel(channel_id)
        
        if channel:
            embed = discord.Embed(
                description=f"💔 **{member.name}** has left the server. Current total count: {member.guild.member_count} members.",
                color=discord.Color.dark_gray()
            )
            await channel.send(embed=embed)

# =========================================================
# 🍧 MODULE 2: NEKOBOT STYLE ANIME FEATURES
# =========================================================

@bot.tree.command(name="serve", description="☕ Serve a fresh coffee to a friend in a cute cafe style")
async def serve(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="✨ Stardust Cafe Special Order! ✨",
        description=f"**A fresh, warm coffee has been freshly brewed and served!** ☕🍰",
        color=discord.Color.from_rgb(245, 222, 179)
    )
    embed.set_image(url="https://media.tenor.com/7S8Y-Xshg3YAAAAC/anime-coffee.gif")
    embed.set_footer(text="Have a cozy day at Stardust Cafe! 💕")
    await interaction.response.send_message(content=f"☕ {interaction.user.mention} serves a delicious coffee to {member.mention}!", embed=embed)

@bot.tree.command(name="hug", description="🫂 Give a warm, cozy anime hug to someone")
async def hug(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="✨ A Warm Stardust Hug! ✨",
        description=f"**Sending cute, cozy and wholesome vibes across the server!** 💖",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    embed.set_image(url="https://media.tenor.com/v8t_P6K3L48AAAAC/anime-hug.gif")
    embed.set_footer(text="Shared with love in Stardust Cafe! ✨")
    await interaction.response.send_message(content=f"🫂 {interaction.user.mention} wraps their arms tightly around {member.mention}!", embed=embed)

# =========================================================
# 🛡️ MODULE 3: HIGH-LEVEL MODERATION COMMANDS
# =========================================================

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
        await interaction.response.send_message(content=member.mention, embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Error: Permission Hierarchy Failed.", ephemeral=True)

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
        await interaction.response.send_message(content=member.mention, embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Error: Hierarchy issue.", ephemeral=True)

@bot.tree.command(name="mute", description="🤫 Timeout a member for a specific duration")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🤫 Member Muted",
            description=f"**{member.name}** has been placed in timeout for `{minutes}` minutes.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(content=member.mention, embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# =========================================================
# 📜 MODULE 4: TOP LEVEL HELP & INFO MENU
# =========================================================

@bot.tree.command(name="help", description="📖 View all available commands for Stardust Bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ Stardust Enterprise Bot - Premium Menu ✨",
        description="Welcome to the high-level custom service network. Here are the active modules:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="⚙️ Admin/Systems Setup", value="`/set-welcome` - Configure greeting updates", inline=False)
    embed.add_field(name="🛡️ Moderation System", value="`/kick` - Kick users\n`/ban` - Ban users\n`/mute` - Timeout configurations", inline=False)
    embed.add_field(name="☕ Cafe & Fun System", value="`/serve` - Interactive coffee system\n`/hug` - Wholesome interaction tool\n`/ping` - Speed analyzer", inline=False)
    embed.set_footer(text="Stardust Premium Core Engine 🌟")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Test the bot's reaction speed")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency is `{latency}ms` ✨")

# Bot Deployment Integration
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN is missing!")
