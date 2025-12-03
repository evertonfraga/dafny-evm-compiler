// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract SimpleTokenTest is Test {
    address token;
    
    function setUp() public {
        // Deploy SimpleToken (constructor runs during deployment)
        string memory path = "../output/SimpleToken/SimpleToken.bin";
        string memory hexCode = vm.readFile(path);
        bytes memory bytecode = vm.parseBytes(hexCode);
        
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "deployment failed");
        token = deployed;
    }
    
    function testInitialBalance() public view {
        (bool success, bytes memory data) = token.staticcall(
            abi.encodeWithSignature("getBalance()")
        );
        assertTrue(success, "getBalance should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 0, "initial balance should be 0");
    }
    
    function testMint() public {
        // Mint 100 tokens
        (bool success, bytes memory data) = token.call(
            abi.encodeWithSignature("mint(uint256)", 100)
        );
        assertTrue(success, "mint should succeed");
        
        // Check balance
        (bool success2, bytes memory data2) = token.staticcall(
            abi.encodeWithSignature("getBalance()")
        );
        assertTrue(success2, "getBalance should succeed");
        uint256 balance = abi.decode(data2, (uint256));
        assertEq(balance, 100, "balance should be 100 after mint");
    }
    
    function testTransferAfterMint() public {
        // Mint first
        token.call(abi.encodeWithSignature("mint(uint256)", 100));
        
        // Transfer 50
        (bool success, bytes memory data) = token.call(
            abi.encodeWithSignature("transfer(uint256)", 50)
        );
        assertTrue(success, "transfer should succeed");
        bool result = abi.decode(data, (bool));
        assertTrue(result, "transfer should return true");
        
        // Check balance
        (, bytes memory data2) = token.staticcall(
            abi.encodeWithSignature("getBalance()")
        );
        uint256 balance = abi.decode(data2, (uint256));
        assertEq(balance, 50, "balance should be 50 after transfer");
    }
    
    function testTransferFailsWithoutBalance() public {
        // Try to transfer without balance
        (bool success,) = token.call(
            abi.encodeWithSignature("transfer(uint256)", 100)
        );
        assertFalse(success, "transfer should fail without balance");
    }
}
