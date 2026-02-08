// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract SimpleTokenNoConstructorTest is Test {
    address token;
    address owner = address(0x1);
    
    function setUp() public {
        bytes memory bytecode = vm.parseBytes(vm.readFile("../../output/SimpleTokenNoConstructor/SimpleTokenNoConstructor.bin"));
        
        vm.prank(owner);
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "deployment failed");
        token = deployed;
    }
    
    function test_InitialSupply() public {
        (bool success, bytes memory data) = token.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        assertTrue(success, "totalSupply() should succeed");
        uint256 supply = abi.decode(data, (uint256));
        assertEq(supply, 1_000_000, "totalSupply should be 1M");
    }
    
    function test_OwnerBalance() public {
        (bool success, bytes memory data) = token.staticcall(
            abi.encodeWithSignature("balances(address)", owner)
        );
        assertTrue(success, "balances() should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 1_000_000, "owner should have 1M tokens");
    }
}
