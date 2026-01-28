// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract TestPublicVars {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    
    constructor() {
        totalSupply = 1000;
    }
}
