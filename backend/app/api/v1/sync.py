from fastapi import APIRouter, WebSocket
from services.sync_service import SyncManager
from utils.crdt import CRDTEngine

router = APIRouter()
sync_manager = SyncManager()

@router.websocket("/ws/sync/{note_id}")
async def websocket_sync(websocket: WebSocket, note_id: str, user_id: int):
    await websocket.accept()
    crdt_engine = CRDTEngine(note_id, user_id)
    
    # Add client to sync group
    sync_manager.add_client(note_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process update with CRDT
            processed_update = crdt_engine.process_update(data)
            
            # Broadcast to other clients
            await sync_manager.broadcast(
                note_id, 
                processed_update,
                exclude=websocket
            )
            
            # AI processing on significant changes
            if processed_update['change_size'] > 50:
                ai_result = await ai_service.process_note({
                    'id': note_id,
                    'user_id': user_id,
                    'content': crdt_engine.get_content()
                })
                await websocket.send_json({'ai_update': ai_result})
                
    except WebSocketDisconnect:
        sync_manager.remove_client(note_id, websocket)