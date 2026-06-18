import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import json
import random

# =========================================================
# ⚙️ INFRASTRUCTURE LAYER (KEEP ALIVE & DB)
# =========================================================
app = Flask('')

@app.route('/')
def home():
    return "Stardust Premium Engine Operational."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

DATA_FILE = "server_configurations.json"

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================================
# 🤖 BOT INITIALIZATION
# =========================================================
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
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync Error: {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="Stardust Global Network 🌐"))

# =========================================================
# 🛠️ SYSTEM 1: DYNO-STYLE CLEAN WELCOME SYSTEM
# =========================================================

@bot.tree.command(name="welcome-set", description="⚙️ Map the greeting system to a text channel")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_set(interaction: discord.Interaction, channel: discord.TextChannel):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db:
        db[g_id] = {}
    db[g_id]["channel"] = channel.id
    save_db(db)
    
    embed = discord.Embed(description=f"Configuration Saved (⁠•⁠‿⁠•⁠) Mapped to {channel.mention}.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="welcome-reset", description="❌ Wipe welcome module settings")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_reset(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "channel" in db[g_id]:
        del db[g_id]["channel"]
        save_db(db)
        embed = discord.Embed(description="Welcome configuration cleared (⁠◔⁠‿⁠◔⁠)", color=discord.Color.red())
    else:
        embed = discord.Embed(description="Welcome configuration not active ʘ⁠‿⁠ʘ", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)
# =========================================================
# 💰 PREMIUM ECONOMY SLASH COMMANDS
# =========================================================

@bot.tree.command(name="reward-set", description="💰 Configure the reward/paycheck destination channel")
@app_commands.checks.has_permissions(administrator=True)
async def reward_set(interaction: discord.Interaction, channel: discord.TextChannel):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db:
        db[g_id] = {}
    db[g_id]["reward_channel"] = channel.id
    save_db(db)
    
    embed = discord.Embed(description=f"✨ **Premium Reward Engine Active!** Mapped to {channel.mention}.", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reward-reset", description="❌ Wipe reward module settings")
@app_commands.checks.has_permissions(administrator=True)
async def reward_reset(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "reward_channel" in db[g_id]:
        del db[g_id]["reward_channel"]
        save_db(db)
        embed = discord.Embed(description="Reward system deactivated successfully (⁠•⁠‿⁠•⁠)", color=discord.Color.red())
    else:
        embed = discord.Embed(description="Reward engine wasn't active on this server.", color=discord.Color.orange())
@bot.tree.command(name="reward-test", description="🧪 Trigger a simulated custom economy reward card event")
@app_commands.checks.has_permissions(administrator=True)
async def reward_test(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "reward_channel" in db[g_id]:
        reward_channel = interaction.guild.get_channel(db[g_id]["reward_channel"])
        if reward_channel:
            amount = random.randint(5000, 75000)
            embed = discord.Embed(title="✨ lucky (TEST)", color=discord.Color.from_rgb(241, 196, 15))
            embed.description = (
                f"{interaction.user.mention}\n\n"
                f"**+${amount:,}**\n\n"
                f"*chat wage* ·  *lvl {random.randint(10, 45)}*\n\n"
                f"*the right beat in the right second.*"
            )
            await reward_channel.send(embed=embed)
            await interaction.response.send_message("Test reward embed triggered in reward channel.", ephemeral=True)
            return
    await interaction.response.send_message("Reward channel not configured ʘ⁠‿⁠ʘ Run `/reward-set` first.", ephemeral=True)
        
# CLEAN DYNO STYLE ENGINE
def generate_welcome_card(member):
    dyno_description = (
        "╭🎈━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "   ⭐  *𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝑺𝒕𝒂𝒓𝒅𝒖𝒔𝒕 𝑪𝒂𝒇𝒆!* ⭐\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━🎈╯\n\n"
        "𝖧𝖾𝗒 {mention}! (⁠◠⁠‿⁠◕⁠)\n\n"
        "*𝑾𝒆 𝒂𝒓𝒆 𝒔𝒐 𝒉𝒂𝒑𝒑𝒚 𝒕𝒐 𝒉𝒂𝒗𝒆 𝒚𝒐𝒖 𝒉𝒆𝒓𝒆!* (⁠≧⁠▽⁠≦⁠)\n"
        "*𝑮𝒓𝒂𝒃 𝒂 𝒄𝒖𝒑 𝒐𝒇 𝒄𝒐𝒇𝒇𝒆𝒆, 𝒄𝒉𝒊𝒍𝒍, 𝒂𝒏𝒅 𝒎𝒂𝒌𝒆 𝒏𝒆𝒘 𝒇𝒓𝒊𝒆𝒏𝒅𝒔!* (⁠✯⁠ᴗ⁠✯⁠)\n\n"
        "📌 𝖣𝗈𝗇't 𝖿𝗈𝗋𝗀𝖾𝗍 𝗍𝗈 𝖼𝗁𝖾𝖼𝗄𝗑 𝗈𝗎𝗋 𝗋𝗎𝓵𝒆𝒔! (⁠◍⁠•⁠ᴗ⁠•⁠◍)\n\n"
        "**Identity:** {name} | **Member Count:** #{count}"
    ).format(mention=member.mention, name=member.name, count=member.guild.member_count)

    embed = discord.Embed(
        description=dyno_description,
        color=discord.Color.from_rgb(47, 49, 54)
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1515969029708320778/1516977720138006632/CofeeManga__A_Popular_Platform_for_Manga_Enthusiasts.jpg?ex=6a349b18&is=6a334998&hm=9838ef43a2c5fc09352e6e954d910dd34aa675081c107d3e90ccf28594687cd9&")
    return embed

@bot.tree.command(name="welcome-test", description="🧪 Trigger a simulated custom decorated welcome card event")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_test(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = interaction.guild.get_channel(db[g_id]["channel"])
        if channel:
            card = generate_welcome_card(interaction.user)
            await channel.send(content=f"Welcome {interaction.user.mention}!", embed=card)
            await interaction.response.send_message("Test custom embed triggered.", ephemeral=True)
            return
    await interaction.response.send_message("Welcome channel not configured ʘ⁠‿⁠ʘ Run `/welcome-set` first.", ephemeral=True)

@bot.event
async def on_member_join(member: discord.Member):
    db = load_db()
    g_id = str(member.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = member.guild.get_channel(db[g_id]["channel"])
        if channel:
            card = generate_welcome_card(member)
            await channel.send(content=f"Welcome {member.mention}!", embed=card)

@bot.event
async def on_member_remove(member: discord.Member):
    db = load_db()
    g_id = str(member.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = member.guild.get_channel(db[g_id]["channel"])
        if channel:
            embed = discord.Embed(description=f"💔 **{member.name}** left the server. Total scale: {member.guild.member_count} members.", color=discord.Color.dark_gray())
            await channel.send(embed=embed)

# =========================================================
# 🍧 MODULE 2: FUN INTERACTIONS (GIF ENDPOINT FIXED)
# =========================================================

@bot.tree.command(name="serve", description="☕ Serve a fresh brewed cafe drink to a server member")
async def serve(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="Stardust Cafe Order! (⁠ ⁠╹⁠▽⁠╹⁠ ⁠)", description=f"**A warm, fresh coffee has been served to {member.mention}!** ☕", color=discord.Color.from_rgb(245, 222, 179))
    embed.set_image(url="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3h0Y3h4ZzZ0bWp3NW4xeWxtdDJvN2d5dGtsamFlZ3R0ZzZmdDZzMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1498bN8wK8zT0c/giphy.gif")
    embed.set_footer(text="Have a cozy day! (⁠◍⁠•⁠ᴗ⁠•⁠◍⁠)")
    await interaction.response.send_message(content=f"☕ {interaction.user.mention} serves coffee to {member.mention}!", embed=embed)

@bot.tree.command(name="hug", description="🫂 Give a warm, cozy anime hug to someone")
async def hug(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="Stardust Hug! (⁠≧⁠▽⁠≦⁠)", description=f"**Wholesome cozy vibes are traveling across channels!** 💖", color=discord.Color.from_rgb(255, 182, 193))
    embed.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDJ0Y2c1amwzdWlhM3gxeGNidmxtMWd5dWQzYjU5dGtwcnF0OTY0bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lrr9rHuoJOE0w/giphy.gif")
    embed.set_footer(text="Shared with love! (⁠•⁠‿⁠•⁠)")
    await interaction.response.send_message(content=f"🫂 {interaction.user.mention} wraps their arms tightly around {member.mention}!", embed=embed)

# =========================================================
# 🛡️ MODULE 3: MODERATION SUITE (FIXED BAN TYPO)
# =========================================================

@bot.tree.command(name="kick", description="🔒 Remove a user from the guild")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="🔨 Member Kicked", description=f"**{member.name}** removed safely ◉⁠‿⁠◉", color=discord.Color.red())
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Hierarchy error.", ephemeral=True)

@bot.tree.command(name="ban", description="🚫 Blacklist and permanently ban a member")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="🚨 Member Banned", description=f"**{member.name}** data purged ʘ⁠‿⁠ʘ", color=discord.Color.dark_red())
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Permission failed.", ephemeral=True)

@bot.tree.command(name="mute", description="🤫 Timeout a member for a specific duration")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(title="🤫 Member Muted", description=f"**{member.name}** muted for `{minutes}` minutes (⁠◔⁠‿⁠◔⁠)", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Execution invalid.", ephemeral=True)

# =========================================================
# 📜 MODULE 4: UTILITY CONTROL CENTER
# =========================================================

@bot.tree.command(name="help", description="📖 View all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Stardust Control Suite (⁠•⁠‿⁠•⁠)", description="Premium active modules:", color=discord.Color.blurple())
    embed.add_field(name="⚙️ Welcome Setup", value="`/welcome-set` | `/welcome-test` | `/welcome-reset`", inline=False)
    embed.add_field(name="🛡️ Moderation", value="`/kick` | `/ban` | `/mute`", inline=False)
    embed.add_field(name="☕ Cafe Features", value="`/serve` | `/hug` | `/ping`", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Performance speed delay check")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! Speed: `{round(bot.latency * 1000)}ms` (⁠◠⁠‿⁠◕⁠)")

# Deploy System Launch Configuration
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: Running operation token string empty.")
