from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from enum import Enum

class Type(Enum):
    INT = "int"
    UINT256 = "uint256"
    UINT128 = "uint128"
    UINT64 = "uint64"
    UINT32 = "uint32"
    UINT16 = "uint16"
    UINT8 = "uint8"
    INT256 = "int256"
    INT128 = "int128"
    BOOL = "bool"
    ADDRESS = "address"
    STRING = "string"
    BYTES = "bytes"
    BYTES32 = "bytes32"
    ARRAY = "array"
    MAPPING = "mapping"
    STRUCT = "struct"

@dataclass
class DafnyType:
    base: Type
    bounds: Optional[tuple] = None
    element_type: Optional['DafnyType'] = None
    key_type: Optional['DafnyType'] = None
    value_type: Optional['DafnyType'] = None
    struct_name: Optional[str] = None

@dataclass
class Variable:
    name: str
    type: DafnyType
    visibility: str = "internal"  # public, private, internal
    is_public: bool = False
    visibility: str = "internal"  # public, private, internal
    is_public: bool = False

@dataclass
class Expression:
    pass

@dataclass
class Literal(Expression):
    value: Union[int, bool, str]
    type: DafnyType

@dataclass
class VarRef(Expression):
    name: str

@dataclass
class BinaryOp(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class IfExpression(Expression):
    """If expression: if condition then thenExpr else elseExpr"""
    condition: Expression
    then_expr: Expression
    else_expr: Expression

@dataclass
class FunctionCall(Expression):
    name: str
    args: List[Expression]

@dataclass
class ArrayAccess(Expression):
    array: Union[str, 'ArrayAccess']  # Can be nested: arr[i][j]
    index: Expression

@dataclass
class MappingAccess(Expression):
    mapping: str
    key: Expression

@dataclass
class StructAccess(Expression):
    struct: str
    field: str

@dataclass
class ArrayLength(Expression):
    array: str

@dataclass
class ContractCall(Expression):
    address: Expression
    method: str  # call, delegatecall, staticcall
    data: Optional[Expression] = None
    value: Optional[Expression] = None

@dataclass
class GlobalVar(Expression):
    name: str  # msg.sender, msg.value, block.timestamp, etc.

@dataclass
class Statement:
    pass

@dataclass
class VarDecl(Statement):
    var: Variable
    init: Optional[Expression] = None

@dataclass
class Assignment(Statement):
    target: str
    value: Expression
    index: Optional[Expression] = None
    indices: Optional[List[Expression]] = None  # For nested mappings: arr[i][j][k]
    is_map_update: bool = False  # True if value is a functional map update

@dataclass
class MapUpdate(Expression):
    """Represents functional map update: map[key := value]"""
    base: Union[str, 'MapUpdate']  # Can be nested
    key: Expression
    value: Expression

@dataclass
class Return(Statement):
    value: Optional[Union[Expression, List[Expression]]] = None

@dataclass
class Assert(Statement):
    condition: Expression

@dataclass
class Require(Statement):
    condition: Expression

@dataclass
class EmitEvent(Statement):
    name: str
    args: List[Expression]

@dataclass
class Revert(Statement):
    message: Optional[str] = None
    error_name: Optional[str] = None
    error_args: List[Expression] = None

@dataclass
class Selfdestruct(Statement):
    recipient: Expression

@dataclass
class ArrayPush(Statement):
    array: str
    value: Expression

@dataclass
class ArrayPop(Statement):
    array: str

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class ForLoop(Statement):
    init: Optional[Statement]
    condition: Expression
    update: Optional[Statement]
    body: List[Statement]

@dataclass
class Event:
    name: str
    params: List[Variable]
    indexed: List[bool] = None  # Which params are indexed
    anonymous: bool = False
    
    def __post_init__(self):
        if self.indexed is None:
            self.indexed = [False] * len(self.params)

@dataclass
class CustomError:
    name: str
    params: List[Variable]

@dataclass
class Library:
    name: str
    path: str

@dataclass
class Struct:
    name: str
    fields: List[Variable]

@dataclass
class Modifier:
    name: str
    params: List[Variable]
    body: List[Statement]

@dataclass
class Method:
    name: str
    params: List[Variable]
    returns: Optional[Union[DafnyType, List[Variable]]]
    preconditions: List[Expression]
    postconditions: List[Expression]
    body: List[Statement]
    is_public: bool = False
    is_payable: bool = False
    visibility: str = "public"  # public, private, internal, external
    state_mutability: Optional[str] = None  # view, pure, payable
    modifiers: List[str] = field(default_factory=list)

@dataclass
class Contract:
    name: str
    fields: List[Variable]
    methods: List[Method]
    invariants: List[Expression]
    imports: List[str] = field(default_factory=list)
    constructor: Optional[Method] = None
    events: List[Event] = field(default_factory=list)
    libraries: List[Library] = field(default_factory=list)
    structs: List[Struct] = field(default_factory=list)
    base_class: Optional[str] = None
    modifiers: List[Modifier] = field(default_factory=list)
    errors: List[CustomError] = field(default_factory=list)
    receive_method: Optional[Method] = None
    fallback_method: Optional[Method] = None
    constants: Dict[str, Any] = field(default_factory=dict)  # Ghost constants
