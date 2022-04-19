import os, discord, sqlite3
from discord.ext import commands
from discord.ext import commands, tasks
from itertools import cycle
import random
import externalfunctions

default_intents = discord.Intents.default()
default_intents.members = True
bot = commands.Bot(command_prefix="_", intents=default_intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    change_status.start()
    rentaloop.start()
    print(">Connecté en tant que:", bot.user.name)
    print(">ID:", bot.user.id)


status = cycle(["by akira#9322", "_help"])


@tasks.loop(seconds=4)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

@tasks.loop(seconds=3600)
async def rentaloop():
    
    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT hashfield FROM fieldsdetails""")
    data = []
    for row in cursor:
        data.append(row[0])
    
    for field in data:

        cursor = conn.cursor()
        cursor.execute("""SELECT rentability, money FROM fieldsdetails WHERE hashfield=?""", (field,))
        data = list(cursor.fetchone())
        renta = int(data[0])
        money = data[1]
        updatedmoney = renta + money

        cursor.execute("""UPDATE fieldsdetails SET money = ? WHERE hashfield=?""", (updatedmoney, field))
        conn.commit()
        cursor.close()

@bot.command()
async def createfield(ctx):

    await ctx.send("Okay, let's create your field...")

    hash = externalfunctions.random_string(16)
    data = (ctx.author.id, hash)

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM users WHERE id=?""", (ctx.author.id,))


    if cursor.fetchone() !=  None:
        
        await ctx.send("Oh, you already have a field !")
        cursor.close()

    else:

        cursor.close()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO users(id, hashfield) VALUES(?, ?)""", data)
        conn.commit()

        cursor.close()

        await ctx.send("Your field has been created. I'll give you a bit of money...")

        data = (hash, 10, 0, 0, 1000, 0, 0, 0, 0)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO fieldsdetails(hashfield, dimension, rentability, bleamount, money, basic_agri, rare_agri, epic_agri, legendary_agri) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
        conn.commit()

        await ctx.send("I add 1000$ to your field's wallet.")
        await ctx.send("Have a good game :)")


@bot.command(pass_context=True)
async def fieldinfo(ctx, user: discord.User=None):

    if user == None:
        user = ctx.author

    await ctx.send("Collecting field's data...")

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM users WHERE id=?""", (ctx.author.id,))


    if cursor.fetchone() !=  None:
        
        await ctx.send("Fetching field's data...")
        cursor.execute("""SELECT hashfield FROM users WHERE id=?""", (user.id,))
        data = cursor.fetchone()
        hashfield = data[0]

        cursor.execute("""SELECT dimension, rentability, bleamount, money, basic_agri, rare_agri, epic_agri, legendary_agri FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
        data = list(cursor.fetchone())
        dicofieldinfo = []
        for i in data:
            dicofieldinfo.append(i)

        embed = discord.Embed(title = "Field info :")
        embed.set_thumbnail(url = user.avatar_url)
        embed.add_field(name = "Dimension :", value = str(dicofieldinfo[0]), inline = True)
        embed.add_field(name = "Rentability :", value = str(dicofieldinfo[1]) + "/hour", inline = True)
        embed.add_field(name = "Wheat amount :", value =  str(dicofieldinfo[2]), inline = True)
        embed.add_field(name = "Money amount :", value =  str(dicofieldinfo[3]), inline = True)
        embed.add_field(name = "Basic agricultor :", value = str(dicofieldinfo[4]), inline = True)
        embed.add_field(name = "Rare agricultor :", value = str(dicofieldinfo[5]), inline = True)
        embed.add_field(name = "Epic agricultor :", value = str(dicofieldinfo[6]), inline = True)
        embed.add_field(name = "Legendary agricultor :", value = str(dicofieldinfo[7]), inline = True)

        await ctx.send(embed = embed)


    else:

        await ctx.send("Look like this user don't have a field. Please use _createfield.")

@bot.command()
async def roll(ctx):

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM users WHERE id=?""", (ctx.author.id,))


    if cursor.fetchone() !=  None:
        
        cursor.execute("""SELECT hashfield FROM users WHERE id=?""", (ctx.author.id,))
        hashfield = cursor.fetchone()[0]

        cursor.execute("""SELECT money FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
        money = cursor.fetchone()[0]

        if money < 500 :
            await ctx.send("You don't have enough money to roll an agricultor.")

        else:

            await ctx.send("Right, let me search an agricultor that would fit good in your field...")
            money = money - 500
            cursor.execute("""UPDATE fieldsdetails SET money = ? WHERE hashfield = ?""", (money, hashfield))
            conn.commit()

            agriList = ["basic", "rare", "epic", "legendary"]
            pickedagri = random.choices(agriList, weights=(70, 20, 10, 5), k=1)[0]


            if pickedagri == "basic" :

                await ctx.send("Alright, you now have a new basic agricultor in your field !")
                cursor.execute("""SELECT basic_agri FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
                basicamount = cursor.fetchone()[0]
                basicamount += 1
                cursor.execute("""UPDATE fieldsdetails SET basic_agri = ? WHERE hashfield = ?""", (basicamount, hashfield))
                conn.commit()

            elif pickedagri == "rare" :

                await ctx.send("Ho ! A brand new rare agricultor for you and your field !")
                cursor.execute("""SELECT rare_agri FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
                rareamount = cursor.fetchone()[0]
                rareamount += 1
                cursor.execute("""UPDATE fieldsdetails SET rare_agri = ? WHERE hashfield = ?""", (rareamount, hashfield))
                conn.commit()

            elif pickedagri == "epic" :

                await ctx.send("Ayo !!! You are lucky today, an epic agricultor join your field !")
                cursor.execute("""SELECT epic_agri FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
                epicamount = cursor.fetchone()[0]
                epicamount += 1
                cursor.execute("""UPDATE fieldsdetails SET epic_agri = ? WHERE hashfield = ?""", (epicamount, hashfield))
                conn.commit()

            elif pickedagri == "legendary" :
                
                await ctx.send("OMFFFGGGG BRO YOU DROP A LEGENDARY AGRICULTOR !!! FBZEGERNYGUISDR")
                cursor.execute("""SELECT legendary_agri FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
                legendaryamount = cursor.fetchone()[0]
                legendaryamount += 1
                cursor.execute("""UPDATE fieldsdetails SET legendary_agri = ? WHERE hashfield = ?""", (legendaryamount, hashfield))
                conn.commit()

            cursor.close()

        externalfunctions.updaterenta(hashfield)

    else:
        await ctx.send("Look like you don't have a field. Please use _createfield.")


@bot.command()
async def upgrade(ctx):

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM users WHERE id=?""", (ctx.author.id,))


    if cursor.fetchone() !=  None:
        
        cursor.execute("""SELECT hashfield FROM users WHERE id=?""", (ctx.author.id,))
        hashfield = cursor.fetchone()[0]
    
        cursor.execute("""SELECT dimension, money FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
        data = list(cursor.fetchone())
        dimension = data[0]
        money = data[1]

        dimensiondico = {10: 0, 25: 10000, 50: 50000, 100: 100000, 200: 300000, 500: 750000, 1000:1500000}
        
        embed = discord.Embed(title = "Upgrades prices :")
        embed.set_thumbnail(url = "https://cdn.icon-icons.com/icons2/2578/PNG/128/upgrade_icon_153946.png")
        embed.add_field(name = "25 :", value = "10 000$", inline = True)
        embed.add_field(name = "50 :", value = "50 000$", inline = True)
        embed.add_field(name = "100 :", value = "100 000$", inline = True)
        embed.add_field(name = "200 :", value = "300 000$", inline = True)
        embed.add_field(name = "500 :", value = "750 000$", inline = True)
        embed.add_field(name = "1000 :", value = "1 500 000$", inline = True)

        await ctx.send(embed = embed)

        message = await ctx.send("Your field's dimension is actually " + str(dimension) + " and you have " + str(money) + "$. Wanna upgrade it ?")

        yas = '✅'
        nay = '❌'
        await message.add_reaction(yas)
        await message.add_reaction(nay)

        valid_reactions = ['✅', '❌']

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == yas:

            await ctx.send("Okay, let's upgrade it !")

            key = dimension
 
            temp = list(dimensiondico)
            try:
                res = temp[temp.index(key) + 1]
            except (ValueError, IndexError):
                res = None

            if money < dimensiondico[res] :

                await ctx.send("You don't have enough money :/")

            else:

                await ctx.send("Upgrading...")

                cursor.execute("""UPDATE fieldsdetails SET dimension = ? WHERE hashfield = ?""", (res, hashfield))
                conn.commit()

                await ctx.send("Done ! Now your field's dimension is " + str(res))
            
            
        else:

            await ctx.send("Upgrade canceled.")

        externalfunctions.updaterenta(hashfield)

    else:

        await ctx.send("Look like you don't have a field. Please use _createfield.")

@bot.command()
async def sell(ctx):

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM users WHERE id=?""", (ctx.author.id,))


    if cursor.fetchone() !=  None:
        
        cursor.execute("""SELECT hashfield FROM users WHERE id=?""", (ctx.author.id,))
        hashfield = cursor.fetchone()[0]
    
        cursor.execute("""SELECT money, bleamount FROM fieldsdetails WHERE hashfield=?""", (hashfield,))
        data = list(cursor.fetchone())
        money = int(data[0])
        wheatamount = int(data[1])

        price = externalfunctions.getwheatprice()

        message = await ctx.send("Actual wheat's price is " + str(price) + "$. Are you sure about your sell ?")

        yas = '✅'
        nay = '❌'
        await message.add_reaction(yas)
        await message.add_reaction(nay)

        valid_reactions = ['✅', '❌']

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == yas:

            updatedmoney = money + (wheatamount*price)

            cursor.execute("""UPDATE fieldsdetails SET money = ? WHERE hashfield=?""", (updatedmoney, hashfield))
            conn.commit()

            wheatamount = 0
            cursor.execute("""UPDATE fieldsdetails SET bleamount = ? WHERE hashfield=?""", (wheatamount, hashfield))
            conn.commit()

            await ctx.send("Done ! I sell all of your wheat for you. You make " + str(updatedmoney-money) + "$ of benefit !")

        else:

            await ctx.send("Sell cancelled.")


    else:
        await ctx.send("Look like you don't have a field. Please use _createfield.")


@bot.command()
async def statsinfo(ctx):

    embed = discord.Embed(title = "Informations :")
    embed.set_thumbnail(url = "https://cdn.icon-icons.com/icons2/38/PNG/512/question_emoticon_5618.png")
    embed.add_field(name = "Agricultor's drop rate :", value = "Basic : 70% | Rare : 30% | Epic : 15% | Legendary : 5%", inline = False)
    embed.add_field(name = "Agricultor's production :", value = "Basic : 1 w/h | Rare : 1,5 w/h | Epic : 2,5 w/h | Legendary : 5 w/h", inline = False)
    embed.add_field(name = "Wheat price :", value = "Wheat price is based on ETH price, divided by 1000 and round down.", inline = False)
    embed.add_field(name = "Rentability :", value = "Rentability = (Basic + Rare*1,5 + Epic*2,5 + Legendary*5) + Dimension", inline = False)

    await ctx.send(embed = embed)

@bot.command()
async def how2start(ctx):

    embed = discord.Embed(title = "How to start :")
    embed.set_thumbnail(url = "https://cdn.icon-icons.com/icons2/38/PNG/512/question_emoticon_5618.png")
    embed.add_field(name = "First create your field : ", value = "```_createfield```", inline = False)
    embed.add_field(name = "You can roll to recruit agricultors and have more production. A roll cost 500$", value = "```_roll```", inline = False)
    embed.add_field(name = "You can trade your wheat amount with $", value = "```_sell```", inline = False)
    embed.add_field(name = "And you can upgrade your field's dimension to have a bigger rentability :", value = "```_upgrade```", inline = False)
    embed.add_field(name = "More info about stats :", value = "```_statsinfo```", inline = False) 

    await ctx.send(embed = embed)

@bot.command()
async def help(ctx):

    hEmbed = discord.Embed(
        title="",
    )
    createf = str("""```\n_createfield\n```""")
    infof = str("""```\n_fieldinfo\n```""")
    rollf = str("""```\n_roll\n```""")
    upgradef = str("""```\n_upgrade\n```""")
    sellf = str("""```\n_sell\n```""")
    statf = str("""```\n_statsinfo\n```""")
    howto = str("""```\n_how2start\n```""")
    h = str("""```\n_help\n```""")
    hEmbed.add_field(name="Create your field", value=createf, inline=False, )
    hEmbed.add_field(name="Get info about your field", value=infof, inline=False, )
    hEmbed.add_field(name="Roll an agricultor. Cost : 500$", value=rollf, inline=False, )  
    hEmbed.add_field(name="Upgrade your field's dimension", value=upgradef, inline=False, )
    hEmbed.add_field(name="Sell all of your wheat", value=sellf, inline=False, )
    hEmbed.add_field(name="Get infos about agricultor's rarity and other details", value=statf, inline=False, )
    hEmbed.add_field(name="Help you to understand how the bot work", value=howto, inline=False, )   
    hEmbed.add_field(name="Show the help pannel", value=h, inline=False, )
    hEmbed.set_footer(text="|      made by akira#9322 [v1.0]     |")
    hEmbed.set_author(
        name="[Help pannel]", icon_url="https://static.thenounproject.com/png/64267-200.png")

    await ctx.send(embed=hEmbed)



bot.run("")

