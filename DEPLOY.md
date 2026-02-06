# Deploying to Sepolia Testnet

# Deploying to Sepolia Testnet

## Contract: DafnyToken (DFY)

This contract showcases:
- **Token metadata**: Name "Dafny Token", Symbol "DFY"
- **Formal verification** with Dafny preconditions/postconditions
- **Public variable getters** (name, symbol, totalSupply, balances, allowances)
- **Mint functionality**: Anyone can mint tokens to their own address
- **Burn functionality**: Holders can burn their own tokens
- **Events** (Transfer, Approval, Mint, Burn)
- **Memory safety** with dynamic allocation
- **Calldata bounds checking**

**Constructor parameter:** `initialSupply: uint256` (default: 1,000,000 tokens to deployer)

## Prerequisites

1. Account seed in `.account.txt`
2. Sepolia RPC URL in `.env`:
   ```
   SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
   ```
3. Sepolia ETH for gas

## Deploy

```bash
./deploy-sepolia.sh
```

## Manual Deployment

```bash
# Compile
python3 cli.py examples/DafnyToken.dfy --no-verify -o output/DafnyToken

# Deploy
cd script
forge script DeployDafnyToken.s.sol:DeployDafnyToken \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast \
    --verify \
    -vvv
```

## Interact

```bash
# Get token name
cast call <CONTRACT_ADDRESS> "name()" --rpc-url $SEPOLIA_RPC_URL

# Get token symbol
cast call <CONTRACT_ADDRESS> "symbol()" --rpc-url $SEPOLIA_RPC_URL

# Get total supply
cast call <CONTRACT_ADDRESS> "totalSupply()" --rpc-url $SEPOLIA_RPC_URL

# Get balance
cast call <CONTRACT_ADDRESS> "balances(address)" <ADDRESS> --rpc-url $SEPOLIA_RPC_URL

# Mint tokens (anyone can mint)
cast send <CONTRACT_ADDRESS> "mint(uint256)" <AMOUNT> \
    --private-key <KEY> --rpc-url $SEPOLIA_RPC_URL

# Burn own tokens
cast send <CONTRACT_ADDRESS> "burn(uint256)" <AMOUNT> \
    --private-key <KEY> --rpc-url $SEPOLIA_RPC_URL

# Transfer tokens
cast send <CONTRACT_ADDRESS> "transfer(address,uint256)" <TO> <AMOUNT> \
    --private-key <KEY> --rpc-url $SEPOLIA_RPC_URL
```
