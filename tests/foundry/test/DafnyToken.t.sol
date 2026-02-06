// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract DafnyTokenTest is Test {
    address dafnyToken;
    address owner = address(0x1);
    address alice = address(0x2);
    address bob = address(0x3);
    
    function setUp() public {
        // Deploy with 1M initial supply
        dafnyToken = deployWithConstructor(1_000_000);
    }
    
    function deployWithConstructor(uint256 initialSupply) internal returns (address) {
        bytes memory bytecode = vm.parseBytes(vm.readFile("../../output/DafnyToken/DafnyToken.bin"));
        bytes memory constructorArgs = abi.encode(initialSupply);
        bytes memory deploymentBytecode = abi.encodePacked(bytecode, constructorArgs);
        
        address deployed;
        vm.prank(owner);
        assembly {
            deployed := create(0, add(deploymentBytecode, 0x20), mload(deploymentBytecode))
        }
        require(deployed != address(0), "deployment failed");
        return deployed;
    }
    
    // Test 1: Constructor sets initial supply
    function test_ConstructorSetsInitialSupply() public {
        (bool success, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        assertTrue(success, "totalSupply() should succeed");
        uint256 supply = abi.decode(data, (uint256));
        assertEq(supply, 1_000_000, "totalSupply should be 1M");
    }
    
    // Test 2: Owner receives initial supply
    function test_OwnerReceivesInitialSupply() public {
        (bool success, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("balances(address)", owner)
        );
        assertTrue(success, "balances() should succeed");
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 1_000_000, "owner should have 1M tokens");
    }
    
    // Test 3: Token symbol
    function test_TokenSymbol() public {
        // Check symbol
        (bool success, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("symbol()")
        );
        assertTrue(success, "symbol() should succeed");
        bytes32 symbol = abi.decode(data, (bytes32));
        assertEq(symbol, bytes32("DFY"), "symbol should be DFY");
    }
    
    // Test 4: Mint increases supply and balance
    function test_MintIncreasesSupplyAndBalance() public {
        vm.prank(alice);
        (bool success,) = dafnyToken.call(
            abi.encodeWithSignature("mint(uint256)", 500)
        );
        assertTrue(success, "mint should succeed");
        
        // Check alice's balance
        (, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("balances(address)", alice)
        );
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 500, "alice should have 500 tokens");
        
        // Check total supply
        (, data) = dafnyToken.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        uint256 supply = abi.decode(data, (uint256));
        assertEq(supply, 1_000_500, "totalSupply should be 1M + 500");
    }
    
    // Test 5: Burn decreases supply and balance
    function test_BurnDecreasesSupplyAndBalance() public {
        // First mint some tokens to alice
        vm.prank(alice);
        dafnyToken.call(abi.encodeWithSignature("mint(uint256)", 1000));
        
        // Then burn 300
        vm.prank(alice);
        (bool success,) = dafnyToken.call(
            abi.encodeWithSignature("burn(uint256)", 300)
        );
        assertTrue(success, "burn should succeed");
        
        // Check alice's balance
        (, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("balances(address)", alice)
        );
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 700, "alice should have 700 tokens");
        
        // Check total supply
        (, data) = dafnyToken.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        uint256 supply = abi.decode(data, (uint256));
        assertEq(supply, 1_000_700, "totalSupply should be 1M + 700");
    }
    
    // Test 6: Transfer works
    function test_Transfer() public {
        vm.prank(owner);
        (bool success,) = dafnyToken.call(
            abi.encodeWithSignature("transfer(address,uint256)", bob, 100)
        );
        assertTrue(success, "transfer should succeed");
        
        // Check bob's balance
        (, bytes memory data) = dafnyToken.staticcall(
            abi.encodeWithSignature("balances(address)", bob)
        );
        uint256 balance = abi.decode(data, (uint256));
        assertEq(balance, 100, "bob should have 100 tokens");
        
        // Check owner's balance
        (, data) = dafnyToken.staticcall(
            abi.encodeWithSignature("balances(address)", owner)
        );
        balance = abi.decode(data, (uint256));
        assertEq(balance, 999_900, "owner should have 999,900 tokens");
    }
    
    // Test 7: Cannot burn more than balance
    function test_CannotBurnMoreThanBalance() public {
        vm.prank(alice);
        dafnyToken.call(abi.encodeWithSignature("mint(uint256)", 100));
        
        vm.prank(alice);
        (bool success,) = dafnyToken.call(
            abi.encodeWithSignature("burn(uint256)", 200)
        );
        assertFalse(success, "burn should fail when amount > balance");
    }
}
