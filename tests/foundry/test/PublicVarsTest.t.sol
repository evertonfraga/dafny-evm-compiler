// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract PublicVarsTest is Test {
    address dafnyContract;
    
    function setUp() public {
        // Deploy Dafny-compiled PublicVarsOnly contract
        dafnyContract = deployBytecode("../../output/PublicVarsOnly/PublicVarsOnly.bin");
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
    
    // Test 1: totalSupply getter should work
    function test_TotalSupplyGetter() public {
        (bool success, bytes memory data) = dafnyContract.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        assertTrue(success, "totalSupply() should succeed");
        uint256 supply = abi.decode(data, (uint256));
        assertEq(supply, 1000000, "totalSupply should be 1000000");
    }
    
    // Test 2: balances getter should work
    function test_BalancesGetter() public {
        address testAddr = address(0x123);
        (bool success, bytes memory data) = dafnyContract.staticcall(
            abi.encodeWithSignature("balances(address)", testAddr)
        );
        assertTrue(success, "balances(address) should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 0, "balance should be 0 for new address");
    }
    
    // Test 3: balances getter with different addresses
    function test_BalancesGetterDifferentAddresses() public {
        address addr1 = address(0x123);
        address addr2 = address(0x456);
        
        (bool success1, bytes memory data1) = dafnyContract.staticcall(
            abi.encodeWithSignature("balances(address)", addr1)
        );
        (bool success2, bytes memory data2) = dafnyContract.staticcall(
            abi.encodeWithSignature("balances(address)", addr2)
        );
        
        assertTrue(success1 && success2, "both calls should succeed");
        uint256 balance1 = abi.decode(data1, (uint256));
        uint256 balance2 = abi.decode(data2, (uint256));
        assertEq(balance1, 0, "first balance should be 0");
        assertEq(balance2, 0, "second balance should be 0");
    }
    
    // Test 4: Invalid function selector should revert
    function test_InvalidSelectorReverts() public {
        (bool success, bytes memory data) = dafnyContract.call(
            abi.encodeWithSelector(bytes4(0xdeadbeef))
        );
        assertFalse(success, "invalid selector should fail");
        assertEq(data.length, 0, "should revert with no data");
    }
}
