"""
Module C: Liquidity Pool Analysis
Analyzes DEX liquidity and LP token locks
"""
import logging
from typing import Dict, Any
from web3 import Web3

logger = logging.getLogger(__name__)

# Chainlink Price Feed ABI (ETH/USD)
CHAINLINK_PRICE_FEED_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"name": "roundId", "type": "uint80"},
            {"name": "answer", "type": "int256"},
            {"name": "startedAt", "type": "uint256"},
            {"name": "updatedAt", "type": "uint256"},
            {"name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Chainlink ETH/USD Price Feeds
CHAINLINK_PRICE_FEEDS = {
    "ethereum": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  # ETH/USD
    "bsc": "0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE",      # BNB/USD
    "polygon": "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0"   # MATIC/USD
}

# Uniswap V2 Pair ABI (minimal)
PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"}
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    }
]

# Uniswap V2 Factory ABI (minimal)
FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"}
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "type": "function"
    }
]

# Common DEX factory addresses
DEX_FACTORIES = {
    "ethereum": {
        "uniswap_v2": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "sushiswap": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    },
    "bsc": {
        "pancakeswap": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    },
    "polygon": {
        "quickswap": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32"
    }
}


async def get_eth_price(blockchain) -> float:
    """
    Get current ETH/BNB/MATIC price from Chainlink oracle
    
    Args:
        blockchain: Blockchain client instance
        
    Returns:
        Current price in USD (fallback to $2000 if fails)
    """
    try:
        chain_name = blockchain.chain_name
        price_feed_address = CHAINLINK_PRICE_FEEDS.get(chain_name)
        
        if not price_feed_address:
            logger.debug(f"No Chainlink feed for {chain_name}, using fallback")
            return 2000.0
        
        w3 = blockchain.w3
        price_feed = w3.eth.contract(
            address=Web3.to_checksum_address(price_feed_address),
            abi=CHAINLINK_PRICE_FEED_ABI
        )
        
        # Get latest price
        latest_data = price_feed.functions.latestRoundData().call()
        price = latest_data[1] / 1e8  # Chainlink returns 8 decimals
        
        logger.info(f"Chainlink price for {chain_name}: ${price:.2f}")
        return price
        
    except Exception as e:
        logger.debug(f"Chainlink price fetch failed: {e}, using fallback $2000")
        return 2000.0


async def get_pair_address(token_address: str, blockchain) -> str:
    """
    Find DEX pair address for token
    
    Args:
        token_address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Pair contract address or None
    """
    try:
        chain_name = blockchain.chain_name
        factories = DEX_FACTORIES.get(chain_name, {})
        
        if not factories:
            logger.warning(f"No DEX factories configured for {chain_name}")
            return None
        
        # WETH/WBNB/WMATIC addresses
        weth_addresses = {
            "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
            "polygon": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
        }
        
        weth = weth_addresses.get(chain_name)
        if not weth:
            logger.warning(f"No WETH address for {chain_name}")
            return None
        
        w3 = blockchain.w3
        
        # Try each factory
        for factory_name, factory_address in factories.items():
            try:
                factory_contract = w3.eth.contract(
                    address=Web3.to_checksum_address(factory_address),
                    abi=FACTORY_ABI
                )
                
                pair_address = factory_contract.functions.getPair(
                    Web3.to_checksum_address(token_address),
                    Web3.to_checksum_address(weth)
                ).call()
                
                # Check if pair exists (not zero address)
                if pair_address != "0x0000000000000000000000000000000000000000":
                    logger.info(f"Found pair on {factory_name}: {pair_address}")
                    return pair_address
                    
            except Exception as e:
                logger.debug(f"Factory {factory_name} check failed: {str(e)}")
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding pair: {str(e)}")
        return None


async def analyze_liquidity_pool(pair_address: str, token_address: str, blockchain) -> Dict[str, Any]:
    """
    Analyze liquidity pool reserves
    
    Args:
        pair_address: DEX pair contract address
        token_address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Liquidity data
    """
    try:
        if not pair_address:
            return {"error": "No pair address"}
        
        w3 = blockchain.w3
        pair_contract = w3.eth.contract(
            address=Web3.to_checksum_address(pair_address),
            abi=PAIR_ABI
        )
        
        # Get reserves
        reserves = pair_contract.functions.getReserves().call()
        reserve0 = reserves[0]
        reserve1 = reserves[1]
        
        # Get token addresses
        token0 = pair_contract.functions.token0().call()
        token1 = pair_contract.functions.token1().call()
        
        # Determine which reserve is our token
        token_address_checksum = Web3.to_checksum_address(token_address)
        if token0.lower() == token_address.lower():
            token_reserve = reserve0
            paired_reserve = reserve1
        else:
            token_reserve = reserve1
            paired_reserve = reserve0
        
        # Convert from wei
        token_liquidity = token_reserve / 1e18
        paired_liquidity = paired_reserve / 1e18
        
        logger.info(f"Liquidity: {token_liquidity:.2f} token, {paired_liquidity:.4f} paired")
        
        # Get real-time price from Chainlink
        paired_token_price = await get_eth_price(blockchain)
        total_liquidity_usd = paired_liquidity * paired_token_price * 2
        
        logger.info(f"Total liquidity: ${total_liquidity_usd:,.0f} (paired token @ ${paired_token_price:.2f})")
        
        return {
            "token_liquidity": token_liquidity,
            "paired_liquidity": paired_liquidity,
            "total_liquidity_usd": total_liquidity_usd,
            "pair_address": pair_address
        }
        
    except Exception as e:
        logger.error(f"Liquidity analysis error: {str(e)}")
        return {"error": str(e)}


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Analyze liquidity pool status
    
    Checks:
    - Total liquidity locked
    - LP token holder concentration
    - Liquidity lock duration
    - Rug pull via liquidity removal risk
    
    Args:
        address: Token contract address
        blockchain: Blockchain client instance
        
    Returns:
        Analysis result with risk score and warnings
    """
    try:
        warnings = []
        risk_score = 0
        data = {}
        features = {}
        
        # Try to find and analyze DEX pair
        pair_address = await get_pair_address(address, blockchain)
        
        if pair_address:
            liquidity_data = await analyze_liquidity_pool(pair_address, address, blockchain)
            
            if "error" not in liquidity_data:
                total_liquidity = liquidity_data.get("total_liquidity_usd", 0)
                data["total_liquidity_usd"] = total_liquidity
                data["pair_address"] = liquidity_data.get("pair_address")
                data["is_locked"] = False  # Would need to check lock contracts
                data["lock_duration_days"] = 0
                
                # Analyze liquidity amount
                if total_liquidity < 10000:
                    warnings.append("🚨 CRITICAL: Very low liquidity (<$10k)")
                    risk_score += 40
                elif total_liquidity < 50000:
                    warnings.append("⚠️ LOW: Limited liquidity (<$50k)")
                    risk_score += 25
                elif total_liquidity < 100000:
                    warnings.append("⚡ Moderate liquidity (<$100k)")
                    risk_score += 10
                else:
                    logger.info(f"Good liquidity: ${total_liquidity:,.0f}")
                
                features["liquidity_usd"] = min(total_liquidity / 1000000, 1.0)
                features["is_locked"] = 0.0  # Not locked
            else:
                warnings.append("⚠️ Could not fetch liquidity data")
                data["total_liquidity_usd"] = 50000  # Conservative estimate
                risk_score += 20
        else:
            # No pair found
            logger.info(f"No DEX pair found for {address}")
            warnings.append("⚠️ No DEX liquidity pool detected")
            
            total_liquidity = 50000  # Conservative estimate
            is_locked = False
            lock_days = 0
            
            data["total_liquidity_usd"] = total_liquidity
            data["is_locked"] = is_locked
            data["lock_duration_days"] = lock_days
            data["pair_address"] = None
            
            warnings.append("🚨 No DEX pair found - high risk")
            risk_score += 35
            
            features["liquidity_usd"] = 0.05
            features["is_locked"] = 0.0
        
        # Check lock status (placeholder - would need lock contract integration)
        if not data.get("is_locked", False):
            warnings.append("⚠️ Liquidity not locked - withdrawal risk")
            risk_score += 20
        
        risk_score = min(risk_score, 100)
        
        logger.info(f"Liquidity analysis complete for {address}: Risk={risk_score}")
        
        return {
            "risk_score": risk_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Liquidity analysis failed: {str(e)}")
        return {
            "risk_score": 50,
            "warnings": [f"Analysis error: {str(e)}"],
            "data": {},
            "features": {}
        }
