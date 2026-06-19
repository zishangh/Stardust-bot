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

@bot.tree.command(name="serve", description="🍽️ Serve a 100% pure premium global aesthetic food item from the Stardust Cafe")
@discord.app_commands.describe(
    item="Choose the premium safe item to serve",
    member="The customer who will receive this delicious treat"
)
@discord.app_commands.choices(item=[
    # Original Base Menu (Pure Veg / Soft Drinks)
    discord.app_commands.Choice(name="☕ Barista Coffee", value="coffee"),
    discord.app_commands.Choice(name="🍕 Woodfired Pizza", value="pizza"),
    discord.app_commands.Choice(name="🍔 Gourmet Burger", value="burger"),
    discord.app_commands.Choice(name="🥤 Chilled Drink", value="cold_drink"),
    discord.app_commands.Choice(name="🍛 Royal Indian Curry", value="indian_spicy"),
    discord.app_commands.Choice(name="🍩 Glazed Donuts", value="donuts"),
    # New 10 100% Pure & Safe International Choices
    discord.app_commands.Choice(name="🇯🇵 Japan: Sweet Matcha Mochi", value="japan_mochi"),
    discord.app_commands.Choice(name="🌮 Mexico: Cheesy Veg Quesadilla", value="mexico_quesadilla"),
    discord.app_commands.Choice(name="🥐 France: Butter Croissant & Cafe", value="france_croissant"),
    discord.app_commands.Choice(name="🍝 Italy: Creamy Alfredo Pasta", value="italy_pasta"),
    discord.app_commands.Choice(name="🇨🇳 China: Steamed Veg Dim Sum Box", value="china_dimsum"),
    discord.app_commands.Choice(name="🇹🇷 Turkey: Royal Pistachio Baklava", value="turkey_baklava"),
    discord.app_commands.Choice(name="🇰🇷 South Korea: Cheesy Rice Cakes (Tteokbokki)", value="korea_tteokbokki"),
    discord.app_commands.Choice(name="🇹🇭 Thailand: Mango Sticky Rice Dessert", value="thailand_mangorice"),
    discord.app_commands.Choice(name="🇪🇸 Spain: Crispy Sweet Churros Box", value="spain_churros"),
    discord.app_commands.Choice(name="🇺🇸 USA: Loaded Premium Waffles", value="usa_waffles")
])
async def serve(interaction: discord.Interaction, item: str, member: discord.Member):
    await interaction.response.defer()
    
    menu_data = {
        "coffee": {
            "title": "☕ STARDUST PREMIUM BARISTA",
            "item_name": "Freshly Brewed Barista Coffee",
            "origin": "Stardust Cafe House Blend ✨",
            "line": "A warm, aromatic blend crafted with golden coffee beans and premium cream froth. Served hot just for you! 🌸"
        },
        "pizza": {
            "title": "🍕 WOODFIRED ITALIAN DELIGHT",
            "item_name": "Authentic Woodfired Pizza",
            "origin": "Naples Heritage 🇮🇹",
            "line": "A piping hot crust loaded with premium stretching mozzarella, fresh basil, and signature rich marinara sauce! 🧀"
        },
        "burger": {
            "title": "🍔 CLASSIC GOURMET STACK",
            "item_name": "Gourmet Crispy Stack Burger",
            "origin": "Chef's Special 🧑‍🍳",
            "line": "A giant, juicy premium patty layered with melting cheddar, crunchy lettuce, and a secret smoky chef's sauce! 🥓"
        },
        "cold_drink": {
            "title": "🥤 ICY REFRESHING BLISS",
            "item_name": "Chilled Bubble Icy Soda",
            "origin": "Arctic Frost Edition 🧊",
            "line": "An absolute freeze experience! A crystal-clear sparkling beverage bubbling with icy freshness to cool your soul."
        },
        "indian_spicy": {
            "title": "🍛 ROYAL INDIAN SPICE PLATTER",
            "item_name": "Aromatic Royal Curry Platter",
            "origin": "Imperial India 🇮🇳",
            "line": "A rich, steaming hot authentic curry cooked with secret traditional spices, fresh cream, and pure love. 🔥🌶️"
        },
        "donuts": {
            "title": "🍩 GLAZED SWEET CONFECTION",
            "item_name": "Premium Glazed Chocolate Donuts",
            "origin": "Sweet Treats Corner 🌸",
            "line": "A heavenly box of soft, airy donuts dipped in premium milk chocolate and topped with colorful pastel flakes."
        },
        "japan_mochi": {
            "title": "🇯🇵 JAPAN: TRADITIONAL MATCHA HARMONY",
            "item_name": "Sweet Green Tea Matcha Mochi",
            "origin": "Kyoto, Japan 🇯🇵",
            "line": "Soft, chewy pounded rice cakes filled with premium aromatic sweet green tea matcha cream. A peaceful bliss! 🌸"
        },
        "mexico_quesadilla": {
            "title": "🌮 MEXICO: FIESTA CHEESY CRUNCH",
            "item_name": "Loaded Veggie Quesadilla",
            "origin": "Puebla, Mexico 🇲🇽",
            "line": "Grilled warm tortillas packed full with melting Monterey Jack cheese, sweet corn, bell peppers, and zesty herbs! 🧀"
        },
        "france_croissant": {
            "title": "🥐 FRANCE: ROYAL PARISIAN BREAKFAST",
            "item_name": "Golden Butter Croissant & Cafe",
            "origin": "Paris, France 🇫🇷",
            "line": "Flaky, multi-layered warm pastry baked with pure French butter, serving an elite melt-inyour-mouth luxury vibe! ✨"
        },
        "italy_pasta": {
            "title": "🍝 ITALY: TUSCAN HARVEST",
            "item_name": "Creamy Alfredo Fettuccine Pasta",
            "origin": "Tuscany, Italy 🇮🇹",
            "line": "Perfectly al dente pasta tossed gently in a rich, velvet sauce of aged parmesan, fresh garlic, and melted butter! 🧀"
        },
        "china_dimsum": {
            "title": "🇨🇳 CHINA: IMPERIAL DIM SUM BOX",
            "item_name": "Steamed Artisan Veg Dim Sums",
            "origin": "Guangzhou, China 🇨🇳",
            "line": "A traditional steaming bamboo basket containing delicate, translucent crystal dumplings filled with finely chopped fresh greens! 🥢"
        },
        "turkey_baklava": {
            "title": "🇹🇷 TURKEY: SULTAN'S PALACE DESSERT",
            "item_name": "Royal Pistachio Baklava",
            "origin": "Gaziantep, Turkey 🇹🇷",
            "line": "Rich, sweet pastry made of layers of flaky phyllo dough filled with crushed premium pistachios and sweetened with pure syrup! 🍯"
        },
        "korea_tteokbokki": {
            "title": "🇰🇷 SOUTH KOREA: SEOUL STREET KITCHEN",
            "item_name": "Spicy Cheesy Tteokbokki",
            "origin": "Seoul, South Korea 🇰🇷",
            "line": "Chewy, cylindrical rice cakes simmered beautifully in a fiery, sweet gochujang chili sauce, topped with melted mozzarella! 🌶️"
        },
        "thailand_mangorice": {
            "title": "🇹🇭 THAILAND: EXOTIC SIAM TROPICS",
            "item_name": "Sweet Mango Sticky Rice",
            "origin": "Bangkok, Thailand 🇹🇭",
            "line": "Warm glutinous rice cooked in sweet coconut milk, served with fresh, juicy slices of ripened golden mangoes! 🥭"
        },
        "spain_churros": {
            "title": "🇪🇸 SPAIN: MADRID STREET TREAT",
            "item_name": "Crispy Cinnamon Churros Box",
            "origin": "Madrid, Spain 🇪🇸",
            "line": "Golden fried pastry dough dusted beautifully with cinnamon sugar, served with a cup of rich, warm melted milk chocolate! 🍫"
        },
        "usa_waffles": {
            "title": "🇺🇸 USA: CLASSIC DOWNTOWN DINER",
            "item_name": "Loaded Premium Buttermilk Waffles",
            "origin": "New York, USA 🇺🇸",
            "line": "Fluffy, crispy golden waffles topped with sweet maple syrup, a dollop of fresh whipped cream, and wild berries! 🧇"
        }
    }

    selected = menu_data.get(item)
    
    # Elegant embed using native Discord structures to ensure mentions parse into live links
    embed = discord.Embed(
        title=f"👑 ─── {selected['title']} ─── 👑",
        color=discord.Color.from_rgb(245, 238, 227)
    )
    
    # Plain text assignment blocks that natively parse into blue mentions inside Discord clients
    embed.description = (
        f"**👑 International Order Fulfilled!**\n\n"
        f"**🔹 Guest Served:** {member.mention}\n"
        f"**🔹 Gourmet Item:** `{selected['item_name']}`\n"
        f"**🔹 Culinary Origin:** *{selected['origin']}*\n\n"
        f"ℹ️ *{selected['line']}*\n\n"
        f"─── *Enjoy your elite dining experience!* ───"
    )
    
    embed.set_footer(text=f"✨ Stardust Butler System • Order requested by {interaction.user.name}")
    
    content_text = f"🛎️ {member.mention}, you have been served a premium meal!"
    await interaction.followup.send(content=content_text, embed=embed)
    
        
    
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
        data[user_id] = {"balance": 500}  # ✨ Welcome Bonus!
    return data


@bot.tree.command(name="daily", description="🎁 Claim your daily premium Stardust Rewards!")
async def daily(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    data = load_economy()
    data = check_account(user_id, data)
    
    reward = 200
    data[user_id]["balance"] += reward
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
    
# Deploy System Launch Configuration
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: Running operation token string empty.")
