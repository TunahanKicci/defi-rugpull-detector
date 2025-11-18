"""
Token analysis endpoint
"""
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional
import logging

from api.models.response import AnalysisResponse, ErrorResponse
from utils.validators import validate_contract_address, is_valid_chain
from services.analysis_orchestrator import AnalysisOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/analyze/{address}",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_token(
    address: str = Path(..., description="Token contract address"),
    chain: str = Query("ethereum", description="Blockchain network (ethereum, bsc, polygon)"),
    force_refresh: bool = Query(False, description="Force refresh cached data")
):
    """
    Analyze a token contract for rug pull risk
    
    **Performs comprehensive analysis including:**
    - Smart contract security scan
    - Holder distribution analysis
    - Liquidity pool assessment
    - Transfer pattern anomalies
    - Scam pattern matching
    - Tokenomics review
    - ML-based risk scoring
    
    **Returns:**
    - Risk score (0-100)
    - Detailed analysis from all modules
    - Warnings and recommendations
    """
    try:
        # Validate inputs
        normalized_address = validate_contract_address(address)
        if not normalized_address:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid contract address format"}
            )
        
        if not is_valid_chain(chain):
            raise HTTPException(
                status_code=400,
                detail={"error": f"Unsupported chain: {chain}. Supported: ethereum, bsc, polygon"}
            )
        
        logger.info(f"Starting analysis for {normalized_address} on {chain}")
        
        # Initialize orchestrator and run analysis
        orchestrator = AnalysisOrchestrator(chain=chain)
        result = await orchestrator.analyze(
            address=normalized_address,
            force_refresh=force_refresh
        )
        
        logger.info(f"Analysis completed for {normalized_address}: Risk Score = {result.get('risk_score', 0)}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error during analysis", "message": str(e)}
        )


@router.get("/analyze/{address}/quick")
async def quick_analysis(
    address: str = Path(..., description="Token contract address"),
    chain: str = Query("ethereum", description="Blockchain network")
):
    """
    Quick analysis with cached data only
    
    Returns basic risk assessment without deep analysis
    """
    try:
        normalized_address = validate_contract_address(address)
        if not normalized_address:
            raise HTTPException(status_code=400, detail="Invalid address")
        
        orchestrator = AnalysisOrchestrator(chain=chain)
        result = await orchestrator.quick_check(normalized_address)
        
        return result
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
