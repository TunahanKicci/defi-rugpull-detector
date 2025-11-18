"""
WebSocket Manager for real-time monitoring
"""
import logging
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time monitoring
    """
    
    def __init__(self):
        # Active connections: {address: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        
        # Monitoring status: {address: {"active": bool, "alerts": [], ...}}
        self.monitoring_status: Dict[str, Dict] = {}
        
        # Background tasks
        self.monitor_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, address: str, chain: str):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            address: Token contract address
            chain: Blockchain network
        """
        await websocket.accept()
        self.active_connections[address].append(websocket)
        
        logger.info(f"WebSocket connected for {address} (Total: {len(self.active_connections[address])})")
        
        # Start monitoring if not already active
        if address not in self.monitor_tasks:
            await self.start_monitoring(address, chain)
        
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "address": address,
            "chain": chain,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, address: str):
        """
        Remove WebSocket connection
        
        Args:
            websocket: WebSocket connection
            address: Token contract address
        """
        if address in self.active_connections:
            try:
                self.active_connections[address].remove(websocket)
            except ValueError:
                pass
            
            # Clean up if no more connections
            if not self.active_connections[address]:
                del self.active_connections[address]
                # Stop monitoring task
                if address in self.monitor_tasks:
                    self.monitor_tasks[address].cancel()
                    del self.monitor_tasks[address]
                
                logger.info(f"All WebSocket connections closed for {address}")
    
    async def broadcast(self, address: str, message: dict):
        """
        Broadcast message to all connections for an address
        
        Args:
            address: Token contract address
            message: Message to broadcast
        """
        if address not in self.active_connections:
            return
        
        dead_connections = []
        
        for websocket in self.active_connections[address]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
                dead_connections.append(websocket)
        
        # Remove dead connections
        for ws in dead_connections:
            self.disconnect(ws, address)
    
    async def start_monitoring(self, address: str, chain: str):
        """
        Start real-time monitoring for a token
        
        Args:
            address: Token contract address
            chain: Blockchain network
        """
        if address in self.monitor_tasks:
            logger.info(f"Monitoring already active for {address}")
            return
        
        self.monitoring_status[address] = {
            "active": True,
            "chain": chain,
            "alerts": [],
            "last_update": datetime.utcnow().isoformat()
        }
        
        # Create monitoring task
        task = asyncio.create_task(self._monitor_token(address, chain))
        self.monitor_tasks[address] = task
        
        logger.info(f"Started monitoring for {address} on {chain}")
    
    async def stop_monitoring(self, address: str, chain: str):
        """
        Stop real-time monitoring for a token
        
        Args:
            address: Token contract address
            chain: Blockchain network
        """
        if address in self.monitor_tasks:
            self.monitor_tasks[address].cancel()
            del self.monitor_tasks[address]
        
        if address in self.monitoring_status:
            self.monitoring_status[address]["active"] = False
        
        logger.info(f"Stopped monitoring for {address}")
    
    async def get_monitor_status(self, address: str, chain: str) -> Dict:
        """
        Get current monitoring status
        
        Args:
            address: Token contract address
            chain: Blockchain network
            
        Returns:
            Monitoring status
        """
        return self.monitoring_status.get(address, {
            "active": False,
            "chain": chain,
            "alerts": [],
            "last_update": None
        })
    
    async def _monitor_token(self, address: str, chain: str):
        """
        Background task to monitor token events
        
        Args:
            address: Token contract address
            chain: Blockchain network
        """
        try:
            # TODO: Implement actual WebSocket monitoring using Web3.py
            # For now, simulate with periodic checks
            
            while True:
                # Simulate event detection
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Update status
                self.monitoring_status[address]["last_update"] = datetime.utcnow().isoformat()
                
                # Broadcast heartbeat
                await self.broadcast(address, {
                    "type": "heartbeat",
                    "address": address,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring task cancelled for {address}")
        except Exception as e:
            logger.error(f"Monitoring error for {address}: {str(e)}")
