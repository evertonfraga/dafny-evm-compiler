from typing import List
from ..parser.dafny_ast import *

class YulGenerator:
    def __init__(self):
        self.indent_level = 0
        self.storage_slots = {}
        self.next_slot = 0
        self.event_signatures = {}
        self.error_signatures = {}
        self.current_method = None  # Track current method for return handling
        self.yul_builtins = {
            'add', 'sub', 'mul', 'div', 'mod', 'lt', 'gt', 'eq',
            'iszero', 'and', 'or', 'xor', 'not', 'shl', 'shr', 'sar',
            'keccak256', 'address', 'balance', 'origin', 'caller',
            'callvalue', 'calldataload', 'calldatasize', 'calldatacopy',
            'codesize', 'codecopy', 'gasprice', 'extcodesize', 'extcodecopy',
            'returndatasize', 'returndatacopy', 'extcodehash', 'create',
            'create2', 'call', 'callcode', 'delegatecall', 'staticcall',
            'return', 'revert', 'selfdestruct', 'invalid', 'log0', 'log1',
            'log2', 'log3', 'log4', 'chainid', 'basefee', 'pop', 'mload',
            'mstore', 'mstore8', 'sload', 'sstore', 'msize', 'gas',
            'jumpi', 'pc', 'timestamp', 'number', 'difficulty', 'gaslimit',
            'coinbase', 'byte', 'signextend', 'addmod', 'mulmod', 'exp',
            'sdiv', 'smod', 'slt', 'sgt', 'sha3', 'stop'
        }
    
    def _safe_method_name(self, name: str) -> str:
        """Ensure method name doesn't conflict with Yul builtins"""
        if name.lower() in self.yul_builtins:
            return f"fn_{name}"
        return name
    
    def generate(self, contract: Contract) -> str:
        # Reset state for deterministic compilation
        self.storage_slots = {}
        self.next_slot = 0
        self.event_signatures = {}
        self.error_signatures = {}
        self.struct_layouts = {}
        self.contract = contract  # Store contract for modifier access
        self.constants = contract.constants  # Store ghost constants
        
        self._compute_struct_layouts(contract.structs)
        self._allocate_storage(contract.fields)
        self._compute_event_signatures(contract.events)
        self._compute_error_signatures(contract.errors)
        
        yul_code = f"object \"{contract.name}\" {{\n"
        yul_code += f"  code {{\n"
        yul_code += self._generate_constructor(contract)
        yul_code += f"    datacopy(0, dataoffset(\"runtime\"), datasize(\"runtime\"))\n"
        yul_code += f"    return(0, datasize(\"runtime\"))\n"
        yul_code += f"  }}\n"
        yul_code += f"  object \"runtime\" {{\n"
        yul_code += f"    code {{\n"
        yul_code += self._generate_dispatcher(contract.methods)
        yul_code += self._generate_methods(contract.methods)
        yul_code += f"    }}\n"
        yul_code += f"  }}\n"
        yul_code += f"}}\n"
        
        return yul_code
    
    def _allocate_storage(self, fields: List[Variable]):
        # Use declaration order, not alphabetical
        for field in fields:
            if field.type.base == Type.STRUCT:
                # Structs take multiple slots based on field count
                struct_name = field.type.struct_name
                if struct_name in self.struct_layouts:
                    field_count = len(self.struct_layouts[struct_name])
                    self.storage_slots[field.name] = self.next_slot
                    self.next_slot += field_count
                else:
                    self.storage_slots[field.name] = self.next_slot
                    self.next_slot += 1
            else:
                self.storage_slots[field.name] = self.next_slot
                self.next_slot += 1
    
    def _compute_struct_layouts(self, structs: List[Struct]):
        for struct in structs:
            layout = {}
            for i, field in enumerate(struct.fields):
                layout[field.name] = i
            self.struct_layouts[struct.name] = layout
    
    def _compute_event_signatures(self, events: List[Event]):
        from Crypto.Hash import keccak
        for event in events:
            param_types = ','.join(self._type_to_solidity(p.type) for p in event.params)
            signature = f"{event.name}({param_types})"
            k = keccak.new(digest_bits=256)
            k.update(signature.encode())
            self.event_signatures[event.name] = '0x' + k.hexdigest()
    
    def _compute_error_signatures(self, errors: List[CustomError]):
        from Crypto.Hash import keccak
        for error in errors:
            param_types = ','.join(self._type_to_solidity(p.type) for p in error.params)
            signature = f"{error.name}({param_types})"
            k = keccak.new(digest_bits=256)
            k.update(signature.encode())
            # Error selector is first 4 bytes
            self.error_signatures[error.name] = '0x' + k.hexdigest()[:8]
    
    def _generate_constructor(self, contract: Contract) -> str:
        code = ""
        
        # Check if constructor uses mappings/arrays (needs helper functions)
        needs_helpers = False
        if contract.constructor:
            for stmt in contract.constructor.body:
                if isinstance(stmt, Assignment):
                    if stmt.index or stmt.indices:
                        needs_helpers = True
                        break
                    # Check if value is a MapUpdate (functional syntax)
                    if isinstance(stmt.value, MapUpdate):
                        needs_helpers = True
                        break
        
        # Add helper functions if needed
        if needs_helpers:
            code += "    function keccak256_mapping(slot, key) -> result {\n"
            code += "      mstore(0, slot)\n"
            code += "      mstore(32, key)\n"
            code += "      result := keccak256(0, 64)\n"
            code += "    }\n\n"
        
        # Initialize all fields to 0 first
        for field in contract.fields:
            code += f"    sstore({self.storage_slots[field.name]}, 0)\n"
        
        # Execute constructor body if present
        if contract.constructor:
            # Load constructor parameters from calldata
            offset = 0
            for param in contract.constructor.params:
                code += f"    let {param.name} := calldataload({offset})\n"
                offset += 32
            
            for stmt in contract.constructor.body:
                code += self._generate_statement(stmt, 2)
        
        return code
    
    def _generate_dispatcher(self, methods: List[Method]) -> str:
        code = ""
        
        # Check for receive function (no calldata, has value)
        if self.contract.receive_method:
            code += "      if and(iszero(calldatasize()), callvalue()) {\n"
            code += "        receive_fn()\n"
            code += "        return(0, 0)\n"
            code += "      }\n"
        
        # Check for fallback function (no matching selector or no calldata)
        has_fallback = self.contract.fallback_method is not None
        
        code += "      let selector := shr(224, calldataload(0))\n"
        
        for method in methods:
            if method.is_public:
                sig = self._method_signature(method)
                selector = self._compute_selector(sig)
                safe_name = self._safe_method_name(method.name)
                code += f"      if eq(selector, {selector}) {{\n"
                code += f"        {safe_name}()\n"
                code += f"      }}\n"
        
        if has_fallback:
            code += "      fallback_fn()\n"
        else:
            code += "      revert(0, 0)\n"
        
        code += "\n"
        return code
    
    def _generate_methods(self, methods: List[Method]) -> str:
        code = ""
        # Add helper function for mapping storage
        code += "      function keccak256_mapping(slot, key) -> result {\n"
        code += "        mstore(0, slot)\n"
        code += "        mstore(32, key)\n"
        code += "        result := keccak256(0, 64)\n"
        code += "      }\n\n"
        
        # Add helper for keccak256 hash
        code += "      function keccak256_hash(value) -> result {\n"
        code += "        mstore(0, value)\n"
        code += "        result := keccak256(0, 32)\n"
        code += "      }\n\n"
        
        # Add helper for array base location
        code += "      function keccak256_single(slot) -> result {\n"
        code += "        mstore(0, slot)\n"
        code += "        result := keccak256(0, 32)\n"
        code += "      }\n\n"
        
        # Generate receive function if present
        if self.contract.receive_method:
            code += self._generate_special_function(self.contract.receive_method, "receive_fn")
        
        # Generate fallback function if present
        if self.contract.fallback_method:
            code += self._generate_special_function(self.contract.fallback_method, "fallback_fn")
        
        for method in methods:
            code += self._generate_method(method)
        return code
    
    def _generate_special_function(self, method: Method, fn_name: str) -> str:
        code = f"      function {fn_name}() {{\n"
        
        # Generate body (indent level 4 for inside function)
        for stmt in method.body:
            code += self._generate_statement(stmt, indent=4)
        
        code += "      }\n\n"
        return code
    
    def _generate_method(self, method: Method) -> str:
        self.current_method = method  # Set context
        safe_name = self._safe_method_name(method.name)
        
        # For internal/private methods, generate proper function signatures with returns
        is_internal = method.visibility in ['internal', 'private']
        
        if is_internal:
            # Generate internal function with parameters and return values
            params = ', '.join(param.name for param in method.params)
            
            returns_sig = ""
            if method.returns:
                if isinstance(method.returns, list):
                    return_names = ', '.join(self._safe_method_name(r.name) for r in method.returns)
                    returns_sig = f" -> {return_names}"
                else:
                    # Single unnamed return
                    returns_sig = " -> result"
            
            code = f"      function {safe_name}({params}){returns_sig} {{\n"
        else:
            # External/public methods use calldata
            code = f"      function {safe_name}() {{\n"
        
        # Non-payable check (only for external/public)
        if not is_internal and not method.is_payable:
            code += f"        if callvalue() {{ revert(0, 0) }}\n"
        
        # Load parameters from calldata (only for external/public)
        if not is_internal:
            offset = 4
            for i, param in enumerate(method.params):
                code += f"        let {param.name} := calldataload({offset})\n"
                offset += 32
        
        # Declare return variables if they have names (only for external/public)
        if not is_internal and method.returns:
            if isinstance(method.returns, list):
                for ret_var in method.returns:
                    var_name = self._safe_method_name(ret_var.name)
                    code += f"        let {var_name} := 0\n"
        
        # Inject modifier checks
        if hasattr(method, 'modifiers') and method.modifiers:
            for modifier_name in method.modifiers:
                # Find the modifier in the contract
                if hasattr(self, 'contract') and self.contract.modifiers:
                    for modifier in self.contract.modifiers:
                        if modifier.name == modifier_name:
                            # Inject modifier body (requires statements)
                            for stmt in modifier.body:
                                if isinstance(stmt, Require):
                                    code += f"        if iszero({self._generate_expr(stmt.condition)}) {{ revert(0, 0) }}\n"
        
        for precond in method.preconditions:
            code += f"        if iszero({self._generate_expr(precond)}) {{ revert(0, 0) }}\n"
        
        for stmt in method.body:
            code += self._generate_statement(stmt, 2)
        
        # Add implicit return for void methods (no explicit return in body)
        has_return = any(isinstance(stmt, Return) for stmt in method.body)
        if not has_return and not is_internal:
            # Only add implicit returns for external/public methods
            if method.returns:
                # Has return type but no return statement - return default values
                if isinstance(method.returns, list):
                    code += "    mstore(0, 0)\n"
                    code += f"    return(0, {len(method.returns) * 32})\n"
                else:
                    code += "    mstore(0, 0)\n"
                    code += "    return(0, 32)\n"
            else:
                # Void method - return empty
                code += "    return(0, 0)\n"
        
        code += f"      }}\n\n"
        self.current_method = None  # Clear context
        return code
    
    def _generate_statement(self, stmt: Statement, indent: int) -> str:
        ind = "  " * indent
        
        if isinstance(stmt, VarDecl):
            init = self._generate_expr(stmt.init) if stmt.init else "0"
            
            # Handle if expressions
            if init.startswith("IF_EXPR("):
                # Extract: IF_EXPR(cond, then, else) - handle nested parens/commas
                depth = 0
                parts = []
                current = ""
                for i, char in enumerate(init[8:-1]):  # Skip "IF_EXPR(" and ")"
                    if char in '([':
                        depth += 1
                        current += char
                    elif char in ')]':
                        depth -= 1
                        current += char
                    elif char == ',' and depth == 0:
                        parts.append(current.strip())
                        current = ""
                    else:
                        current += char
                if current:
                    parts.append(current.strip())
                
                if len(parts) == 3:
                    cond, then_val, else_val = parts
                    code = f"{ind}let {stmt.var.name} := 0\n"
                    code += f"{ind}if {cond} {{ {stmt.var.name} := {then_val} }}\n"
                    code += f"{ind}if iszero({cond}) {{ {stmt.var.name} := {else_val} }}\n"
                    return code
            
            return f"{ind}let {stmt.var.name} := {init}\n"
        
        if isinstance(stmt, Assignment):
            # Check if value is a functional map update: map := map[key := value]
            if isinstance(stmt.value, MapUpdate):
                # Convert functional update to imperative assignment
                # Extract all updates from nested MapUpdate structure
                updates = []
                current = stmt.value
                while isinstance(current, MapUpdate):
                    updates.append((current.key, current.value))
                    if isinstance(current.base, MapUpdate):
                        current = current.base
                    else:
                        break
                
                # Generate imperative assignments
                # For: map := map[k1 := v1][k2 := v2]
                # Generate: sstore(keccak256(slot, k1), v1); sstore(keccak256(slot, k2), v2)
                code = ""
                slot = self.storage_slots.get(stmt.target, 0)
                
                # Reverse to process innermost first
                for key_expr, val_expr in reversed(updates):
                    key = self._generate_expr(key_expr)
                    value = self._generate_expr(val_expr)
                    
                    # Check if this is a nested map update (value is MapUpdate)
                    if isinstance(val_expr, MapUpdate):
                        # Nested: allowances[owner := allowances[owner][spender := amount]]
                        # First level: owner -> inner map
                        # Second level: spender -> amount
                        inner_updates = []
                        inner_current = val_expr
                        while isinstance(inner_current, MapUpdate):
                            inner_updates.append((inner_current.key, inner_current.value))
                            if isinstance(inner_current.base, MapUpdate):
                                inner_current = inner_current.base
                            else:
                                break
                        
                        # Generate nested storage access
                        for inner_key_expr, inner_val_expr in reversed(inner_updates):
                            inner_key = self._generate_expr(inner_key_expr)
                            inner_value = self._generate_expr(inner_val_expr)
                            storage_loc = f"keccak256_mapping(keccak256_mapping({slot}, {key}), {inner_key})"
                            code += f"{ind}sstore({storage_loc}, {inner_value})\n"
                    else:
                        # Simple update
                        storage_loc = f"keccak256_mapping({slot}, {key})"
                        code += f"{ind}sstore({storage_loc}, {value})\n"
                
                return code
            
            if stmt.indices:  # Nested mapping/array assignment: arr[i][j] := value
                slot = self.storage_slots.get(stmt.target, 0)
                # Compute nested storage location
                # For allowances[owner][spender], compute: keccak256(keccak256(slot, owner), spender)
                storage_loc = str(slot)
                for idx in stmt.indices:
                    key = self._generate_expr(idx)
                    storage_loc = f"keccak256_mapping({storage_loc}, {key})"
                value = self._generate_expr(stmt.value)
                return f"{ind}sstore({storage_loc}, {value})\n"
            elif stmt.index:  # Single-level array/mapping assignment
                slot = self.storage_slots.get(stmt.target, 0)
                key = self._generate_expr(stmt.index)
                value = self._generate_expr(stmt.value)
                return f"{ind}sstore(keccak256_mapping({slot}, {key}), {value})\n"
            elif '.' in stmt.target:  # Struct field assignment
                parts = stmt.target.split('.')
                if len(parts) == 2:
                    struct_name, field_name = parts
                    base_slot = self.storage_slots.get(struct_name, 0)
                    # Find field offset
                    for struct_type, layout in self.struct_layouts.items():
                        if field_name in layout:
                            offset = layout[field_name]
                            value = self._generate_expr(stmt.value)
                            return f"{ind}sstore({base_slot + offset}, {value})\n"
                    # Fallback
                    value = self._generate_expr(stmt.value)
                    return f"{ind}sstore({base_slot}, {value})\n"
            elif stmt.target in self.storage_slots:
                value_expr = self._generate_expr(stmt.value)
                # Skip map[] initialization - mappings are implicit in EVM
                if value_expr == "map[]":
                    return ""
                return f"{ind}sstore({self.storage_slots[stmt.target]}, {value_expr})\n"
            else:
                return f"{ind}{stmt.target} := {self._generate_expr(stmt.value)}\n"
        
        if isinstance(stmt, EmitEvent):
            if stmt.name in self.event_signatures:
                event = None
                for e in self.contract.events:
                    if e.name == stmt.name:
                        event = e
                        break
                
                if event:
                    sig = self.event_signatures[stmt.name]
                    code = ""
                    
                    # Separate indexed and non-indexed params
                    topics = []
                    data_args = []
                    for i, (arg, is_indexed) in enumerate(zip(stmt.args, event.indexed)):
                        if is_indexed:
                            topics.append(self._generate_expr(arg))
                        else:
                            data_args.append(arg)
                    
                    # Store non-indexed data in memory
                    for i, arg in enumerate(data_args):
                        code += f"{ind}mstore({i * 32}, {self._generate_expr(arg)})\n"
                    
                    data_size = len(data_args) * 32
                    
                    # Choose log instruction based on number of topics
                    # log0: no topics, log1: 1 topic (sig), log2: sig + 1 indexed, etc.
                    if event.anonymous:
                        # Anonymous events don't include signature as topic
                        if len(topics) == 0:
                            code += f"{ind}log0(0, {data_size})\n"
                        elif len(topics) == 1:
                            code += f"{ind}log1(0, {data_size}, {topics[0]})\n"
                        elif len(topics) == 2:
                            code += f"{ind}log2(0, {data_size}, {topics[0]}, {topics[1]})\n"
                        elif len(topics) == 3:
                            code += f"{ind}log3(0, {data_size}, {topics[0]}, {topics[1]}, {topics[2]})\n"
                    else:
                        # Regular events include signature as first topic
                        if len(topics) == 0:
                            code += f"{ind}log1(0, {data_size}, {sig})\n"
                        elif len(topics) == 1:
                            code += f"{ind}log2(0, {data_size}, {sig}, {topics[0]})\n"
                        elif len(topics) == 2:
                            code += f"{ind}log3(0, {data_size}, {sig}, {topics[0]}, {topics[1]})\n"
                        elif len(topics) == 3:
                            code += f"{ind}log4(0, {data_size}, {sig}, {topics[0]}, {topics[1]}, {topics[2]})\n"
                    
                    return code
            return ""
        
        if isinstance(stmt, Revert):
            if stmt.error_name and stmt.error_name in self.error_signatures:
                # Custom error: revert ErrorName(args)
                sig = self.error_signatures[stmt.error_name]
                code = f"{ind}mstore(0, {sig})\n"
                # Encode args after selector
                for i, arg in enumerate(stmt.error_args or []):
                    code += f"{ind}mstore({4 + i * 32}, {self._generate_expr(arg)})\n"
                size = 4 + len(stmt.error_args or []) * 32
                code += f"{ind}revert(0, {size})\n"
                return code
            elif stmt.message:
                # Revert with message: encode Error(string) selector + message
                # Error(string) selector is 0x08c379a0
                code = f"{ind}mstore(0, 0x08c379a000000000000000000000000000000000000000000000000000000000)\n"
                # For simplicity, just revert with selector
                code += f"{ind}revert(0, 4)\n"
                return code
            else:
                # Simple revert
                return f"{ind}revert(0, 0)\n"
        
        if isinstance(stmt, Selfdestruct):
            recipient = self._generate_expr(stmt.recipient)
            return f"{ind}selfdestruct({recipient})\n"
        
        if isinstance(stmt, Return):
            # Check if we're in an internal/private method
            is_internal = self.current_method and self.current_method.visibility in ['internal', 'private']
            
            if stmt.value:
                # Check if multiple returns
                if isinstance(stmt.value, list):
                    if is_internal:
                        # For internal methods, assign to return variables
                        code = ""
                        for i, (val, ret_var) in enumerate(zip(stmt.value, self.current_method.returns)):
                            var_name = self._safe_method_name(ret_var.name)
                            code += f"{ind}{var_name} := {self._generate_expr(val)}\n"
                        return code
                    else:
                        # For external methods, use memory and return
                        code = ""
                        for i, val in enumerate(stmt.value):
                            code += f"{ind}mstore({i * 32}, {self._generate_expr(val)})\n"
                        return code + f"{ind}return(0, {len(stmt.value) * 32})\n"
                else:
                    val_expr = self._generate_expr(stmt.value)
                    
                    if is_internal:
                        # For internal methods with single return, assign to result
                        if self.current_method.returns:
                            if isinstance(self.current_method.returns, list) and len(self.current_method.returns) > 0:
                                var_name = self._safe_method_name(self.current_method.returns[0].name)
                                return f"{ind}{var_name} := {val_expr}\n"
                            else:
                                # Unnamed return
                                return f"{ind}result := {val_expr}\n"
                        return ""
                    else:
                        # For external methods, use memory and return
                        # Handle if expressions
                        if val_expr.startswith("IF_EXPR("):
                            depth = 0
                            parts = []
                            current = ""
                            for char in val_expr[8:-1]:  # Skip "IF_EXPR(" and ")"
                                if char in '([':
                                    depth += 1
                                    current += char
                                elif char in ')]':
                                    depth -= 1
                                    current += char
                                elif char == ',' and depth == 0:
                                    parts.append(current.strip())
                                    current = ""
                                else:
                                    current += char
                            if current:
                                parts.append(current.strip())
                            
                            if len(parts) == 3:
                                cond, then_val, else_val = parts
                                code = f"{ind}let _return_val := 0\n"
                                code += f"{ind}if {cond} {{ _return_val := {then_val} }}\n"
                                code += f"{ind}if iszero({cond}) {{ _return_val := {else_val} }}\n"
                                code += f"{ind}mstore(0, _return_val)\n{ind}return(0, 32)\n"
                                return code
                        
                        return f"{ind}mstore(0, {val_expr})\n{ind}return(0, 32)\n"
            
            # No return value
            if is_internal:
                return ""  # Internal functions just exit
            return f"{ind}return(0, 0)\n"
        
        if isinstance(stmt, Assert):
            return f"{ind}if iszero({self._generate_expr(stmt.condition)}) {{ revert(0, 0) }}\n"
        
        if isinstance(stmt, Require):
            return f"{ind}if iszero({self._generate_expr(stmt.condition)}) {{ revert(0, 0) }}\n"
        
        if isinstance(stmt, ArrayPush):
            slot = self.storage_slots.get(stmt.array, 0)
            value = self._generate_expr(stmt.value)
            # Get current length, store value at keccak256(slot) + length, increment length
            code = f"{ind}let len := sload({slot})\n"
            code += f"{ind}sstore(add(keccak256_single({slot}), len), {value})\n"
            code += f"{ind}sstore({slot}, add(len, 1))\n"
            return code
        
        if isinstance(stmt, ArrayPop):
            slot = self.storage_slots.get(stmt.array, 0)
            # Decrement length, delete last element
            code = f"{ind}let len := sload({slot})\n"
            code += f"{ind}if iszero(len) {{ revert(0, 0) }}\n"
            code += f"{ind}let newLen := sub(len, 1)\n"
            code += f"{ind}sstore(add(keccak256_single({slot}), newLen), 0)\n"
            code += f"{ind}sstore({slot}, newLen)\n"
            return code
        
        if isinstance(stmt, IfStatement):
            code = f"{ind}if {self._generate_expr(stmt.condition)} {{\n"
            for s in stmt.then_body:
                code += self._generate_statement(s, indent + 1)
            code += f"{ind}}}\n"
            if stmt.else_body:
                code += f"{ind}if iszero({self._generate_expr(stmt.condition)}) {{\n"
                for s in stmt.else_body:
                    code += self._generate_statement(s, indent + 1)
                code += f"{ind}}}\n"
            return code
        
        if isinstance(stmt, WhileLoop):
            code = f"{ind}for {{ }} {self._generate_expr(stmt.condition)} {{ }} {{\n"
            for s in stmt.body:
                code += self._generate_statement(s, indent + 1)
            code += f"{ind}}}\n"
            return code
        
        if isinstance(stmt, ForLoop):
            code = f"{ind}for {{ "
            if stmt.init:
                # Inline init without newline
                init_code = self._generate_statement(stmt.init, 0).strip()
                code += init_code
            code += f" }} {self._generate_expr(stmt.condition)} {{ "
            if stmt.update:
                # Inline update without newline
                update_code = self._generate_statement(stmt.update, 0).strip()
                code += update_code
            code += f" }} {{\n"
            for s in stmt.body:
                code += self._generate_statement(s, indent + 1)
            code += f"{ind}}}\n"
            return code
        
        return ""
    
    def _generate_expr(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return str(expr.value).lower() if isinstance(expr.value, bool) else str(expr.value)
        
        if isinstance(expr, VarRef):
            # Check if it's a ghost constant
            if hasattr(self, 'constants') and expr.name in self.constants:
                return str(self.constants[expr.name])
            if expr.name in self.storage_slots:
                return f"sload({self.storage_slots[expr.name]})"
            return expr.name
        
        if isinstance(expr, GlobalVar):
            global_map = {
                'msg.sender': 'caller()',
                'msg.value': 'callvalue()',
                'msg.data': 'calldatasize()',
                'msg.sig': 'shr(224, calldataload(0))',
                'tx.origin': 'origin()',
                'tx.gasprice': 'gasprice()',
                'block.timestamp': 'timestamp()',
                'block.number': 'number()',
                'block.difficulty': 'difficulty()',
                'block.gaslimit': 'gaslimit()',
                'block.coinbase': 'coinbase()',
                'block.chainid': 'chainid()',
            }
            return global_map.get(expr.name, '0')
        
        if isinstance(expr, ArrayAccess) or isinstance(expr, MappingAccess):
            # Handle nested access: arr[i][j] becomes nested ArrayAccess
            if isinstance(expr, ArrayAccess) and isinstance(expr.array, (ArrayAccess, MappingAccess)):
                # Nested access - compute recursively
                # First get the inner storage location
                inner_loc = self._generate_expr(expr.array)
                # Then apply this level's index
                key = self._generate_expr(expr.index)
                # If inner_loc is already an sload(), extract the location
                if inner_loc.startswith('sload('):
                    inner_loc = inner_loc[6:-1]  # Remove sload( and )
                return f"sload(keccak256_mapping({inner_loc}, {key}))"
            else:
                # Single level access
                slot = self.storage_slots.get(expr.array if isinstance(expr, ArrayAccess) else expr.mapping, 0)
                key = self._generate_expr(expr.index if isinstance(expr, ArrayAccess) else expr.key)
                # Compute keccak256(slot . key) for storage location
                return f"sload(keccak256_mapping({slot}, {key}))"
        
        if isinstance(expr, StructAccess):
            base_slot = self.storage_slots.get(expr.struct, 0)
            # Find struct type and field offset
            for struct_name, layout in self.struct_layouts.items():
                if expr.field in layout:
                    offset = layout[expr.field]
                    return f"sload({base_slot + offset})"
            return f"sload({base_slot})"
        
        if isinstance(expr, ArrayLength):
            slot = self.storage_slots.get(expr.array, 0)
            return f"sload({slot})"  # Length stored at base slot
        
        if isinstance(expr, ContractCall):
            addr = self._generate_expr(expr.address)
            if expr.method == 'call':
                # call(gas, addr, value, argsOffset, argsSize, retOffset, retSize)
                value = self._generate_expr(expr.value) if expr.value else "0"
                # For simplicity, assume data is already in memory at 0
                return f"call(gas(), {addr}, {value}, 0, 32, 0, 32)"
            elif expr.method == 'delegatecall':
                return f"delegatecall(gas(), {addr}, 0, 32, 0, 32)"
            elif expr.method == 'staticcall':
                return f"staticcall(gas(), {addr}, 0, 32, 0, 32)"
        
        if isinstance(expr, UnaryOp):
            operand = self._generate_expr(expr.operand)
            if expr.op == '!':
                return f"iszero({operand})"
            return operand
        
        if isinstance(expr, IfExpression):
            # Yul doesn't have ternary or if expressions
            # We need to generate a function that returns the value
            # For now, use a workaround: generate inline switch expression
            # This only works in Yul 0.8.0+, otherwise need temp variable
            cond = self._generate_expr(expr.condition)
            then_val = self._generate_expr(expr.then_expr)
            else_val = self._generate_expr(expr.else_expr)
            
            # Use: if condition { result := then } if iszero(condition) { result := else }
            # But since we're in expression context, we need a different approach
            # Generate a unique temp variable name
            import random
            temp_var = f"_if_result_{random.randint(1000, 9999)}"
            
            # This is a hack - we return a placeholder that needs statement context
            # Better: return a special marker that VarDecl/Assignment can expand
            return f"IF_EXPR({cond}, {then_val}, {else_val})"
        
        if isinstance(expr, BinaryOp):
            # Handle 'in' operator for mappings
            if expr.op.strip() == 'in':
                # In EVM, mappings are infinite - all keys exist with default value 0
                # We can't check existence, so we check if value != 0
                # For verification, this is modeled correctly
                # For now, return 1 (true) since mappings are infinite in EVM
                # Better: check if sload(key) != 0
                left = self._generate_expr(expr.left)  # key
                right = expr.right.name if hasattr(expr.right, 'name') else str(expr.right)  # mapping name
                slot = self.storage_slots.get(right, 0)
                # Check if value at key is non-zero
                return f"iszero(iszero(sload(keccak256_mapping({slot}, {left}))))"
            
            left = self._generate_expr(expr.left)
            right = self._generate_expr(expr.right)
            op_map = {
                '+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod',
                '<': 'lt', '>': 'gt', '==': 'eq'
            }
            if expr.op == '!=':
                return f"iszero(eq({left}, {right}))"
            elif expr.op == '<=':
                return f"iszero(gt({left}, {right}))"
            elif expr.op == '>=':
                return f"iszero(lt({left}, {right}))"
            else:
                yul_op = op_map.get(expr.op, expr.op)
                return f"{yul_op}({left}, {right})"
        
        if isinstance(expr, FunctionCall):
            # Built-in functions
            if expr.name == 'keccak256':
                # For single arg, just pass it through - caller handles memory
                args = ', '.join(self._generate_expr(arg) for arg in expr.args)
                return f"keccak256_hash({args})"
            
            builtin_map = {
                'sha256': 'sha256',
                'ripemd160': 'ripemd160',
                'ecrecover': 'ecrecover',
                'addmod': 'addmod',
                'mulmod': 'mulmod',
                'gasleft': 'gas',
            }
            if expr.name in builtin_map:
                if expr.name == 'gasleft':
                    return 'gas()'
                args = ', '.join(self._generate_expr(arg) for arg in expr.args)
                return f"{builtin_map[expr.name]}({args})"
            
            args = ', '.join(self._generate_expr(arg) for arg in expr.args)
            return f"{expr.name}({args})"
        
        return "0"
    
    def _method_signature(self, method: Method) -> str:
        param_types = ','.join(self._type_to_solidity(p.type) for p in method.params)
        return f"{method.name}({param_types})"
    
    def _type_to_solidity(self, dtype: DafnyType) -> str:
        type_map = {
            Type.INT: 'int256',
            Type.UINT256: 'uint256',
            Type.UINT128: 'uint128',
            Type.UINT64: 'uint64',
            Type.UINT32: 'uint32',
            Type.UINT16: 'uint16',
            Type.UINT8: 'uint8',
            Type.INT256: 'int256',
            Type.INT128: 'int128',
            Type.BOOL: 'bool',
            Type.ADDRESS: 'address',
            Type.STRING: 'string',
            Type.BYTES: 'bytes',
            Type.BYTES32: 'bytes32',
        }
        return type_map.get(dtype.base, 'uint256')
    
    def _compute_selector(self, signature: str) -> str:
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256)
        k.update(signature.encode())
        return '0x' + k.hexdigest()[:8]
