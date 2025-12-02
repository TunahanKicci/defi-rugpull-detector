"""
Module D: Transfer Anomaly Detection v2.0
Uses Etherscan API for comprehensive transfer history analysis.
"""
import logging
from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import IsolationForest
from web3 import Web3
import aiohttp
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Whitelisted tokens
WHITELISTED_TOKENS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",  # stETH
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
    "0x514910771af9ca656af840dff83e8264ecf986ca",  # LINK
    "0xcf0c122c6b73ff809c693db761e7baebe62b6a2e",  # FLOKI
}

REBASE_TOKENS = {
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",  # stETH
    "0x9559aaa82d9649c7a7b220e7c461d2e74c9a3593",  # rETH
}


async def fetch_etherscan_transfers(
    address: str, 
    etherscan_api_key: str,
    blockchain
) -> List[Dict]:
    """
    Fetch transfer events from Etherscan API V2.
    Returns up to 10,000 most recent transfers.
    
    Note: Free tier has rate limits - fallback to RPC if needed.
    """
    # Etherscan V2 API endpoint
    base_url = "https://api.etherscan.io/v2/api"
    
    # Get current block
    try:
        current_block = blockchain.w3.eth.block_number
    except:
        current_block = 23900000  # Fallback estimate
    
    # Conservative range: 7000 blocks (~1 day) to avoid rate limits
    start_block = max(0, current_block - 7000)
    
    params = {
        "chainid": "1",  # Ethereum mainnet
        "module": "logs",
        "action": "getLogs",
        "address": address,
        "topic0": TRANSFER_EVENT_TOPIC,
        "fromBlock": start_block,
        "toBlock": "latest",
        "apikey": etherscan_api_key,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, timeout=15) as response:
                data = await response.json()
                
                status = data.get("status")
                message = data.get("message", "")
                result = data.get("result", [])
                
                # Check for success
                if status == "1" and isinstance(result, list) and len(result) > 0:
                    logger.info(f"✓ Etherscan V2: Fetched {len(result)} transfers from last 7k blocks")
                    return result
                elif status == "0" and "no records found" in message.lower():
                    logger.info("Etherscan: No transfers found (token may be inactive)")
                    return []
                else:
                    # Try even smaller range (2000 blocks)
                    logger.debug(f"Etherscan: {message}, trying minimal range...")
                    params["fromBlock"] = max(0, current_block - 2000)
                    
                    async with session.get(base_url, params=params, timeout=10) as response2:
                        data2 = await response2.json()
                        if data2.get("status") == "1" and isinstance(data2.get("result"), list):
                            result2 = data2["result"]
                            if len(result2) > 0:
                                logger.info(f"✓ Etherscan V2 (minimal): Fetched {len(result2)} transfers")
                                return result2
                            else:
                                logger.info("Etherscan: No transfers in minimal range")
                                return []
                        else:
                            # API unavailable - not critical, RPC fallback will handle it
                            logger.debug(f"Etherscan V2 unavailable: {data2.get('message', 'Unknown error')}")
                            return []
    except Exception as e:
        logger.debug(f"Etherscan V2 error: {e}")
        return []



async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Comprehensive transfer analysis using Etherscan API v2.0
    """
    try:
        logger.info(f"Starting Transfer Anomaly Analysis v2.0 for {address}...")
        
        warnings = []
        risk_score = 0
        w3 = blockchain.w3
        checksum_address = w3.to_checksum_address(address)
        
        is_whitelisted = address.lower() in WHITELISTED_TOKENS
        is_rebase_token = address.lower() in REBASE_TOKENS

        # Get token info
        total_supply = 1_000_000_000
        decimals = 18
        try:
            contract = w3.eth.contract(address=checksum_address, abi=[
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
            ])
            total_supply_raw = contract.functions.totalSupply().call()
            decimals = contract.functions.decimals().call()
            total_supply = total_supply_raw / (10 ** decimals) if decimals > 0 else total_supply_raw
        except Exception as e:
            logger.warning(f"Could not fetch supply/decimals: {e}")

        # STRATEGY 1: Try Etherscan API (best option)
        logs = []
        used_etherscan = False
        etherscan_api_key = settings.ETHERSCAN_API_KEY
        if etherscan_api_key and len(etherscan_api_key) > 5:
            try:
                logs = await fetch_etherscan_transfers(address, etherscan_api_key, blockchain)
                if len(logs) > 0:
                    used_etherscan = True
                    logger.info(f"✓ Using Etherscan data: {len(logs)} transfers")
            except Exception as e:
                logger.warning(f"Etherscan failed: {e}")
        
        # STRATEGY 2: If Etherscan fails, try small RPC sample (last resort)
        if len(logs) == 0:
            logger.warning("Etherscan unavailable, falling back to RPC sample (limited data)")
            try:
                current_block = w3.eth.block_number
                for block_range in [20, 10, 5, 2]:
                    try:
                        logs = w3.eth.get_logs({
                            'fromBlock': current_block - block_range,
                            'toBlock': current_block,
                            'address': checksum_address,
                            'topics': [TRANSFER_EVENT_TOPIC]
                        })
                        if len(logs) >= 0:  # Accept even 0 logs
                            logger.info(f"✓ RPC fallback: {len(logs)} transfers from {block_range} blocks")
                            break
                    except:
                        continue
            except Exception as e:
                logger.error(f"RPC fallback failed: {e}")

        total_transfers = len(logs)
        logger.info(f"Analyzing {total_transfers} transfer events...")

        # Parse transfers
        transfers = []
        mint_count = 0
        burn_count = 0
        large_transfers = 0
        whale_movements = []
        hourly_activity = {}  # Track activity over time

        for log in logs:
            try:
                # Parse addresses from topics
                topics = log.get('topics', [])
                if len(topics) < 3:
                    continue

                from_hex = topics[1] if isinstance(topics[1], str) else topics[1].hex()
                to_hex = topics[2] if isinstance(topics[2], str) else topics[2].hex()
                
                from_addr = w3.to_checksum_address("0x" + from_hex[-40:])
                to_addr = w3.to_checksum_address("0x" + to_hex[-40:])
                
                # Parse value
                data_hex = log.get('data', '0x')
                if isinstance(data_hex, str):
                    data_hex = data_hex.replace('0x', '')
                value = int(data_hex, 16) / (10 ** decimals) if data_hex else 0

                transfers.append(value)

                # Detect mints/burns
                if from_addr == ZERO_ADDRESS:
                    mint_count += 1
                if to_addr == ZERO_ADDRESS:
                    burn_count += 1
                
                # Detect whale transfers (>1% of supply)
                if total_supply > 0 and (value / total_supply) > 0.01:
                    large_transfers += 1
                    if len(whale_movements) < 10:  # Keep top 10
                        whale_movements.append({
                            "from": from_addr,
                            "to": to_addr,
                            "amount": float(f"{value:.4f}"),
                            "percentage": float(f"{(value/total_supply)*100:.2f}"),
                            "timestamp": log.get('timeStamp', 'N/A')
                        })

                # Track hourly activity (for pattern detection)
                timestamp = log.get('timeStamp')
                if timestamp:
                    try:
                        ts_int = int(timestamp, 16) if isinstance(timestamp, str) and timestamp.startswith('0x') else int(timestamp)
                        hour = datetime.fromtimestamp(ts_int).strftime('%Y-%m-%d %H:00')
                        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                    except:
                        pass

            except Exception as parse_err:
                logger.debug(f"Parse error: {parse_err}")
                continue

        # ML Anomaly Detection
        anomaly_score_ml = 0.0
        if len(transfers) > 10:
            try:
                X = np.array(transfers).reshape(-1, 1)
                clf = IsolationForest(random_state=42, contamination=0.1)
                preds = clf.fit_predict(X)
                outliers_count = list(preds).count(-1)
                anomaly_score_ml = min((outliers_count / len(transfers)) * 3, 1.0)
                
                if is_whitelisted and anomaly_score_ml < 0.85:
                    anomaly_score_ml = max(0, anomaly_score_ml - 0.3)
            except Exception as ml_err:
                logger.debug(f"ML error: {ml_err}")

        # ===== RISK SCORING =====
        
        # IMPORTANT: If using RPC fallback (not Etherscan), data is very limited
        # Don't penalize too much - insufficient data ≠ high risk
        data_source = "etherscan" if used_etherscan else "rpc_sample"
        
        # A) Activity Score
        if total_transfers == 0:
            warnings.append("🚨 NO TRANSFER ACTIVITY - Possible dead token")
            risk_score += 60  # Major red flag
        elif total_transfers < 10 and not used_etherscan:
            # RPC fallback with low count - neutral (data too limited)
            warnings.append(f"ℹ️ Limited sample ({total_transfers} transfers) - RPC fallback mode")
            risk_score += 0  # Neutral - can't judge with tiny sample
        elif total_transfers < 10 and used_etherscan:
            # Etherscan shows genuinely low activity
            warnings.append(f"⚠️ Very low activity ({total_transfers} transfers in 50k blocks)")
            risk_score += 40
        elif total_transfers < 50 and not is_whitelisted and used_etherscan:
            warnings.append(f"ℹ️ Low activity ({total_transfers} transfers)")
            risk_score += 15
        else:
            logger.info(f"✓ Healthy activity: {total_transfers} transfers")

        # B) Mint/Burn Analysis
        if mint_count > 0:
            mint_rate = mint_count / max(total_transfers, 1)
            if is_rebase_token:
                if mint_count > 100:
                    warnings.append(f"ℹ️ {mint_count} mints (staking rewards)")
            else:
                if mint_rate > 0.5:
                    warnings.append(f"🚨 Excessive minting: {mint_count} events ({mint_rate*100:.1f}% of transfers)")
                    risk_score += 50
                elif mint_count > 20:
                    warnings.append(f"⚠️ {mint_count} mint events detected")
                    risk_score += 30
                elif mint_count > 5:
                    warnings.append(f"⚡ {mint_count} mint events")
                    risk_score += 15

        if burn_count > 5:
            warnings.append(f"♻️ {burn_count} burn events (deflationary)")
            risk_score -= 5  # Slightly positive

        # C) Whale Activity
        if large_transfers > 0:
            whale_rate = large_transfers / max(total_transfers, 1)
            if is_whitelisted:
                if whale_rate > 0.3:
                    warnings.append(f"ℹ️ {large_transfers} large transfers (institutional)")
                    risk_score += 5
            else:
                if whale_rate > 0.5:
                    warnings.append(f"🚨 WHALE DOMINATED: {large_transfers} large transfers ({whale_rate*100:.1f}%)")
                    risk_score += 40
                elif whale_rate > 0.2:
                    warnings.append(f"⚠️ {large_transfers} whale transfers ({whale_rate*100:.1f}%)")
                    risk_score += 20
                else:
                    warnings.append(f"ℹ️ {large_transfers} large transfers")
                    risk_score += 10

        # D) ML Anomaly
        if anomaly_score_ml > 0.7:
            if is_whitelisted:
                warnings.append(f"ℹ️ Varied transfer patterns (Score: {anomaly_score_ml:.2f})")
                risk_score += 5
            else:
                warnings.append(f"🤖 Unusual transfer patterns (Score: {anomaly_score_ml:.2f})")
                risk_score += 25

        # E) Time-based Pattern Analysis
        if len(hourly_activity) > 0:
            activity_values = list(hourly_activity.values())
            
            # Detect suspicious patterns (e.g., all activity in 1 hour = dump?)
            if len(hourly_activity) == 1 and total_transfers > 20:
                warnings.append("⚠️ All activity concentrated in single time period")
                risk_score += 15

        return {
            "risk_score": min(risk_score, 100),
            "warnings": warnings if warnings else ["✓ No anomalies detected"],
            "data": {
                "total_transfers_analyzed": total_transfers,
                "recent_mints": mint_count,
                "recent_burns": burn_count,
                "large_transfers_count": large_transfers,
                "whale_movements": whale_movements[:5],
                "ml_anomaly_score": float(f"{anomaly_score_ml:.2f}"),
                "unique_time_periods": len(hourly_activity),
                "avg_transfers_per_hour": float(f"{np.mean(list(hourly_activity.values())):.1f}") if hourly_activity else 0,
                "data_source": data_source,
                "limited_sample": not used_etherscan
            },
            "features": {
                "transfer_count_log": float(np.log1p(total_transfers)),
                "anomaly_score": float(anomaly_score_ml),
                "mint_rate": float(mint_count / max(total_transfers, 1)),
                "whale_rate": float(large_transfers / max(total_transfers, 1))
            }
        }

    except Exception as e:
        logger.error(f"D Module Critical Fail: {str(e)}")
        return {
            "risk_score": 0, 
            "warnings": [f"⚠️ Analysis failed: {str(e)}"], 
            "data": {}, 
            "features": {
                "transfer_count_log": 0.0,
                "anomaly_score": 0.0,
                "mint_rate": 0.0,
                "whale_rate": 0.0
            }
        }
    """
    Transfer modellerini analiz eder. 
    GÜNCELLEME: Whitelist ve rebase token desteği eklendi.
    """
    try:
        logger.info(f"Starting Transfer Anomaly Analysis for {address}...")
        
        warnings = []
        risk_score = 0
        data = {}
        features = {}

        w3 = blockchain.w3
        checksum_address = w3.to_checksum_address(address)
        
        # Check if token is whitelisted or rebase token
        is_whitelisted = address.lower() in WHITELISTED_TOKENS
        is_rebase_token = address.lower() in REBASE_TOKENS

        # 2. Toplam Arzı Al
        total_supply = 1_000_000_000
        decimals = 18
        try:
            contract = w3.eth.contract(address=checksum_address, abi=[
                {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
            ])
            total_supply_raw = contract.functions.totalSupply().call()
            decimals = contract.functions.decimals().call()
            if decimals > 0:
                total_supply = total_supply_raw / (10 ** decimals)
            else:
                total_supply = total_supply_raw
        except Exception as e:
            logger.warning(f"Could not fetch supply/decimals: {e}")

        # 3. Transfer Loglarını Çek - Adaptive block range with fallback
        logs = []
        logs_fetch_failed = False
        
        try:
            current_block = w3.eth.block_number
            
            # Extremely conservative ranges for high-volume tokens (Alchemy is very restrictive)
            # For mega-volume tokens, even 5 blocks can be too much
            block_ranges = [20, 10, 5, 2, 1] if not is_whitelisted else [10, 5, 2, 1]
            
            for block_range in block_ranges:
                try:
                    start_block_int = max(0, current_block - block_range)
                    
                    logger.info(f"Fetching logs from last {block_range} blocks: {start_block_int} to {current_block}")

                    logs = w3.eth.get_logs({
                        'fromBlock': start_block_int,
                        'toBlock': current_block,
                        'address': checksum_address,
                        'topics': [TRANSFER_EVENT_TOPIC]
                    })
                    logger.info(f"✓ Successfully fetched {len(logs)} transfer logs from {block_range} blocks")
                    break  # Success - exit loop
                    
                except Exception as log_err:
                    error_msg = str(log_err).lower()
                    is_rate_limit = any(x in error_msg for x in ['query', 'limit', 'exceed', 'too many', 'timeout', 'bad request', '400'])
                    
                    if is_rate_limit and block_range != block_ranges[-1]:
                        logger.debug(f"Range {block_range} exceeded limit, trying {block_ranges[block_ranges.index(block_range)+1]}...")
                        continue  # Try next smaller range
                    elif block_range == block_ranges[-1]:
                        # Even 1 block failed - token has extreme volume
                        logger.info(f"Token has extreme transfer volume - skipping on-chain log analysis")
                        logs_fetch_failed = True
                        break
                    else:
                        logger.error(f"Log fetch error: {log_err}")
                        logs_fetch_failed = True
                        break
        except Exception as outer_err:
            logger.error(f"Critical error fetching logs: {outer_err}")
            logs_fetch_failed = True

        total_transfers = len(logs)
        logger.info(f"Fetched {total_transfers} transfer logs.")

        # 4. Logları İşle
        transfers = []
        mint_count = 0
        large_transfers = 0
        whale_movements = []

        for log in logs:
            try:
                if len(log['topics']) < 3: continue

                from_addr = w3.to_checksum_address("0x" + log['topics'][1].hex()[-40:])
                to_addr = w3.to_checksum_address("0x" + log['topics'][2].hex()[-40:])
                
                data_hex = log['data'].hex()
                if not data_hex: value = 0
                else: value = int(data_hex, 16) / (10 ** decimals)

                transfers.append(value)

                if from_addr == ZERO_ADDRESS:
                    mint_count += 1
                
                # Whale: %1'den büyük transfer
                if total_supply > 0 and (value / total_supply) > 0.01:
                    large_transfers += 1
                    whale_movements.append({
                        "from": from_addr,
                        "to": to_addr,
                        "amount": float(f"{value:.4f}"),
                        "tx_hash": log['transactionHash'].hex()
                    })

            except Exception:
                continue

        # 5. ML Anomali Tespiti (context-aware)
        anomaly_score_ml = 0.0
        outliers_count = 0
        
        # Eğer yeterli veri varsa ML çalıştır
        if len(transfers) > 5:
            try:
                X = np.array(transfers).reshape(-1, 1)
                clf = IsolationForest(random_state=42, contamination='auto')
                preds = clf.fit_predict(X)
                outliers_count = list(preds).count(-1)
                # ML skoru - whitelisted için normalize et
                anomaly_score_ml = min((outliers_count / len(transfers)) * 3, 1.0)
                
                # Whitelisted tokens için daha tolerant threshold
                if is_whitelisted and anomaly_score_ml < 0.85:
                    logger.info(f"Whitelisted token - anomaly score {anomaly_score_ml:.2f} is expected")
                    anomaly_score_ml = max(0, anomaly_score_ml - 0.3)  # Reduce false positives
            except Exception:
                pass
        
        # 6. Risk Hesaplama (CONTEXT-AWARE)
        
        # Special case: If log fetch completely failed (extreme volume token)
        if logs_fetch_failed:
            logger.info(f"Transfer analysis skipped due to extreme volume - using Etherscan data instead")
            warnings.append("ℹ️ High-volume token - on-chain log analysis unavailable")
            warnings.append("ℹ️ Risk assessment based on holder distribution & liquidity analysis")
            return {
                "risk_score": 0,  # Neutral - defer to other modules (holder, liquidity, etc)
                "warnings": warnings,
                "data": {
                    "total_transfers_analyzed": 0,
                    "recent_mints": 0,
                    "large_transfers_count": 0,
                    "whale_movements": [],
                    "ml_anomaly_score": 0.0,
                    "extreme_volume": True,
                    "note": "Token volume exceeds RPC limits - analysis deferred to other modules"
                },
                "features": {
                    "transfer_count_log": 5.0,  # Assume high activity (better than 0)
                    "anomaly_score": 0.0
                }
            }
        
        # A) Hareketsizlik Cezası
        if total_transfers == 0:
            warnings.append("ℹ️ No transfers detected in recent blocks")
            # Don't penalize too much - other modules (holder, liquidity) will catch dead tokens
            risk_score += 0  # Neutral - let other modules decide
        elif total_transfers < 5 and not is_whitelisted:
            warnings.append(f"ℹ️ Low activity ({total_transfers} transfers in sample)")
            risk_score += 0  # Neutral
        
        # B) Mint Riski (CONTEXT-AWARE)
        if mint_count > 0:
            if is_rebase_token:
                # Rebase tokens (stETH, rETH) mint regularly - this is NORMAL
                logger.info(f"Rebase token - {mint_count} mint events are expected (staking rewards)")
                if mint_count > 50:  # Only warn if excessive
                    warnings.append(f"ℹ️ {mint_count} mint events (normal for staking token)")
            else:
                # Non-rebase tokens - minting is suspicious
                if mint_count > 20:
                    warnings.append(f"🚨 {mint_count} mint events detected (Supply Inflation Risk)")
                    risk_score += 40
                elif mint_count > 5:
                    warnings.append(f"⚠️ {mint_count} mint events detected")
                    risk_score += 25
                else:
                    warnings.append(f"⚡ {mint_count} mint events detected")
                    risk_score += 10

        # C) Whale Riski (CONTEXT-AWARE)
        if large_transfers > 0:
            if is_whitelisted:
                # Whitelisted tokens have institutional flows - less risky
                if large_transfers > 10:
                    warnings.append(f"ℹ️ {large_transfers} large transfers (institutional activity)")
                    risk_score += 5
            else:
                # Unknown tokens - whale activity is more suspicious
                warnings.append(f"⚠️ {large_transfers} whale transfers detected")
                risk_score += 10 + min(large_transfers * 2, 20)

        # D) ML Anomali Riski (CONTEXT-AWARE)
        if anomaly_score_ml > 0.7:
            if is_whitelisted:
                # Whitelisted tokens - unusual patterns less concerning
                warnings.append(f"ℹ️ Varied transfer patterns (Score: {anomaly_score_ml:.2f})")
                risk_score += 5
            else:
                # Unknown tokens - unusual patterns are red flags
                warnings.append(f"🤖 Unusual transfer patterns detected (Score: {anomaly_score_ml:.2f})")
                risk_score += 25

        return {
            "risk_score": min(risk_score, 100),
            "warnings": warnings,
            "data": {
                "total_transfers_analyzed": total_transfers,
                "recent_mints": mint_count,
                "large_transfers_count": large_transfers,
                "whale_movements": whale_movements[:5],
                "ml_anomaly_score": float(f"{anomaly_score_ml:.2f}")
            },
            "features": {
                "transfer_count_log": float(np.log1p(total_transfers)),
                "anomaly_score": float(anomaly_score_ml)
            }
        }

    except Exception as e:
        logger.error(f"D Module Critical Fail: {str(e)}")
        return {"risk_score": 0, "warnings": [f"Error: {str(e)}"], "data": {}, "features": {}}