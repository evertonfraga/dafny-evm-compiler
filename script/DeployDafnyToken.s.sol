// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

contract DeployDafnyToken is Script {
    function run() external {
        // Read deployment bytecode (path relative to project root)
        string memory path = "output/DafnyToken/DafnyToken.bin";
        bytes memory bytecode = vm.parseBytes(vm.readFile(path));
        
        // Get deployer private key from seed
        string memory seedRaw = vm.readFile(".account.txt");
        // Trim whitespace/newlines
        string memory seed = vm.trim(seedRaw);
        uint256 deployerPrivateKey = vm.deriveKey(seed, 0);
        address deployer = vm.addr(deployerPrivateKey);
        
        console.log("Deploying from:", deployer);
        console.log("Balance:", deployer.balance);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Constructor parameter: initialSupply = 1,000,000 tokens
        uint256 initialSupply = 1_000_000;
        bytes memory constructorArgs = abi.encode(initialSupply);
        bytes memory deploymentBytecode = abi.encodePacked(bytecode, constructorArgs);
        
        // Deploy contract
        address deployed;
        assembly {
            deployed := create(0, add(deploymentBytecode, 0x20), mload(deploymentBytecode))
        }
        require(deployed != address(0), "Deployment failed");
        
        console.log("DafnyToken (DFY) deployed to:", deployed);
        console.log("Initial supply:", initialSupply);
        
        vm.stopBroadcast();
    }
}
