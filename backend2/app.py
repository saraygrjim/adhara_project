from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from prompt_toolkit.validation import Validator, ValidationError
import json
import random
from web3 import Web3, HTTPProvider
from PyInquirer import prompt, print_json


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


options = [
    {
        'type': 'list',
        'name': 'theme',
        'message': 'Please, register or log in',
        'choices': [
            'Register',
            'Log in',
            'Exit'
        ]
    },
    {
        'type': 'list',
        'name': 'theme',
        'message': 'Please, register or log in',
        'choices': [
            'Log in',
            'Exit'
        ]
    },
    {
        'type': 'list',
        'name': 'theme',
        'message': 'Please, register or log in',
        'choices': [
            'Register',
            'Exit'
        ]
    },
    {
        'type': 'list',
        'name': 'theme',
        'message': 'What do you want to do?',
        'choices': [
            'Make a bet',
            'Execute bet',
            'See my bets',
            'See my balance',
            'Log out'
        ]
    }
]

##----------------------INITIALIZATION OF CONTRACT----------------------##

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path    = '../build/contracts/ERC20.json'
deployed_contract_address = '0x8847E824cB169B88C92343e26298e06Ca4a423eF'

with open(compiled_contract_path) as file:
    contract_json = json.load(file)     # load contract info as JSON
    contract_abi = contract_json['abi'] # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
accounts = web3.eth.get_accounts()

def countUsers():
    with open("users.json") as usersFile:
        data = usersFile.read()
        users = json.loads(data)
        return len(users) + 1

##----------------------CLASS----------------------##
# !! ONLY 9 USERS COULD BE REGISTERED BECAUSE THERE ARE ONLY 10 DIRECTIONS 
class User:
    def __init__(self, name, password, address="0"):
        if(address == "0"):
            counter = countUsers()
            self.address  = accounts[counter] 
            self.name     = name
            self.password = password
        else:
            if(address in accounts):
                self.address = address
            else:
                raise Exception('Incorrect json file')
            self.name     = name
            self.password = password

class Bet:
    def __init__(self, name, address, holdId, solve=False, winner=""):
        self.owner   = name
        self.address = address
        self.holdId  = holdId
        self.solve   = solve
        self.winner  = winner


##----------------------GLOBAL VARIABLES----------------------##
counterHolds    = 0
currentUser     = User("0", "0", "0")

##----------------------VALIDATORS----------------------##
class newNameValidator(Validator):
    def validate(self, document):
        ok = userExist(document.text)
        if ok != -1:
            raise ValidationError(
                message='This user already exist',
                cursor_position=len(document.text))  # Move cursor to end

class nameValidator(Validator):
    def validate(self, document):
        ok = userExist(document.text)
        if ok == -1:
            raise ValidationError(
                message='There is no user with this name',
                cursor_position=len(document.text))  # Move cursor to end

class passwordValidator(Validator):
    global currentUser
    def validate(self, document):
        ok = userExist(currentUser.name)
        if ok.password != document.text:
            raise ValidationError(
                message='Incorrect password, please try again',
                cursor_position=len(document.text))  # Move cursor to end

##----------------------FUCTIONS----------------------##

def initialTransfers():
    '''
    This fuction execute the initial transfer of 100 tokens to 
    all the accounts.
    '''
    for account in accounts:
        if(contract.functions.balanceOf(account).call() == 0 and getUser(account) == -1):
            contract.functions.transfer(account, 100).transact()
        # print(contract.functions.balanceOf(account).call()) 

def decodeUser(user):
    ''' 
    convert json object to user class
    '''
    return User(user["name"], user["password"], user["address"])

def decodeBet(bet):
    ''' 
    convert json object to bet class
    '''
    return Bet(bet["owner"], bet["address"], bet["holdId"], bet["solve"], bet["winner"])

def updateUsers(user):
    '''
    add a new user in the json file
    '''
    with open("users.json", "r") as file:
        data = json.load(file)
    data.append(user.__dict__)
    with open("users.json", "w") as file:
        json.dump(data, file)

def updateBets(bets):
    '''
    update the bets
    '''
    data = []
    for bet in bets:
        data.append(bet.__dict__)
    with open("bets.json", "w") as file:
        json.dump(data, file)

def getUser(address):
    '''
    return the owner of the address
    '''
    with open("users.json") as usersFile:
        data  = usersFile.read()
        users = json.loads(data, object_hook=decodeUser)

        for user in users:
            if(user.address == address):
                return user
        return -1

def getBet(address):
    '''
    return the current bet of the 
    address owner
    '''
    with open("bets.json") as betsFile:
        data = betsFile.read()
        bets = json.loads(data, object_hook=decodeBet)

        for bet in bets:
            if(bet.address == address and bet.solve == False):
                return -1
        return 0

def getUserBets(user):
    '''
    return all the bets solved and unsolved 
    of the user
    '''
    with open("bets.json") as betsFile:
        data     = betsFile.read()
        bets     = json.loads(data, object_hook=decodeBet)
        userBets = []
        for bet in bets:
            if(bet.owner == user.name):
                userBets.append(bet)
        return userBets

def countBets():
    '''
    return how many users have participated 
    in the current bet 
    '''
    with open("bets.json") as betsFile:
        data    = betsFile.read()
        bets    = json.loads(data, object_hook=decodeBet)
        counter = 0
        for bet in bets:
            if not bet.solve:
                counter = counter + 1 
        return(counter)

def userExist(name):
    '''
    if the user is register return the user, 
    if not return -1
    '''
    with open("users.json") as usersFile:
        data  = usersFile.read()
        users = json.loads(data, object_hook=decodeUser)
        for user in users:
            if user.name == name: 
                return user
        return -1

def getBalance(user):
    '''
    return the balance of a user
    '''
    return contract.functions.balanceOf(user.address).call()

def register():
    '''
    register a new user
    '''
    global currentUser
    registerQ = [
        {
            'type': 'input',
            'name': 'name',
            'message': 'What\'s your name for the register',
            'validate' : newNameValidator
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'Please, type a password',
        },
    ]
    name     = prompt(registerQ[0])['name']
    password = prompt(registerQ[1])['password']
    user     = User(name, password)
    updateUsers(user)
    currentUser = user
    return 0

def logIn():
    '''
    log in of an existing user
    '''
    global currentUser
    logInQ = [
        {
            'type': 'input',
            'name': 'name',
            'message': 'What\'s yout name',
            'validate' : nameValidator
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'Please, type your password',
            'validate' : passwordValidator
        },
    ]
    with open("users.json") as usersFile:
        data  = usersFile.read()
        users = json.loads(data, object_hook=decodeUser)

        name = prompt(logInQ[0])['name']
        currentUser.name = name
        password = prompt(logInQ[1])['password']

        for user in users:
            if (user.name == name and user.password == password):
                currentUser.name = user.name
                currentUser.password = user.password
                currentUser.address = user.address

    
def newBet():
    '''
    participate in a bet
    If everything is correct, return 0
    If the user has already participate in this bet, return -1
    If there are already 4 bets, return -2
    If the user doesn't have enough money, return -3
    '''
    holdId = countBets() + 1
    if(getBet(currentUser.address) == -1):                            return -1
    if(holdId > 4):                                                   return -2
    if(contract.functions.balanceOf(currentUser.address).call() < 5): return -3

    # approve and execute the hold
    contract.functions.approve(currentUser.address, 5).transact()
    contract.functions.holdFrom(currentUser.address, web3.eth.defaultAccount, 5, holdId).transact()

    # create the bet and add to json file
    bet = Bet(currentUser.name, currentUser.address, holdId)
    with open("bets.json", "r") as file:
        data = json.load(file)
    data.append(bet.__dict__)
    with open("bets.json", "w") as file:
        json.dump(data, file)
    return 0
    
def executeBets():
    '''
    when 4 users participate in 
    the bet the winner can be chosen 
    Return the name of the winner
    '''
    if countBets() < 4: raise Exception('There is not enoug bets')
    winner = random.randint(0, 3)
    with open("bets.json") as betsFile:
        data = betsFile.read()
        bets = json.loads(data, object_hook=decodeBet)

        for bet in bets:
            if not bet.solve:
                contract.functions.executeHold(bet.holdId).transact()
                bet.solve = True
                bet.winner = bets[winner].owner
            
        contract.functions.transfer(bets[winner].address, 20).transact()
        updateBets(bets)
    return bets[winner].owner


##----------------------MAIN----------------------##
def main():
    global currentUser
    initialTransfers()
    begins = True
    while (begins):
        count = countUsers()
        if count >= 10: # if all the addres are assigned it couldn't be possible to register a new user
            answers = prompt(options[1])['theme']
        elif count == 1: # if no user has been registererd it couldn't be possible to log in
            answers = prompt(options[2])['theme']
        else: # there are users registered and there are unassigned addresses 
            answers = prompt(options[0])['theme']

        if answers == options[0]['choices'][0]: # register
            register()
        elif answers == options[0]['choices'][1]: # login
            logIn()
        elif answers == options[0]['choices'][2]: # exit
            begins = False

        if begins:
            logOut = False
            while not logOut:
                print(bcolors.OKCYAN + bcolors.BOLD + "\nYOU ARE IN \"" + currentUser.name + "\" SESSION" + bcolors.BOLD + bcolors.ENDC)
                answers = prompt(options[3])['theme']
            
                if answers == options[3]['choices'][0]: # make a bet
                    result = newBet()
                    if result == -1:
                        print(bcolors.FAIL + bcolors.BOLD + "Sorry, you have a bet of 5 tokens unsolved, please wait other players to bet \n" + bcolors.BOLD + bcolors.ENDC)
                    elif result == 0:
                        print(bcolors.OKGREEN + bcolors.BOLD + "You just bet 5 tokens \n" + bcolors.BOLD + bcolors.ENDC)
                    else: 
                        print(bcolors.FAIL + bcolors.BOLD + "Sorry, you don\'t have enough money to bet \n" + bcolors.BOLD + bcolors.ENDC)
                elif  answers == options[3]['choices'][1]: # execute the bet
                    count = countBets()
                    if count == 4:
                        print(bcolors.OKGREEN + bcolors.BOLD + "There are enough bets, we can play \n" + bcolors.BOLD + bcolors.ENDC)
                        winner = executeBets()
                        print(bcolors.OKGREEN + bcolors.BOLD + "The winner is " + winner + "\n" + bcolors.BOLD + bcolors.ENDC)
                    elif count < 4:
                        print(bcolors.FAIL + bcolors.BOLD + "There aren't enough bets, we need 4 and we have "+ str(count) +"\n" + bcolors.BOLD + bcolors.ENDC)

                elif answers == options[3]['choices'][2]: # see my bets
                    userBets = getUserBets(currentUser)
                    i = 0
                    for bet in userBets:
                        if userBets[i].solve:
                            print(bcolors.OKGREEN + bcolors.BOLD + "In bet " + str(i) + " the winner was " + str(userBets[i].winner) + bcolors.BOLD + bcolors.ENDC)
                        else:
                            print(bcolors.OKGREEN + bcolors.BOLD + "Bet " + str(i) + " is unsolve" + bcolors.BOLD + bcolors.ENDC)
                        i = i + 1
                    print("")
                elif answers ==options[3]['choices'][3]: # see my balance
                    print(bcolors.OKGREEN + bcolors.BOLD + "Your balance is " + str(getBalance(currentUser)) + " tokens \n" + bcolors.BOLD + bcolors.ENDC)
                else: #log out
                    logOut = True
    exit()

if __name__ == "__main__":
    main()
