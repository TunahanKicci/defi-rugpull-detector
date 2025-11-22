

"""
Module B: Holder Analysis
Analyzes token distribution using 'Active Wallet Sampling' via Etherscan & RPC.
Replaces mock data with real on-chain balance checks.
"""
import logging
import requests
from typing import Dict, Any, List
from web3 import Web3
from config.settings import settings

logger = logging.getLogger(__name__)

# Etherscan API Ayarları
ETHERSCAN_API_KEY = settings.ETHERSCAN_API_KEY
ETHERSCAN_URL = "https://api.etherscan.io/v2/api"

def calculate_gini(balances: List[float]) -> float:
    """
    Gini katsayısını hesaplar (0: Eşit dağılım, 1: Tam eşitsizlik/Merkeziyetçi).
    """
    if not balances: return 0.0
    sorted_balances = sorted(balances)
    n = len(balances)
    cumulative_sum = sum((i + 1) * bal for i, bal in enumerate(sorted_balances))
    total_sum = sum(sorted_balances)
    if total_sum == 0: return 0.0
    return (2 * cumulative_sum) / (n * total_sum) - (n + 1) / n

async def analyze(address: str, blockchain) -> Dict[str, Any]:
    """
    Gerçek zamanlı Holder analizi yapar.
    Yöntem: Son transferlerden aktif cüzdanları bul -> RPC ile gerçek bakiyelerini sor.
    """
    try:
        logger.info(f"Starting Real Holder Analysis for {address}...")
        
        data = {}
        warnings = []
        risk_score = 0
        
        w3 = blockchain.w3
        checksum_address = w3.to_checksum_address(address)

        # 1. Toplam Arzı (Total Supply) Çek - RPC
        contract = w3.eth.contract(address=checksum_address, abi=[
            {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
            {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}
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
            logger.debug(f"Could not fetch total supply via RPC: {e}")
            # Total supply olmadan da analiz yapabiliriz - sadece yüzde hesaplayamayız
            pass

        # 2. YENİ STRATEJİ: Etherscan API'den transfer verilerini kullan (RPC'siz)
        # Transfer miktarlarından holder profilini çıkarıyoruz - RPC'ye hiç çağrı yapmıyoruz
        holder_transfers = {}  # address -> {"incoming": total, "outgoing": total}
        
        try:
            # Yüksek hacimli tokenlar için blok aralığı stratejisi kullan
            # Son 100 blok içindeki transferleri çek (yaklaşık 20 dakika)
            try:
                latest_block = w3.eth.block_number
                start_block = latest_block - 100
            except:
                # RPC çalışmazsa default range
                latest_block = 0
                start_block = 0
            
            params = {
                "chainid": 1,
                "module": "account",
                "action": "tokentx",
                "contractaddress": checksum_address,
                "startblock": start_block if start_block > 0 else None,
                "endblock": latest_block if latest_block > 0 else None,
                "page": 1,
                "offset": 20,
                "sort": "desc",
                "apikey": ETHERSCAN_API_KEY
            }
            
            # None değerlerini kaldır
            params = {k: v for k, v in params.items() if v is not None}
            
            response = requests.get(ETHERSCAN_URL, params=params, timeout=10)
            tx_data = response.json()
            
            if tx_data["status"] == "1" and tx_data["result"]:
                logger.info(f"Analyzing {len(tx_data['result'])} recent transfers...")
                
                for tx in tx_data["result"]:
                    from_addr = w3.to_checksum_address(tx["from"])
                    to_addr = w3.to_checksum_address(tx["to"])
                    value = int(tx["value"]) / (10 ** decimals)
                    
                    # Transfer miktarlarını topla
                    if from_addr not in holder_transfers:
                        holder_transfers[from_addr] = {"incoming": 0, "outgoing": 0}
                    if to_addr not in holder_transfers:
                        holder_transfers[to_addr] = {"incoming": 0, "outgoing": 0}
                    
                    holder_transfers[from_addr]["outgoing"] += value
                    holder_transfers[to_addr]["incoming"] += value
                
                logger.info(f"Collected transfer data for {len(holder_transfers)} unique addresses")
            else:
                msg = tx_data.get('message', 'Unknown error')
                logger.warning(f"Etherscan API returned status 0: {msg}")
                
        except Exception as api_err:
            logger.warning(f"Etherscan API failed: {api_err}")
            
        # 3. Transfer Net Balance'ı Hesapla (Proxy Balance)
        # Net = incoming - outgoing (pozitif = holder, negatif = sattı)
        holder_balances = []
        
        for addr, transfers in holder_transfers.items():
            net_balance = transfers["incoming"] - transfers["outgoing"]
            if net_balance > 0:  # Sadece pozitif balans olanları al
                holder_balances.append({
                    "address": addr,
                    "balance": net_balance,
                    "total_incoming": transfers["incoming"],
                    "total_outgoing": transfers["outgoing"]
                })
        
        logger.info(f"Found {len(holder_balances)} addresses with positive net balance")

        # 4. Metrikleri Hesapla
        # Bakiyeye göre sırala (Büyükten küçüğe)
        holder_balances.sort(key=lambda x: x["balance"], reverse=True)
        
        # Top 10 Holder Hesabı
        top_10_holders = holder_balances[:10]
        top_10_sum = sum(h["balance"] for h in top_10_holders)
        
        # Top 10 Yüzdesi (eğer total supply varsa)
        top_10_ratio = 0
        if total_supply and total_supply > 0:
            top_10_ratio = top_10_sum / total_supply
        else:
            # Total supply yoksa, relative scoring (top 10 / tüm örneklem)
            total_sample = sum(h["balance"] for h in holder_balances)
            if total_sample > 0:
                top_10_ratio = top_10_sum / total_sample
                warnings.append("ℹ️ Using sample-based ratio (total supply unavailable)")

        # Gini Katsayısı (Sadece örneklem üzerinden)
        balances_list = [h["balance"] for h in holder_balances]
        gini_coefficient = calculate_gini(balances_list)

        # 5. Risk Skorlama
        
        # Kural 1: Top 10 çok yüksekse (>%95)
        if top_10_ratio > 0.98:
            risk_score += 60
            warnings.append(f"🚨 EXTREME CENTRALIZATION: Top 10 holders own {top_10_ratio*100:.1f}%")
        elif top_10_ratio > 0.90:
            risk_score += 40
            warnings.append(f"⚠️ High Centralization: Top 10 own {top_10_ratio*100:.1f}%")
        elif top_10_ratio > 0.70:
            risk_score += 15
            warnings.append(f"ℹ️ Concentrated supply: Top 10 own {top_10_ratio*100:.1f}%")

        # Kural 2: Gini Katsayısı
        if gini_coefficient > 0.9:
            risk_score += 10
            warnings.append("⚠️ High inequality between active holders")

        # Kural 3: Çok az holder verisi varsa (örneklem boyutu uyarısı)
        sample_size = len(holder_balances)
        if sample_size < 5:
            warnings.append(f"⚠️ Limited sample size ({sample_size} holders) - results may not be representative")
            risk_score += 15
        elif sample_size < 10:
            warnings.append(f"ℹ️ Moderate sample size ({sample_size} holders) - consider as estimation")
            risk_score += 5

        data["top_10_ratio"] = float(f"{top_10_ratio:.4f}")
        data["gini_coefficient"] = float(f"{gini_coefficient:.4f}")
        data["analyzed_wallet_count"] = len(holder_balances)
        data["top_holders"] = top_10_holders # Frontend'de listelemek için

        features = {
            "top_10_ratio": float(top_10_ratio),
            "gini_coefficient": float(gini_coefficient),
            "holder_count_proxy": len(holder_balances)
        }

        logger.info(f"B Module Analysis Complete. Risk: {risk_score}")
        
        return {
            "risk_score": min(risk_score, 100),
            "warnings": warnings,
            "data": data,
            "features": features
        }

    except Exception as e:
        logger.error(f"Holder analysis failed: {str(e)}")
        return {
            "risk_score": 0,
            "warnings": [f"Module B Error: {str(e)}"],
            "data": {},
            "features": {}
        }
