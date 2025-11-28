"""
Module D: Transfer Anomaly Detection
Analyzes transfer patterns for suspicious activity using Real-time Blockchain Logs & ML.
"""
import logging
from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import IsolationForest
from web3 import Web3

# Logger ayarları
logger = logging.getLogger(__name__)

# ERC20 Transfer Event Signature
TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Whitelisted tokens (known legitimate tokens with expected patterns)
WHITELISTED_TOKENS = {
    "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",  # stETH - Lido Staked Ether (rebase token)
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
    "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",  # MATIC
    "0x514910771af9ca656af840dff83e8264ecf986ca",  # LINK
}

# Known rebase/liquid staking tokens (minting is expected)
REBASE_TOKENS = {
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",  # stETH
    "0x9559aaa82d9649c7a7b220e7c461d2e74c9a3593",  # rETH - Rocket Pool
    "0xac3e018457b222d93114458476f3e3416abbe38f",  # sfrxETH
}

async def analyze(address: str, blockchain) -> Dict[str, Any]:
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

        # 3. Transfer Loglarını Çek (Son 100 Blok - USDT gibi yüksek hacimli tokenlar için düşük)
        try:
            current_block = w3.eth.block_number
            # 100 blok = ~20 dakika, yeterli örneklem
            start_block_int = max(0, current_block - 100)
            
            from_block_hex = w3.to_hex(start_block_int)
            to_block_hex = w3.to_hex(current_block) 
            
            logger.info(f"Fetching logs from last 100 blocks: {from_block_hex} to {to_block_hex}")

            logs = w3.eth.get_logs({
                'fromBlock': from_block_hex,  
                'toBlock': to_block_hex,
                'address': checksum_address,
                'topics': [TRANSFER_EVENT_TOPIC]
            })
            logger.info(f"Successfully fetched {len(logs)} transfer logs")
        except Exception as log_err:
            # RPC "query exceeds" hatası için daha açıklayıcı log
            if 'query exceeds' in str(log_err):
                logger.warning(f"Token has too many transfers, using empty dataset: {log_err}")
            else:
                logger.error(f"Log fetch error: {log_err}")
            logs = []

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
        
        # A) Hareketsizlik Cezası
        if total_transfers == 0:
            warnings.append("⚠️ No activity in the last 100 blocks")
            risk_score += 25 if not is_whitelisted else 0  # Whitelisted tokens can be inactive
        elif total_transfers < 10 and not is_whitelisted:
            warnings.append(f"ℹ️ Very low activity ({total_transfers} txs)")
            risk_score += 10
        
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