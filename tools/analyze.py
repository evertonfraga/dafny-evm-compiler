#!/usr/bin/env python3
"""
Analyze compiled bytecode for security and optimization
"""
import sys
from pathlib import Path

def analyze_bytecode(bytecode_hex: str):
    """Analyze EVM bytecode"""
    
    bytecode = bytes.fromhex(bytecode_hex)
    
    analysis = {
        'size': len(bytecode),
        'opcodes': {},
        'storage_ops': 0,
        'memory_ops': 0,
        'jumps': 0,
        'calls': 0,
    }
    
    i = 0
    while i < len(bytecode):
        opcode = bytecode[i]
        
        # Count opcode
        analysis['opcodes'][opcode] = analysis['opcodes'].get(opcode, 0) + 1
        
        # Categorize operations
        if opcode in (0x54, 0x55):  # SLOAD, SSTORE
            analysis['storage_ops'] += 1
        elif opcode in (0x51, 0x52, 0x53):  # MLOAD, MSTORE, MSTORE8
            analysis['memory_ops'] += 1
        elif opcode in (0x56, 0x57, 0x58):  # JUMP, JUMPI, PC
            analysis['jumps'] += 1
        elif opcode in (0xF1, 0xF2, 0xF4, 0xFA):  # CALL, CALLCODE, DELEGATECALL, STATICCALL
            analysis['calls'] += 1
        
        # Handle PUSH opcodes
        if 0x60 <= opcode <= 0x7F:
            push_size = opcode - 0x5F
            i += push_size
        
        i += 1
    
    return analysis

def print_analysis(analysis: dict):
    """Print analysis results"""
    print("=== Bytecode Analysis ===")
    print(f"Size: {analysis['size']} bytes")
    print(f"Storage operations: {analysis['storage_ops']}")
    print(f"Memory operations: {analysis['memory_ops']}")
    print(f"Jumps: {analysis['jumps']}")
    print(f"External calls: {analysis['calls']}")
    print(f"Unique opcodes: {len(analysis['opcodes'])}")
    
    # Gas estimation
    base_gas = 21000
    storage_gas = analysis['storage_ops'] * 20000  # Approximate
    memory_gas = analysis['memory_ops'] * 3
    jump_gas = analysis['jumps'] * 8
    
    estimated_gas = base_gas + storage_gas + memory_gas + jump_gas
    print(f"\nEstimated execution gas: {estimated_gas}")
    
    # Security checks
    print("\n=== Security Checks ===")
    if analysis['calls'] > 0:
        print("⚠️  Contains external calls - review for reentrancy")
    else:
        print("✓ No external calls")
    
    if analysis['storage_ops'] > 10:
        print("⚠️  High storage operations - consider optimization")
    else:
        print("✓ Reasonable storage usage")
    
    if analysis['size'] > 24576:
        print("❌ Exceeds contract size limit (24KB)")
    else:
        print(f"✓ Within size limit ({analysis['size']}/24576 bytes)")

def compare_bytecodes(file1: str, file2: str):
    """Compare two bytecode files"""
    with open(file1, 'r') as f:
        bc1 = f.read().strip()
    with open(file2, 'r') as f:
        bc2 = f.read().strip()
    
    print(f"File 1: {len(bc1)//2} bytes")
    print(f"File 2: {len(bc2)//2} bytes")
    print(f"Difference: {abs(len(bc1) - len(bc2))//2} bytes")
    
    if bc1 == bc2:
        print("✓ Bytecodes are identical")
    else:
        print("⚠️  Bytecodes differ")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze EVM bytecode')
    parser.add_argument('bytecode', help='Path to .bin file')
    parser.add_argument('--compare', help='Compare with another bytecode file')
    
    args = parser.parse_args()
    
    with open(args.bytecode, 'r') as f:
        bytecode = f.read().strip()
    
    analysis = analyze_bytecode(bytecode)
    print_analysis(analysis)
    
    if args.compare:
        print("\n=== Comparison ===")
        compare_bytecodes(args.bytecode, args.compare)
