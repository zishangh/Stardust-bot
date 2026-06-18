import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import json

# =========================================================
# ⚙️ INFRASTRUCTURE LAYER (KEEP ALIVE & DB)
# =========================================================
app = Flask('')

@app.route('/')
def home():
    return "Stardust Premium Engine Core Operational."

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
        print(f"Operational Success: Synced {len(synced)} high-end slash commands.")
    except Exception as e:
        print(f"Sync Failure: {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="Stardust Global Network 🌐"))

# =========================================================
# 🛠️ SYSTEM 1: PREMIUM WELCOME & MANAGEMENT SUITE
# =========================================================

# 1. SETUP CHANNEL
@bot.tree.command(name="welcome-set", description="⚙️ Map the premium automated greeting system to a text channel")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_set(interaction: discord.Interaction, channel: discord.TextChannel):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db:
        db[g_id] = {}
    db[g_id]["channel"] = channel.id
    if "msg" not in db[g_id]:
        db[g_id]["msg"] = "Welcome to the community! We are absolutely thrilled to have you here with us."
    save_db(db)
    
    embed = discord.Embed(title="⚙️ Configuration Saved", description=f"Premium Welcome system mapped to {channel.mention}.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

# 2. CUSTOMIZE MESSAGE
@bot.tree.command(name="welcome-msg", description="✍️ Customize the embedded card text message description")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_msg(interaction: discord.Interaction, text: str):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db:
        db[g_id] = {}
    db[g_id]["msg"] = text
    save_db(db)
    
    embed = discord.Embed(title="⚙️ Message Updated", description=f"Card display message has been set to:\n`{text}`", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

# 3. RESET MODULE
@bot.tree.command(name="welcome-reset", description="❌ Wipe welcome module settings and disable alerts")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_reset(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "channel" in db[g_id]:
        del db[g_id]["channel"]
        save_db(db)
        embed = discord.Embed(description="🗑️ Welcome configuration cleared successfully.", color=discord.Color.red())
    else:
        embed = discord.Embed(description="❌ Welcome configuration not active on this server.", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

# Helper function to generate premium welcome embed card layout
def generate_welcome_card(member, custom_msg):
    embed = discord.Embed(
        title="✨ WELCOME TO THE COMMUNITY ✨",
        description=f"Welcome {member.mention} to **{member.guild.name}**!\n\n{custom_msg}",
        color=discord.Color.from_rgb(255, 192, 203)
    )
    embed.add_field(name="User Identity", value=f"👤 **Tag:** {member.name}\n🆔 **ID:** {member.id}", inline=True)
    embed.add_field(name="Server Scale", value=f"📈 **Member Count:** {member.guild.member_count}th member", inline=True)
    embed.set_image(url="https://images.squarespace-cdn.com/content/v1/5c1a84f39f8770b02996d925/1547000216694-O5OHZZN22MZZIKREB2B8/banner-abstract.png")
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Account Created: {member.created_at.strftime('%Y-%m-%d')}")
    return embed

# 4. TEST SYSTEM INSTANTLY
@bot.tree.command(name="welcome-test", description="🧪 Trigger a simulated welcome embed card event to test settings")
@app_commands.checks.has_permissions(administrator=True)
async def welcome_test(interaction: discord.Interaction):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = interaction.guild.get_channel(db[g_id]["channel"])
        if channel:
            custom_msg = db[g_id].get("msg", "Welcome to the community!")
            card = generate_welcome_card(interaction.user, custom_msg)
            await channel.send(content=f"👋 Test Simulation: {interaction.user.mention}!", embed=card)
            await interaction.response.send_message("✅ Test embed triggered in configured welcome channel.", ephemeral=True)
            return
    await interaction.response.send_message("❌ Welcome channel not configured. Run `/welcome-set` first.", ephemeral=True)

# 5. ACTUAL AUTOMATIC EVENTS
@bot.event
async def on_member_join(member: discord.Member):
    db = load_db()
    g_id = str(member.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = member.guild.get_channel(db[g_id]["channel"])
        if channel:
            custom_msg = db[g_id].get("msg", "Welcome to the community!")
            card = generate_welcome_card(member, custom_msg)
            await channel.send(content=f"👋 Welcome {member.mention}!", embed=card)

@bot.event
async def on_member_remove(member: discord.Member):
    db = load_db()
    g_id = str(member.guild.id)
    if g_id in db and "channel" in db[g_id]:
        channel = member.guild.get_channel(db[g_id]["channel"])
        if channel:
            embed = discord.Embed(description=f"💔 **{member.name}** has left the server. Member count drop: {member.guild.member_count} members.", color=discord.Color.dark_gray())
            await channel.send(embed=embed)

# =========================================================
# 🍧 MODULE 2: RE-OPTIMIZED HIGH QUALITY FUN INTERACTIONS
# =========================================================

@bot.tree.command(name="serve", description="☕ Serve a fresh brewed cafe drink to a server member")
async def serve(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="✨ Stardust Cafe Special Order! ✨", description="**A fresh, hot coffee has been prepared and served at your table!** ☕🍰", color=discord.Color.from_rgb(245, 222, 179))
    embed.set_image(url="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3h0Y3h4ZzZ0bWp3NW4xeWxtdDJvN2d5dGtsamFlZ3R0ZzZmdDZzMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1498bN8wK8zT0c/giphy.gif")
    embed.set_footer(text="Have a cozy day at Stardust Cafe! 💕")
    await interaction.response.send_message(content=f"☕ {interaction.user.mention} serves a delicious coffee to {member.mention}!", embed=embed)

@bot.tree.command(name="hug", description="🫂 Wrap your arms tightly around someone to deliver cozy vibes")
async def hug(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="✨ A Wholesome Stardust Hug! ✨", description="**The room feels warmer already! Wholesome vibes are traveling across channels!** 💖", color=discord.Color.from_rgb(255, 182, 193))
    embed.set_image(url="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDJ0Y2c1amwzdWlhM3gxeGNidmxtMWd5dWQzYjU5dGtwcnF0OTY0bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lrr9rHuoJOE0w/giphy.gif")
    embed.set_footer(text="Shared with love in Stardust Cafe! ✨")
    await interaction.response.send_message(content=f"🫂 {interaction.user.mention} wraps their arms tightly around {member.mention}!", embed=embed)

# =========================================================
# 🛡️ MODULE 3: MODERATION SUITE
# =========================================================

@bot.tree.command(name="kick", description="🔒 Remove a user from the guild perimeter")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="🔨 Member Kicked", description=f"**{member.name}** removed safely.", color=discord.Color.red())
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Administration structural error.", ephemeral=True)

@bot.tree.command(name="ban", description="🚫 Blacklist and permanently terminate a profile from the server")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="🚨 Member Banned", description=f"**{member.name}** data purged.", color=discord.Color.dark_red())
        embed.add_field(name="Reason", value=reason)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Permissions check hierarchy failed.", ephemeral=True)

@bot.tree.command(name="mute", description="🤫 Enforce a quiet protocol status profile restriction")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(title="🤫 Timeout Instantiated", description=f"**{member.name}** muted for `{minutes}` minutes.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Command execution invalid profile state.", ephemeral=True)

# =========================================================
# 📜 MODULE 4: UTILITY CONTROL CENTER
# =========================================================

@bot.tree.command(name="help", description="📖 View the standard network operating documentation commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="✨ Stardust Enterprise Control Suite ✨", description="Operating standard premium production protocols:", color=discord.Color.blurple())
    embed.add_field(name="⚙️ Management Suite", value="`/welcome-set` - Map welcome alert\n`/welcome-msg` - Custom greeting content\n`/welcome-test` - Trigger test module layout\n`/welcome-reset` - Reset welcome database entries", inline=False)
    embed.add_field(name="🛡️ Moderation Operations", value="`/kick` - Evict profile\n`/ban` - Terminate profile permission access\n`/mute` - Restrict text capability status", inline=False)
    embed.add_field(name="☕ Cafe Infrastructure", value="`/serve` - Interactive drink delivery\n`/hug` - Animation connection module\n`/ping` - System execution speed delay check", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Performance speed analytics report")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! Core Latency Response speed: `{round(bot.latency * 1000)}ms` ✨")

# Deploy System Launch Configuration
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: Running operation token string empty.")
