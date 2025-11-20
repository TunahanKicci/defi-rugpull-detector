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
        total_supply = 0
        try:
            decimals = contract.functions.decimals().call()
            total_supply_raw = contract.functions.totalSupply().call()
            total_supply = total_supply_raw / (10 ** decimals)
        except Exception as e:
            logger.error(f"Failed to fetch supply: {e}")
            return {"risk_score": 0, "warnings": ["Could not fetch total supply"]}

        data["total_supply"] = total_supply

        # 2. Aktif Cüzdanları Bul (Etherscan API - tokentx)
        # Son 100 transferi çekip kimlerin aktif olduğunu buluyoruz.
        active_addresses = set()
        
        try:
            params = {
                "chainid": 1,  # Ethereum Mainnet
                "module": "account",
                "action": "tokentx",
                "contractaddress": checksum_address,
                "page": 1,
                "offset": 100, # Son 100 işlem yeterli
                "sort": "desc",
                "apikey": ETHERSCAN_API_KEY
            }
            
            response = requests.get(ETHERSCAN_URL, params=params, timeout=10)
            tx_data = response.json()
            
            if tx_data["status"] == "1" and tx_data["result"]:
                for tx in tx_data["result"]:
                    active_addresses.add(w3.to_checksum_address(tx["from"]))
                    active_addresses.add(w3.to_checksum_address(tx["to"]))
            else:
                logger.warning(f"Etherscan API warning: {tx_data.get('message')}")
                
        except Exception as api_err:
            logger.warning(f"Etherscan API failed, falling back to partial checks: {api_err}")

        # Eğer hiç adres bulamazsa (API hatası veya 0 tx), contract owner'ı ekle
        if not active_addresses:
            try:
                owner = contract.functions.owner().call()
                active_addresses.add(owner)
            except:
                pass
            
        # 3. Gerçek Bakiyeleri Sorgula (RPC - balanceOf)
        # Bulduğumuz adreslerin ŞU ANKİ gerçek bakiyesini soruyoruz.
        holder_balances = []
        whale_holdings = 0
        
        # Burn adresi (0xdead...) genelde holder sayılmaz, filtreleyebiliriz ama 
        # supply hesaplamasında önemli olabilir. Şimdilik dahil ediyoruz.
        
        for addr in list(active_addresses)[:10]: # RPC'yi yormamak için max 10 adres (hızlı test)
            try:
                bal_raw = contract.functions.balanceOf(addr).call()
                bal = bal_raw / (10 ** decimals)
                if bal > 0:
                    holder_balances.append({"address": addr, "balance": bal})
            except:
                continue

        # 4. Metrikleri Hesapla
        # Bakiyeye göre sırala (Büyükten küçüğe)
        holder_balances.sort(key=lambda x: x["balance"], reverse=True)
        
        # Top 10 Holder Hesabı
        top_10_holders = holder_balances[:10]
        top_10_sum = sum(h["balance"] for h in top_10_holders)
        
        # Top 10 Yüzdesi
        top_10_ratio = 0
        if total_supply > 0:
            top_10_ratio = top_10_sum / total_supply

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

        # Kural 3: Çok az holder verisi varsa
        if len(holder_balances) < 5:
            warnings.append("ℹ️ Very few active holders found (Low Adoption)")
            risk_score += 10

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