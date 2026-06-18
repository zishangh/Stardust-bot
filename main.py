import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime
import json
import random
import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

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
            # content= karke humne embed ke upar real ping attach kar diya hai
            await reward_channel.send(content=interaction.user.mention, embed=embed)
            await interaction.response.send_message("Test reward embed triggered in reward channel.", ephemeral=True)
            return
    await interaction.response.send_message("Reward channel not configured ʘ⁠‿⁠ʘ Run `/reward-set` first.", ephemeral=True)
# =========================================================
# 📊 PREMIUM LEVEL, XP & RANK SYSTEM
# =========================================================

@bot.tree.command(name="level-set-channel", description="📊 Set the channel where level up cards will be announced")
@app_commands.checks.has_permissions(administrator=True)
async def level_set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db: db[g_id] = {}
    db[g_id]["level_channel"] = channel.id
    save_db(db)
    await interaction.response.send_message(f"✨ Level up alerts will now be sent in {channel.mention}!", ephemeral=True)

@bot.tree.command(name="level-set-msg", description="💬 Customize the text message sent along with the level up card")
@app_commands.checks.has_permissions(administrator=True)
async def level_set_msg(interaction: discord.Interaction, message: str):
    db = load_db()
    g_id = str(interaction.guild.id)
    if g_id not in db: db[g_id] = {}
    db[g_id]["level_msg"] = message
    save_db(db)
    await interaction.response.send_message(f"✅ Level up message updated to:\n`{message}`", ephemeral=True)

@bot.tree.command(name="rank", description="💳 Display your premium elegant beige rank card & performance stats")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()
    target = member or interaction.user
    db = load_db()
    g_id = str(interaction.guild.id)
    u_id = str(target.id)
    
    user_data = db.get(g_id, {}).get("users", {}).get(u_id, {"xp": 0, "level": 1, "balance": 0, "messages": 0})
    xp = user_data.get("xp", 0)
    lvl = user_data.get("level", 1)
    bal = user_data.get("balance", 0)
    msg_count = user_data.get("messages", int(xp / 20) + 1)
    next_xp = lvl * 375
    
    # 🏅 Performance Level Tier Calculator
    if lvl >= 50: tier = "Grandmaster ✨"
    elif lvl >= 25: tier = "Elite Vibe 💫"
    elif lvl >= 10: tier = "Gold Member 🌟"
    else: tier = "Rising Star 🌱"

    server_users = db.get(g_id, {}).get("users", {})
    sorted_users = sorted(server_users.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    rank_pos = 1
    for index, (uid, data) in enumerate(sorted_users):
        if uid == u_id:
            rank_pos = index + 1
            break

    # 🎨 TIKO STYLE HD BIG IMAGE GENERATOR (950x420 pixels for server text space)
    W, H = 950, 420
    card = Image.new("RGBA", (W, H), (245, 238, 227, 255)) # Soft Luxury Badami Background
    draw = ImageDraw.Draw(card)
    
    # Cute Frosted Outer Border Frame
    draw.rounded_rectangle([20, 20, W-20, H-20], radius=30, fill=(255, 254, 252, 130), outline=(185, 170, 150, 255), width=3)
    
    # Progress Bar Track (Pearl Muted Dark Beige)
    bar_x1, bar_y1, bar_x2, bar_y2 = 320, 310, 900, 335
    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=12, fill=(215, 205, 192, 255))
    
    # Rich Chocolate Solid Progress Fill
    progress = min(xp / next_xp, 1.0) if next_xp > 0 else 1.0
    if progress > 0:
        fill_x2 = bar_x1 + int((bar_x2 - bar_x1) * progress)
        draw.rounded_rectangle([bar_x1, bar_y1, fill_x2, bar_y2], radius=12, fill=(84, 62, 49, 255))
        
    # User Circular Avatar System (Upper Left Side Alignment)
    pfp_url = target.display_avatar.url
    pfp_res = requests.get(pfp_url)
    pfp_img = Image.open(io.BytesIO(pfp_res.content)).convert("RGBA").resize((210, 210))
    
    mask = Image.new("L", (210, 210), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 210, 210), fill=255)
    
    pfp_circular = ImageOps.fit(pfp_img, (210, 210), centering=(0.5, 0.5))
    card.paste(pfp_circular, (50, 50), mask=mask)
    draw.ellipse((46, 46, 264, 264), outline=(150, 125, 105, 255), width=4) # Antique Ring Border
    
    # ✒️ Serif Style / Elegant Text Alignment (High Contrast Coffee Charcoal)
    draw.text((320, 45), f"@{target.name.lower()} ☕", fill=(54, 43, 38, 255), stroke_width=1)
    draw.text((320, 105), f"Level: {lvl}  •  Server Rank: #{rank_pos} 🏆", fill=(125, 96, 81, 255))
    draw.text((320, 155), f"Performance: {tier}", fill=(138, 105, 93, 255))
    draw.text((320, 205), f"Experience: {xp} / {next_xp} XP 🌱", fill=(80, 72, 66, 255))
    draw.text((320, 255), f"Total Chats Logged: {msg_count:,} messages 💬", fill=(105, 105, 100, 255))
    
    # 🌟 Center Bottom Server Name Alignment
    server_name = f"~ {interaction.guild.name.upper()} ~"
    draw.text((W // 2 - 60, 370), server_name, fill=(160, 145, 130, 255))
    
    fp = io.BytesIO()
    card.save(fp, "PNG")
    fp.seek(0)
    
    file = discord.File(fp, filename="rank_card.png")
    await interaction.followup.send(file=file)
    
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
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    g_id = str(message.guild.id)
    u_id = str(message.author.id)
    db = load_db()
    
    if g_id not in db: db[g_id] = {}
    if "users" not in db[g_id]: db[g_id]["users"] = {}
    if u_id not in db[g_id]["users"]:
        db[g_id]["users"][u_id] = {"xp": 0, "level": 1, "balance": 0, "messages": 0}
        
    user_data = db[g_id]["users"][u_id]
    
    # 📈 Message counter tracker core activation
    user_data["messages"] = user_data.get("messages", 0) + 1
    
    old_lvl = user_data.get("level", 1)
    xp_gain = random.randint(15, 25)
    user_data["xp"] = user_data.get("xp", 0) + xp_gain
    
    next_xp = old_lvl * 375
    if user_data["xp"] >= next_xp:
        user_data["level"] = old_lvl + 1
        user_data["xp"] -= next_xp
        save_db(db)
        
        if "level_channel" in db[g_id]:
            lvl_channel = message.guild.get_channel(db[g_id]["level_channel"])
            if lvl_channel:
                custom_msg = db[g_id].get("level_msg", "GG {member}! You leveled up!").format(member=message.author.mention)
                await lvl_channel.send(f"🏆 {custom_msg} **Level {old_lvl + 1}**!")

    if random.random() < 0.10 and "reward_channel" in db[g_id]:
        reward_channel = message.guild.get_channel(db[g_id]["reward_channel"])
        if reward_channel:
            amount = random.randint(5000, 75000)
            user_data["balance"] = user_data.get("balance", 0) + amount
            
            embed = discord.Embed(title="✨ lucky", color=discord.Color.from_rgb(241, 196, 15))
            embed.description = (
                f"{message.author.mention}\n\n"
                f"**+${amount:,}**\n\n"
                f"*chat wage* ·  *lvl {user_data['level']}*\n\n"
                f"*keeping the vibe alive and thriving.*"
            )
            await reward_channel.send(content=message.author.mention, embed=embed)

    save_db(db)
    await bot.process_commands(message)
    
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
