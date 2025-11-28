"""
Module C: Liquidity Pool Analysis
Analyzes DEX liquidity and LP token locks
"""
import logging
from typing import Dict, Any
from web3 import Web3

logger = logging.getLogger(__name__)

# Whitelisted tokens (major stablecoins and wrapped tokens - don't need lock warnings)
WHITELISTED_TOKENS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
    "0x4fabb145d64652a948d72533023f6e7a623c7c53",  # BUSD
    "0x514910771af9ca656af840dff83e8264ecf986ca",  # LINK
    "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",  # MATIC
}

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
        Liquidity data with price, market cap, volume
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
        
        # Get token decimals
        token_contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=[{
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }, {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }]
        )
        
        try:
            token_decimals = token_contract.functions.decimals().call()
        except:
            token_decimals = 18
            
        try:
            total_supply_raw = token_contract.functions.totalSupply().call()
            total_supply = total_supply_raw / (10 ** token_decimals)
        except:
            total_supply = None
        
        # Determine which reserve is our token
        token_address_checksum = Web3.to_checksum_address(token_address)
        if token0.lower() == token_address.lower():
            token_reserve = reserve0 / (10 ** token_decimals)
            paired_reserve = reserve1 / 1e18  # Assuming WETH/WBNB is 18 decimals
        else:
            token_reserve = reserve1 / (10 ** token_decimals)
            paired_reserve = reserve0 / 1e18
        
        logger.info(f"Liquidity: {token_reserve:.2f} token, {paired_reserve:.4f} paired")
        
        # Get real-time price from Chainlink
        paired_token_price = await get_eth_price(blockchain)
        
        # Calculate price and liquidity
        if token_reserve > 0:
            price_in_paired = paired_reserve / token_reserve
            price_usd = price_in_paired * paired_token_price
        else:
            price_in_paired = 0
            price_usd = 0
        
        # Total liquidity (both sides)
        total_liquidity_usd = paired_reserve * paired_token_price * 2
        
        # Market cap calculation
        if total_supply and price_usd:
            market_cap = total_supply * price_usd
        else:
            market_cap = 0
        
        logger.info(f"Total liquidity: ${total_liquidity_usd:,.0f} (paired token @ ${paired_token_price:.2f})")
        logger.info(f"Token price: ${price_usd:.8f}, Market cap: ${market_cap:,.0f}")
        
        return {
            "token_liquidity": float(token_reserve),
            "paired_liquidity": float(paired_reserve),
            "total_liquidity_usd": float(total_liquidity_usd),
            "price_usd": float(price_usd),
            "price_in_paired": float(price_in_paired),
            "market_cap": float(market_cap),
            "total_supply": float(total_supply) if total_supply else None,
            "pair_address": pair_address,
            "paired_token_price": float(paired_token_price)
        }
        
    except Exception as e:
        logger.error(f"Liquidity analysis error: {str(e)}")
        return {"error": str(e)}


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Analyze liquidity pool status
    
    Checks:
    - Total liquidity locked
    - Token price and market cap
    - LP token holder concentration
    - Liquidity lock duration (placeholder)
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
        
        # Check if token is whitelisted (major tokens)
        is_whitelisted = address.lower() in WHITELISTED_TOKENS
        
        # Try to find and analyze DEX pair
        pair_address = await get_pair_address(address, blockchain)
        
        if pair_address:
            liquidity_data = await analyze_liquidity_pool(pair_address, address, blockchain)
            
            if "error" not in liquidity_data:
                total_liquidity = liquidity_data.get("total_liquidity_usd", 0)
                price_usd = liquidity_data.get("price_usd", 0)
                market_cap = liquidity_data.get("market_cap", 0)
                
                # Populate data with actual values
                data["liquidity_usd"] = total_liquidity
                data["price_usd"] = price_usd
                data["market_cap"] = market_cap
                data["pair_address"] = liquidity_data.get("pair_address")
                data["token_reserve"] = liquidity_data.get("token_liquidity", 0)
                data["paired_reserve"] = liquidity_data.get("paired_liquidity", 0)
                data["paired_token_price"] = liquidity_data.get("paired_token_price", 0)
                
                # Lock status (would need lock contract integration)
                # Placeholder: Check common lock contracts like Unicrypt, Team Finance, etc.
                data["is_locked"] = False  # TODO: Implement lock detection
                data["lock_duration_days"] = 0
                data["volume_24h"] = 0  # TODO: Would need to query DEX API or track Transfer events
                
                # Risk assessment based on liquidity
                if total_liquidity < 5000:
                    warnings.append("🚨 CRITICAL: Extremely low liquidity (<$5k) - HIGH RUG RISK")
                    risk_score += 50
                elif total_liquidity < 10000:
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
                
                # Price validation
                if price_usd <= 0:
                    warnings.append("⚠️ Token price could not be determined")
                    risk_score += 15
                elif price_usd < 0.000000001:
                    warnings.append("ℹ️ Extremely low token price (micro-cap)")
                
                # Market cap validation
                if market_cap > 0:
                    if market_cap < 10000:
                        warnings.append("⚠️ Very small market cap (<$10k)")
                        risk_score += 10
                    elif market_cap > 10000000000 and not is_whitelisted:
                        # Only warn for non-whitelisted tokens with >$10B market cap
                        warnings.append("⚠️ Unusually high market cap - verify supply")
                    elif is_whitelisted and market_cap > 1000000000000:
                        # Even whitelisted: sanity check for >$1T
                        warnings.append("ℹ️ Major token with large market cap")
                
                features["liquidity_usd"] = min(total_liquidity / 1000000, 1.0)
                features["price_usd"] = min(price_usd * 1000000, 1.0)  # Normalize
                features["market_cap"] = min(market_cap / 100000000, 1.0)
                features["is_locked"] = 0.0
            else:
                warnings.append("⚠️ Could not fetch liquidity data")
                data["liquidity_usd"] = 0
                data["price_usd"] = 0
                data["market_cap"] = 0
                data["is_locked"] = False
                data["lock_duration_days"] = 0
                data["volume_24h"] = 0
                risk_score += 30
                
                features["liquidity_usd"] = 0
                features["is_locked"] = 0.0
        else:
            # No pair found - very high risk
            logger.info(f"No DEX pair found for {address}")
            warnings.append("🚨 No DEX liquidity pool detected - CRITICAL")
            
            data["liquidity_usd"] = 0
            data["price_usd"] = 0
            data["market_cap"] = 0
            data["is_locked"] = False
            data["lock_duration_days"] = 0
            data["pair_address"] = None
            data["volume_24h"] = 0
            
            risk_score += 55
            
            features["liquidity_usd"] = 0
            features["is_locked"] = 0.0
        
        # Lock status penalty (smart evaluation)
        is_whitelisted = address.lower() in WHITELISTED_TOKENS
        is_locked = data.get("is_locked", False)
        
        if not is_locked:
            if is_whitelisted:
                # Whitelisted tokens don't need lock warnings
                logger.info(f"Whitelisted token - skipping lock requirement")
            elif total_liquidity > 1000000:
                # High liquidity (>$1M) - lock is less critical
                warnings.append("ℹ️ Liquidity not locked (but high liquidity reduces risk)")
                risk_score += 5
            elif total_liquidity > 500000:
                # Medium-high liquidity ($500k-$1M)
                warnings.append("⚡ Liquidity not locked - moderate withdrawal risk")
                risk_score += 10
            else:
                # Low liquidity - lock is critical
                warnings.append("⚠️ Liquidity not locked - HIGH withdrawal risk")
                risk_score += 20
        
        risk_score = min(risk_score, 100)
        
        logger.info(f"Liquidity analysis complete for {address}: Risk={risk_score}")
        
        return {
            "risk_score": risk_score,
            "confidence": 80,  # Add confidence score
            "warnings": warnings,
            "data": data,
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Liquidity analysis failed: {str(e)}")
        return {
            "risk_score": 60,
            "confidence": 0,
            "warnings": [f"⚠️ Analysis error: {str(e)}"],
            "data": {
                "liquidity_usd": 0,
                "price_usd": 0,
                "market_cap": 0,
                "is_locked": False,
                "lock_duration_days": 0,
                "volume_24h": 0
            },
            "features": {
                "liquidity_usd": 0,
                "is_locked": 0.0
            }
        }
