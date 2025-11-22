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

async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Transfer modellerini analiz eder. 
    GÜNCELLEME: Düşük aktivite artık risk puanını artırıyor.
    """
    try:
        logger.info(f"Starting Transfer Anomaly Analysis for {address}...")
        
        warnings = []
        risk_score = 0
        data = {}
        features = {}

        w3 = blockchain.w3
        checksum_address = w3.to_checksum_address(address)

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

        # 5. ML Anomali Tespiti
        anomaly_score_ml = 0.0
        outliers_count = 0
        
        # Eğer yeterli veri varsa ML çalıştır
        if len(transfers) > 5:
            try:
                X = np.array(transfers).reshape(-1, 1)
                clf = IsolationForest(random_state=42, contamination='auto')
                preds = clf.fit_predict(X)
                outliers_count = list(preds).count(-1)
                # ML skoru
                anomaly_score_ml = min((outliers_count / len(transfers)) * 3, 1.0)
            except Exception:
                pass
        
        # 6. Risk Hesaplama (GÜNCELLENEN KISIM)
        
        # A) Hareketsizlik Cezası
        if total_transfers == 0:
            warnings.append("⚠️ No activity in the last 2000 blocks (Dead or Locked)")
            risk_score += 35  # Hiç hareket yoksa orta risk
        elif total_transfers < 10:
            warnings.append(f"ℹ️ Very low activity ({total_transfers} txs)")
            risk_score += 15  # Çok az hareket varsa düşük-orta risk
        
        # B) Mint Riski
        if mint_count > 0:
            warnings.append(f"🚨 {mint_count} mint events detected (Supply Inflation)")
            risk_score += 40

        # C) Whale Riski
        if large_transfers > 0:
            warnings.append(f"⚠️ {large_transfers} whale transfers detected")
            risk_score += 15 + (large_transfers * 2)

        # D) ML Anomali Riski
        if anomaly_score_ml > 0.5:
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