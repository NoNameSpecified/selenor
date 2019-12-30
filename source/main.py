import random, discord
from discord.ext.commands import Bot
from time import sleep

# for this, it is the file in the db folder ( __init__.py )
from db import *

"""
copied  from the internet, just to decrypt the token
"""
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encryptedToken = b'eUJhYc3woIJkgskY3BAKhxaTQ2GcN7xR8vc2vnJT57gKa48aqejeapPi9dGXwnEc0J29hFkP1I9YdfrEW21KnxX3Mn5O9IYDEX2cvu8qTng='
password = input("Enter password: ")

def decrypt(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest() ; enc = base64.b64decode(enc) ; iv = enc[:16] ; cipher = AES.new(private_key, AES.MODE_CBC, iv) ; return unpad(cipher.decrypt(enc[16:]))
decrypted = decrypt(encryptedToken, password)

"""

// INIT

"""

# init json handling and discord
db = house_database_handler()
staffMembers = ["Kendrik", "felix.rnd", "TheFlightEnthousiast"]
BOT_PREFIX = ("\\")
# Oof close your eyes please !
token = decrypted.decode()
client = Bot(command_prefix=BOT_PREFIX)




"""

// GLOBAL THINGS

"""

async def check_if_staff(uName):
    if uName not in staffMembers:
        await ctx.send("```diff\n- Hey ! Dont do this if you arent staff```")
        return 0

async def yes_or_no_check():
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    yOrNo = answer.content.lower()
    if yOrNo != "y" and yOrNo != "yes":
        await ctx.send("```\nabort```")
        return 1

# ~~~ custom status ~~~
@client.event
async def on_ready():
    activity = discord.Game(name="The Crown of Selenor")
    await client.change_presence(status=discord.Status.idle, activity=activity)

# ~~~ list houses ~~~
@client.command("listHouses", pass_context=True, brief="List all users", aliases=['listhouses', 'list1'])
async def listHouse(ctx):
    try:
        x = db.listHouses()
        await ctx.send(x)
    except:
        await ctx.send("Internal Error. Call Admin")

# ~~~ list users ~~~
@client.command("listUsers", pass_context=True, brief="List all users", aliases=['listusers', 'list2'])
async def listUser(ctx):
    try:
        x = db.listUsers()
        await ctx.send(x)
    except:
        await ctx.send("Internal Error. Call Admin")

"""

// USER THINGSParanoid Staff

"""

# ~~~ get information about the population of someone ~~~
@client.command("fuck", pass_context=True)
async def population(ctx):
    db.recalculate_economy("all")
    await ctx.send("ok")

# ~~~ get information about the population of someone ~~~
@client.command("stats", pass_context=True, description="get some info", aliases=["population"], brief="information about your population")
async def population(ctx, member="error"):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # automatically get role of user
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            member = memberRoles[i].lower()
    if "royal_administration" in memberRoles:
        member = "royal_administration"
    if member == "error":
        await ctx.send("```diff\n- Enter a name too```")
        return "error"
    if member not in memberRoles and ctx.message.author.name not in staffMembers:
        await ctx.send("goddamnit")
        return 0
    member = member.lower().strip()
    print("looking for ", member)
    info = db.lookFor(member)
    await ctx.send(info)


# ~~~ get information about the population of yourself ~~~
@client.command("me", pass_context=True, description="get some info", aliases=["personal"], brief="information about your character")
async def population(ctx, mode="normal", value = None, amount = None):
    member = ctx.message.author.display_name
    member = member.lower().strip()
    print("looking for ", member)
    # can change with same command
    if mode == "change" and value != None and amount != None:
        await ctx.send("```diff\nSure [y/N]```")
        answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await ctx.send("```\nabort```")
            return 1
        info = db.lookFor(member, "personal", mode, value, amount)
        await ctx.send(info)
    else:
        info = db.lookFor(member, "personal", mode, None, None)
        await ctx.send(str(info))


# ~~~ update specific stuff ~~~
@client.command("send", pass_context=True, description="change single stuff", aliases=["pay"], brief="send money")
async def singleChange(ctx, moneyReceiver="error", amount="error"):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    # automatically get role of user
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            print("ha, gotcha")
            moneySender = memberRoles[i].lower()
    if moneySender == "error" or moneyReceiver == "error" or amount == "error":
        await ctx.send("```diff\n- Error - use the command as\n\\send TO AMOUNT```")
    amount = int(amount)

    #  check again
    await ctx.send("```diff\n- Sending " + str(amount)+ " goldpiece from your house to " + str(moneyReceiver) +".\nConfirm and Checkout ? [y/N]```")
    yes_or_no_check()
    await ctx.send("```processing request.```")
    try:
        sendMoney = db.sendMoney(moneySender, moneyReceiver, amount)
        await ctx.send(sendMoney)
    except:
        await ctx.send("`Error.`")



# ~~~ update specific stuff ~~~
@client.command("change", pass_context=True, description="change single stuff", aliases=["bruv"], brief="who will ever look for this ?")
async def singleChange(ctx):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    print(memberRoles)
    MAX_KNIGHTS = 15
    MAX_GUARDS = 100
    KNIGHTS_SALARY = 15000
    GUARDS_SALARIY = 15000
    ARMY_SALARY = 100

    # automatically get role of user
    if "royal_administration" in memberRoles:
        houseRole = "royal_administration"
    else:
        for i in range(len(memberRoles)):
            if memberRoles[i].lower().startswith("house_"):
                print("ha, gotcha")
                houseRole = memberRoles[i].lower()
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
        amount = int(answer.content.lower().strip())
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
    yes_or_no_check()
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, futureSalary)
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ berlin wall be like ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""

// START OF STAFF ONLY

"""



# ~~~ update all houses ~~~
@client.command("updateAll", pass_context=True, brief="update user", aliases=['updateall', 'all'])
async def updateAll(ctx):
    check_if_staff(ctx.message.author.name)
    await ctx.send("```diff\nSure [y/N]```")
    yes_or_no_check()
    await ctx.send("```processing request.```")
    db.updateAll()

# ~~~ fully update a specific house ~~~
@client.command("updateHouse", pass_context=True, brief="update user", aliases=['update', 'updateuser'])
async def updateUser(ctx):
    check_if_staff(ctx.message.author.name)
    await ctx.send("Updating Uname :")
    uName = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    uName = uName.content
    returned = db.updateHouse(uName.lower().strip())
    await ctx.send(returned)

# ~~~ update specific stuff ADMIN STUFF ~~~
@client.command("changeHouse", pass_context=True, description="only staff", aliases=["staff1"], brief="who will ever look for this ?")
async def singleStaffChange(ctx):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    check_if_staff(ctx.message.author.name)
    await ctx.send("House to change :")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    houseRole = answer.content.lower().strip()
    sleep(1)
    await ctx.send("```diff\nWhich value do you want to change ?```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    choice = answer.content.strip()
    sleep(1)
    await ctx.send("```diff\nNew Value : ```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    amount = float(answer.content.lower().strip())
    #  check again
    await ctx.send("```diff\nSure [y/N]```")
    yes_or_no_check()
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, 0)
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)


# ~~~ staff change player stats ~~~
@client.command("changePlayer", pass_context=True, description="only staff", aliases=["staff2", "changeUser"], brief="who will ever look for this ?")
async def singleStaffChange(ctx):
    memberRoles = [y.name.lower() for y in ctx.message.author.roles]
    check_if_staff(ctx.message.author.name)
    await ctx.send("player to change :")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    houseRole = answer.content.lower().strip()
    sleep(1)
    await ctx.send("```diff\nWhich value do you want to change ?```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    choice = answer.content.strip()
    sleep(1)
    await ctx.send("```diff\nNew Value : ```")
    sleep(0.1)
    answer = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    amount = float(answer.content.lower().strip())
    #  check again
    await ctx.send("```diff\nSure [y/N]```")
    yes_or_no_check()
    await ctx.send("```processing request.```")
    print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
    # use the database handler
    updated = db.changeSpecific(houseRole, choice, amount, 0, "players")
    # and its all done ! lets inform the user
    # // or if there was an error returned, send error message
    await ctx.send(updated)

# ~~~ init a user ~~~
@client.command("init_user", pass_context=True, brief="create a new player",  aliases=['create', 'createUser'])
async def initUser(ctx):
    # only staff can create members
    check_if_staff(ctx.message.author.name)

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
    sleep(0.5)
    await ctx.send("attackStats of player :")
    attack = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    attack = int(attack.content.strip())
    sleep(0.5)
    await ctx.send("counterStats of player :")
    counterStats = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    counterStats = int(counterStats.content.strip())
    sleep(0.5)
    await ctx.send("equipment of player :")
    equipment = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    equipment = str(equipment.content.strip())
    sleep(0.5)
    await ctx.send("dexterity of player :")
    dexterity = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    dexterity = int(dexterity.content.strip())
    sleep(0.5)
    await ctx.send("assassinationCapacity of player :")
    assassinationCapacity = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    assassinationCapacity = int(assassinationCapacity.content.strip())
    sleep(0.5)
    await ctx.send("guards of player :")
    guards = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    guards = int(guards.content.strip())
    sleep(0.5)

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
@client.command("init", pass_context=True, brief="create a new house",  aliases=['createHouse'])
async def initHouse(ctx):
    # only staff can create members
    check_if_staff(ctx.message.author.name)



    """
        Asking all the stuff
    """

    await ctx.send("new user name :")
    uName = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("user population")
    population = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("user natality in %")
    natality = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("children rate in %")
    childrenRate = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("elderly rate in %")
    elderlyRate = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("mortality rate in %")
    mortality = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("popularity in %")
    popularity = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Men rate in %")
    menPart = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Lower class rate in %")
    lowerClassRate = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Upper class rate in %")
    upperClassRate = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Lower Class tax - int")
    lowerClassTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Middle Class tax - int")
    middleClassTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Upper Class tax - int")
    upperClassTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Initial Army - int")
    army = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Guild Tax - int")
    guildTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Vassal Tax - int")
    vassalTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Lord Tax - int")
    lordTax = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Initial Gold - int")
    totalGold = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Number of knights - int")
    knights = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Number of guards - int")
    guards = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)
    await ctx.send("Number of squires - int")
    squires = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    sleep(1)

    """
        Converting all the stuff, precalculating a bit
    """

    uName = uName.content.strip()
    population = int(population.content)
    natality = float(natality.content) / 100
    childrenRate = float(childrenRate.content) / 100
    elderlyRate = float(elderlyRate.content) / 100
    mortality = float(mortality.content) / 100
    popularity = float(popularity.content) / 100
    children = int((childrenRate) * population)
    elderly = int((elderlyRate) * population)
    workingPopulation = int(population - children - elderly)
    menPart = float(menPart.content) / 100
    womenPart = 1 - menPart
    men = int((menPart) * workingPopulation)
    women = int(workingPopulation - men)
    lowerClassRate = float(lowerClassRate.content) / 100
    upperClassRate = float(upperClassRate.content) / 100
    lowerClassTax = float(lowerClassTax.content)
    middleClassTax = float(middleClassTax.content)
    upperClassTax = float(upperClassTax.content)
    lowerClass = int((lowerClassRate) * workingPopulation)
    upperClass = int((upperClassRate) * workingPopulation)
    middleClass = int(workingPopulation - lowerClass - upperClass)
    army = int(army.content)
    guildTax = float(guildTax.content)
    vassalTax = float(vassalTax.content)
    lordTax = float(lordTax.content )
    income = 0
    expenses = 0
    totalGold = float(totalGold.content)
    knights = int(knights.content)
    guards = int(guards.content)
    squires = int(squires.content)

    """
        Processing with the database stuff
    """

    await ctx.send("processing request")
    sleep(4) # yes, this is useless and only to be like "oh we re making complicated stuff" xDD

    # all setup, check one last time
    await ctx.send("Create user (YES or no)")
    askHim = await client.wait_for('message')
    if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
        # this is a loooot of variables lmao
        db.createHouse(uName, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires)
        await ctx.send("seems like everything turned out ok.")
    else:
        await ctx.send("aborted")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ berlin wall be like ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

# all set up ! we can go !

"""


# RUN RUN RUN RUN - I CAN BE A BACKPACK WHILE YOU JUMP (seagulls - stop it now !)
print("LETS GO")
client.run(token)
