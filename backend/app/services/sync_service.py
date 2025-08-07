from utils import crdt
from db.session import SessionLocal
from services import note_service
from typing import Dict, List
import json
from fastapi import WebSocket

class SyncManager:
    active_connections: Dict[str, List[WebSocket]] = {}
    note_states: Dict[str, crdt.CRDTEngine] = {}

    @classmethod
    async def connect(cls, websocket: WebSocket, note_id: str, user_id: str):
        await websocket.accept()
        
        # Create or get CRDT state for this note
        if note_id not in cls.note_states:
            cls.note_states[note_id] = crdt.CRDTEngine(note_id)
        
        # Add connection to note room
        if note_id not in cls.active_connections:
            cls.active_connections[note_id] = []
        cls.active_connections[note_id].append(websocket)
        
        # Send current state to new client
        current_state = cls.note_states[note_id].get_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "state": current_state
        }))

    @classmethod
    async def disconnect(cls, websocket: WebSocket, note_id: str):
        if note_id in cls.active_connections:
            cls.active_connections[note_id].remove(websocket)
            if not cls.active_connections[note_id]:
                del cls.active_connections[note_id]
                # Optionally: persist note state to database
                # db = SessionLocal()
                # note_service.NoteService(db).update_note(
                #     note_id, 
                #     user_id, 
                #     {"content": cls.note_states[note_id].get_state()['content']}
                # )
                # del cls.note_states[note_id]

    @classmethod
    async def broadcast(cls, note_id: str, message: dict, exclude: WebSocket = None):
        if note_id in cls.active_connections:
            for connection in cls.active_connections[note_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except:
                        # Handle disconnected clients
                        pass

    @classmethod
    async def handle_operation(cls, websocket: WebSocket, note_id: str, user_id: str, operation: dict):
        # Apply operation to CRDT
        new_state = cls.note_states[note_id].apply_operation(
            operation, 
            f"{user_id}_{operation.get('device_id', 'default')}"
        )
        
        # Broadcast update to all clients in the room
        await cls.broadcast(note_id, {
            "type": "operation",
            "operation": operation,
            "state": new_state
        }, exclude=websocket)
        
        # Send confirmation to sender
        await websocket.send_json({
            "type": "acknowledge",
            "operation_id": operation.get('id'),
            "state": new_state
        })
        
        # Trigger AI processing on significant changes
        if operation.get('change_size', 0) > 100:
            db = SessionLocal()
            note_service.NoteService(db).process_note_ai(
                note_service.NoteService(db).get_note(note_id, user_id))
            db.close()