"""
Blockchain network configurations
"""
from typing import Dict, Any


CHAINS = {
    "ethereum": {
        "chain_id": 1,
        "name": "Ethereum Mainnet",
        "rpc_env": "ETHEREUM_RPC",
        "wss_env": "ETHEREUM_WSS",
        "explorer": "https://etherscan.io",
        "explorer_api": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_token": "ETH",
        "dex_routers": {
            "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
        }
    },
    "bsc": {
        "chain_id": 56,
        "name": "Binance Smart Chain",
        "rpc_env": "BSC_RPC",
        "wss_env": "BSC_WSS",
        "explorer": "https://bscscan.com",
        "explorer_api": "https://api.bscscan.com/api",
        "api_key_env": "BSCSCAN_API_KEY",
        "native_token": "BNB",
        "dex_routers": {
            "pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "pancakeswap_v3": "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4"
        }
    },
    "polygon": {
        "chain_id": 137,
        "name": "Polygon",
        "rpc_env": "POLYGON_RPC",
        "wss_env": "POLYGON_WSS",
        "explorer": "https://polygonscan.com",
        "explorer_api": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "native_token": "MATIC",
        "dex_routers": {
            "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        }
    }
}


def get_chain_config(chain_name: str) -> Dict[str, Any]:
    """Get configuration for a specific chain"""
    return CHAINS.get(chain_name.lower(), CHAINS["ethereum"])


def get_all_chains() -> Dict[str, Dict[str, Any]]:
    """Get all chain configurations"""
    return CHAINS
