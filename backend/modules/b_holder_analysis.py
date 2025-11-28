"""
Module B: Holder Analysis - IMPROVED VERSION
Analyzes token distribution using multi-page Etherscan API + fallback strategies
"""
import logging
import requests
import asyncio
from typing import Dict, Any, List, Optional
from web3 import Web3
from config.settings import settings

logger = logging.getLogger(__name__)

# Etherscan API Settings
ETHERSCAN_API_KEY = settings.ETHERSCAN_API_KEY
ETHERSCAN_URL = "https://api.etherscan.io/v2/api"  # V2 API (V1 deprecated)

# Known system addresses to filter out
SYSTEM_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",  # Burn address
    "0x000000000000000000000000000000000000dead",  # Dead address
    "0xdead000000000000000042069420694206942069",  # Another burn
}

# Whitelisted tokens - known legitimate tokens with expected distribution
WHITELISTED_TOKENS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "stETH",  # Lido - rebase token
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "WBTC",
    "0x514910771af9ca656af840dff83e8264ecf986ca": "LINK",
    "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0": "MATIC",
}


def calculate_gini(balances: List[float]) -> float:
    """
    Calculate Gini coefficient (0: Equal distribution, 1: Total inequality)
    """
    if not balances or len(balances) < 2:
        return 0.0
    
    sorted_balances = sorted(balances)
    n = len(balances)
    cumulative_sum = sum((i + 1) * bal for i, bal in enumerate(sorted_balances))
    total_sum = sum(sorted_balances)
    
    if total_sum == 0:
        return 0.0
    
    return (2 * cumulative_sum) / (n * total_sum) - (n + 1) / n


async def fetch_transfers_multi_page(
    checksum_address: str,
    w3: Web3,
    max_pages: int = 3,
    offset_per_page: int = 1000
) -> List[Dict]:
    """
    Fetch multiple pages of transfers from Etherscan API with smart timeout handling
    
    Args:
        checksum_address: Token contract address
        w3: Web3 instance
        max_pages: Maximum number of pages to fetch (default 3 for speed)
        offset_per_page: Number of transactions per page
        
    Returns:
        List of transfer transactions
    """
    all_transfers = []
    
    try:
        # Use recent blocks only (last ~1 day ≈ 7000 blocks for faster queries)
        try:
            latest_block = w3.eth.block_number
            start_block = max(0, latest_block - 7000)
            logger.info(f"Querying blocks {start_block} to {latest_block}")
        except Exception as e:
            logger.debug(f"Could not fetch block number: {e}")
            latest_block = None
            start_block = None
        
        for page in range(1, max_pages + 1):
            try:
                params = {
                    "chainid": 1,
                    "module": "account",
                    "action": "tokentx",
                    "contractaddress": checksum_address,
                    "page": page,
                    "offset": offset_per_page,
                    "sort": "desc",
                    "apikey": ETHERSCAN_API_KEY
                }
                
                # Add block range if available
                if start_block is not None:
                    params["startblock"] = start_block
                if latest_block is not None:
                    params["endblock"] = latest_block
                
                # Progressive timeout: first page longer, subsequent shorter
                timeout = 10 if page == 1 else 5
                
                logger.info(f"Fetching page {page} (timeout: {timeout}s)...")
                response = requests.get(ETHERSCAN_URL, params=params, timeout=timeout)
                tx_data = response.json()
                
                if tx_data["status"] == "1" and tx_data["result"]:
                    transfers = tx_data["result"]
                    all_transfers.extend(transfers)
                    logger.info(f"✓ Page {page}: {len(transfers)} transfers (Total: {len(all_transfers)})")
                    
                    # If we got less than offset, we've reached the end
                    if len(transfers) < offset_per_page:
                        logger.info("Reached end of available transfers")
                        break
                    
                    # Tiny delay to respect API rate limits
                    await asyncio.sleep(0.1)
                else:
                    msg = tx_data.get('message', 'Unknown error')
                    logger.warning(f"Page {page} returned no data: {msg}")
                    # Don't break - try next page
                    if page == 1:
                        break  # If first page fails, stop
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Page {page} timeout - continuing with available data")
                # Don't break - we can still use data from previous pages
                break
                    
            except Exception as page_err:
                logger.warning(f"Error on page {page}: {page_err}")
                # Continue if we have data from previous pages
                if len(all_transfers) > 0:
                    logger.info(f"Continuing with {len(all_transfers)} transfers from previous pages")
                    break
                else:
                    break
        
        logger.info(f"✅ Total transfers fetched: {len(all_transfers)}")
        return all_transfers
        
    except Exception as e:
        logger.error(f"Multi-page fetch failed: {e}")
        return all_transfers  # Return whatever we got


async def get_real_balances_sample(
    addresses: List[str],
    contract,
    decimals: int,
    max_calls: int = 50
) -> Dict[str, float]:
    """
    Get real on-chain balances for a sample of addresses via RPC
    
    Args:
        addresses: List of addresses to check
        contract: Web3 contract instance
        decimals: Token decimals
        max_calls: Maximum number of RPC calls to make
        
    Returns:
        Dict of address -> balance
    """
    balances = {}
    
    # Take a sample if too many addresses
    sample_addresses = addresses[:max_calls]
    
    logger.info(f"Fetching real balances for {len(sample_addresses)} addresses...")
    
    for i, addr in enumerate(sample_addresses):
        try:
            # Skip system addresses
            if addr.lower() in [a.lower() for a in SYSTEM_ADDRESSES]:
                continue
            
            balance_raw = contract.functions.balanceOf(addr).call()
            balance = balance_raw / (10 ** decimals)
            
            if balance > 0:
                balances[addr] = balance
            
            # Progress log every 10 addresses
            if (i + 1) % 10 == 0:
                logger.debug(f"Checked {i + 1}/{len(sample_addresses)} addresses")
                
        except Exception as e:
            logger.debug(f"Could not fetch balance for {addr}: {e}")
            continue
    
    logger.info(f"Successfully fetched {len(balances)} non-zero balances")
    return balances


async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    IMPROVED Real-time Holder Analysis
    
    Strategy:
    1. Fetch multiple pages of transfers (up to 5000 txs)
    2. Build holder profile from transfer patterns
    3. Verify top holders with real RPC balance checks
    4. Calculate distribution metrics
    """
    try:
        logger.info(f"Starting IMPROVED Holder Analysis for {address}...")
        
        data = {}
        warnings = []
        risk_score = 0
        confidence_score = 0
        
        w3 = blockchain.w3
        checksum_address = w3.to_checksum_address(address)
        
        # Check if whitelisted (major tokens get special treatment)
        is_whitelisted = address.lower() in WHITELISTED_TOKENS
        token_name = WHITELISTED_TOKENS.get(address.lower(), "Unknown")

        # 1. Get token metadata
        contract = w3.eth.contract(address=checksum_address, abi=[
            {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
        ])

        decimals = 18
        total_supply = None
        
        try:
            decimals = contract.functions.decimals().call()
            total_supply_raw = contract.functions.totalSupply().call()
            total_supply = total_supply_raw / (10 ** decimals)
            data["total_supply"] = total_supply
            logger.info(f"Total supply: {total_supply:,.0f} tokens")
        except Exception as e:
            logger.warning(f"Could not fetch total supply: {e}")

        # 2. Fetch multiple pages of transfers (reduced for speed)
        all_transfers = await fetch_transfers_multi_page(
            checksum_address, 
            w3,
            max_pages=3,  # Reduced from 5 to 3 for speed
            offset_per_page=1000
        )
        
        # Minimum threshold check (with whitelist awareness)
        if len(all_transfers) < 10:
            logger.warning(f"Insufficient transfer data ({len(all_transfers)} transfers)")
            
            # Whitelisted tokens (stETH, USDC, etc) get special treatment
            if is_whitelisted:
                logger.info(f"Whitelisted token ({token_name}) - low activity is acceptable")
                return {
                    "risk_score": 0,  # No risk for known legitimate tokens
                    "confidence": 50,
                    "warnings": [
                        f"ℹ️ {token_name} is a known legitimate token",
                        f"ℹ️ Limited transfer data ({len(all_transfers)} transfers)",
                        "ℹ️ May be primarily CEX-traded or in low volatility period"
                    ],
                    "data": {
                        "token_name": token_name,
                        "analyzed_wallet_count": 0,
                        "total_transfers_analyzed": len(all_transfers),
                        "data_quality": "whitelisted_insufficient",
                        "total_supply": total_supply,
                        "gini_coefficient": None,
                        "top_10_holders_percentage": None,
                        "total_holders": None
                    },
                    "features": {
                        "activity_level": 1.0,  # Assume healthy for whitelisted
                        "top_10_ratio": 0.0,
                        "gini_coefficient": 0.0,
                        "holder_count_proxy": 1.0,
                        "confidence": 0.5
                    }
                }
            
            # NON-WHITELISTED: Much higher risk for dead/abandoned tokens
            if len(all_transfers) == 0:
                activity_risk = 60  # Increased from 20 - DEAD TOKEN
                activity_msg = "🚨 CRITICAL: Zero on-chain activity - likely DEAD or ABANDONED"
                activity_confidence = 5
            elif len(all_transfers) <= 3:
                activity_risk = 40  # Increased from 10 - Very suspicious
                activity_msg = "🚨 Extremely low activity - potential dead project"
                activity_confidence = 10
            else:
                activity_risk = 20  # 4-9 transfers - still concerning
                activity_msg = "⚠️ Very low activity - insufficient for analysis"
                activity_confidence = 15
            
            return {
                "risk_score": activity_risk,
                "confidence": activity_confidence,
                "warnings": [
                    "🚨 Insufficient transfer data for holder analysis",
                    f"⚠️ Only {len(all_transfers)} recent transfers in last ~1 day",
                    activity_msg,
                    "⚠️ Unable to verify holder distribution"
                ],
                "data": {
                    "analyzed_wallet_count": 0,
                    "total_transfers_analyzed": len(all_transfers),
                    "data_quality": "critical_insufficient",
                    "gini_coefficient": None,
                    "top_10_holders_percentage": None,
                    "total_holders": None
                },
                "features": {
                    "activity_level": len(all_transfers) / 100,  # Normalized activity score
                    "top_10_ratio": 0.0,
                    "gini_coefficient": 0.0,
                    "holder_count_proxy": 0.0,  # No data = worst case
                    "confidence": activity_confidence / 100
                }
            }

        # 3. Build holder profile from transfers
        holder_transfers = {}
        unique_addresses = set()
        
        for tx in all_transfers:
            try:
                from_addr = w3.to_checksum_address(tx["from"])
                to_addr = w3.to_checksum_address(tx["to"])
                value = int(tx["value"]) / (10 ** decimals)
                
                # Track all addresses
                unique_addresses.add(from_addr)
                unique_addresses.add(to_addr)
                
                # Initialize holders
                if from_addr not in holder_transfers:
                    holder_transfers[from_addr] = {"incoming": 0, "outgoing": 0}
                if to_addr not in holder_transfers:
                    holder_transfers[to_addr] = {"incoming": 0, "outgoing": 0}
                
                # Aggregate transfers
                holder_transfers[from_addr]["outgoing"] += value
                holder_transfers[to_addr]["incoming"] += value
                
            except Exception as e:
                continue
        
        logger.info(f"Analyzed {len(all_transfers)} transfers, found {len(unique_addresses)} unique addresses")

        # 4. Calculate net balances from transfers
        holder_net_balances = []
        
        for addr, transfers in holder_transfers.items():
            # Skip system addresses
            if addr.lower() in [a.lower() for a in SYSTEM_ADDRESSES]:
                continue
            
            net_balance = transfers["incoming"] - transfers["outgoing"]
            
            if net_balance > 0:
                holder_net_balances.append({
                    "address": addr,
                    "balance": net_balance,
                    "incoming": transfers["incoming"],
                    "outgoing": transfers["outgoing"]
                })
        
        # Sort by balance
        holder_net_balances.sort(key=lambda x: x["balance"], reverse=True)
        
        logger.info(f"Found {len(holder_net_balances)} addresses with positive net balance")

        # 5. VERIFICATION: Get real balances for top 15 holders (reduced from 20)
        top_addresses = [h["address"] for h in holder_net_balances[:15]]
        
        real_balances = await get_real_balances_sample(
            top_addresses,
            contract,
            decimals,
            max_calls=15  # Reduced from 20
        )
        
        # If we got real balances, use them for top holders
        if real_balances:
            verified_holders = [
                {"address": addr, "balance": bal}
                for addr, bal in real_balances.items()
            ]
            verified_holders.sort(key=lambda x: x["balance"], reverse=True)
            
            logger.info(f"Verified {len(verified_holders)} top holder balances via RPC")
            
            # Use verified balances for top 10, estimated for the rest
            top_10_holders = verified_holders[:10]
            confidence_score = 80  # High confidence with real data
        else:
            # Fallback to net balance estimates
            top_10_holders = holder_net_balances[:10]
            confidence_score = 50  # Medium confidence with estimates
            warnings.append("ℹ️ Using transfer-based balance estimates (RPC unavailable)")

        # 6. Calculate metrics
        
        # Use verified real balances if available, otherwise use transfer-based estimates
        holders_for_calculation = verified_holders if real_balances else holder_net_balances
        
        top_10_sum = sum(h["balance"] for h in top_10_holders)
        
        # Top 10 ratio - use REAL holders data
        top_10_ratio = 0
        if total_supply and total_supply > 0:
            top_10_ratio = top_10_sum / total_supply
        else:
            # Relative ratio if no supply - use actual holder balances
            total_sample = sum(h["balance"] for h in holders_for_calculation[:100])  # Top 100 for better estimate
            if total_sample > 0:
                top_10_ratio = top_10_sum / total_sample
                warnings.append("ℹ️ Using sample-based ratio (total supply unavailable)")
                confidence_score -= 10

        # Gini coefficient - FIXED: use real holder balances, not transfer estimates
        # Use only verified balances or top holders for more accurate Gini
        if real_balances and len(verified_holders) >= 5:
            all_balances = [h["balance"] for h in verified_holders]
            confidence_score += 10  # Boost confidence for real data
        else:
            # Use top holders only for better accuracy
            all_balances = [h["balance"] for h in holders_for_calculation[:50]]
        
        gini_coefficient = calculate_gini(all_balances)

        # Sample size for confidence
        sample_size = len(holder_net_balances)
        
        # Adjust confidence based on sample size
        if sample_size < 10:
            confidence_score = max(20, confidence_score - 30)
        elif sample_size < 50:
            confidence_score = max(40, confidence_score - 15)
        elif sample_size >= 100:
            confidence_score = min(100, confidence_score + 10)

        # 7. Risk Scoring
        
        # Centralization risk
        if top_10_ratio > 0.95:
            risk_score += 60
            warnings.append(f"🚨 EXTREME CENTRALIZATION: Top 10 holders own {top_10_ratio*100:.1f}%")
        elif top_10_ratio > 0.85:
            risk_score += 45
            warnings.append(f"🚨 Very High Centralization: Top 10 own {top_10_ratio*100:.1f}%")
        elif top_10_ratio > 0.70:
            risk_score += 30
            warnings.append(f"⚠️ High Centralization: Top 10 own {top_10_ratio*100:.1f}%")
        elif top_10_ratio > 0.50:
            risk_score += 15
            warnings.append(f"⚡ Concentrated supply: Top 10 own {top_10_ratio*100:.1f}%")

        # Gini inequality risk
        if gini_coefficient > 0.95:
            risk_score += 15
            warnings.append(f"⚠️ Extreme inequality (Gini: {gini_coefficient:.3f})")
        elif gini_coefficient > 0.85:
            risk_score += 10
            warnings.append(f"⚡ High inequality between holders (Gini: {gini_coefficient:.3f})")

        # Sample size warnings
        if sample_size < 5:
            warnings.append(f"⚠️ Very limited sample ({sample_size} holders) - LOW CONFIDENCE")
            risk_score += 20
        elif sample_size < 20:
            warnings.append(f"ℹ️ Small sample size ({sample_size} holders) - use as estimate")
            risk_score += 5

        # Data quality
        data["top_10_ratio"] = float(f"{top_10_ratio:.4f}")
        data["top_10_holders_percentage"] = float(top_10_ratio * 100)  # Add percentage for frontend
        data["gini_coefficient"] = float(f"{gini_coefficient:.4f}")
        data["analyzed_wallet_count"] = sample_size
        data["total_holders"] = len(unique_addresses)  # Add total unique addresses
        data["total_transfers_analyzed"] = len(all_transfers)
        data["confidence_score"] = confidence_score
        data["top_holders"] = [
            {
                "address": h["address"],
                "balance": h["balance"],
                "percentage": (h["balance"] / total_supply * 100) if total_supply else 0
            }
            for h in top_10_holders[:10]
        ]
        data["data_quality"] = "high" if confidence_score >= 70 else "medium" if confidence_score >= 40 else "low"

        features = {
            "top_10_ratio": float(top_10_ratio),
            "gini_coefficient": float(gini_coefficient),
            "holder_count_proxy": min(sample_size / 100, 1.0),
            "confidence": float(confidence_score / 100)
        }

        logger.info(f"✅ Holder Analysis Complete: Risk={risk_score}, Confidence={confidence_score}%, Sample={sample_size}")
        
        return {
            "risk_score": min(risk_score, 100),
            "confidence": confidence_score,
            "warnings": warnings,
            "data": data,
            "features": features
        }

    except Exception as e:
        logger.error(f"Holder analysis failed: {str(e)}", exc_info=True)
        return {
            "risk_score": 0,
            "confidence": 0,
            "warnings": [f"⚠️ Analysis failed: {str(e)}"],
            "data": {"analyzed_wallet_count": 0},
            "features": {}
        }