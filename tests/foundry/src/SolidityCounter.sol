// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract SolidityCounter {
    uint256 public count;
    uint256 public maxValue;

    constructor() {
        count = 0;
        maxValue = 1000;
    }

    function increment() external returns (uint256) {
        require(count < maxValue);
        count = count + 1;
        return count;
    }

    function decrement() external returns (uint256) {
        require(count > 0);
        count = count - 1;
        return count;
    }

    function reset() external {
        count = 0;
    }

    function getCount() external view returns (uint256) {
        return count;
    }

    function setMaxValue(uint256 newMax) external {
        require(newMax >= count);
        maxValue = newMax;
    }
}
