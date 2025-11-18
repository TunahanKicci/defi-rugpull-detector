"""
Real-time monitoring endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Path, Query, HTTPException
import logging
import json

from services.websocket_manager import WebSocketManager
from utils.validators import validate_contract_address

router = APIRouter()
logger = logging.getLogger(__name__)
ws_manager = WebSocketManager()


@router.get("/monitor/{address}")
async def get_monitoring_status(
    address: str = Path(..., description="Token contract address"),
    chain: str = Query("ethereum", description="Blockchain network")
):
    """
    Get current monitoring status for a token
    
    Returns active alerts and recent events
    """
    try:
        normalized_address = validate_contract_address(address)
        if not normalized_address:
            raise HTTPException(status_code=400, detail="Invalid address")
        
        status = await ws_manager.get_monitor_status(normalized_address, chain)
        
        return {
            "address": normalized_address,
            "chain": chain,
            "monitoring": status.get("active", False),
            "alerts": status.get("alerts", []),
            "last_update": status.get("last_update")
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/monitor/ws/{address}")
async def websocket_monitor(
    websocket: WebSocket,
    address: str,
    chain: str = "ethereum"
):
    """
    WebSocket endpoint for real-time monitoring
    
    Streams live events:
    - Large transfers
    - LP removals
    - Contract modifications
    - Suspicious activities
    """
    normalized_address = validate_contract_address(address)
    if not normalized_address:
        await websocket.close(code=4000, reason="Invalid address")
        return
    
    await ws_manager.connect(websocket, normalized_address, chain)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, normalized_address)
        logger.info(f"WebSocket disconnected for {normalized_address}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        ws_manager.disconnect(websocket, normalized_address)


@router.post("/monitor/{address}/start")
async def start_monitoring(
    address: str = Path(..., description="Token contract address"),
    chain: str = Query("ethereum", description="Blockchain network")
):
    """
    Start real-time monitoring for a token
    """
    try:
        normalized_address = validate_contract_address(address)
        if not normalized_address:
            raise HTTPException(status_code=400, detail="Invalid address")
        
        await ws_manager.start_monitoring(normalized_address, chain)
        
        return {
            "status": "monitoring_started",
            "address": normalized_address,
            "chain": chain
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor/{address}/stop")
async def stop_monitoring(
    address: str = Path(..., description="Token contract address"),
    chain: str = Query("ethereum", description="Blockchain network")
):
    """
    Stop real-time monitoring for a token
    """
    try:
        normalized_address = validate_contract_address(address)
        if not normalized_address:
            raise HTTPException(status_code=400, detail="Invalid address")
        
        await ws_manager.stop_monitoring(normalized_address, chain)
        
        return {
            "status": "monitoring_stopped",
            "address": normalized_address,
            "chain": chain
        }
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
