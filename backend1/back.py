import json
import random

from web3 import Web3, HTTPProvider
from PyInquirer import prompt, print_json

##----------------------INITIALIZATION OF CONTRACT----------------------##

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path    = '../build/contracts/ERC20.json'
deployed_contract_address = '0xdA89381950F696DA7Fc86B0d8d747D9BddB1b1Af'

with open(compiled_contract_path) as file:
    contract_json = json.load(file)     # load contract info as JSON
    contract_abi = contract_json['abi'] # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
__contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
accounts = web3.eth.get_accounts()



#--------------------------------------------#
#-----------------User Class-----------------#
#--------------------------------------------#
def countUsers():
    with open("users.json") as usersFile:
        data = usersFile.read()
        users = json.loads(data)
        return len(users) + 1

class User:
    def __init__(self, name, address="0"):
        if(address == "0"):
            counter = countUsers()
            self.address  = accounts[counter] 
            self.name     = name
        else:
            if(address in accounts):
                self.address = address
            else:
                raise Exception('Incorrect json file')
            self.name     = name

    def __str__(self):
        return 'User ' + str(self.name) + ' , Address: ' + str(self.address) + '\n'

def __decodeUser(user):
    ''' 
    * Convert json object to user class
    * Returns:
    *   - User object
    * '''
    return User(user["name"], user["address"])

#--------------------------------------------#
#------------------Bet Class-----------------#
#--------------------------------------------#
class Bet:
    def __init__(self, id, address, holdId, solve=False, winner=""):
        self.id      = id
        self.address = address
        self.holdId  = holdId
        self.solve   = solve
        self.winner  = winner

    def __str__(self):
        if self.solve:
            return 'In the bet ' + str(self.id) + ' the winner was ' + str(self.winner)
        else:
            return 'The bet ' + str(self.id) + ' hasn\'t been played yet'

def __decodeBet(bet):
    ''' 
    * Convert json object to bet class
    * Returns:
    *   - Bet object
    '''
    return Bet(bet["id"], bet["address"], bet["holdId"], bet["solve"], bet["winner"])

#--------------------------------------------#
#---------------Private functions------------#
#--------------------------------------------#


def __updateUsers(user):
    '''
    * Add a new user in the json file
    '''
    with open("users.json", "r") as file:
        data = json.load(file)
    data.append(user.__dict__)
    with open("users.json", "w") as file:
        json.dump(data, file)

def __getUser(address):
    '''
    * Return the owner of the address
    * Returns:
    *     - User:     if the user exists
    *     - Value -1: if the user doesnt exist
    '''
    with open("users.json") as usersFile:
        data  = usersFile.read()
        users = json.loads(data, object_hook=__decodeUser)

        for user in users:
            if(user.address == address):
                return user
        return -1

def __countUnsolveBets():
    '''
    * Return how many users have participated 
    * in the current bet 
    '''
    with open("bets.json") as betsFile:
        data    = betsFile.read()
        bets    = json.loads(data, object_hook=__decodeBet)
        counter = 0
        for bet in bets:
            if not bet.solve:
                counter = counter + 1 
        return(counter)

def __countSolveBets():
    '''
    * Return how many users have participated 
    * in the current bet 
    '''
    with open("bets.json") as betsFile:
        data    = betsFile.read()
        bets    = json.loads(data, object_hook=__decodeBet)
        counter = 0
        for bet in bets:
            if bet.solve:
                counter = counter + 1 
        return(counter)


def __getCurrentBet(address):
    '''
    * Return the current bet of the address owner
    * Returns:
    *     - Value -1: There are no bet
    *     - Value  0: The bet
    '''
    with open("bets.json") as betsFile:
        data = betsFile.read()
        bets = json.loads(data, object_hook=__decodeBet)

        for bet in bets:
            if(bet.address == address and bet.solve == False):
                return bet
        return -1


def __updateBets(bets):
    '''
    * Update the bets
    '''
    data = []
    for bet in bets:
        data.append(bet.__dict__)
    with open("bets.json", "w") as file:
        json.dump(data, file)

#--------------------------------------------#
#---------------Public functions-------------#
#--------------------------------------------#

def loadUsers():
    '''
    * Load the users already registeres in users.json
    * Returns the array of users
    '''
    with open("users.json") as usersFile:
        data  = usersFile.read()
        users = json.loads(data, object_hook=__decodeUser)

        return users

def newUser(name):
    '''
    * Create a new user
    * Returns:
    *   - Value -1 :    There are no more address
    *   - user address: Everuthing is correct
    '''
    if countUsers() == len(accounts): return -1
    name     = name
    user     = User(name)
    __updateUsers(user)
    # currentUser = user
    return user.address

def makeBet(address):
    '''
    * Participate in a bet
    * Returns:
    *   - Value 0:  Everything is correct
    *   - Value -1: The user has already participate in this bet
    *   - Value -1: There are already 4 bets
    *   - Value -3: The user doesn't have enough balance
    '''
    holdId = __countUnsolveBets() + 1
    if(__getCurrentBet(address) != -1):                   return -1
    if(holdId > 4):                                       return -2
    if(__contract.functions.balanceOf(address).call() < 5): return -3

    # approve and execute the hold
    __contract.functions.approve(address, 5).transact()
    __contract.functions.holdFrom(address, web3.eth.defaultAccount, 5, holdId).transact()

    user = __getUser(address)
    id = (__countSolveBets()/4) + 1
    # create the bet and add to json file
    bet = Bet(id, user.address, holdId)
    with open("bets.json", "r") as file:
        data = json.load(file)
    data.append(bet.__dict__)
    with open("bets.json", "w") as file:
        json.dump(data, file)
    return 0

def executeBet():
    '''
    * When 4 users participate in the bet the winner can be chosen 
    * Returns:
    *     - Address of the winner: Everything was ok
    *     - Value -1             : There are no enough bets
    '''
    if __countUnsolveBets() < 4: return -1

    winner      = random.randint(0, 3)
    unsolveBets = []
    with open("bets.json") as betsFile:
        data = betsFile.read()
        bets = json.loads(data, object_hook=__decodeBet)

        for bet in bets:
            if not bet.solve:
                unsolveBets.append(bet)
                
        for bet in unsolveBets:
            bets.remove(bet)
            __contract.functions.executeHold(bet.holdId).transact()
            bet.solve = True
            bet.winner = unsolveBets[winner].address
        
        bets.extend(unsolveBets)
        __contract.functions.transfer(unsolveBets[winner].address, 20).transact()
        __updateBets(bets)
    return unsolveBets[winner].address

def getBalance(address):
    '''
    * Return the balance of a user
    '''
    return __contract.functions.balanceOf(address).call()

def getBets(address):
    '''
    * Return all the bets solved and unsolved 
    * of the user
    '''
    with open("bets.json") as betsFile:
        data     = betsFile.read()
        bets     = json.loads(data, object_hook=__decodeBet)
        userBets = []
        for bet in bets:
            if(bet.address == address):
                userBets.append(bet)
        return userBets


for account in accounts:
    if(__contract.functions.balanceOf(account).call() == 0 and __getUser(account) == -1):
        __contract.functions.transfer(account, 100).transact()
    # print(contract.functions.balanceOf(account).call()) 

