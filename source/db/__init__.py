import json
import os


"""

    this is quite messy, and seems long, but dw, it's just that there is a lot of data
        and variables to manage everytime we change something

"""


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
        rate = json.load(rates_file)
        self.guardsSalary = rate["rates"]["guardsSalary"]
        self.knightsSalary = rate["rates"]["knightsSalary"]
        self.armySalary = rate["rates"]["armySalary"]


    def overwrite_json_db(self, content):
        self.json_db = open(self.pathToJson, "w")
        self.perfectionJson = json.dumps(content, indent=4, separators=(',', ': '))
        self.json_db.write(self.perfectionJson)
        self.json_db.close()

    def find_index_in_db(self, dataToFindIn, userNameToFind):
        index = -1
        for i in range(len(dataToFindIn)):
            if dataToFindIn[i]["name"].lower() == userNameToFind.lower():
                return i
        # -1 will be used as error in below functions
        return index

    # pay from house to house
    def sendMoney(self, sender, receiver, amount):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)

            senderIndex = self.find_index_in_db(data["houses"], sender)
            receiverIndex = self.find_index_in_db(data["houses"], receiver)

            print(data["houses"][senderIndex]["totalGold"])
            data["houses"][senderIndex]["totalGold"] = data["houses"][senderIndex]["totalGold"] - amount
            print(data["houses"][senderIndex]["totalGold"])
            print(data["houses"][receiverIndex]["totalGold"])
            data["houses"][receiverIndex]["totalGold"] = data["houses"][receiverIndex]["totalGold"] + amount
            print(data["houses"][receiverIndex]["totalGold"])
            # finish, write, close
            self.overwrite_json_db(data)
            return "`Sent the CA$H`"


    # look for a specific user, then show its specifications
    def lookFor(self, user, mode="house", personalMode = "normal", personalValue = None, personalAmount = None):
        with open(self.pathToJson) as db:
            data = json.load(db)
            print("Loaded Database")
            print("Going on")
            # index set to -1 if below code fails, obsolete with the new try
            # but anyways

            if mode == "house":
                index = self.find_index_in_db(data["houses"], user)
                print("checkpoint 1")
                if data["houses"][index]["name"].lower() != user.lower() or index == -1:
                    return "```diff\n- error, get the name right pls```"
                print("checkpoint 2")
                # that took some time..
                name = str(data["houses"][index]["name"]) ; population = str(data["houses"][index]["population"]) ; natality = str(data["houses"][index]["natality"]) ; childrenRate = str(data["houses"][index]["childrenRate"]) ; elderlyRate = str(data["houses"][index]["elderlyRate"]) ; mortality = str(data["houses"][index]["mortality"]) ; popularity = str(data["houses"][index]["popularity"]) ; children = str(data["houses"][index]["children"]) ; elderly = str(data["houses"][index]["elderly"]) ;  workingPopulation = str(data["houses"][index]["workingPopulation"]) ; menPart = str(data["houses"][index]["menPart"]) ; womenPart = str(data["houses"][index]["womenPart"]) ; men = str(int(data["houses"][index]["men"])) ; women = str(data["houses"][index]["workingPopulation"] - data["houses"][index]["men"]) ; lowerClassRate = str(data["houses"][index]["lowerClassRate"]) ;  upperClassRate = str(data["houses"][index]["upperClassRate"]) ; lowerClassTax = str(data["houses"][index]["lowerClassTax"]) ; middleClassTax = str(data["houses"][index]["middleClassTax"]) ; upperClassTax = str(data["houses"][index]["upperClassTax"]) ; lowerClass = str(data["houses"][index]["lowerClass"]) ;  middleClass = str(data["houses"][index]["middleClass"]) ; upperClass = str(data["houses"][index]["upperClass"]) ; army = str(data["houses"][index]["army"]) ; guildTax = str(data["houses"][index]["guildTax"]) ; vassalTax = str(data["houses"][index]["vassalTax"]) ; lordTax = str(data["houses"][index]["lordTax"]) ; income = str(data["houses"][index]["income"]) ;  expenses = str(data["houses"][index]["expenses"]) ; totalGold = str(data["houses"][index]["totalGold"]) ; knights = str(data["houses"][index]["knights"]) ; guards = str(data["houses"][index]["guards"]) ; squires = str(data["houses"][index]["squires"])
                # Discord formatted information to return
                print("checkpoint 3")
                # This took some time ...
                formattedInfo = str("\n```diff\n-        Population of " + name + ":\nTotal Population : " + population + "\nChildren : " + children + "\nElders : " + elderly + "\nWorking Population : " + workingPopulation + "\nMen : " + men + "\nWomen : " + women + "\nMiddle Class : " + middleClass + "\nUpper Class : " + upperClass + "\nPoor Class : " + lowerClass + "\nArmy : " + army + " men" + "\nGuards : " + guards + "\nKnights : " + knights + "\nSquires : " + squires + "\n\n\n-          Statistics" + "\nPopularity : " + str((float(popularity)*100)) + " percent" + "\nNatality : " + str((float(natality)*100)) + " percent" + "\nMortality : " + str((float(mortality)*100)) + " percent" + "\nchildren rate : " + str((float(childrenRate)*100)) + " percent" + "\nElders Rate : " + str((float(elderlyRate)*100)) + " percent" + "\nLower Class Rate : " + str((float(lowerClassRate)*100)) + " percent" + "\nUpper Class Rate : " + str((float(upperClassRate)*100)) + " percent" + "\nLower Class Tax : " + lowerClassTax + "\nMiddle Class Tax : " + middleClassTax + "\nUpper Class Tax: " + upperClassTax + "\n\n\n-          Economy" + "\nIncome : " + income + "\nExpenses : " + expenses + "\nTotal Gold : " + totalGold + "\n```")
                print("done")
                return formattedInfo

            # yes this is supposed to be a LOOK at stats, but its also easier to use it to change guards for users
            elif mode == "personal":
                index = self.find_index_in_db(data["players"], user)
                if personalMode == "change" and personalValue != None and personalAmount != None:
                    personalValue = personalValue.lower()
                    if personalValue not in ["guards"]:
                        return "For now you can only change `guards`."
                    if int(personalAmount) > 3:
                        return "Maximum 3 guards. If you are lord and want more, ask staff specifically"

                    try:
                        data["players"][index][personalValue] = personalAmount
                        # finish, write, close
                        self.overwrite_json_db(data)

                        return "ok it worked"
                    except:
                        return "Nope, wrong value it seems"
                        {'name': 'mistress adelaide s airgetlam', 'house': 'house_airgetlam', 'age': 12, 'attackStats': 0, 'counterStats': 0, 'equipment': 'unarmed', 'dexterity': 0, 'assassinationCapacity': 0, 'guards': '3'}
                else:
                    name = str(data["players"][index]["name"]); house = str(data["players"][index]["house"]) ; age = str(data["players"][index]["age"]) ;  attackStats = str(data["players"][index]["attackStats"]) ;  dexterity = str(data["players"][index]["dexterity"]) ; counterStats = str(data["players"][index]["counterStats"]) ; equipment = str(data["players"][index]["equipment"]) ; assassinationCapacity = str(data["players"][index]["assassinationCapacity"]) ; guards = str(data["players"][index]["guards"])
                    formattedInfo = str("\n```diff\n-        Stats of Player : " + name + ":\nhouse : " + house + "\nAge : " + age + "\nattackStats : " + attackStats + "\ncounterStats : " + counterStats + "\nequipment : " + equipment + "\ndexterity: " + dexterity + "\nassassinationCapacity : " + assassinationCapacity + "\nguards : " + guards + "```")

                    return formattedInfo

    # to get a list with all users.
    # can be used either for the user, or in this module
    def listHouses(self):
        with open(self.pathToJson, "r") as db:
            data = json.load(db) ; x = [data["houses"][i]["name"] for i in range(len(data["houses"]))] ; return x
    def listUsers(self):
        with open(self.pathToJson, "r") as db:
            data = json.load(db) ; x = [data["players"][i]["name"] for i in range(len(data["players"]))] ; return x


    # create a player character
    def createUser(self, name, house, age, attack, counter, equipment, dexterity, assassinationCapacity, guards):
        # check if user exists
        users = self.listUsers()
        if name in users:
            print("nope, user already exists")
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
    def createHouse(self, uName, population, natality, childrenRate, elderlyRate, mortality, popularity, children, elderly, workingPopulation, menPart, womenPart, men, women, lowerClassRate, upperClassRate, lowerClassTax, middleClassTax, upperClassTax, lowerClass, middleClass, upperClass, army, guildTax, vassalTax, lordTax, income, expenses, totalGold, knights, guards, squires):
        # here we goo
        self.jsonTemp = {}
        self.uName = uName.strip().lower()
        # check if user exists
        users = self.listUsers()
        if self.uName in users:
            print("nope, user already exists")
            return("error")
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
            print(self.json_db_content["houses"][0])
        except:
            # this is the first player, so go creating it
            self.jsonTemp["houses"] = []

        self.json_db_content["houses"].append({
            "name" : uName, "population" : population,
            "natality" : natality,
            "childrenRate" : childrenRate,
            "elderlyRate" : elderlyRate,
            "mortality" : mortality,
            "popularity" : popularity,
            "children" : children,
            "elderly" : elderly,
            "workingPopulation" : workingPopulation,
            "menPart" : menPart,
            "womenPart" : womenPart,
            "men" : men,
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
            "squires" : squires
        })
        # finish and write to file
        content = self.json_db_content
        self.overwrite_json_db(content)


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
            print("Changing for ", houseRole)
            with open(self.pathToJson, "r") as db:
                data = json.load(db)
                index = self.find_index_in_db(data["houses"], houseRole)

                # this will be called before the actual change
                # to get the maximumg amount of troops the player can afford
                if mode == "info":
                    maxExpenses = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]
                    maximumTroopsBeforeDeficit = maxExpenses // self.armySalary
                    return str(maximumTroopsBeforeDeficit)

                # else, normal mode
                print("Before Change : ", data["houses"][index][choice])

                if (choice == "upperClassTax" and amount > 200) or (choice == "middleClassTax" and amount > 100) or (choice == "lowerClassTax" and amount > 60):
                    return "`Too high taxes`"

                if futureExpenses > data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"] :
                    return "```diff\n- Your future expenses would be higher as your income.\nThis is not possible to change over he bot.\nAsk the staff for major changes that come with debt.```"
                data["houses"][index][choice] = amount
                if choice == "army":
                    data["houses"][index]["workingPopulation"] = data["houses"][index]["population"] - data["houses"][index]["elderly"] -data["houses"][index]["children"]  - data["houses"][index]["army"]
                    data["houses"][index]["expenses"] = data["houses"][index]["army"] * 100

                data["houses"][index]["income"] = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]


        if mode == "players":
            print("Changing for ", houseRole)
            with open(self.pathToJson, "r") as db:
                data = json.load(db)
                index = self.find_index_in_db(data["players"], houseRole)
                print(choice, amount)
                # else, normal mode
                print("Before Change : ", data["players"][index][choice])
                data["players"][index][choice] = int(amount)
                print("bruh")
        # finish, write, close
        self.overwrite_json_db(data)
        # inform user
        return "```\nYay ! It worked !```"

    def updateHouse(self, user=None, rates="rates.json"):
        if user == None: return "No user specified"
        user = user.lower()

        # get user index
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            try:
                index = self.find_index_in_db(data["houses"], user)
            except:
                return "User not found"
            print(index)

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
            lowerClass = int(workingPopulation * data["houses"][index]["lowerClassRate"])
            upperClass = int(workingPopulation * data["houses"][index]["upperClassRate"])
            middleClass = int(workingPopulation - data["houses"][index]["lowerClass"] - data["houses"][index]["upperClass"])


            #guildTax = pass
            #vassalTax = pass
            #lordTax = pass
            income = middleClass * data["houses"][index]["middleClassTax"] + lowerClass * data["houses"][index]["lowerClassTax"] + upperClass * data["houses"][index]["upperClassTax"]
            expenses = data["houses"][index]["army"] * self.armySalary + data["houses"][index]["knights"] * self.knightsSalary + data["houses"][index]["guards"] * self.guardsSalary + data["houses"][index]["squires"] * 0
            totalGold = data["houses"][index]["totalGold"] + income - expenses

            #data["houses"][index]["name"] = pass
            data["houses"][index]["population"] = newPopulation
            #data["houses"][index]["natality"] = natality
            #data["houses"][index]["childrenRate"] = pass
            #data["houses"][index]["elderlyRate"] = pass
            #data["houses"][index]["mortality"] = mortality
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
            data["houses"][index]["income"] = income
            print(data["houses"][index]["income"])
            data["houses"][index]["expenses"] = expenses
            data["houses"][index]["totalGold"] = totalGold
            #data["houses"][index]["knights"] = knights
            #data["houses"][index]["guards"] = guards
            #data["houses"][index]["squires"] = squires

            #overwrite old file
            self.overwrite_json_db(data)
            # nice, lets inform the user
            return "All went smooth. User has been updated"

    def updateAll(self):
        x = self.listHouses()
        for house in x:
            self.updateHouse(house)
        return "All users have been updated"



    def recalculate_economy(self, house):
        with open(self.pathToJson, "r") as db:
            data = json.load(db)
            if house == "all":
                for index in range(len(data["houses"])):
                    data["houses"][index]["workingPopulation"] =  data["houses"][index]["population"] - data["houses"][index]["elderly"] -data["houses"][index]["children"] - data["houses"][index]["army"]
                    data["houses"][index]["expenses"] = data["houses"][index]["army"] * 100
                    data["houses"][index]["income"] = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]

            else:
                index = self.find_index_in_db(data["houses"], house)
                data["houses"][index]["workingPopulation"] =  data["houses"][index]["population"] - data["houses"][index]["elderly"] -data["houses"][index]["children"] - data["houses"][index]["army"]
                data["houses"][index]["expenses"] = data["houses"][index]["army"] * 100
                data["houses"][index]["income"] = data["houses"][index]["middleClass"] * data["houses"][index]["middleClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["lowerClassTax"] + data["houses"][index]["lowerClass"] * data["houses"][index]["upperClassTax"]

        self.overwrite_json_db(data)
