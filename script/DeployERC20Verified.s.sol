// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

contract DeployERC20Verified is Script {
    function run() external {
        // Read deployment bytecode
        string memory path = "../../output/ERC20Verified/ERC20Verified.bin";
        bytes memory bytecode = vm.parseBytes(vm.readFile(path));
        
        // Get deployer private key from seed
        string memory seed = vm.readFile(".account.txt");
        uint256 deployerPrivateKey = vm.deriveKey(seed, 0);
        address deployer = vm.addr(deployerPrivateKey);
        
        console.log("Deploying from:", deployer);
        console.log("Balance:", deployer.balance);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy contract
        address deployed;
        assembly {
            deployed := create(0, add(bytecode, 0x20), mload(bytecode))
        }
        require(deployed != address(0), "Deployment failed");
        
        console.log("ERC20Verified deployed to:", deployed);
        
        // Verify deployment by calling totalSupply()
        (bool success, bytes memory data) = deployed.staticcall(
            abi.encodeWithSignature("totalSupply()")
        );
        require(success, "totalSupply() call failed");
        uint256 supply = abi.decode(data, (uint256));
        console.log("Total supply:", supply);
        
        vm.stopBroadcast();
    }
}
