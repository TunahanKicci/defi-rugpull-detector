"""
Application constants
"""

# Risk score thresholds
RISK_CRITICAL = 80
RISK_HIGH = 60
RISK_MEDIUM = 40
RISK_LOW = 20

# Token holder thresholds
HOLDER_CONCENTRATION_HIGH = 50  # %
HOLDER_CONCENTRATION_MEDIUM = 30  # %
TOP_HOLDERS_COUNT = 10

# Liquidity thresholds
MIN_LIQUIDITY_USD = 10000
LP_LOCK_REQUIRED_MONTHS = 3
LP_TO_MCAP_RATIO_MIN = 0.05  # 5%

# Transfer anomaly thresholds
LARGE_TRANSFER_THRESHOLD = 0.05  # 5% of supply
WHALE_THRESHOLD = 0.01  # 1% of supply

# Tokenomics thresholds
MAX_BUY_TAX = 10  # %
MAX_SELL_TAX = 15  # %
MAX_TOTAL_TAX = 20  # %

# Contract security flags
RISKY_FUNCTIONS = [
    "mint",
    "burn",
    "blacklist",
    "pause",
    "setTaxes",
    "setFees",
    "excludeFromFees",
    "setMaxTransaction",
    "setMaxWallet"
]

DANGEROUS_FUNCTIONS = [
    "selfdestruct",
    "delegatecall",
    "withdrawETH",
    "withdrawToken",
    "transferOwnership"
]

# Cache TTL (seconds)
CACHE_CONTRACT_INFO = 3600  # 1 hour
CACHE_HOLDER_DATA = 300  # 5 minutes
CACHE_LP_DATA = 300  # 5 minutes
CACHE_PRICE_DATA = 60  # 1 minute

# API Rate limits
MAX_REQUESTS_PER_MINUTE = 60
MAX_REQUESTS_PER_HOUR = 1000

# WebSocket events
WS_EVENT_LP_REMOVAL = "lp_removal"
WS_EVENT_LARGE_TRANSFER = "large_transfer"
WS_EVENT_OWNERSHIP_CHANGE = "ownership_change"
WS_EVENT_CONTRACT_PAUSE = "contract_pause"

# ML Model params
ML_MODEL_VERSION = "1.0.0"
ML_FEATURE_COUNT = 50
ML_ANOMALY_THRESHOLD = 0.7

# Supported chains
SUPPORTED_CHAINS = ["ethereum", "bsc", "polygon"]

# DEX Factory addresses
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
PANCAKESWAP_V2_FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"

# Token standards
ERC20_INTERFACE_ID = "0x36372b07"
ERC20_ABI_MINIMAL = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
]
