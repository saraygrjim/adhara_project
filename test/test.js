const ERC20 = artifacts.require("ERC20");

contract("ERC20", accounts => {
    const truffleAssert = require('truffle-assertions');
    let instance;
    const zeroAddress = "0x0000000000000000000000000000000000000000";

    beforeEach('should setup the contract instance', async () => {
      instance = await ERC20.deployed();
    });

    it("balanceOf(): should put 1000000000 ERC20 in the first account", async () => {
      const balance = await instance.balanceOf(accounts[0]);
      const balanceExpected = 1000000000;

      assert.equal(balance, balanceExpected, "1000000000 wasn't in the first account");
    });

    it("name(): should put name 'name' in the contract", async () => {
      const name = await instance.name();
      assert.equal(name, 'sarayContract');
    });

    it("symbol(): should put symbol 'symbol' in the contract", async () => {
      const symbol = await instance.symbol();
      assert.equal(symbol, 'symbol');
    });
    
    it('transfer(): should fail because it is not possible to transfer to a zero address', async () => {
      const amount = 10;
      
      await truffleAssert.reverts(instance.transfer(zeroAddress, amount, {
        'from': accounts[0]
      }));
    });

    it('transfer(): should fail because the sender doesn\'t have enough balance', async () => {
      const amount = 10000000000;

      await truffleAssert.reverts(instance.transfer(accounts[1], amount, {'from': accounts[0]}));
    });


    it("transfer(): should return true because of a correct transfer", async () => {
      const amount = 10;
      await instance.transfer(accounts[1], amount);
      const balance = await instance.balanceOf(accounts[1]);
      assert.equal(balance, 10);
    });
    
    it("transfer(): should emmit a Transfer event", async () => {
      const amount = 10;

      const result = await instance.transfer(accounts[1], amount, {'from': accounts[0]});
      truffleAssert.eventEmitted(result, 'Transfer');
    });

    it("approve(): should emmit a Approval event", async () => {
      const amount = 10;

      const result = await instance.approve(accounts[1], amount, {'from': accounts[0]});
      truffleAssert.eventEmitted(result, 'Approval');
    });

    it("approve(): should approve the transaction", async () => {
      const amount = 10;
      const allowanceExpected = 10;

      await instance.approve(accounts[2], amount, {'from': accounts[0]});
      const allowance = await instance.allowance(accounts[0], accounts[2]);

      assert.equal(allowance, allowanceExpected);
    });

    it("approve(): should fail because it is not possible to approve to a zero address ", async () => {
      const amount = 10;
      const holdId = 0;

      await truffleAssert.reverts(instance.approve(zeroAddress, amount, {'from': accounts[0]}));
    });

    it("hold(): should return true because of a correct hold ", async () => {
      const amount = 5;
      const holdId = 0;

      await instance.hold(accounts[1], amount, holdId, {
        'from': accounts[0]
      });
      const result = await instance.getHold(holdId);

      assert.equal(result, true);
    });

    it("hold(): should fail because it is not possible to hold to a zero address ", async () => {
      const amount = 10;
      const holdId = 0;

      await truffleAssert.reverts(instance.hold(zeroAddress, amount, holdId, {
        'from': accounts[0]
      }));
    });

    it('hold(): should fail because the sender doesn\'t have enough balance', async () => {
      const amount = 10000000000;

      await truffleAssert.reverts(instance.hold(accounts[1], amount, 0, {
        'from': accounts[0]
      }));
    });

    it('hold(): should fail because the holdId already exist', async () => {
      const holdId = 5;
      const amount = 1;

      await instance.hold(accounts[1], amount, holdId, {
        'from': accounts[0]
      });

      await truffleAssert.reverts(instance.hold(accounts[1], amount, holdId, {
        'from': accounts[0]
      }));
    });

    it("allowance(): allowance should be equal to 0 because there is not aprove between this two accounts", async () => {
      const result = await instance.allowance(accounts[3], accounts[4]);
      assert.equal(result, 0);
    });

    

    // esta no la hago porque ya se checkea con holdFrom y transferFrom
    // it("should fail because it is not possible to approve from a zero address ", async () => {
    //   const amount = 10;
    //   const holdId = 0;

    //   await truffleAssert.reverts(instance.approve(accounts[1], amount, {'from': zeroAddress}));
    // });


    it("transferFrom(): should return true because of a correct transferFrom ", async () => {
      const amount = 10;
      const balance1Expected = 10;
      const balance2Expected = 10;

      await instance.transferFrom(accounts[1], accounts[2], amount, {
        'from': accounts[0]
      });
      
      const balance1 = await instance.balanceOf(accounts[1]);
      const balance2 = await instance.balanceOf(accounts[2]);
      assert.equal(balance1, balance1Expected);
      assert.equal(balance2, balance2Expected);
    });

    it("transferFrom(): should emmit a Transfer event", async () => {
      const amount = 10;

      const result = await instance.transferFrom(accounts[1], accounts[2], amount);
      truffleAssert.eventEmitted(result, 'Transfer');
    });

    it("transferFrom(): should fail because it is not possible to transfer from a zero address ", async () => {
      const amount = 10;

      await truffleAssert.reverts(instance.transferFrom(zeroAddress, accounts[2], amount, {
        'from': accounts[0]
      }));
    });

    it("transferFrom(): should fail because it is not possible to transfer to a zero address ", async () => {
      const amount = 10;

      await truffleAssert.reverts(instance.transferFrom(accounts[1], zeroAddress, amount, {
        'from': accounts[0]
      }));
    });
    
    it('transferFrom(): should fail because the amount exceeds the allowance', async () => {
      const amount = 100;

      await instance.approve(accounts[3], amount-90, {'from': accounts[0]});
      await truffleAssert.reverts(instance.transferFrom(accounts[1], accounts[3], amount));
    });


    it("holdFrom(): should return true because of a correct holdFrom ", async () => {
      const amount = 10;
      const holdId = 2;

      await instance.transfer(accounts[1], amount);
      await instance.approve(accounts[1], amount, {'from': accounts[0]});
      await instance.holdFrom(accounts[1], accounts[2], amount, holdId);

      const result = await instance.getHold(holdId);

      assert.equal(result, true);
    });

    it("holdFrom(): should fail because it is not possible to hold to a zero address ", async () => {
      const amount = 10;
      const holdId = 2;

      await truffleAssert.reverts(instance.holdFrom(accounts[1], zeroAddress, amount, holdId));
    });

    it("holdFrom(): should fail because it is not possible to hold from a zero address ", async () => {
      const amount = 10;
      const holdId = 2;

      await truffleAssert.reverts(instance.holdFrom(zeroAddress, accounts[1], amount, holdId));
    });

    it('holdFrom(): should fail because the sender doesn\'t have enough balance', async () => {
      const amount = 10000000000;
      const holdId = 2;

      await truffleAssert.reverts(instance.holdFrom(accounts[1], accounts[2], amount, holdId));
    });

    it('holdFrom(): should fail because the holdId already exist', async () => {
      const holdId = 6;
      const amount = 1;

      await instance.transfer(accounts[1], amount);
      await instance.approve(accounts[1], amount, {'from': accounts[0]});
      await instance.holdFrom(accounts[1], accounts[2], amount, holdId);

      await truffleAssert.reverts(instance.holdFrom(accounts[1], accounts[2], amount, holdId));
    });

    it("executeHold(): should return true because of a correct execution of a hold ", async () => {
      const amount = 5;
      const holdId = 50;

      await instance.hold(accounts[4], amount, holdId, {
        'from': accounts[0]
      });
      await instance.executeHold(holdId, {
        'from': accounts[0]
      });

      const finalBalance = await instance.balanceOf(accounts[4]);
      assert.equal(finalBalance.valueOf(), amount);
    });

    it("executeHold(): should emmit a Transfer event", async () => {
      const holdId = 6;

      const result = await instance.executeHold(holdId, {
        'from': accounts[0]
      });
      truffleAssert.eventEmitted(result, 'Transfer');
    });

    it("executeHold(): should fail because the holdId doesnt exist ", async () => {
      const amount = 5;
      const holdId = 20;

      await truffleAssert.reverts(instance.executeHold(holdId, {
        'from': accounts[0]
      }));
    });


    it("executeHold(): should fail because the hold can only be executed by the same address that created the hold ", async () => {
      const amount = 5;
      const holdId = 50;

      await instance.hold(accounts[4], amount, holdId, {
        'from': accounts[0]
      });
      
      await truffleAssert.reverts(instance.executeHold(holdId, {
        'from': accounts[2]
      }));
    });


    it("removeHold(): should return true because of a hold was removed ", async () => {
      const amount = 5;
      const holdId = 51;

      await instance.hold(accounts[5], amount, holdId, {
        'from': accounts[0]
      });
      await instance.removeHold(holdId, {
        'from': accounts[0]
      });

      const hold = await instance.getHold(holdId)
      assert.equal(hold, false);
    });

    it("removeHold(): should fail because the holdId doesnt exist ", async () => {
      const amount = 5;
      const holdId = 20;

      await truffleAssert.reverts(instance.removeHold(holdId, {
        'from': accounts[0]
      }));
    });

    it("removeHold(): should fail because the hold can only be executed by the same address that created the hold ", async () => {
      const amount = 5;
      const holdId = 53;

      await instance.hold(accounts[4], amount, holdId, {
        'from': accounts[0]
      });
      
      await truffleAssert.reverts(instance.removeHold(holdId, {
        'from': accounts[2]
      }));
    });

    it("totalSupply(): total supply should be equal to  1000000000", async () => {
      const totalSupplyExpected = 1000000000;
      const totalSupply = await instance.totalSupply();
      assert.equal(totalSupplyExpected, totalSupply);
    });



// DONE: events emmited
// DONE: check correct name
// DONE: check correct symbol
// DONE: check correct initial balance (check of balanceOf)
// DONE: check correct total supply
// DONE: check correct transfer
// DONE: check transfer and transfer requires
    // DONE: ERC20: transfer from the zero address
    // DONE: ERC20: transfer to the zero address
    // DONE: ERC20: sender doesnt have enough balance
// DONE: check correct hold
// DONE: check hold requires
    // DONE: ERC20: transfer from the zero address
    // DONE: ERC20: transfer to the zero address
    // DONE: ERC20: sender doesnt have enough balance.
    // DONE: ERC20: holdId already exist.
// DONE: check allowance
// DONE: check approve
// DONE: check approve requires
    // DONE: ERC20: approve from the zero address
    // DONE: ERC20: approve to the zero address
// DONE: check transferFrom 
// DONE: check transferFrom requires
    // DONE: ERC20: transfer from the zero address
    // DONE: ERC20: transfer to the zero address
    // DONE: ERC20: sender doesnt have enough balance
    // DONE: ERC20: transfer amount exceeds _allowances
// DONE: check holdFrom
// DONE: check holdFrom requires
    // DONE: ERC20: transfer from the zero address
    // DONE: ERC20: transfer to the zero address
    // DONE: ERC20: sender doesnt have enough balance.
    // DONE: ERC20: holdId already exist.
    // DONE: ERC20: transfer amount exceeds _allowances
// DONE: check executeHold
// DONE: check executeHold requires
    // DONE: ERC20: holdId doesnt exist
    // DONE: ERC20: can only be executed by the same address that created the hold
// DONE: check removeHold
// DONE: check removeHold requires
    // DONE: ERC20: holdId doesnt exist
    // DONE: ERC20: can only be executed by the same address that created the hold  


});


// ERC20.address;
// ERC20.deployed().then(function(instance) { app = instance;});
// app;
// web3.eth.getAccounts().then(function(result) { accounts = result});
// accounts;