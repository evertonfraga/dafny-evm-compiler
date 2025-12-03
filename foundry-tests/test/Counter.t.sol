// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract CounterTest is Test {
    address counter;
    
    function setUp() public {
        // Deploy Counter (constructor runs during deployment)
        string memory path = "../output/Counter/Counter.bin";
        string memory hexCode = vm.readFile(path);
        bytes memory bytecode = vm.parseBytes(hexCode);
        
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "deployment failed");
        counter = deployed;
    }
    
    function testInitialValue() public view {
        (bool success, bytes memory data) = counter.staticcall(
            abi.encodeWithSignature("getCount()")
        );
        assertTrue(success, "getCount should succeed");
        uint256 value = abi.decode(data, (uint256));
        assertEq(value, 0, "initial count should be 0");
    }
    
    function testIncrement() public {
        // Increment
        (bool success, bytes memory data) = counter.call(
            abi.encodeWithSignature("increment()")
        );
        assertTrue(success, "increment should succeed");
        uint256 newCount = abi.decode(data, (uint256));
        assertEq(newCount, 1, "increment should return 1");
        
        // Check value
        (bool success2, bytes memory data2) = counter.staticcall(
            abi.encodeWithSignature("getCount()")
        );
        assertTrue(success2, "getCount should succeed");
        uint256 value = abi.decode(data2, (uint256));
        assertEq(value, 1, "count should be 1 after increment");
    }
    
    function testMultipleIncrements() public {
        for (uint i = 0; i < 5; i++) {
            (bool success,) = counter.call(abi.encodeWithSignature("increment()"));
            assertTrue(success, "increment should succeed");
        }
        
        (bool success, bytes memory data) = counter.staticcall(
            abi.encodeWithSignature("getCount()")
        );
        assertTrue(success);
        uint256 value = abi.decode(data, (uint256));
        assertEq(value, 5, "count should be 5 after 5 increments");
    }
    
    function testReset() public {
        // Increment a few times
        counter.call(abi.encodeWithSignature("increment()"));
        counter.call(abi.encodeWithSignature("increment()"));
        
        // Reset
        (bool success,) = counter.call(abi.encodeWithSignature("reset()"));
        assertTrue(success, "reset should succeed");
        
        // Check value is 0
        (, bytes memory data) = counter.staticcall(
            abi.encodeWithSignature("getCount()")
        );
        uint256 value = abi.decode(data, (uint256));
        assertEq(value, 0, "count should be 0 after reset");
    }
}
