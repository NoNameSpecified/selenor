import random, discord
from discord.ext.commands import Bot
# custom database handler
from test_db import *
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
db = house_database_handler("database2.json")
# wow the first staff guy seems really cool, hes probably the best staff, read all the rules and all
staffMembers = ["Kendrik", "Faerix", "TheFlightEnthousiast", "birb", "avo"]
powerRoles = ["lady", "lord", "mayor", "king", "hand", "house leader"]
BOT_PREFIX = ("]")
# Oof close your eyes please !
token = "Njc1NjU0ODM4NDk5MDE2NzQ1.Xj_TVw.es6G6netpQPQtVafR9XjMEKVd0U"
worked = "✅"
someError = "❌"
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

async def sendError(error="error", channel="REE"):
    embed=discord.Embed(title="Error.", description=someError + " " + error, color=0xff0000)
    await channel.send(embed=embed)

async def sendRequest(request=" ", channel="REE"):
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    embed=discord.Embed(title="Request", description=request, color=choice(colors))
    await channel.send(embed=embed)

async def sendEmbed(title="Aha", channel="REE"):
    colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
    embed=discord.Embed(title=title, description="...", color=choice(colors))
    await channel.send(embed=embed)

# ~~~ set custom status ~~~
@client.event
async def on_ready():
    activity = discord.Game(name="The Crown of Selenor")
    await client.change_presence(status=discord.Status.online, activity=activity)
    channel = client.get_channel(653291682791555082)

@client.event
async def on_message(message):
    # check if message is for our bot
    if not(message.content.startswith(BOT_PREFIX)): return 0;
    command = message.content.split(BOT_PREFIX)[1].lower().split(" ")

    i = 1
    param = ["None", "None", "None", "None"]
    for i in range(len(command)):
        print(param[i])
        param[i] = command[i]
    print("x", param)
    command = command[0]
    channel = message.channel
    server = message.guild
    nickName = message.author.display_name
    if message.author.name in staffMembers: staff = 1
    else: staff = 0
    # automatically get role of user
    memberRoles = [y.name.lower() for y in message.author.roles]

    power = 0
    if "house leader" in memberRoles: power = 1
    # try to get automatically the house of caller
    for i in range(len(memberRoles)):
        if memberRoles[i].lower().startswith("house_"):
            member = memberRoles[i].lower()

    for i in range(len(memberRoles)):
        if "guild of " in memberRoles[i]:
            print("ha, got guilder")
            guildRole = memberRoles[i].split()
            print(guildRole)
            guild = guildRole[2]
            print(guild)

    print(command)

    if command == "liststaff":
        await channel.send(staffMembers)

    elif command in ["gfuel", "69"]:
        if (message.author.name == "birb" or message.author.name == "Kendrik"):
            await channel.send("@birb#1435 is the pengest ever -PArAnoiD 2020")

    elif command in ["listhouses", "list1"]:
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
        item = param[1] ; amount = param[2]
        if power == 0 : await sendError("House leader only.", channel) ; return 0
        # if he doesnt specify, just list items
        if item == "None":
            items, prices = db.listItems()
            embed = discord.Embed(title="Available items : ", color=0xffffff)
            for i in range(len(request)):
                embed.add_field(name="Item : "+str(items[i].upper()), value="Price : "+str(prices[i]), inline=False)

            await channel.send(embed=embed)
            return 0
        # he can buy more, but first, lets go with 1 by default
        if item != "None" and amount == "None":
            amount = 1

        request = db.buyItem(member, item, amount, "info")
        await channel.send(request)
        if "error" in request.lower(): return -1
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1

        tryOrFail = db.buyItem(member, item, amount, "normal")
        await channel.send(tryOrFail)


    elif command in ["stats", "population"]:
        if staff == 1:
            member = param[1]
        try:
            if double_house[member]:
                print(double_house[member])
                await channel.send("First for " + str(double_house[member]))
                info = db.lookFor(double_house[member])
                await channel.send(info)
        except:
            pass

        # by default return an error, this is just when staff calls command without precising
        if staff == 0 and member == "None":
            await sendError("Enter a name too", channel)
            return "error"
        # obsolete
        member = member.lower().strip()
        print("looking for ", member)
        info = db.lookFor(member)
        await channel.send(info)


    elif command in ["inventory", "stuff", "backpack"]:
        house = param[1]
        print(house)
        if staff == 1 and house=="None":
            await channel.send("`Use as \\inventory house_name`")
        elif staff == 1: member = house

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
            if int(amount) > 3 and not(power):
                await sendError("Max 3 guards.", channel)
                return 1
            if int(amount) > 5 and not("royal_administration" in memberRoles):
                await sendError("Max 5 guards", channel)
                return 1

            await sendRequest("Sure [y/N]", channel)
            answer = await client.wait_for('message', check=lambda response: response.author == message.author)
            yOrNo = answer.content.lower()
            if yOrNo != "y" and yOrNo != "yes":
                await sendError("Abort", channel)
                return 1
            amount = int(amount)
            info = db.lookFor(member, "personal", mode, value, amount)
            await channel.send(info)
        info = db.lookFor(member, "personal", mode, None, None)

        embed = discord.Embed(title="Player "+str(member)+" : ", color=0x1840ee)
        for i in range(len(info[0])):
            embed.add_field(name=str(info[0][i]), value=str(info[1][i]), inline=False)
        await channel.send(embed=embed)
        """
        embed = discord.Embed(title="Stats for "+str(member)+" : ", color=250000)
        for i in range(len(info[0])):
            if info[1][i] == "title":
                embed.add_field(name=str(info[0][i].upper()), value="RE", inline=False)
            else:
                embed.add_field(name=str(info[0][i]), value=str(info[1][i]), inline=True)
        await channel.send(embed=embed)
        """

    elif command in ["travel", "move"]:
        destination = param[1]
        member = nickName.lower().strip()
        if destination == "None":
            await sendRequest("Enter Destionation : ", channel)
            destination = await client.wait_for('message', check=lambda response: response.author == message.author)
            destination = destination.content.lower()

        print("looking for ", member)
        print(destination)
        request = db.travel(member, destination)
        await channel.send(request)
        return 0

    elif command in ["guild", "guildinfo"]:
        guildParam = param[1]
        if guildParam == "None" and guild == "None":
            await sendError("Give guild to look for", channel)
            return 1
        if staff == 1:
            guild = guildParam

        info = db.lookFor(guild, "guilds", "None", "None", "None")
        await channel.send(str(info))

    elif command in ["send", "pay"]:
        if power == 0: await sendError("house leader only.", channel) ; return 0
        moneyReceiver = param[1] ; amount = param[2]
        moneySender = member

        if moneyReceiver == "None" or amount == "None":
            await sendError("Error - use the command as\n\\send TO AMOUNT", channel)
            return -1
        try:
            amount = int(amount)
        except:
            await sendErro("Invalid number", channel)
            return -1

        try:
            if double_house[moneySender]:
                print(double_house[moneySender])
                await sendRequest("Send money from "+ str(moneySender) + " or " + str(double_house[moneySender]) + " [1/2] :", channel)
                sleep(0.1)
                houseChoice = await client.wait_for('message', check=lambda response: response.author == message.author)
                houseChoice = houseChoice.content.lower().strip()
                if houseChoice != "1" and houseChoice != "2":
                    await sendError("Aborted.")
                    return 1
                elif houseChoice == "2":
                    houseRole = double_house[moneySender]
                moneySender = houseRole

                await sendRequest("Amount", channel)
                sleep(0.1)
                oneMoreThing = await client.wait_for('message', check=lambda response: response.author == message.author)
                amount = oneMoreThing.content.lower().strip()

                await sendRequest("Receiver", channel)
                sleep(0.1)
                oneMoreThing = await client.wait_for('message', check=lambda response: response.author == message.author)
                moneyReceiver = oneMoreThing.content.lower().strip()

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
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("Processing request.", channel)
        try:
            sendMoney = db.sendMoney(moneySender, moneyReceiver, amount, mode)
            await sendEmbed(sendMoney, channel)
        except:
            await sendError("Error.", channel)

    elif command in ["change"]:
        if power == 0 : await sendError("House Leaders only.", channel) ; return 0


        print(memberRoles)
        ARMY_SALARY = 100 # useless, obsolete ? maybe..

        try:
            if double_house[houseRole]:
                print(double_house[houseRole])
                await sendRequest("Change values for "+ str(houseRole) + " or " + str(double_house[houseRole]) + " [1/2] :", channel)
                sleep(0.1)
                houseChoice = await client.wait_for('message', check=lambda response: response.author == message.author)
                houseChoice = houseChoice.content.lower().strip()
                if houseChoice != "1" and houseChoice != "2":
                    await sendError("Aborted.")
                    return 1
                elif houseChoice == "2":
                    member = double_house[member]
        except:
            pass

        await sendRequest("Are you sure you want to change values for "+ str(member) + " [y/N] :", channel)
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        answer = answer.content.lower().strip()
        if answer != "y" and answer != "yes":
            await sendError("Aborted.", channel)
            return 1

        sleep(1)
        await sendRequest("Which value do you want to change ? ['army' ; 'taxes']", channel)
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        choice = answer.content.lower().strip()
        if choice not in ['army', 'taxes']:
            await sendError("Unknown option. Abort.", channel)

        if choice.lower() == "army":
            updated = db.changeSpecific(member, "army", 0, 0, "info")#
            await sendEmbed("You can afford maximum " + updated + " troops", channel)

            sleep(1)
            await sendRequest("Amount of : " + choice, channel)
            sleep(0.1)
            answer = await client.wait_for('message', check=lambda response: response.author == message.author)
            try:
                amount = int(answer.content.lower().strip())
            except:
                await sendError("hmmm", channel)
                return "error"
            if choice == "army":
                salary = ARMY_SALARY

            # calculate future salary here
            futureSalary = salary * amount
            # inform the sender
            await sendRequest("You're monthly (weekly irl) EXPENSES will grow by\n- " + str(futureSalary) + " gold pieces.\nProceed & checkout ? [y/N]", channel)
            sleep(0.1)

        elif choice == "taxes":
            salary = 0
            sleep(0.5)
            await sendRequest("Which value do you want to change ? \n lower or middle or upper ?", channel)
            sleep(0.1)
            answer = await client.wait_for('message', check=lambda response: response.author == message.author)
            choice = answer.content.strip()
            if "lower" in choice.lower():
                choice = "lowerClassTax"
            elif "middle" in choice.lower():
                choice = "middleClassTax"
            elif "upper" in choice.lower():
                choice = "upperClassTax"
            if choice not in ['lowerClassTax' , 'middleClassTax' , 'upperClassTax']:
                await sendError("Error, not found (check capital letters)", channel)
                return -1

            sleep(1)
            await sendRequest("New taxes for : " + choice + " (goldpieces)", channel)
            sleep(0.1)
            answer = await client.wait_for('message', check=lambda response: response.author == message.author)
            amount = int(answer.content.lower().strip())

            # calculate future salary here
            futureSalary = 0
            # inform the sender
            await sendRequest("Proceed & checkout ? [y/N]", channel)
            sleep(0.1)

        #  check again
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", channel)
        print("Processing for ", member, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(member, choice, amount, futureSalary)
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
        if staff == 0: await sendError("Staff only.", channel) ; return 0

        await sendRequest("Sure [y/N]", channel)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1

        await sendEmbed("processing request.", channel)
        db.updateAll()
        await channel.send(worked)

    elif command in ["changehouse", "staff1"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0

        houseRole = param[1] ; choice = param[2] ; amount = param[3]

        if houseRole == "None" or choice == "None" or amount == "None":
            await sendError("Use as \\staff1 house_name choice newValue", channel)
            return 0

        amount = float(amount)
        #  check again
        await sendRequest("Sure [y/N]", channel)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", channel)
        print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(houseRole, choice, amount, 0)
        # and its all done ! lets inform the user
        # // or if there was an error returned, send error message
        await channel.send(updated)

    elif command in ["changeplayer", "changeuser", "staff2"]:
        if staff == 0: await sendError("Staff only", channel) ; return 0

        await sendRequest("player to change :", channel)
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        houseRole = answer.content.lower().strip()
        await sendRequest("value to change :", channel)
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        choice = answer.content.lower().strip()
        await sendRequest("new value :", channel)
        sleep(0.1)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        amount = answer.content.lower().strip()
        if choice != "name" and choice!= "equipment": amount = float(amount)
        else: amount = str(answer.content.lower().strip())
        #  check again
        await sendRequest("Sure [y/N]", channel)
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
        yOrNo = answer.content.lower()
        if yOrNo != "y" and yOrNo != "yes":
            await sendError("Abort.", channel)
            return 1
        await sendEmbed("processing request.", channel)
        print("Processing for ", houseRole, "\nWants to change ", choice, ", ", amount)
        # use the database handler
        updated = db.changeSpecific(houseRole, choice, amount, 0, "players")
        # and its all done ! lets inform the user
        # // or if there was an error returned, send error message
        await channel.send(updated)

    elif command in ["inituser", "init_user", "init2"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0

        await sendRequest("NICKNAME of player :", channel)
        uName = await client.wait_for('message', check=lambda response: response.author == message.author)
        name = uName.content.lower().strip()
        sleep(0.5)
        await sendRequest("house_ROLE of player :", channel)
        house = await client.wait_for('message', check=lambda response: response.author == message.author)
        house = house.content.lower().strip()
        sleep(0.5)
        await sendRequest("Age of player :", channel)
        age = await client.wait_for('message', check=lambda response: response.author == message.author)
        age = int(age.content.strip())

        attack = 8
        counterStats = 8
        equipment = "basic sword"
        dexterity = 8
        assassinationCapacity = 8
        guards = 1

        # all setup, check one last time
        await sendRequest("Create user (YES or no)", channel)
        askHim = await client.wait_for('message', check=lambda response: response.author == message.author)
        if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
            # this is a loooot of variables lmao
            db.createUser(name, house, age, attack, counterStats, equipment, dexterity, assassinationCapacity, guards)
            await channel.send(worked)
        else:
            await sendError("aborted", channel)

    elif command in ["inithouse", "init_house", "init1"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0

        house_name = param[1]

        if house_name == "None":
            await sendError("Please enter a name too", channel)
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

        await sendEmbed("processing request", channel)

        # all setup, check one last time
        await sendRequest("Create user (YES or no)", channel)
        askHim = await client.wait_for('message', check=lambda response: response.author == message.author)
        if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
            # this is a loooot of variables lmao
            db.createHouse(house_name, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires)

            # we have created the house values
            # now we create the channels
            await server.create_category(house_name)
            await server.create_role(name=house_name)

            newCategory = discord.utils.get(server.categories, name=house_name)
            newHouseRole = discord.utils.get(server.roles, name=house_name)

            houseChannelName = house_name.split("_")

            await server.create_text_channel( houseChannelName[0] + "-" + houseChannelName[1] + "-general", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[0] + "-" + houseChannelName[1] + "-general")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)

            await server.create_text_channel( houseChannelName[1] + "-map", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[1] + "-map")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)

            await server.create_text_channel( houseChannelName[1] + "-administration", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[1] + "-administration")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)

            await server.create_text_channel( houseChannelName[1] + "-rp", category=newCategory)
            newChannel = discord.utils.get(server.channels, name=houseChannelName[1] + "-rp")
            await newChannel.set_permissions(server.default_role, read_messages=False, send_messages=False)
            await newChannel.set_permissions(newHouseRole, read_messages=True, send_messages=True)

            await channel.send(worked)

        else:
            await sendError("aborted", channel)

    elif command in ["user", "player"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0
        print("ree")
        await sendRequest("User to look up : ", channel)
        print("RE")
        user = await client.wait_for('message', check=lambda response: response.author == message.author)
        user = user.content.lower().strip()
        print(user)
        info = db.lookFor(user, "personal", "normal", None, None)
        embed = discord.Embed(title="Player "+str(user)+" : ", color=0x1840ee)
        for i in range(len(info[0])):
            embed.add_field(name=str(info[0][i]), value=str(info[1][i]), inline=False)
        await channel.send(embed=embed)

    elif command in ["merge"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0

        houseFrom = param[1] ; houseTo = param[2]
        if houseFrom == "None" or houseTo == "None":
            await sendError("use as : \\merge house_from house_to", channel)
            return 0

        # you wont be able to come back..
        await sendError("Merge "  + str(houseFrom) + " with " + str(houseTo) + " ?\nthis will **permanently** delete " + str(houseFrom) + ". [y/N]", channel)
        askHim = await client.wait_for('message', check=lambda response: response.author == message.author)
        print(askHim.content)
        if askHim.content.lower().strip() == "yes" or askHim.content.lower().strip() == "y":
            # a soul for a soul..
            returned = db.mergeHouses(houseFrom, houseTo)
            await channel.send(returned)
            await channel.send(worked)
        else:
            await sendError("aborted", channel)

    elif command in ["grep", "grab"]:
        if staff == 0: await sendError("Staff only.", channel) ; return 0
        print(param[1])
        house = param[1] ; value = param[2]
        request = db.grepValue(house, value)
        await channel.send(request)

    elif command in ["history"]:
        if staff == 0:
            request = db.travelHistory(nickName)
            await channel.send(request)
            return 0

        await sendRequest("User : (all for all)", channel)
        user = await client.wait_for('message', check=lambda response: response.author == message.author)
        user = user.content.lower()

        # if user == "all" : handle for all users

        request = db.travelHistory(user)
        await channel.send(request)
        return 0

    elif command in ["man", "manual", "help"]:
        category = param[1]
        if param[1] == "None":
            embed=discord.Embed(title="Manual", description="Command Table :", color=0xdd7b28)
            embed.add_field(name="General : ", value="General commands, lists etc\n--> "+BOT_PREFIX+"man general", inline=False)
            embed.add_field(name="Game : ", value="House and Players related\n--> "+BOT_PREFIX+"man game", inline=False)
            embed.add_field(name="Staff : ", value="Staff related\n--> "+BOT_PREFIX+"man staff", inline=False)
        elif param[1].lower() == "general":
            embed=discord.Embed(title="Manual", description="Category General :", color=0xc5bcc5)
            embed.add_field(name=BOT_PREFIX+"listStaff", value="List Staff\nAliases : "+BOT_PREFIX+"None", inline=False)
            embed.add_field(name=BOT_PREFIX+"listHouses", value="List Houses\nAliases : "+BOT_PREFIX+"list1", inline=False)
            embed.add_field(name=BOT_PREFIX+"listPlayers", value="List Players\nAliases : "+BOT_PREFIX+"list2", inline=False)
            embed.add_field(name=BOT_PREFIX+"listGuilds", value="List Guilds\nAliases : "+BOT_PREFIX+"list3", inline=False)
            embed.add_field(name=BOT_PREFIX+"items", value="List items and prices in shop\nAliases : "+BOT_PREFIX+"list4", inline=False)

        elif param[1].lower() == "game":
            embed=discord.Embed(title="Manual", description="Category Game :", color=0x8ae1c2)
            embed.add_field(name=BOT_PREFIX+"buy CHOICE AMOUNT", value="HOUSE LEADER ONLY\nBuy things from the inventory\nAliases : "+BOT_PREFIX+"shop", inline=False)
            embed.add_field(name=BOT_PREFIX+"send HOUSE_TO AMOUNT", value="HOUSE LEADER ONLY\nSend money to another house\nAliases : "+BOT_PREFIX+"pay", inline=False)
            embed.add_field(name=BOT_PREFIX+"change", value="HOUSE LEADER ONLY\nChange taxes and army\nAliases : "+BOT_PREFIX+"None", inline=False)
            embed.add_field(name=BOT_PREFIX+"stats", value="Detailed statistics of your house\nAliases : "+BOT_PREFIX+"populatin", inline=False)
            embed.add_field(name=BOT_PREFIX+"inventory", value="List items you bought\nAliases : "+BOT_PREFIX+"stuff", inline=False)
            embed.add_field(name=BOT_PREFIX+"me ( change guards AMOUNT(max3 or 5 for house leader) )", value="Details about your character and change guards\nAliases : "+BOT_PREFIX+"personal", inline=False)
            embed.add_field(name=BOT_PREFIX+"travel", value="Log your travel for staff\nAliases : "+BOT_PREFIX+"move", inline=False)

            embed.add_field(name=BOT_PREFIX+"guild", value="GUILD MEMBERS ONLY\nAliases : "+BOT_PREFIX+"guildInfo", inline=False)

        elif param[1].lower() == "staff":
            embed=discord.Embed(title="Manual", description="Category Staff :", color=0xffffff)
            embed.add_field(name=BOT_PREFIX+"init_house HOUSE_NAME", value="Create a new house\nAliases : "+BOT_PREFIX+"init1", inline=False)
            embed.add_field(name=BOT_PREFIX+"init_user", value="Create  a new User\nAliases : "+BOT_PREFIX+"init2", inline=False)
            embed.add_field(name=BOT_PREFIX+"user", value="Get Statistics of User\nAliases : "+BOT_PREFIX+"player", inline=False)
            embed.add_field(name=BOT_PREFIX+"grep HOUSE_NAME VALUE", value="Grab a specific value\nAliases : "+BOT_PREFIX+"grab", inline=False)
            embed.add_field(name=BOT_PREFIX+"recalibrate", value="Recalibrate and recalculate economy section\nAliases : "+BOT_PREFIX+"fuck", inline=False)
            embed.add_field(name=BOT_PREFIX+"update", value="Update all houses and players\nAliases : "+BOT_PREFIX+"None", inline=False)
            embed.add_field(name=BOT_PREFIX+"recalibrate", value="Recalibrate and recalculate economy section\nAliases : "+BOT_PREFIX+"fuck", inline=False)
            embed.add_field(name=BOT_PREFIX+"merge HOUSE_FROM HOUSE_TO", value="Merge two houses\nAliases : "+BOT_PREFIX+"None", inline=False)
            embed.add_field(name=BOT_PREFIX+"changeHouse HOUSE_NAME VALUE NEWVALUE", value="Change house value\nAliases : "+BOT_PREFIX+"staff1", inline=False)
            embed.add_field(name=BOT_PREFIX+"changePlayer", value="Change Player value\nAliases : "+BOT_PREFIX+"staff2", inline=False)

        else:
            await sendError("No Manual Entry.", channel)
            return 0

        await channel.send(embed=embed)

    # everything failed
    else:
        await sendError("Command not found, Use "+BOT_PREFIX+"man/manual to get help", channel)



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
    if message.author.name not in staffMembers:
        await sendError("Hey ! Dont do this if you arent staff", channel)
        return 1
    # init variables
    anotherOne, index, players, playerAttacks = True, -1, [], []

    # get all members in fight
    while anotherOne:
        index += 1
        await channel.send("```Player " + str(index) + ": name```")
        answer = await client.wait_for('message', check=lambda response: response.author == message.author)
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

    await channel.send("```Sorted the players : ```" + str(players))
