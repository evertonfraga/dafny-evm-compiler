// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";

contract ConstructorDebugTest is Test {
    function test_DeployWithConstructorArg() public {
        // Read bytecode
        string memory hexCode = vm.readFile("../../output/DafnyToken/DafnyToken.bin");
        console.log("Hex code length:", bytes(hexCode).length);
        
        // Encode constructor arg
        bytes memory constructorArgs = abi.encode(uint256(1_000_000));
        console.log("Constructor args length:", constructorArgs.length);
        console.logBytes(constructorArgs);
        
        // Parse bytecode
        bytes memory bytecode = vm.parseBytes(hexCode);
        console.log("Parsed bytecode length:", bytecode.length);
        
        // Concatenate
        bytes memory fullBytecode = abi.encodePacked(bytecode, constructorArgs);
        console.log("Full bytecode length:", fullBytecode.length);
        
        // Deploy
        address deployed;
        assembly {
            deployed := create(0, add(fullBytecode, 0x20), mload(fullBytecode))
        }
        require(deployed != address(0), "deployment failed");
        console.log("Deployed to:", deployed);
        
        // Check totalSupply
        (bool success, bytes memory data) = deployed.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        console.log("totalSupply() success:", success);
        if (success) {
            uint256 supply = abi.decode(data, (uint256));
            console.log("Total supply:", supply);
            assertEq(supply, 1_000_000, "should be 1M");
        }
    }
}
