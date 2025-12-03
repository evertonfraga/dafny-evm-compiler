// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract MyTokenTest is Test {
    address token;
    address alice = address(0x1);
    address bob = address(0x2);
    
    function setUp() public {
        string memory path = "../output/MyToken/MyToken.bin";
        string memory hexCode = vm.readFile(path);
        bytes memory bytecode = vm.parseBytes(hexCode);
        
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "deployment failed");
        token = deployed;
    }
    
    function testMintAndBalanceOf() public {
        // Mint to alice
        (bool success,) = token.call(
            abi.encodeWithSignature("mint(address,uint256)", alice, 1000)
        );
        assertTrue(success, "mint should succeed");
        
        // Check alice's balance
        (bool success2, bytes memory data) = token.staticcall(
            abi.encodeWithSignature("balanceOf(address)", alice)
        );
        assertTrue(success2, "balanceOf should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 1000, "alice should have 1000 tokens");
    }
    
    function testMultipleMints() public {
        // Mint to alice
        token.call(abi.encodeWithSignature("mint(address,uint256)", alice, 500));
        
        // Mint to bob
        token.call(abi.encodeWithSignature("mint(address,uint256)", bob, 300));
        
        // Mint more to alice
        token.call(abi.encodeWithSignature("mint(address,uint256)", alice, 200));
        
        // Check balances
        (, bytes memory aliceData) = token.staticcall(
            abi.encodeWithSignature("balanceOf(address)", alice)
        );
        uint256 aliceBalance = abi.decode(aliceData, (uint256));
        assertEq(aliceBalance, 700, "alice should have 700 tokens");
        
        (, bytes memory bobData) = token.staticcall(
            abi.encodeWithSignature("balanceOf(address)", bob)
        );
        uint256 bobBalance = abi.decode(bobData, (uint256));
        assertEq(bobBalance, 300, "bob should have 300 tokens");
    }
    
    function testBalanceOfUnknownAddress() public view {
        // Check balance of address that never received tokens
        (, bytes memory data) = token.staticcall(
            abi.encodeWithSignature("balanceOf(address)", address(0x999))
        );
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 0, "unknown address should have 0 balance");
    }
}
