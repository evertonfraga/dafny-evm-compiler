#!/usr/bin/env python3
"""
Compile Dafny contracts and prepare them for Hardhat testing
"""
import sys
import json
from pathlib import Path
from src.dafny_compiler import DafnyEVMCompiler

def compile_for_hardhat(dafny_file: str, output_dir: str = "hardhat-tests/contracts-out"):
    """Compile Dafny contract and generate Hardhat-compatible artifacts"""
    compiler = DafnyEVMCompiler(verify=False)
    
    print(f"Compiling {dafny_file}...")
    result = compiler.compile_file(dafny_file, skip_verification=True)
    
    if not result['success']:
        print(f"❌ Compilation failed: {result['error']}")
        return False
    
    contract_name = result['contract_name']
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Parse ABI
    abi = json.loads(result['abi'])
    
    # Create Hardhat-compatible artifact
    artifact = {
        "contractName": contract_name,
        "abi": abi,
        "bytecode": "0x" + result['bytecode'],
        "deployedBytecode": "0x" + result['runtime_bytecode'],
        "linkReferences": {},
        "deployedLinkReferences": {}
    }
    
    # Write artifact
    artifact_file = output_path / f"{contract_name}.json"
    with open(artifact_file, 'w') as f:
        json.dump(artifact, f, indent=2)
    
    print(f"✓ Generated artifact: {artifact_file}")
    print(f"✓ Contract: {contract_name}")
    print(f"✓ Bytecode size: {len(result['bytecode']) // 2} bytes")
    print(f"✓ Functions: {len([x for x in abi if x['type'] == 'function'])}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 compile_for_hardhat.py <dafny_file>")
        sys.exit(1)
    
    success = compile_for_hardhat(sys.argv[1])
    sys.exit(0 if success else 1)
