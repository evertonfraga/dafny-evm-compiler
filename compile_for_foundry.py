#!/usr/bin/env python3
"""Compile Dafny contracts for Foundry integration tests."""

import sys
import subprocess
from pathlib import Path

def compile_contract(dafny_file: str):
    """Compile a Dafny contract, skipping verification."""
    result = subprocess.run(
        ["python3", "cli.py", dafny_file, "--skip-verification"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to compile {dafny_file}")
        print(result.stderr)
        return False
    
    print(f"✅ Compiled {dafny_file}")
    return True

def main():
    contracts = [
        "examples/SimpleToken.dfy",
        "examples/Counter.dfy",
        "examples/MyToken.dfy",
        "examples/ERC20Token.dfy",
    ]
    
    success_count = 0
    for contract in contracts:
        if Path(contract).exists():
            if compile_contract(contract):
                success_count += 1
    
    print(f"\n✅ Compiled {success_count}/{len(contracts)} contracts")

if __name__ == "__main__":
    main()
