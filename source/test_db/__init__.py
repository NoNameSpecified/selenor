import json
import os, time
import random
from datetime import datetime


"""

    this is quite messy, and seems long, but dw, it's just that there is a lot of data
        and variables to manage everytime we change something

"""


# actually the name isnt right,
# first it was suppsoed to handle houses, then another one the players etc..
# but that would be overkill, so lets go with the messy version !
class house_database_handler:
    def __init__(self, pathToJson="database.json"):
        self.pathToJson = pathToJson

        # check if file is created |-> else let's create it
        if os.path.exists(pathToJson) == False:
            open(self.pathToJson, "w")
        try:
            with open(self.pathToJson) as db:
                self.jsonContent = json.load(db)
        except:
            pass # and fuck it
        rates_file = open("rates.json", "r")

        # these are the rates that are used everywhere, and wont be changed normally
        rate = json.load(rates_file)
        self.guardsSalary = rate["rates"]["guardsSalary"]
        self.knightsSalary = rate["rates"]["knightsSalary"]
        self.armySalary = rate["rates"]["armySalary"]
        self.lowerClassTaxMax = rate["rates"]["lowerClassTaxMax"]
        self.middleClassTaxMax = rate["rates"]["middleClassTaxMax"]
        self.upperClassTaxMax = rate["rates"]["upperClassTaxMax"]
        self.houseTax = rate["rates"]["queen-fucking-high-taxes"]
        # shop, also in rates.json
        self.port = rate["shop"]["port"]
        self.city = rate["shop"]["city"]
        self.boat = rate["shop"]["boat"]
        self.road = rate["shop"]["road"]
        self.bridge = rate["shop"]["bridge"]
        self.temple = rate["shop"]["temple"]
        self.school = rate["shop"]["school"]

        self.shop = {
            "port": self.port,
            "city": self.city,
            "boat": self.boat,
            "road": self.road,
            "bridge": self.bridge,
            "temple": self.temple,
            "school": self.school
        }

    # in the selenor game, we calculated everything with dices, i.e for example !roll 10d20*100 for population etc
    def dice(self, numberOfDices, diceFaces):
        result = diceFaces/2
        for i in range(numberOfDices+1):
            result = result + random.randint(1, diceFaces)
        return int(result)

    # logs, for logs..
    def log(self, content):
        now = datetime.now()
        dateAndTime = now.strftime("%d/%m/%Y %H:%M:%S")
        logFile = open("logs.txt", "a")
        logFile.write(dateAndTime+" : " + content + "\n")
        logFile.close()
        return 0

    # used after changing the json, to overwrite the database
    def overwrite_json_db(self, content):
        self.json_db = open(self.pathToJson, "w")
        self.perfectionJson = json.dumps(content, indent=4, separators=(',', ': '))
        self.json_db.write(self.perfectionJson)
        self.json_db.close()

    # houses are only marked with nametags, from which we must find the correct index
    def find_index_in_db(self, dataToFindIn, userNameToFind):
        for i in range(len(dataToFindIn)):
            if dataToFindIn[i]["name"].lower() == userNameToFind.lower():
                return int(i)
        # as we return a string the program will abort
        print("failed at ", userNameToFind)
        return "nope"

    # to get a list with all users.
    # can be used either for the user, or in this module
    def listHouses(self):
        with open(self.pathToJson, "r") as db:
            data = json.load(db) ; x = [data["houses"][i]["name"] for i in range(len(data["houses"]))] ; return x
    def listUsers(self):
        with open(self.pathToJson, "r") as db:
            data = json.load(db) ; x = [data["players"][i]["name"] for i in range(len(data["players"]))] ; return x
    def listGuilds(self):
        with open(self.pathToJson, "r") as db:
            data = json.load(db) ; x = [data["guilds"][i]["name"] for i in range(len(data["guilds"]))] ; return x
    def listItems(self):
        with open("rates.json", "r") as db:
            y = []
            data = json.load(db) ; x = [key for key, value in data["shop"].items()]
            for i in range(len(x)):
                name = x[i]
                y.append(data["shop"][name])
            return x,y

    # merge two houses, e.g if one took over the other
    def mergeHouses(self, houseFrom, houseTo):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            indexFrom = self.find_index_in_db(data["houses"], houseFrom)
            indexTo = self.find_index_in_db(data["houses"], houseTo)
            # give population and gold.
            # the other values will be recalculated
            data["houses"][indexTo]["population"] = int(data["houses"][indexTo]["population"]) + int(data["houses"][indexFrom]["population"])
            data["houses"][indexTo]["totalGold"] = int(data["houses"][indexTo]["totalGold"]) + int(data["houses"][indexFrom]["totalGold"])
            # mark as inactive in the db, dont delete it (coz u never know)
            data["houses"][indexFrom]["active"] = "False"
            self.log("Merged house " + str(houseFrom) + " with " + str(houseTo))
            self.overwrite_json_db(data)
        return "Merged."

    # uses below function, updates all houses by looping through them
    def updateAll(self):
        x = self.listHouses()
        for house in x:
            self.updateHouse(house)
            self.taxes(house, "royal_administration")

        print("\n\n\nUPDATE FINISHED HOUSES\n\n\n")
        x = self.listUsers()
        for player in x:
            self.updatePlayer(player)
        print("\n\n\nUPDATE FINISHED PLAYERS\n\n\n")
        self.log("Updated all houses and players and paid taxes.")
        return "All users have been updated"


    # pay from house to house
    def sendMoney(self, sender, receiver, amount, mode):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            receiver = receiver.lower()
            senderIndex = self.find_index_in_db(data["houses"], sender)
            if mode == "houses":
                receiverIndex = self.find_index_in_db(data["houses"], receiver)
            elif mode == "guilds":
                receiverIndex = self.find_index_in_db(data["guilds"], receiver)
            else:
                return "error"

            data["houses"][senderIndex]["totalGold"] = data["houses"][senderIndex]["totalGold"] - amount
            data[mode][receiverIndex]["totalGold"] = data[mode][receiverIndex]["totalGold"] + amount
            self.log("House " +str(sender) + " sent " +str(receiver) + " " + str(amount) + " goldpieces")
            # finish, write, close
            self.overwrite_json_db(data)
            return "`Sent the CA$H`"

    # pay em bills
    def taxes(self, house, IRS):
        houses = [house]
        if house == "all":
            houses = self.listHouses()
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            for house in range(len(houses)):
                senderIndex = self.find_index_in_db(data["houses"], houses[house])
                receiverIndex = self.find_index_in_db(data["houses"], IRS)

                if data["houses"][senderIndex]["nettoIncome"] > 100:
                    amount = data["houses"][senderIndex]["nettoIncome"] * self.houseTax
                else:
                    amount = 0

                data["houses"][senderIndex]["totalGold"] = data["houses"][senderIndex]["totalGold"] - amount
                data["houses"][receiverIndex]["totalGold"] = data["houses"][receiverIndex]["totalGold"] + amount
            # finish, write, close
            self.overwrite_json_db(data)
            return "paid "+str(amount)

    #  houses can buy stuff
    def buyItem(self, house, item, amount, mode="normal"):
        with open(self.pathToJson, "r") as db:
            amount = int(amount)
            data = json.load(db)
            houseName = house
            house = self.find_index_in_db(data["houses"], house)
            items, prices = self.listItems()
            if item not in items:
                return "```Error. Did not found item (list items with \\buy)```"

            try:
                price = self.shop[item]
            except:
                return "```Error. Did not found item (list items with \\buy)```"

            totalPrice = price * amount

            if mode == "info":
                return "`Buying " + str(amount) + " " + str(item) + " for " + str(totalPrice) + " goldpieces ? [y/N]`"
            elif mode == "normal":
                # take money
                if totalPrice > data["houses"][house]["totalGold"]:
                    return "`Not enough funds.`"
                data["houses"][house]["totalGold"] = data["houses"][house]["totalGold"] - totalPrice
                try:
                    data["houses"][house]["inventory"][item] = data["houses"][house]["inventory"][item] + amount
                except:
                    data["houses"][house]["inventory"] = {}
                    data["houses"][house]["inventory"][item] = amount

                if item == "school":
                    data["houses"][house]["lowerClassRate"] = data["houses"][house]["lowerClassRate"] - 0.03

                elif item == "city":
                    data["houses"][house]["population"] = data["houses"][house]["population"] + 15000

                self.log("House " +str(houseName) + " bought " +str(item) + ". Amount : " + str(amount) + " for " + str(totalPrice) + " goldpieces")
                # finish, write, close
                self.overwrite_json_db(data)
                return "`House " + str(houseName) + " bought " + str(amount) + " " + str(item) + " for " + str(totalPrice) + " goldpieces.`"

    # look for a specific user, then show its specifications
    def lookFor(self, user, mode="house", personalMode = "normal", personalValue = None, personalAmount = None):
        with open(self.pathToJson) as db:
            data = json.load(db)
            # index set to -1 if below code fails, obsolete with the new try
            # but anyways

            if mode == "house":
                index = self.find_index_in_db(data["houses"], user)
                if data["houses"][index]["name"].lower() != user.lower() or index == -1:
                    return "```diff\n- error, get the name right pls```"
                # that took some time..
                name = str(data["houses"][index]["name"]) ; population = str(data["houses"][index]["population"]) ; natality = str(data["houses"][index]["natality"] * 100) ; childrenRate = str(data["houses"][index]["childrenRate"] * 100) ; elderlyRate = str(data["houses"][index]["elderlyRate"] * 100) ; mortality = str(data["houses"][index]["mortality"] * 100) ; popularity = str(data["houses"][index]["popularity"] * 100) ; children = str(data["houses"][index]["children"]) ; elderly = str(data["houses"][index]["elderly"]) ;  workingPopulation = str(data["houses"][index]["workingPopulation"]) ; menPart = str(data["houses"][index]["menPart"]) ; womenPart = str(data["houses"][index]["womenPart"]) ; men = str(int(data["houses"][index]["men"])) ; women = str(data["houses"][index]["workingPopulation"] - data["houses"][index]["men"]) ; lowerClassRate = str(data["houses"][index]["lowerClassRate"]*100) ;  upperClassRate = str(data["houses"][index]["upperClassRate"]*100) ; lowerClassTax = str(data["houses"][index]["lowerClassTax"]) ; middleClassTax = str(data["houses"][index]["middleClassTax"]) ; upperClassTax = str(data["houses"][index]["upperClassTax"]) ; lowerClass = str(data["houses"][index]["lowerClass"]) ;  middleClass = str(data["houses"][index]["middleClass"]) ; upperClass = str(data["houses"][index]["upperClass"]) ; army = str(data["houses"][index]["army"]) ; guildTax = str(data["houses"][index]["guildTax"]) ; vassalTax = str(data["houses"][index]["vassalTax"]) ; lordTax = str(data["houses"][index]["lordTax"]) ; income = str(data["houses"][index]["income"]) ;  expenses = str(data["houses"][index]["expenses"]) ; totalGold = str(data["houses"][index]["totalGold"]) ; knights = str(data["houses"][index]["knights"]) ; guards = str(data["houses"][index]["guards"]) ; squires = str(data["houses"][index]["squires"]) ; nettoIncome = str(data["houses"][index]["nettoIncome"])
                # Discord formatted information to return
                # This took some time ...
                formattedInfo = str("\n```diff\n-        Population of " + name + ":\nTotal Population : " + population + "\nChildren : " + children + "\nElders : " + elderly + "\nWorking Population : " + workingPopulation + "\nMen : " + men + "\nWomen : " + women + "\nMiddle Class : " + middleClass + "\nUpper Class : " + upperClass + "\nPoor Class : " + lowerClass + "\nArmy : " + army + " men" + "\nGuards : " + guards + "\nKnights : " + knights + "\nSquires : " + squires + "\n\n\n-          Statistics" + "\nPopularity : " + str((float(popularity))) + " percent" + "\nNatality : " + str((float(natality))) + " percent" + "\nMortality : " + str((float(mortality))) + " percent" + "\nchildren rate : " + str((float(childrenRate))) + " percent" + "\nElders Rate : " + str((float(elderlyRate))) + " percent" + "\nLower Class Rate : " + str((float(lowerClassRate))) + " percent" + "\nUpper Class Rate : " + str((float(upperClassRate))) + " percent" + "\nLower Class Tax : " + lowerClassTax + "\nMiddle Class Tax : " + middleClassTax + "\nUpper Class Tax: " + upperClassTax + "\n\n\n-          Economy" + "\nRaw income : " + income + "\nExpenses :   " + expenses + "\nIncome :    " + nettoIncome + "\nTotal Gold : " + totalGold + "\n```")

                try:
                    if data["houses"][index]["blocked"] == "true":
                        formattedInfo = str("\n```diff\n-        Population of " + name + ":\nTotal Population : " + population + "\nChildren : " + children + "\nElders : " + elderly + "\nWorking Population : " + workingPopulation + "\nMen : " + men + "\nWomen : " + women + "\nMiddle Class : " + middleClass + "\nUpper Class : " + upperClass + "\nPoor Class : " + lowerClass + "\n- Army : BLOCKED (you are in debt)" + "\nGuards : " + guards + "\nKnights : " + knights + "\nSquires : " + squires + "\n\n\n-          Statistics" + "\nPopularity : " + str((float(popularity))) + " percent" + "\nNatality : " + str((float(natality))) + " percent" + "\nMortality : " + str((float(mortality))) + " percent" + "\nchildren rate : " + str((float(childrenRate))) + " percent" + "\nElders Rate : " + str((float(elderlyRate))) + " percent" + "\nLower Class Rate : " + str((float(lowerClassRate))) + " percent" + "\nUpper Class Rate : " + str((float(upperClassRate))) + " percent" + "\nLower Class Tax : " + lowerClassTax + "\nMiddle Class Tax : " + middleClassTax + "\nUpper Class Tax: " + upperClassTax + "\n\n\n-          Economy" + "\nRaw income : " + income + "\nExpenses :   " + expenses + "\nIncome :    " + nettoIncome + "\nTotal Gold : " + totalGold + "\n```")
                except:
                    pass # hm
                print(formattedInfo)
                return formattedInfo

            # yes this is supposed to be a LOOK at stats, but its also easier to use it to change guards for users
            elif mode == "personal":
                index = self.find_index_in_db(data["players"], user)

                # is used with "\me change guards X"
                if personalMode == "change" and personalValue != None and personalAmount != None:
                    personalValue = personalValue.lower()
                    if personalValue not in ["guards"]:
                        return "For now you can only change `guards`."

                    try:
                        data["players"][index][personalValue] = personalAmount
                        # finish, write, close
                        self.overwrite_json_db(data)
                        self.recalculate_economy("all")
                        return "ok it worked"
                    except:
                        return "Nope, wrong value it seems"

                # just show the stats
                else:
                    name = str(data["players"][index]["name"]); house = str(data["players"][index]["house"]) ; age = str(data["players"][index]["age"]) ;  attackStats = str(data["players"][index]["attackStats"]) ;  dexterity = str(data["players"][index]["dexterity"]) ; counterStats = str(data["players"][index]["counterStats"]) ; equipment = str(data["players"][index]["equipment"]) ; assassinationCapacity = str(data["players"][index]["assassinationCapacity"]) ; guards = str(data["players"][index]["guards"])
                    formattedInfo = [
                        ["House", "Age", "Attack Stats", "counterStats", "Equipment", "Dexterity", "AssinationCapacity", "Guards"],
                        [house, age, attackStats, counterStats, equipment, dexterity, assassinationCapacity, guards]
                    ]
                    #formattedInfo = str("\n```diff\n-        Stats of Player : " + name + ":\nhouse : " + house + "\nAge : " + age + "\nattackStats : " + attackStats + "\ncounterStats : " + counterStats + "\nequipment : " + equipment + "\ndexterity: " + dexterity + "\nassassinationCapacity : " + assassinationCapacity + "\nguards : " + guards + "```")

                    return formattedInfo

            # guild information
            elif mode == "guilds":
                    index = self.find_index_in_db(data["guilds"], user)

                    name = str(data["guilds"][index]["name"]); owner = str(data["guilds"][index]["owner"]) ; location = str(data["guilds"][index]["location"]) ;  totalGold = str(data["guilds"][index]["totalGold"])
                    formattedInfo = str("\n```diff\n-        Stats of Guild of " + name + ":\nOwner : " + owner + "\nLocation : " + location + "\nTotal Gold : " + totalGold + "```")
                    return formattedInfo

    # automatically fetch all guards of a house combined.
    def calculate_guards(self, house):
        houseName = "house_"+house
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            guards = 0
            x = 0
            for i in range(len(data["players"])):
                if house in data["players"][i]["house"]:
                    x = x+1
                    guards = guards + int(data["players"][i]["guards"])
            return guards

    # recalculate the popularity of a house
    def calculate_popularity(self, index):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)

            middleTax = data["houses"][index]["middleClassTax"]
            lowerTax = data["houses"][index]["lowerClassTax"]
            upperTax = data["houses"][index]["upperClassTax"]
            if middleTax > 70:
                popularity = 5
            elif middleTax > 51:
                popularity = 20
            elif middleTax > 31:
                popularity = 50 - random.randint(0, 10)
            elif middleTax > 21:
                popularity = 60 - random.randint(0, 20)
            elif middleTax > 11:
                popularity = 70 - random.randint(0, 20)
            else:
                popularity = 80
            return popularity / 100

    # create a player character
    def createUser(self, name, house, age, attack, counter, equipment, dexterity, assassinationCapacity, guards):
        # check if user exists
        users = self.listUsers()
        if name in users:
            # already exists
            return("error")
        # load and save in memory
        # load and save in mem the json file
        try:
            with open(self.pathToJson, "r") as self.json_file:
                self.json_db_content = json.load(self.json_file)
                self.json_players = self.json_db_content['players']
        except:
            # first time we do this.
            pass

        # user doesnt exist so go creating it

        try:
            print(self.json_db_content["players"][0])
            self.json_db_content["players"].append({
                "name": name,
                "house": house,
                "age": age,
                "attackStats": attack,
                "counterStats": counter,
                "equipment": equipment,
                "dexterity": dexterity,
                "assassinationCapacity": assassinationCapacity,
                "guards": guards
            })
            content = self.json_db_content
            self.overwrite_json_db(content)
        except:
            pass


    # a lot of values, a lot of messy code
    def createHouse(self, uName, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires, villageName, villageCoordinates, houseType, immigration):
        # here we goo
        self.jsonTemp = {}
        self.uName = uName.strip().lower()
        # check if user exists
        users = self.listHouses()
        if self.uName in users:
            # already exists
            return("error - House exists")

        # load and save in mem the json file
        try:
            with open(self.pathToJson, "r") as self.json_file:
                self.json_db_content = json.load(self.json_file)
                self.json_players = self.json_db_content['houses']
        except:
            # first time we do this.
            pass

        # user doesnt exist so go creating it
        try:
            x = (self.json_db_content["houses"][0])
        except:
            # this is the first player, so go creating it
            self.json_db_content["houses"] = []
        # check if village exists
        for i in range(len(self.json_db_content["houses"])):
            try:
                houseCities = list(self.json_db_content["houses"][i]["cities"].keys())
                for insideIndex in range(len(houseCities)):
                    coordinates = tuple(self.json_db_content["houses"][i]["cities"]["coordinates"][houseCities[insideIndex]])
                    if houseCities[insideIndex] == villageName or coordinates == villageCoordinates:
                        return "error. village exists (check name or coordinates)"
            except Exception as e:
                print(e)
                pass

        self.json_db_content["houses"].append({
            "name" : uName,
            "type" : houseType,
            "totalPopulation" : 0,
            "natality" : 0,
            "childrenRate" : 0,
            "elderlyRate" : 0,
            "mortality" : 0,
            "popularity" : popularity,
            "children" : 0,
            "elderly" : 0,
            "workingPopulation" : 0,
            "menPart" : 0,
            "womenPart" : 0,
            "men" : 0,
            "lowerClassRate" : lowerClassRate,
            "upperClassRate" : upperClassRate,
            "lowerClassTax" : lowerClassTax,
            "middleClassTax" : middleClassTax,
            "upperClassTax" : upperClassTax,
            "lowerClass" : lowerClass,
            "middleClass" : middleClass,
            "upperClass" : upperClass,
            "army" : army,
            "guildTax" : guildTax,
            "vassalTax" : vassalTax,
            "lordTax" : lordTax,
            "income" : income,
            "expenses" : expenses,
            "totalGold" : totalGold,
            "knights" : knights,
            "guards" : guards,
            "squires" : squires,
            "cities": {villageName: {
                        "coordinates":villageCoordinates,
                        "population" : population,
                        "menPart" : menPart,
                        "womenPart" : womenPart,
                        "men" : men,
                        "immigration": immigration,
                        "children" : children,
                        "elderly" : elderly,
                        "workingPopulation" : workingPopulation,
                        "natality" : natality,
                        "childrenRate" : childrenRate,
                        "elderlyRate" : elderlyRate,
                        "mortality" : mortality,
                                    }
                    }
        })
        # finish and write to file
        content = self.json_db_content
        self.overwrite_json_db(content)
        return "worked"


    # this is just to change some values without upating all values
    # to update a whole user (new population etc.) look below
    def changeSpecific(self, houseRole, choice, amount, futureExpenses, mode="normal"):

        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            index = self.find_index_in_db(data["houses"], houseRole)
            # this will be called when informing the user
            if mode == "info":
                maxExpenses = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]
                massTroops = maxExpenses // self.armySalary
                return str(massTroops)

        if mode == "normal":
            with open(self.pathToJson, "r") as db:
                data = json.load(db)
                index = self.find_index_in_db(data["houses"], houseRole)

                # this will be called before the actual change
                # to get the maximumg amount of troops the player can afford
                if mode == "info":
                    maxExpenses = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]
                    maximumTroopsBeforeDeficit = maxExpenses // self.armySalary
                    return str(maximumTroopsBeforeDeficit)

                if choice == "army" and amount > data["houses"][index]["population"] - data["houses"][index]["elderly"] - data["houses"][index]["children"] - 1:
                    return "too much army"

                # else, normal mode

                if (choice == "upperClassTax" and amount > self.upperClassTaxMax) or (choice == "middleClassTax" and amount > self.middleClassTaxMax) or (choice == "lowerClassTax" and amount > self.lowerClassTaxMax):
                    return "`Too high taxes ( " + str(self.upperClassTaxMax) + " max for upper class), ( " + str(self.middleClassTaxMax) + " max for middle class), ( " + str(self.lowerClassTaxMax) + " max for lower class),`"

                if choice == "army" and futureExpenses > data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"] :
                    return "```diff\n- Your future expenses would be higher as your income.\nThis is not possible to change over he bot.\nAsk the staff for major changes that come with debt.```"
                data["houses"][index][choice] = amount
                data["houses"][index]["workingPopulation"] = int(data["houses"][index]["population"] - data["houses"][index]["children"] - data["houses"][index]["elderly"] - data["houses"][index]["army"])
                data["houses"][index]["men"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["menPart"])
                data["houses"][index]["women"] = int(data["houses"][index]["workingPopulation"] - data["houses"][index]["men"])
                data["houses"][index]["lowerClass"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["lowerClassRate"])
                data["houses"][index]["upperClass"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["upperClassRate"])
                data["houses"][index]["middleClass"] = int(data["houses"][index]["workingPopulation"] - data["houses"][index]["lowerClass"] - data["houses"][index]["upperClass"])
                data["houses"][index]["income"] = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["upperClass"] * data["houses"][index]["upperClassTax"]
                if choice == "army":
                    data["houses"][index]["expenses"] = amount * self.armySalary + data["houses"][index]["guards"] * self.guardsSalary

        if mode == "players":
            with open(self.pathToJson, "r") as db:
                data = json.load(db)
                index = self.find_index_in_db(data["players"], houseRole)
                # else, normal mode
                if choice != "name" and choice != "equipment": amount = int(amount)
                data["players"][index][choice] = amount
        # finish, write, close
        self.log("House/Player " +str(houseRole) + " changed " + choice + " to " + str(amount))
        self.overwrite_json_db(data)
        self.recalculate_economy("all")
        # inform user
        return "```\nYay ! It worked !```"

    # update their age and stuff
    def updatePlayer(self, player):
        # get user index
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data["players"], user)
            except:
                return "User not found"
            if data["players"][index]["age"] > 16:
                data["players"][index]["age"] = data["players"][index]["age"] + 1
            else:
                data["players"][index]["age"] = data["players"][index]["age"] + 2
            self.overwrite_json_db(data)
            return "done"

    # this could be optimized
    def updateHouse(self, user=None, rates="rates.json"):
        """
        ### TODO TODO TODO TODO BEFORE NEXT UPDATE NEXT SUNDAY
        """
        if user == None: return "No user specified"
        user = user.lower()
        debt = False
        # get user index
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data["houses"], user)
            except:
                return "User not found"

            """
                many things to change.. yes it took me some time too lmao
            """
            #natality = pass
            #mortality = pass
            newPopulation = data["houses"][index]["population"] + (data["houses"][index]["population"] * data["houses"][index]["natality"]) - (data["houses"][index]["population"] * data["houses"][index]["mortality"])
            #popularity = manualPopularity
            children, elderly = int(data["houses"][index]["population"] * data["houses"][index]["childrenRate"]), int(data["houses"][index]["population"] * data["houses"][index]["elderlyRate"])
            workingPopulation = int(data["houses"][index]["population"] - data["houses"][index]["children"] - data["houses"][index]["elderly"] - data["houses"][index]["army"])
            men = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["menPart"])
            women = int(data["houses"][index]["workingPopulation"] - data["houses"][index]["men"])
            #knights, guards, squires = 0, 0, 0

            for ii in range(len(data["houses"])):

                house = data["houses"][ii]["name"].split("_")[1]
                guards = self.calculate_guards(house)

            data["houses"][index]["guards"] = guards
            lowerClass = int(workingPopulation * data["houses"][index]["lowerClassRate"])
            upperClass = int(workingPopulation * data["houses"][index]["upperClassRate"])
            middleClass = int(workingPopulation - data["houses"][index]["lowerClass"] - data["houses"][index]["upperClass"])

            natality = (data["houses"][index]["health"] / 100) * 5
            mortality = 1 + (data["houses"][index]["health"] / 100)

            #guildTax = pass
            #vassalTax = pass
            #lordTax = pass
            income = middleClass * data["houses"][index]["middleClassTax"] + lowerClass * data["houses"][index]["lowerClassTax"] + upperClass * data["houses"][index]["upperClassTax"]
            expenses = data["houses"][index]["army"] * self.armySalary + data["houses"][index]["knights"] * self.knightsSalary + data["houses"][index]["guards"] * self.guardsSalary + data["houses"][index]["squires"] * 0
            nettoIncome = data["houses"][index]["income"] - data["houses"][index]["expenses"]
            totalGold = data["houses"][index]["totalGold"] + nettoIncome

            #data["houses"][index]["name"] = pass
            data["houses"][index]["population"] = newPopulation
            data["houses"][index]["natality"] = natality / 100
            #data["houses"][index]["childrenRate"] = pass
            #data["houses"][index]["elderlyRate"] = pass
            data["houses"][index]["mortality"] = mortality / 100
            #data["houses"][index]["popularity"] = pass
            data["houses"][index]["children"] = children
            data["houses"][index]["elderly"] = elderly
            data["houses"][index]["workingPopulation"] = workingPopulation
            #data["houses"][index]["menPart"] = pass
            #data["houses"][index]["womenPart"] = pass
            data["houses"][index]["men"] = men
            data["houses"][index]["women"] = women
            #data["houses"][index]["lowerClassRate"] = pass
            #data["houses"][index]["upperClassRate"] = pass
            #data["houses"][index]["lowerClassTax"] = pass
            #data["houses"][index]["middleClassTax"] = pass
            #data["houses"][index]["upperClassTax"] = pass
            data["houses"][index]["lowerClass"] = lowerClass
            data["houses"][index]["middleClass"] = middleClass
            data["houses"][index]["upperClass"] = upperClass
            #data["houses"][index]["army"] = pass
            # economy sector
            #data["houses"][index]["incomeTax"] = pass
            #data["houses"][index]["guildTax"] = pass
            #data["houses"][index]["vassalTax"] = pass
            #data["houses"][index]["lordTax"] = pass
            popularity = self.calculate_popularity(index)
            data["houses"][index]["popularity"] = popularity

            data["houses"][index]["income"] = income
            data["houses"][index]["expenses"] = expenses
            data["houses"][index]["totalGold"] = totalGold
            data["houses"][index]["nettoIncome"] = nettoIncome
            if data["houses"][index]["totalGold"] < 0 :
                data["houses"][index]["blocked"] = "true"
                debt = True
                data["houses"][index]["army"] = 0
            else:
                data["houses"][index]["blocked"] = "false"

            #data["houses"][index]["knights"] = knights
            #data["houses"][index]["guards"] = guards
            #data["houses"][index]["squires"] = squires
            self.log("Updated house " + str(user))
            #overwrite old file
            self.overwrite_json_db(data)
            # nice, lets inform the user
            if debt == True:
                return r"/!\ Player is currently in debt. Army blocked."
            return "All went smooth. User has been updated"


    def recalculate_economy(self, house):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            if house == "all":
                for index in range(len(data["houses"])):

                    house = data["houses"][index]["name"].split("_")[1]
                    guards = self.calculate_guards(house)
                    data["houses"][index]["guards"] = guards
                    data["houses"][index]["children"] = int(data["houses"][index]["population"] * data["houses"][index]["childrenRate"])
                    data["houses"][index]["elderly"] = int(data["houses"][index]["population"] * data["houses"][index]["elderlyRate"])
                    for i in range(len(data["houses"])):
                        try:
                            houseCities = list(data["houses"][i]["cities"].keys())
                            for insideIndex in range(len(houseCities)):
                                coordinates = tuple(data["houses"][i]["cities"]["coordinates"][houseCities[insideIndex]])
                                print(data["houses"][i]["cities"])
                        except Exception as e:
                            print(e)
                            pass
                    data["houses"][index]["workingPopulation"] = int(data["houses"][index]["population"] - data["houses"][index]["children"] - data["houses"][index]["elderly"] - data["houses"][index]["army"])
                    data["houses"][index]["men"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["menPart"])
                    data["houses"][index]["women"] = int(data["houses"][index]["workingPopulation"] - data["houses"][index]["men"])
                    data["houses"][index]["lowerClass"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["lowerClassRate"])
                    data["houses"][index]["upperClass"] = int(data["houses"][index]["workingPopulation"] * data["houses"][index]["upperClassRate"])
                    data["houses"][index]["middleClass"] = int(data["houses"][index]["workingPopulation"] - data["houses"][index]["lowerClass"] - data["houses"][index]["upperClass"])
                    data["houses"][index]["income"] = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["upperClass"] * data["houses"][index]["upperClassTax"]
                    data["houses"][index]["expenses"] = int(data["houses"][index]["army"]) * self.armySalary + int(data["houses"][index]["guards"]) * self.guardsSalary
                    data["houses"][index]["nettoIncome"] = data["houses"][index]["income"] - data["houses"][index]["expenses"]
                    popularity = self.calculate_popularity(index)
                    data["houses"][index]["popularity"] = popularity


                    lower = data["houses"][index]["upperClassTax"] / 200
                    middle = data["houses"][index]["middleClassTax"] / 100
                    upper = data["houses"][index]["lowerClassTax"] / 60
                    health = 100 - (lower * random.randint(50,60) + middle *  random.randint(50,60) + upper *  random.randint(12,20) )
                    data["houses"][index]["health"] = health
                    natality = (data["houses"][index]["health"] / 100) * 5
                    mortality = 1 + (data["houses"][index]["health"] / 100)
                    data["houses"][index]["natality"] = natality / 100
                    data["houses"][index]["mortality"] = mortality / 100

                    if data["houses"][index]["totalGold"] < 0:
                        data["houses"][index]["blocked"] = "true"
                    else:
                        data["houses"][index]["blocked"] = "false"

        self.overwrite_json_db(data)

    def grepValue(self, house, value, mode="houses"):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data[mode], house)
            except:
                return "User not found"
            try:
                grepped = data[mode][index][value]
            except:
                return "Value not valid"

            return grepped

    def inventory(self, house):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data["houses"], house)
            except:
                return "User not found"
            try:

                inventory = data["houses"][index]["inventory"]
            except:
                return "Inventory empty"

            return inventory

    def travel(self, member, destination):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data["players"], member)
            except:
                return "User not found"
            now = datetime.now()
            dateAndTime = now.strftime("%d/%m/%Y %H:%M:%S")
            data["players"][index]["travel"] = str(dateAndTime) + ": " + destination
            self.overwrite_json_db(data)
            self.log("Player " + str(member) + " travels to " + str(destination))
            return "Travelling to "+destination

    def travelHistory(self, member):
        with open(self.pathToJson, "r") as db:
            userList = [member]
            resultChar = ""
            data = json.load(db)
            if member == "all":
                userList = self.listUsers()
            print(userList)
            for i in range(len(userList)):
                index = self.find_index_in_db(data["players"], userList[i])
                try:
                    destination = data["players"][index]["travel"]
                    print(data["players"][index]["travel"], destination)
                    resultChar = resultChar + "Player: `" + str(data["players"][index]["name"]) + "` travelling to `" + destination + "`\n"
                except:
                    pass
            return resultChar


# bruh, line 652 the 1st february 2020
# EOF
