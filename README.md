# **Adhara Coding Assigment**

## **Implement an improved ERC20 Contract supporting balances on hold** ##

The smart contract is implemented in solidity. The public functions are designed as is said at the comments of the interface provided. 

As the methods transfer() and transferFrom() have the same biehaviour the auxiliary and private method __transfer() is implemented in order to obtain the same process in both public methods.

For the methods hold() and holdFrom() the procedure is the same, an auxiliary and private method __hold() is implemented and both public methods call __hold() to execute the hold.

Also, the private method __aprove() is implemented because not only the public method approve() needs to execute approvals, for example, hold()

## **Implement a simple backend providing some endpoints to interact with the contract** ##

For the backend, two approaches are implemented backend1 and backend2, both of them are implemented in python and all the requirements are in both.

It is necessary in both approaches to first compile and change the address before running the contract

### **Backend1**

The backend 1 is a backend with endpoints, has public and private functions and if you call it in another program you can only execute the functions to create an user, load existing users, make a bet, execute a bet if it is possible, get bets and balance of an user. 

### **Backend2**
The backend 2 is implemented as a util to execute in terminal, in every step the util checks the files bets and users. The user executes the util and selects what to do, so in order to test it you have to run it and go through the different posibilities.

This backend was created due to a bad interpretation of the requeriments of the backend, thast why the code might be less clean than the backend 1 implementation.
