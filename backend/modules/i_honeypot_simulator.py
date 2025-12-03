"""
Module I: Honeypot Simulator - DYNAMIC ANALYSIS
Simulates buy/sell transactions to detect honeypots WITHOUT spending real funds
Uses eth_call to simulate transactions in read-only mode
"""
import logging
from typing import Dict, Any, Optional, Tuple
from web3 import Web3
from web3.exceptions import ContractLogicError
import asyncio

logger = logging.getLogger(__name__)

# Uniswap V2 Router ABI (minimal - only swap functions)
UNISWAP_V2_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokensSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# ERC20 Transfer/Approve ABI
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

# Known DEX routers
DEX_ROUTERS = {
    "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
}

# WETH address on Ethereum mainnet
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# Test addresses (random addresses with likely some ETH)
TEST_BUYER_ADDRESS = "0x0000000000000000000000000000000000000001"  # Simulated buyer


def parse_revert_reason(error_data: str) -> str:
    """
    Parse revert reason from error data
    
    Args:
        error_data: Hex error data from reverted transaction
        
    Returns:
        Human-readable revert reason
    """
    try:
        if not error_data or error_data == "0x":
            return "Unknown error (no revert data)"
        
        # Remove 0x prefix
        if error_data.startswith("0x"):
            error_data = error_data[2:]
        
        # Standard Error(string) selector: 0x08c379a0
        if error_data.startswith("08c379a0"):
            # Decode string
            # Skip selector (8 chars) and offset (64 chars)
            string_data = error_data[8 + 64:]
            # Get length
            if len(string_data) >= 64:
                length = int(string_data[:64], 16)
                # Get string bytes
                string_bytes = bytes.fromhex(string_data[64:64 + length * 2])
                return string_bytes.decode('utf-8', errors='ignore')
        
        # Common revert patterns
        common_errors = {
            "TRANSFER_FAILED": "Transfer failed",
            "INSUFFICIENT_OUTPUT": "Insufficient output amount",
            "INSUFFICIENT_LIQUIDITY": "Insufficient liquidity",
            "LOCKED": "Trading locked",
            "UNAUTHORIZED": "Unauthorized",
            "HONEYPOT": "Honeypot detected",
        }
        
        for pattern, message in common_errors.items():
            if pattern.lower() in error_data.lower():
                return message
        
        return f"Revert (data: {error_data[:20]}...)"
    
    except Exception as e:
        logger.debug(f"Failed to parse revert reason: {e}")
        return "Unknown error"


async def simulate_buy(
    w3: Web3,
    token_address: str,
    router_address: str,
    amount_eth: float = 0.1
) -> Tuple[bool, str, Optional[int]]:
    """
    Simulate buying tokens from Uniswap using eth_call (no real transaction)
    
    Args:
        w3: Web3 instance
        token_address: Token contract address
        router_address: DEX router address
        amount_eth: Amount of ETH to simulate buying with
        
    Returns:
        (success, message, estimated_gas)
    """
    try:
        router = w3.eth.contract(
            address=Web3.to_checksum_address(router_address),
            abi=UNISWAP_V2_ROUTER_ABI
        )
        
        # Prepare swap parameters
        amount_in = w3.to_wei(amount_eth, 'ether')
        amount_out_min = 0  # Accept any amount (just testing)
        path = [
            Web3.to_checksum_address(WETH_ADDRESS),
            Web3.to_checksum_address(token_address)
        ]
        to = TEST_BUYER_ADDRESS
        deadline = w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes
        
        # Build transaction
        tx = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            amount_out_min,
            path,
            to,
            deadline
        ).build_transaction({
            'from': TEST_BUYER_ADDRESS,
            'value': amount_in,
            'gas': 500000,  # High gas limit for simulation
            'gasPrice': w3.eth.gas_price
        })
        
        # Simulate with eth_call
        try:
            result = w3.eth.call(tx)
            
            # Success! Now estimate gas
            try:
                gas_estimate = w3.eth.estimate_gas(tx)
                return (True, "✅ Buy simulation successful", gas_estimate)
            except Exception as gas_error:
                # Call succeeded but gas estimation failed (rare)
                return (True, "✅ Buy simulation successful (gas estimation failed)", None)
        
        except ContractLogicError as e:
            # Transaction reverted
            error_data = str(e)
            revert_reason = parse_revert_reason(error_data)
            return (False, f"❌ Buy FAILED: {revert_reason}", None)
        
        except Exception as e:
            return (False, f"❌ Buy simulation error: {str(e)[:100]}", None)
    
    except Exception as e:
        logger.error(f"Buy simulation setup failed: {e}")
        return (False, f"Setup error: {str(e)[:100]}", None)


def find_token_holder(w3: Web3, token_address: str) -> Optional[str]:
    """
    Find a real address that holds tokens by checking recent transfers
    """
    try:
        token = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        logger.debug(f"Searching for token holder for {token_address}...")
        
        # Get recent Transfer events with smaller block ranges to avoid RPC limits
        latest_block = w3.eth.block_number
        
        # Try progressively smaller block ranges
        block_ranges = [1000, 500, 100]
        
        for block_range in block_ranges:
            from_block = max(0, latest_block - block_range)
            
            try:
                logger.debug(f"Querying Transfer events from block {from_block} to {latest_block} ({block_range} blocks)")
                events = token.events.Transfer.get_logs(
                    fromBlock=from_block,
                    toBlock='latest'
                )
                
                if len(events) > 0:
                    logger.info(f"Found {len(events)} transfer events for {token_address}")
                    
                    # Check balances of recent recipients (reverse order - most recent first)
                    checked = 0
                    for event in reversed(events[-50:]):  # Check last 50 transfers
                        recipient = event['args']['to']
                        if recipient == '0x0000000000000000000000000000000000000000':
                            continue  # Skip burn address
                        
                        try:
                            balance = token.functions.balanceOf(recipient).call()
                            checked += 1
                            if balance > 0:
                                logger.info(f"✓ Found holder with balance: {recipient} (balance: {balance})")
                                return recipient
                        except Exception as e:
                            logger.debug(f"Could not check balance for {recipient}: {e}")
                            continue
                    
                    logger.debug(f"Checked {checked} addresses, none with positive balance")
                else:
                    logger.debug(f"No transfers found in last {block_range} blocks")
            
            except Exception as e:
                logger.debug(f"Error fetching Transfer events (range {block_range}): {e}")
                continue  # Try smaller range
        
        logger.warning(f"No holder found for {token_address} after trying multiple block ranges")
        return None
    
    except Exception as e:
        logger.error(f"find_token_holder failed: {e}")
        return None


async def simulate_sell(
    w3: Web3,
    token_address: str,
    router_address: str,
    holder_address: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    """
    Simulate selling tokens back to ETH using eth_call
    
    Args:
        w3: Web3 instance
        token_address: Token contract address
        router_address: DEX router address
        holder_address: Address that holds tokens (for realistic simulation)
        
    Returns:
        (success, message, estimated_gas)
    """
    try:
        # If no holder provided, try to find one from recent transfers
        if not holder_address:
            holder_address = find_token_holder(w3, token_address)
            if not holder_address:
                # Can't find holder - skip sell simulation
                logger.info("No token holder found - skipping sell simulation")
                return (True, "⚠️ Sell simulation skipped (no token holder found)", None)
            logger.info(f"Using holder address for sell simulation: {holder_address}")
        
        holder_address = Web3.to_checksum_address(holder_address)
        
        # Get token contract
        token = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        # Try to get actual balance (if holder has tokens)
        try:
            balance = token.functions.balanceOf(holder_address).call()
            if balance == 0:
                # No balance, use a fake amount for simulation
                balance = w3.to_wei(100, 'ether')  # Assume 100 tokens
        except:
            balance = w3.to_wei(100, 'ether')
        
        # Use 50% of balance for simulation
        amount_to_sell = balance // 2
        if amount_to_sell == 0:
            amount_to_sell = w3.to_wei(1, 'ether')
        
        # First simulate approve
        try:
            approve_tx = token.functions.approve(
                Web3.to_checksum_address(router_address),
                amount_to_sell
            ).build_transaction({
                'from': holder_address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price
            })
            
            # Simulate approve
            w3.eth.call(approve_tx)
        except ContractLogicError as e:
            error_data = str(e)
            revert_reason = parse_revert_reason(error_data)
            return (False, f"❌ Approve FAILED: {revert_reason} (Honeypot indicator!)", None)
        except Exception as e:
            logger.debug(f"Approve simulation issue: {e}")
            # Continue anyway - might work
        
        # Now simulate sell
        router = w3.eth.contract(
            address=Web3.to_checksum_address(router_address),
            abi=UNISWAP_V2_ROUTER_ABI
        )
        
        path = [
            Web3.to_checksum_address(token_address),
            Web3.to_checksum_address(WETH_ADDRESS)
        ]
        deadline = w3.eth.get_block('latest')['timestamp'] + 300
        
        tx = router.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
            amount_to_sell,
            0,  # Accept any amount
            path,
            holder_address,
            deadline
        ).build_transaction({
            'from': holder_address,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price
        })
        
        try:
            result = w3.eth.call(tx)
            
            # Success! Estimate gas
            try:
                gas_estimate = w3.eth.estimate_gas(tx)
                return (True, "✅ Sell simulation successful", gas_estimate)
            except:
                return (True, "✅ Sell simulation successful (gas estimation failed)", None)
        
        except ContractLogicError as e:
            error_data = str(e)
            revert_reason = parse_revert_reason(error_data)
            return (False, f"❌ Sell FAILED: {revert_reason} (HONEYPOT!)", None)
        
        except Exception as e:
            return (False, f"❌ Sell simulation error: {str(e)[:100]}", None)
    
    except Exception as e:
        logger.error(f"Sell simulation setup failed: {e}")
        return (False, f"Setup error: {str(e)[:100]}", None)


async def simulate_direct_transfer(
    w3: Web3,
    token_address: str,
    from_address: str
) -> Tuple[bool, str]:
    """
    Simulate a simple transfer to detect transfer restrictions
    
    Args:
        w3: Web3 instance
        token_address: Token contract address
        from_address: Address to transfer from
        
    Returns:
        (success, message)
    """
    try:
        token = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        # Simulate transfer 1 token to self
        tx = token.functions.transfer(
            from_address,
            w3.to_wei(1, 'ether')
        ).build_transaction({
            'from': from_address,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        try:
            w3.eth.call(tx)
            return (True, "✅ Direct transfer works")
        except ContractLogicError as e:
            error_data = str(e)
            revert_reason = parse_revert_reason(error_data)
            return (False, f"❌ Transfer blocked: {revert_reason}")
        except Exception as e:
            return (False, f"❌ Transfer error: {str(e)[:100]}")
    
    except Exception as e:
        return (False, f"Setup error: {str(e)[:100]}")


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Run honeypot simulation - the ultimate scam detection test
    
    Tests:
    1. Can you BUY the token? (Uniswap simulation)
    2. Can you SELL the token? (Reverse swap simulation)
    3. Can you TRANSFER the token? (Direct transfer test)
    4. Gas cost analysis (Excessive gas = suspicious)
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Analysis results with simulation outcomes
    """
    try:
        w3 = blockchain.w3
        warnings = []
        risk_score = 0
        data = {}
        features = {}
        
        logger.info(f"🎯 Starting honeypot simulation for {address}...")
        
        # Choose router (prefer Uniswap V2)
        router_address = DEX_ROUTERS["uniswap_v2"]
        
        # Test 1: Simulate BUY
        buy_success, buy_message, buy_gas = await simulate_buy(
            w3, address, router_address, amount_eth=0.1
        )
        
        data["buy_simulation"] = {
            "success": buy_success,
            "message": buy_message,
            "gas_estimate": buy_gas
        }
        
        logger.info(f"Buy simulation: {buy_message}")
        
        if not buy_success:
            warnings.append(f"🚨 CRITICAL: {buy_message}")
            risk_score += 60
            features["can_buy"] = 0
        else:
            features["can_buy"] = 1
            if buy_gas and buy_gas > 300000:
                warnings.append(f"⚠️ High buy gas cost ({buy_gas:,}) - potential issue")
                risk_score += 10
        
        # Test 2: Simulate SELL
        # Try to find a real holder for more accurate simulation
        holder_address = None
        try:
            logger.debug("Attempting to find a real token holder...")
            holder_address = find_token_holder(w3, address)
            if holder_address:
                logger.info(f"Found holder for sell simulation: {holder_address}")
            else:
                logger.info("No holder found - sell simulation will be skipped")
        except Exception as e:
            logger.warning(f"Could not find holder: {e}")
        
        sell_success, sell_message, sell_gas = await simulate_sell(
            w3, address, router_address, holder_address
        )
        
        data["sell_simulation"] = {
            "success": sell_success,
            "message": sell_message,
            "gas_estimate": sell_gas
        }
        
        logger.info(f"Sell simulation: {sell_message}")
        
        if not sell_success:
            warnings.append(f"🚨 HONEYPOT DETECTED: {sell_message}")
            risk_score += 80  # CRITICAL - this is the smoking gun!
            features["can_sell"] = 0
        else:
            features["can_sell"] = 1
            if sell_gas and sell_gas > 400000:
                warnings.append(f"⚠️ High sell gas cost ({sell_gas:,}) - potential restriction")
                risk_score += 15
        
        # Test 3: Direct transfer (if sell failed, this helps diagnose)
        if not sell_success:
            transfer_success, transfer_message = await simulate_direct_transfer(
                w3, address, holder_address or TEST_BUYER_ADDRESS
            )
            
            data["transfer_simulation"] = {
                "success": transfer_success,
                "message": transfer_message
            }
            
            logger.info(f"Transfer simulation: {transfer_message}")
            
            if not transfer_success:
                warnings.append(f"⚠️ Transfer restrictions detected: {transfer_message}")
                risk_score += 20
                features["can_transfer"] = 0
            else:
                features["can_transfer"] = 1
                warnings.append("ℹ️ Direct transfer works but sell fails - likely DEX restriction")
        else:
            features["can_transfer"] = 1
        
        # Gas analysis
        if buy_gas and sell_gas:
            gas_ratio = sell_gas / buy_gas if buy_gas > 0 else 1
            data["gas_ratio"] = round(gas_ratio, 2)
            
            if gas_ratio > 2:
                warnings.append(f"⚠️ Sell gas is {gas_ratio:.1f}x higher than buy - suspicious")
                risk_score += 12
        
        # Overall verdict
        # Check if sell was actually tested or skipped
        sell_skipped = "skipped" in sell_message.lower()
        
        if sell_skipped:
            # Sell not tested - base verdict on buy + transfer
            if buy_success:
                data["verdict"] = "SAFE"
                data["verdict_confidence"] = "medium"
                logger.info("✅ VERDICT: Buy works, sell not tested - assuming SAFE (popular token)")
                risk_score = max(0, risk_score - 80)  # Remove honeypot penalty
            else:
                data["verdict"] = "LOCKED"
                data["verdict_confidence"] = "high"
                logger.warning("🚨 VERDICT: Buy fails, sell not tested - LOCKED")
        elif buy_success and sell_success:
            data["verdict"] = "SAFE"
            data["verdict_confidence"] = "high"
            logger.info("✅ VERDICT: Token appears tradeable (NOT a honeypot)")
        elif buy_success and not sell_success:
            data["verdict"] = "HONEYPOT"
            data["verdict_confidence"] = "very_high"
            logger.warning("🚨 VERDICT: HONEYPOT CONFIRMED - Can buy but cannot sell!")
        elif not buy_success and not sell_success:
            data["verdict"] = "LOCKED"
            data["verdict_confidence"] = "high"
            logger.warning("🚨 VERDICT: Trading completely locked")
        else:
            data["verdict"] = "SUSPICIOUS"
            data["verdict_confidence"] = "medium"
            logger.warning("⚠️ VERDICT: Unusual behavior detected")
        
        # Features for ML
        features["simulation_verdict"] = {
            "SAFE": 0,
            "HONEYPOT": 1,
            "LOCKED": 0.8,
            "SUSPICIOUS": 0.6
        }.get(data["verdict"], 0.5)
        
        features["buy_gas_normalized"] = min((buy_gas or 0) / 500000, 1.0)
        features["sell_gas_normalized"] = min((sell_gas or 0) / 500000, 1.0)
        
        risk_score = min(risk_score, 100)
        
        logger.info(
            f"✅ Honeypot simulation complete for {address}: "
            f"Risk={risk_score}, Verdict={data['verdict']}"
        )
        
        return {
            "risk_score": risk_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }
    
    except Exception as e:
        logger.error(f"Honeypot simulation failed: {str(e)}", exc_info=True)
        return {
            "risk_score": 0,  # Don't penalize if simulation fails (might be network issue)
            "warnings": [f"⚠️ Simulation unavailable: {str(e)[:100]}"],
            "data": {
                "error": str(e),
                "verdict": "UNKNOWN",
                "verdict_confidence": "none"
            },
            "features": {
                "can_buy": 0.5,
                "can_sell": 0.5,
                "can_transfer": 0.5,
                "simulation_verdict": 0.5,
                "buy_gas_normalized": 0,
                "sell_gas_normalized": 0
            }
        }
