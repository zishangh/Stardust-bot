import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import datetime

# Flask Setup (Render ke liye background support)
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
# 🛠️ MODULE 1: HIGH-LEVEL MODERATION COMMANDS (Cute style)
# =========================================================

# 1. KICK COMMAND
@bot.tree.command(name="kick", description="🔒 Kisi member ko server se kick karein")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="🔨 Member Kicked!",
            description=f"**{member.name}** ko server se nikal diya gaya hai.",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text="Stardust Security System ✨")
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Mere paas is user ko kick karne ki permission nahi hai!", ephemeral=True)

# 2. BAN COMMAND
@bot.tree.command(name="ban", description="🚫 Kisi member ko server se permanently ban karein")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🚨 Member Banned!",
            description=f"**{member.name}** ko hamesha ke liye ban kar diya gaya hai.",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message("❌ Galti hui! Check karein ki meri role sabse upar hai ya nahi.", ephemeral=True)

# 3. MUTE / TIMEOUT COMMAND
@bot.tree.command(name="mute", description="🤫 Kisi member ko kuch samay ke liye mute (timeout) karein")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🤫 Member Muted!",
            description=f"**{member.mention}** ko `{minutes}` minutes ke liye shant kara diya gaya hai.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Mute nahi kar paya: {e}", ephemeral=True)

# =========================================================
# 🍧 MODULE 2: CUTE & UNIQUE CAFE FEATURES
# =========================================================

@bot.tree.command(name="serve", description="☕ Apne kisi dost ko ek pyari si coffee bhein")
async def serve(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="✨ Stardust Cafe Special Order! ✨",
        description=f"{interaction.user.mention} ne {member.mention} ko ek garm-a-garm, pyari si **Stardust Special Coffee** serve ki hai! ☕🍰",
        color=discord.Color.from_rgb(245, 222, 179) # Cafe theme color
    )
    embed.set_image(url="https://i.imgur.com/🎵 placeholder link agar aage GIF lagani ho toh") # Hum aage gifs bhi add kar sakte hain!
    embed.set_footer(text="Have a cozy day at Stardust Cafe! 💕")
    await interaction.response.send_message(embed=embed)

# =========================================================
# 📜 MODULE 3: TOP LEVEL HELP & INFO MENU
# =========================================================

@bot.tree.command(name="help", description="📖 Stardust Bot ke saare advanced commands dekhein")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ Stardust Cafe Bot - Premium Menu ✨",
        description="Dyno se bhi zyadah cute aur professional! Niche mere commands diye gaye hain:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🛡️ Moderation Commands", value="`/kick` - Member nikalne ke liye\n`/ban` - Permanent ban ke liye\n`/mute` - Timeout dene ke liye (Minutes daal kar)", inline=False)
    embed.add_field(name="☕ Cafe & Fun Commands", value="`/serve` - Kisi dost ko unique style mein coffee bhej kar khush karne ke liye\n`/ping` - Bot ki latency dekhne ke liye", inline=False)
    embed.set_footer(text="Stardust Cafe Community ke liye kadi mehnat se banaya gaya hai 🌟")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Bot ki speed test karein")
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
