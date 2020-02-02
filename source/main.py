import random, discord
from discord.ext.commands import Bot
# custom database handler
from db import *
from time import sleep
from discord.ext.commands import CommandNotFound



# --------- Info and general informations, and the token encryption thing -----------



"""
INFO :

    this is a discord bot, to be used by players in discord to get informations about their specific things,
     stats etc.

    the discord things (ctx module and all) are from the discord API (import discord)

    the database handler is from db/__init__.py

    (the tiny ascii arts are from http://www.ascii.co.uk/art/ )

"""


"""
encryption bit copied from the internet, it is only to decrypt the token
otherwise people could see the token and run an imposter bot if i forget to delete it when i share the code
"""
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encryptedToken = b'pQ88Unwa617iyMZ0o3vghxrPhyUsvi2o/bKmOCr63Cpiw/2mo927AETjqJ/OdilHCY0c6+Epxsy82a+CXqX1I+YEw79wdMEFky5w+h4SlLI='
password = input("Enter password: ")

def encrypt(raw, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))

def decrypt(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest() ; enc = base64.b64decode(enc) ; iv = enc[:16] ; cipher = AES.new(private_key, AES.MODE_CBC, iv) ; return unpad(cipher.decrypt(enc[16:]))
decrypted = decrypt(encryptedToken, password)



# --------- BOT CODE BELOW -----------



"""

// INIT

"""


# init json handling and discord
db = house_database_handler()
# wow the first staff guy seems really cool, hes probably the best staff, read all the rules and all
staffMembers = ["Kendrik", "Faerix", "TheFlightEnthousiast", "birb", "sad!"]
powerRoles = ["lady", "lord", "mayor", "king", "hand", "house leader"]
BOT_PREFIX = ("\\")
# Oof close your eyes please !
token = decrypted.decode()
client = Bot(command_prefix=BOT_PREFIX)



"""

// GLOBAL THINGS

"""

# when a house controls another one, but didnt merge with it
# below for example at "change", they will be able to choose which house they want to change values for
double_house = {
    "house_berg": "house_cilderhurs",
    "house_gar": "house_dragonovic",
    "house_lancaster": "royal_administration"
}


# hello there
@client.command("listStaff", brief="list staff allowed usery")
async def listStaff(ctx):
    await ctx.send(staffMembers)

# ~~~ er nothing to see here ! move on ~~~
@client.command("gFuel", pass_context=True, brief="nothing to see here", aliases=['69'])
async def listHouse(ctx):
    if (ctx.message.author.name == "birb" or ctx.message.author.name == "Kendrik"):
        await ctx.send("@birb#1435 is the pengest ever -PArAnoiD 2020")

# ~~~ set custom status ~~~
@client.event
async def on_ready():
    activity = discord.Game(name="The Crown of Selenor")
    await client.change_presence(status=discord.Status.online, activity=activity)


# ~~~ list houses ~~~
@client.command("listHouses", pass_context=True, brief="List all houses", aliases=['listhouses', 'list1'])
async def listHouse(ctx):
    try:
        x = db.listHouses()
        await ctx.send(x)
    except:
        await ctx.send("Internal Error. Call Admin")

# ~~~ list users ~~~
@client.command("listUsers", pass_context=True, brief="List all characters", aliases=['listusers', 'list2'])
async def listUser(ctx):
    try:
        x = db.listUsers()
        await ctx.send(x)
    except:
        await ctx.send("Internal Error. Call Admin")

# ~~~ list guilds ~~~
@client.command("listGuilds", pass_context=True, brief="List all guilds", aliases=['listguilds', 'list3'])
async def listUser(ctx):
    try:
        x = db.listGuilds()
        await ctx.send(x)
    except:
        await ctx.send("Internal Error. Call Admin")

# ~~~ list houses ~~~
@client.command("listItems", pass_context=True, brief="List items for your house", aliases=['items', 'list4'])
async def listItems(ctx):
    x, y = db.listItems()
    charArray = ""
    for i in range(len(x)):
        charArray = charArray + ("\n" + "Item " + str(x[i]) + ", price : " + str(y[i]))
    await ctx.send("Here are the available items : \n" + charArray)
    return 0

"""

// USER THINGS

          ___I_
         /\-_--\
        /  \_-__\
        |[]| [] |


"""


# ~~~ recalculate the economy without whole update (see below) which will update the population etc too ~~~
# this could theoritically be removed now
@client.command("recalibrate", pass_context=True, aliases=["fuck"])
async def population(ctx):
    db.recalculate_economy("all")
    await ctx.send("ok")


# ~~~ buy some things in the shop ~~~
@client.command("buy", pass_context=True, aliases=["buyItems", "shop"])
async def buy(ctx, item = None, amount = None):
    # automatically get role of user
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # try to get automatically the house of caller
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            member = memberRoles[i].lower()
    if "house leader" not in memberRoles:
        await ctx.send("Restricted access.")
        return 0
    # if he doesnt specify, just list items
    if item == None:
        x, y = db.listItems()
        charArray = ""
        for i in range(len(x)):
            charArray = charArray + ("\n" + "Item " + str(x[i]) + ", price : " + str(y[i]))
        await ctx.send("Here are the available items : \n" + charArray)
        return 0
    # he can buy more, but first, lets go with 1 by default
    if item != None and amount == None:
        amount = 1

    request = db.buyItem(member, item, amount, "info")
    await ctx.send(request)
    if "error" in request.lower(): return -1
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1

    tryOrFail = db.buyItem(member, item, amount, "normal")
    await ctx.send(tryOrFail)


# ~~~ "\stats" to get information about client house ; "\stats" house_xyz for admin ~~~
@client.command("stats", pass_context=True, aliases=["population"], brief="information about your population")
async def population(ctx, member="error"):
    # automatically get role of user
    print(member)
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # try to get automatically the house of caller
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            member = memberRoles[i].lower()
            print(member)
    try:
        if double_house[member]:
            print(double_house[member])
            await ctx.send("First for " + str(double_house[member]))
            info = db.lookFor(double_house[member])
            await ctx.send(info)
    except:
        pass

    # by default return an error, this is just when staff calls command without precising
    if member == "error":
        await ctx.send("```diff\n- Enter a name too```")
        return "error"
    # obsolete
    if member not in memberRoles and ctx.message.author.name not in staffMembers:
        await ctx.send("goddamnit")
        return 0
    member = member.lower().strip()
    print("looking for ", member)
    info = db.lookFor(member)
    await ctx.send(info)


# ~~~ users have inventory of things they bought~~~
@client.command("inventory", pass_context=True, aliases=["stuff", "backpack"], brief="thats a big backback")
async def population(ctx, house="error"):
    # automatically get role of user
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # try to get automatically the house of caller
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            member = memberRoles[i].lower()

    if ctx.message.author in staffMembers and house=="error":
        await ctx.send("`Use as \\inventory house_name`")
    elif ctx.message.author in staffMembers: member = house

    member = member.lower().strip()
    print("looking inventory for ", member)
    request = db.inventory(member)
    if "empty" in request:
        await ctx.send("`Inventory empty \\-_-/`Buy something !")
        return 0
    itemNames = list(request.keys())
    print(itemNames[0])
    # ey im actually kinda happy that worked !!
    charArray = ""
    for i in range(len(request)):
        charArray = charArray + ("\n" + "Item " + str(itemNames[i].upper()) + ", amount : " + str(request[itemNames[i]]))
    await ctx.send("```\nInventory for house " + member + " : \n" + charArray+"\n```")
    return 0

    await ctx.send(request)


# ~~~ get character info ONLY for users NOT STAFF - staff uses the "\user user nickname" ~~~
@client.command("me", pass_context=True, aliases=["personal"], brief="information about your character")
async def population(ctx, mode="normal", value = None, amount = None):
    member = ctx.message.author.display_name
    member = member.lower().strip()
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    try:
        # check if allowed
        for i in range(len(powerRoles)):
            if powerRoles[i] in ctx.message.author.display_name or "king" in ctx.message.author.display_name:
                power = 1
        for i in range(len(memberRoles)):
            if powerRoles[i] in memberRoles[i].lower() or memberRoles[i].lower() == "house leader":
                print("seems like he is powerful person")
                checkMember = memberRoles[i].lower()
                power = 1
    except:
        pass

    print("looking for ", member)
    print(amount)
    # can change with same command
    if mode == "change" and value != None and amount != None:
        if int(amount) > 3:
            try:
                print(power)
                if int(amount) > 5:
                    await ctx.send("Max 5 guards")
                    return 1
            except:
                await ctx.send("Max 3 guards.")
                return 1

        await ctx.send("```diff\nSure [y/N]```")
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await ctx.send("```\nabort```")
            return 1
        amount = int(amount)
        info = db.lookFor(member, "personal", mode, value, amount)
        await ctx.send(info)
    info = db.lookFor(member, "personal", mode, None, None)
    await ctx.send(str(info))


# ~~~ people can travel ~~~
@client.command("travel", pass_context=True, aliases=["move"], brief="information about your character")
async def population(ctx, *, destination = None):
    member = ctx.message.author.display_name
    member = member.lower().strip()
    if destination == None:
        await ctx.send("`Enter destination \\travel destination`")
    print("looking for ", member)
    print(destination)
    request = db.travel(member, destination)
    await ctx.send(request)
    return 0


# ~~~ get information about your guild if you got one ~~~
@client.command("guild", pass_context=True, aliases=["guildInfo"], brief="information about your guild")
async def population(ctx, guild="error"):
    # look into first function where we use memberRoles to understand
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # automatically get role of user
    for i in range(len(memberRoles)):
        print(memberRoles[i])
        if "guild of " in memberRoles[i]:
            print("ha, gotcha")
            memberRole = memberRoles[i].split()
            print(memberRole)
            member = memberRole[2]
            print(memberRole)

    if ctx.message.author.name in staffMembers:
        member = guild
    if member == "error":
        await ctx.send("Give guild to look for")
        return 1
    print(member)

    info = db.lookFor(member, "guilds", None, None, None)
    await ctx.send(str(info))


# ~~~ houses can send gold to a house or to a guild ~~~
@client.command("send", pass_context=True, aliases=["pay"], brief="send money to house / guild")
async def sendCash(ctx, moneyReceiver="error", amount="error"):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]

    # check if allowed (only house leader)
    for i in range(len(powerRoles)):
        if powerRoles[i] in ctx.message.author.display_name:
            power = 1
    for i in range(len(memberRoles)):
        if memberRoles[i].lower() == "house leader" or memberRoles[i].lower() == "royal_administration":
            print("seems like he is powerful person")
            member = memberRoles[i].lower()
            power = 1
    try:
        print(power)
    except:
        await ctx.send("Restricted access.")
        return 0
    # passed test so lets go
    # automatically get house of user
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("royal_"):
            print("ha, gotcha")
            moneySender = memberRoles[i].lower()
            break
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            moneySender = memberRoles[i].lower()
            break

    try:
        if double_house[moneySender]:
            print(double_house[moneySender])
            await ctx.send("```diff\n- Send money from "+ str(moneySender) + " or " + str(double_house[moneySender]) + " [1/2] :```")
            sleep(0.1)
            houseChoice = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            houseChoice = houseChoice.content.lower().strip()
            if houseChoice != "1" and houseChoice != "2":
                await ctx.send("```\nAborted.```")
                return 1
            elif houseChoice == "2":
                houseRole = double_house[moneySender]
            moneySender = houseRole

            await ctx.send("```Amount```")
            sleep(0.1)
            oneMoreThing = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            amount = oneMoreThing.content.lower().strip()

            await ctx.send("```Receiver```")
            sleep(0.1)
            oneMoreThing = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            moneyReceiver = oneMoreThing.content.lower().strip()

    except:
        pass

    if moneySender == "error" or moneyReceiver == "error" or amount == "error":
        await ctx.send("```diff\n- Error - use the command as\n\\send TO AMOUNT```")
    x = db.listHouses()
    if moneyReceiver not in x:
        mode = "guilds"
    else:
        mode = "houses"
    amount = int(amount)

    #  check again
    await ctx.send("```diff\n- Sending " + str(amount)+ " goldpiece from your house to " + str(moneyReceiver) +".\nConfirm and Checkout ? [y/N]```")
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1
    await ctx.send("```processing request.```")
    try:
        sendMoney = db.sendMoney(moneySender, moneyReceiver, amount, mode)
        await ctx.send(sendMoney)
    except:
        await ctx.send("`Error.`")


# ~~~ update specific stuff, only house leaders tho ~~~
@client.command("change", pass_context=True, aliases=["noOneWillUseThisAliasDummy"], brief="house leader can change taxes and army")
async def singleChange(ctx):
    """
    TODO : make a single function for taxes (syntax \taxes class newTax )
    """
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    try:
        # check if allowed
        for i in range(len(powerRoles)):
            if powerRoles[i] in ctx.message.author.display_name or "king" in ctx.message.author.display_name:
                power = 1
        for i in range(len(memberRoles)):
            if powerRoles[i] in memberRoles[i].lower() or memberRoles[i].lower() == "house leader":
                print("seems like he is powerful person")
                member = memberRoles[i].lower()
                power = 1
        try:
            print(power)
        except:
            await ctx.send("Restricted access.")
            return 0
    except:
        pass

    print(memberRoles)
    ARMY_SALARY = 100 # useless, obsolete ? maybe..

    # automatically get role of user
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            houseRole = memberRoles[i].lower()
    try:
        if double_house[houseRole]:
            print(double_house[houseRole])
            await ctx.send("```diff\n- Change values for "+ str(houseRole) + " or " + str(double_house[houseRole]) + " [1/2] :```")
            sleep(0.1)
            houseChoice = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            houseChoice = houseChoice.content.lower().strip()
            if houseChoice != "1" and houseChoice != "2":
                await ctx.send("```\nAborted.```")
                return 1
            elif houseChoice == "2":
                houseRole = double_house[houseRole]
    except:
        pass

    await ctx.send("```diff\n- Are you sure you want to change values for "+ str(houseRole) + " [y/N] :```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    answer = answer.content.lower().strip()
    if answer != "y" and answer != "yes":
        await ctx.send("```\nAborted.```")
        return 1

    sleep(1)
    await ctx.send("```diff\nWhich value do you want to change ? ['army' ; 'taxes']```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    choice = answer.content.lower().strip()
    if choice not in ['army', 'taxes']:
        await ctx.send("```\nUnknown option. Abort.```")

    if choice.lower() == "army":
        updated = db.changeSpecific(houseRole, "army", 0, 0, "info")#
        await ctx.send("```You can afford maximum " + updated + " troops```")

        sleep(1)
        await ctx.send("```diff\nAmount of : " + choice + "```")
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        try:
            amount = int(answer.content.lower().strip())
        except:
            await ctx.send("hmmm")
            return "error"
        if choice == "army":
            salary = ARMY_SALARY

        # calculate future salary here
        futureSalary = salary * amount
        # inform the sender
        await ctx.send("```diff\nYou're monthly (weekly irl) EXPENSES will grow by\n- " + str(futureSalary) + " gold pieces.\nProceed & checkout ? [y/N]```")
        sleep(0.1)

    elif choice == "taxes":
        salary = 0
        sleep(0.5)
        await ctx.send("```diff\nWhich value do you want to change ? ```\n `lower` or `middle` or `upper` ?")
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        choice = answer.content.strip()
        if "lower" in choice.lower():
            choice = "lowerClassTax"
        elif "middle" in choice.lower():
            choice = "middleClassTax"
        elif "upper" in choice.lower():
            choice = "upperClassTax"
        if choice not in ['lowerClassTax' , 'middleClassTax' , 'upperClassTax']:
            await ctx.send("Error, not found (check capital letters)")
            return -1

        sleep(1)
        await ctx.send("```diff\nNew taxes for : " + choice + " (goldpieces)```")
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        amount = int(answer.content.lower().strip())

        # calculate future salary here
        futureSalary = 0
        # inform the sender
        await ctx.send("```diff\nProceed & checkout ? [y/N]```")
        sleep(0.1)

    #  check again
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, futureSalary)
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)



"""

// GAME THINGS (fights and all)
            Spartians ! Lay down your weapons !
      /| ________________
O|===|* >________________>
      \|

"""



# ~~~ and his name is..... (john cena) ~~~
@client.command("fight", pass_context=True, brief="update user", aliases=['Fight', 'wwe'])
async def updateAll(ctx):
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1
    # init variables
    anotherOne, index, players, playerAttacks = True, -1, [], []

    # get all members in fight
    while anotherOne:
        index += 1
        await ctx.send("```Player " + str(index) + ": name```")
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        if answer.content.lower() in ["abort", "stop"]:
            return -1
        if answer.content.lower() in ["none", "no"]:
            anotherOne == False
            break
        players.append(answer.content.lower())

    # grep all attackStats
    for i in range(len(players)):
        request = (db.grepValue(players[i], "attackStats", "players"))
        print(request)
        playerAttacks.append(int(request))
    # backup, just in case
    rankedStats = playerAttacks

    # custom sort, we sort the attack stats and player list appropriately
    i = -1
    while i <= len(playerAttacks):
      i += 1
      try:
        if rankedStats[i] < rankedStats[i+1]:
          saved = rankedStats[i]
          rankedStats[i] = rankedStats[i+1]
          rankedStats[i+1] = saved

          saved = players[i]
          players[i] = players[i+1]
          players[i+1] = saved

          i = -1
      except:
        pass

    await ctx.send("```Sorted the players : ```" + str(players))



"""

// START OF STAFF ONLY
        GET OFF MY PROPERTY
    ___
 __(   )====::
/~~~~~~~~~\
\O.O.O.O.O/

"""



# ~~~ update all houses (used once per week, changes population etc) ~~~
@client.command("updateAll", pass_context=True, brief="update user", aliases=['updateall', 'all'])
async def updateAll(ctx):
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1
    await ctx.send("```diff\nSure [y/N]```")
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1
    await ctx.send("```processing request.```")
    db.updateAll()
    await ctx.send("hmm. i dont get any wrong response... lets say it worked !")


# ~~~ fully update a specific house (ex to try something, then rollback tho) ~~~
# ~~~ above function in fact loops through all houses with this function (in the db module) ~~~
@client.command("updateHouse", pass_context=True, brief="update ALL houses", aliases=['update', 'updateuser'])
async def updateUser(ctx):
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1
    await ctx.send("Updating Uname :")
    uName = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    uName = uName.content
    returned = db.updateHouse(uName.lower().strip())
    await ctx.send(returned)

# ~~~ update specific stuff ADMIN STUFF ~~~
@client.command("changeHouse", pass_context=True, aliases=["staff1"], brief="staff can update a house")
async def singleStaffChange(ctx, house="error", choice="error", amount="error"):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1

    if house == "error" or choice == "error" or amount == "error":
        await ctx.send("`Use as \\staff1 house_name choice newValue`")

    amount = float(amount)
    #  check again
    await ctx.send("```diff\nSure [y/N]```")
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, 0)
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)


# ~~~ staff change player stats ~~~
@client.command("changePlayer", pass_context=True, aliases=["staff2", "changeUser"], brief="staff can change character stats")
async def singleStaffChange(ctx, choice="error", amount="error"):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1
    if choice == "error" or amount == "error":
        await ctx.send("`Use as \\staff2 choice amount`")
    await ctx.send("player to change :")

    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    houseRole = answer.content.lower().strip()

    if choice != "name" and choice!= "equipment": amount = float(amount)
    else: amount = str(answer.content.lower().strip())
    #  check again
    await ctx.send("```diff\nSure [y/N]```")
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, 0, "players")
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)


# ~~~ init a user ~~~
@client.command("initUser", pass_context=True, brief="create a new player",  aliases=['createUser', 'init_user'])
async def initUser(ctx):
    # only staff can create members
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1

    await ctx.send("NICKNAME of player :")
    uName = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    name = uName.content.lower().strip()
    sleep(0.5)
    await ctx.send("house_ROLE of player :")
    house = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    house = house.content.lower().strip()
    sleep(0.5)
    await ctx.send("Age of player :")
    age = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    age = int(age.content.strip())

    attack = 8
    counterStats = 8
    equipment = "basic sword"
    dexterity = 8
    assassinationCapacity = 8
    guards = 1

    # all setup, check one last time
    await ctx.send("Create user (YES or no)")
    askHim = await client.wait_for('message')
    if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
        # this is a loooot of variables lmao
        db.createUser(name, house, age, attack, counterStats, equipment, dexterity, assassinationCapacity, guards)
        await ctx.send("seems like everything turned out ok.")
    else:
        await ctx.send("aborted")


# ~~~ init a house ~~~
@client.command("initHouse", pass_context=True, brief="create a new house",  aliases=['createHouse', 'init_house'])
async def initHouse(ctx, house_name="error"):
    # only staff can create members
    if ctx.message.author.name not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 1

    if house_name == "error":
        await ctx.send("`Please enter a name too`")
        return 0

    """
        calculating
    """
    # population
    diceResult = db.dice(10, 20)
    population = diceResult * 100

    natality = 5 / 100
    childrenRate = db.dice(1, 10) / 100
    elderlyRate = db.dice(1, 10) / 100
    mortality = 5 / 100
    popularity = 80 / 100

    diceResult = db.dice(1, 20)
    menPart = (diceResult + 40) / 100

    lowerClassRate = db.dice(1, 30) / 100
    upperClassRate = db.dice(1, 6) / 100
    lowerClassTax = 10
    middleClassTax = 10
    upperClassTax = 10
    army = 0
    guildTax, vassalTax, lordTax, knights, squires, guards = 0, 0, 0, 0, 0, 0
    totalGold = 50000

    # calculating the actual amounts out of the rates
    children = int((childrenRate) * population)
    elderly = int((elderlyRate) * population)
    workingPopulation = int(population - children - elderly)
    womenPart = 1 - menPart
    men = int((menPart) * workingPopulation)
    women = int(workingPopulation - men)
    lowerClass = int((lowerClassRate) * workingPopulation)
    upperClass = int((upperClassRate) * workingPopulation)
    middleClass = int(workingPopulation - lowerClass - upperClass)
    income = 0
    expenses = 0

    """
        Processing with the database stuff
    """

    await ctx.send("processing request")

    # all setup, check one last time
    await ctx.send("Create user (YES or no)")
    askHim = await client.wait_for('message')
    if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
        # this is a loooot of variables lmao
        db.createHouse(house_name, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires)
        await ctx.send("seems like everything turned out ok.")
    else:
        await ctx.send("aborted")

# ~~~ see user stats  ~~~
@client.command("user", pass_context=True, brief="get user info",  aliases=['player'])
async def showMe(ctx, *, member="error"):
    print(member)
    if ctx.message.author.name in staffMembers:
        member = member.lower().strip()
    if ctx.message.author.name in staffMembers and member == "error":
        await ctx.send("```diff\n- Enter a name too```")
        return "error"
    elif ctx.message.author.name in staffMembers:
        member = member.lower().strip()
    elif member == "error":
        return "error"

    info = db.lookFor(member, "personal", "normale", None, None)
    await ctx.send(str(info))

# ~~~ see user stats  ~~~
@client.command("merge", pass_context=True, brief="merge two houses (staff only)",  aliases=['fusion'])
async def showMe(ctx, houseFrom = "error", houseTo = "error"):
    print("making an offer,,, they cannot refuse.")
    if ctx.message.author.name not in staffMembers:
        await ctx.send("nope.")
        return 0
    if houseFrom == "error" or houseTo == "error":
        await ctx.send("use as : \\merge house_from house_to")
        return 0

    # you wont be able to come back..
    await ctx.send("```diff\n- Merge "  + str(houseFrom) + " with " + str(houseTo) + " ?\nthis will **permanently** delete " + str(houseFrom) + ". [y/N]```")
    askHim = await client.wait_for('message')
    print(askHim.content)
    if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
        # a soul for a soul..
        returned = db.mergeHouses(houseFrom, houseTo)
        await ctx.send(returned)
        await ctx.send("seems like everything turned out ok.")
    else:
        await ctx.send("aborted")

# grep a specific value
@client.command("grab", pass_context=True, aliases=["grep"])
async def population(ctx, house="error", value="error"):
    if ctx.message.author.name not in staffMembers:
        await ctx.send("nope.")
        return 0
    if house == "error" or value == "error":
        await ctx.send("house and value to grab please")
        return 0
    request = db.grepValue(house, value)
    await ctx.send(request)


# ~~~ grab travelling ~~~
@client.command("history", pass_context=True, aliases=["travellingHistory"], brief="information about your character")
async def population(ctx, *, member = "error"):
    if ctx.message.author.name not in staffMembers:
        member = ctx.message.author.display_name.lower().strip()
    else:
        member = member.lower().strip()
    if member == "error":
        member = "all"
        print("all")
    print("looking for ", member)

    request = db.travelHistory(member)

    await ctx.send(request)
    return 0



"""
                |--------------------------------|
            o --|  filthy russians communists !! |
           \|/  |--------------------------------|
           / \
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ berlin wall be like ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
                |---------------------|
            o --|  тупые американцы ! |
           \|/  |---------------------|
           / \
"""


"""

logbook of the captain : currently listening to nirvana, mtv unplugged
'oh but why you include that in here ?'
well its the end of the code so im free !

"""


# RUN RUN RUN RUN - I CAN BE A BACKPACK WHILE YOU JUMP (seagulls - stop it now !)
print("Starting bot")
client.run(token)
# tada ! line 709 at 11.01.20 lmao
# bruh, 789 now at 18.01.20
# hmm, 30.01.20 - 947 lines
# actually, 1st february : doing a lot of optimization, so - 913 lines ! (nice)
