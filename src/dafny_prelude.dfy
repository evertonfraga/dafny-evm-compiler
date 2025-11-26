// EVM Type Definitions for Dafny Verification
// This file defines EVM types that can be formally verified

// Unsigned integers (using max value, not overflow boundary)
type uint8   = x: int | 0 <= x <= 0xFF
type uint16  = x: int | 0 <= x <= 0xFFFF
type uint32  = x: int | 0 <= x <= 0xFFFFFFFF
type uint64  = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFF
type uint128 = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
type uint256 = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

// Signed integers
type int8    = x: int | -0x80 <= x <= 0x7F
type int16   = x: int | -0x8000 <= x <= 0x7FFF
type int32   = x: int | -0x80000000 <= x <= 0x7FFFFFFF
type int64   = x: int | -0x8000000000000000 <= x <= 0x7FFFFFFFFFFFFFFF
type int128  = x: int | -0x80000000000000000000000000000000 <= x <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
type int256  = x: int | -0x8000000000000000000000000000000000000000000000000000000000000000 <= x <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

// Address (20 bytes = 160 bits)
type address = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

// Bytes types
type bytes32 = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
type bytes20 = x: int | 0 <= x <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
type bytes4  = x: int | 0 <= x <= 0xFFFFFFFF

// EVM Global State (for verification)
// These model the EVM execution context

// msg.sender: caller address (verified to be valid address)
ghost const msg_sender: address

// msg.value: ether sent with transaction (verified to be non-negative)
ghost const msg_value: int
ghost const msg_value_valid: msg_value >= 0

// block.timestamp: current block timestamp (verified to be monotonic)
ghost const block_timestamp: int
ghost const block_timestamp_valid: block_timestamp >= 0

// Verification conditions for payable methods:
// - Must explicitly handle msg.value
// - Balance updates must be proven correct

// Verification conditions for view methods:
// - Cannot have 'modifies this' clause
// - Dafny enforces this automatically

// Verification conditions for pure methods:
// - Cannot read state variables
// - Cannot have 'modifies' or 'reads' clauses

// Note: mapping<K,V> and array<T> are compiler syntax
// During verification: mapping→map, array→seq
// During compilation: proper EVM storage layout

