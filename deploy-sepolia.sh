#!/bin/bash
set -e

echo "=== Deploying Dafny-Compiled DafnyToken (DFY) to Sepolia ==="
echo ""

# Check if account file exists
if [ ! -f .account.txt ]; then
    echo "Error: .account.txt not found"
    exit 1
fi

# Check if RPC URL is set
if [ -z "$SEPOLIA_RPC_URL" ]; then
    echo "Error: SEPOLIA_RPC_URL environment variable not set"
    echo "Example: export SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY"
    exit 1
fi

echo "Compiling Dafny contract..."
python3 cli.py examples/DafnyToken.dfy --no-verify -o output/DafnyToken

echo ""
echo "Deploying to Sepolia..."
cd script
forge script DeployDafnyToken.s.sol:DeployDafnyToken \
    --rpc-url $SEPOLIA_RPC_URL \
    --broadcast \
    --verify \
    -vvv

echo ""
echo "Deployment complete!"
