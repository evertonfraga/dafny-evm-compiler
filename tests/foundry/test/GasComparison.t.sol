// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {SolidityCounter} from "../src/SolidityCounter.sol";
import {SoliditySimpleToken} from "../src/SoliditySimpleToken.sol";
import {SolidityMyToken} from "../src/SolidityMyToken.sol";

contract GasComparisonTest is Test {
    // Dafny-compiled contracts
    address dafnyCounter;
    address dafnySimpleToken;
    address dafnyMyToken;
    
    // Solidity contracts
    SolidityCounter solCounter;
    SoliditySimpleToken solSimpleToken;
    SolidityMyToken solMyToken;
    
    address alice = address(0x1);

    function setUp() public {
        // Deploy Dafny contracts
        dafnyCounter = deployBytecode("../../output/Counter/Counter.bin");
        dafnySimpleToken = deployBytecode("../../output/SimpleToken/SimpleToken.bin");
        dafnyMyToken = deployBytecode("../../output/MyToken/MyToken.bin");
        
        // Deploy Solidity contracts
        solCounter = new SolidityCounter();
        solSimpleToken = new SoliditySimpleToken();
        solMyToken = new SolidityMyToken();
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

    // ============ Counter Tests ============
    
    function test_Gas_Counter_getCount() public {
        uint256 gasDafny = gasleft();
        dafnyCounter.staticcall(abi.encodeWithSignature("getCount()"));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solCounter.getCount();
        gasSol = gasSol - gasleft();
        
        _logComparison("Counter.getCount", gasDafny, gasSol);
    }
    
    function test_Gas_Counter_increment() public {
        uint256 gasDafny = gasleft();
        dafnyCounter.call(abi.encodeWithSignature("increment()"));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solCounter.increment();
        gasSol = gasSol - gasleft();
        
        _logComparison("Counter.increment", gasDafny, gasSol);
    }
    
    function test_Gas_Counter_decrement() public {
        // Setup: increment first
        dafnyCounter.call(abi.encodeWithSignature("increment()"));
        solCounter.increment();
        
        uint256 gasDafny = gasleft();
        dafnyCounter.call(abi.encodeWithSignature("decrement()"));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solCounter.decrement();
        gasSol = gasSol - gasleft();
        
        _logComparison("Counter.decrement", gasDafny, gasSol);
    }
    
    function test_Gas_Counter_reset() public {
        // Setup: increment first
        dafnyCounter.call(abi.encodeWithSignature("increment()"));
        solCounter.increment();
        
        uint256 gasDafny = gasleft();
        dafnyCounter.call(abi.encodeWithSignature("reset()"));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solCounter.reset();
        gasSol = gasSol - gasleft();
        
        _logComparison("Counter.reset", gasDafny, gasSol);
    }

    // ============ SimpleToken Tests ============
    
    function test_Gas_SimpleToken_getBalance() public {
        uint256 gasDafny = gasleft();
        dafnySimpleToken.staticcall(abi.encodeWithSignature("getBalance()"));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solSimpleToken.getBalance();
        gasSol = gasSol - gasleft();
        
        _logComparison("SimpleToken.getBalance", gasDafny, gasSol);
    }
    
    function test_Gas_SimpleToken_mint() public {
        uint256 gasDafny = gasleft();
        dafnySimpleToken.call(abi.encodeWithSignature("mint(uint256)", 100));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solSimpleToken.mint(100);
        gasSol = gasSol - gasleft();
        
        _logComparison("SimpleToken.mint", gasDafny, gasSol);
    }
    
    function test_Gas_SimpleToken_transfer() public {
        // Setup: mint first
        dafnySimpleToken.call(abi.encodeWithSignature("mint(uint256)", 1000));
        solSimpleToken.mint(1000);
        
        uint256 gasDafny = gasleft();
        dafnySimpleToken.call(abi.encodeWithSignature("transfer(uint256)", 100));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solSimpleToken.transfer(100);
        gasSol = gasSol - gasleft();
        
        _logComparison("SimpleToken.transfer", gasDafny, gasSol);
    }

    // ============ MyToken Tests ============
    
    function test_Gas_MyToken_balanceOf() public {
        uint256 gasDafny = gasleft();
        dafnyMyToken.staticcall(abi.encodeWithSignature("balanceOf(address)", alice));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solMyToken.balanceOf(alice);
        gasSol = gasSol - gasleft();
        
        _logComparison("MyToken.balanceOf", gasDafny, gasSol);
    }
    
    function test_Gas_MyToken_mint() public {
        uint256 gasDafny = gasleft();
        dafnyMyToken.call(abi.encodeWithSignature("mint(address,uint256)", alice, 1000));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solMyToken.mint(alice, 1000);
        gasSol = gasSol - gasleft();
        
        _logComparison("MyToken.mint", gasDafny, gasSol);
    }
    
    function test_Gas_MyToken_mint_existing() public {
        // Setup: mint first to warm storage
        dafnyMyToken.call(abi.encodeWithSignature("mint(address,uint256)", alice, 500));
        solMyToken.mint(alice, 500);
        
        uint256 gasDafny = gasleft();
        dafnyMyToken.call(abi.encodeWithSignature("mint(address,uint256)", alice, 500));
        gasDafny = gasDafny - gasleft();
        
        uint256 gasSol = gasleft();
        solMyToken.mint(alice, 500);
        gasSol = gasSol - gasleft();
        
        _logComparison("MyToken.mint(warm)", gasDafny, gasSol);
    }

    // ============ Helper ============
    
    function _logComparison(string memory fn, uint256 dafny, uint256 sol) internal view {
        int256 diff = int256(dafny) - int256(sol);
        console.log(fn);
        console.log("  Dafny:", dafny);
        console.log("  Solidity:", sol);
        console.log("  Diff:", diff);
    }
}
