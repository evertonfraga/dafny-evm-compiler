// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract SoliditySimpleToken {
    uint256 public totalSupply;
    uint256 public balances;

    constructor() {
        totalSupply = 1000000;
    }

    function transfer(uint256 amount) external returns (bool) {
        require(amount > 0);
        require(amount <= balances);
        balances = balances - amount;
        return true;
    }

    function getBalance() external view returns (uint256) {
        return balances;
    }

    function mint(uint256 amount) external {
        require(amount > 0);
        totalSupply = totalSupply + amount;
        balances = balances + amount;
    }
}
