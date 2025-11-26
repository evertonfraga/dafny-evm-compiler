"""
ABI (Application Binary Interface) Generator for Dafny EVM Compiler

Generates JSON ABI compatible with Ethereum tools (web3.js, ethers.js, etc.)
"""

import json
import hashlib
from typing import List, Dict, Any
from ..parser.dafny_ast import Contract, Method, Event, Variable, DafnyType, Type

class ABIGenerator:
    def __init__(self):
        pass
    
    def generate(self, contract: Contract) -> str:
        """Generate JSON ABI for a contract"""
        abi = []
        
        # Add constructor if present
        if contract.constructor and contract.constructor.params:
            abi.append({
                "type": "constructor",
                "inputs": [self._param_to_abi(p) for p in contract.constructor.params],
                "stateMutability": "nonpayable"
            })
        else:
            # Default constructor with no parameters
            abi.append({
                "type": "constructor",
                "inputs": [],
                "stateMutability": "nonpayable"
            })
        
        # Add methods
        for method in contract.methods:
            # Only include public and external methods in ABI
            if method.visibility in ['public', 'external']:
                abi.append(self._method_to_abi(method))
        
        # Add events
        for event in contract.events:
            abi.append(self._event_to_abi(event))
        
        return json.dumps(abi, indent=2)
    
    def _method_to_abi(self, method: Method) -> Dict[str, Any]:
        """Convert a Method to ABI function entry"""
        abi_entry = {
            "type": "function",
            "name": method.name,
            "inputs": [self._param_to_abi(p) for p in method.params],
            "outputs": self._returns_to_abi(method.returns),
            "stateMutability": self._get_state_mutability(method)
        }
        
        return abi_entry
    
    def _event_to_abi(self, event: Event) -> Dict[str, Any]:
        """Convert an Event to ABI event entry"""
        inputs = []
        for i, param in enumerate(event.params):
            is_indexed = event.indexed[i] if i < len(event.indexed) else False
            param_abi = self._param_to_abi(param)
            param_abi["indexed"] = is_indexed
            inputs.append(param_abi)
        
        return {
            "type": "event",
            "name": event.name,
            "inputs": inputs,
            "anonymous": False
        }
    
    def _param_to_abi(self, param: Variable) -> Dict[str, Any]:
        """Convert a parameter to ABI input/output format"""
        entry = {
            "name": param.name,
            "type": self._type_to_solidity(param.type),
            "internalType": self._type_to_solidity(param.type)
        }
        
        return entry
    
    def _returns_to_abi(self, returns) -> List[Dict[str, Any]]:
        """Convert return values to ABI outputs"""
        if returns is None:
            return []
        
        # Multiple returns
        if isinstance(returns, list):
            return [self._param_to_abi(r) for r in returns]
        
        # Single return (DafnyType)
        return [{
            "name": "",
            "type": self._type_to_solidity(returns),
            "internalType": self._type_to_solidity(returns)
        }]
    
    def _get_state_mutability(self, method: Method) -> str:
        """Determine state mutability for a method"""
        if method.state_mutability:
            return method.state_mutability
        
        if method.is_payable:
            return "payable"
        
        # Auto-detect view: has returns but no modifies
        if method.returns and not hasattr(method, 'modifies'):
            return "view"
        
        # Default to nonpayable
        return "nonpayable"
    
    def _type_to_solidity(self, dafny_type: DafnyType) -> str:
        """Convert Dafny type to Solidity ABI type"""
        type_map = {
            Type.UINT256: "uint256",
            Type.UINT128: "uint128",
            Type.UINT64: "uint64",
            Type.UINT32: "uint32",
            Type.UINT16: "uint16",
            Type.UINT8: "uint8",
            Type.INT256: "int256",
            Type.INT128: "int128",
            Type.INT: "int256",
            Type.BOOL: "bool",
            Type.ADDRESS: "address",
            Type.STRING: "string",
            Type.BYTES: "bytes",
            Type.BYTES32: "bytes32",
        }
        
        if dafny_type.base == Type.ARRAY:
            elem_type = self._type_to_solidity(dafny_type.element_type)
            return f"{elem_type}[]"
        
        if dafny_type.base == Type.MAPPING:
            # Mappings can't be in ABI (not supported in function parameters)
            return "bytes32"
        
        if dafny_type.base == Type.STRUCT:
            # Structs become tuples in ABI
            return "tuple"
        
        return type_map.get(dafny_type.base, "uint256")
    
    def compute_function_selector(self, method: Method) -> str:
        """Compute the 4-byte function selector for a method"""
        from Crypto.Hash import keccak
        param_types = ','.join(self._type_to_solidity(p.type) for p in method.params)
        signature = f"{method.name}({param_types})"
        k = keccak.new(digest_bits=256)
        k.update(signature.encode())
        return '0x' + k.hexdigest()[:8]
