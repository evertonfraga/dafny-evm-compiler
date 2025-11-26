#!/usr/bin/env python3
"""
Deployment helper for Dafny-compiled contracts
"""
import sys
import json
from web3 import Web3
from pathlib import Path

def deploy_contract(bytecode_file: str, rpc_url: str, private_key: str):
    """Deploy a compiled contract to Ethereum network"""
    
    # Read bytecode
    with open(bytecode_file, 'r') as f:
        bytecode = f.read().strip()
    
    # Connect to network
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print(f"Failed to connect to {rpc_url}")
        return None
    
    # Setup account
    account = w3.eth.account.from_key(private_key)
    
    # Prepare transaction
    transaction = {
        'from': account.address,
        'data': '0x' + bytecode,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price,
    }
    
    # Sign and send
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        print(f"Contract deployed at: {receipt['contractAddress']}")
        return receipt['contractAddress']
    else:
        print("Deployment failed")
        return None

def estimate_gas(bytecode_file: str):
    """Estimate deployment gas cost"""
    with open(bytecode_file, 'r') as f:
        bytecode = f.read().strip()
    
    # Base cost + per-byte cost
    base_cost = 21000
    byte_cost = len(bytecode) // 2 * 200  # Approximate
    
    total = base_cost + byte_cost
    print(f"Estimated gas: {total}")
    print(f"Bytecode size: {len(bytecode) // 2} bytes")
    
    return total

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Dafny contracts')
    parser.add_argument('bytecode', help='Path to .bin file')
    parser.add_argument('--rpc', help='RPC URL', default='http://localhost:8545')
    parser.add_argument('--key', help='Private key')
    parser.add_argument('--estimate', action='store_true', help='Estimate gas only')
    
    args = parser.parse_args()
    
    if args.estimate:
        estimate_gas(args.bytecode)
    else:
        if not args.key:
            print("Error: --key required for deployment")
            sys.exit(1)
        deploy_contract(args.bytecode, args.rpc, args.key)
