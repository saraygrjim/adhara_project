var erc20 = artifacts.require("ERC20");

module.exports = function(deployer) {
    deployer.deploy(erc20, "sarayContract", "symbol", 1000000000);
};
