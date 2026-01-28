// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract SolidityMyToken {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;

    constructor() {
        totalSupply = 1000000;
    }

    function mint(address to, uint256 amount) external {
        require(amount > 0);
        totalSupply = totalSupply + amount;
        balances[to] = balances[to] + amount;
    }

    function balanceOf(address account) external view returns (uint256) {
        return balances[account];
    }
}
