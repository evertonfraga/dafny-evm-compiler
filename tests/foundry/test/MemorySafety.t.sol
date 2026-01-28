// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract MemorySafetyTest is Test {
    address dafnyToken;
    
    function setUp() public {
        // Deploy Dafny-compiled SimpleToken
        dafnyToken = deployBytecode("../../output/SimpleToken/SimpleToken.bin");
    }
    
    function deployBytecode(string memory path) internal returns (address) {
        bytes memory bytecode = vm.parseBytes(vm.readFile(path));
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "deployment failed");
        return deployed;
    }
    
    // Test 1: Normal function call should work
    function test_NormalCallWorks() public {
        // Mint some tokens first
        (bool success,) = dafnyToken.call(abi.encodeWithSignature("mint(uint256)", 1000));
        assertTrue(success, "mint should succeed");
        
        // Get balance
        (bool success2, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("getBalance()")
        );
        assertTrue(success2, "getBalance should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 1000, "should have 1000 tokens");
    }
    
    // Test 2: Truncated calldata should be rejected
    function test_TruncatedCalldataRejected() public {
        // Mint some tokens first
        dafnyToken.call(abi.encodeWithSignature("mint(uint256)", 1000));
        
        // Call transfer with only selector, no amount parameter (should be rejected)
        bytes4 selector = bytes4(keccak256("transfer(uint256)"));
        console.log("Selector:", uint32(selector));
        (bool success, bytes memory data) = address(dafnyToken).call(
            abi.encodePacked(selector)
        );
        console.log("Success:", success);
        console.log("Data length:", data.length);
        assertFalse(success, "truncated calldata should fail");
        assertEq(data.length, 0, "should revert with no data");
    }
    
    // Test 3: Empty calldata should be rejected
    function test_EmptyCalldataRejected() public {
        // Call with no calldata (should be rejected)
        (bool success, bytes memory data) = address(dafnyToken).call("");
        assertFalse(success, "empty calldata should fail");
        assertEq(data.length, 0, "should revert with no data");
    }
    
    // Test 4: Verify memory allocation doesn't collide
    function test_MultipleReturnsNoCollision() public {
        // Mint tokens
        dafnyToken.call(abi.encodeWithSignature("mint(uint256)", 1000));
        
        // Multiple rapid calls shouldn't cause memory corruption
        for (uint i = 0; i < 10; i++) {
            (bool success, bytes memory data) = dafnyToken.staticcall(
                abi.encodeWithSignature("getBalance()")
            );
            assertTrue(success, "getBalance should succeed");
            uint256 balance = abi.decode(data, (uint256));
            assertEq(balance, 1000, "balance should remain consistent");
        }
    }
}
