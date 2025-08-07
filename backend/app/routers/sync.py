from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.crdt import CRDTEngine
from services.sync_service import SyncManager
import json

router = APIRouter(tags=["Sync"])

sync_manager = SyncManager()

@router.websocket("/ws/{note_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    note_id: str,
    user_id: str
):
    await sync_manager.connect(websocket, note_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            operation = json.loads(data)
            await sync_manager.handle_operation(websocket, note_id, user_id, operation)
            
    except WebSocketDisconnect:
        await sync_manager.disconnect(websocket, note_id)