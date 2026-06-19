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
    
    if lvl >= 50: tier = "Grandmaster"
    elif lvl >= 25: tier = "Elite Vibe"
    elif lvl >= 10: tier = "Gold Member"
    else: tier = "Rising Star"

    server_users = db.get(g_id, {}).get("users", {})
    sorted_users = sorted(server_users.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    rank_pos = 1
    for index, (uid, data) in enumerate(sorted_users):
        if uid == u_id:
            rank_pos = index + 1
            break

    W, H = 950, 420
    card = Image.new("RGBA", (W, H), (245, 238, 227, 255)) 
    draw = ImageDraw.Draw(card)
    
    # Outer Border Frame
    draw.rounded_rectangle([20, 20, W-20, H-20], radius=30, fill=(255, 254, 252, 130), outline=(185, 170, 150, 255), width=3)
    
    # Progress Bar Track
    bar_x1, bar_y1, bar_x2, bar_y2 = 320, 310, 900, 335
    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=12, fill=(215, 205, 192, 255))
    
    progress = min(xp / next_xp, 1.0) if next_xp > 0 else 1.0
    if progress > 0:
        fill_x2 = bar_x1 + int((bar_x2 - bar_x1) * progress)
        draw.rounded_rectangle([bar_x1, bar_y1, fill_x2, bar_y2], radius=12, fill=(84, 62, 49, 255))
        
    pfp_url = target.display_avatar.url
    pfp_res = requests.get(pfp_url)
    pfp_img = Image.open(io.BytesIO(pfp_res.content)).convert("RGBA").resize((210, 210))
    
    mask = Image.new("L", (210, 210), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 210, 210), fill=255)
    
    pfp_circular = ImageOps.fit(pfp_img, (210, 210), centering=(0.5, 0.5))
    card.paste(pfp_circular, (50, 50), mask=mask)
    draw.ellipse((46, 46, 264, 264), outline=(150, 125, 105, 255), width=4)
    
    # ✒️ Load Professional Bold Serif System Font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "DejaVuSerif-Bold.ttf"
    ]
    
    title_font = None
    body_font = None
    
    for path in font_paths:
        try:
            title_font = ImageFont.truetype(path, 36)
            body_font = ImageFont.truetype(path, 26)
            break
        except Exception:
            continue
            
    # Fallback to default enlarged size if system path fails
    if not title_font:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Premium Dark Coffee Charcoal Color
    text_color = (44, 34, 30, 255)
    sub_color = (74, 58, 50, 255)
    
    # Text Placement with Clean Sizes
    draw.text((320, 45), f"@{target.name.lower()}", fill=text_color, font=title_font)
    draw.text((320, 110), f"Level: {lvl}  •  Server Rank: #{rank_pos}", fill=sub_color, font=body_font)
    draw.text((320, 160), f"Performance: {tier}", fill=sub_color, font=body_font)
    draw.text((320, 210), f"Experience: {xp} / {next_xp} XP", fill=sub_color, font=body_font)
    draw.text((320, 260), f"Total Chats Logged: {msg_count:,} messages", fill=sub_color, font=body_font)
    
    server_name = f"~ {interaction.guild.name.upper()} ~"
    draw.text((W // 2 - 110, 370), server_name, fill=(115, 95, 80, 255), font=body_font)
    
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
        new_lvl = old_lvl + 1
        user_data["level"] = new_lvl
        user_data["xp"] -= next_xp
        save_db(db)
        
        if "level_channel" in db[g_id]:
            lvl_channel = message.guild.get_channel(db[g_id]["level_channel"])
            if lvl_channel:
                # 🎨 TIKO STYLE AUTOMATIC LEVEL UP HD POSTER (950x320)
                W, H = 950, 320
                lvl_card = Image.new("RGBA", (W, H), (245, 238, 227, 255)) 
                l_draw = ImageDraw.Draw(lvl_card)
                
                # Frosted Outer Frame
                l_draw.rounded_rectangle([20, 20, W-20, H-20], radius=25, fill=(255, 254, 252, 130), outline=(150, 125, 105, 255), width=3)
                
                # Fetch User Circular Avatar for Level Poster
                try:
                    pfp_url = message.author.display_avatar.url
                    pfp_res = requests.get(pfp_url)
                    pfp_img = Image.open(io.BytesIO(pfp_res.content)).convert("RGBA").resize((180, 180))
                    
                    mask = Image.new("L", (180, 180), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0, 180, 180), fill=255)
                    
                    pfp_circular = ImageOps.fit(pfp_img, (180, 180), centering=(0.5, 0.5))
                    lvl_card.paste(pfp_circular, (50, 70), mask=mask)
                    l_draw.ellipse((46, 66, 234, 254), outline=(138, 105, 93, 255), width=4)
                except Exception:
                    pass
                
                # ✒️ Load Professional Bold Serif System Font
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                    "DejaVuSerif-Bold.ttf"
                ]
                
                title_font = None
                body_font = None
                
                for path in font_paths:
                    try:
                        title_font = ImageFont.truetype(path, 38)
                        body_font = ImageFont.truetype(path, 26)
                        break
                    except Exception:
                        continue
                        
                if not title_font:
                    title_font = ImageFont.load_default()
                    body_font = ImageFont.load_default()

                # Premium High Contrast Solid Colors (No boxes, no distortion)
                text_color = (44, 34, 30, 255)
                sub_color = (74, 58, 50, 255)
                
                # Serif Straight Typography
                l_draw.text((270, 65), "LEVEL UP!", fill=text_color, font=title_font)
                l_draw.text((270, 130), f"@{message.author.name.lower()} has reached", fill=sub_color, font=body_font)
                l_draw.text((270, 185), f"LEVEL {new_lvl}", fill=text_color, font=title_font)
                
                s_name = f"~ {message.guild.name.upper()} ~"
                l_draw.text((W // 2 - 110, 270), s_name, fill=(115, 95, 80, 255), font=body_font)
                
                fp = io.BytesIO()
                lvl_card.save(fp, "PNG")
                fp.seek(0)
                file = discord.File(fp, filename="levelup.png")
                
                custom_msg = db[g_id].get("level_msg", "GG {member}!").format(member=message.author.mention)
                await lvl_channel.send(content=custom_msg, file=file)

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
    
# ====================================================================
# ☕ MODULE 2: FUN INTERACTIONS (PREMIUM GIF SERVING ENGINE)
# ====================================================================

@bot.tree.command(name="serve", description="🛎️ Serve a premium global meal to a highly distinguished member")
@discord.app_commands.describe(
    item="Choose the premium safe item to serve",
    member="The customer who will receive this delicious treat"
)
@discord.app_commands.choices(item=[
    # Original Base Menu
    discord.app_commands.Choice(name="☕ Barista Coffee", value="coffee"),
    discord.app_commands.Choice(name="🍕 Woodfired Pizza", value="pizza"),
    discord.app_commands.Choice(name="🍔 Gourmet Burger", value="burger"),
    discord.app_commands.Choice(name="🥤 Chilled Drink", value="cold_drink"),
    discord.app_commands.Choice(name="🍛 Royal Indian Curry", value="indian_spicy"),
    discord.app_commands.Choice(name="🍩 Glazed Donuts", value="donuts"),
    # International Choices
    discord.app_commands.Choice(name="🍡 Japan: Sweet Matcha Mochi", value="japan_mochi"),
    discord.app_commands.Choice(name="🌮 Mexico: Cheesy Veg Quesadilla", value="mexico_quesadilla"),
    discord.app_commands.Choice(name="🥐 France: Butter Croissant & Cafe", value="france_croissant"),
    discord.app_commands.Choice(name="🍝 Italy: Creamy Alfredo Pasta", value="italy_pasta"),
    discord.app_commands.Choice(name="🥟 China: Steamed Veg Dim Sum Box", value="china_dimsum"),
    discord.app_commands.Choice(name="🥮 Turkey: Royal Pistachio Baklava", value="turkey_baklava"),
    discord.app_commands.Choice(name="🍢 South Korea: Cheesy Rice Cakes (Tteokbokki)", value="korea_tteokbokki"),
    discord.app_commands.Choice(name="🥭 Thailand: Mango Sticky Rice Dessert", value="thailand_mangorice"),
    discord.app_commands.Choice(name="🥖 Spain: Crispy Sweet Churros Box", value="spain_churros"),
    discord.app_commands.Choice(name="🧇 USA: Loaded Premium Waffles", value="usa_waffles")
])
async def serve(interaction: discord.Interaction, item: str, member: discord.Member):
    await interaction.response.defer()
    
    menu_data = {
        "coffee": {"title": "BARISTA ESPRESSO", "item_name": "Premium Barista Coffee", "origin": "Milan, Italy 🇮🇹", "line": "A rich, dark aromatic espresso topped with perfect velvety crema."},
        "donuts": {"title": "GLAZED LUXURY", "item_name": "Gourmet Glazed Donuts", "origin": "Belgium 🇧🇪", "line": "Fluffy, artisanal dough glazed with premium melted white chocolate."},
        "cold_drink": {"title": "CRYSTAL ICY COLD", "item_name": "Chilled Icy Soda Pop", "origin": "Atlanta, USA 🇺🇸", "line": "An ice-cold sparkling beverage served with fresh mint leaves."},
        "burger": {"title": "GOURMET STACK", "item_name": "Artisanal Double-Stack Burger", "origin": "Hamburg, Germany 🇩🇪", "line": "Premium grilled cutlet layered with aged cheddar and secret house sauce."},
        "pizza": {"title": "WOODFIRED ITALIAN", "item_name": "Artisanal Neapolitan Pizza", "origin": "Naples, Italy 🇮🇹", "line": "Authentic sourdough crust topped with fresh mozzarella and torn basil."},
        "indian_spicy": {"title": "ROYAL CURRY EXPERT", "item_name": "Shahi Indian Mughlai Curry", "origin": "Delhi, India 🇮🇳", "line": "A rich, slow-cooked buttery gravy infused with exotic royal spices."},
        "japan_mochi": {"title": "MATCHA SUPREME", "item_name": "Sweet Uji Matcha Mochi", "origin": "Kyoto, Japan 🇯🇵", "line": "Soft, chewy rice cake outer layer filled with sweet premium red bean paste."},
        "mexico_quesadilla": {"title": "CHEESY SUPREME", "item_name": "Smoked Pepper Quesadilla", "origin": "Puebla, Mexico 🇲🇽", "line": "Toasted tortilla loaded with melted Monterey Jack cheese and fresh jalapenos."},
        "france_croissant": {"title": "BUTTER CRUISE", "item_name": "Flaky Flurries Croissant", "origin": "Paris, France 🇫🇷", "line": "Light, buttery puff pastry layers crafted by elite French artisans."},
        "italy_pasta": {"title": "CREAMY ALFREDO", "item_name": "Truffle Mushroom Alfredo", "origin": "Rome, Italy 🇮🇹", "line": "Al dente fettuccine tossed in a rich parmesan and wild truffle cream sauce."},
        "china_dimsum": {"title": "STEAMED BLISS", "item_name": "Crystal Veg Dim Sum Box", "origin": "Guangdong, China 🇨🇳", "line": "Translucent dumpling wraps tightly packing finely minced premium farm greens."},
        "turkey_baklava": {"title": "ROYAL PISTACHIO", "item_name": "Layered Honey Gold Baklava", "origin": "Gaziantep, Turkey 🇹🇷", "line": "Crispy golden filo sheets dripping with organic honey and crushed pistachios."},
        "korea_tteokbokki": {"title": "SEOUL SPICY SOUL", "item_name": "Cheesy Gochujang Tteokbokki", "origin": "Seoul, South Korea 🇰🇷", "line": "Simmered chewy cylindrical rice cakes bathed in fiery, sweet chili glaze."},
        "thailand_mangorice": {"title": "SIAM SWEET", "item_name": "Sweet Coconut Mango Rice", "origin": "Bangkok, Thailand 🇹🇭", "line": "Warm fragrant sticky rice paired with sweet yellow mango slices and coconut milk."},
        "spain_churros": {"title": "CRISPY CINNAMON", "item_name": "Golden Sweet Churros", "origin": "Madrid, Spain 🇪🇸", "line": "Golden fried pastry dough dusted beautifully with cinnamon sugar, served with a cup of rich, warm chocolate dip."},
        "usa_waffles": {"title": "USA: CLASSIC DOWNTOWN DINER", "item_name": "Loaded Premium Buttermilk Waffles", "origin": "New York, USA 🇺🇸", "line": "Fluffy, crispy golden waffles topped with sweet maple syrup, a dollop of fresh whipped cream, and wild berries."}
    }
    
    if item not in menu_data:
        await interaction.followup.send("❌ Error: Invalid menu item selected.")
        return

    selected = menu_data.get(item)
    
    # 💰 ECONOMY SYSTEM
    prices = {
        "coffee": 50, "donuts": 60, "cold_drink": 70, "burger": 100, "pizza": 120, "indian_spicy": 150,
        "japan_mochi": 180, "mexico_quesadilla": 200, "france_croissant": 220, "italy_pasta": 250,
        "china_dimsum": 260, "turkey_baklava": 280, "korea_tteokbokki": 300, "thailand_mangorice": 320,
        "spain_churros": 340, "usa_waffles": 350
    }
    
    item_cost = prices.get(item, 0)
    user_id = str(interaction.user.id)
    eco_data = load_economy()
    eco_data = check_account(user_id, eco_data)
    
    if eco_data[user_id]["balance"] < item_cost:
        embed_fail = discord.Embed(
            title="💸 INSUFFICIENT FUNDS",
            description=f"❌ {interaction.user.mention}, aapke paas `{selected['item_name']}` serve karne ke liye paryapt coins nahi hain!\n\n💰 **Required:** `{item_cost} Coins` | 💳 **Your Balance:** `{eco_data[user_id]['balance']} Coins`\n\n💡 *Coins kamane ke liye `/daily` command use karein!*",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed_fail)
        return
        
    eco_data[user_id]["balance"] -= item_cost
    save_economy(eco_data)

    desc_template = (
        f"**👑 International Order Fulfilled!**\n\n"
        f"**🔹 Gourmet Item:** `{selected['item_name']}`\n"
        f"**🔹 Culinary Origin:** *{selected['origin']}*\n"
        f"💸 **Cost Deducted:** `{item_cost} Stardust Coins`\n\n"
        f"ℹ️ *{selected['line']}*\n\n"
        f"─── *Enjoy your elite dining experience!* ───"
    )
    
    embed = discord.Embed(
        title=f"👑 ─── {selected['title']} ─── 👑",
        description=desc_template,
        color=discord.Color.from_rgb(245, 238, 227)
    )
    embed.set_footer(text=f"✨ Stardust Butler System • Balance Left: {eco_data[user_id]['balance']} Coins")
    
    content_text = f"🛎️ {member.mention}, you have been served a premium meal!"
    await interaction.followup.send(content=content_text, embed=embed)

# ==============================================================================
# 🎭 MODULE 2.5: ANIME INTERACTION SUITE (ROLEPLAY - DIRECT GIF FIX)
# ==============================================================================

@bot.tree.command(name="hug", description="🤗 Give a super warm anime hug to another member!")
@discord.app_commands.describe(member="The member you want to hug")
async def hug(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("🤗 *Aww, did you just hug yourself? That's so sweet!*", ephemeral=True)
    
    embed = discord.Embed(
        title="✨ Cuddle Time! ✨",
        description=f"**{interaction.user.display_name}** wraps their arms tightly around **{member.display_name}** for a super warm, cozy hug! *~chu*",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/od5H3PmEG5EVq/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} You got a hug!", embed=embed)

@bot.tree.command(name="kiss", description="💋 Give a sweet anime kiss to someone special!")
@discord.app_commands.describe(member="The member you want to kiss")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("💋 *Wait... how do you even kiss yourself?*", ephemeral=True)
    
    embed = discord.Embed(
        title="💖 Sweet Affection 💖",
        description=f"**{interaction.user.display_name}** pulls **{member.display_name}** close and gives them a sweet, romantic kiss! *Blushes*",
        color=discord.Color.from_rgb(255, 105, 180)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/lTQF0ODLLjhza/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Someone kissed you!", embed=embed)

@bot.tree.command(name="cuddle", description="🧸 Cuddle up cozy with another member!")
@discord.app_commands.describe(member="The member you want to cuddle")
async def cuddle(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("🧸 *Grab a warm blanket if you are feeling a bit lonely!*", ephemeral=True)
    
    embed = discord.Embed(
        title="🐾 Cozy Snuggles 🐾",
        description=f"**{interaction.user.display_name}** snuggles up next to **{member.display_name}**, cuddling them closely and feeling super safe.",
        color=discord.Color.from_rgb(230, 230, 250)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/Zz9Ja5Oazv5xe/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Cuddle request accepted!", embed=embed)

@bot.tree.command(name="slap", description="💥 Give a sharp anime slap across the face!")
@discord.app_commands.describe(member="The member you want to slap")
async def slap(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("💥 *Ouch! Please don't hurt yourself!*", ephemeral=True)
    
    embed = discord.Embed(
        title="💢 Ouch! 💢",
        description=f"**{interaction.user.display_name}** swings their hand and **SLAPS** **{member.display_name}** right across the face! *B-Baka!*",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/Zau0yrl17uzdK/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} You just got slapped!", embed=embed)

@bot.tree.command(name="pat", description="🐱 Gently pat someone's head!")
@discord.app_commands.describe(member="The member you want to pat")
async def pat(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="🌸 Gentle Headpats 🌸",
        description=f"**{interaction.user.display_name}** gently pats **{member.display_name}** on the head. *Good day!*",
        color=discord.Color.from_rgb(255, 218, 185)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/ARSp9T7wwxNcs/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Pat pat!", embed=embed)

@bot.tree.command(name="wipetears", description="😢 Gently wipe away someone's tears.")
@discord.app_commands.describe(member="The member whose tears you want to wipe")
async def wipetears(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("😢 *Don't cry! Everything is going to be alright.*", ephemeral=True)
    
    embed = discord.Embed(
        title="🥺 Comfort 🥺",
        description=f"**{interaction.user.display_name}** leans in softly and gently wipes away the tears from **{member.display_name}**'s eyes. *'Don't cry, I am right here.'*",
        color=discord.Color.from_rgb(173, 216, 230)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/9f2hmeIcG7W7e/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} It's going to be okay.", embed=embed)

@bot.tree.command(name="lapride", description="🚲 Give someone a playful ride on your lap!")
@discord.app_commands.describe(member="The member you want to give a lap ride to")
async def lapride(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("❌ *You cannot sit on your own lap!*", ephemeral=True)
    
    embed = discord.Embed(
        title="✨ Playful Lap Ride ✨",
        description=f"**{interaction.user.display_name}** pulls **{member.display_name}** onto their lap and playfully carries them around! *Wheee!*",
        color=discord.Color.from_rgb(244, 164, 96)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/142UITj96U275e/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Look out!", embed=embed)

@bot.tree.command(name="handhold", description="🤝 Interlock fingers and hold hands!")
@discord.app_commands.describe(member="The member whose hand you want to hold")
async def handhold(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("🤝 *Holding your own hand? Sending you a virtual hug!*", ephemeral=True)
    
    embed = discord.Embed(
        title="💞 Holding Hands 💞",
        description=f"**{interaction.user.display_name}** gently reaches out, interlocking fingers to softly hold **{member.display_name}**'s hand...",
        color=discord.Color.from_rgb(255, 192, 203)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/j4bK8EwSgB00E/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Holding hands...", embed=embed)

@bot.tree.command(name="hairflip", description="🌟 Gently move a strand of hair away from someone's face.")
@discord.app_commands.describe(member="The member whose hair you want to tuck away")
async def hairflip(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("✨ *You just styled your own hair! looking sharp!*", ephemeral=True)
    
    embed = discord.Embed(
        title="😳 Attentive 😳",
        description=f"**{interaction.user.display_name}** leans close, softly tucking a stray strand of hair behind **{member.display_name}**'s ear...",
        color=discord.Color.from_rgb(221, 160, 221)
    )
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/134P6jh9pG4GgU/giphy.gif")
    await interaction.response.send_message(content=f"{member.mention} Soft touch...", embed=embed)






    
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

# =====================================================================
# 💰 MODULE 5: STARDUST CAFE LUXURY ECONOMY & GLOBAL SHOP
# =====================================================================

ECONOMY_FILE = "economy.json"

def load_economy():
    if os.path.exists(ECONOMY_FILE):
        try:
            with open(ECONOMY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_economy(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_account(user_id: str, data):
    if user_id not in data:
        data[user_id] = {"balance": 0, "last_daily": 0, "inventory": []}
    elif "inventory" not in data[user_id]:
        data[user_id]["inventory"] = []  # Purane registered users ke profile me inventory automatically add ho jayegi
    return data

@bot.tree.command(name="daily", description="🎁 Claim your daily premium Stardust Rewards!")
async def daily(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    data = load_economy()
    data = check_account(user_id, data)
    
    import time
    current_time = int(time.time())
    last_claim = data[user_id].get("last_daily", 0)
    cooldown = 86400  # 24 Hours in seconds
    
    if current_time - last_claim < cooldown:
        remaining_time = cooldown - (current_time - last_claim)
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        
        embed = discord.Embed(
            title="⏳ COOLDOWN ACTIVE",
            description=f"❌ {interaction.user.mention}, aap pehle hi aaj ka reward le chuke hain!\n\n⏳ **Agle reward ke liye intezar karein:** `{hours}h {minutes}m`",
            color=discord.Color.from_rgb(245, 238, 227)
        )
        await interaction.followup.send(embed=embed)
        return

    reward = 200
    data[user_id]["balance"] += reward
    data[user_id]["last_daily"] = current_time
    save_economy(data)
    
    embed = discord.Embed(
        title="🌟 ─── STARDUST DAILY BONUS ─── 🌟",
        description=(
            f"**Good Morning, Chef!** ✨\n\n"
            f"🎁 You have claimed your daily **{reward} Stardust Coins**!\n"
            f"💳 **New Wallet Balance:** `{data[user_id]['balance']} Coins`\n\n"
            f"─── *Come back tomorrow for more rewards!* ───"
        ),
        color=discord.Color.from_rgb(245, 238, 227)
    )
    embed.set_footer(text="✨ Powered by Stardust Luxury Butler")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="wallet", description="💳 View your personal Stardust Cafe balance sheet")
async def wallet(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    data = load_economy()
    data = check_account(user_id, data)
    
    balance = data[user_id]["balance"]
    
    embed = discord.Embed(
        title="💳 ─── STARDUST VAULT BALANCE ─── 💳",
        description=(
            f"👤 **Account Holder:** {interaction.user.mention}\n"
            f"🏛️ **Bank Status:** `Verified Pro Developer ✅`\n\n"
            f"🪙 **Available Balance:** `{balance} Stardust Coins`\n\n"
            f"💸 *Use `/menu` to check what luxurious food you can buy!*"
        ),
        color=discord.Color.from_rgb(245, 238, 227)
    )
    embed.set_footer(text="✨ Stardust Butler System")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="menu", description="📜 Open the ultimate global menu card of Stardust Cafe")
async def menu(interaction: discord.Interaction):
    await interaction.response.defer()
    
    shop_content = (
        "👑 **─── 🌟 STARDUST LUXURY CAFÉ MENU 🌟 ───** 👑\n"
        "*Every dish is 100% pure, premium, and globally certified.*\n\n"
        "**☕ HOUSE SPECIALS**\n"
        "• `coffee` ── ☕ Barista Coffee ── **50 Coins**\n"
        "• `donuts` ── 🍩 Glazed Donuts ── **60 Coins**\n"
        "• `cold_drink` ── 🥤 Chilled Icy Drink ── **70 Coins**\n"
        "• `burger` ── 🍔 Gourmet Stack Burger ── **100 Coins**\n"
        "• `pizza` ── 🍕 Woodfired Italian Pizza ── **120 Coins**\n"
        "• `indian_spicy` ── 🍛 Royal Indian Curry ── **150 Coins**\n\n"
        "**✈️ PRESTIGE GLOBAL CONFECTIONS**\n"
        "• `japan_mochi` ── 🇯🇵 Sweet Matcha Mochi ── **180 Coins**\n"
        "• `mexico_quesadilla` ── 🌮 Cheesy Veg Quesadilla ── **200 Coins**\n"
        "• `france_croissant` ── 🥐 Butter Croissant & Cafe ── **220 Coins**\n"
        "• `italy_pasta` ── 🍝 Creamy Alfredo Pasta ── **250 Coins**\n"
        "• `china_dimsum` ── 🇨🇳 Steamed Veg Dim Sum Box ── **260 Coins**\n"
        "• `turkey_baklava` ── 🇹🇷 Royal Pistachio Baklava ── **280 Coins**\n"
        "• `korea_tteokbokki` ── 🇰🇷 Cheesy Rice Cakes ── **300 Coins**\n"
        "• `thailand_mangorice` ── 🇹🇭 Mango Sticky Rice ── **320 Coins**\n"
        "• `spain_churros` ── 🇪🇸 Crispy Sweet Churros ── **340 Coins**\n"
        "• `usa_waffles` ── 🇺🇸 Loaded Premium Waffles ── **350 Coins**\n\n"
        "─── *To serve an item, you must have enough coins!* ───"
    )
    
    embed = discord.Embed(
        title="📜 ─── EST. 2026 GLOBAL MENU CARD ─── 📜",
        description=shop_content,
        color=discord.Color.from_rgb(245, 238, 227)
    )
    embed.set_footer(text="✨ Stardust Cafe Premium Management")
    await interaction.followup.send(embed=embed)
# ==============================================================================
# 🛒 MODULE 5.5: STARDUST COSMIC SHOP & INVENTORY
# ==============================================================================

SHOP_ITEMS = {
    # 🐾 COSMIC PETS CATEGORY
    "nebula_kitten": {"price": 1200, "type": "Pet", "display": "🐱 Nebula Kitten", "desc": "A cute space kitty that floats around your profile."},
    "stardust_dragon": {"price": 5000, "type": "Pet", "display": "🐲 Stardust Dragon", "desc": "A legendary cosmic dragon protecting your wallet."},
    "cyber_puppy": {"price": 2500, "type": "Pet", "display": "🐶 Cyber Puppy", "desc": "A futuristic neon puppy with glowing eyes."},
    
    # 🏅 PREMIUM BADGES CATEGORY
    "rich_vibes": {"price": 3000, "type": "Badge", "display": "💰 Richie Rich", "desc": "Show everyone that you are drowning in Stardust Coins!"},
    "elite_gamer": {"price": 1500, "type": "Badge", "display": "🎮 Elite Gamer", "desc": "A custom badge for the true grinders of the server."},
    "stardust_legend": {"price": 8000, "type": "Badge", "display": "✨ Cosmic Legend", "desc": "The ultimate status symbol on the server."}
}

@bot.tree.command(name="shop", description="🛒 Browse the premium Stardust Cosmic Shop!")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌟 STARDUST COSMIC SHOP 🌟",
        description="Welcome to the elite market! Use `/buy <item_name>` to unlock these premium collectibles.\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(147, 112, 219)
    )
    
    pets_text = ""
    for item_id, info in SHOP_ITEMS.items():
        if info["type"] == "Pet":
            pets_text += f"**{info['display']}** (`{item_id}`)\n🪙 Price: **{info['price']} Coins**\n✨ *{info['desc']}*\n\n"
    embed.add_field(name="🐾 Cosmic Pets", value=pets_text or "No pets available.", inline=False)
    
    badges_text = ""
    for item_id, info in SHOP_ITEMS.items():
        if info["type"] == "Badge":
            badges_text += f"**{info['display']}** (`{item_id}`)\n🪙 Price: **{info['price']} Coins**\n✨ *{info['desc']}*\n\n"
    embed.add_field(name="🏅 Premium Badges", value=badges_text or "No badges available.", inline=False)
    
    embed.set_footer(text="✨ Stardust Economy System • Shop Luxury Items")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="buy", description="🛍️ Purchase an item or adopt a pet from the shop!")
@discord.app_commands.describe(item_id="The short ID of the item (e.g., nebula_kitten, rich_vibes)")
async def buy(interaction: discord.Interaction, item_id: str):
    await interaction.response.defer()
    
    user_id = str(interaction.user.id)
    item_id = item_id.lower().strip()
    
    if item_id not in SHOP_ITEMS:
        return await interaction.followup.send("❌ **Invalid Item ID!** Please check `/shop` for the correct item keywords.", ephemeral=True)
    
    item = SHOP_ITEMS[item_id]
    
    data = load_economy()
    data = check_account(user_id, data)
    
    if item_id in data[user_id]["inventory"]:
        return await interaction.followup.send(f"❌ **You already own {item['display']}!** You cannot buy duplicates of this item.", ephemeral=True)
    
    if data[user_id]["balance"] < item["price"]:
        shortage = item["price"] - data[user_id]["balance"]
        return await interaction.followup.send(f"❌ **Insufficient Funds!** You need **{shortage} more Stardust Coins** to purchase {item['display']}.", ephemeral=True)
    
    data[user_id]["balance"] -= item["price"]
    data[user_id]["inventory"].append(item_id)
    save_economy(data)
    
    embed = discord.Embed(
        title="🎉 Purchase Successful! 🎉",
        description=f"Congratulations **{interaction.user.display_name}**!\n\n"
                    f"You have successfully acquired/adopted **{item['display']}**!\n"
                    f"🪙 **{item['price']} Stardust Coins** have been deducted from your wallet.",
        color=discord.Color.from_rgb(50, 205, 50)
    )
    embed.set_footer(text=f"New Wallet Balance: {data[user_id]['balance']} Coins")
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="inventory", description="🎒 View all your adopted cosmic pets and premium badges!")
async def inventory(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_economy()
    data = check_account(user_id, data)
    
    user_inventory = data[user_id].get("inventory", [])
    
    embed = discord.Embed(
        title=f"🎒 {interaction.user.display_name}'s Cosmic Vault",
        description="Here is everything you have collected from the Stardust Shop!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(30, 144, 255)
    )
    
    if not user_inventory:
        embed.description += "\n*Your vault is completely empty! Collect some coins and visit `/shop` to buy cute things!*"
    else:
        pets_list = []
        badges_list = []
        
        for item_id in user_inventory:
            if item_id in SHOP_ITEMS:
                item = SHOP_ITEMS[item_id]
                if item["type"] == "Pet":
                    pets_list.append(item["display"])
                elif item["type"] == "Badge":
                    badges_list.append(item["display"])
                    
        embed.add_field(name="🐾 Adopted Pets", value="\n".join(pets_list) if pets_list else "*No pets adopted yet.*", inline=True)
        embed.add_field(name="🏅 Unlocked Badges", value="\n".join(badges_list) if badges_list else "*No badges unlocked yet.*", inline=True)
        
    embed.set_footer(text="✨ Showcase your inventory to your friends!")
    await interaction.response.send_message(embed=embed)
# ==============================================================================
# 💎 MODULE 6.0: ADMIN ECONOMY, LEADERBOARD & ADVANCED GIVEAWAYS
# ==============================================================================

import asyncio
import random
import re

# 1. ADMIN COMMAND: ADD MONEY
@bot.tree.command(name="addmoney", description="⚙️ Admin Only: Add Stardust Coins to a member's wallet!")
@discord.app_commands.describe(member="The member receiving the coins", amount="Amount of coins to add")
@discord.app_commands.checks.has_permissions(administrator=True)
async def addmoney(interaction: discord.Interaction, member: discord.Member, amount: int):
    if amount <= 0:
        return await interaction.response.send_message("❌ **Amount must be greater than 0!**", ephemeral=True)
        
    await interaction.response.defer()
    user_id = str(member.id)
    
    data = load_economy()
    data = check_account(user_id, data)
    
    data[user_id]["balance"] += amount
    save_economy(data)
    
    embed = discord.Embed(
        title="✨ Stardust Treasury Mint ✨",
        description=f"Successfully added **{amount:,} Stardust Coins** to {member.mention}'s vault! 🪙",
        color=discord.Color.from_rgb(255, 215, 0)
    )
    embed.set_footer(text=f"Authorized by: {interaction.user.display_name}")
    await interaction.followup.send(embed=embed)

@addmoney.error
async def addmoney_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ **Permission Denied!** Only server Administrators can use this command.", ephemeral=True)


# 2. ECONOMY RANK / LEADERBOARD COMMAND
@bot.tree.command(name="richest", description="🏆 View the top 10 richest members in the server!")
async def richest(interaction: discord.Interaction):
    await interaction.response.defer()
    data = load_economy()
    
    # Sort users by balance descending
    sorted_users = sorted(data.items(), key=lambda item: item[0] if isinstance(item[1], int) else item[1].get("balance", 0), reverse=True)
    
    embed = discord.Embed(
        title="👑 STARDUST WEALTH LEADERBOARD 👑",
        description="Here are the top elite billionaires of the server!\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(230, 230, 250)
    )
    
    leaderboard_text = ""
    rank = 1
    for user_id, user_data in sorted_users[:10]:
        # Handle old int data type vs new dict data type safely
        balance = user_data if isinstance(user_data, int) else user_data.get("balance", 0)
        
        member = interaction.guild.get_member(int(user_id))
        name = member.display_name if member else f"User ({user_id})"
        
        # Add medals for top 3
        if rank == 1: medal = "🥇"
        elif rank == 2: medal = "🥈"
        elif rank == 3: medal = "🥉"
        else: medal = f"`#{rank}` "
        
        leaderboard_text += f"{medal} **{name}** — 🪙 `{balance:,}` Coins\n"
        rank += 1
        
    embed.description += f"\n{leaderboard_text or '*No records found.*'}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    embed.set_footer(text="✨ Grinding pays off! Check your balance with /wallet")
    await interaction.followup.send(embed=embed)


# 3. LUXURY & PROFESSIONAL GIVEAWAY SYSTEM
def parse_duration(duration_str: str) -> int:
    """Helper to convert 5h, 30m, 1d into seconds"""
    match = re.match(r"(\d+)([smhd])", duration_str.lower().strip())
    if not match:
        return 0
    amount, unit = match.groups()
    amount = int(amount)
    if unit == 's': return amount
    if unit == 'm': return amount * 60
    if unit == 'h': return amount * 3600
    if unit == 'd': return amount * 86400
    return 0

@bot.tree.command(name="gstart", description="🎉 Launch a premium aesthetic giveaway!")
@discord.app_commands.describe(duration="Time duration (e.g., 30m, 5h, 1d)", winners="Number of winners", prize="The prize description")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def gstart(interaction: discord.Interaction, duration: str, winners: int, prize: str):
    seconds = parse_duration(duration)
    if seconds <= 0:
        return await interaction.response.send_message("❌ **Invalid duration format!** Use `30m` (minutes), `5h` (hours), or `1d` (days).", ephemeral=True)
    if winners <= 0:
        return await interaction.response.send_message("❌ **Winners must be at least 1!**", ephemeral=True)
        
    await interaction.response.defer()
    
    # Clean professional embed setup matching the provided asset styling
    embed = discord.Embed(
        title=f"🎁 {prize.upper()} 🎁",
        description=f"♡ React with \"🎉\" to join!\n\n"
                    f"♡ **Ends:** in {duration}\n"
                    f"♡ **Hosted by:** {interaction.user.mention}\n"
                    f"♡ **Winners:** {winners}\n\n"
                    f"୨୧ *All extra entries from roles stack! Check channels for perks.* ୨୧\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(186, 85, 211)
    )
    embed.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW9pM3R5Y3B4NXc0M3B5M3B5M3B5M3B5M3B5M3B5M3B5JmN0PWc/l3q2zVr6cu95nF6O4/giphy.gif")
    embed.set_footer(text="💧 Click the reaction below to enter!")
    
    # Send message and add reaction
    g_message = await interaction.followup.send(embed=embed, wait=True)
    await g_message.add_reaction("🎉")
    
    # Wait for the duration
    await asyncio.sleep(seconds)
    
    # Fetch final message data to get accurate reactions
    try:
        g_message = await interaction.channel.fetch_message(g_message.id)
    except discord.NotFound:
        return  # Giveaway channel or message was deleted
        
    reaction = discord.utils.get(g_message.reactions, emoji="🎉")
    users = [user async for user in reaction.users() if not user.bot]
    
    if len(users) == 0:
        end_embed = discord.Embed(
            title="🎉 GIVEAWAY ENDED 🎉",
            description=f"**Prize:** {prize}\n\n❌ **No entries received.** No winners could be determined!",
            color=discord.Color.red()
        )
        return await g_message.edit(embed=end_embed)
        
    # Choose winners dynamically
    chosen_winners = random.sample(users, min(len(users), winners))
    winner_mentions = ", ".join([winner.mention for winner in chosen_winners])
    
    end_embed = discord.Embed(
        title="🎉 GIVEAWAY CONCLUDED 🎉",
        description=f"♡ **Prize:** {prize}\n"
                    f"♡ **Hosted by:** {interaction.user.mention}\n"
                    f"♡ **Winners:** {winner_mentions}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✨ Congratulations! Please contact staff or use commands to claim your reward! ✨",
        color=discord.Color.from_rgb(50, 205, 50)
    )
    await g_message.edit(embed=end_embed)
    await interaction.channel.send(f"🎊 Congratulations {winner_mentions}! You won the giveaway for **{prize}**! 🎊")

@gstart.error
async def gstart_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ **Permission Denied!** You need `Manage Server` permissions to host giveaways.", ephemeral=True)
# ==============================================================================
# 🛡️ MODULE 7.0: AUTOMOD & ADVANCED MODERATION SUITE
# ==============================================================================

# 1. AUTOMOD SYSTEM (Banned Words List)
# Aap is list me apni marzi se aur bhi words comma (,) laga kar jod sakte hain
BANNED_WORDS = ["badword1", "badword2", "fuck", "bitch", "asshole", "slut"]

@bot.event
async def on_message(message: discord.Message):
    # Agar message bot ka apna hai toh ignore karein
    if message.author.bot:
        return

    # Check if message contains any banned word
    content_lower = message.content.lower()
    for word in BANNED_WORDS:
        if word in content_lower:
            try:
                await message.delete()
                
                # Send warning embed in chat
                embed = discord.Embed(
                    title="🛡️ AutoMod Protection",
                    description=f"⚠️ {message.author.mention}, your message was automatically removed because it contained blocked or inappropriate language.",
                    color=discord.Color.from_rgb(255, 69, 0)
                )
                warn_msg = await message.channel.send(embed=embed)
                # 5 seconds baad warning message ko delete kar dega taaki chat clean rahe
                await asyncio.sleep(5)
                await warn_msg.delete()
                return
            except discord.Forbidden:
                print(f"Missing permissions to delete message in {message.channel.name}")
            except Exception as e:
                print(f"Error in AutoMod: {e}")

    # Yeh line zaroori hai taaki baki normal commands bhi chalte rahein
    await bot.process_commands(message)


# 2. ADD ROLE COMMAND
@bot.tree.command(name="addrole", description="➕ Give a server role to a member safely.")
@discord.app_commands.describe(member="The member to receive the role", role="The role you want to give")
@discord.app_commands.checks.has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await interaction.response.defer()
    
    # Check bot role hierarchy
    if role >= interaction.guild.me.top_role:
        return await interaction.followup.send("❌ **Permission Error:** That role is higher than my bot's highest role! Move my role up in server settings.", ephemeral=True)
        
    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="✨ Role Granted ✨",
            description=f"Successfully assigned the role {role.mention} to **{member.display_name}**!",
            color=discord.Color.from_rgb(50, 205, 50)
        )
        embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send("❌ I do not have permission to manage this role.", ephemeral=True)


# 3. REMOVE ROLE COMMAND
@bot.tree.command(name="removerole", description="➖ Take away a server role from a member.")
@discord.app_commands.describe(member="The member whose role will be removed", role="The role you want to remove")
@discord.app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await interaction.response.defer()
    
    if role >= interaction.guild.me.top_role:
        return await interaction.followup.send("❌ **Permission Error:** That role is higher than my bot's highest role!", ephemeral=True)
        
    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="✨ Role Removed ✨",
            description=f"Successfully removed the role {role.mention} from **{member.display_name}**.",
            color=discord.Color.from_rgb(255, 99, 71)
        )
        embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send("❌ I do not have permission to modify this role.", ephemeral=True)


# 4. WARN COMMAND
@bot.tree.command(name="warn", description="⚠️ Issue a formal warning to a rule breaker.")
@discord.app_commands.describe(member="The member to warn", reason="The reason for the warning")
@discord.app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("❌ You cannot warn yourself!", ephemeral=True)
    if member.bot:
        return await interaction.response.send_message("❌ You cannot warn a bot!", ephemeral=True)
        
    await interaction.response.defer()
    
    # Public warning card in the server channel
    server_embed = discord.Embed(
        title="⚠️ Member Formally Warned ⚠️",
        description=f"**User:** {member.mention} (`{member.id}`)\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user.mention}",
        color=discord.Color.from_rgb(255, 140, 0)
    )
    server_embed.set_timestamp()
    await interaction.followup.send(embed=server_embed)
    
    # Attempt to DM the user to notify them privately
    try:
        dm_embed = discord.Embed(
            title=f"⚠️ Warning Notification from {interaction.guild.name}",
            description=f"You have been issued a formal warning.\n\n"
                        f"📝 **Reason:** {reason}\n"
                        f"🛡️ Please review the server rules to avoid further moderation actions (mute/kick/ban).",
            color=discord.Color.orange()
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # User has DMs closed, safe to ignore
        pass

# Error handlers for permission checks
@addrole.error
@removerole.error
async def role_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ **Permission Denied!** You need `Manage Roles` permission to run this command.", ephemeral=True)

@warn.error
async def warn_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ **Permission Denied!** You need `Kick Members` permission to warn users.", ephemeral=True)
# ==============================================================================
# 📊 MODULE 8.0: WEEKLY MULTI-PAGE LEADERBOARD & ADVANCED AUTOMOD CONTROL
# ==============================================================================

import json
from discord.ext import tasks

# Global database structure for configuration (Aap chahein toh ise alag file me save kar sakte hain)
# Format: {"guild_id": {"channel_id": 123, "message_id": 456, "automod_enabled": True}}
SERVER_CONFIGS = {}

# ------------------------------------------------------------------------------
# 🏆 SECTION A: AUTOMATIC MULTI-PAGE LEADERBOARD SYSTEM
# ------------------------------------------------------------------------------

async def generate_leaderboard_embeds(guild: discord.Guild):
    """Helper function to generate all pages for the weekly leaderboard"""
    data = load_economy() # Economy, inventory, aur levels ka data fetch karne ke liye
    
    # 1. Page One: Rich Currency Leaderboard
    sorted_money = sorted(data.items(), key=lambda item: item[1] if isinstance(item[1], int) else item[1].get("balance", 0), reverse=True)[:5]
    money_text = ""
    for r, (u_id, u_data) in enumerate(sorted_money, 1):
        bal = u_data if isinstance(u_data, int) else u_data.get("balance", 0)
        m = guild.get_member(int(u_id))
        money_text += f"`#{r}` **{m.display_name if m else 'Left Member'}** — 🪙 `{bal:,}` Coins\n"

    embed1 = discord.Embed(
        title="👑 WEEKLY ELITE LEADERBOARD: WALLET 👑",
        description=f"Top economy giants this week:\n\n{money_text or '*No data collected yet.*'}",
        color=discord.Color.from_rgb(255, 215, 0)
    )
    embed1.set_footer(text="Page 1/3 • Updates automatically every week!")

    # 2. Page Two: Collector Vault (Items Bought from Shop)
    sorted_items = sorted(data.items(), key=lambda item: len(item[1].get("inventory", [])) if isinstance(item[1], dict) else 0, reverse=True)[:5]
    items_text = ""
    for r, (u_id, u_data) in enumerate(sorted_items, 1):
        inv_count = len(u_data.get("inventory", [])) if isinstance(u_data, dict) else 0
        m = guild.get_member(int(u_id))
        items_text += f"`#{r}` **{m.display_name if m else 'Left Member'}** — 🎒 `{inv_count}` Shop Items Unlocked\n"

    embed2 = discord.Embed(
        title="🎒 WEEKLY ELITE LEADERBOARD: VAULT 🎒",
        description=f"Top shop collectors this week:\n\n{items_text or '*No data collected yet.*'}",
        color=discord.Color.from_rgb(30, 144, 255)
    )
    embed2.set_footer(text="Page 2/3 • Updates automatically every week!")

    # 3. Page Three: Chat Engagement & Messages
    # (Assuming level/message counter is stored in database as 'messages' or 'xp')
    sorted_levels = sorted(data.items(), key=lambda item: item[1].get("last_daily", 0) if isinstance(item[1], dict) else 0, reverse=True)[:5]
    levels_text = ""
    for r, (u_id, u_data) in enumerate(sorted_levels, 1):
        m = guild.get_member(int(u_id))
        levels_text += f"`#{r}` **{m.display_name if m else 'Left Member'}** — Active Status Verified ✅\n"

    embed3 = discord.Embed(
        title="💬 WEEKLY ELITE LEADERBOARD: ENGAGEMENT 💬",
        description=f"Top active chatters this week:\n\n{levels_text or '*No data collected yet.*'}",
        color=discord.Color.from_rgb(186, 85, 211)
    )
    embed3.set_footer(text="Page 3/3 • Updates automatically every week!")

    return [embed1, embed2, embed3]


# ⏳ AUTOMATIC WEEKLY LOOP TASK (Runs background process)
@tasks.loop(hours=168.0) # 168 Hours = Exact 1 Week
async def weekly_leaderboard_updater():
    for guild_id, config in list(SERVER_CONFIGS.items()):
        guild = bot.get_guild(int(guild_id))
        if not guild: continue
        
        channel = guild.get_channel(config.get("channel_id"))
        if not channel: continue
        
        try:
            embeds = await generate_leaderboard_embeds(guild)
            # Purane tracked message ko edit karne ke badle clear fresh report create karega
            msg = await channel.send(embed=embeds[0])
            config["message_id"] = msg.id
            
            # Dynamic multi-page sliding panel emulation using interactions
            # For simplicity without UI crash on host restart, we send them as sequential stack logs or dynamic embeds
        except Exception as e:
            print(f"Error updating weekly stats for guild {guild_id}: {e}")


# SLASH COMMAND: SET LEADERBOARD CHANNEL
@bot.tree.command(name="setleaderboard", description="⚙️ Admin Only: Set the active dynamic weekly leaderboard channel!")
@discord.app_commands.describe(channel="The channel where leaderboard pages will stay synced")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setleaderboard(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer()
    g_id = str(interaction.guild_id)
    
    if g_id not in SERVER_CONFIGS:
        SERVER_CONFIGS[g_id] = {}
        
    SERVER_CONFIGS[g_id]["channel_id"] = channel.id
    
    embeds = await generate_leaderboard_embeds(interaction.guild)
    
    await channel.send("📊 **STARDUST LIVE STATS CONTROL CENTER** 📊\n*This message updates dynamically every week.*")
    for embed in embeds:
        await channel.send(embed=embed)
        
    if not weekly_leaderboard_updater.is_running():
        weekly_leaderboard_updater.start()
        
    await interaction.followup.send(f"✅ **Success!** Leaderboard channel has been mapped to {channel.mention}. All stat categories are now live.")


# SLASH COMMAND: REMOVE LEADERBOARD
@bot.tree.command(name="removeleaderboard", description="⚙️ Admin Only: Disable and wipe weekly leaderboard tracker configurations.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def removeleaderboard(interaction: discord.Interaction):
    g_id = str(interaction.guild_id)
    if g_id in SERVER_CONFIGS and "channel_id" in SERVER_CONFIGS[g_id]:
        SERVER_CONFIGS[g_id].pop("channel_id", None)
        await interaction.response.send_message("🗑️ **Leaderboard Disabled!** Automatic weekly logging cycles removed for this server.")
    else:
        await interaction.response.send_message("❌ **No active leaderboard configuration found** to clear.", ephemeral=True)


# SLASH COMMAND: TEST LEADERBOARD
@bot.tree.command(name="testleaderboard", description="🧪 Test Only: Force render the multi-page board layout instantly.")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def testleaderboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embeds = await generate_leaderboard_embeds(interaction.guild)
    
    for embed in embeds:
        await interaction.channel.send(embed=embed)
    await interaction.followup.send("🎯 **Test Render Triggered!** Check the channel to verify the structured layout cards.")


# ------------------------------------------------------------------------------
# 🛡️ SECTION B: PREMIUM CONTROL AUTOMOD MANAGEMENT SYSTEM
# ------------------------------------------------------------------------------

# Premium system curated badwords filtering matrix
BLOCK_LIST = ["fuck", "bitch", "asshole", "slut", "nigger", "dick", "bastard"]

@bot.tree.command(name="automod_setup", description="🛡️ Admin Only: Enable or Disable global chat text guard filters.")
@discord.app_commands.describe(status="Choose True to active safety shield, False to pause")
@discord.app_commands.checks.has_permissions(administrator=True)
async def automod_setup(interaction: discord.Interaction, status: bool):
    g_id = str(interaction.guild_id)
    if g_id not in SERVER_CONFIGS:
        SERVER_CONFIGS[g_id] = {}
        
    SERVER_CONFIGS[g_id]["automod_enabled"] = status
    state_str = "🟢 **ENABLED & MONITORING CHAT**" if status else "🔴 **DISABLED / SHUTDOWN**"
    
    embed = discord.Embed(
        title="🛡️ STARDUST AUTOMOD CENTRAL SUITE",
        description=f"Global safety filter update:\n\nSystem Core State: {state_str}\n"
                    f"Action Policy: *Instant Message Wiping + Automated Log Warn Warnings*",
        color=discord.Color.gold() if status else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)


# EVENT LISTENER: BACKEND INTERCEPT CHAT SECURITY MONITORING
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    g_id = str(message.guild.id)
    # Check config map to see if security engine state is enabled
    is_automod_on = SERVER_CONFIGS.get(g_id, {}).get("automod_enabled", True) # Defaults to true if setup command hasn't been run yet

    if is_automod_on:
        clean_content = message.content.lower().strip()
        for toxic_word in BLOCK_LIST:
            if toxic_word in clean_content:
                try:
                    await message.delete()
                    alert = discord.Embed(
                        title="🛡️ System Shield Intervention",
                        description=f"⚠️ {message.author.mention}, your text pattern triggered the premium word block filter list. Clean chat environment rules apply.",
                        color=discord.Color.from_rgb(255, 99, 71)
                    )
                    warn_msg = await message.channel.send(embed=alert)
                    await asyncio.sleep(4)
                    await warn_msg.delete()
                    return # Stop verification immediately since the threat object is scrubbed
                except discord.Forbidden:
                    pass # Log silently if missing role privileges over that individual admin object
                except Exception as e:
                    print(f"Filter Exception: {e}")

    await bot.process_commands(message)

# PERMISSION ERROR HANDLERS
@setleaderboard.error
@removeleaderboard.error
@automod_setup.error
async def admin_modules_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ **Access Denied!** This feature module requires active `Administrator` permissions.", ephemeral=True)
# ==============================================================================
# 🚀 MODULE 9.0: ADVANCED ECONOMY, BOOSTER REWARDS & PERK SHOP
# ==============================================================================

# 1. AUTOMATIC NITRO BOOSTER REWARD DETECTOR
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Check agar user ne abhi booster status start kiya hai
    if not before.premium_since and after.premium_since:
        user_id = str(after.id)
        
        # Load aur check account database
        data = load_economy()
        data = check_account(user_id, data)
        
        # 🪙 Reward: Give 10,000 bonus coins to the booster!
        booster_bonus = 10000
        data[user_id]["balance"] += booster_bonus
        
        # 🏅 Reward: Automatically append exclusive badge to their inventory
        if "booster_elite" not in data[user_id]["inventory"]:
            data[user_id]["inventory"].append("booster_elite")
            
        save_economy(data)
        
        # Try to send a gorgeous thank you announcement in a general/system channel
        channel = after.guild.system_channel or after.guild.text_channels[0]
        if channel:
            embed = discord.Embed(
                title="✨ ULTRA SERVER BOOST DETECTED ✨",
                description=f"💖 Thank you so much for boosting the server, {after.mention}!\n\n"
                            f"🎁 **Your Premium Booster Rewards have been added:**\n"
                            f"🪙 +**{booster_bonus:,} Stardust Coins** injected into your wallet!\n"
                            f"🏅 Unlocked Exclusive Badge: **🔮 Server Booster** (Check `/inventory`)\n\n"
                            f"୨୧ *Your support keeps our galaxy shining bright!* ୨୧",
                color=discord.Color.from_rgb(244, 127, 255)
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await channel.send(embed=embed)


# 2. UPDATING THE EXTENDED SHOP DICTIONARY WITH PERKS
# Is database structural design ko hum slash commands me handle karenge safely
PERK_SHOP = {
    "vip_lounge": {"price": 15000, "display": "🎟️ Custom Temporary Channel", "desc": "Creates a private temporary text channel just for you for 24 hours."},
    "premium_role": {"price": 20000, "display": "✨ Star Elite Role", "desc": "Unlocks the exclusive premium server role directly on your profile."}
}

# 3. SLASH COMMAND: BUY PERK FROM SHOP
@bot.tree.command(name="buyperk", description="🎟️ Purchase exclusive server privileges and temporary channels!")
@discord.app_commands.describe(perk_id="Choose from 'vip_lounge' or 'premium_role'")
async def buyperk(interaction: discord.Interaction, perk_id: str):
    await interaction.response.defer()
    
    user_id = str(interaction.user.id)
    perk_id = perk_id.lower().strip()
    
    if perk_id not in PERK_SHOP:
        return await interaction.followup.send("❌ **Invalid Perk ID!** Use `vip_lounge` or `premium_role`.", ephemeral=True)
        
    perk = PERK_SHOP[perk_id]
    data = load_economy()
    data = check_account(user_id, data)
    
    # Check user balance
    if data[user_id]["balance"] < perk["price"]:
        shortage = perk["price"] - data[user_id]["balance"]
        return await interaction.followup.send(f"❌ **Insufficient Funds!** You need **{shortage} more coins** to buy {perk['display']}.", ephemeral=True)
        
    # Deduct funds
    data[user_id]["balance"] -= perk["price"]
    save_economy(data)
    
    # ─── PERK ACTION EXECUTION ───
    
    # Action A: Temp Text Channel Creation
    if perk_id == "vip_lounge":
        try:
            guild = interaction.guild
            # Owner permissions setup for the buyer
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            new_channel = await guild.create_text_channel(name=f"☁️-{interaction.user.display_name}-lounge", overwrites=overwrites)
            
            # Send intro greeting inside the temp channel
            await new_channel.send(f"🎉 Welcome {interaction.user.mention} to your custom private lounge! You have full access here for the next 24 hours.")
            
            embed = discord.Embed(
                title="🎟️ Perk Unlocked Successfully!",
                description=f"Created your temporary custom space: {new_channel.mention}!\n"
                            f"🪙 **{perk['price']} Coins** have been processed from your balance.",
                color=discord.Color.from_rgb(147, 112, 219)
            )
            await interaction.followup.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ **System Error:** Bot is missing `Manage Channels` permissions to execute this item.", ephemeral=True)
            
    # Action B: Give Special Permanent Server Role
    elif perk_id == "premium_role":
        try:
            # Server me is naam ka role dhoondhein ya naya banayein
            guild = interaction.guild
            role_name = "Star Elite ✨"
            existing_role = discord.utils.get(guild.roles, name=role_name)
            
            if not existing_role:
                existing_role = await guild.create_role(name=role_name, color=discord.Color.from_rgb(255, 215, 0))
                
            if existing_role >= guild.me.top_role:
                return await interaction.followup.send("❌ **Hierarchy Error:** Move the bot's role higher in integration settings.", ephemeral=True)
                
            await interaction.user.add_roles(existing_role)
            
            embed = discord.Embed(
                title="✨ Premium Role Active ✨",
                description=f"Congratulations! The legendary role {existing_role.mention} has been added to your account.",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ **System Error:** Bot is missing `Manage Roles` permission to award this badge.", ephemeral=True)


# 4. SLASH COMMAND: BROWSE PERK SHOP LIST
@bot.tree.command(name="perkshop", description="🛒 Browse the exclusive advanced server privilege marketplace!")
async def perkshop(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔮 STARDUST ULTIMATE PERK MARKETPLACE 🔮",
        description="Unlock exclusive server rights and permissions using your hard-earned coins!\n\n"
                    "Use `/buyperk <perk_id>` to purchase.\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(230, 230, 250)
    )
    
    for p_id, info in PERK_SHOP.items():
        embed.add_field(
            name=f"{info['display']} (`{p_id}`)",
            value=f"🪙 Price: **{info['price']} Coins**\nℹ️ *{info['desc']}*",
            inline=False
        )
        
    embed.set_footer(text="✨ Luxury Server Customization Panel")
    await interaction.response.send_message(embed=embed)

# Deploy System Launch Configuration
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: Running operation token string empty.")
