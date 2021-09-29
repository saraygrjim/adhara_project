import sys
sys.path.insert(0, '.')
from back import *

def main():
    users = loadUsers()
    size = len(users)

    if len(users) < 9:
        for i in range(0,9-size):
            users.append( User("user"+ str(i + size) , newUser("user"+str(i))))

    count = 0
    for user in users:
        if (random.randint(0, 1) == 0) and count < 4:
            count = count + 1
            print("User " + user.name + " has " + str(getBalance(user.address)) + " tokens")
            print("User " + user.name + " make a bet")
            makeBet(user.address)
            print("User " + user.name + " has " + str(getBalance(user.address)) + " tokens\n")
    
    winner = executeBet()

    for user in users:
        if user.address == winner:
            print("The winner is " + user.name)

    for user in users:
        print("User " + user.name + " has " + str(getBalance(user.address)) + " tokens")
        bets = getBets(user.address)
        if len(bets) == 0:
            print("The user hasn't bet yet\n")
        else:
            print("The bets of "  + user.name + " are " )
            for bet in bets:
                print(str(bet))
        
            print("")

if __name__ == "__main__":
    main()


